import { cmd } from "./cmd"
import { Client } from "@modelcontextprotocol/sdk/client/index.js"
import { StreamableHTTPClientTransport } from "@modelcontextprotocol/sdk/client/streamableHttp.js"
import { SSEClientTransport } from "@modelcontextprotocol/sdk/client/sse.js"
import { UnauthorizedError } from "@modelcontextprotocol/sdk/client/auth.js"
import * as prompts from "@clack/prompts"
import { UI } from "../ui"
import { MCP } from "../../mcp"
import { McpAuth } from "../../mcp/auth"
import { McpOAuthProvider } from "../../mcp/oauth-provider"
import { Config } from "../../config/config"
import { Instance } from "../../project/instance"
import { Installation } from "../../installation"
import path from "path"
import { Global } from "../../global"

function getAuthStatusIcon(status: MCP.AuthStatus): string {
  switch (status) {
    case "authenticated":
      return "✓"
    case "expired":
      return "⚠"
    case "not_authenticated":
      return "○"
  }
}

function getAuthStatusText(status: MCP.AuthStatus): string {
  switch (status) {
    case "authenticated":
      return "已认证"
    case "expired":
      return "已过期"
    case "not_authenticated":
      return "未认证"
  }
}

type McpEntry = NonNullable<Config.Info["mcp"]>[string]

type McpConfigured = Config.Mcp
function isMcpConfigured(config: McpEntry): config is McpConfigured {
  return typeof config === "object" && config !== null && "type" in config
}

type McpRemote = Extract<McpConfigured, { type: "remote" }>
function isMcpRemote(config: McpEntry): config is McpRemote {
  return isMcpConfigured(config) && config.type === "remote"
}

export const McpCommand = cmd({
  command: "mcp",
  describe: "manage MCP (Model Context Protocol) servers",
  builder: (yargs) =>
    yargs
      .command(McpAddCommand)
      .command(McpListCommand)
      .command(McpAuthCommand)
      .command(McpLogoutCommand)
      .command(McpDebugCommand)
      .demandCommand(),
  async handler() {},
})

export const McpListCommand = cmd({
  command: "list",
  aliases: ["ls"],
  describe: "list MCP servers and their status",
  async handler() {
    await Instance.provide({
      directory: process.cwd(),
      async fn() {
        UI.empty()
        prompts.intro("MCP 服务器")

        const config = await Config.get()
        const mcpServers = config.mcp ?? {}
        const statuses = await MCP.status()

        const servers = Object.entries(mcpServers).filter((entry): entry is [string, McpConfigured] =>
          isMcpConfigured(entry[1]),
        )

        if (servers.length === 0) {
          prompts.log.warn("未配置 MCP 服务器")
          prompts.outro("使用 opencode mcp add 添加服务器")
          return
        }

        for (const [name, serverConfig] of servers) {
          const status = statuses[name]
          const hasOAuth = isMcpRemote(serverConfig) && !!serverConfig.oauth
          const hasStoredTokens = await MCP.hasStoredTokens(name)

          let statusIcon: string
          let statusText: string
          let hint = ""

          if (!status) {
            statusIcon = "○"
            statusText = "未初始化"
          } else if (status.status === "connected") {
            statusIcon = "✓"
            statusText = "已连接"
            if (hasOAuth && hasStoredTokens) {
              hint = " (OAuth)"
            }
          } else if (status.status === "disabled") {
            statusIcon = "○"
            statusText = "已禁用"
          } else if (status.status === "needs_auth") {
            statusIcon = "⚠"
            statusText = "需要认证"
          } else if (status.status === "needs_client_registration") {
            statusIcon = "✗"
            statusText = "需要客户端注册"
            hint = "\n    " + status.error
          } else {
            statusIcon = "✗"
            statusText = "失败"
            hint = "\n    " + status.error
          }

          const typeHint = serverConfig.type === "remote" ? serverConfig.url : serverConfig.command.join(" ")
          prompts.log.info(
            `${statusIcon} ${name} ${UI.Style.TEXT_DIM}${statusText}${hint}\n    ${UI.Style.TEXT_DIM}${typeHint}`,
          )
        }

        prompts.outro(`${servers.length} 个服务器`)
      },
    })
  },
})

