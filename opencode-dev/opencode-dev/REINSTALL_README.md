# OpenCode 重装工具 (Python 版本)

一个交互式的 Python 脚本，用于卸载、安装和重装 OpenCode，支持自定义大模型配置。

## 功能特性

- ✅ **交互式菜单**：友好的命令行界面，支持中文
- ✅ **完整卸载**：清理所有配置文件和认证数据
- ✅ **灵活安装**：支持自定义 Claude、ChatGPT、Gemini 配置
- ✅ **状态检查**：实时查看安装和配置状态
- ✅ **安全操作**：需要确认后才执行敏感操作
- ✅ **彩色输出**：清晰的提示和状态信息

## 使用方法

### 快速开始

```bash
cd opencode-dev
python reinstall_opencode.py
```

### 主菜单选项

```
1. 卸载 OpenCode
   - 删除 opencode-ai 全局包
   - 清理配置文件和认证数据
   - 删除 Claude Code 兼容数据

2. 安装 OpenCode
   - 安装 opencode-ai 全局包
   - 配置 oh-my-opencode 插件
   - 支持自定义大模型参数

3. 完全重装（卸载 + 安装）
   - 自动执行完整卸载
   - 自动执行完整安装

4. 检查安装状态
   - 查看 OpenCode 安装状态
   - 检查配置文件状态
   - 显示 Bun 版本信息

0. 退出
```

## 大模型配置

### Claude 配置选项

1. **标准 Pro/Max 模式**：使用 Claude Pro/Max 订阅
2. **Max20 模式**：使用 Claude Max20（20倍加速模式）
3. **不使用 Claude**：跳过 Claude 集成

### ChatGPT 配置

- 有订阅：集成 ChatGPT（需要额外配置 `opencode-openai-codex-auth`）
- 无订阅：跳过 ChatGPT 集成

### Gemini 配置

- 启用：集成 Gemini 模型（需要额外配置 `opencode-antigravity-auth`）
- 禁用：跳过 Gemini 集成

## 系统要求

- **Python 3.6+**
- **Bun**：脚本会自动检查 Bun 是否安装

### 安装 Bun

```bash
# 使用 curl
curl -fsSL https://bun.sh/install | bash

# 或者访问官网下载
https://bun.sh
```

## 卸载内容

执行卸载时会删除以下内容：

1. `opencode-ai` 全局包（通过 `bun remove -g`）
2. `%USERPROFILE%\.config\opencode` 配置目录
3. `%USERPROFILE%\.opencode` 认证数据
4. `%USERPROFILE%\.claude\todos` (Claude Code 兼容)
5. `%USERPROFILE%\.claude\transcripts` (Claude Code 兼容)
6. `.opencode` 项目配置（当前目录）

## 安装后配置

### Claude 认证

```bash
opencode auth login
# 选择: Anthropic -> Claude Pro/Max
```

### ChatGPT 认证（如已配置）

参考 `OH_MY_OPENCODE_README.md` 配置 `opencode-openai-codex-auth`

### Gemini 认证（如已配置）

参考 `OH_MY_OPENCODE_README.md` 配置 `opencode-antigravity-auth`

## 使用提示

- 提示词中包含 `'ultrawork'` 或 `'ulw'` 可激活最大性能模式
- 详细文档请查看 `OH_MY_OPENCODE_README.md`
- 加入社区：https://discord.gg/opencode

## 安全提示

- ⚠️ 卸载会删除所有配置文件，包括 API keys 和会话记录
- ⚠️ 执行卸载前请确保已备份重要配置
- ✅ 所有危险操作都需要用户确认

## 故障排除

### Bun 未找到

```
[ERROR] 未找到 bun！请先安装 bun
```

**解决方案**：先安装 Bun，参考上面的安装说明。

### 安装失败

```
[ERROR] OpenCode 安装失败
```

**解决方案**：
1. 检查网络连接
2. 确认 Bun 正常工作：`bun --version`
3. 手动安装：`https://opencode.ai/docs`

### 配置文件找不到

```
[ERROR] 找不到 opencode.json 配置文件
```

**解决方案**：重新运行安装脚本。

## 命令行参数

当前版本不支持命令行参数，所有操作都通过交互式菜单完成。

## 许可证

与 OpenCode 项目相同。

## 贡献

欢迎提交 Issue 和 Pull Request！
