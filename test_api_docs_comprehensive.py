#!/usr/bin/env python3
"""
API文档可用性和完整性检测脚本
检测OpenAPI.json生成问题和Swagger UI可用性
"""
import requests
import json
import time
from datetime import datetime

def test_api_docs_functionality():
    """测试API文档功能的完整性"""
    
    base_url = "http://10.0.0.66:8000"
    
    print("🔍 API文档可用性和完整性检测")
    print(f"目标服务器: {base_url}")
    print(f"测试时间: {datetime.now()}")
    print("=" * 60)
    
    results = {}
    
    # 1. 测试根路径
    print("\n1️⃣ 测试API根路径访问")
    try:
        response = requests.get(f"{base_url}/", timeout=10)
        if response.status_code == 200:
            print("✅ 根路径访问正常")
            results['root_path'] = 'success'
        else:
            print(f"❌ 根路径访问异常: HTTP {response.status_code}")
            results['root_path'] = f'failed_http_{response.status_code}'
    except Exception as e:
        print(f"❌ 根路径访问失败: {e}")
        results['root_path'] = f'failed_exception_{str(e)[:50]}'
    
    # 2. 测试OpenAPI JSON生成
    print("\n2️⃣ 测试OpenAPI JSON生成")
    try:
        response = requests.get(f"{base_url}/openapi.json", timeout=10)
        print(f"HTTP状态码: {response.status_code}")
        
        if response.status_code == 200:
            try:
                openapi_data = response.json()
                print("✅ OpenAPI JSON解析成功")
                print(f"📊 API标题: {openapi_data.get('info', {}).get('title', 'N/A')}")
                print(f"📊 API版本: {openapi_data.get('info', {}).get('version', 'N/A')}")
                print(f"📊 端点数量: {len(openapi_data.get('paths', {}))}")
                
                # 检查核心端点
                paths = openapi_data.get('paths', {})
                core_endpoints = ['/query', '/financial-analysis', '/money-flow-analysis']
                missing_endpoints = []
                
                for endpoint in core_endpoints:
                    if endpoint in paths:
                        print(f"✅ 核心端点存在: {endpoint}")
                    else:
                        print(f"❌ 核心端点缺失: {endpoint}")
                        missing_endpoints.append(endpoint)
                
                if not missing_endpoints:
                    results['openapi_json'] = 'success'
                    results['endpoints_complete'] = True
                else:
                    results['openapi_json'] = 'success_but_incomplete'
                    results['missing_endpoints'] = missing_endpoints
                    
            except json.JSONDecodeError as e:
                print(f"❌ OpenAPI JSON解析失败: {e}")
                print(f"响应内容预览: {response.text[:200]}...")
                results['openapi_json'] = 'failed_json_decode'
                
        elif response.status_code == 500:
            print("❌ OpenAPI生成内部服务器错误 (500)")
            print(f"错误响应: {response.text[:300]}...")
            results['openapi_json'] = 'failed_500_error'
            
        else:
            print(f"❌ OpenAPI访问异常: HTTP {response.status_code}")
            results['openapi_json'] = f'failed_http_{response.status_code}'
            
    except Exception as e:
        print(f"❌ OpenAPI请求失败: {e}")
        results['openapi_json'] = f'failed_exception_{str(e)[:50]}'
    
    # 3. 测试Swagger UI访问
    print("\n3️⃣ 测试Swagger UI访问")
    try:
        response = requests.get(f"{base_url}/docs", timeout=10)
        if response.status_code == 200:
            if 'swagger-ui' in response.text.lower():
                print("✅ Swagger UI页面加载正常")
                results['swagger_ui'] = 'success'
            else:
                print("⚠️  Swagger UI页面内容异常")
                results['swagger_ui'] = 'content_abnormal'
        else:
            print(f"❌ Swagger UI访问异常: HTTP {response.status_code}")
            results['swagger_ui'] = f'failed_http_{response.status_code}'
    except Exception as e:
        print(f"❌ Swagger UI访问失败: {e}")
        results['swagger_ui'] = f'failed_exception_{str(e)[:50]}'
    
    # 4. 测试ReDoc访问
    print("\n4️⃣ 测试ReDoc访问")
    try:
        response = requests.get(f"{base_url}/redoc", timeout=10)
        if response.status_code == 200:
            print("✅ ReDoc页面访问正常")
            results['redoc'] = 'success'
        else:
            print(f"❌ ReDoc访问异常: HTTP {response.status_code}")
            results['redoc'] = f'failed_http_{response.status_code}'
    except Exception as e:
        print(f"❌ ReDoc访问失败: {e}")
        results['redoc'] = f'failed_exception_{str(e)[:50]}'
    
    # 5. 测试API健康检查
    print("\n5️⃣ 测试API健康检查")
    try:
        response = requests.get(f"{base_url}/health", timeout=10)
        if response.status_code == 200:
            health_data = response.json()
            print("✅ 健康检查正常")
            print(f"📊 系统状态: {health_data.get('status', 'N/A')}")
            results['health_check'] = 'success'
        else:
            print(f"❌ 健康检查异常: HTTP {response.status_code}")
            results['health_check'] = f'failed_http_{response.status_code}'
    except Exception as e:
        print(f"❌ 健康检查失败: {e}")
        results['health_check'] = f'failed_exception_{str(e)[:50]}'
    
    # 6. 测试核心查询功能
    print("\n6️⃣ 测试核心查询功能")
    try:
        test_payload = {
            "question": "系统状态测试",
            "top_k": 1
        }
        response = requests.post(
            f"{base_url}/query", 
            json=test_payload,
            timeout=15
        )
        if response.status_code == 200:
            query_result = response.json()
            if query_result.get('success'):
                print("✅ 核心查询功能正常")
                results['core_query'] = 'success'
            else:
                print(f"⚠️  查询执行失败: {query_result.get('error', 'Unknown')}")
                results['core_query'] = 'query_failed'
        else:
            print(f"❌ 查询请求异常: HTTP {response.status_code}")
            results['core_query'] = f'failed_http_{response.status_code}'
    except Exception as e:
        print(f"❌ 查询功能测试失败: {e}")
        results['core_query'] = f'failed_exception_{str(e)[:50]}'
    
    # 生成测试总结
    print("\n" + "=" * 60)
    print("📊 API文档检测结果总结")
    print("=" * 60)
    
    success_count = sum(1 for v in results.values() if v == 'success')
    total_count = len(results)
    success_rate = (success_count / total_count) * 100
    
    print(f"✅ 成功项目: {success_count}/{total_count}")
    print(f"📊 成功率: {success_rate:.1f}%")
    
    print("\n📋 详细结果:")
    status_map = {
        'success': '✅',
        'failed_500_error': '❌ (500错误)',
        'failed_json_decode': '❌ (JSON解析失败)',
        'content_abnormal': '⚠️  (内容异常)',
        'query_failed': '⚠️  (查询失败)'
    }
    
    for test_name, result in results.items():
        icon = status_map.get(result, '❌' if 'failed' in result else '⚠️ ')
        print(f"  {icon} {test_name}: {result}")
    
    # 问题诊断建议
    if results.get('openapi_json') == 'failed_500_error':
        print("\n🔧 问题诊断建议:")
        print("❌ OpenAPI生成500错误 - 可能原因:")
        print("  1. Pydantic模型定义有循环引用")
        print("  2. FastAPI应用启动时某个模块导入失败")
        print("  3. 某个路由函数的类型注解有问题")
        print("  4. API文档生成过程中访问了异常的资源")
        print("\n💡 建议检查:")
        print("  - 检查api/main.py中的所有路由定义")
        print("  - 检查Pydantic模型的Field定义")
        print("  - 查看API服务器启动日志")
        print("  - 尝试注释掉部分路由逐一排查")
    
    return results

if __name__ == "__main__":
    test_api_docs_functionality()