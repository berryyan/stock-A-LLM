# test_api_correct.py
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

def test_query_endpoint():
    """测试查询端点 - 使用正确的参数名"""
    print_section("3. 测试查询端点")
    
    # 测试查询 - 使用 'question' 而不是 'query'
    test_queries = [
        {
            "question": "贵州茅台最新股价是多少？",
            "top_k": 5
        },
        {
            "question": "茅台2024年营收情况",
            "context": {"company": "贵州茅台"},
            "top_k": 3
        },
        {
            "question": "分析贵州茅台的投资价值",
            "filters": {"year": 2024}
        }
    ]
    
    for i, query_data in enumerate(test_queries, 1):
        print(f"\n测试查询 {i}: {query_data['question']}")
        try:
            response = requests.post(
                f"{BASE_URL}/query",
                json=query_data
            )
            if response.status_code == 200:
                result = response.json()
                print(f"✅ 成功")
                print(f"   响应预览: {str(result)[:200]}...")
            else:
                print(f"❌ 失败: {response.status_code}")
                print(f"   错误: {response.json()}")
        except Exception as e:
            print(f"❌ 异常: {str(e)}")

def test_api_exploration():
    """探索API的实际端点"""
    print_section("4. 探索可用的API端点")
    
    # 从OpenAPI文档获取所有端点
    try:
        response = requests.get(f"{BASE_URL}/openapi.json")
        if response.status_code == 200:
            openapi = response.json()
            paths = openapi.get("paths", {})
            
            print("可用的API端点:")
            for path, methods in paths.items():
                for method in methods:
                    print(f"  {method.upper()} {path}")
                    
            # 测试一些可能的端点
            possible_endpoints = [
                ("/search", {"question": "贵州茅台股价"}),
                ("/ask", {"question": "贵州茅台股价"}),
                ("/chat", {"question": "贵州茅台股价"}),
                ("/analyze", {"question": "贵州茅台股价"}),
            ]
            
            print("\n尝试其他可能的端点:")
            for endpoint, data in possible_endpoints:
                try:
                    response = requests.post(f"{BASE_URL}{endpoint}", json=data)
                    if response.status_code != 404:
                        print(f"  ✅ {endpoint} - 状态码: {response.status_code}")
                except:
                    pass
                    
    except Exception as e:
        print(f"无法获取OpenAPI文档: {e}")

def test_with_curl_commands():
    """提供curl命令示例"""
    print_section("5. CURL命令测试示例")
    
    print("""
# 1. 测试基本查询
curl -X POST http://localhost:8000/query \\
  -H "Content-Type: application/json" \\
  -d '{"question": "贵州茅台最新股价"}'

# 2. 带参数的查询
curl -X POST http://localhost:8000/query \\
  -H "Content-Type: application/json" \\
  -d '{
    "question": "茅台2024年营收情况",
    "top_k": 3,
    "context": {"company": "贵州茅台"}
  }'

# 3. 获取所有端点信息
curl http://localhost:8000/openapi.json | python -m json.tool
""")

def test_minimal_query():
    """最简单的查询测试"""
    print_section("6. 最简单的查询测试")
    
    # 最基础的请求
    data = {"question": "贵州茅台"}
    
    print(f"发送请求: {json.dumps(data, ensure_ascii=False)}")
    
    try:
        response = requests.post(
            f"{BASE_URL}/query",
            json=data,
            timeout=30
        )
        
        print(f"状态码: {response.status_code}")
        print(f"响应头: {dict(response.headers)}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ 成功!")
            print(f"完整响应: {json.dumps(result, indent=2, ensure_ascii=False)}")
        else:
            print(f"❌ 失败")
            print(f"错误响应: {response.text}")
            
    except requests.exceptions.Timeout:
        print("❌ 请求超时（30秒）")
    except Exception as e:
        print(f"❌ 异常: {type(e).__name__}: {str(e)}")

def print_usage_guide():
    """打印使用指南"""
    print_section("使用指南")
    
    print("""
根据API定义，正确的请求格式是：

POST /query
{
    "question": "用户问题",     // 必需
    "context": {},             // 可选，上下文信息
    "filters": {},             // 可选，过滤条件
    "top_k": 5                 // 可选，返回结果数量
}

注意：
1. 参数名是 'question' 而不是 'query'
2. 只有 'question' 是必需的
3. 没有 'query_type' 参数

在Swagger UI中测试：
1. 访问 http://localhost:8000/docs
2. 找到 POST /query 端点
3. 点击 "Try it out"
4. 输入正确的JSON格式
5. 执行请求
""")

if __name__ == "__main__":
    print("股票分析系统 API 测试（正确版）")
    print("="*60)
    
    # 运行测试
    test_health()
    test_status()
    test_query_endpoint()
    test_api_exploration()
    test_minimal_query()
    test_with_curl_commands()
    print_usage_guide()
    
    print("\n" + "="*60)
    print("测试完成！")