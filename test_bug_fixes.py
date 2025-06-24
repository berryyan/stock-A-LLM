#!/usr/bin/env python3
"""
Bug修复验证测试
专门测试刚修复的两个Bug
"""
import requests
import json
import time
from datetime import datetime

def test_bug_fixes():
    """测试刚修复的两个Bug"""
    
    base_url = "http://localhost:8000"
    
    print("🔧 Bug修复验证测试")
    print("=" * 60)
    print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("目标：验证SQL输出解析错误和NoneType错误已修复")
    print("")
    
    # 测试用例 - 针对之前失败的两个查询
    test_cases = [
        {
            "name": "Bug 1: SQL输出解析错误修复测试",
            "question": "比较茅台和五粮液的资金流向",
            "query_type": "sql",
            "description": "之前失败原因：Could not parse LLM output",
            "expected": "应该正常返回资金流向对比结果"
        },
        {
            "name": "Bug 2: NoneType错误修复测试", 
            "question": "贵州茅台最新财务数据",
            "query_type": "sql",
            "description": "之前失败原因：object of type 'NoneType' has no len()",
            "expected": "应该正常返回财务数据"
        }
    ]
    
    results = []
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"测试 {i}: {test_case['name']}")
        print(f"问题: {test_case['question']}")
        print(f"类型: {test_case['query_type']}")
        print(f"之前问题: {test_case['description']}")
        print(f"期望结果: {test_case['expected']}")
        
        try:
            start_time = time.time()
            
            payload = {
                "question": test_case['question'],
                "query_type": test_case['query_type']
            }
            
            response = requests.post(
                f"{base_url}/query",
                json=payload
            )
            
            end_time = time.time()
            duration = end_time - start_time
            
            if response.status_code == 200:
                result = response.json()
                
                test_result = {
                    "test_name": test_case['name'],
                    "question": test_case['question'],
                    "success": result.get('success', False),
                    "duration": duration,
                    "response": result
                }
                results.append(test_result)
                
                print(f"✅ HTTP状态: {response.status_code}")
                print(f"⏱️  响应时间: {duration:.2f}秒")
                
                if result.get('success'):
                    print(f"🎉 测试成功: Bug已修复!")
                    
                    answer = result.get('answer', '')
                    if answer:
                        print(f"✅ 答案长度: {len(answer)}字符")
                        
                        # 检查是否包含预期内容
                        if test_case['name'].startswith("Bug 1"):
                            # 资金流向对比测试
                            if any(keyword in answer for keyword in ['茅台', '五粮液', '资金', '流向', '对比']):
                                print(f"✅ 包含资金流向对比信息")
                            else:
                                print(f"⚠️  答案内容可能不完整")
                        
                        elif test_case['name'].startswith("Bug 2"):
                            # 财务数据测试  
                            if any(keyword in answer for keyword in ['营收', '利润', '资产', '财务']):
                                print(f"✅ 包含财务数据信息")
                            else:
                                print(f"⚠️  答案内容可能不完整")
                        
                        # 显示答案预览
                        preview = answer[:150].replace('\n', ' ')
                        print(f"📝 答案预览: {preview}...")
                        
                else:
                    error = result.get('error', 'unknown error')
                    print(f"❌ 测试失败: {error}")
                    print(f"🔍 需要进一步检查错误原因")
                    test_result['error'] = error
                    
            else:
                print(f"❌ HTTP错误: {response.status_code}")
                test_result = {
                    "test_name": test_case['name'],
                    "success": False,
                    "duration": duration,
                    "http_error": response.status_code
                }
                results.append(test_result)
                
        except requests.exceptions.ConnectionError:
            print(f"❌ 连接失败 - API服务器未启动")
            results.append({
                "test_name": test_case['name'],
                "success": False,
                "error": "连接失败"
            })
            break
        except Exception as e:
            print(f"❌ 请求异常: {e}")
            results.append({
                "test_name": test_case['name'],
                "success": False,
                "error": str(e)
            })
        
        print("-" * 50)
        time.sleep(2)
    
    # 生成测试报告
    print("\\n📊 Bug修复验证报告")
    print("=" * 60)
    
    total_tests = len(results)
    successful_tests = sum(1 for r in results if r['success'])
    success_rate = (successful_tests / total_tests * 100) if total_tests > 0 else 0
    
    print(f"总测试数: {total_tests}")
    print(f"成功数: {successful_tests}")
    print(f"成功率: {success_rate:.1f}%")
    
    print(f"\\n📋 详细结果:")
    for i, result in enumerate(results, 1):
        status = "✅ 成功" if result['success'] else "❌ 失败"
        duration = f"{result.get('duration', 0):.2f}s" if 'duration' in result else "N/A"
        print(f"{i}. {result['test_name']}: {status} ({duration})")
        if not result['success'] and 'error' in result:
            print(f"   错误: {result['error']}")
    
    # 总结
    print(f"\\n🎯 修复验证结论:")
    if success_rate == 100:
        print("🎉 所有Bug已成功修复！")
        print("✅ SQL输出解析错误已解决")
        print("✅ NoneType错误已解决") 
        print("✅ 系统功能恢复正常")
    elif success_rate > 0:
        print("⚠️  部分Bug已修复，仍有问题需要解决")
    else:
        print("❌ Bug修复不成功，需要进一步调试")
    
    return results

if __name__ == "__main__":
    print("🔧 Bug修复专项验证测试")
    print("测试目标：验证SQL输出解析和NoneType错误修复")
    print("=" * 80)
    
    test_bug_fixes()