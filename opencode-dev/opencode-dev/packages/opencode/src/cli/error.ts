import { ConfigMarkdown } from "@/config/markdown"
import { Config } from "../config/config"
import { MCP } from "../mcp"
import { Provider } from "../provider/provider"
import { UI } from "./ui"

export function FormatError(input: unknown) {
  if (MCP.Failed.isInstance(input))
    return `MCP 服务器 "${input.data.name}" 失败。注意，opencode 目前还不支持 MCP 认证。`
  if (Provider.ModelNotFoundError.isInstance(input)) {
    const { providerID, modelID, suggestions } = input.data
    return [
      `未找到模型: ${providerID}/${modelID}`,
      ...(Array.isArray(suggestions) && suggestions.length ? ["您是指: " + suggestions.join(", ")] : []),
      `尝试: \`opencode models\` 列出可用模型`,
      `或检查您的配置文件 (opencode.json) 中的提供商/模型名称`,
    ].join("\n")
  }
  if (Provider.InitError.isInstance(input)) {
    return `初始化提供商 "${input.data.providerID}" 失败。请检查凭据和配置。`
  }
  if (Config.JsonError.isInstance(input)) {
    return `配置文件 ${input.data.path} 不是有效的 JSON(C) 格式` + (input.data.message ? `: ${input.data.message}` : "")
  }
  if (Config.ConfigDirectoryTypoError.isInstance(input)) {
    return `目录 "${input.data.dir}" 在 ${input.data.path} 中无效。请将目录重命名为 "${input.data.suggestion}" 或删除它。这是一个常见的拼写错误。`
  }
  if (ConfigMarkdown.FrontmatterError.isInstance(input)) {
    return `解析 ${input.data.path} 中的前置元数据失败:\n${input.data.message}`
  }
  if (Config.InvalidError.isInstance(input))
    return [
      `配置无效${input.data.path && input.data.path !== "config" ? ` (位置: ${input.data.path})` : ""}` +
        (input.data.message ? `: ${input.data.message}` : ""),
      ...(input.data.issues?.map((issue) => "↳ " + issue.message + " " + issue.path.join(".")) ?? []),
    ].join("\n")

  if (UI.CancelledError.isInstance(input)) return ""
}

export function FormatUnknownError(input: unknown): string {
  if (input instanceof Error) {
    return input.stack ?? `${input.name}: ${input.message}`
  }

  if (typeof input === "object" && input !== null) {
    try {
      return JSON.stringify(input, null, 2)
    } catch {
      return "Unexpected error (unserializable)"
    }
  }

  return String(input)
}
