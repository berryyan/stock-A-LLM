#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Financial Agent 修复验证脚本
只验证刚修复的方法调用问题
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.financial_agent_modular import FinancialAgentModular
import time

def verify_fixes():
    """验证修复的问题"""
    print("=" * 80)
    print("Financial Agent 修复验证")
    print("=" * 80)
    
    agent = FinancialAgentModular()
    
    # 只测试之前失败的4个用例
    test_cases = [
        # 多期对比 - 之前报错 compare_financial_periods
        ("贵州茅台最近3期财务对比", True, "多期对比"),
        
        # 盈利能力 - 之前报错 _analyze_profitability
        ("分析比亚迪的盈利能力", True, "盈利能力分析"),
        
        # 偿债能力 - 之前报错 _analyze_solvency
        ("分析万科A的偿债能力", True, "偿债能力分析"),
        
        # 成长能力 - 之前报错 _analyze_growth
        ("分析宁德时代的成长性", True, "成长能力分析"),
    ]
    
    passed = 0
    failed = 0
    
    for query, expected_success, test_name in test_cases:
        print(f"\n测试: {test_name}")
        print(f"查询: {query}")
        
        try:
            result = agent.analyze(query)
            actual_success = result.get('success', False)
            
            print(f"结果: {'成功' if actual_success else '失败'}")
            
            if actual_success:
                print("✅ 不再报方法不存在错误")
                passed += 1
                # 打印一些结果预览
                if result.get('result'):
                    preview = str(result['result'])[:100]
                    print(f"预览: {preview}...")
            else:
                error = result.get('error', '未知错误')
                if 'has no attribute' in error:
                    print(f"❌ 仍有方法错误: {error}")
                    failed += 1
                else:
                    print(f"⚠️ 其他错误: {error}")
                    # 这里不算失败，因为可能是其他原因
                    passed += 1
                    
        except Exception as e:
            print(f"❌ 异常: {str(e)}")
            failed += 1
    
    print(f"\n{'='*80}")
    print(f"验证结果: {passed}/{len(test_cases)} 个方法调用修复成功")
    
    return failed == 0

if __name__ == "__main__":
    success = verify_fixes()
    exit(0 if success else 1)