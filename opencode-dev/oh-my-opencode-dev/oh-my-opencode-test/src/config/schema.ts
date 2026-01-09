import { z } from "zod"
import { AnyMcpNameSchema, McpNameSchema } from "../mcp/types"

const PermissionValue = z.enum(["ask", "allow", "deny"])

const BashPermission = z.union([
  PermissionValue,
  z.record(z.string(), PermissionValue),
])

const AgentPermissionSchema = z.object({
  edit: PermissionValue.optional(),
  bash: BashPermission.optional(),
  webfetch: PermissionValue.optional(),
  doom_loop: PermissionValue.optional(),
  external_directory: PermissionValue.optional(),
})

export const BuiltinAgentNameSchema = z.enum([
  "Sisyphus",
  "oracle",
  "librarian",
  "explore",
  "frontend-ui-ux-engineer",
  "document-writer",
  "multimodal-looker",
])

export const BuiltinSkillNameSchema = z.enum([
  "playwright",
])

export const OverridableAgentNameSchema = z.enum([
  "build",
  "plan",
  "Sisyphus",
  "OpenCode-Builder",
  "Planner-Sisyphus",
  "oracle",
  "librarian",
  "explore",
  "frontend-ui-ux-engineer",
  "document-writer",
  "multimodal-looker",
])

export const AgentNameSchema = BuiltinAgentNameSchema

export const HookNameSchema = z.enum([
  "todo-continuation-enforcer",
  "context-window-monitor",
  "session-recovery",
  "session-notification",
  "comment-checker",
  "grep-output-truncator",
  "tool-output-truncator",
  "directory-agents-injector",
  "directory-readme-injector",
  "empty-task-response-detector",
  "think-mode",
  "anthropic-context-window-limit-recovery",
  "rules-injector",
  "background-notification",
  "auto-update-checker",
  "startup-toast",
  "keyword-detector",
  "agent-usage-reminder",
  "non-interactive-env",
  "interactive-bash-session",
  "empty-message-sanitizer",
  "thinking-block-validator",
  "ralph-loop",
  "preemptive-compaction",
  "compaction-context-injector",
  "claude-code-hooks",
  "auto-slash-command",
  "edit-error-recovery",
])

export const BuiltinCommandNameSchema = z.enum([
  "init-deep",
])

