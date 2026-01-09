#!/usr/bin/env python3
"""
OpenCode 环境变量管理工具
"""

import os
import sys
import subprocess
import platform

def set_permanent_env_var(name, value):
    """设置永久环境变量"""
    if platform.system() == 'Windows':
        try:
            subprocess.run(['setx', name, value], check=True, capture_output=True)
            print(f'✓ 已设置永久环境变量: {name}')
            return True
        except subprocess.CalledProcessError as e:
            print(f'✗ 设置失败: {e}')
            return False
    else:
        print(f'请手动添加到 ~/.bashrc 或 ~/.zshrc:')
        print(f'export {name}="{value}"')
        return False

def remove_permanent_env_var(name):
    """删除永久环境变量"""
    if platform.system() == 'Windows':
        try:
            subprocess.run([
                'reg', 'delete', 
                'HKEY_CURRENT_USER\\Environment', 
                '/v', name, '/f'
            ], check=True, capture_output=True)
            print(f'✓ 已删除永久环境变量: {name}')
            return True
        except subprocess.CalledProcessError:
            print(f'⚠ 环境变量 {name} 不存在或删除失败')
            return False
    else:
        print(f'请手动从 shell 配置文件中删除: export {name}=...')
        return False

def list_opencode_env_vars():
    """列出 OpenCode 相关的环境变量"""
    env_vars = [
        'OPENAI_API_KEY',
        'ANTHROPIC_API_KEY', 
        'GOOGLE_GENERATIVE_AI_API_KEY',
        'NVIDIA_API_KEY',
        'CUSTOM_OPENAI_API_KEY',
        'CUSTOM_API_KEY',
        'OLLAMA_API_KEY'
    ]
    
    print('OpenCode 相关环境变量状态:')
    print('-' * 50)
    
    for var in env_vars:
        value = os.environ.get(var)
        if value:
            # 只显示前10个字符，保护隐私
            masked_value = value[:10] + '...' if len(value) > 10 else value
            print(f'✓ {var} = {masked_value}')
        else:
            print(f'✗ {var} = (未设置)')

def main():
    if len(sys.argv) < 2:
        print('OpenCode 环境变量管理工具')
        print('')
        print('用法:')
        print('  py env-manager.py list                    # 列出环境变量')
        print('  py env-manager.py set <name> <value>      # 设置环境变量')
        print('  py env-manager.py remove <name>           # 删除环境变量')
        print('')
        print('示例:')
        print('  py env-manager.py set NVIDIA_API_KEY nvapi-xxx')
        print('  py env-manager.py remove NVIDIA_API_KEY')
        return
    
    command = sys.argv[1].lower()
    
    if command == 'list':
        list_opencode_env_vars()
    elif command == 'set' and len(sys.argv) == 4:
        name, value = sys.argv[2], sys.argv[3]
        # 设置当前会话
        os.environ[name] = value
        # 设置永久
        set_permanent_env_var(name, value)
        print(f'💡 重启命令行后生效，或运行: set {name}={value[:10]}...')
    elif command == 'remove' and len(sys.argv) == 3:
        name = sys.argv[2]
        # 删除当前会话
        if name in os.environ:
            del os.environ[name]
        # 删除永久
        remove_permanent_env_var(name)
        print('💡 重启命令行后生效')
    else:
        print('无效的命令或参数')

if __name__ == '__main__':
    main()