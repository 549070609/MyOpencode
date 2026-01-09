@echo off
echo 设置 NVIDIA API Key 环境变量...

REM 设置当前会话的环境变量
set NVIDIA_API_KEY=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

REM 设置用户级别的永久环境变量
setx NVIDIA_API_KEY "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"

echo.
echo ✅ 环境变量设置完成！
echo.
echo 📋 配置信息:
echo   API 地址: https://integrate.api.nvidia.com/v1
echo   模型名称: moonshotai/kimi-k2-thinking
echo   显示名称: Kimi K2 Thinking
echo   环境变量: NVIDIA_API_KEY
echo.
echo 🚀 现在你可以启动 OpenCode:
echo   opencode
echo.
echo 💡 在 OpenCode 中使用模型:
echo   1. 启动 OpenCode 后，模型会自动使用配置的 Kimi K2 Thinking
echo   2. 如需切换模型，可以在对话中输入: /model
echo   3. 或者修改配置文件: C:\Users\%USERNAME%\.config\opencode\opencode.json
echo.
pause