# 文件名: test_api_client.py
# 测试API功能

import requests
import json

API_BASE_URL = "http://localhost:8000"

def test_health():
    """测试健康检查"""
    print("1. 测试健康检查")
    response = requests.get(f"{API_BASE_URL}/health")
    print(f"状态码: {response.status_code}")
    print(f"响应: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    print()

def test_status():
    """测试系统状态"""
    print("2. 测试系统状态")
    response = requests.get(f"{API_BASE_URL}/status")
    print(f"状态码: {response.status_code}")
    print(f"响应: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    print()

def test_query():
    """测试查询功能"""
    print("3. 测试查询功能")
    
    queries = [
        "贵州茅台最新股价是多少？",
        "贵州茅台2024年第一季度的表现如何？",
        "比较茅台和五粮液的市值"
    ]
    
    for question in queries[:1]:  # 先测试第一个
        print(f"\n查询: {question}")
        response = requests.post(
            f"{API_BASE_URL}/query",
            json={"question": question}
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"成功: {result['success']}")
            if result['success']:
                print(f"查询类型: {result.get('query_type', 'N/A')}")
                print(f"答案: {result.get('answer', 'N/A')[:200]}...")
            else:
                print(f"错误: {result.get('error', 'N/A')}")
        else:
            print(f"请求失败: {response.status_code}")

def test_suggestions():
    """测试查询建议"""
    print("\n4. 测试查询建议")
    response = requests.get(f"{API_BASE_URL}/suggestions?q=茅台")
    if response.status_code == 200:
        suggestions = response.json()['suggestions']
        print("建议查询:")
        for i, suggestion in enumerate(suggestions, 1):
            print(f"  {i}. {suggestion}")
    print()

def test_recent_reports():
    """测试最近报告"""
    print("5. 测试最近报告")
    response = requests.get(f"{API_BASE_URL}/reports/recent?days=7&limit=3")
    if response.status_code == 200:
        data = response.json()
        print(f"时间范围: {data['period']['start']} - {data['period']['end']}")
        print(f"找到 {data['total']} 份报告")
        for report in data['reports'][:3]:
            print(f"  - {report['ts_code']} {report['name']}: {report['title'][:50]}...")
    print()

def test_compare():
    """测试公司比较"""
    print("6. 测试公司比较")
    response = requests.post(
        f"{API_BASE_URL}/compare",
        json={
            "companies": ["600519.SH", "000858.SZ"],
            "aspect": "最新股价"
        }
    )
    if response.status_code == 200:
        result = response.json()
        print(f"比较成功: {result['success']}")
        if result['success']:
            print(f"比较结果: {result.get('comparison', 'N/A')[:200]}...")
    print()

def main():
    print("股票分析系统 API 测试")
    print("="*60)
    
    try:
        # 测试基础功能
        test_health()
        test_status()
        
        # 测试查询功能
        test_query()
        test_suggestions()
        test_recent_reports()
        
        # 测试高级功能
        test_compare()
        
    except requests.exceptions.ConnectionError:
        print("错误: 无法连接到API服务器")
        print("请确保API服务器正在运行: python -m api.main")
    except Exception as e:
        print(f"测试失败: {e}")

if __name__ == "__main__":
    main()
