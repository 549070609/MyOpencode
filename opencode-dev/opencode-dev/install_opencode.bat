@echo off
REM ================================================
REM OpenCode + Oh My OpenCode 安装脚本 (Windows)
REM ================================================
REM
REM 这个脚本会引导你完成以下步骤�?REM 1. 检�?安装 OpenCode
REM 2. 安装 oh-my-opencode 插件
REM 3. 配置订阅选项（Claude、ChatGPT、Gemini�?REM 4. 验证安装
REM 5. 配置认证
REM ================================================

setlocal enabledelayedexpansion

echo.
echo ================================================
echo oMoMoMoMo... 欢迎安装 Oh My OpenCode!
echo ================================================
echo.
echo 本脚本将帮助你：
echo 1. 安装 OpenCode
echo 2. 配置 Oh My OpenCode 插件
echo 3. 设置 AI 模型订阅（Claude、ChatGPT、Gemini�?echo 4. 完成认证配置
echo.
echo 按任意键继续...
pause >nul

REM 检�?bun 是否安装
echo.
echo [检查] 检�?bun 是否已安�?..
where bun >nul 2>&1
if %errorlevel% neq 0 (
    echo [错误] 未找�?bun！请先安�?bun�?    echo     curl -fsSL https://bun.sh/install ^| bash
    echo 或者访问：https://bun.sh
    pause
    exit /b 1
)
echo [OK] bun 已安�?
REM Step 0: 询问订阅情况
echo.
echo ================================================
echo Step 0: 配置你的 AI 模型订阅
echo ================================================
echo.
echo 请回答以下问题来配置安装选项�?echo.

REM Claude 订阅
set /p claude_answer="你有 Claude Pro/Max 订阅吗？(y/n): "
if /i "%claude_answer%"=="y" (
    set /p claude_max20="你是否在 max20�?0倍）模式下？(y/n): "
    if /i "!claude_max20!"=="y" (
        set CLAUDE_FLAG=--claude=max20
        echo [配置] Claude: max20 模式
    ) else (
        set CLAUDE_FLAG=--claude=yes
        echo [配置] Claude: 标准 Pro/Max 模式
    )
) else (
    set CLAUDE_FLAG=--claude=no
    echo [配置] Claude: 无订�?)

REM ChatGPT 订阅
set /p chatgpt_answer="你有 ChatGPT 订阅吗？(y/n): "
if /i "%chatgpt_answer%"=="y" (
    set CHATGPT_FLAG=--chatgpt=yes
    echo [配置] ChatGPT: 有订�?) else (
    set CHATGPT_FLAG=--chatgpt=no
    echo [配置] ChatGPT: 无订�?)

REM Gemini 订阅
set /p gemini_answer="你想集成 Gemini 模型吗？(y/n): "
if /i "%gemini_answer%"=="y" (
    set GEMINI_FLAG=--gemini=yes
    echo [配置] Gemini: 启用
) else (
    set GEMINI_FLAG=--gemini=no
    echo [配置] Gemini: 禁用
)

echo.
echo 配置摘要�?echo   Claude: %CLAUDE_FLAG%
echo   ChatGPT: %CHATGPT_FLAG%
echo   Gemini: %GEMINI_FLAG%
echo.

REM Step 1: 检�?安装 OpenCode
echo.
echo ================================================
echo Step 1: 检�?安装 OpenCode
echo ================================================
echo.

where opencode >nul 2>&1
if %errorlevel% equ 0 (
    echo [检查] OpenCode 已安�?    for /f "tokens=*" %%i in ('opencode --version 2^>nul') do (
        echo   版本: %%i
    )

    echo.
    set /p reinstall_opencode="是否重新安装 OpenCode�?y/n，通常�?n): "
    if /i not "!reinstall_opencode!"=="y" (
        echo [跳过] 使用已安装的 OpenCode
        goto install_plugin
    )
)

