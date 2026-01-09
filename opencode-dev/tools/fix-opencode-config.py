#!/usr/bin/env python3
"""
修复 OpenCode 配置问题
"""

import os
import json
import subprocess
import platform

def fix_environment_variable():
    """修复环境变量设置"""
    api_key = "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"
    env_var_name = "NVIDIA_API_KEY"
    
    print("修复环境变量设置...")
    
    # 设置当前会话环境变量
    os.environ[env_var_name] = api_key
    print(f"✓ 已设置当前会话环境变量: {env_var_name}")
    
    # 设置永久环境变量（Windows）
    if platform.system() == 'Windows':
        try:
            subprocess.run(['setx', env_var_name, api_key], check=True, capture_output=True)
            print(f"✓ 已设置永久环境变量: {env_var_name}")
        except subprocess.CalledProcessError as e:
            print(f"⚠ 设置永久环境变量失败: {e}")
    
    return True

def fix_opencode_config():
    """修复 OpenCode 配置文件"""
    home_dir = os.path.expanduser('~')
    config_path = os.path.join(home_dir, '.config', 'opencode', 'opencode.json')
    
    print(f"修复 OpenCode 配置文件: {config_path}")
    
    # 确保配置目录存在
    config_dir = os.path.dirname(config_path)
    os.makedirs(config_dir, exist_ok=True)
    
    # 创建正确的配置
    config = {
        "plugin": ["oh-my-opencode"],
        "model": "custom-openai:moonshotai/kimi-k2-thinking",
        "provider": {
            "custom-openai": {
                "name": "NVIDIA API",
                "api": "https://integrate.api.nvidia.com/v1",
                "npm": "@ai-sdk/openai-compatible",
                "env": ["NVIDIA_API_KEY"],
                "models": {
                    "moonshotai/kimi-k2-thinking": {
                        "name": "Kimi K2 Thinking",
                        "temperature": True,
                        "tool_call": True,
                        "attachment": False,
                        "reasoning": True,
                        "limit": {
                            "context": 200000,
                            "output": 8192
                        },
                        "cost": {
                            "input": 0.002,
                            "output": 0.004
                        }
                    }
                }
            }
        },
        "$schema": "https://opencode.ai/config.json"
    }
    
    # 保存配置文件
    try:
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        print(f"✓ 已更新配置文件: {config_path}")
        return True
    except Exception as e:
        print(f"✗ 保存配置文件失败: {e}")
        return False

def verify_config():
    """验证配置是否正确"""
    print("\n验证配置...")
    
    # 检查环境变量
    api_key = os.environ.get('NVIDIA_API_KEY')
    if api_key:
        print(f"✓ 环境变量 NVIDIA_API_KEY: {api_key[:20]}...")
    else:
        print("✗ 环境变量 NVIDIA_API_KEY 未设置")
        return False
    
    # 检查配置文件
    home_dir = os.path.expanduser('~')
    config_path = os.path.join(home_dir, '.config', 'opencode', 'opencode.json')
    
    if os.path.exists(config_path):
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            model = config.get('model')
            if model == 'custom-openai:moonshotai/kimi-k2-thinking':
                print(f"✓ 配置文件模型设置正确: {model}")
            else:
                print(f"✗ 配置文件模型设置错误: {model}")
                return False
            
            provider = config.get('provider', {}).get('custom-openai')
            if provider and provider.get('api') == 'https://integrate.api.nvidia.com/v1':
                print("✓ 配置文件 API 地址正确")
            else:
                print("✗ 配置文件 API 地址错误")
                return False
            
            return True
            
        except Exception as e:
            print(f"✗ 读取配置文件失败: {e}")
            return False
    else:
        print(f"✗ 配置文件不存在: {config_path}")
        return False

def main():
    print("OpenCode 配置修复工具")
    print("=" * 50)
    
    # 修复环境变量
    fix_environment_variable()
    
    print()
    
    # 修复配置文件
    fix_opencode_config()
    
    print()
    
    # 验证配置
    if verify_config():
        print("\n✅ 配置修复完成！")
        print("\n下一步:")
        print("1. 重启命令行窗口（让环境变量生效）")
        print("2. 运行: opencode")
        print("3. 如果还有问题，尝试重启 OpenCode")
        
        print(f"\n💡 测试命令:")
        print(f"   echo %NVIDIA_API_KEY%")
        print(f"   opencode --version")
    else:
        print("\n❌ 配置修复失败，请检查错误信息")

if __name__ == "__main__":
    main()