export const McpAuthCommand = cmd({
  command: "auth [name]",
  describe: "authenticate with an OAuth-enabled MCP server",
  builder: (yargs) =>
    yargs
      .positional("name", {
        describe: "name of the MCP server",
        type: "string",
      })
      .command(McpAuthListCommand),
  async handler(args) {
    await Instance.provide({
      directory: process.cwd(),
      async fn() {
        UI.empty()
        prompts.intro("MCP OAuth 认证")

        const config = await Config.get()
        const mcpServers = config.mcp ?? {}

        // Get OAuth-capable servers (remote servers with oauth not explicitly disabled)
        const oauthServers = Object.entries(mcpServers).filter(
          (entry): entry is [string, McpRemote] => isMcpRemote(entry[1]) && entry[1].oauth !== false,
        )

        if (oauthServers.length === 0) {
          prompts.log.warn("未配置支持 OAuth 的 MCP 服务器")
          prompts.log.info("远程 MCP 服务器默认支持 OAuth。在 opencode.json 中添加远程服务器:")
          prompts.log.info(`
  "mcp": {
    "my-server": {
      "type": "remote",
      "url": "https://example.com/mcp"
    }
  }`)
          prompts.outro("完成")
          return
        }

        let serverName = args.name
        if (!serverName) {
          // Build options with auth status
          const options = await Promise.all(
            oauthServers.map(async ([name, cfg]) => {
              const authStatus = await MCP.getAuthStatus(name)
              const icon = getAuthStatusIcon(authStatus)
              const statusText = getAuthStatusText(authStatus)
              const url = cfg.url
              return {
                label: `${icon} ${name} (${statusText})`,
                value: name,
                hint: url,
              }
            }),
          )

          const selected = await prompts.select({
            message: "选择要认证的 MCP 服务器",
            options,
          })
          if (prompts.isCancel(selected)) throw new UI.CancelledError()
          serverName = selected
        }

        const serverConfig = mcpServers[serverName]
        if (!serverConfig) {
          prompts.log.error(`未找到 MCP 服务器: ${serverName}`)
          prompts.outro("完成")
          return
        }

        if (!isMcpRemote(serverConfig) || serverConfig.oauth === false) {
          prompts.log.error(`MCP 服务器 ${serverName} 不是支持 OAuth 的远程服务器`)
          prompts.outro("完成")
          return
        }

        // Check if already authenticated
        const authStatus = await MCP.getAuthStatus(serverName)
        if (authStatus === "authenticated") {
          const confirm = await prompts.confirm({
            message: `${serverName} 已有有效凭据。重新认证？`,
          })
          if (prompts.isCancel(confirm) || !confirm) {
            prompts.outro("已取消")
            return
          }
        } else if (authStatus === "expired") {
          prompts.log.warn(`${serverName} 凭据已过期。正在重新认证...`)
        }

        const spinner = prompts.spinner()
        spinner.start("启动 OAuth 流程...")

        try {
          const status = await MCP.authenticate(serverName)

          if (status.status === "connected") {
            spinner.stop("认证成功！")
          } else if (status.status === "needs_client_registration") {
            spinner.stop("认证失败", 1)
            prompts.log.error(status.error)
            prompts.log.info("在 MCP 服务器配置中添加 clientId:")
            prompts.log.info(`
  "mcp": {
    "${serverName}": {
      "type": "remote",
      "url": "${serverConfig.url}",
      "oauth": {
        "clientId": "your-client-id",
        "clientSecret": "your-client-secret"
      }
    }
  }`)
          } else if (status.status === "failed") {
            spinner.stop("认证失败", 1)
            prompts.log.error(status.error)
          } else {
            spinner.stop("意外状态: " + status.status, 1)
          }
        } catch (error) {
          spinner.stop("认证失败", 1)
          prompts.log.error(error instanceof Error ? error.message : String(error))
        }

        prompts.outro("完成")
      },
    })
  },
})