export const AgentOverrideConfigSchema = z.object({
  model: z.string().optional(),
  temperature: z.number().min(0).max(2).optional(),
  top_p: z.number().min(0).max(1).optional(),
  prompt: z.string().optional(),
  prompt_append: z.string().optional(),
  tools: z.record(z.string(), z.boolean()).optional(),
  disable: z.boolean().optional(),
  description: z.string().optional(),
  mode: z.enum(["subagent", "primary", "all"]).optional(),
  color: z
    .string()
    .regex(/^#[0-9A-Fa-f]{6}$/)
    .optional(),
  permission: AgentPermissionSchema.optional(),
})

export const AgentOverridesSchema = z.object({
  build: AgentOverrideConfigSchema.optional(),
  plan: AgentOverrideConfigSchema.optional(),
  Sisyphus: AgentOverrideConfigSchema.optional(),
  "OpenCode-Builder": AgentOverrideConfigSchema.optional(),
  "Planner-Sisyphus": AgentOverrideConfigSchema.optional(),
  oracle: AgentOverrideConfigSchema.optional(),
  librarian: AgentOverrideConfigSchema.optional(),
  explore: AgentOverrideConfigSchema.optional(),
  "frontend-ui-ux-engineer": AgentOverrideConfigSchema.optional(),
  "document-writer": AgentOverrideConfigSchema.optional(),
  "multimodal-looker": AgentOverrideConfigSchema.optional(),
})

export const ClaudeCodeConfigSchema = z.object({
  mcp: z.boolean().optional(),
  commands: z.boolean().optional(),
  skills: z.boolean().optional(),
  agents: z.boolean().optional(),
  hooks: z.boolean().optional(),
  plugins: z.boolean().optional(),
  plugins_override: z.record(z.string(), z.boolean()).optional(),
})

export const SisyphusAgentConfigSchema = z.object({
  disabled: z.boolean().optional(),
  default_builder_enabled: z.boolean().optional(),
  planner_enabled: z.boolean().optional(),
  replace_plan: z.boolean().optional(),
})

export const CommentCheckerConfigSchema = z.object({
  /** 自定义提示词以替换默认警告消息。使用 {{comments}} 占位符表示检测到的注释 XML。 */
  custom_prompt: z.string().optional(),
})

export const DynamicContextPruningConfigSchema = z.object({
  /** 启用动态上下文修剪（默认：false） */
  enabled: z.boolean().default(false),
  /** 通知级别：off（关闭）、minimal（最小化）或 detailed（详细）（默认：detailed） */
  notification: z.enum(["off", "minimal", "detailed"]).default("detailed"),
  /** 轮次保护 - 防止修剪最近的工作输出 */
  turn_protection: z.object({
    enabled: z.boolean().default(true),
    turns: z.number().min(1).max(10).default(3),
  }).optional(),
  /** 永远不应被修剪的工具 */
  protected_tools: z.array(z.string()).default([
    "task", "todowrite", "todoread",
    "lsp_rename", "lsp_code_action_resolve",
    "session_read", "session_write", "session_search",
  ]),
  /** 修剪策略配置 */
  strategies: z.object({
    /** 移除重复的工具调用（相同工具 + 相同参数） */
    deduplication: z.object({
      enabled: z.boolean().default(true),
    }).optional(),
    /** 当文件随后被读取时，修剪写入输入 */
    supersede_writes: z.object({
      enabled: z.boolean().default(true),
      /** 激进模式：如果任何后续读取则修剪任何写入 */
      aggressive: z.boolean().default(false),
    }).optional(),
    /** 在 N 轮后修剪错误的工作输入 */
    purge_errors: z.object({
      enabled: z.boolean().default(true),
      turns: z.number().min(1).max(20).default(5),
    }).optional(),
  }).optional(),
})

export const ExperimentalConfigSchema = z.object({
  aggressive_truncation: z.boolean().optional(),
  auto_resume: z.boolean().optional(),
  /** 在阈值处启用抢先压缩（自 v2.9.0 起默认为 true） */
  preemptive_compaction: z.boolean().optional(),
  /** 触发抢先压缩的阈值百分比（默认：0.80） */
  preemptive_compaction_threshold: z.number().min(0.5).max(0.95).optional(),
  /** 截断所有工具输出，而不仅仅是白名单工具（默认：false）。工具输出截断器默认已启用 - 通过 disabled_hooks 禁用。 */
  truncate_all_tool_outputs: z.boolean().optional(),
  /** 动态上下文修剪配置 */
  dynamic_context_pruning: DynamicContextPruningConfigSchema.optional(),
  /** 为压缩启用 DCP（动态上下文修剪）- 当超出 token 限制时首先运行（默认：false） */
  dcp_for_compaction: z.boolean().optional(),
})

export const SkillSourceSchema = z.union([
  z.string(),
  z.object({
    path: z.string(),
    recursive: z.boolean().optional(),
    glob: z.string().optional(),
  }),
])

export const SkillDefinitionSchema = z.object({
  description: z.string().optional(),
  template: z.string().optional(),
  from: z.string().optional(),
  model: z.string().optional(),
  agent: z.string().optional(),
  subtask: z.boolean().optional(),
  "argument-hint": z.string().optional(),
  license: z.string().optional(),
  compatibility: z.string().optional(),
  metadata: z.record(z.string(), z.unknown()).optional(),
  "allowed-tools": z.array(z.string()).optional(),
  disable: z.boolean().optional(),
})

export const SkillEntrySchema = z.union([
  z.boolean(),
  SkillDefinitionSchema,
])

export const SkillsConfigSchema = z.union([
  z.array(z.string()),
  z.record(z.string(), SkillEntrySchema).and(z.object({
    sources: z.array(SkillSourceSchema).optional(),
    enable: z.array(z.string()).optional(),
    disable: z.array(z.string()).optional(),
  }).partial()),
])

export const RalphLoopConfigSchema = z.object({
  /** 启用 ralph loop 功能（默认：false - 可选功能） */
  enabled: z.boolean().default(false),
  /** 如果在命令中未指定，则为默认最大迭代次数（默认：100） */
  default_max_iterations: z.number().min(1).max(1000).default(100),
  /** 相对于项目根目录的自定义状态文件目录（默认：.opencode/） */
  state_dir: z.string().optional(),
})

export const BackgroundTaskConfigSchema = z.object({
  defaultConcurrency: z.number().min(1).optional(),
  providerConcurrency: z.record(z.string(), z.number().min(1)).optional(),
  modelConcurrency: z.record(z.string(), z.number().min(1)).optional(),
})

export const OhMyOpenCodeConfigSchema = z.object({
  $schema: z.string().optional(),
  disabled_mcps: z.array(AnyMcpNameSchema).optional(),
  disabled_agents: z.array(BuiltinAgentNameSchema).optional(),
  disabled_skills: z.array(BuiltinSkillNameSchema).optional(),
  disabled_hooks: z.array(HookNameSchema).optional(),
  disabled_commands: z.array(BuiltinCommandNameSchema).optional(),
  agents: AgentOverridesSchema.optional(),
  claude_code: ClaudeCodeConfigSchema.optional(),
  google_auth: z.boolean().optional(),
  sisyphus_agent: SisyphusAgentConfigSchema.optional(),
  comment_checker: CommentCheckerConfigSchema.optional(),
  experimental: ExperimentalConfigSchema.optional(),
  auto_update: z.boolean().optional(),
  skills: SkillsConfigSchema.optional(),
  ralph_loop: RalphLoopConfigSchema.optional(),
  background_task: BackgroundTaskConfigSchema.optional(),
})

export type OhMyOpenCodeConfig = z.infer<typeof OhMyOpenCodeConfigSchema>
export type AgentOverrideConfig = z.infer<typeof AgentOverrideConfigSchema>
export type AgentOverrides = z.infer<typeof AgentOverridesSchema>
export type BackgroundTaskConfig = z.infer<typeof BackgroundTaskConfigSchema>
export type AgentName = z.infer<typeof AgentNameSchema>
export type HookName = z.infer<typeof HookNameSchema>
export type BuiltinCommandName = z.infer<typeof BuiltinCommandNameSchema>
export type BuiltinSkillName = z.infer<typeof BuiltinSkillNameSchema>
export type SisyphusAgentConfig = z.infer<typeof SisyphusAgentConfigSchema>
export type CommentCheckerConfig = z.infer<typeof CommentCheckerConfigSchema>
export type ExperimentalConfig = z.infer<typeof ExperimentalConfigSchema>
export type DynamicContextPruningConfig = z.infer<typeof DynamicContextPruningConfigSchema>
export type SkillsConfig = z.infer<typeof SkillsConfigSchema>
export type SkillDefinition = z.infer<typeof SkillDefinitionSchema>
export type RalphLoopConfig = z.infer<typeof RalphLoopConfigSchema>

export { AnyMcpNameSchema, type AnyMcpName, McpNameSchema, type McpName } from "../mcp/types"
