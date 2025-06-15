# test_api_client_fixed.py
import requests
import json
from datetime import datetime, timedelta

# API基础URL
BASE_URL = "http://localhost:8000"

def print_section(title):
    print(f"\n{'='*60}")
    print(f"{title}")
    print('='*60)

def test_health():
    """测试健康检查"""
    print_section("1. 测试健康检查")
    response = requests.get(f"{BASE_URL}/health")
    print(f"状态码: {response.status_code}")
    print(f"响应: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")

def test_status():
    """测试系统状态"""
    print_section("2. 测试系统状态")
    response = requests.get(f"{BASE_URL}/status")
    print(f"状态码: {response.status_code}")
    print(f"响应: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")

def test_query_types():
    """测试不同的查询类型值"""
    print_section("3. 测试查询类型")
    
    # 尝试不同的可能值
    possible_types = [
        "sql", "SQL", "sql_only",
        "rag", "RAG", "rag_only",
        "hybrid", "HYBRID", "auto", "AUTO"
    ]
    
    test_query = "贵州茅台最新股价"
    
    for query_type in possible_types:
        try:
            response = requests.post(
                f"{BASE_URL}/query",
                json={
                    "query": test_query,
                    "query_type": query_type
                }
            )
            if response.status_code == 200:
                print(f"✅ 成功: query_type='{query_type}'")
                print(f"   响应: {response.json()['data'][:100]}...")
                break
            else:
                error = response.json().get('detail', 'Unknown error')
                print(f"❌ 失败: query_type='{query_type}' - {error}")
        except Exception as e:
            print(f"❌ 错误: query_type='{query_type}' - {str(e)}")

def test_direct_endpoints():
    """直接测试各个端点"""
    print_section("4. 直接测试各端点")
    
    endpoints = [
        ("/sql", "贵州茅台最新股价"),
        ("/rag", "茅台2024年营收情况"),
        ("/hybrid", "分析贵州茅台的投资价值")
    ]
    
    for endpoint, query in endpoints:
        print(f"\n测试 {endpoint}:")
        try:
            response = requests.post(
                f"{BASE_URL}{endpoint}",
                json={"query": query}
            )
            if response.status_code == 200:
                result = response.json()
                print(f"✅ 成功")
                print(f"   类型: {result.get('query_type', 'N/A')}")
                print(f"   数据: {str(result.get('data', ''))[:200]}...")
            else:
                print(f"❌ 失败: {response.status_code}")
                print(f"   错误: {response.json()}")
        except Exception as e:
            print(f"❌ 异常: {str(e)}")

def test_companies():
    """测试公司列表"""
    print_section("5. 测试公司列表")
    
    # 获取公司列表
    response = requests.get(f"{BASE_URL}/companies")
    if response.status_code == 200:
        companies = response.json()
        print(f"✅ 获取到 {len(companies)} 家公司")
        # 显示前5家
        for company in companies[:5]:
            print(f"   - {company.get('code', 'N/A')}: {company.get('name', 'N/A')}")
    else:
        print(f"❌ 失败: {response.status_code}")

def test_recent_announcements():
    """测试最近公告"""
    print_section("6. 测试最近公告")
    
    # 使用正确的参数格式
    params = {
        "start_date": (datetime.now() - timedelta(days=7)).strftime("%Y%m%d"),
        "end_date": datetime.now().strftime("%Y%m%d"),
        "limit": 5
    }
    
    response = requests.get(f"{BASE_URL}/announcements/recent", params=params)
    if response.status_code == 200:
        announcements = response.json()
        print(f"✅ 找到 {len(announcements)} 份公告")
        for ann in announcements:
            print(f"   - {ann.get('ts_code', 'N/A')}: {ann.get('title', 'N/A')[:50]}...")
    else:
        print(f"❌ 失败: {response.status_code}")
        print(f"   错误: {response.text}")

def test_swagger_ui():
    """提供Swagger UI使用指南"""
    print_section("7. Swagger UI 使用指南")
    print("""
1. 打开浏览器访问: http://localhost:8000/docs

2. 使用步骤:
   a) 找到想要测试的端点（如 POST /query）
   b) 点击端点展开详情
   c) 点击 "Try it out" 按钮
   d) 在请求体中输入参数，例如:
      {
        "query": "贵州茅台最新股价",
        "query_type": "sql"  // 注意使用小写
      }
   e) 点击 "Execute" 执行请求
   f) 查看下方的响应结果

3. 推荐测试顺序:
   - GET /health （无参数）
   - GET /status （无参数）
   - POST /sql （只需要query参数）
   - POST /rag （只需要query参数）
   - POST /query （需要query和query_type参数）
""")

if __name__ == "__main__":
    print("股票分析系统 API 测试（修复版）")
    print("="*60)
    
    # 运行所有测试
    test_health()
    test_status()
    test_query_types()
    test_direct_endpoints()
    test_companies()
    test_recent_announcements()
    test_swagger_ui()
    
    print("\n" + "="*60)
    print("测试完成！")