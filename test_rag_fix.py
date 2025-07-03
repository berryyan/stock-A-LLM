#!/usr/bin/env python3
"""
快速测试RAG查询是否正常工作
"""
import requests
import json

def test_rag_query():
    """测试RAG查询通过API"""
    api_url = "http://localhost:8000/query"
    
    test_query = "贵州茅台最新年报"
    
    print(f"测试查询: {test_query}")
    
    try:
        response = requests.post(api_url, json={
            "question": test_query,
            "query_type": "hybrid",
            "top_k": 5
        }, timeout=120)
        
        if response.status_code == 200:
            result = response.json()
            print("\nAPI响应成功:")
            print(json.dumps(result, ensure_ascii=False, indent=2))
            
            # 检查sources结构
            if 'sources' in result and result['sources']:
                print("\n检查sources结构:")
                if 'rag' in result['sources']:
                    rag_sources = result['sources']['rag']
                    print(f"sources.rag包含的字段: {list(rag_sources.keys())}")
                    
                    if 'sources' in rag_sources:
                        print(f"sources.rag.sources类型: {type(rag_sources['sources'])}")
                        print(f"sources.rag.sources数量: {len(rag_sources['sources']) if isinstance(rag_sources['sources'], list) else 'N/A'}")
                    
                    if 'documents' in rag_sources:
                        print("⚠️ 发现documents字段（不应该存在）")
                    else:
                        print("✓ 没有documents字段（正确）")
                        
        else:
            print(f"API请求失败: {response.status_code}")
            print(response.text)
            
    except Exception as e:
        print(f"错误: {e}")

if __name__ == "__main__":
    print("=" * 60)
    print("RAG查询修复测试")
    print("=" * 60)
    print("\n请确保API服务器正在运行: python -m uvicorn api.main:app --reload")
    print("\n")
    
    test_rag_query()