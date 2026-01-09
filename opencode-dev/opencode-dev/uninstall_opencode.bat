@echo off
REM ================================================
REM OpenCode 完全卸载脚本 (Windows)
REM ================================================
REM
REM 卸载内容�?REM 1. opencode-ai �?(通过 bun)
REM 2. %USERPROFILE%\.config\opencode 配置目录
REM 3. %USERPROFILE%\.opencode 认证数据
REM 4. .opencode 项目配置（当前目录）
REM 5. %USERPROFILE%\.claude\todos �?transcripts（如果使�?Claude Code 兼容层）
REM ================================================

setlocal enabledelayedexpansion

echo ================================================
echo OpenCode Complete Uninstall Script
echo ================================================
echo.

REM 列出将要删除的内�?echo Will delete:
echo 1. opencode-ai package (via bun remove -g)
echo 2. %%USERPROFILE%%\.config\opencode config directory
echo 3. %%USERPROFILE%%\.opencode auth data
echo 4. %%USERPROFILE%%\.claude\todos and transcripts
echo 5. .opencode project config (current directory)
echo.

REM 确认
set /p confirm="Confirm uninstall? Enter yes to continue: "
if /i not "%confirm%"=="yes" (
    echo Uninstall cancelled.
    pause
    exit /b 1
)

echo.
echo ================================================
echo Starting uninstall...
echo ================================================
echo.

REM 1. 卸载 opencode-ai
echo 1. Uninstalling opencode-ai...
where bun >nul 2>&1
if %errorlevel% equ 0 (
    bun remove -g opencode-ai
    if %errorlevel% equ 0 (
        echo [OK] opencode-ai uninstalled successfully
    ) else (
        echo [SKIP] opencode-ai may not be installed or uninstall failed
    )
) else (
    echo [SKIP] bun not found, skipping package uninstall
)
echo.

REM 2. 删除配置文件
echo 2. Deleting config files and auth data...

REM Delete %%USERPROFILE%%\.config\opencode
if exist "%USERPROFILE%\.config\opencode" (
    rmdir /s /q "%USERPROFILE%\.config\opencode"
    if %errorlevel% equ 0 (
        echo [OK] Deleted: OpenCode config directory
    ) else (
        echo [FAIL] Delete failed: OpenCode config directory
    )
) else (
    echo [SKIP] Path does not exist: OpenCode config directory
)

REM Delete %%USERPROFILE%%\.opencode
if exist "%USERPROFILE%\.opencode" (
    rmdir /s /q "%USERPROFILE%\.opencode"
    if %errorlevel% equ 0 (
        echo [OK] Deleted: OpenCode auth data
    ) else (
        echo [FAIL] Delete failed: OpenCode auth data
    )
) else (
    echo [SKIP] Path does not exist: OpenCode auth data
)

REM Delete %%USERPROFILE%%\.claude\todos
if exist "%USERPROFILE%\.claude\todos" (
    rmdir /s /q "%USERPROFILE%\.claude\todos"
    if %errorlevel% equ 0 (
        echo [OK] Deleted: Claude Code todos
    ) else (
        echo [FAIL] Delete failed: Claude Code todos
    )
) else (
    echo [SKIP] Path does not exist: Claude Code todos
)

REM Delete %%USERPROFILE%%\.claude\transcripts
if exist "%USERPROFILE%\.claude\transcripts" (
    rmdir /s /q "%USERPROFILE%\.claude\transcripts"
    if %errorlevel% equ 0 (
        echo [OK] Deleted: Claude Code transcripts
    ) else (
        echo [FAIL] Delete failed: Claude Code transcripts
    )
) else (
    echo [SKIP] Path does not exist: Claude Code transcripts
)

REM Delete current directory .opencode
if exist ".opencode" (
    rmdir /s /q ".opencode"
    if %errorlevel% equ 0 (
        echo [OK] Deleted: Project-level config
    ) else (
        echo [FAIL] Delete failed: Project-level config
    )
) else (
    echo [SKIP] Path does not exist: Project-level config
)

echo.

REM 3. 验证卸载
echo ================================================
echo Verifying uninstall...
echo ================================================
echo.

where opencode >nul 2>&1
if %errorlevel% equ 0 (
    echo [WARNING] opencode still exists in system
    echo.
    for /f "delims=" %%i in ('where opencode') do (
        echo   Path: %%i
    )
    echo.
    echo   You may need to manually delete this file
) else (
    echo [OK] opencode completely removed
)

echo.
echo ================================================
echo Uninstall complete!
echo ================================================

pause
