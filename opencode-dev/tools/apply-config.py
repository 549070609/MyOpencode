#!/usr/bin/env python3
"""
应用模型配置的简单脚本
"""

import os
import sys
import json

# 添加 install/scripts 目录到 Python 路径
script_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.dirname(script_dir)  # 回到 opencode-dev 根目录
install_dir = os.path.join(root_dir, 'install')
scripts_dir = os.path.join(install_dir, 'scripts')
sys.path.insert(0, scripts_dir)

# 导入配置函数
try:
    from create_doc import configure_custom_models
    
    print("正在应用 Kimi K2 Thinking 模型配置...")
    success = configure_custom_models()
    
    if success:
        print("\n✅ 配置应用成功！")
        print("现在你可以运行 `opencode` 启动 AI 编程助手")
    else:
        print("\n❌ 配置应用失败")
        
except ImportError as e:
    print(f"错误: 无法导入配置函数: {e}")
    sys.exit(1)
except Exception as e:
    print(f"配置过程中发生错误: {e}")
    sys.exit(1)