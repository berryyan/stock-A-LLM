#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
分析RAG Agent测试失败原因
"""

import json
from collections import defaultdict

def analyze_failures():
    """分析失败的测试用例"""
    with open('rag_agent_comprehensive_results.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # 统计失败原因
    failure_reasons = defaultdict(int)
    failed_cases = []
    
    for detail in data['details']:
        if detail['status'].startswith('❌'):
            failed_cases.append(detail)
            
            # 提取错误信息
            if 'result' in detail and 'error' in detail['result']:
                error = detail['result']['error']
                failure_reasons[error] += 1
            elif 'error' in detail:
                error = detail['error']
                failure_reasons[error] += 1
    
    print("=" * 80)
    print("RAG Agent 失败分析")
    print("=" * 80)
    print(f"\n总失败数: {len(failed_cases)}")
    
    print("\n失败原因统计:")
    print("-" * 80)
    for reason, count in sorted(failure_reasons.items(), key=lambda x: x[1], reverse=True):
        print(f"{reason}: {count}次")
    
    print("\n详细失败用例:")
    print("-" * 80)
    
    # 按功能分组显示失败用例
    failures_by_function = defaultdict(list)
    for case in failed_cases:
        failures_by_function[case['function']].append(case)
    
    for function, cases in failures_by_function.items():
        print(f"\n【{function}】({len(cases)}个失败)")
        for case in cases:
            print(f"  - {case['name']}")
            if 'result' in case and 'error' in case['result']:
                print(f"    错误: {case['result']['error']}")
            elif 'error' in case:
                print(f"    错误: {case['error']}")
    
    # 分析失败模式
    print("\n失败模式分析:")
    print("-" * 80)
    
    # 统计正向/负向测试失败
    positive_failures = sum(1 for case in failed_cases if case['category'] == 'positive')
    negative_failures = sum(1 for case in failed_cases if case['category'] == 'negative')
    
    print(f"正向测试失败: {positive_failures}个")
    print(f"负向测试失败: {negative_failures}个")
    
    # 负向测试失败的特殊分析
    if negative_failures > 0:
        print("\n负向测试失败分析（这些应该失败但却成功了）:")
        for case in failed_cases:
            if case['category'] == 'negative':
                print(f"  - {case['name']}: 期望失败但实际成功")
    
    # 建议
    print("\n改进建议:")
    print("-" * 80)
    if "没有找到符合条件的数据" in failure_reasons:
        print("1. 多数失败是因为'没有找到符合条件的数据'，可能是:")
        print("   - Milvus中缺少测试数据")
        print("   - 查询条件过于严格")
        print("   - 日期格式或股票代码格式问题")
    
    if negative_failures > 10:
        print("2. 负向测试失败较多，说明错误处理不够严格:")
        print("   - 需要加强输入验证")
        print("   - 错误的查询应该返回明确的错误信息")
    
    print("\n总结:")
    print(f"- 通过率: {data['passed']}/{data['total']} ({data['passed']/data['total']*100:.1f}%)")
    print(f"- 主要问题: 数据查询和负向测试处理")
    print(f"- 建议优先级: {'高' if data['passed']/data['total'] < 0.8 else '中'}")


if __name__ == "__main__":
    analyze_failures()