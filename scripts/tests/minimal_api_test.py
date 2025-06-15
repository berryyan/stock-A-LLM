# minimal_api_test.py
# 最小化API测试

import requests
import json

BASE_URL = "http://localhost:8000"

print("=== 最小化API测试 ===\n")

# 测试查询
queries = [
    "贵州茅台股价",
    "茅台2024年营收",
    "分析茅台投资价值"
]

for i, question in enumerate(queries, 1):
    print(f"{i}. 查询: {question}")
    
    response = requests.post(
        f"{BASE_URL}/query",
        json={"question": question},
        timeout=30
    )
    
    if response.status_code == 200:
        result = response.json()
        if result.get('success'):
            print(f"   ✅ 成功")
            print(f"   查询类型: {result.get('query_type')}")
            answer = result.get('answer', '')
            if answer:
                print(f"   回答: {answer[:100]}...")
        else:
            print(f"   ❌ 失败: {result.get('error')}")
    else:
        print(f"   ❌ HTTP {response.status_code}")
    
    print()

print("\n提示：如果仍然出现 QueryType 错误，请：")
print("1. 停止API服务 (Ctrl+C)")
print("2. 运行: python simple_fix_hybrid_agent.py")
print("3. 重新启动API服务: python api/main.py")
print("4. 再次运行此测试")
