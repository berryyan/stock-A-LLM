#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
验证 Money Flow Agent 修复效果
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.money_flow_agent_modular import MoneyFlowAgentModular

def test_fixed_issues():
    """测试修复的问题"""
    agent = MoneyFlowAgentModular()
    
    # 之前失败的测试用例
    test_cases = [
        ("评估平安银行的主力资金", "深度分析"),
        ("评估平安银行的游资行为", "术语转换 + 深度分析"),
        ("研究宁德时代的资金趋势", "深度分析"),
        ("如何看待茅台的资金流出", "简称提示"),
        ("分析茅台的大资金流向", "简称提示"),
        # 新增一个应该成功的案例（来自测试报告中成功的）
        ("评估中国平安的主力资金", "深度分析")
    ]
    
    results = []
    
    for query, expected_behavior in test_cases:
        print(f"\n{'='*60}")
        print(f"测试查询: {query}")
        print(f"期望行为: {expected_behavior}")
        print('-'*60)
        
        result = agent.analyze(query)
        
        success = result.get('success', False)
        error = result.get('error', None)
        
        print(f"执行结果:")
        print(f"  成功: {success}")
        print(f"  错误: {error}")
        
        if success:
            # 预览结果的前200个字符
            result_text = result.get('result', '')
            preview = result_text[:200] + '...' if len(result_text) > 200 else result_text
            print(f"  预览: {preview}")
        
        results.append({
            'query': query,
            'expected': expected_behavior,
            'success': success,
            'error': error
        })
    
    # 汇总结果
    print(f"\n{'='*60}")
    print("测试结果汇总:")
    print('-'*60)
    
    success_count = sum(1 for r in results if r['success'])
    total_count = len(results)
    
    for r in results:
        status = "✅ 成功" if r['success'] else "❌ 失败"
        print(f"{status} | {r['query']}")
        if not r['success']:
            print(f"     错误: {r['error']}")
    
    print(f"\n成功率: {success_count}/{total_count} ({success_count/total_count*100:.1f}%)")


if __name__ == "__main__":
    test_fixed_issues()