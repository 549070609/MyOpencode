# OpenCode 快速开始指南

## 🚀 5分钟快速安装

### 1. 进入安装目录
```bash
cd "D:\localproject\prototypeDesign\openCode\opencode-dev"
```

### 2. 配置模型（必需）
```bash
# 复制配置模板
copy install\config\model-config.template.json install\config\model-config.json

# 编辑配置文件
notepad install\config\model-config.json
```

**最简配置示例**：
```json
{
  "api_url": "https://api.openai.com/v1",
  "api_key": "sk-your-openai-key-here",
  "model_name": "gpt-4o"
}
```

### 3. 运行安装
```bash
py install.py install
```

### 4. 启动使用
```bash
opencode
```

## 📝 配置文件位置

**配置文件路径**：
```
D:\localproject\prototypeDesign\openCode\opencode-dev\install\config\model-config.json
```

## 🔧 常用配置模板

### OpenAI GPT-4
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

### 本地 Ollama
```json
{
  "api_url": "http://localhost:11434/v1",
  "api_key": "ollama",
  "model_name": "llama3.2"
}
```

## ⚡ 常用命令

```bash
# 安装
py install.py install

# 配置模型
py install.py config

# 卸载
py install.py uninstall

# 启动 OpenCode
opencode
```

## 🆘 遇到问题？

1. **配置文件不存在**：运行 `copy install\config\model-config.template.json install\config\model-config.json`
2. **JSON 格式错误**：检查引号和逗号是否正确
3. **Bun 未安装**：访问 https://bun.sh 安装
4. **权限问题**：以管理员身份运行

详细说明请查看 `INSTALL-README.md`