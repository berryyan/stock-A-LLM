# test_timeout_fixed.py
import requests
import time

BASE_URL = "http://localhost:8000"

print("=== 测试超时修复效果 ===\n")

# 测试之前会超时的查询
test_queries = [
    "600519今天的成交量",
    "贵州茅台今天的股价",
    "茅台昨天的涨跌幅",
    "贵州茅台最新收盘价"
]

for i, query in enumerate(test_queries, 1):
    print(f"{i}. 测试查询: {query}")
    
    start_time = time.time()
    
    try:
        response = requests.post(
            f"{BASE_URL}/query",
            json={"question": query},
            timeout=90
        )
        
        elapsed = time.time() - start_time
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                print(f"   ✅ 成功 (耗时: {elapsed:.1f}秒)")
                answer = str(result.get('answer', ''))[:80]
                print(f"   结果: {answer}...")
            else:
                print(f"   ❌ 失败: {result.get('error')}")
        else:
            print(f"   ❌ HTTP {response.status_code}")
            
    except requests.exceptions.Timeout:
        print(f"   ⏱️ 超时 (>90秒)")
    except Exception as e:
        print(f"   ❌ 错误: {str(e)}")
    
    print()
    time.sleep(2)

print("测试完成!")
