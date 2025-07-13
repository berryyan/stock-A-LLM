#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
分析SQL Agent测试失败案例
"""

import json
import os

def analyze_sql_agent_failures():
    """分析SQL Agent的失败测试"""
    report_file = 'test_report_20250713_003817.json'
    
    if not os.path.exists(report_file):
        print("SQL Agent报告文件不存在")
        return
    
    with open(report_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    print("="*80)
    print("SQL Agent 失败测试分析")
    print("="*80)
    print(f"\n总测试数: {data['total']}")
    print(f"通过: {data['passed']}")
    print(f"失败: {data['failed']}")
    print(f"通过率: {data['passed']/data['total']*100:.1f}%")
    
    print("\n失败的测试用例:")
    print("-"*80)
    
    # 分析错误
    errors = data.get('errors', [])
    for i, error in enumerate(errors, 1):
        print(f"\n失败 #{i}:")
        print(f"类别: {error.get('category', 'Unknown')}")
        print(f"测试: {error.get('test_name', 'Unknown')}")
        print(f"查询: {error.get('query', 'Unknown')}")
        print(f"错误: {error.get('error', 'Unknown')}")
        print(f"耗时: {error.get('elapsed_time', 0):.3f}秒")
    
    # 统计失败模式
    print("\n失败模式分析:")
    print("-"*80)
    error_patterns = {}
    for error in errors:
        error_msg = error.get('error') or ''
        if error_msg and '无法识别输入内容' in error_msg:
            pattern = '股票识别失败'
        elif '连接' in error_msg:
            pattern = '连接错误'
        elif '参数' in error_msg:
            pattern = '参数错误'
        else:
            pattern = '其他错误'
        
        if pattern not in error_patterns:
            error_patterns[pattern] = []
        error_patterns[pattern].append(error.get('query', ''))
    
    for pattern, queries in error_patterns.items():
        print(f"\n{pattern} ({len(queries)}次):")
        for query in queries:
            print(f"  - {query}")
    
    # 分析成功的测试分布
    print("\n\n成功测试分布:")
    print("-"*80)
    
    details = data.get('details', [])
    category_stats = {}
    
    for test in details:
        category = test.get('category', 'Unknown')
        if category not in category_stats:
            category_stats[category] = {'total': 0, 'passed': 0, 'failed': 0}
        
        category_stats[category]['total'] += 1
        if test.get('passed', False):
            category_stats[category]['passed'] += 1
        else:
            category_stats[category]['failed'] += 1
    
    for category, stats in sorted(category_stats.items()):
        total = stats['total']
        passed = stats['passed']
        rate = (passed / total * 100) if total > 0 else 0
        status = "✅" if rate == 100 else "⚠️" if rate >= 80 else "❌"
        print(f"{category}: {passed}/{total} ({rate:.1f}%) {status}")

if __name__ == "__main__":
    analyze_sql_agent_failures()