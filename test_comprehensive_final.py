#!/usr/bin/env python3
"""
综合功能测试 - 最终验证
包含资金流向分析和智能日期解析功能的完整测试
"""
import requests
import json
import time
from datetime import datetime

def test_all_functions():
    """综合测试所有功能"""
    
    base_url = "http://localhost:8000"
    
    print("🔬 股票分析系统 v1.4.1 综合功能测试")
    print("=" * 80)
    print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"API地址: {base_url}")
    print("测试目标: 验证RAG修复后的系统完整性")
    print("")
    
    # 测试计划
    test_plans = [
        {
            "category": "💰 资金流向分析功能",
            "tests": [
                {
                    "name": "主力资金流向查询",
                    "question": "600519.SH最近的资金流向如何？",
                    "query_type": "sql"
                },
                {
                    "name": "超大单资金分析", 
                    "question": "600519.SH超大单分析",
                    "query_type": "sql"
                },
                {
                    "name": "资金流向趋势分析",
                    "question": "600519.SH趋势分析",
                    "query_type": "hybrid"
                },
                {
                    "name": "美的集团资金流向",
                    "question": "美的集团最近三个月趋势分析",
                    "query_type": "hybrid"
                }
            ]
        },
        {
            "category": "🧠 智能日期解析功能",
            "tests": [
                {
                    "name": "最新股价查询",
                    "question": "茅台最新股价是多少？",
                    "query_type": "sql"
                },
                {
                    "name": "最新财务数据",
                    "question": "贵州茅台最新财务数据",
                    "query_type": "sql"
                },
                {
                    "name": "最新公告查询（RAG）",
                    "question": "贵州茅台最新公告说了什么",
                    "query_type": "rag"
                },
                {
                    "name": "现在时间表达",
                    "question": "比亚迪现在的股价如何？",
                    "query_type": "sql"
                }
            ]
        }
    ]
    
    overall_results = []
    
    for plan in test_plans:
        print(f"\n{plan['category']}")
        print("=" * 60)
        
        category_results = []
        
        for i, test_case in enumerate(plan['tests'], 1):
            print(f"\n{i}. {test_case['name']}")
            print(f"   问题: {test_case['question']}")
            print(f"   类型: {test_case['query_type']}")
            
            try:
                start_time = time.time()
                
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
                    
                    test_result = {
                        "category": plan['category'],
                        "test_name": test_case['name'],
                        "question": test_case['question'],
                        "query_type": test_case['query_type'],
                        "success": result.get('success', False),
                        "duration": duration,
                        "answer_length": len(result.get('answer', '')),
                        "actual_query_type": result.get('query_type', ''),
                    }
                    
                    if result.get('success'):
                        print(f"   ✅ 成功 ({duration:.1f}s) - {len(result.get('answer', ''))}字符")
                        
                        # 简要分析
                        answer = result.get('answer', '')
                        if '资金' in answer or '流入' in answer or '流出' in answer:
                            print(f"   💰 包含资金流向信息")
                        if any(date_indicator in answer for date_indicator in ['2024', '2025', '最新', '最近']):
                            print(f"   📅 包含时间信息")
                        
                    else:
                        error = result.get('error', 'unknown')
                        print(f"   ❌ 失败: {error}")
                        test_result['error'] = error
                    
                    category_results.append(test_result)
                    
                else:
                    print(f"   ❌ HTTP错误: {response.status_code}")
                    category_results.append({
                        "category": plan['category'],
                        "test_name": test_case['name'],
                        "success": False,
                        "http_error": response.status_code
                    })
                    
            except requests.exceptions.ConnectionError:
                print(f"   ❌ 连接失败")
                print("   💡 请确认API服务器已在Windows环境启动")
                category_results.append({
                    "category": plan['category'],
                    "test_name": test_case['name'],
                    "success": False,
                    "error": "连接失败"
                })
                break
            except Exception as e:
                print(f"   ❌ 异常: {e}")
                category_results.append({
                    "category": plan['category'],
                    "test_name": test_case['name'],
                    "success": False,
                    "error": str(e)
                })
            
            time.sleep(1.5)  # 控制请求频率
        
        overall_results.extend(category_results)
        
        # 分类总结
        successful = sum(1 for r in category_results if r['success'])
        total = len(category_results)
        print(f"\n{plan['category']} 总结: {successful}/{total} 通过 ({(successful/total*100) if total > 0 else 0:.1f}%)")
    
    # 最终报告
    print(f"\n📊 最终测试报告")
    print("=" * 80)
    
    total_tests = len(overall_results)
    successful_tests = sum(1 for r in overall_results if r['success'])
    success_rate = (successful_tests / total_tests * 100) if total_tests > 0 else 0
    
    print(f"📈 总体统计:")
    print(f"   总测试数: {total_tests}")
    print(f"   成功数: {successful_tests}")
    print(f"   成功率: {success_rate:.1f}%")
    
    # 按功能分类统计
    money_flow_tests = [r for r in overall_results if '💰' in r.get('category', '')]
    date_intelligence_tests = [r for r in overall_results if '🧠' in r.get('category', '')]
    
    if money_flow_tests:
        mf_success = sum(1 for r in money_flow_tests if r['success'])
        print(f"   💰 资金流向分析: {mf_success}/{len(money_flow_tests)} ({(mf_success/len(money_flow_tests)*100):.1f}%)")
    
    if date_intelligence_tests:
        di_success = sum(1 for r in date_intelligence_tests if r['success'])
        print(f"   🧠 智能日期解析: {di_success}/{len(date_intelligence_tests)} ({(di_success/len(date_intelligence_tests)*100):.1f}%)")
    
    # 按查询类型统计
    sql_tests = [r for r in overall_results if r.get('query_type') == 'sql']
    rag_tests = [r for r in overall_results if r.get('query_type') == 'rag']
    hybrid_tests = [r for r in overall_results if r.get('query_type') == 'hybrid']
    
    print(f"\n📊 按查询类型统计:")
    if sql_tests:
        sql_success = sum(1 for r in sql_tests if r['success'])
        print(f"   SQL查询: {sql_success}/{len(sql_tests)} ({(sql_success/len(sql_tests)*100):.1f}%)")
    
    if rag_tests:
        rag_success = sum(1 for r in rag_tests if r['success'])
        print(f"   RAG查询: {rag_success}/{len(rag_tests)} ({(rag_success/len(rag_tests)*100):.1f}%)")
    
    if hybrid_tests:
        hybrid_success = sum(1 for r in hybrid_tests if r['success'])
        print(f"   Hybrid查询: {hybrid_success}/{len(hybrid_tests)} ({(hybrid_success/len(hybrid_tests)*100):.1f}%)")
    
    # 性能统计
    successful_results = [r for r in overall_results if r['success'] and 'duration' in r]
    if successful_results:
        avg_duration = sum(r['duration'] for r in successful_results) / len(successful_results)
        print(f"\n⏱️  平均响应时间: {avg_duration:.1f}秒")
    
    # 结论
    print(f"\n🎯 测试结论:")
    if success_rate >= 90:
        print("🎉 系统功能优秀！所有主要功能运行正常")
        print("✅ RAG修复完全成功，未影响其他功能")
        print("✅ 资金流向分析功能正常")
        print("✅ 智能日期解析功能正常")
    elif success_rate >= 75:
        print("👍 系统功能良好，大部分功能正常运行")
        print("⚠️  少数测试失败，可能需要微调")
    elif success_rate >= 50:
        print("⚠️  系统功能一般，有一些问题需要解决")
    else:
        print("❌ 系统功能存在较多问题，需要进一步调试")
    
    print(f"\n📋 下一步建议:")
    if success_rate >= 90:
        print("1. 完成版本管理和文档更新")
        print("2. 部署到生产环境")
        print("3. 进行用户验收测试")
    else:
        print("1. 分析失败的测试用例")
        print("2. 针对性修复问题")
        print("3. 重新进行完整测试")
    
    return overall_results

if __name__ == "__main__":
    test_all_functions()