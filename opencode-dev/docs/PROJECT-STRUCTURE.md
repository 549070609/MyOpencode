# OpenCode 项目文件结构

## 📁 整体结构

```
opencode-dev/
├── install.py                      # 🚀 主安装入口
├── README.md                       # 📖 项目主说明
├── install/                        # 📦 安装相关文件
│   ├── README.md                   # 安装工具详细说明
│   ├── config/                     # ⚙️ 配置文件目录
│   │   ├── model-config.template.json  # 配置模板
│   │   ├── config-examples.json    # 配置示例
│   │   └── model-config.json       # 用户配置文件
│   ├── docs/                       # 📚 安装文档目录
│   │   ├── INSTALL-README.md       # 完整安装说明
│   │   ├── QUICK-START.md          # 快速开始指南
│   │   ├── MODEL-CONFIG-GUIDE.md   # 配置详细指南
│   │   └── MODEL-CONFIG-README.md  # 配置技术说明
│   ├── scripts/                    # 🔧 脚本目录
│   │   └── create_doc.py           # 主安装脚本
│   └── uninstaller/                # 🗑️ 卸载模块
│       ├── main.py                 # 卸载主程序
│       ├── models.py               # 数据模型
│       ├── platform_detector.py   # 平台检测
│       ├── executable_detector.py # 可执行文件检测
│       ├── package_manager.py     # 包管理器处理
│       ├── directory_cleaner.py   # 目录清理
│       ├── project_scanner.py     # 项目扫描
│       └── tests/                  # 测试文件
├── tools/                          # 🔧 工具和测试脚本
│   ├── README.md                   # 工具说明
│   ├── apply-config.py             # 快速配置应用
│   ├── env-manager.py              # 环境变量管理
│   ├── fix-opencode-config.py      # 配置修复工具
│   ├── test-kimi-model.py          # Kimi 模型测试
│   ├── test-nvidia-api.py          # NVIDIA API 测试
│   ├── validate-and-fix-config.py  # 配置验证修复
│   └── setup-env.bat               # Windows 环境设置
├── docs/                           # 📚 项目文档
│   ├── README.md                   # 文档导航
│   ├── 01-Product Overview.md      # 产品概述
│   ├── FINAL-SETUP-GUIDE.md        # 最终设置指南
│   ├── KIMI-SETUP-GUIDE.md         # Kimi 设置指南
│   ├── PROJECT-STRUCTURE.md        # 本文件结构说明
│   └── test.md                     # 测试文档
├── opencode-dev/                   # 🎯 OpenCode 源码
└── oh-my-opencode-dev/            # 🔌 oh-my-opencode 源码
```

## 🔄 文件结构变更

### v2.1 目录优化（当前版本）

**新增目录**：
- `tools/` - 工具和测试脚本专用目录
- `docs/` - 项目文档专用目录

**文件重新组织**：
- 测试脚本 → `tools/` 目录
  - `test-kimi-model.py`
  - `test-nvidia-api.py`
  - `validate-and-fix-config.py`
- 配置工具 → `tools/` 目录
  - `apply-config.py`
  - `env-manager.py`
  - `fix-opencode-config.py`
  - `setup-env.bat`
- 项目文档 → `docs/` 目录
  - `01-Product Overview.md`
  - `FINAL-SETUP-GUIDE.md`
  - `KIMI-SETUP-GUIDE.md`
  - `PROJECT-STRUCTURE.md`
  - `test.md`

**优化效果**：
- ✅ 根目录更加简洁
- ✅ 文件分类更加清晰
- ✅ 工具和文档易于查找
- ✅ 项目结构更加专业

### v2.0 重构

**新增**：
- `install.py` - 新的主入口文件
- `install/` - 统一的安装相关文件目录
- `install/config/` - 配置文件专用目录
- `install/docs/` - 安装文档专用目录
- `install/scripts/` - 脚本专用目录
- `install/uninstaller/` - 卸载模块专用目录

**移动**：
- `create_doc.py` → `install/scripts/create_doc.py`
- `model-config.*.json` → `install/config/`
- 安装文档 → `install/docs/`
- `uninstaller/` → `install/uninstaller/`

### v1.x 旧结构（已废弃）

```
opencode-dev/
├── create_doc.py                   # 旧主脚本
├── model-config.json               # 旧配置文件
├── *.md                           # 散落的文档文件
└── uninstaller/                   # 旧卸载目录
```

## 🎯 使用方式

### 主要入口

```bash
# 新的主入口（推荐）
py install.py

# 支持的命令
py install.py install    # 安装
py install.py config     # 配置
py install.py uninstall  # 卸载
```

### 配置文件

**位置**：`install/config/model-config.json`

**创建**：
```bash
copy install\config\model-config.template.json install\config\model-config.json
```

### 文档查看

- **项目文档**：`docs/` 目录
  - **产品概述**：`docs/01-Product Overview.md`
  - **设置指南**：`docs/FINAL-SETUP-GUIDE.md`
  - **Kimi 配置**：`docs/KIMI-SETUP-GUIDE.md`
  - **项目结构**：`docs/PROJECT-STRUCTURE.md`
