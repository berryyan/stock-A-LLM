#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
分析Hybrid Agent v2失败的测试用例
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
    print("Hybrid Agent 失败测试详细分析 V2")
    print("="*80)
    
    # 基本统计
    print(f"\n基本统计:")
    print(f"总测试: {data.get('total', 0)}")
    print(f"通过: {data.get('passed', 0)}")
    print(f"失败: {data.get('failed', 0)}")
    print(f"通过率: {data['passed']/data['total']*100:.1f}%")
    
    # 改进情况
    print(f"\n改进情况:")
    print(f"- 投资价值分析：从 3/9 提升到 6/9 (+3)")
    print(f"- 综合对比分析：从 4/8 提升到 5/8 (+1)")
    print(f"- 错误传递：从 4/8 提升到 5/8 (+1)")
    
    # 分析仍然失败的测试
    print(f"\n\n仍然失败的测试详情:")
    print("-"*80)
    
    details = data.get('details', [])
    failed_tests = []
    
    # 收集失败的测试
    for test in details:
        status = test.get('status', '')
        if '失败' in status or '❌' in status:
            failed_tests.append(test)
    
    # 按功能分组
    failed_by_function = {}
    for test in failed_tests:
        func = test.get('function', 'Unknown')
        if func not in failed_by_function:
            failed_by_function[func] = []
        failed_by_function[func].append(test)
    
    # 分析每个功能的失败
    for func_name, tests in failed_by_function.items():
        print(f"\n### {func_name} ({len(tests)}个失败) ###")
        for test in tests:
            print(f"\n测试名: {test.get('name', 'Unknown')}")
            print(f"类型: {test.get('category', 'Unknown')}")
            
            # 尝试从details中找到query
            query = "Unknown"
            for detail in details:
                if detail.get('name') == test.get('name'):
                    # 从测试定义中提取查询
                    if '基础分析' in test['name']:
                        query = "分析贵州茅台的投资价值"
                    elif '评估机会' in test['name']:
                        query = "评估宁德时代的投资机会"
                    elif '是否值得' in test['name']:
                        query = "比亚迪值得投资吗"
                    elif '财务风险' in test['name']:
                        query = "评估万科A的财务风险和股价表现"
                    elif '风险状况' in test['name']:
                        query = "分析恒大的风险状况"
                    elif '股价波动' in test['name']:
                        query = "评估宁德时代的股价波动风险"
                    elif '错误类型' in test['name']:
                        query = "贵州茅台的天气风险"
                    elif '两股对比' in test['name']:
                        query = "对比茅台和五粮液的综合实力"
                    elif 'vs格式' in test['name']:
                        query = "平安银行 vs 招商银行全面对比"
                    elif '多维度' in test['name']:
                        query = "从财务、技术、市场等角度对比茅台和五粮液"
                    elif 'RAG错误' in test['name']:
                        query = "查询xyz公司的年报"
                    elif '隐藏错误' in test['name']:
                        query = "贵州茅台的股价"
                    elif '错误格式' in test['name']:
                        query = ""
                    elif '多股票查询' in test['name']:
                        query = "查询贵州茅台、五粮液、泸州老窖的股价"
                    elif '超长查询' in test['name']:
                        query = "贵州茅台" * 100
                    elif '通配符' in test['name']:
                        query = "*茅台*的股价"
                    elif '歧义查询' in test['name']:
                        query = "平安的情况如何"
                    break
            
            print(f"查询: {query}")
            
            result = test.get('result', {})
            if isinstance(result, dict):
                print(f"成功: {result.get('success', False)}")
                if result.get('error'):
                    print(f"错误: {result['error']}")
                if result.get('query_type'):
                    print(f"路由: {result['query_type']}")
                if result.get('answer'):
                    answer = result['answer']
                    if isinstance(answer, str):
                        print(f"答案预览: {answer[:100]}...")
    
    # 分析路由问题
    print(f"\n\n### 路由分析 ###")
    route_stats = {}
    for test in failed_tests:
        result = test.get('result', {})
        if isinstance(result, dict):
            route = result.get('query_type', 'Unknown')
            route_stats[route] = route_stats.get(route, 0) + 1
    
    print("失败测试的路由分布:")
    for route, count in sorted(route_stats.items(), key=lambda x: x[1], reverse=True):
        print(f"  {route}: {count}次")
    
    # 建议
    print(f"\n\n### 改进建议 ###")
    print("1. 投资价值分析：仍有3个失败，可能需要进一步优化Financial Agent的调用")
    print("2. 风险评估分析：4个失败，需要检查风险相关查询的路由")
    print("3. 综合对比分析：3个失败，PARALLEL路由可能需要优化")
    print("4. 错误传递：需要确保错误信息正确格式化和传递")

if __name__ == "__main__":
    analyze_hybrid_failures()