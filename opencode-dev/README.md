# OpenCode 一键安装工具

> 🚀 OpenCode AI 编程助手的完整安装解决方案

## 📁 项目结构

```
opencode-dev/
├── install.py                      # 主安装入口
├── README.md                       # 项目说明
├── install/                        # 安装相关文件
│   ├── README.md                   # 详细说明
│   ├── docs/                       # 文档目录
│   │   ├── INSTALL-README.md       # 完整安装说明
│   │   ├── QUICK-START.md          # 快速开始指南
│   │   ├── MODEL-CONFIG-GUIDE.md   # 配置详细指南
│   │   └── MODEL-CONFIG-README.md  # 配置技术说明
│   ├── config/                     # 配置文件目录
│   │   ├── model-config.template.json  # 配置模板
│   │   ├── config-examples.json    # 配置示例
│   │   └── model-config.json       # 用户配置文件
│   ├── scripts/                    # 脚本目录
│   │   └── create_doc.py           # 主安装脚本
│   └── uninstaller/                # 卸载模块
│       ├── main.py
│       ├── models.py
│       └── ...
├── tools/                          # 工具和测试脚本
│   ├── README.md                   # 工具说明
│   ├── apply-config.py             # 快速配置应用
│   ├── env-manager.py              # 环境变量管理
│   ├── fix-opencode-config.py      # 配置修复工具
│   ├── test-kimi-model.py          # Kimi 模型测试
│   ├── test-nvidia-api.py          # NVIDIA API 测试
│   ├── validate-and-fix-config.py  # 配置验证修复
│   └── setup-env.bat               # Windows 环境设置
├── docs/                           # 项目文档
│   ├── 01-Product Overview.md      # 产品概述
│   ├── FINAL-SETUP-GUIDE.md        # 最终设置指南
│   ├── KIMI-SETUP-GUIDE.md         # Kimi 设置指南
│   ├── PROJECT-STRUCTURE.md        # 项目结构说明
│   └── test.md                     # 测试文档
├── opencode-dev/                   # OpenCode 源码
└── oh-my-opencode-dev/            # oh-my-opencode 源码
```

## 🚀 快速开始

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
py install.py
```

### 3. 启动使用
```bash
opencode
```

## 📚 文档

- **[install/docs/MODEL-CONFIG-GUIDE.md](install/docs/MODEL-CONFIG-GUIDE.md)** - 🔥 重点：配置文件详细说明
- **[install/docs/QUICK-START.md](install/docs/QUICK-START.md)** - 5分钟快速安装
- **[install/docs/INSTALL-README.md](install/docs/INSTALL-README.md)** - 详细的安装和配置指南
- **[install/README.md](install/README.md)** - 完整功能说明
- **[tools/README.md](tools/README.md)** - 工具和测试脚本说明
- **[docs/](docs/)** - 项目文档集合

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

## 🎮 命令行选项

```bash
# 显示菜单
py install.py

# 直接安装
py install.py install

# 配置模型
py install.py config

# 完全卸载
py install.py uninstall

# 显示帮助
py install.py --help
```

## 🔧 实用工具

项目提供了丰富的工具和测试脚本，位于 `tools/` 目录：

```bash
# 快速应用配置
py tools/apply-config.py

# 管理环境变量
py tools/env-manager.py list
py tools/env-manager.py set NVIDIA_API_KEY your-key

# 修复配置问题
py tools/fix-opencode-config.py

# 测试模型连接
py tools/test-kimi-model.py
py tools/test-nvidia-api.py

# 验证和修复配置
py tools/validate-and-fix-config.py
```

详细说明请查看 [tools/README.md](tools/README.md)

## 🛠️ 系统要求

- **操作系统**: Windows 10/11
- **Python**: 3.7+
- **Bun**: 最新版本
- **网络**: 需要访问 GitHub 和 NPM

## 🆘 故障排除

| 问题 | 解决方案 |
|------|----------|
| 配置文件不存在 | `copy install\config\model-config.template.json install\config\model-config.json` |
| JSON 格式错误 | 检查引号、逗号、括号是否正确 |
| Bun 未安装 | 访问 https://bun.sh 安装 |
| 权限问题 | 以管理员身份运行 |

## 📝 更新日志

- **v2.1** - 优化项目目录结构，工具和文档分类整理
- **v2.0** - 重构文件结构，优化组织方式
- **v1.3** - JSON 配置文件支持，增强易用性
- **v1.2** - 添加自定义模型配置功能  
- **v1.1** - 添加 oh-my-opencode 插件支持
- **v1.0** - 初始版本，基本安装卸载功能