- **安装文档**：`install/docs/` 目录
  - **快速开始**：`install/docs/QUICK-START.md`
  - **详细配置**：`install/docs/MODEL-CONFIG-GUIDE.md`
  - **完整安装**：`install/docs/INSTALL-README.md`

### 工具使用

- **配置工具**：`tools/` 目录
  - **快速配置**：`py tools/apply-config.py`
  - **环境管理**：`py tools/env-manager.py`
  - **配置修复**：`py tools/fix-opencode-config.py`
- **测试工具**：`tools/` 目录
  - **Kimi 测试**：`py tools/test-kimi-model.py`
  - **API 测试**：`py tools/test-nvidia-api.py`
  - **配置验证**：`py tools/validate-and-fix-config.py`

## 🔧 开发者信息

### 路径处理

脚本中的路径处理函数：

```python
def get_install_dir():
    """获取 install 目录"""
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def get_config_dir():
    """获取配置文件目录"""
    install_dir = get_install_dir()
    return os.path.join(install_dir, 'config')
```

### 模块导入

```python
# 新的导入方式
script_dir = os.path.dirname(os.path.abspath(__file__))
install_dir = os.path.dirname(script_dir)
uninstaller_dir = os.path.join(install_dir, 'uninstaller')
sys.path.insert(0, uninstaller_dir)

from main import OpenCodeUninstaller
```

## 📋 文件功能说明

### 核心文件

| 文件 | 功能 | 重要性 |
|------|------|--------|
| `install.py` | 主入口，导入并执行安装脚本 | ⭐⭐⭐ |
| `install/scripts/create_doc.py` | 核心安装逻辑 | ⭐⭐⭐ |
| `install/config/model-config.json` | 用户配置文件 | ⭐⭐⭐ |

### 配置文件

| 文件 | 功能 | 用途 |
|------|------|------|
| `model-config.template.json` | 配置模板 | 用户复制使用 |
| `config-examples.json` | 配置示例 | 参考不同 API 配置 |
| `model-config.json` | 用户配置 | 实际使用的配置 |

### 文档文件

| 目录 | 用途 | 内容 |
|------|------|------|
| `install/docs/` | 安装相关文档 | 安装、配置指南 |
| `docs/` | 项目文档 | 产品概述、设置指南 |

| 文件 | 目标用户 | 内容 |
|------|----------|------|
| `install/docs/QUICK-START.md` | 新用户 | 5分钟快速安装 |
| `install/docs/MODEL-CONFIG-GUIDE.md` | 所有用户 | 详细配置说明 |
| `install/docs/INSTALL-README.md` | 高级用户 | 完整安装指南 |
| `docs/FINAL-SETUP-GUIDE.md` | 所有用户 | 最终设置指南 |
| `docs/KIMI-SETUP-GUIDE.md` | Kimi 用户 | Kimi 模型配置 |

### 工具文件

| 目录 | 用途 | 内容 |
|------|------|------|
| `tools/` | 工具和测试脚本 | 配置、测试、管理工具 |

| 文件 | 功能 | 用途 |
|------|------|------|
| `apply-config.py` | 快速配置应用 | 一键应用模型配置 |
| `env-manager.py` | 环境变量管理 | 设置、删除、查看环境变量 |
| `fix-opencode-config.py` | 配置修复 | 修复配置问题 |
| `test-kimi-model.py` | Kimi 模型测试 | 测试 Kimi 连接 |
| `test-nvidia-api.py` | NVIDIA API 测试 | 测试 NVIDIA API |
| `validate-and-fix-config.py` | 配置验证修复 | 综合配置验证 |
| `setup-env.bat` | Windows 环境设置 | 批处理环境设置 |

### 卸载模块

| 文件 | 功能 |
|------|------|
| `main.py` | 卸载主程序 |
| `models.py` | 数据模型定义 |
| `platform_detector.py` | 检测操作系统平台 |
| `executable_detector.py` | 查找可执行文件 |
| `package_manager.py` | 处理包管理器卸载 |
| `directory_cleaner.py` | 清理目录和文件 |
| `project_scanner.py` | 扫描项目中的配置 |

## 🎉 优势

### 组织性
- ✅ 文件分类清晰
- ✅ 功能模块化
- ✅ 易于维护

### 可扩展性
- ✅ 新功能易于添加
- ✅ 文档结构化
- ✅ 配置集中管理

### 用户体验
- ✅ 单一入口点
- ✅ 路径引用统一
- ✅ 文档易于查找

## 🔄 迁移指南

如果你有旧版本的配置：

1. **备份旧配置**：
   ```bash
   copy model-config.json model-config.backup.json
   ```

2. **迁移到新位置**：
   ```bash
   copy model-config.json install\config\model-config.json
   ```

3. **使用新入口**：
   ```bash
   py install.py config
   ```

4. **清理旧文件**（可选）：
   ```bash
   del model-config.json
   del create_doc.py
   ```