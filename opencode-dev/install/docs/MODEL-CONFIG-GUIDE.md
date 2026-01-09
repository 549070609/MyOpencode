# model-config.json 配置详细指南

## 📍 配置文件位置

```
D:\localproject\prototypeDesign\openCode\opencode-dev\install\config\model-config.json
```

## 🚀 快速配置步骤

### 第一步：创建配置文件

```bash
# 进入目录
cd "D:\localproject\prototypeDesign\openCode\opencode-dev"

# 复制模板文件
copy install\config\model-config.template.json install\config\model-config.json
```

### 第二步：编辑配置文件

使用任何文本编辑器打开配置文件：

```bash
# 使用记事本
notepad install\config\model-config.json

# 或使用 VS Code
code install\config\model-config.json

# 或使用其他编辑器
```

### 第三步：修改配置内容

根据你的需求修改以下三个必需字段：

```json
{
  "api_url": "你的API地址",
  "api_key": "你的API密钥", 
  "model_name": "你的模型名称"
}
```

## 📝 配置文件格式说明

### 基本结构

```json
{
  // 这是注释，程序会自动忽略
  "字段名": "字段值",
  "另一个字段": "另一个值"
}
```

**重要提示**：
- 所有字符串必须用双引号 `"` 包围
- 字段之间用逗号 `,` 分隔
- 最后一个字段后面不要加逗号
- 支持 `//` 注释，程序会自动处理

## 🔧 必需字段详解

### 1. api_url（API 连接地址）

**作用**：指定 AI 模型的 API 服务地址

**格式**：完整的 HTTPS URL，以 `/v1` 结尾

**常用地址**：
```json
// OpenAI 官方
"api_url": "https://api.openai.com/v1"

// NVIDIA API
"api_url": "https://integrate.api.nvidia.com/v1"

// 本地 Ollama
"api_url": "http://localhost:11434/v1"

// 自定义代理服务
"api_url": "https://your-proxy-service.com/v1"
```

### 2. api_key（API 密钥）

**作用**：用于身份验证的密钥

**格式**：字符串，通常以特定前缀开头

**示例**：
```json
// OpenAI 密钥（以 sk- 开头）
"api_key": "sk-proj-abcd1234567890..."

// NVIDIA 密钥（以 nvapi- 开头）
"api_key": "nvapi-1234567890abcdef..."

// 本地 Ollama（可以是任意值）
"api_key": "ollama"

// 其他服务的密钥
"api_key": "your-actual-api-key"
```

### 3. model_name（模型名称）

**作用**：指定要使用的具体模型

**格式**：字符串，模型的准确名称

**常用模型**：
```json
// OpenAI 模型
"model_name": "gpt-4o"
"model_name": "gpt-4o-mini"
"model_name": "gpt-3.5-turbo"

// NVIDIA 模型
"model_name": "meta/llama-3.1-nemotron-70b-instruct"
"model_name": "nvidia/llama-3.1-nemotron-70b-instruct"

// Anthropic Claude
"model_name": "claude-3-5-sonnet-20241022"

// Google Gemini
"model_name": "gemini-2.0-flash-exp"

// 本地 Ollama 模型
"model_name": "llama3.2"
"model_name": "qwen2.5"
```

## 🎯 完整配置示例

### 示例 1：OpenAI GPT-4o（最简配置）

```json
{
  // OpenAI 官方 API
  "api_url": "https://api.openai.com/v1",
  
  // 你的 OpenAI API Key
  "api_key": "sk-proj-your-openai-key-here",
  
  // GPT-4o 模型
  "model_name": "gpt-4o"
}
```

### 示例 2：NVIDIA API Llama 模型

```json
{
  // NVIDIA API 地址
  "api_url": "https://integrate.api.nvidia.com/v1",
  
  // 你的 NVIDIA API Key
  "api_key": "nvapi-your-nvidia-key-here",
  
  // Llama 3.1 Nemotron 模型
  "model_name": "meta/llama-3.1-nemotron-70b-instruct",
  
  // 可选：提供商显示名称
  "provider_name": "NVIDIA API",
  
  // 可选：模型显示名称
  "model_display_name": "Llama 3.1 Nemotron 70B"
}
```

### 示例 3：本地 Ollama 模型

```json
{
  // 本地 Ollama 地址
  "api_url": "http://localhost:11434/v1",
  
  // Ollama 不需要真实密钥
  "api_key": "ollama",
  
  // 本地模型名称
  "model_name": "llama3.2",
  
  // 可选配置
  "provider_name": "Ollama Local",
  "model_display_name": "Llama 3.2 Local"
}
```

### 示例 4：完整配置（包含所有可选字段）

```json
{
  // 必需字段
  "api_url": "https://integrate.api.nvidia.com/v1",
  "api_key": "nvapi-your-key-here",
  "model_name": "meta/llama-3.1-nemotron-70b-instruct",
  
  // 可选：显示配置
  "provider_name": "NVIDIA API",
  "env_var_name": "NVIDIA_API_KEY",
  "model_display_name": "Llama 3.1 Nemotron 70B",
  
  // 可选：模型功能
  "model_features": {
    "temperature": true,    // 支持温度参数
    "tool_call": true,      // 支持工具调用
    "attachment": false,    // 支持附件上传
    "reasoning": true       // 支持推理模式
  },
  
  // 可选：模型限制
  "model_limits": {
    "context": 131072,      // 最大上下文长度
    "output": 4096          // 最大输出长度
  },
  
  // 可选：成本信息
  "model_cost": {
    "input": 0.003,         // 输入成本（美元/千token）
    "output": 0.006         // 输出成本（美元/千token）
  }
}
```

