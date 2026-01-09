#!/usr/bin/env python3
"""
测试 Kimi K2 Thinking 模型
"""

import requests
import os

def test_kimi_model():
    api_key = "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"
    base_url = "https://integrate.api.nvidia.com/v1"
    model_id = "moonshotai/kimi-k2-thinking"
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    data = {
        "model": model_id,
        "messages": [
            {"role": "user", "content": "你好，请介绍一下你自己"}
        ],
        "max_tokens": 200,
        "temperature": 0.7
    }
    
    try:
        print(f"测试模型: {model_id}")
        print(f"API Key: {api_key[:20]}...")
        print()
        
        response = requests.post(f"{base_url}/chat/completions", 
                               headers=headers, 
                               json=data, 
                               timeout=30)
        
        print(f"响应状态码: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            content = result['choices'][0]['message']['content']
            print(f"✅ 模型响应成功:")
            print(f"   {content}")
            
            # 检查是否有推理过程
            if 'reasoning' in result.get('choices', [{}])[0].get('message', {}):
                reasoning = result['choices'][0]['message']['reasoning']
                print(f"\n🧠 推理过程:")
                print(f"   {reasoning[:200]}...")
            
            return True
        else:
            print(f"❌ 模型测试失败: {response.status_code}")
            print(f"错误信息: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ 请求失败: {e}")
        return False

if __name__ == "__main__":
    success = test_kimi_model()
    
    if success:
        print("\n✅ Kimi K2 Thinking 模型工作正常！")
        print("配置应该是正确的，问题可能在于:")
        print("1. 环境变量没有正确设置")
        print("2. OpenCode 需要重启")
        print("3. 配置文件格式问题")
    else:
        print("\n❌ 模型测试失败，建议使用其他模型")