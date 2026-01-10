# OpenCode 综合打包工具

打包 `oh-my-opencode` 和 `opencode-dev` 项目的统一 Python 脚本工具。

## 前置要求

- **Python 3.8+**
- **Bun** (JavaScript 运行时): https://bun.sh
- **Rust** (仅桌面应用构建需要): https://rustup.rs

## 使用方法

### 基本用法

```bash
# 打包所有项目
python build_packages.py --all

# 仅打包 oh-my-opencode
python build_packages.py --oh-my-opencode

# 仅打包 opencode-dev
python build_packages.py --opencode

# Windows 用户可以使用 py 命令
py build_packages.py --all
```

### 常用选项

| 选项 | 说明 |
|------|------|
| `--all` | 打包所有项目 (默认) |
| `--oh-my-opencode` | 仅打包 oh-my-opencode |
| `--opencode` | 仅打包 opencode-dev |
| `--desktop` | 构建桌面应用 (需要 Rust) |
| `--clean` | 清理构建产物后再构建 |
| `--output DIR` | 自定义输出目录 (默认: ./dist) |
| `--release` | 发布模式 (默认) |
| `--debug` | 调试模式 |
| `--skip-install` | 跳过依赖安装 |
| `--parallel` | 并行构建 (实验性) |
| `--version VERSION` | 设置版本号 |

### 桌面应用打包

```bash
# Windows NSIS 安装程序
python build_packages.py --opencode --desktop --bundle-type nsis

# Windows MSI 安装程序
python build_packages.py --opencode --desktop --bundle-type msi

# macOS DMG
python build_packages.py --opencode --desktop --bundle-type dmg

# Linux DEB
python build_packages.py --opencode --desktop --bundle-type deb

# Linux AppImage
python build_packages.py --opencode --desktop --bundle-type appimage
```

### 高级用法

```bash
# 清理后重新构建，并行执行
python build_packages.py --all --clean --parallel

# 设置版本号并打包
python build_packages.py --all --version 2.0.0

# 指定输出目录
python build_packages.py --all --output ./my-release

# 调试模式构建桌面应用
python build_packages.py --desktop --debug
```

## 输出结构

构建完成后，`dist` 目录结构如下：

```
dist/
├── oh-my-opencode/
│   ├── dist/              # 编译后的 JS 文件
│   └── oh-my-opencode-x.x.x.tgz  # npm 包
├── opencode-dev/
│   ├── util/dist/
│   ├── sdk/dist/
│   ├── plugin/dist/
│   ├── opencode/dist/
│   └── app/dist/
├── desktop/               # 如果构建了桌面应用
│   └── bundle/
│       ├── nsis/         # Windows 安装程序
│       ├── msi/          # Windows MSI
│       ├── dmg/          # macOS
│       └── deb/          # Linux
└── build-report.json     # 构建报告
```

## 构建报告

每次构建完成后会生成 `build-report.json`，包含：

- 构建时间戳
- 版本号
- 各项目构建状态
- 构建耗时
- 输出文件列表
- 错误信息（如果有）

## 故障排除

### bun 未安装

```
❌ 未检测到 bun，请先安装: https://bun.sh
```

安装 bun:
```bash
# Windows (PowerShell)
irm bun.sh/install.ps1 | iex

# macOS/Linux
curl -fsSL https://bun.sh/install | bash
```

### Rust 未安装 (桌面应用构建)

```bash
# 访问 https://rustup.rs 安装 Rust
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
```

### 依赖安装失败

尝试清理后重新构建:
```bash
python build_packages.py --all --clean
```

### 类型检查警告

类型检查警告不会阻止构建，只会显示警告信息继续执行。

## 与 build_desktop.py 的关系

本工具包含了 `build_desktop.py` 的所有功能，并额外支持：

- 打包 oh-my-opencode
- 统一的输出目录管理
- 并行构建
- 构建报告生成
- 版本号管理

如果只需要构建桌面应用，仍然可以使用 `build_desktop.py`。