## 🔍 常见 API 服务商配置

### OpenAI 官方

```json
{
  "api_url": "https://api.openai.com/v1",
  "api_key": "sk-proj-your-openai-key",
  "model_name": "gpt-4o",
  "provider_name": "OpenAI",
  "env_var_name": "OPENAI_API_KEY"
}
```

**获取 API Key**：
1. 访问 https://platform.openai.com/api-keys
2. 登录你的 OpenAI 账户
3. 点击 "Create new secret key"
4. 复制生成的密钥（以 `sk-` 开头）

### NVIDIA API

```json
{
  "api_url": "https://integrate.api.nvidia.com/v1",
  "api_key": "nvapi-your-nvidia-key",
  "model_name": "meta/llama-3.1-nemotron-70b-instruct",
  "provider_name": "NVIDIA",
  "env_var_name": "NVIDIA_API_KEY"
}
```

**获取 API Key**：
1. 访问 https://build.nvidia.com/
2. 注册并登录 NVIDIA 账户
3. 选择模型并获取 API Key
4. 复制生成的密钥（以 `nvapi-` 开头）

**常用 NVIDIA 模型**：
- `meta/llama-3.1-nemotron-70b-instruct`
- `nvidia/llama-3.1-nemotron-70b-instruct`
- `meta/llama-3.1-8b-instruct`

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

**设置 Ollama**：
1. 安装 Ollama：https://ollama.ai/
2. 下载模型：`ollama pull llama3.2`
3. 启动服务：`ollama serve`
4. 使用上述配置

**常用 Ollama 模型**：
- `llama3.2` - Meta Llama 3.2
- `qwen2.5` - 阿里通义千问
- `gemma2` - Google Gemma 2
- `mistral` - Mistral 7B

### 其他兼容服务

```json
{
  "api_url": "https://your-service.com/v1",
  "api_key": "your-service-key",
  "model_name": "your-model-name",
  "provider_name": "Your Service",
  "env_var_name": "YOUR_SERVICE_API_KEY"
}
```

## ⚠️ 常见错误和解决方法

### 错误 1：配置文件不存在

**错误信息**：
```
❌ 未找到配置文件: D:\localproject\prototypeDesign\openCode\opencode-dev\install\config\model-config.json
```

**解决方法**：
```bash
cd "D:\localproject\prototypeDesign\openCode\opencode-dev"
copy install\config\model-config.template.json install\config\model-config.json
```

### 错误 2：JSON 格式错误

**错误信息**：
```
❌ JSON 格式错误: Invalid control character at: line 5 column 10
```

**常见原因和解决方法**：

1. **缺少引号**：
   ```json
   // 错误
   "api_url": https://api.openai.com/v1
   
   // 正确
   "api_url": "https://api.openai.com/v1"
   ```

2. **多余的逗号**：
   ```json
   // 错误
   {
     "api_url": "https://api.openai.com/v1",
     "api_key": "sk-test",
     "model_name": "gpt-4o",  // 最后一行不应该有逗号
   }
   
   // 正确
   {
     "api_url": "https://api.openai.com/v1",
     "api_key": "sk-test",
     "model_name": "gpt-4o"
   }
   ```

3. **缺少逗号**：
   ```json
   // 错误
   {
     "api_url": "https://api.openai.com/v1"
     "api_key": "sk-test"
   }
   
   // 正确
   {
     "api_url": "https://api.openai.com/v1",
     "api_key": "sk-test"
   }
   ```

### 错误 3：必需字段缺失

**错误信息**：
```
❌ 缺少必需字段: api_key
```

**解决方法**：
确保配置文件包含所有必需字段：
```json
{
  "api_url": "必须填写",
  "api_key": "必须填写",
  "model_name": "必须填写"
}
```

### 错误 4：API Key 无效

**错误信息**：
```
API 调用失败: 401 Unauthorized
```

**解决方法**：
1. 检查 API Key 是否正确
2. 确认 API Key 是否有效（未过期）
3. 验证 API Key 是否有访问指定模型的权限

## 🧪 测试配置

配置完成后，运行以下命令测试：

```bash
cd "D:\localproject\prototypeDesign\openCode\opencode-dev"
py install.py config
```

成功的输出应该类似：
```
✅ 配置完成!
   提供商: Your Provider
   API 地址: https://your-api.com/v1
   模型: Your Model (your-model-name)
   环境变量: YOUR_API_KEY
```

## 📋 配置检查清单

在保存配置文件前，请检查：

- [ ] 文件位置正确：`D:\localproject\prototypeDesign\openCode\opencode-dev\install\config\model-config.json`
- [ ] JSON 格式正确（所有引号、逗号、括号匹配）
- [ ] 包含三个必需字段：`api_url`、`api_key`、`model_name`
- [ ] API URL 格式正确（以 `/v1` 结尾）
- [ ] API Key 有效且未过期
- [ ] 模型名称准确无误
- [ ] 文件保存为 UTF-8 编码

## 🔄 更新配置

如需更改配置：

1. 编辑 `install\config\model-config.json` 文件
2. 保存文件
3. 重新运行配置命令：
   ```bash
   py install.py config
   ```

配置会立即生效，无需重新安装 OpenCode。