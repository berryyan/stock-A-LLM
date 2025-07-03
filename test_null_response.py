#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试API处理null响应的情况
"""

import requests
import json

def test_queries():
    """测试不同查询的响应"""
    
    url = "http://localhost:8000/query"
    
    queries = [
        ("万科A最新公告", "SQL查询公告列表"),
        ("万科A最新公告的主要内容", "可能仍被路由到ANNS"),
        ("贵州茅台最新公告", "SQL查询公告列表"),
        ("总结万科A的年报", "RAG查询"),
    ]
    
    for query, description in queries:
        print(f"\n{'='*60}")
        print(f"测试: {description}")
        print(f"查询: {query}")
        print('-'*60)
        
        payload = {
            "question": query,
            "query_type": "auto"
        }
        
        try:
            response = requests.post(url, json=payload, timeout=60)
            
            if response.status_code == 200:
                data = response.json()
                
                # 检查关键字段
                print(f"成功: {data.get('success')}")
                print(f"查询类型: {data.get('query_type')}")
                print(f"有answer: {'是' if data.get('answer') else '否'}")
                print(f"有sources: {'是' if data.get('sources') else '否'}")
                print(f"有error: {'是' if data.get('error') else '否'}")
                
                # 如果有sources，显示结构
                if data.get('sources'):
                    sources = data['sources']
                    print(f"\nsources结构:")
                    for key in sources:
                        print(f"  - {key}: {type(sources[key])}")
                        if isinstance(sources[key], dict) and 'sources' in sources[key]:
                            print(f"    - sources字段: {type(sources[key]['sources'])}")
                            if isinstance(sources[key]['sources'], list):
                                print(f"    - sources长度: {len(sources[key]['sources'])}")
                                
                # 如果所有字段都是null，这是一个问题
                if all(data.get(field) is None for field in ['answer', 'query_type', 'sources', 'error']):
                    print("\n⚠️ 警告: 所有响应字段都是null，这表明查询处理失败")
                    
            else:
                print(f"请求失败: {response.status_code}")
                
        except Exception as e:
            print(f"错误: {str(e)}")
            
            
if __name__ == "__main__":
    print("测试API对不同查询的响应...")
    test_queries()