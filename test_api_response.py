#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试API响应格式
"""
import requests
import json

def test_query_response():
    """测试查询响应格式"""
    url = "http://localhost:8001/query"
    query = "贵州茅台最新股价"
    
    print(f"测试查询: {query}")
    
    try:
        response = requests.post(url, json={"question": query})
        
        if response.status_code == 200:
            data = response.json()
            print("\n响应数据结构:")
            print(json.dumps(data, indent=2, ensure_ascii=False))
            
            # 检查关键字段
            print("\n字段检查:")
            print(f"- success: {data.get('success')}")
            print(f"- question: {data.get('question')}")
            print(f"- answer: {data.get('answer', '(空)')}")
            print(f"- query_type: {data.get('query_type')}")
            
            if data.get('answer'):
                print("\n✅ answer字段有内容，修复成功！")
            else:
                print("\n❌ answer字段为空，需要检查！")
        else:
            print(f"HTTP错误: {response.status_code}")
            
    except Exception as e:
        print(f"请求失败: {e}")

if __name__ == "__main__":
    test_query_response()