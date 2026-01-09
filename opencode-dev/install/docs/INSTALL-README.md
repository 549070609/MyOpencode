# OpenCode 安装说明

## 概述

这是一个 OpenCode AI 编程助手的一键安装工具，支持自动安装 OpenCode 和 oh-my-opencode 插件，并提供自定义模型配置功能。

## 系统要求

- **操作系统**: Windows 10/11
- **Python**: 3.7+
- **Bun**: 最新版本 (https://bun.sh)
- **网络**: 需要访问 GitHub 和 NPM

## 快速安装

### 1. 下载安装包

确保你已经下载了完整的安装包到：
```
D:\localproject\prototypeDesign\openCode\
```

### 2. 运行安装程序

打开 PowerShell 或命令提示符，进入安装目录：

```bash
cd "D:\localproject\prototypeDesign\openCode\opencode-dev"
py create_doc.py
```

### 3. 选择安装选项

程序会显示菜单：
```
==================================================
OpenCode 安装/卸载工具
==================================================

请选择操作:
  1. 安装 OpenCode (包含 opencode + oh-my-opencode)
  2. 彻底删除 OpenCode
  0. 退出

请输入选项 (0-2):
```

选择 `1` 开始安装。

### 4. 配置自定义模型（可选）

安装完成后，程序会询问：
```
是否配置自定义大模型? (Y/n):
```

- 输入 `Y` 或直接回车：配置自定义模型
- 输入 `n`：跳过配置，稍后可手动配置

## 自定义模型配置

### 方法一：安装时配置

在安装过程中选择配置自定义模型，程序会读取配置文件：
```
D:\localproject\prototypeDesign\openCode\opencode-dev\model-config.json
```

### 方法二：单独配置

随时可以运行配置命令：
```bash
cd "D:\localproject\prototypeDesign\openCode\opencode-dev"
py create_doc.py config
```

## 模型配置文件设置

### 配置文件位置
```
D:\localproject\prototypeDesign\openCode\opencode-dev\model-config.json
```

### 创建配置文件

1. **复制模板文件**：
   ```bash
   copy model-config.template.json model-config.json
   ```

2. **编辑配置文件**：
   使用任何文本编辑器打开 `model-config.json`

### 配置示例

#### 最简配置（OpenAI）
```json
{
  // API 连接地址
  "api_url": "https://api.openai.com/v1",
  
  // 你的 OpenAI API Key
  "api_key": "sk-your-openai-api-key-here",
  
  // 模型名称
  "model_name": "gpt-4o"
}
```

#### NVIDIA API 配置
```json
{
  // NVIDIA API 地址
  "api_url": "https://integrate.api.nvidia.com/v1",
  
  // 你的 NVIDIA API Key
  "api_key": "nvapi-your-nvidia-key-here",
  
  // NVIDIA 模型名称
  "model_name": "meta/llama-3.1-nemotron-70b-instruct",
  
  // 提供商显示名称
  "provider_name": "NVIDIA API",
  
  // 环境变量名
  "env_var_name": "NVIDIA_API_KEY",
  
  // 模型显示名称
  "model_display_name": "Llama 3.1 Nemotron 70B"
}
```

#### 本地 Ollama 配置
```json
{
  // Ollama 本地地址
  "api_url": "http://localhost:11434/v1",
  
  // Ollama 不需要真实 API Key
  "api_key": "ollama",
  
  // 本地模型名称
  "model_name": "llama3.2",
  
  // 提供商名称
  "provider_name": "Ollama Local",
  
  // 环境变量名
  "env_var_name": "OLLAMA_API_KEY"
}
```

#### 完整配置示例
```json
{
  // API 连接地址
  "api_url": "https://integrate.api.nvidia.com/v1",
  
  // API Key
  "api_key": "nvapi-your-key-here",
  
  // 模型名称
  "model_name": "meta/llama-3.1-nemotron-70b-instruct",
  
  // 提供商名称（可选）
  "provider_name": "NVIDIA API",
  
  // 环境变量名（可选）
  "env_var_name": "NVIDIA_API_KEY",
  
  // 模型显示名称（可选）
  "model_display_name": "Llama 3.1 Nemotron 70B",
  
  // 模型功能配置（可选）
  "model_features": {
    "temperature": true,    // 支持温度参数
    "tool_call": true,      // 支持工具调用
    "attachment": false,    // 支持附件
    "reasoning": true       // 支持推理
  },
  
  // 模型限制（可选）
  "model_limits": {
    "context": 131072,      // 上下文长度
    "output": 4096          // 输出长度
  },
  
  // 成本配置（可选）
  "model_cost": {
    "input": 0.003,         // 输入成本（每千token）
    "output": 0.006         // 输出成本（每千token）
  }
}
```

### 配置字段说明

#### 必需字段
| 字段 | 说明 | 示例 |
|------|------|------|
| `api_url` | API 连接地址 | `"https://api.openai.com/v1"` |
| `api_key` | API 密钥 | `"sk-your-key-here"` |
| `model_name` | 模型名称 | `"gpt-4o"` |

#### 可选字段
| 字段 | 默认值 | 说明 |
|------|--------|------|
| `provider_name` | `"Custom OpenAI Compatible"` | 提供商显示名称 |
| `env_var_name` | `"CUSTOM_OPENAI_API_KEY"` | 环境变量名 |
| `model_display_name` | 使用 `model_name` | 模型显示名称 |

## 常用 API 提供商配置

### OpenAI
```json
{
  "api_url": "https://api.openai.com/v1",
  "api_key": "sk-your-openai-key",
  "model_name": "gpt-4o"
}
```

### NVIDIA API
```json
{
  "api_url": "https://integrate.api.nvidia.com/v1",
  "api_key": "nvapi-your-key",
  "model_name": "meta/llama-3.1-nemotron-70b-instruct"
}
```

### Anthropic Claude (通过代理)
```json
{
  "api_url": "https://your-claude-proxy.com/v1",
  "api_key": "your-claude-key",
  "model_name": "claude-3-5-sonnet-20241022"
}
```

### Google Gemini (通过代理)
```json
{
  "api_url": "https://your-gemini-proxy.com/v1",
  "api_key": "your-gemini-key",
  "model_name": "gemini-2.0-flash-exp"
}
```

### 本地 Ollama
```json
{
  "api_url": "http://localhost:11434/v1",
  "api_key": "ollama",
  "model_name": "llama3.2"
}
```

## 完整安装流程

### 1. 准备工作
```bash
# 进入安装目录
cd "D:\localproject\prototypeDesign\openCode\opencode-dev"

# 检查 Python 版本
python --version

# 检查 Bun 版本
bun --version
```

### 2. 配置模型（推荐先配置）
```bash
# 复制配置模板
copy model-config.template.json model-config.json

# 编辑配置文件（使用你喜欢的编辑器）
notepad model-config.json
```

### 3. 运行安装
```bash
# 启动安装程序
py create_doc.py

# 或直接安装
py create_doc.py install
```

### 4. 验证安装
```bash
# 检查 OpenCode 是否安装成功
opencode --version

# 启动 OpenCode
opencode
```

## 命令行选项

```bash
# 显示菜单
py create_doc.py

# 直接安装
py create_doc.py install

# 直接卸载
py create_doc.py uninstall

# 配置模型
py create_doc.py config

# 显示帮助
py create_doc.py --help
```

## 故障排除

### 1. 配置文件不存在
**错误信息**：
```
❌ 未找到配置文件: D:\localproject\prototypeDesign\openCode\opencode-dev\model-config.json
```

**解决方法**：
```bash
copy model-config.template.json model-config.json
# 然后编辑 model-config.json
```

### 2. JSON 格式错误
**错误信息**：
```
❌ JSON 格式错误: Invalid control character at: line X column Y
```

**解决方法**：
- 检查 JSON 语法是否正确
- 确保所有字符串都用双引号包围
- 检查是否有多余的逗号
- 可以使用在线 JSON 验证工具检查格式

### 3. 必需字段缺失
**错误信息**：
```
❌ 缺少必需字段: api_url, api_key, model_name
```

**解决方法**：
确保配置文件包含所有必需字段：
```json
{
  "api_url": "your-api-url",
  "api_key": "your-api-key", 
  "model_name": "your-model-name"
}
```

### 4. Bun 未安装
**错误信息**：
```
错误: 未找到 bun，请先安装 bun (https://bun.sh)
```

**解决方法**：
访问 https://bun.sh 安装 Bun

### 5. 权限问题
**错误信息**：
```
权限不足: Access denied
```

**解决方法**：
以管理员身份运行 PowerShell 或命令提示符

## 使用 OpenCode

安装完成后：

1. **启动 OpenCode**：
   ```bash
   opencode
   ```

2. **使用 oh-my-opencode 功能**：
   在对话中包含 "ultrawork" 或 "ulw" 关键字即可启用所有高级功能

3. **配置文件位置**：
   ```
   C:\Users\你的用户名\.config\opencode\opencode.json
   ```

## 卸载 OpenCode

如需完全卸载 OpenCode：

```bash
cd "D:\localproject\prototypeDesign\openCode\opencode-dev"
py create_doc.py uninstall
```

这将删除：
- OpenCode 可执行文件
- 配置文件和缓存
- 通过包管理器安装的组件
- oh-my-opencode 插件

## 技术支持

如果遇到问题：

1. 检查系统要求是否满足
2. 确保网络连接正常
3. 查看错误信息并参考故障排除部分
4. 检查配置文件格式是否正确

## 更新日志

- **v1.0**: 初始版本，支持基本安装和卸载
- **v1.1**: 添加 oh-my-opencode 插件支持
- **v1.2**: 添加自定义模型配置功能
- **v1.3**: 改进为 JSON 配置文件方式，增强易用性