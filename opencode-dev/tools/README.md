# OpenCode 工具集

这个目录包含了 OpenCode 项目的各种实用工具和测试脚本。

## 🔧 配置工具

### apply-config.py
快速应用 Kimi K2 Thinking 模型配置的简单脚本。

```bash
py tools/apply-config.py
```

### env-manager.py
OpenCode 环境变量管理工具，用于设置、删除和查看环境变量。

```bash
# 列出环境变量
py tools/env-manager.py list

# 设置环境变量
py tools/env-manager.py set NVIDIA_API_KEY your-api-key

# 删除环境变量
py tools/env-manager.py remove NVIDIA_API_KEY
```

### fix-opencode-config.py
修复 OpenCode 配置问题的工具，自动设置正确的配置文件和环境变量。

```bash
py tools/fix-opencode-config.py
```

### setup-env.bat
Windows 批处理脚本，快速设置 NVIDIA API Key 环境变量。

```cmd
tools\setup-env.bat
```

## 🧪 测试工具

### test-kimi-model.py
测试 Kimi K2 Thinking 模型的连接和功能。

```bash
py tools/test-kimi-model.py
```

### test-nvidia-api.py
测试 NVIDIA API 连接并获取可用模型列表。

```bash
py tools/test-nvidia-api.py
```

### validate-and-fix-config.py
验证和修复 OpenCode 配置的综合工具，基于成功的测试来确保配置正确。

```bash
py tools/validate-and-fix-config.py
```

## 📝 使用说明

1. **配置模型**: 使用 `apply-config.py` 或 `fix-opencode-config.py`
2. **管理环境变量**: 使用 `env-manager.py` 
3. **测试连接**: 使用 `test-kimi-model.py` 或 `test-nvidia-api.py`
4. **验证配置**: 使用 `validate-and-fix-config.py`

## 🔗 相关文档

- [安装指南](../docs/FINAL-SETUP-GUIDE.md)
- [Kimi 设置指南](../docs/KIMI-SETUP-GUIDE.md)
- [项目结构](../docs/PROJECT-STRUCTURE.md)