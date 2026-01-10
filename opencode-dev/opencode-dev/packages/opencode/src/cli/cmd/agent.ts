import { cmd } from "./cmd"
import * as prompts from "@clack/prompts"
import { UI } from "../ui"
import { Global } from "../../global"
import { Agent } from "../../agent/agent"
import { Provider } from "../../provider/provider"
import path from "path"
import fs from "fs/promises"
import matter from "gray-matter"
import { Instance } from "../../project/instance"
import { EOL } from "os"
import type { Argv } from "yargs"

type AgentMode = "all" | "primary" | "subagent"

const AVAILABLE_TOOLS = [
  "bash",
  "read",
  "write",
  "edit",
  "list",
  "glob",
  "grep",
  "webfetch",
  "task",
  "todowrite",
  "todoread",
]

const AgentCreateCommand = cmd({
  command: "create",
  describe: "create a new agent",
  builder: (yargs: Argv) =>
    yargs
      .option("path", {
        type: "string",
        describe: "directory path to generate the agent file",
      })
      .option("description", {
        type: "string",
        describe: "what the agent should do",
      })
      .option("mode", {
        type: "string",
        describe: "agent mode",
        choices: ["all", "primary", "subagent"] as const,
      })
      .option("tools", {
        type: "string",
        describe: `comma-separated list of tools to enable (default: all). Available: "${AVAILABLE_TOOLS.join(", ")}"`,
      })
      .option("model", {
        type: "string",
        alias: ["m"],
        describe: "model to use in the format of provider/model",
      }),
  async handler(args) {
    await Instance.provide({
      directory: process.cwd(),
      async fn() {
        const cliPath = args.path
        const cliDescription = args.description
        const cliMode = args.mode as AgentMode | undefined
        const cliTools = args.tools

        const isFullyNonInteractive = cliPath && cliDescription && cliMode && cliTools !== undefined

        if (!isFullyNonInteractive) {
          UI.empty()
          prompts.intro("创建 Agent")
        }

        const project = Instance.project

        // Determine scope/path
        let targetPath: string
        if (cliPath) {
          targetPath = path.join(cliPath, "agent")
        } else {
          let scope: "global" | "project" = "global"
          if (project.vcs === "git") {
            const scopeResult = await prompts.select({
              message: "位置",
              options: [
                {
                  label: "当前项目",
                  value: "project" as const,
                  hint: Instance.worktree,
                },
                {
                  label: "全局",
                  value: "global" as const,
                  hint: Global.Path.config,
                },
              ],
            })
            if (prompts.isCancel(scopeResult)) throw new UI.CancelledError()
            scope = scopeResult
          }
          targetPath = path.join(
            scope === "global" ? Global.Path.config : path.join(Instance.worktree, ".opencode"),
            "agent",
          )
        }

        // Get description
        let description: string
        if (cliDescription) {
          description = cliDescription
        } else {
          const query = await prompts.text({
            message: "描述",
            placeholder: "这个 Agent 应该做什么？",
            validate: (x) => (x && x.length > 0 ? undefined : "必填"),
          })
          if (prompts.isCancel(query)) throw new UI.CancelledError()
          description = query
        }

        // Generate agent
        const spinner = prompts.spinner()
        spinner.start("生成 Agent 配置...")
        const model = args.model ? Provider.parseModel(args.model) : undefined
        const generated = await Agent.generate({ description, model }).catch((error) => {
          spinner.stop(`LLM 生成 Agent 失败: ${error.message}`, 1)
          if (isFullyNonInteractive) process.exit(1)
          throw new UI.CancelledError()
        })
        spinner.stop(`Agent ${generated.identifier} 已生成`)

        // Select tools
        let selectedTools: string[]
        if (cliTools !== undefined) {
          selectedTools = cliTools ? cliTools.split(",").map((t) => t.trim()) : AVAILABLE_TOOLS
        } else {
          const result = await prompts.multiselect({
            message: "选择要启用的工具",
            options: AVAILABLE_TOOLS.map((tool) => ({
              label: tool,
              value: tool,
            })),
            initialValues: AVAILABLE_TOOLS,
          })
          if (prompts.isCancel(result)) throw new UI.CancelledError()
          selectedTools = result
        }

        // Get mode
        let mode: AgentMode
        if (cliMode) {
          mode = cliMode
        } else {
          const modeResult = await prompts.select({
            message: "Agent 模式",
            options: [
              {
                label: "全部",
                value: "all" as const,
                hint: "可作为主 Agent 和子 Agent 使用",
              },
              {
                label: "主 Agent",
                value: "primary" as const,
                hint: "作为主/顶层 Agent",
              },
              {
                label: "子 Agent",
                value: "subagent" as const,
                hint: "可被其他 Agent 作为子 Agent 调用",
              },
            ],
            initialValue: "all" as const,
          })
          if (prompts.isCancel(modeResult)) throw new UI.CancelledError()
          mode = modeResult
        }

        // Build tools config
        const tools: Record<string, boolean> = {}
        for (const tool of AVAILABLE_TOOLS) {
          if (!selectedTools.includes(tool)) {
            tools[tool] = false
          }
        }

        // Build frontmatter
        const frontmatter: {
          description: string
          mode: AgentMode
          tools?: Record<string, boolean>
        } = {
          description: generated.whenToUse,
          mode,
        }
        if (Object.keys(tools).length > 0) {
          frontmatter.tools = tools
        }

        // Write file
        const content = matter.stringify(generated.systemPrompt, frontmatter)
        const filePath = path.join(targetPath, `${generated.identifier}.md`)

        await fs.mkdir(targetPath, { recursive: true })

        const file = Bun.file(filePath)
        if (await file.exists()) {
          if (isFullyNonInteractive) {
            console.error(`Error: Agent file already exists: ${filePath}`)
            process.exit(1)
          }
          prompts.log.error(`Agent 文件已存在: ${filePath}`)
          throw new UI.CancelledError()
        }

        await Bun.write(filePath, content)

        if (isFullyNonInteractive) {
          console.log(filePath)
        } else {
          prompts.log.success(`Agent 已创建: ${filePath}`)
          prompts.outro("完成")
        }
      },
    })
  },
})

const AgentListCommand = cmd({
  command: "list",
  describe: "list all available agents",
  async handler() {
    await Instance.provide({
      directory: process.cwd(),
      async fn() {
        const agents = await Agent.list()
        const sortedAgents = agents.sort((a, b) => {
          if (a.native !== b.native) {
            return a.native ? -1 : 1
          }
          return a.name.localeCompare(b.name)
        })

        for (const agent of sortedAgents) {
          process.stdout.write(`${agent.name} (${agent.mode})` + EOL)
          process.stdout.write(`  ${JSON.stringify(agent.permission, null, 2)}` + EOL)
        }
      },
    })
  },
})

export const AgentCommand = cmd({
  command: "agent",
  describe: "manage agents",
  builder: (yargs) => yargs.command(AgentCreateCommand).command(AgentListCommand).demandCommand(),
  async handler() {},
})
