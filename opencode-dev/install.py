#!/usr/bin/env python3
"""
OpenCode 安装工具主入口

提供 opencode 和 oh-my-opencode 的安装和彻底删除功能。
"""

import os
import sys

# 添加 install/scripts 目录到 Python 路径
script_dir = os.path.dirname(os.path.abspath(__file__))
install_dir = os.path.join(script_dir, 'install')
scripts_dir = os.path.join(install_dir, 'scripts')
sys.path.insert(0, scripts_dir)

# 导入主安装脚本
try:
    from create_doc import main
    
    if __name__ == '__main__':
        main()
except ImportError as e:
    print(f"错误: 无法导入安装脚本: {e}")
    print(f"请确保文件结构完整，scripts 目录位于: {scripts_dir}")
    sys.exit(1)