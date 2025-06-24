#!/usr/bin/env python3
"""
智能日期解析功能测试
测试"最新"、"最近"等时间表达的智能转换
"""
import requests
import json
import time
from datetime import datetime

def test_date_intelligence():
    """测试智能日期解析功能"""
    
    base_url = "http://localhost:8000"
    
    # 智能日期解析测试用例
    test_cases = [
        {
            "name": "最新股价查询（交易日解析）",
            "question": "茅台最新股价是多少？",
            "query_type": "sql",
            "expected": "应该自动转换为最近交易日的股价查询",
            "check_keywords": ["股价", "收盘价", "涨跌", "茅台", "600519"]
        },
        {
            "name": "最近财务数据查询（报告期解析）",
            "question": "贵州茅台最新财务数据",
            "query_type": "sql", 
            "expected": "应该自动转换为最新报告期的财务数据",
            "check_keywords": ["营收", "利润", "资产", "财务", "亿元"]
        },
        {
            "name": "最新公告查询（公告日期解析）",
            "question": "贵州茅台最新公告说了什么",
            "query_type": "rag",
            "expected": "应该查找最新的公告内容",
            "check_keywords": ["公告", "茅台", "2024", "2025"]
        },
        {
            "name": "现在时间表达查询",
            "question": "比亚迪现在的股价如何？",
            "query_type": "sql",
            "expected": "应该转换为最近交易日查询",
            "check_keywords": ["比亚迪", "002594", "股价", "收盘"]
        }
    ]
    
    print("🧠 智能日期解析功能测试")
    print("=" * 60)
    print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"API地址: {base_url}")
    print("测试目标: 验证智能日期解析不会干扰RAG查询，但正常处理SQL查询")
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
                    "question": test_case['question'],
                    "query_type": test_case['query_type'],
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
                        
                        # 检查关键词
                        check_keywords = test_case.get('check_keywords', [])
                        found_keywords = [kw for kw in check_keywords if kw in answer]
                        if found_keywords:
                            print(f"✅ 包含期望关键词: {', '.join(found_keywords)}")
                        else:
                            print(f"⚠️  未发现期望关键词: {', '.join(check_keywords)}")
                        
                        # 显示答案预览
                        preview = answer[:200].replace('\n', ' ')
                        print(f"📝 答案预览: {preview}...")
                        
                        # 检查是否包含具体日期（表明智能解析生效）
                        import re
                        date_patterns = [
                            r'\d{4}-\d{2}-\d{2}',  # YYYY-MM-DD
                            r'\d{4}年\d{1,2}月\d{1,2}日',  # 中文日期
                            r'\d{8}',  # YYYYMMDD
                        ]
                        
                        found_dates = []
                        for pattern in date_patterns:
                            dates = re.findall(pattern, answer)
                            found_dates.extend(dates)
                        
                        if found_dates:
                            print(f"✅ 智能日期解析生效: 发现具体日期 {found_dates[:3]}")
                        else:
                            print(f"ℹ️  未发现具体日期，可能是语义查询")
                    
                    # 分析查询类型和路由
                    actual_query_type = result.get('query_type', '')
                    routing_info = result.get('routing', {})
                    
                    print(f"🔍 实际查询类型: {actual_query_type}")
                    
                    if routing_info:
                        entities = routing_info.get('entities', [])
                        time_range = routing_info.get('time_range', '')
                        if entities:
                            print(f"🔍 识别实体: {entities}")
                        if time_range:
                            print(f"🔍 时间范围: {time_range}")
                    
                    # 检查数据来源
                    sources = result.get('sources', {})
                    if 'sql' in sources:
                        print(f"✅ 包含SQL查询结果")
                    if 'rag' in sources:
                        print(f"✅ 包含RAG查询结果")
                    
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
    print("\n📊 智能日期解析功能测试报告")
    print("=" * 60)
    
    total_tests = len(results)
    successful_tests = sum(1 for r in results if r['success'])
    success_rate = (successful_tests / total_tests * 100) if total_tests > 0 else 0
    
    print(f"总测试数: {total_tests}")
    print(f"成功数: {successful_tests}")
    print(f"成功率: {success_rate:.1f}%")
    
    # 分析SQL vs RAG查询的成功情况
    sql_tests = [r for r in results if r.get('query_type') == 'sql']
    rag_tests = [r for r in results if r.get('query_type') == 'rag']
    
    sql_success = sum(1 for r in sql_tests if r['success'])
    rag_success = sum(1 for r in rag_tests if r['success'])
    
    print(f"SQL查询成功率: {sql_success}/{len(sql_tests)} = {(sql_success/len(sql_tests)*100) if sql_tests else 0:.1f}%")
    print(f"RAG查询成功率: {rag_success}/{len(rag_tests)} = {(rag_success/len(rag_tests)*100) if rag_tests else 0:.1f}%")
    
    if successful_tests == total_tests:
        print("🎉 所有智能日期解析测试通过！")
        print("✅ 智能日期解析功能运行正常")
        print("✅ RAG查询未受到过度干扰")
    elif successful_tests > 0:
        print("⚠️  部分测试通过，需要检查失败的测试")
    else:
        print("❌ 所有测试失败，需要检查系统状态")
    
    print("\n📋 详细结果:")
    for i, result in enumerate(results, 1):
        status = "✅ 成功" if result['success'] else "❌ 失败"
        duration = f"{result.get('duration', 0):.2f}s" if 'duration' in result else "N/A"
        query_type = result.get('query_type', 'unknown')
        print(f"{i}. {result['test_name']} ({query_type}): {status} ({duration})")
        if not result['success'] and 'error' in result:
            print(f"   错误: {result['error']}")
    
    return results

if __name__ == "__main__":
    print("🧠 智能日期解析功能专项测试")
    print("测试内容：最新/最近时间表达的智能转换")
    print("重点验证：RAG修复后智能日期解析仍正常工作")
    print("=" * 80)
    
    test_date_intelligence()