# OpenCode 自定义模型配置说明

## 概述

OpenCode 支持通过 JSON 配置文件来配置自定义模型，使用 OpenAI 兼容协议。

## 使用方法

### 1. 创建配置文件

复制 `model-config.template.json` 为 `model-config.json`：

```bash
copy model-config.template.json model-config.json
```

### 2. 编辑配置文件

编辑 `model-config.json`，配置你的模型信息。

### 3. 应用配置

运行配置命令：

```bash
py create_doc.py config
```

## 配置文件格式

### 必需字段

```json
{
  "api_url": "https://api.openai.com/v1",
  "api_key": "your-api-key-here", 
  "model_name": "gpt-4o"
}
```

### 完整配置示例

```json
{
  // API 连接地址 - 支持任何 OpenAI 兼容的 API 端点
  "api_url": "https://integrate.api.nvidia.com/v1",
  
  // API Key - 你的 API 密钥
  "api_key": "nvapi-your-key-here",
  
  // 模型名称 - 要使用的具体模型
  "model_name": "meta/llama-3.1-nemotron-70b-instruct",
  
  // 提供商名称 - 显示名称（可选）
  "provider_name": "NVIDIA API",
  
  // 环境变量名 - API Key 的环境变量名（可选）
  "env_var_name": "NVIDIA_API_KEY",
  
  // 模型显示名称 - 在界面中显示的名称（可选）
  "model_display_name": "Llama 3.1 Nemotron 70B",
  
  // 模型功能配置（可选）
  "model_features": {
    "temperature": true,    // 是否支持温度参数
    "tool_call": true,      // 是否支持工具调用
    "attachment": false,    // 是否支持附件
    "reasoning": true       // 是否支持推理
  },
  
  // 模型限制（可选）
  "model_limits": {
    "context": 131072,      // 上下文长度限制
    "output": 4096          // 输出长度限制
  },
  
  // 成本配置（可选，用于成本估算）
  "model_cost": {
    "input": 0.003,         // 输入 token 成本（每千 token）
    "output": 0.006         // 输出 token 成本（每千 token）
  }
}
```

## 字段说明

### 必需字段

| 字段 | 类型 | 说明 | 示例 |
|------|------|------|------|
| `api_url` | string | API 连接地址 | `"https://api.openai.com/v1"` |
| `api_key` | string | API 密钥 | `"sk-your-key-here"` |
| `model_name` | string | 模型名称 | `"gpt-4o"` |

### 可选字段

| 字段 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `provider_name` | string | `"Custom OpenAI Compatible"` | 提供商显示名称 |
| `env_var_name` | string | `"CUSTOM_OPENAI_API_KEY"` | 环境变量名 |
| `model_display_name` | string | 使用 `model_name` | 模型显示名称 |
| `model_features` | object | 见下表 | 模型功能配置 |
| `model_limits` | object | 见下表 | 模型限制配置 |
| `model_cost` | object | 见下表 | 成本配置 |

### model_features 字段

| 字段 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `temperature` | boolean | `true` | 是否支持温度参数 |
| `tool_call` | boolean | `true` | 是否支持工具调用 |
| `attachment` | boolean | `false` | 是否支持附件 |
| `reasoning` | boolean | `false` | 是否支持推理 |

### model_limits 字段

| 字段 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `context` | number | `128000` | 上下文长度限制 |
| `output` | number | `4096` | 输出长度限制 |

### model_cost 字段

| 字段 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `input` | number | `0` | 输入 token 成本（每千 token） |
| `output` | number | `0` | 输出 token 成本（每千 token） |

## 支持的 API 提供商

由于使用 OpenAI 兼容协议，支持以下提供商：

- **OpenAI**: `https://api.openai.com/v1`
- **NVIDIA API**: `https://integrate.api.nvidia.com/v1`
- **Anthropic Claude**: 通过兼容代理
- **Google Gemini**: 通过兼容代理
- **本地 Ollama**: `http://localhost:11434/v1`
- **其他兼容服务**: 任何支持 OpenAI API 格式的服务

## 常见配置示例

### OpenAI GPT-4

```json
{
  "api_url": "https://api.openai.com/v1",
  "api_key": "sk-your-openai-key",
  "model_name": "gpt-4o",
  "provider_name": "OpenAI",
  "env_var_name": "OPENAI_API_KEY"
}
```

### NVIDIA API

```json
{
  "api_url": "https://integrate.api.nvidia.com/v1",
  "api_key": "nvapi-your-key",
  "model_name": "meta/llama-3.1-nemotron-70b-instruct",
  "provider_name": "NVIDIA",
  "env_var_name": "NVIDIA_API_KEY"
}
```

### 本地 Ollama

```json
{
  "api_url": "http://localhost:11434/v1",
  "api_key": "ollama",
  "model_name": "llama3.2",
  "provider_name": "Ollama Local",
  "env_var_name": "OLLAMA_API_KEY"
}
```

## 注意事项

1. **JSON 注释**: 配置文件支持 `//` 注释，会在解析时自动移除
2. **环境变量**: API Key 会自动设置为指定的环境变量
3. **文件位置**: 配置文件必须放在脚本同目录下，命名为 `model-config.json`
4. **备份**: 建议保留 `model-config.template.json` 作为模板参考

## 故障排除

### 配置文件不存在
- 确保 `model-config.json` 文件存在于脚本目录
- 可以复制 `model-config.template.json` 作为起点

### JSON 格式错误
- 检查 JSON 语法是否正确
- 确保所有字符串都用双引号包围
- 检查是否有多余的逗号

### 必需字段缺失
- 确保 `api_url`、`api_key`、`model_name` 三个字段都已配置
- 字段值不能为空字符串