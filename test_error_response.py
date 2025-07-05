#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试API错误响应格式
"""
import requests
import json

def test_error_cases():
    """测试各种错误情况"""
    url = "http://localhost:8001/query"
    
    error_cases = [
        "",  # 空查询
        "INVALID123的股价",  # 无效股票代码
        "不存在的公司最新股价",  # 不存在的股票
    ]
    
    for query in error_cases:
        print(f"\n测试查询: '{query}'")
        print("-" * 50)
        
        try:
            response = requests.post(url, json={"question": query})
            print(f"HTTP状态码: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print("\n完整响应:")
                print(json.dumps(data, indent=2, ensure_ascii=False))
                
                print("\n关键字段:")
                print(f"- success: {data.get('success')}")
                print(f"- error: {data.get('error')}")
                print(f"- answer: {data.get('answer')}")
                
            else:
                print(f"响应内容: {response.text}")
                
        except Exception as e:
            print(f"请求失败: {e}")

if __name__ == "__main__":
    test_error_cases()