export const McpAuthListCommand = cmd({
  command: "list",
  aliases: ["ls"],
  describe: "list OAuth-capable MCP servers and their auth status",
  async handler() {
    await Instance.provide({
      directory: process.cwd(),
      async fn() {
        UI.empty()
        prompts.intro("MCP OAuth 状态")

        const config = await Config.get()
        const mcpServers = config.mcp ?? {}

        // Get OAuth-capable servers
        const oauthServers = Object.entries(mcpServers).filter(
          (entry): entry is [string, McpRemote] => isMcpRemote(entry[1]) && entry[1].oauth !== false,
        )

        if (oauthServers.length === 0) {
          prompts.log.warn("未配置支持 OAuth 的 MCP 服务器")
          prompts.outro("完成")
          return
        }

        for (const [name, serverConfig] of oauthServers) {
          const authStatus = await MCP.getAuthStatus(name)
          const icon = getAuthStatusIcon(authStatus)
          const statusText = getAuthStatusText(authStatus)
          const url = serverConfig.url

          prompts.log.info(`${icon} ${name} ${UI.Style.TEXT_DIM}${statusText}\n    ${UI.Style.TEXT_DIM}${url}`)
        }

        prompts.outro(`${oauthServers.length} 个支持 OAuth 的服务器`)
      },
    })
  },
})

export const McpLogoutCommand = cmd({
  command: "logout [name]",
  describe: "remove OAuth credentials for an MCP server",
  builder: (yargs) =>
    yargs.positional("name", {
      describe: "name of the MCP server",
      type: "string",
    }),
  async handler(args) {
    await Instance.provide({
      directory: process.cwd(),
      async fn() {
        UI.empty()
        prompts.intro("MCP OAuth 登出")

        const authPath = path.join(Global.Path.data, "mcp-auth.json")
        const credentials = await McpAuth.all()
        const serverNames = Object.keys(credentials)

        if (serverNames.length === 0) {
          prompts.log.warn("未存储 MCP OAuth 凭据")
          prompts.outro("完成")
          return
        }

        let serverName = args.name
        if (!serverName) {
          const selected = await prompts.select({
            message: "选择要登出的 MCP 服务器",
            options: serverNames.map((name) => {
              const entry = credentials[name]
              const hasTokens = !!entry.tokens
              const hasClient = !!entry.clientInfo
              let hint = ""
              if (hasTokens && hasClient) hint = "令牌 + 客户端"
              else if (hasTokens) hint = "令牌"
              else if (hasClient) hint = "客户端注册"
              return {
                label: name,
                value: name,
                hint,
              }
            }),
          })
          if (prompts.isCancel(selected)) throw new UI.CancelledError()
          serverName = selected
        }

        if (!credentials[serverName]) {
          prompts.log.error(`未找到凭据: ${serverName}`)
          prompts.outro("完成")
          return
        }

        await MCP.removeAuth(serverName)
        prompts.log.success(`已删除 ${serverName} 的 OAuth 凭据`)
        prompts.outro("完成")
      },
    })
  },
})

