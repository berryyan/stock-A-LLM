# test_fixed_api.py
# 测试修复后的API

import requests
import json
import time

BASE_URL = "http://localhost:8000"

def test_queries():
    """测试各种查询"""
    
    queries = [
        ("贵州茅台股价", "SQL查询"),
        ("茅台2024年营收情况", "RAG查询"),
        ("分析贵州茅台的财务状况", "混合查询"),
    ]
    
    print("=== 测试修复后的API ===\n")
    
    for question, query_type in queries:
        print(f"测试 {query_type}: {question}")
        
        try:
            response = requests.post(
                f"{BASE_URL}/query",
                json={"question": question},
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                
                if result.get('success'):
                    print("✅ 成功!")
                    print(f"   查询类型: {result.get('query_type')}")
                    
                    # 检查answer字段
                    answer = result.get('answer')
                    if isinstance(answer, str):
                        print(f"   回答 (字符串): {answer[:100]}...")
                    else:
                        print(f"   ⚠️  回答类型错误: {type(answer)} - {answer}")
                        
                    # 显示数据源
                    sources = result.get('sources', [])
                    if sources:
                        print(f"   数据源: {len(sources)} 个")
                else:
                    print(f"❌ 查询失败: {result.get('error')}")
            else:
                print(f"❌ HTTP错误: {response.status_code}")
                
        except Exception as e:
            print(f"❌ 异常: {str(e)}")
            
        print()
        time.sleep(2)  # 避免过快请求

def test_health():
    """测试健康检查"""
    print("\n测试健康检查...")
    response = requests.get(f"{BASE_URL}/health")
    if response.status_code == 200:
        print("✅ API服务正常运行")
    else:
        print("❌ API服务异常")

if __name__ == "__main__":
    test_health()
    test_queries()
    
    print("\n测试完成!")
    print("如果仍有问题，请查看 manual_fix_guide.py")
