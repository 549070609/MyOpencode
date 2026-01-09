#!/usr/bin/env python3
"""
验证和修复 OpenCode 配置
基于 test-kimi-model.py 的成功测试来确保配置正确
"""

import requests
import os
import json
import subprocess
import platform

# 你提供的配置参数
CONFIG_PARAMS = {
    "api_url": "https://integrate.api.nvidia.com/v1",
    "api_key": "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",
    "model_name": "moonshotai/kimi-k2-thinking",
    "provider_name": "NVIDIA API",
    "env_var_name": "NVIDIA_API_KEY",
    "model_display_name": "Kimi K2 Thinking"
}

def test_api_connection():
    """测试 API 连接是否正常"""
    print("🔍 步骤 1: 测试 API 连接...")
    
    headers = {
        "Authorization": f"Bearer {CONFIG_PARAMS['api_key']}",
        "Content-Type": "application/json"
    }
    
    data = {
        "model": CONFIG_PARAMS['model_name'],
        "messages": [
            {"role": "user", "content": "Hello, please respond with 'API connection successful'"}
        ],
        "max_tokens": 50,
        "temperature": 0.1
    }
    
    try:
        response = requests.post(
            f"{CONFIG_PARAMS['api_url']}/chat/completions", 
            headers=headers, 
            json=data, 
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            content = result['choices'][0]['message']['content']
            print(f"✅ API 连接成功!")
            print(f"   模型响应: {content}")
            return True
        else:
            print(f"❌ API 连接失败: {response.status_code}")
            print(f"   错误信息: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ 网络请求失败: {e}")
        return False

def setup_environment_variable():
    """设置环境变量"""
    print("\n🔧 步骤 2: 设置环境变量...")
    
    env_var_name = CONFIG_PARAMS['env_var_name']
    api_key = CONFIG_PARAMS['api_key']
    
    # 设置当前会话环境变量
    os.environ[env_var_name] = api_key
    print(f"✅ 已设置当前会话环境变量: {env_var_name}")
    
    # 设置永久环境变量（Windows）
    if platform.system() == 'Windows':
        try:
            subprocess.run(['setx', env_var_name, api_key], check=True, capture_output=True)
            print(f"✅ 已设置永久环境变量: {env_var_name}")
            return True
        except subprocess.CalledProcessError as e:
            print(f"⚠ 设置永久环境变量失败: {e}")
            return False
    else:
        print(f"💡 请手动添加到 ~/.bashrc 或 ~/.zshrc:")
        print(f"   export {env_var_name}=\"{api_key}\"")
        return True

def create_model_config_file():
    """创建模型配置文件"""
    print("\n📝 步骤 3: 创建模型配置文件...")
    
    config_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'install', 'config')
    config_file = os.path.join(config_dir, 'model-config.json')
    
    # 确保配置目录存在
    os.makedirs(config_dir, exist_ok=True)
    
    # 创建配置内容
    config_content = {
        "api_url": CONFIG_PARAMS['api_url'],
        "api_key": CONFIG_PARAMS['api_key'],
        "model_name": CONFIG_PARAMS['model_name'],
        "provider_name": CONFIG_PARAMS['provider_name'],
        "env_var_name": CONFIG_PARAMS['env_var_name'],
        "model_display_name": CONFIG_PARAMS['model_display_name'],
        "model_features": {
            "temperature": True,
            "tool_call": True,
            "attachment": False,
            "reasoning": True
        },
        "model_limits": {
            "context": 200000,
            "output": 8192
        },
        "model_cost": {
            "input": 0.002,
            "output": 0.004
        }
    }
    
    try:
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(config_content, f, indent=2, ensure_ascii=False)
        print(f"✅ 已创建配置文件: {config_file}")
        return True
    except Exception as e:
        print(f"❌ 创建配置文件失败: {e}")
        return False

