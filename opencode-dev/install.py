#!/usr/bin/env python3
"""
OpenCode 安装工具主入口

提供 opencode 和 oh-my-opencode 的安装和彻底删除功能。
"""

import os
import sys
import importlib.util
from typing import Callable


def setup_path() -> str:
    """设置 Python 模块搜索路径"""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    install_dir = os.path.join(script_dir, 'install')
    scripts_dir = os.path.join(install_dir, 'scripts')
    
    # 检查目录是否存在
    if not os.path.exists(scripts_dir):
        print(f"错误: scripts 目录不存在: {scripts_dir}")
        sys.exit(1)
    
    # 添加到 Python 路径
    if scripts_dir not in sys.path:
        sys.path.insert(0, scripts_dir)
    
    return scripts_dir


def load_installer(scripts_dir: str) -> Callable[[], None]:
    """动态加载安装脚本模块"""
    module_path = os.path.join(scripts_dir, 'create_doc.py')
    
    if not os.path.exists(module_path):
        print(f"错误: 安装脚本不存在: {module_path}")
        sys.exit(1)
    
    spec = importlib.util.spec_from_file_location("create_doc", module_path)
    if spec is None or spec.loader is None:
        print(f"错误: 无法加载模块规格: {module_path}")
        sys.exit(1)
    
    module = importlib.util.module_from_spec(spec)
    sys.modules["create_doc"] = module
    spec.loader.exec_module(module)
    
    if not hasattr(module, 'main'):
        print(f"错误: 模块缺少 main 函数: {module_path}")
        sys.exit(1)
    
    return module.main


def main():
    """主入口函数"""
    scripts_dir = setup_path()
    
    try:
        run_installer = load_installer(scripts_dir)
        run_installer()
    except Exception as e:
        print(f"错误: 执行安装脚本时发生异常: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
