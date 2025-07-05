#!/usr/bin/env python3
"""
测试前端错误信息显示功能
"""
import requests
import json

# API基础URL
API_URL = "http://localhost:8000"

def test_error_display():
    """测试各种错误情况下的前端显示"""
    
    # 测试用例列表
    test_cases = [
        {
            "name": "无效股票代码",
            "query": "INVALID123.SH的最新股价",
            "expected_error": "股票代码"
        },
        {
            "name": "股票名称错误",
            "query": "不存在的公司最新股价",
            "expected_error": "无法识别"
        },
        {
            "name": "复杂查询错误",
            "query": "分析一个不存在的股票XYZ的财务状况",
            "expected_error": "无法识别"
        }
    ]
    
    print("开始测试错误信息显示功能...")
    print("=" * 60)
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n测试 {i}: {test_case['name']}")
        print(f"查询: {test_case['query']}")
        
        try:
            # 发送查询请求
            response = requests.post(
                f"{API_URL}/query",
                json={"question": test_case['query']},
                headers={"Content-Type": "application/json"},
                timeout=30
            )
            
            # 解析响应
            result = response.json()
            
            print(f"响应状态码: {response.status_code}")
            print(f"Success: {result.get('success', 'N/A')}")
            
            if result.get('success') is False:
                error_msg = result.get('error', '无错误信息')
                print(f"错误信息: {error_msg}")
                
                # 检查错误信息是否包含预期内容
                if test_case['expected_error'] in error_msg:
                    print(f"✅ 错误信息包含预期内容: '{test_case['expected_error']}'")
                else:
                    print(f"❌ 错误信息未包含预期内容: '{test_case['expected_error']}'")
            else:
                print(f"答案: {result.get('answer', 'N/A')[:100]}...")
                
        except requests.exceptions.RequestException as e:
            print(f"❌ 请求失败: {e}")
        except json.JSONDecodeError as e:
            print(f"❌ JSON解析失败: {e}")
        
        print("-" * 60)
    
    print("\n测试完成！")
    print("\n📌 请在浏览器中访问 http://localhost:3000 并尝试以下查询：")
    for test_case in test_cases:
        print(f"   - {test_case['query']}")
    print("\n确认错误信息是否正确显示在聊天界面中。")

if __name__ == "__main__":
    test_error_display()