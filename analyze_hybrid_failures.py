#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
分析Hybrid Agent失败的测试用例
"""

import json
import os

def analyze_hybrid_failures():
    """分析Hybrid Agent的失败测试"""
    report_file = 'hybrid_agent_comprehensive_results.json'
    
    if not os.path.exists(report_file):
        print("Hybrid Agent报告文件不存在")
        return
    
    with open(report_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    print("="*80)
    print("Hybrid Agent 失败测试分析")
    print("="*80)
    
    # 基本统计
    print(f"\n基本统计:")
    print(f"总测试: {data.get('total', 0)}")
    print(f"通过: {data.get('passed', 0)}")
    print(f"失败: {data.get('failed', 0)}")
    print(f"通过率: {data.get('pass_rate', 0):.1f}%")
    
    # 按功能分类
    print(f"\n功能失败统计:")
    functions = data.get('functions', {})
    for func_name, stats in functions.items():
        if stats.get('failed', 0) > 0:
            print(f"{func_name}: {stats['failed']}个失败 (共{stats['total']}个)")
    
    # 分析失败的测试
    print(f"\n\n失败的测试用例详情:")
    print("-"*80)
    
    details = data.get('details', [])
    failed_tests = []
    
    # 收集失败的测试
    for test in details:
        status = test.get('status', '')
        if '失败' in status or '❌' in status:
            failed_tests.append(test)
    
    # 按功能分组显示失败测试
    failed_by_function = {}
    for test in failed_tests:
        func = test.get('function', 'Unknown')
        if func not in failed_by_function:
            failed_by_function[func] = []
        failed_by_function[func].append(test)
    
    # 重点分析投资价值分析的失败
    if '投资价值分析' in failed_by_function:
        print(f"\n### 投资价值分析失败详情 ###")
        for test in failed_by_function['投资价值分析']:
            print(f"\n测试: {test.get('name', 'Unknown')}")
            print(f"查询: {test.get('query', 'Unknown')}")
            print(f"类型: {test.get('category', 'Unknown')}")
            
            result = test.get('result', {})
            if isinstance(result, dict):
                print(f"成功: {result.get('success', False)}")
                if result.get('error'):
                    print(f"错误: {result['error']}")
                if result.get('query_type'):
                    print(f"路由类型: {result['query_type']}")
                if result.get('answer'):
                    print(f"答案预览: {result['answer'][:200]}...")
    
    # 分析综合对比分析的失败
    if '综合对比分析' in failed_by_function:
        print(f"\n\n### 综合对比分析失败详情 ###")
        for test in failed_by_function['综合对比分析'][:3]:  # 只显示前3个
            print(f"\n测试: {test.get('name', 'Unknown')}")
            print(f"查询: {test.get('query', 'Unknown')}")
            result = test.get('result', {})
            if isinstance(result, dict) and result.get('error'):
                print(f"错误: {result['error']}")
    
    # 分析错误传递的失败
    if '错误传递' in failed_by_function:
        print(f"\n\n### 错误传递失败详情 ###")
        for test in failed_by_function['错误传递'][:3]:  # 只显示前3个
            print(f"\n测试: {test.get('name', 'Unknown')}")
            print(f"查询: {test.get('query', 'Unknown')}")
            result = test.get('result', {})
            if isinstance(result, dict):
                print(f"成功状态: {result.get('success', False)}")
                print(f"错误信息: {result.get('error', 'None')}")
    
    # 统计路由类型
    print(f"\n\n### 路由类型统计 ###")
    route_counts = {}
    for test in failed_tests:
        result = test.get('result', {})
        if isinstance(result, dict):
            route_type = result.get('query_type', 'Unknown')
            route_counts[route_type] = route_counts.get(route_type, 0) + 1
    
    for route_type, count in sorted(route_counts.items(), key=lambda x: x[1], reverse=True):
        print(f"{route_type}: {count}次")
    
    # 总结
    print(f"\n\n### 问题总结 ###")
    print("1. 投资价值分析：6个失败，可能是路由到COMPLEX后处理失败")
    print("2. 综合对比分析：4个失败，可能是复杂查询处理逻辑问题")
    print("3. 错误传递：4个失败，可能是错误信息没有正确传递")
    print("4. 并行查询：3个失败，可能是并行处理逻辑问题")

if __name__ == "__main__":
    analyze_hybrid_failures()