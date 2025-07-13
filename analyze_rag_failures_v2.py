#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
分析RAG Agent测试报告（适配新格式）
"""

import json
import os

def analyze_rag_report():
    """分析RAG Agent测试报告"""
    report_file = 'rag_agent_comprehensive_results.json'
    
    if not os.path.exists(report_file):
        print("RAG Agent报告文件不存在")
        return
    
    with open(report_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    print("="*80)
    print("RAG Agent 测试报告详细分析")
    print("="*80)
    
    # 基本统计
    print(f"\n基本信息:")
    print(f"Agent: {data.get('agent', 'Unknown')}")
    print(f"总测试: {data.get('total', 0)}")
    print(f"通过: {data.get('passed', 0)}")
    print(f"失败: {data.get('failed', 0)}")
    print(f"通过率: {data['passed']/data['total']*100:.1f}%")
    
    # 功能统计
    print(f"\n功能分布:")
    for func, count in data.get('functions', {}).items():
        print(f"  {func}: {count}个测试")
    
    # 分析失败的测试
    print("\n失败的测试用例:")
    print("-"*80)
    
    details = data.get('details', [])
    failed_tests = []
    
    for test in details:
        # 判断是否失败
        status = test.get('status', '')
        if '失败' in status or '❌' in status:
            failed_tests.append(test)
        elif test.get('result', {}).get('success', True) == False:
            failed_tests.append(test)
    
    # 显示失败测试详情
    for i, test in enumerate(failed_tests[:10], 1):  # 只显示前10个
        print(f"\n失败 #{i}:")
        print(f"测试名: {test.get('name', 'Unknown')}")
        print(f"功能: {test.get('function', 'Unknown')}")
        print(f"类别: {test.get('category', 'Unknown')}")
        print(f"状态: {test.get('status', 'Unknown')}")
        print(f"耗时: {test.get('elapsed', 'Unknown')}")
        
        result = test.get('result', {})
        if isinstance(result, dict):
            if result.get('error'):
                print(f"错误: {result['error']}")
            if result.get('suggestion'):
                print(f"建议: {result['suggestion']}")
    
    # 统计失败模式
    print(f"\n\n失败模式统计:")
    print("-"*80)
    
    error_patterns = {}
    for test in failed_tests:
        result = test.get('result', {})
        if isinstance(result, dict) and result.get('error'):
            error = result['error']
            if '没有找到符合条件的数据' in error:
                pattern = '无数据'
            elif '查询过程中出现未知错误' in error:
                pattern = '未知错误'
            elif 'Connection' in error:
                pattern = '连接错误'
            else:
                pattern = '其他错误'
        else:
            pattern = '结果验证失败'
        
        if pattern not in error_patterns:
            error_patterns[pattern] = 0
        error_patterns[pattern] += 1
    
    for pattern, count in sorted(error_patterns.items(), key=lambda x: x[1], reverse=True):
        print(f"{pattern}: {count}次")
    
    # 功能成功率分析
    print(f"\n\n各功能成功率分析:")
    print("-"*80)
    
    function_stats = {}
    for test in details:
        func = test.get('function', 'Unknown')
        if func not in function_stats:
            function_stats[func] = {'total': 0, 'passed': 0}
        
        function_stats[func]['total'] += 1
        
        status = test.get('status', '')
        result = test.get('result', {})
        
        # 判断是否成功
        if '通过' in status or '✅' in status:
            function_stats[func]['passed'] += 1
        elif isinstance(result, dict) and result.get('success', False):
            function_stats[func]['passed'] += 1
    
    for func, stats in sorted(function_stats.items()):
        total = stats['total']
        passed = stats['passed']
        rate = (passed / total * 100) if total > 0 else 0
        status = "✅" if rate >= 95 else "⚠️" if rate >= 80 else "❌"
        print(f"{func}: {passed}/{total} ({rate:.1f}%) {status}")
    
    # 总结
    print(f"\n\n问题总结:")
    print("-"*80)
    print("1. RAG Agent总体通过率76.4%，低于预期")
    print("2. 主要失败原因：")
    print("   - 部分查询返回'没有找到符合条件的数据'")
    print("   - 可能是测试数据与实际Milvus数据不匹配")
    print("   - 或者是查询过滤条件过于严格")
    print("3. 建议：")
    print("   - 检查Milvus中的实际数据")
    print("   - 优化查询过滤逻辑")
    print("   - 增加容错机制")

if __name__ == "__main__":
    analyze_rag_report()