export const McpAddCommand = cmd({
  command: "add",
  describe: "add an MCP server",
  async handler() {
    UI.empty()
    prompts.intro("添加 MCP 服务器")

    const name = await prompts.text({
      message: "输入 MCP 服务器名称",
      validate: (x) => (x && x.length > 0 ? undefined : "必填"),
    })
    if (prompts.isCancel(name)) throw new UI.CancelledError()

    const type = await prompts.select({
      message: "选择 MCP 服务器类型",
      options: [
        {
          label: "本地",
          value: "local",
          hint: "运行本地命令",
        },
        {
          label: "远程",
          value: "remote",
          hint: "连接到远程 URL",
        },
      ],
    })
    if (prompts.isCancel(type)) throw new UI.CancelledError()

    if (type === "local") {
      const command = await prompts.text({
        message: "输入要运行的命令",
        placeholder: "例如: opencode x @modelcontextprotocol/server-filesystem",
        validate: (x) => (x && x.length > 0 ? undefined : "必填"),
      })
      if (prompts.isCancel(command)) throw new UI.CancelledError()

      prompts.log.info(`本地 MCP 服务器 "${name}" 已配置命令: ${command}`)
      prompts.outro("MCP 服务器添加成功")
      return
    }

    if (type === "remote") {
      const url = await prompts.text({
        message: "输入 MCP 服务器 URL",
        placeholder: "例如: https://example.com/mcp",
        validate: (x) => {
          if (!x) return "必填"
          if (x.length === 0) return "必填"
          const isValid = URL.canParse(x)
          return isValid ? undefined : "无效的 URL"
        },
      })
      if (prompts.isCancel(url)) throw new UI.CancelledError()

      const useOAuth = await prompts.confirm({
        message: "此服务器是否需要 OAuth 认证？",
        initialValue: false,
      })
      if (prompts.isCancel(useOAuth)) throw new UI.CancelledError()

      if (useOAuth) {
        const hasClientId = await prompts.confirm({
          message: "您是否有预注册的客户端 ID？",
          initialValue: false,
        })
        if (prompts.isCancel(hasClientId)) throw new UI.CancelledError()

        if (hasClientId) {
          const clientId = await prompts.text({
            message: "输入客户端 ID",
            validate: (x) => (x && x.length > 0 ? undefined : "必填"),
          })
          if (prompts.isCancel(clientId)) throw new UI.CancelledError()

          const hasSecret = await prompts.confirm({
            message: "您是否有客户端密钥？",
            initialValue: false,
          })
          if (prompts.isCancel(hasSecret)) throw new UI.CancelledError()

          let clientSecret: string | undefined
          if (hasSecret) {
            const secret = await prompts.password({
              message: "输入客户端密钥",
            })
            if (prompts.isCancel(secret)) throw new UI.CancelledError()
            clientSecret = secret
          }

          prompts.log.info(`远程 MCP 服务器 "${name}" 已配置 OAuth (客户端 ID: ${clientId})`)
          prompts.log.info("将此添加到您的 opencode.json:")
          prompts.log.info(`
  "mcp": {
    "${name}": {
      "type": "remote",
      "url": "${url}",
      "oauth": {
        "clientId": "${clientId}"${clientSecret ? `,\n        "clientSecret": "${clientSecret}"` : ""}
      }
    }
  }`)
        } else {
          prompts.log.info(`远程 MCP 服务器 "${name}" 已配置 OAuth (动态注册)`)
          prompts.log.info("将此添加到您的 opencode.json:")
          prompts.log.info(`
  "mcp": {
    "${name}": {
      "type": "remote",
      "url": "${url}",
      "oauth": {}
    }
  }`)
        }
      } else {
        const client = new Client({
          name: "opencode",
          version: "1.0.0",
        })
        const transport = new StreamableHTTPClientTransport(new URL(url))
        await client.connect(transport)
        prompts.log.info(`远程 MCP 服务器 "${name}" 已配置 URL: ${url}`)
      }
    }

    prompts.outro("MCP 服务器添加成功")
  },
})

