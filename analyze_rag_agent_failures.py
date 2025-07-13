#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
分析RAG Agent测试失败案例
"""

import json
import os

def analyze_rag_agent_failures():
    """分析RAG Agent的失败测试"""
    report_file = 'rag_agent_comprehensive_results.json'
    
    if not os.path.exists(report_file):
        print("RAG Agent报告文件不存在")
        return
    
    with open(report_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    print("="*80)
    print("RAG Agent 测试报告分析")
    print("="*80)
    
    # 查看报告结构
    print(f"\n报告结构: {list(data.keys())}")
    
    # 计算统计信息 - 处理不同的报告格式
    if 'test_results' in data:
        tests = data.get('test_results', [])
        total = len(tests)
        passed = sum(1 for t in tests if t.get('status') == 'passed')
        failed = total - passed
    elif 'total' in data:
        # 使用根级别的统计信息
        total = data.get('total', 0)
        passed = data.get('passed', 0)
        failed = data.get('failed', 0)
        tests = data.get('details', [])
    else:
        print("无法识别的报告格式")
        return
    
    pass_rate = (passed / total * 100) if total > 0 else 0
    
    print(f"\n总测试数: {total}")
    print(f"通过: {passed}")
    print(f"失败: {failed}")
    print(f"通过率: {pass_rate:.1f}%")
    
    # 分析失败的测试
    print("\n失败的测试用例:")
    print("-"*80)
    
    # 适配不同的测试状态字段
    failed_tests = []
    for t in tests:
        if 'status' in t and t['status'] != 'passed':
            failed_tests.append(t)
        elif 'passed' in t and not t['passed']:
            failed_tests.append(t)
    
    for i, test in enumerate(failed_tests, 1):
        print(f"\n失败 #{i}:")
        print(f"类别: {test.get('test_category', 'Unknown')}")
        print(f"查询: {test.get('query', 'Unknown')}")
        print(f"错误: {test.get('error', 'Unknown')}")
        print(f"耗时: {test.get('elapsed_time', 0):.3f}秒")
        if test.get('result'):
            print(f"结果预览: {str(test['result'])[:100]}...")
    
    # 统计失败模式
    print("\n\n失败模式分析:")
    print("-"*80)
    
    error_patterns = {}
    for test in failed_tests:
        error_msg = test.get('error') or ''
        
        if 'Connection' in error_msg or 'connection' in error_msg:
            pattern = 'Milvus连接错误'
        elif 'collection' in error_msg:
            pattern = 'Collection错误'
        elif '参数' in error_msg:
            pattern = '参数错误'
        elif 'timeout' in error_msg or '超时' in error_msg:
            pattern = '超时错误'
        elif error_msg == '':
            pattern = '无错误信息（可能是结果验证失败）'
        else:
            pattern = '其他错误'
        
        if pattern not in error_patterns:
            error_patterns[pattern] = []
        error_patterns[pattern].append({
            'query': test.get('query', ''),
            'error': error_msg
        })
    
    for pattern, cases in error_patterns.items():
        print(f"\n{pattern} ({len(cases)}次):")
        for case in cases[:3]:  # 只显示前3个例子
            print(f"  查询: {case['query']}")
            if case['error']:
                print(f"  错误: {case['error'][:100]}...")
    
    # 分析成功率分布
    print("\n\n各类别成功率:")
    print("-"*80)
    
    category_stats = {}
    for test in tests:
        category = test.get('test_category', 'Unknown')
        if category not in category_stats:
            category_stats[category] = {'total': 0, 'passed': 0}
        
        category_stats[category]['total'] += 1
        if test.get('status') == 'passed':
            category_stats[category]['passed'] += 1
    
    for category, stats in sorted(category_stats.items()):
        total = stats['total']
        passed = stats['passed']
        rate = (passed / total * 100) if total > 0 else 0
        status = "✅" if rate >= 95 else "⚠️" if rate >= 80 else "❌"
        print(f"{category}: {passed}/{total} ({rate:.1f}%) {status}")
    
    # 检查测试环境信息
    print("\n\n测试环境信息:")
    print("-"*80)
    if 'test_start_time' in data:
        print(f"开始时间: {data['test_start_time']}")
    if 'test_end_time' in data:
        print(f"结束时间: {data['test_end_time']}")
    if 'total_elapsed_time' in data:
        print(f"总耗时: {data['total_elapsed_time']:.1f}秒")

if __name__ == "__main__":
    analyze_rag_agent_failures()