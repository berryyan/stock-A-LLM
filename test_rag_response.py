#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试RAG查询响应格式
"""

import requests
import json
import time

def test_rag_query():
    """测试RAG查询返回的数据格式"""
    
    # API端点
    url = "http://localhost:8000/query"
    
    # 测试查询
    query = "总结万科A的年报"
    
    # 发送请求
    payload = {
        "question": query,
        "query_type": "auto"
    }
    
    print(f"测试查询: {query}")
    print("-" * 50)
    
    try:
        response = requests.post(url, json=payload)
        
        if response.status_code == 200:
            data = response.json()
            
            print("返回状态:", data.get("status"))
            print("\n完整响应结构:")
            print(json.dumps(data, ensure_ascii=False, indent=2))
            
            # 检查关键字段
            if "response" in data:
                print("\n响应内容预览:")
                print(data["response"][:200] + "...")
                
            if "sources" in data:
                print("\n源数据结构:")
                sources = data["sources"]
                
                # 检查各种可能的源数据
                if sources:
                    if "rag" in sources:
                        print("  - RAG源数据存在")
                        rag_data = sources["rag"]
                        print(f"    - 类型: {type(rag_data)}")
                        if isinstance(rag_data, dict):
                            print(f"    - 键: {list(rag_data.keys())}")
                            # 检查是否有sources字段
                            if "sources" in rag_data:
                                print(f"    - sources类型: {type(rag_data['sources'])}")
                                if isinstance(rag_data['sources'], list):
                                    print(f"    - sources长度: {len(rag_data['sources'])}")
                            # 检查是否有documents字段
                            if "documents" in rag_data:
                                print(f"    - documents类型: {type(rag_data['documents'])}")
                                if isinstance(rag_data['documents'], list):
                                    print(f"    - documents长度: {len(rag_data['documents'])}")
                    
                    if "sql" in sources:
                        print("  - SQL源数据存在")
                    
                    if "financial" in sources:
                        print("  - Financial源数据存在")
                        
                    if "money_flow" in sources:
                        print("  - MoneyFlow源数据存在")
                        
        else:
            print(f"请求失败，状态码: {response.status_code}")
            print(f"错误信息: {response.text}")
            
    except Exception as e:
        print(f"发生错误: {str(e)}")
        
    print("\n" + "=" * 50)
    
    # 测试直接RAG查询
    print("\n测试直接RAG查询:")
    payload["query_type"] = "rag"
    
    try:
        response = requests.post(url, json=payload)
        
        if response.status_code == 200:
            data = response.json()
            
            print("返回状态:", data.get("status"))
            
            if "sources" in data:
                print("\n直接RAG查询的源数据结构:")
                sources = data["sources"]
                print(json.dumps(sources, ensure_ascii=False, indent=2)[:500] + "...")
                
        else:
            print(f"请求失败，状态码: {response.status_code}")
            
    except Exception as e:
        print(f"发生错误: {str(e)}")


if __name__ == "__main__":
    print("开始测试RAG响应格式...")
    print("请确保API服务器正在运行: python -m uvicorn api.main:app --reload --host 0.0.0.0 --port 8000")
    print("=" * 50)
    
    # 等待一下确保服务器就绪
    time.sleep(1)
    
    test_rag_query()