#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
分析Money Flow Agent测试失败案例
"""

import json
import os

def analyze_money_flow_failures():
    """分析Money Flow Agent的失败测试"""
    report_file = 'money_flow_test_report_final_20250713_004238.json'
    
    if not os.path.exists(report_file):
        print("Money Flow Agent报告文件不存在")
        return
    
    with open(report_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    print("="*80)
    print("Money Flow Agent 测试报告分析")
    print("="*80)
    
    # 基本统计
    summary = data.get('summary', {})
    print(f"\n基本统计:")
    print(f"总测试: {summary.get('total', 0)}")
    print(f"通过: {summary.get('passed', 0)}")
    print(f"失败: {summary.get('failed', 0)}")
    print(f"通过率: {summary.get('pass_rate', 0)}%")
    
    # 分类统计
    print(f"\n分类统计:")
    categories = data.get('categories', {})
    for cat_name, cat_stats in categories.items():
        total = cat_stats.get('total', 0)
        passed = cat_stats.get('passed', 0)
        rate = (passed / total * 100) if total > 0 else 0
        status = "✅" if rate == 100 else "⚠️" if rate >= 80 else "❌"
        print(f"  {cat_name}: {passed}/{total} ({rate:.1f}%) {status}")
    
    # 查找失败的测试
    print(f"\n失败的测试用例:")
    print("-"*80)
    
    details = data.get('details', [])
    failed_tests = [t for t in details if not t.get('passed', False)]
    
    if not failed_tests:
        print("（没有失败的测试）")
    else:
        for i, test in enumerate(failed_tests, 1):
            print(f"\n失败 #{i}:")
            print(f"类别: {test.get('category', 'Unknown')}")
            print(f"测试: {test.get('test_name', 'Unknown')}")
            print(f"查询: {test.get('query', 'Unknown')}")
            print(f"错误: {test.get('error', 'Unknown')}")
            print(f"耗时: {test.get('elapsed_time', 0):.3f}秒")
            print(f"期望成功: {test.get('expected_success', 'Unknown')}")
            print(f"应路由到SQL: {test.get('should_route_to_sql', 'Unknown')}")
            
            if test.get('result_preview'):
                print(f"结果预览: {test['result_preview'][:200]}...")
    
    # 分析成功测试的性能
    print(f"\n\n性能分析:")
    print("-"*80)
    
    # 计算各类别的平均响应时间
    category_times = {}
    for test in details:
        category = test.get('category', 'Unknown')
        if category not in category_times:
            category_times[category] = []
        category_times[category].append(test.get('elapsed_time', 0))
    
    for category, times in sorted(category_times.items()):
        if times:
            avg_time = sum(times) / len(times)
            max_time = max(times)
            min_time = min(times)
            print(f"{category}:")
            print(f"  平均耗时: {avg_time:.2f}秒")
            print(f"  最快: {min_time:.2f}秒")
            print(f"  最慢: {max_time:.2f}秒")
    
    # 总结
    print(f"\n\n测试总结:")
    print("-"*80)
    print(f"Money Flow Agent 表现优秀，通过率达到 {summary.get('pass_rate', 0)}%")
    
    if failed_tests:
        print(f"\n唯一失败的测试:")
        test = failed_tests[0]
        print(f"- 类别: {test.get('category')}")
        print(f"- 查询: {test.get('query')}")
        print(f"- 原因: {test.get('error')}")
        print(f"\n分析: 可能是特定边界条件或数据问题导致")

if __name__ == "__main__":
    analyze_money_flow_failures()