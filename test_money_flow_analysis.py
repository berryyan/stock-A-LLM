#!/usr/bin/env python3
"""
资金流向分析功能测试
使用 /query 接口测试资金流向相关功能
"""
import requests
import json
import time
from datetime import datetime

def test_money_flow_analysis():
    """测试资金流向分析功能"""
    
    base_url = "http://localhost:8000"
    
    # 资金流向分析测试用例
    test_cases = [
        {
            "name": "股票主力资金流向查询",
            "question": "600519.SH最近的资金流向如何？",
            "query_type": "sql",
            "expected": "应该返回贵州茅台的主力资金流向数据"
        },
        {
            "name": "超大单资金分析",
            "question": "600519.SH超大单资金流向分析",
            "query_type": "sql", 
            "expected": "应该返回超大单净流入/流出数据"
        },
        {
            "name": "行业资金流向对比",
            "question": "比较茅台和五粮液的资金流向",
            "query_type": "sql",
            "expected": "应该返回两只股票的资金流向对比"
        },
        {
            "name": "资金流向趋势分析",
            "question": "600519.SH最近一个月主力资金监控",
            "query_type": "hybrid",
            "expected": "应该结合数据和分析返回资金流向趋势"
        }
    ]
    
    print("💰 资金流向分析功能测试")
    print("=" * 60)
    print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"API地址: {base_url}")
    print("")
    
    results = []
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"测试 {i}: {test_case['name']}")
        print(f"问题: {test_case['question']}")
        print(f"类型: {test_case['query_type']}")
        print(f"期望: {test_case['expected']}")
        
        try:
            start_time = time.time()
            
            # 发送请求
            payload = {
                "question": test_case['question'],
                "query_type": test_case['query_type']
            }
            
            response = requests.post(
                f"{base_url}/query",
                json=payload
                # 移除timeout限制，让API有充足时间处理
            )
            
            end_time = time.time()
            duration = end_time - start_time
            
            if response.status_code == 200:
                result = response.json()
                
                # 记录测试结果
                test_result = {
                    "test_name": test_case['name'],
                    "success": result.get('success', False),
                    "duration": duration,
                    "response": result
                }
                results.append(test_result)
                
                print(f"✅ HTTP状态: {response.status_code}")
                print(f"⏱️  响应时间: {duration:.2f}秒")
                
                if result.get('success'):
                    print(f"✅ 查询成功: True")
                    
                    answer = result.get('answer', '')
                    if answer:
                        print(f"✅ 答案长度: {len(answer)}字符")
                        
                        # 检查是否包含资金流向相关信息
                        money_flow_keywords = [
                            '主力', '净流入', '净流出', '超大单', '大单', 
                            '中单', '小单', '资金', '流向', '万元', '亿元'
                        ]
                        
                        found_keywords = [kw for kw in money_flow_keywords if kw in answer]
                        if found_keywords:
                            print(f"✅ 包含资金流向关键词: {', '.join(found_keywords[:5])}")
                        else:
                            print(f"⚠️  未发现明显的资金流向关键词")
                        
                        # 显示答案预览
                        preview = answer[:200].replace('\n', ' ')
                        print(f"📝 答案预览: {preview}...")
                        
                    # 检查数据源
                    query_type = result.get('query_type', '')
                    sources = result.get('sources', {})
                    
                    if query_type == 'sql' and 'sql' in sources:
                        sql_info = sources['sql']
                        if isinstance(sql_info, dict) and sql_info.get('success'):
                            print(f"✅ SQL查询成功")
                        else:
                            print(f"⚠️  SQL查询可能有问题")
                    
                    if 'rag' in sources:
                        rag_info = sources['rag']
                        if isinstance(rag_info, dict) and rag_info.get('success'):
                            print(f"✅ RAG查询成功")
                    
                else:
                    error = result.get('error', 'unknown error')
                    print(f"❌ 查询失败: {error}")
                    test_result['error'] = error
                    
            else:
                print(f"❌ HTTP错误: {response.status_code}")
                print(f"响应内容: {response.text[:200]}...")
                
                test_result = {
                    "test_name": test_case['name'],
                    "success": False,
                    "duration": duration,
                    "http_error": response.status_code,
                    "error": response.text[:200]
                }
                results.append(test_result)
                
        # 移除了超时处理，因为已经去掉timeout参数
        except requests.exceptions.ConnectionError:
            print(f"❌ 连接失败 - API服务器未启动或网络问题")
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
        time.sleep(2)  # 避免请求过快
    
    # 生成测试报告
    print("\n📊 资金流向分析功能测试报告")
    print("=" * 60)
    
    total_tests = len(results)
    successful_tests = sum(1 for r in results if r['success'])
    success_rate = (successful_tests / total_tests * 100) if total_tests > 0 else 0
    
    print(f"总测试数: {total_tests}")
    print(f"成功数: {successful_tests}")
    print(f"成功率: {success_rate:.1f}%")
    
    if successful_tests == total_tests:
        print("🎉 所有资金流向分析测试通过！")
    elif successful_tests > 0:
        print("⚠️  部分测试通过，需要检查失败的测试")
    else:
        print("❌ 所有测试失败，需要检查系统状态")
    
    print("\n📋 详细结果:")
    for i, result in enumerate(results, 1):
        status = "✅ 成功" if result['success'] else "❌ 失败"
        duration = f"{result.get('duration', 0):.2f}s" if 'duration' in result else "N/A"
        print(f"{i}. {result['test_name']}: {status} ({duration})")
        if not result['success'] and 'error' in result:
            print(f"   错误: {result['error']}")
    
    return results

if __name__ == "__main__":
    print("💰 资金流向分析功能专项测试")
    print("测试内容：主力资金、超大单分析、资金流向对比、趋势分析")
    print("=" * 80)
    
    test_money_flow_analysis()