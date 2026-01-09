# 项目知识库

**生成时间：** 2026-01-02T22:41:22+09:00
**Commit：** d0694e5
**分支：** dev

## 概述

OpenCode 插件：多模型 Agent 编排（Claude Opus 4.5, GPT-5.2, Gemini 3, Grok），11 个 LSP 工具，AST-Grep，Claude Code 兼容层。OpenCode 的 "oh-my-zsh"。

## 项目结构

```
oh-my-opencode/
├── src/
│   ├── agents/        # 7 个 AI Agent - 见 src/agents/AGENTS.md
│   ├── hooks/         # 22 个生命周期钩子 - 见 src/hooks/AGENTS.md
│   ├── tools/         # LSP, AST-Grep, 会话管理 - 见 src/tools/AGENTS.md
│   ├── features/      # Claude Code 兼容层 - 见 src/features/AGENTS.md
│   ├── auth/          # Google Antigravity OAuth - 见 src/auth/AGENTS.md
│   ├── shared/        # 跨模块通用工具 - 见 src/shared/AGENTS.md
│   ├── cli/           # CLI 安装器、诊断工具 - 见 src/cli/AGENTS.md
│   ├── mcp/           # MCP 配置：context7, grep_app
│   ├── config/        # Zod schema，TypeScript 类型定义
│   └── index.ts       # 主插件入口（464 行）
├── script/            # build-schema.ts, publish.ts, generate-changelog.ts
└── dist/              # 构建输出（ESM + .d.ts）
```

## 快速定位

| 任务 | 位置 | 备注 |
|------|----------|-------|
| 添加 Agent | `src/agents/` | 创建 .ts，添加到 builtinAgents，更新 types.ts |
| 添加 Hook | `src/hooks/` | 目录包含 createXXXHook()，从 index.ts 导出 |
| 添加 Tool | `src/tools/` | 目录包含 constants/types/tools.ts，添加到 builtinTools |
| 添加 MCP | `src/mcp/` | 创建配置，添加到 index.ts |
| 添加 Skill | `src/features/builtin-skills/` | 目录包含 SKILL.md |
| 配置 Schema | `src/config/schema.ts` | 之后运行 `bun run build:schema` |
| Claude Code 兼容 | `src/features/claude-code-*-loader/` | Command, skill, agent, mcp 加载器 |

## TDD（测试驱动开发）

**新功能和 bug 修复必须遵循。** 遵循 RED-GREEN-REFACTOR 流程：

```
1. RED    - 先写失败的测试（测试必须失败）
2. GREEN  - 写最少代码通过测试（不多不少）
3. REFACTOR - 清理代码，测试保持 GREEN
4. REPEAT - 下一个测试用例
```

| 阶段 | 动作 | 验证 |
|-------|--------|--------------|
| **RED** | 编写描述期望行为的测试 | `bun test` → FAIL（预期） |
| **GREEN** | 实现最少代码通过测试 | `bun test` → PASS |
| **REFACTOR** | 改进代码质量，消除重复 | `bun test` → PASS（必须保持绿色） |

**规则：**
- 绝不在测试之前写实现代码
- 绝不删除失败的测试来"通过"——修复代码
- 一次一个测试——不要批量
- 测试文件命名：`*.test.ts`，与源文件并列

## 约定规范

- **仅使用 Bun**: `bun run`, `bun test`, `bunx`（绝不使用 npm/npx）
- **类型定义**: bun-types（而非 @types/node）
- **构建**: `bun build` (ESM) + `tsc --emitDeclarationOnly`
- **导出**: index.ts 中使用 barrel 模式；tools/hooks 使用显式命名导出
- **命名**: 目录使用 kebab-case，工厂函数使用 createXXXHook/createXXXTool
- **测试**: BDD 注释 `#given`, `#when`, `#then`（等同于 AAA）；TDD 工作流（RED-GREEN-REFACTOR）
- **温度**: 编码 Agent 使用 0.1，最高 0.3

## 反模式（禁止项）

| 类别 | 禁止项 |
|----------|-----------|
| 类型安全 | `as any`, `@ts-ignore`, `@ts-expect-error` |
| 包管理器 | npm, yarn, npx |
| 文件操作 | 使用 Bash mkdir/touch/rm 创建代码文件 |
| 发布 | 直接 `bun publish`，本地版本号修改 |
| Agent 行为 | 高温度（>0.3），广泛的工具访问，串行调用 Agent |
| Hooks | 严重的 PreToolUse 逻辑，无理由阻塞 |
| 年份 | 代码/提示词中使用 2024（应使用当前年份） |

## Agent 模型

| Agent | 默认模型 | 用途 |
|-------|-------|---------|
| Sisyphus | anthropic/claude-opus-4-5 | 主编排器 |
| oracle | openai/gpt-5.2 | 策略、代码审查 |
| librarian | anthropic/claude-sonnet-4-5 | 文档、开源研究 |
| explore | opencode/grok-code | 快速代码库搜索 |
| frontend-ui-ux-engineer | google/gemini-3-pro-preview | UI 生成 |
| document-writer | google/gemini-3-pro-preview | 技术文档 |
| multimodal-looker | google/gemini-3-flash | PDF/图像分析 |

## 命令

```bash
bun run typecheck      # 类型检查
bun run build          # ESM + 类型声明 + schema
bun run rebuild        # 清理 + 构建
bun test               # 运行测试（380+）
```

## 部署

**仅限 GitHub Actions workflow_dispatch**

1. 绝不在本地修改 package.json 版本号
2. 提交并推送到 dev 分支
3. 触发：`gh workflow run publish -f bump=patch|minor|major`

CI 会自动提交 master 分支的 schema 变更，维护 dev 分支上的 `next` 草稿版本。

## 复杂热点

| 文件 | 行数 | 描述 |
|------|-------|-------------|
| `src/index.ts` | 464 | 主插件，所有 hook/tool 初始化 |
| `src/cli/config-manager.ts` | 669 | JSONC 解析，环境变量检测 |
| `src/auth/antigravity/fetch.ts` | 621 | Token 刷新，URL 重写 |
| `src/tools/lsp/client.ts` | 611 | LSP 协议，JSON-RPC |
| `src/hooks/anthropic-context-window-limit-recovery/executor.ts` | 564 | 多阶段恢复 |
| `src/agents/sisyphus.ts` | 504 | 编排器提示词 |

## 备注

- **OpenCode**: 要求 >= 1.0.150
- **配置**: `~/.config/opencode/oh-my-opencode.json` 或 `.opencode/oh-my-opencode.json`
- **JSONC**: 配置文件支持注释和尾随逗号
- **Claude Code**: settings.json hooks、commands、skills、agents、MCPs 的完整兼容层
- **Skill MCP**: Skills 可以在 YAML 前置元数据中嵌入 MCP 服务器配置