export const McpDebugCommand = cmd({
  command: "debug <name>",
  describe: "debug OAuth connection for an MCP server",
  builder: (yargs) =>
    yargs.positional("name", {
      describe: "name of the MCP server",
      type: "string",
      demandOption: true,
    }),
  async handler(args) {
    await Instance.provide({
      directory: process.cwd(),
      async fn() {
        UI.empty()
        prompts.intro("MCP OAuth 调试")

        const config = await Config.get()
        const mcpServers = config.mcp ?? {}
        const serverName = args.name

        const serverConfig = mcpServers[serverName]
        if (!serverConfig) {
          prompts.log.error(`未找到 MCP 服务器: ${serverName}`)
          prompts.outro("完成")
          return
        }

        if (!isMcpRemote(serverConfig)) {
          prompts.log.error(`MCP 服务器 ${serverName} 不是远程服务器`)
          prompts.outro("完成")
          return
        }

        if (serverConfig.oauth === false) {
          prompts.log.warn(`MCP 服务器 ${serverName} 已显式禁用 OAuth`)
          prompts.outro("完成")
          return
        }

        prompts.log.info(`服务器: ${serverName}`)
        prompts.log.info(`URL: ${serverConfig.url}`)

        // Check stored auth status
        const authStatus = await MCP.getAuthStatus(serverName)
        prompts.log.info(`认证状态: ${getAuthStatusIcon(authStatus)} ${getAuthStatusText(authStatus)}`)

        const entry = await McpAuth.get(serverName)
        if (entry?.tokens) {
          prompts.log.info(`  Access token: ${entry.tokens.accessToken.substring(0, 20)}...`)
          if (entry.tokens.expiresAt) {
            const expiresDate = new Date(entry.tokens.expiresAt * 1000)
            const isExpired = entry.tokens.expiresAt < Date.now() / 1000
            prompts.log.info(`  Expires: ${expiresDate.toISOString()} ${isExpired ? "(EXPIRED)" : ""}`)
          }
          if (entry.tokens.refreshToken) {
            prompts.log.info(`  Refresh token: present`)
          }
        }
        if (entry?.clientInfo) {
          prompts.log.info(`  Client ID: ${entry.clientInfo.clientId}`)
          if (entry.clientInfo.clientSecretExpiresAt) {
            const expiresDate = new Date(entry.clientInfo.clientSecretExpiresAt * 1000)
            prompts.log.info(`  Client secret expires: ${expiresDate.toISOString()}`)
          }
        }

        const spinner = prompts.spinner()
        spinner.start("测试连接...")

        // Test basic HTTP connectivity first
        try {
          const response = await fetch(serverConfig.url, {
            method: "POST",
            headers: {
              "Content-Type": "application/json",
              Accept: "application/json, text/event-stream",
            },
            body: JSON.stringify({
              jsonrpc: "2.0",
              method: "initialize",
              params: {
                protocolVersion: "2024-11-05",
                capabilities: {},
                clientInfo: { name: "opencode-debug", version: Installation.VERSION },
              },
              id: 1,
            }),
          })

          spinner.stop(`HTTP 响应: ${response.status} ${response.statusText}`)

          // Check for WWW-Authenticate header
          const wwwAuth = response.headers.get("www-authenticate")
          if (wwwAuth) {
            prompts.log.info(`WWW-Authenticate: ${wwwAuth}`)
          }

          if (response.status === 401) {
            prompts.log.warn("服务器返回 401 未授权")

            // Try to discover OAuth metadata
            const oauthConfig = typeof serverConfig.oauth === "object" ? serverConfig.oauth : undefined
            const authProvider = new McpOAuthProvider(
              serverName,
              serverConfig.url,
              {
                clientId: oauthConfig?.clientId,
                clientSecret: oauthConfig?.clientSecret,
                scope: oauthConfig?.scope,
              },
              {
                onRedirect: async () => {},
              },
            )

            prompts.log.info("测试 OAuth 流程 (不完成授权)...")

            // Try creating transport with auth provider to trigger discovery
            const transport = new StreamableHTTPClientTransport(new URL(serverConfig.url), {
              authProvider,
            })

            try {
              const client = new Client({
                name: "opencode-debug",
                version: Installation.VERSION,
              })
              await client.connect(transport)
              prompts.log.success("连接成功 (已认证)")
              await client.close()
            } catch (error) {
              if (error instanceof UnauthorizedError) {
                prompts.log.info(`OAuth 流程已触发: ${error.message}`)

                // Check if dynamic registration would be attempted
                const clientInfo = await authProvider.clientInformation()
                if (clientInfo) {
                  prompts.log.info(`客户端 ID 可用: ${clientInfo.client_id}`)
                } else {
                  prompts.log.info("无客户端 ID - 将尝试动态注册")
                }
              } else {
                prompts.log.error(`连接错误: ${error instanceof Error ? error.message : String(error)}`)
              }
            }
          } else if (response.status >= 200 && response.status < 300) {
            prompts.log.success("服务器响应成功 (无需认证或已认证)")
            const body = await response.text()
            try {
              const json = JSON.parse(body)
              if (json.result?.serverInfo) {
                prompts.log.info(`服务器信息: ${JSON.stringify(json.result.serverInfo)}`)
              }
            } catch {
              // Not JSON, ignore
            }
          } else {
            prompts.log.warn(`意外状态: ${response.status}`)
            const body = await response.text().catch(() => "")
            if (body) {
              prompts.log.info(`响应体: ${body.substring(0, 500)}`)
            }
          }
        } catch (error) {
          spinner.stop("连接失败", 1)
          prompts.log.error(`错误: ${error instanceof Error ? error.message : String(error)}`)
        }

        prompts.outro("调试完成")
      },
    })
  },
})