echo [安装] 正在安装 OpenCode...
echo   安装方式: bun install -g opencode-ai
echo.
bun install -g opencode-ai
if %errorlevel% neq 0 (
    echo.
    echo [错误] OpenCode 安装失败�?    echo 请检查网络连接或手动安装：https://opencode.ai/docs
    pause
    exit /b 1
)
echo [OK] OpenCode 安装成功

:install_plugin
REM Step 2: 安装 oh-my-opencode 插件
echo.
echo ================================================
echo Step 2: 安装 Oh My OpenCode 插件
echo ================================================
echo.
echo [安装] 运行安装�?..
echo   命令: bunx oh-my-opencode install --no-tui %CLAUDE_FLAG% %CHATGPT_FLAG% %GEMINI_FLAG%
echo.
bunx oh-my-opencode install --no-tui %CLAUDE_FLAG% %CHATGPT_FLAG% %GEMINI_FLAG%
if %errorlevel% neq 0 (
    echo.
    echo [错误] 插件安装失败�?    echo 请检查网络连接或重试
    pause
    exit /b 1
)
echo [OK] 插件安装成功

REM Step 3: 验证安装
echo.
echo ================================================
echo Step 3: 验证安装
echo ================================================
echo.

echo [验证] 检�?OpenCode 版本...
for /f "tokens=*" %%i in ('opencode --version 2^>nul') do (
    set OPENCODE_VERSION=%%i
)
echo   版本: !OPENCODE_VERSION!

echo [验证] 检查插件配�?..
set OPENCODE_CONFIG=%USERPROFILE%\.config\opencode\opencode.json
if exist "%OPENCODE_CONFIG%" (
    findstr /C:"oh-my-opencode" "%OPENCODE_CONFIG%" >nul
    if %errorlevel% equ 0 (
        echo [OK] oh-my-opencode 插件已注�?    ) else (
        echo [警告] 插件配置可能有问�?    )
) else (
    echo [错误] 找不�?opencode.json 配置文件
)

echo.
if /i not "%CHATGPT_FLAG%"=="--chatgpt=no" (
    echo [提示] 你选择�?ChatGPT 订阅
    echo        需要额外安�?opencode-openai-codex-auth 插件
    echo        请参�?OH_MY_OPENCODE_README.md 进行配置
)

if /i not "%GEMINI_FLAG%"=="--gemini=no" (
    echo [提示] 你选择�?Gemini 集成
    echo        需要额外安�?opencode-antigravity-auth 插件
    echo        请参�?OH_MY_OPENCODE_README.md 进行配置
)

REM Step 4: 配置认证
echo.
echo ================================================
echo Step 4: 配置认证
echo ================================================
echo.

if /i not "%CLAUDE_FLAG%"=="--claude=no" (
    echo.
    echo [认证] 配置 Claude (Anthropic)
    echo        运行: opencode auth login
    echo        选择: Anthropic -^> Claude Pro/Max
    echo.
    set /p claude_auth="现在配置 Claude 认证吗？(y/n): "
    if /i "!claude_auth!"=="y" (
        opencode auth login
    ) else (
        echo [跳过] 稍后运行 opencode auth login 配置
    )
)

echo.
echo ================================================
echo 安装完成�?echo ================================================
echo.
echo 下一步：
echo.
if /i not "%CLAUDE_FLAG%"=="--claude=no" (
    echo 1. 运行 opencode auth login 配置 Claude 认证
    echo.
)
if /i not "%CHATGPT_FLAG%"=="--chatgpt=no" (
    echo 2. 参�?OH_MY_OPENCODE_README.md 配置 opencode-openai-codex-auth
    echo.
)
if /i not "%GEMINI_FLAG%"=="--gemini=no" (
    echo 3. 参�?OH_MY_OPENCODE_README.md 配置 opencode-antigravity-auth
    echo.
)
echo 4. 运行 opencode 开始使用！
echo.
echo 提示�?echo   - 在提示词中包�?'ultrawork' �?'ulw' 可激活最大性能模式
echo   - 详细文档请查�?OH_MY_OPENCODE_README.md
echo   - 加入社区：https://discord.gg/opencode
echo.
echo oMoMoMoMo... 🎉
echo.
pause
