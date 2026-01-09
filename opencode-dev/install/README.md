# OpenCode 一键安装工具

> 🚀 OpenCode AI 编程助手的完整安装解决方案

## 📋 功能特性

- ✅ **一键安装**: 自动安装 OpenCode 和 oh-my-opencode 插件
- ✅ **自定义模型**: 支持 JSON 配置文件方式配置任意 OpenAI 兼容模型
- ✅ **完整卸载**: 彻底清理所有相关文件和配置
- ✅ **错误处理**: 完善的错误提示和故障排除
- ✅ **跨平台**: 支持 Windows 系统（主要测试平台）

## 🎯 快速开始

### 📍 重要：配置文件位置
```
D:\localproject\prototypeDesign\openCode\opencode-dev\install\config\model-config.json
```

### 1. 配置模型（必需步骤）
```bash
cd "D:\localproject\prototypeDesign\openCode\opencode-dev"

# 复制配置模板
copy install\config\model-config.template.json install\config\model-config.json

# 编辑配置文件（重要！）
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

### 2. 安装 OpenCode
```bash
py install.py install
```

### 3. 启动使用
```bash
opencode
```

## 📚 文档

- **[model-config.json 配置详细指南](MODEL-CONFIG-GUIDE.md)** - 🔥 重点：配置文件详细说明
- **[快速开始指南](QUICK-START.md)** - 5分钟快速安装
- **[完整安装说明](INSTALL-README.md)** - 详细的安装和配置指南
- **[模型配置说明](MODEL-CONFIG-README.md)** - JSON 配置文件技术说明

## 🔧 配置示例

**OpenAI GPT-4**:
```json
{
  "api_url": "https://api.openai.com/v1",
  "api_key": "sk-your-key",
  "model_name": "gpt-4o"
}
```

**NVIDIA API**:
```json
{
  "api_url": "https://integrate.api.nvidia.com/v1",
  "api_key": "nvapi-your-key",
  "model_name": "meta/llama-3.1-nemotron-70b-instruct"
}
```

## 📁 文件结构

```
opencode-dev/
├── create_doc.py                    # 主安装脚本
├── model-config.template.json       # 配置模板
├── model-config.json               # 用户配置文件
├── README.md                       # 项目说明
├── QUICK-START.md                  # 快速开始
├── INSTALL-README.md               # 完整安装说明
├── MODEL-CONFIG-README.md          # 配置文件说明
└── uninstaller/                    # 卸载模块
    ├── main.py
    ├── models.py
    └── ...
```

## 🎮 命令行选项

```bash
# 显示菜单
py create_doc.py

# 直接安装
py create_doc.py install

# 配置模型
py create_doc.py config

# 完全卸载
py create_doc.py uninstall

# 显示帮助
py create_doc.py --help
```

## 🔍 支持的模型

由于使用 OpenAI 兼容协议，支持以下提供商：

- **OpenAI** - GPT-4, GPT-4o, GPT-3.5 等
- **NVIDIA API** - Llama, Nemotron 等模型
- **Anthropic Claude** - 通过兼容代理
- **Google Gemini** - 通过兼容代理  
- **本地 Ollama** - 所有本地模型
- **其他兼容服务** - 任何支持 OpenAI API 格式的服务

## 🛠️ 系统要求

- **操作系统**: Windows 10/11
- **Python**: 3.7+
- **Bun**: 最新版本
- **网络**: 需要访问 GitHub 和 NPM

## 🆘 故障排除

| 问题 | 解决方案 |
|------|----------|
| 配置文件不存在 | `copy model-config.template.json model-config.json` |
| JSON 格式错误 | 检查引号、逗号、括号是否正确 |
| Bun 未安装 | 访问 https://bun.sh 安装 |
| 权限问题 | 以管理员身份运行 |

## 📝 更新日志

- **v1.3** - JSON 配置文件支持，增强易用性
- **v1.2** - 添加自定义模型配置功能  
- **v1.1** - 添加 oh-my-opencode 插件支持
- **v1.0** - 初始版本，基本安装卸载功能

## 🤝 贡献

欢迎提交 Issue 和 Pull Request 来改进这个工具。

## 📄 许可证

本项目采用 MIT 许可证。