def create_opencode_config():
    """创建 OpenCode 配置文件"""
    print("\n⚙️ 步骤 4: 创建 OpenCode 配置文件...")
    
    home_dir = os.path.expanduser('~')
    config_path = os.path.join(home_dir, '.config', 'opencode', 'opencode.json')
    config_dir = os.path.dirname(config_path)
    
    # 确保配置目录存在
    os.makedirs(config_dir, exist_ok=True)
    
    # 创建 OpenCode 配置
    opencode_config = {
        "plugin": ["oh-my-opencode"],
        "model": f"custom-openai:{CONFIG_PARAMS['model_name']}",
        "provider": {
            "custom-openai": {
                "name": CONFIG_PARAMS['provider_name'],
                "api": CONFIG_PARAMS['api_url'],
                "npm": "@ai-sdk/openai-compatible",
                "env": [CONFIG_PARAMS['env_var_name']],
                "models": {
                    CONFIG_PARAMS['model_name']: {
                        "name": CONFIG_PARAMS['model_display_name'],
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
    
    try:
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(opencode_config, f, indent=2, ensure_ascii=False)
        print(f"✅ 已创建 OpenCode 配置: {config_path}")
        return True
    except Exception as e:
        print(f"❌ 创建 OpenCode 配置失败: {e}")
        return False

def verify_final_config():
    """验证最终配置"""
    print("\n🔍 步骤 5: 验证最终配置...")
    
    success = True
    
    # 检查环境变量
    env_var = os.environ.get(CONFIG_PARAMS['env_var_name'])
    if env_var == CONFIG_PARAMS['api_key']:
        print(f"✅ 环境变量正确: {CONFIG_PARAMS['env_var_name']}")
    else:
        print(f"❌ 环境变量错误: {CONFIG_PARAMS['env_var_name']}")
        success = False
    
    # 检查 OpenCode 配置文件
    home_dir = os.path.expanduser('~')
    config_path = os.path.join(home_dir, '.config', 'opencode', 'opencode.json')
    
    if os.path.exists(config_path):
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            expected_model = f"custom-openai:{CONFIG_PARAMS['model_name']}"
            if config.get('model') == expected_model:
                print(f"✅ OpenCode 模型配置正确: {expected_model}")
            else:
                print(f"❌ OpenCode 模型配置错误: {config.get('model')}")
                success = False
                
            provider_config = config.get('provider', {}).get('custom-openai', {})
            if provider_config.get('api') == CONFIG_PARAMS['api_url']:
                print(f"✅ API 地址配置正确: {CONFIG_PARAMS['api_url']}")
            else:
                print(f"❌ API 地址配置错误: {provider_config.get('api')}")
                success = False
                
        except Exception as e:
            print(f"❌ 读取 OpenCode 配置失败: {e}")
            success = False
    else:
        print(f"❌ OpenCode 配置文件不存在: {config_path}")
        success = False
    
    return success

def test_with_opencode_format():
    """使用 OpenCode 格式测试模型"""
    print("\n🧪 步骤 6: 使用 OpenCode 格式测试模型...")
    
    # 模拟 OpenCode 的调用方式
    headers = {
        "Authorization": f"Bearer {os.environ.get(CONFIG_PARAMS['env_var_name'])}",
        "Content-Type": "application/json"
    }
    
    data = {
        "model": CONFIG_PARAMS['model_name'],
        "messages": [
            {"role": "user", "content": "你好，请用中文简单介绍一下你自己"}
        ],
        "max_tokens": 200,
        "temperature": 0.7
    }
    
    try:
        response = requests.post(
            f"{CONFIG_PARAMS['api_url']}/chat/completions", 
            headers=headers, 
            json=data, 
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            content = result['choices'][0]['message']['content']
            print(f"✅ OpenCode 格式测试成功!")
            print(f"   模型响应: {content[:100]}...")
            return True
        else:
            print(f"❌ OpenCode 格式测试失败: {response.status_code}")
            print(f"   错误信息: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ OpenCode 格式测试异常: {e}")
        return False

def main():
    print("🚀 OpenCode Kimi K2 Thinking 配置验证和修复工具")
    print("=" * 60)
    print(f"📋 配置参数:")
    print(f"   API 地址: {CONFIG_PARAMS['api_url']}")
    print(f"   模型名称: {CONFIG_PARAMS['model_name']}")
    print(f"   API Key: {CONFIG_PARAMS['api_key'][:20]}...")
    print("=" * 60)
    
    all_success = True
    
    # 步骤 1: 测试 API 连接
    if not test_api_connection():
        all_success = False
        print("\n❌ API 连接测试失败，请检查网络和 API Key")
        return
    
    # 步骤 2: 设置环境变量
    if not setup_environment_variable():
        all_success = False
    
    # 步骤 3: 创建模型配置文件
    if not create_model_config_file():
        all_success = False
    
    # 步骤 4: 创建 OpenCode 配置文件
    if not create_opencode_config():
        all_success = False
    
    # 步骤 5: 验证最终配置
    if not verify_final_config():
        all_success = False
    
    # 步骤 6: 使用 OpenCode 格式测试
    if not test_with_opencode_format():
        all_success = False
    
    print("\n" + "=" * 60)
    if all_success:
        print("🎉 配置验证和修复完成！")
        print("\n📋 下一步操作:")
        print("1. 重启命令行窗口（让环境变量生效）")
        print("2. 运行: opencode")
        print("3. 在 OpenCode 中测试对话")
        print("\n💡 测试命令:")
        print(f"   echo %{CONFIG_PARAMS['env_var_name']}%")
        print("   opencode --version")
        print("\n🔧 如果还有问题:")
        print("   py fix-opencode-config.py")
    else:
        print("❌ 配置过程中遇到问题，请检查上述错误信息")

if __name__ == "__main__":
    main()