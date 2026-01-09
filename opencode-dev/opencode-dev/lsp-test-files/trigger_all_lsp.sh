#!/bin/bash

echo "🚀 开始批量触发 LSP 服务器下载..."

cd /d/localproject/prototypeDesign/openCode/opencode-dev/opencode-dev/lsp-test-files

# 触发各种 LSP 的命令列表
commands=(
    "请使用 lsp 工具分析 test.ts 文件中的所有符号"
    "请使用 lsp 工具分析 test.py 文件中的函数定义"
    "请使用 lsp 工具分析 test.cpp 文件中的类结构"
    "请使用 lsp 工具分析 test.go 文件中的类型定义"
    "请使用 lsp 工具分析 test.rs 文件中的函数"
    "请使用 lsp 工具分析 Test.java 文件中的类"
    "请使用 lsp 工具分析 test.kt 文件中的函数"
    "请使用 lsp 工具分析 test.php 文件中的类方法"
    "请使用 lsp 工具分析 test.rb 文件中的方法定义"
    "请使用 lsp 工具分析 test.lua 文件中的函数"
    "请使用 lsp 工具分析 test.zig 文件中的结构体"
    "请使用 lsp 工具分析 main.tf 文件中的资源定义"
    "请使用 lsp 工具分析 test.yaml 文件的结构"
    "请使用 lsp 工具分析 test.svelte 文件中的组件"
    "请使用 lsp 工具分析 test.vue 文件中的组件定义"
    "请使用 lsp 工具分析 test.astro 文件中的脚本"
    "请使用 lsp 工具分析 test.typ 文件中的函数"
    "请使用 lsp 工具分析 test.dart 文件中的类"
    "请使用 lsp 工具分析 schema.prisma 文件中的模型"
)

# 批量运行命令触发 LSP 下载
for cmd in "${commands[@]}"; do
    echo "📝 执行命令: $cmd"
    timeout 60 opencode run "$cmd" > /dev/null 2>&1
    echo "✅ 完成"
    sleep 2  # 等待 LSP 下载完成
done

echo "🎉 所有 LSP 触发完成！"

# 检查下载的 LSP
echo ""
echo "📊 检查已下载的 LSP 服务器..."
ls -la /c/Users/bj07c/.local/share/opencode/bin/ | grep -E "(clangd|zls|lua-ls|terraform|tinymist|kotlin|gopls|rust-analyzer|jdtls|intelephense|rubocop|bash-language-server|svelte|vue|yaml-ls|astro)" || echo "部分 LSP 可能还在下载中..."