#!/usr/bin/env python3
"""
测试 NVIDIA API 连接和可用模型
"""

import requests
import os
import json

def test_nvidia_api():
    api_key = "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"
    base_url = "https://integrate.api.nvidia.com/v1"
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    print("测试 NVIDIA API 连接...")
    print(f"API Key: {api_key[:20]}...")
    print(f"Base URL: {base_url}")
    print()
    
    # 测试获取可用模型
    try:
        print("获取可用模型列表...")
        response = requests.get(f"{base_url}/models", headers=headers, timeout=10)
        
        if response.status_code == 200:
            models = response.json()
            print("✅ API 连接成功！")
            print(f"找到 {len(models.get('data', []))} 个可用模型:")
            print()
            
            for model in models.get('data', []):
                model_id = model.get('id', 'unknown')
                print(f"  - {model_id}")
                
                # 检查是否包含 kimi 或 moonshot
                if 'kimi' in model_id.lower() or 'moonshot' in model_id.lower():
                    print(f"    ⭐ 这可能是你要找的模型！")
            
            return models.get('data', [])
        else:
            print(f"❌ API 请求失败: {response.status_code}")
            print(f"响应: {response.text}")
            return []
            
    except requests.exceptions.RequestException as e:
        print(f"❌ 网络请求失败: {e}")
        return []

def test_model_chat(model_id):
    """测试特定模型的对话功能"""
    api_key = "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"
    base_url = "https://integrate.api.nvidia.com/v1"
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    data = {
        "model": model_id,
        "messages": [
            {"role": "user", "content": "Hello, can you introduce yourself?"}
        ],
        "max_tokens": 100
    }
    
    try:
        print(f"\n测试模型: {model_id}")
        response = requests.post(f"{base_url}/chat/completions", 
                               headers=headers, 
                               json=data, 
                               timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            content = result['choices'][0]['message']['content']
            print(f"✅ 模型响应成功:")
            print(f"   {content[:100]}...")
            return True
        else:
            print(f"❌ 模型测试失败: {response.status_code}")
            print(f"   {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ 请求失败: {e}")
        return False

if __name__ == "__main__":
    # 测试 API 连接
    models = test_nvidia_api()
    
    if models:
        print("\n" + "="*50)
        print("推荐的模型配置:")
        
        # 查找合适的模型
        recommended_models = []
        for model in models:
            model_id = model.get('id', '')
            # 查找常用的对话模型
            if any(keyword in model_id.lower() for keyword in ['llama', 'mistral', 'gemma', 'qwen']):
                recommended_models.append(model_id)
        
        if recommended_models:
            print("以下是一些推荐的模型:")
            for i, model_id in enumerate(recommended_models[:5], 1):
                print(f"  {i}. {model_id}")
            
            # 测试第一个推荐模型
            if recommended_models:
                test_model = recommended_models[0]
                test_model_chat(test_model)
                
                print(f"\n建议的配置文件内容:")
                print(f'{{')
                print(f'  "api_url": "https://integrate.api.nvidia.com/v1",')
                print(f'  "api_key": "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",')
                print(f'  "model_name": "{test_model}",')
                print(f'  "provider_name": "NVIDIA API",')
                print(f'  "model_display_name": "{test_model.split("/")[-1].title()}"')
                print(f'}}')
        else:
            print("未找到推荐的对话模型")
    else:
        print("无法获取模型列表，请检查 API Key 和网络连接")