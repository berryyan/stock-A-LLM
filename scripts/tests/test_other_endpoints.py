# test_other_endpoints.py
# 测试其他可用的API端点

import requests
import json

BASE_URL = "http://localhost:8000"

print("=== 测试其他API端点 ===\n")

# 1. 测试建议端点
print("1. 测试 /suggestions:")
response = requests.get(f"{BASE_URL}/suggestions")
if response.status_code == 200:
    suggestions = response.json()
    print(f"✅ 成功，获得 {len(suggestions)} 个建议:")
    for s in suggestions[:3]:
        print(f"   - {s}")
else:
    print(f"❌ 失败: {response.status_code}")

# 2. 测试公司列表
print("\n2. 测试 /companies:")
response = requests.get(f"{BASE_URL}/companies")
if response.status_code == 200:
    companies = response.json()
    print(f"✅ 成功，获得 {len(companies)} 家公司")
    # 显示前3家
    for company in companies[:3]:
        if isinstance(company, dict):
            print(f"   - {company.get('code', 'N/A')}: {company.get('name', 'N/A')}")
        else:
            print(f"   - {company}")
else:
    print(f"❌ 失败: {response.status_code}")
    print(f"   错误: {response.text}")

# 3. 测试最近报告
print("\n3. 测试 /reports/recent:")
response = requests.get(f"{BASE_URL}/reports/recent")
if response.status_code == 200:
    reports = response.json()
    print(f"✅ 成功，获得 {len(reports)} 份报告")
    for report in reports[:3]:
        print(f"   - {report.get('title', 'N/A')[:50]}...")
else:
    print(f"❌ 失败: {response.status_code}")

# 4. 测试比较功能
print("\n4. 测试 /compare:")
compare_data = {
    "companies": ["贵州茅台", "五粮液"],
    "metrics": ["营收", "利润"]
}
response = requests.post(f"{BASE_URL}/compare", json=compare_data)
if response.status_code == 200:
    print("✅ 成功")
    result = response.json()
    print(f"   结果: {str(result)[:200]}...")
else:
    print(f"❌ 失败: {response.status_code}")
    print(f"   错误: {response.json()}")

# 5. 测试流式查询
print("\n5. 测试 /query/stream:")
print("   (流式接口测试较复杂，跳过)")

print("\n" + "="*50)
print("\n建议的下一步:")
print("1. 查看API服务的日志窗口，找到具体的错误信息")
print("2. 检查 agents/hybrid_agent.py 中的 QueryType 定义")
print("3. 运行 fix_query_type.py 诊断工具")
print("4. 考虑直接修改源代码中的枚举值定义")