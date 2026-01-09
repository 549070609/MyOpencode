# oh-my-opencode 国际化 (i18n) 使用指南

## 概述

oh-my-opencode 现已支持中英文双语。通过简单的配置即可切换语言。

## 支持的语言

- **English** (`en`) - 默认语言
- **简体中文** (`zh-CN`)

## 快速开始

### 1. 配置语言

在配置文件中添加 `language` 字段：

**全局配置** (`~/.config/opencode/oh-my-opencode.json`)：
```json
{
  "language": "zh-CN"
}
```

**项目配置** (`./.opencode/oh-my-opencode.json`)：
```json
{
  "language": "zh-CN"
}
```

### 2. 重启 OpenCode

配置修改后，重启 OpenCode 即可生效。

## 汉化内容

### ✅ 已汉化

- **Agents (AI 代理)**
  - Sisyphus - 主编排代理
  - Oracle - 策略顾问
  - Librarian - 文档研究员
  - Explore - 代码库探索者
  - Frontend UI/UX Engineer - 前端工程师
  - Document Writer - 文档编写者
  - Multimodal Looker - 多模态分析师

- **Tools (工具)**
  - 所有工具的描述信息
  - LSP 工具集
  - AST-Grep
  - Background Task
  - 等等...

- **配置系统**
  - 支持语言选项
  - 自动加载对应语言

### 🚧 部分汉化

- **CLI 命令行界面** - 框架已就绪，可按需扩展
- **错误消息** - 框架已就绪，可按需扩展

## 配置示例

### 完整配置示例

```json
{
  "$schema": "https://raw.githubusercontent.com/code-yeongyu/oh-my-opencode/master/assets/oh-my-opencode.schema.json",
  "language": "zh-CN",
  "agents": {
    "Sisyphus": {
      "model": "anthropic/claude-opus-4-5",
      "temperature": 0.1
    },
    "oracle": {
      "model": "openai/gpt-5.2"
    }
  }
}
```

### 仅语言配置

```json
{
  "language": "zh-CN"
}
```

## 开发者指南

### 添加新的翻译

1. **编辑语言文件**

   中文翻译：`src/i18n/locales/zh-CN/[模块].ts`
   ```typescript
   export const [模块]ZhCN = {
     key: "中文翻译",
     // ...
   }
   ```

   英文翻译：`src/i18n/locales/en/[模块].ts`
   ```typescript
   export const [模块]En = {
     key: "English translation",
     // ...
   }
   ```

2. **在代码中使用翻译**

   ```typescript
   import { t, getTranslations } from "../i18n"

   // 方式 1: 使用键路径
   const message = t("agents.sisyphus.description")

   // 方式 2: 使用占位符
   const message = t("cli.version.current", { version: "2.14.0" })

   // 方式 3: 获取完整翻译对象
   const translations = getTranslations()
   const description = translations.agents.sisyphus.description
   ```

3. **辅助函数**

   Agents:
   ```typescript
   import { getAgentDescription } from "./agents-i18n"
   const description = getAgentDescription("sisyphus")
   ```

   Tools:
   ```typescript
   import { getToolDescription } from "../tools-i18n"
   const description = getToolDescription("astGrep")
   ```

### 目录结构

```
src/i18n/
├── index.ts                    # i18n 核心函数
├── types.ts                    # TypeScript 类型定义
└── locales/
    ├── en/                     # 英文翻译
    │   ├── agents.ts
    │   ├── tools.ts
    │   ├── cli.ts
    │   ├── common.ts
    │   └── index.ts
    └── zh-CN/                  # 中文翻译
        ├── agents.ts
        ├── agents-prompts.ts   # Agent 提示词
        ├── tools.ts
        ├── cli.ts
        ├── common.ts
        └── index.ts
```

## 架构设计

### 核心功能

- **语言切换**: `setLanguage(language: "en" | "zh-CN")`
- **获取翻译**: `t(key: string, replacements?: Record<string, string>)`
- **获取当前语言**: `getLanguage()`
- **获取翻译对象**: `getTranslations()`

### 加载机制

1. 插件启动时从配置读取 `language` 字段
2. 调用 `setLanguage()` 初始化语言
3. 各模块通过辅助函数获取翻译后的描述
4. Agent 提示词根据语言动态构建

### 类型安全

所有翻译键路径都有 TypeScript 类型检查：

```typescript
export interface I18nTranslations {
  agents: {
    sisyphus: { description: string; ... }
    oracle: { description: string; ... }
    // ...
  }
  tools: { [toolName: string]: { description: string; ... } }
  // ...
}
```

## 常见问题

### Q: 如何切换回英文？

A: 将配置中的 `language` 改为 `"en"` 或删除该字段（默认为英文）。

### Q: 修改语言后没有生效？

A: 需要重启 OpenCode 才能加载新的语言配置。

### Q: 如何为新的 Agent 或 Tool 添加翻译？

A: 
1. 在 `src/i18n/locales/zh-CN/` 对应文件中添加翻译
2. 在 `src/i18n/locales/en/` 对应文件中添加英文原文
3. 在代码中使用辅助函数获取翻译

### Q: CLI 命令是否支持中文？

A: CLI 基础框架已支持，可通过 `t("cli.xxx")` 添加具体翻译。

## 贡献

欢迎贡献更多语言的翻译！请参考现有的 `en` 和 `zh-CN` 目录结构。

## 许可证

与 oh-my-opencode 主项目相同：SUL-1.0
