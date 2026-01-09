# Kimi K2 Thinking 模型配置指南

## ✅ 配置完成状态

你的 Kimi K2 Thinking 模型已经成功配置！

### 📋 配置信息

- **API 地址**: `https://integrate.api.nvidia.com/v1`
- **API Key**: `nvapi-qxrF7km-GrJU0H...` (已设置)
- **模型名称**: `moonshotai/kimi-k2-thinking`
- **显示名称**: `Kimi K2 Thinking`
- **环境变量**: `NVIDIA_API_KEY` (已设置)

### 🔧 模型特性

- ✅ **温度参数**: 支持创意调节
- ✅ **工具调用**: 支持函数调用
- ❌ **附件支持**: 不支持文件上传
- ✅ **推理模式**: 支持思维链推理（Kimi K2 特色）
- 📊 **上下文**: 200,000 tokens
- 📝 **输出限制**: 8,192 tokens

## 🚀 使用方法

### 1. 启动 OpenCode

```bash
opencode
```

### 2. 验证模型配置

启动后，OpenCode 应该自动使用 Kimi K2 Thinking 模型。

### 3. 测试模型功能

在 OpenCode 中输入以下测试：

```
你好，请介绍一下你自己，并展示你的推理能力
```

### 4. 使用 oh-my-opencode 功能

在对话中包含 `ultrawork` 或 `ulw` 关键字来启用高级功能：

```
请帮我 ultrawork 分析这段代码的性能问题
```

## 🔍 故障排除

### 问题 1: "Agent Sisyphus's configured model is not valid"

**解决方案**:
1. 重启命令行窗口
2. 运行: `py fix-opencode-config.py`
3. 重新启动 OpenCode

### 问题 2: 环境变量未生效

**检查命令**:
```bash
echo %NVIDIA_API_KEY%
```

**修复命令**:
```bash
py env-manager.py set NVIDIA_API_KEY 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
```

### 问题 3: 模型响应错误

**测试 API 连接**:
```bash
py test-kimi-model.py
```

## 📁 相关文件

- **配置文件**: `C:\Users\你的用户名\.config\opencode\opencode.json`
- **模型配置**: `install\config\model-config.json`
- **环境变量工具**: `env-manager.py`
- **修复工具**: `fix-opencode-config.py`

## 🎯 模型切换

如需切换到其他模型，可以：

### 方法 1: 修改配置文件

编辑 `install\config\model-config.json`，然后运行：
```bash
py install.py config
```

### 方法 2: 在 OpenCode 中切换

在对话中输入：
```
/model
```

### 方法 3: 使用推荐的其他模型

根据测试结果，以下模型也表现良好：

1. **Llama 3.1 70B**: `abacusai/dracarys-llama-3.1-70b-instruct`
2. **DeepSeek R1**: `deepseek-ai/deepseek-r1`
3. **Qwen 3**: `qwen/qwen3-next-80b-a3b-thinking`

## 💡 使用技巧

### 1. 利用长上下文能力

Kimi K2 支持 200K tokens 上下文，可以处理很长的文档：

```
请分析这个完整的项目代码结构...（粘贴大量代码）
```

### 2. 激活推理模式

使用特定提示词激活深度思考：

```
请深入思考并分析这个问题的多个角度...
```

### 3. 中英文混合使用

Kimi 对中文支持很好，可以自然地中英文混合：

```
请用中文解释这个 Python function 的作用
```

## 🔄 更新和维护

### 定期检查

```bash
# 检查环境变量
py env-manager.py list

# 测试模型连接
py test-kimi-model.py

# 查看可用模型
py test-nvidia-api.py
```

### 配置备份

建议备份配置文件：
```bash
copy "C:\Users\%USERNAME%\.config\opencode\opencode.json" opencode-config-backup.json
```

## 📞 技术支持

如果遇到问题：

1. 查看本指南的故障排除部分
2. 运行 `py fix-opencode-config.py` 自动修复
3. 检查 NVIDIA API 状态和配额
4. 重启 OpenCode 和命令行窗口

---

🎉 **恭喜！你现在可以使用强大的 Kimi K2 Thinking 模型进行 AI 编程了！**