# optimized_test.py
# 优化后的API测试

import requests
import json
import time

BASE_URL = "http://localhost:8000"

def test_with_timeout(query, timeout=60):
    """带超时控制的测试"""
    
    print(f"\n查询: {query}")
    print(f"超时设置: {timeout}秒")
    
    try:
        start = time.time()
        response = requests.post(
            f"{BASE_URL}/query",
            json={"question": query},
            timeout=timeout
        )
        elapsed = time.time() - start
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                print(f"✅ 成功 (耗时: {elapsed:.2f}秒)")
                print(f"   类型: {result.get('query_type')}")
                answer = result.get('answer', '')
                if answer:
                    print(f"   回答: {answer[:100]}...")
            else:
                print(f"❌ 失败: {result.get('error')}")
        else:
            print(f"❌ HTTP {response.status_code}")
            
    except requests.exceptions.Timeout:
        print(f"⏱️  超时 (>{timeout}秒)")
    except Exception as e:
        print(f"❌ 错误: {str(e)}")

def main():
    print("=== 优化后的API测试 ===")
    
    # 测试不同类型的查询
    test_cases = [
        ("简单查询", "茅台股价", 30),
        ("带股票代码", "600519.SH最新价格", 30),
        ("成交量查询", "贵州茅台今天成交量", 45),
        ("复杂查询", "茅台最近5天平均价格", 60),
        ("RAG查询", "茅台2024年第一季度营收", 60),
    ]
    
    for desc, query, timeout in test_cases:
        print(f"\n--- {desc} ---")
        test_with_timeout(query, timeout)
        time.sleep(2)  # 避免过于频繁
    
    print("\n测试完成!")

if __name__ == "__main__":
    main()
