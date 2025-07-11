#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试Financial Agent边界问题修复
验证在股票名称后加"的"是否能解决问题
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.financial_agent_modular import FinancialAgentModular
import time

def test_boundary_cases():
    """测试边界情况"""
    print("=" * 80)
    print("Financial Agent 边界问题测试")
    print("=" * 80)
    
    agent = FinancialAgentModular()
    
    # 原始失败的查询和修改后的查询
    test_cases = [
        # 多期对比
        {
            "original": "万科A季度财务对比分析",
            "fixed": "万科A的季度财务对比分析",
            "category": "多期财务对比"
        },
        
        # 盈利能力
        {
            "original": "贵州茅台净资产收益率分析",
            "fixed": "贵州茅台的净资产收益率分析", 
            "category": "盈利能力分析"
        },
        
        # 运营能力
        {
            "original": "贵州茅台运营能力评价",
            "fixed": "贵州茅台的运营能力评价",
            "category": "运营能力分析"
        }
    ]
    
    results = []
    
    for test_case in test_cases:
        print(f"\n{'='*60}")
        print(f"测试类别: {test_case['category']}")
        print('-'*60)
        
        # 测试原始查询
        print(f"\n1. 原始查询: {test_case['original']}")
        start_time = time.time()
        result_original = agent.analyze(test_case['original'])
        elapsed_original = time.time() - start_time
        
        success_original = result_original.get('success', False)
        print(f"   结果: {'成功' if success_original else '失败'}")
        if not success_original:
            print(f"   错误: {result_original.get('error', '未知错误')}")
        print(f"   耗时: {elapsed_original:.2f}秒")
        
        # 测试修改后的查询
        print(f"\n2. 修改后查询: {test_case['fixed']}")
        start_time = time.time()
        result_fixed = agent.analyze(test_case['fixed'])
        elapsed_fixed = time.time() - start_time
        
        success_fixed = result_fixed.get('success', False)
        print(f"   结果: {'成功' if success_fixed else '失败'}")
        if not success_fixed:
            print(f"   错误: {result_fixed.get('error', '未知错误')}")
        else:
            # 打印部分结果预览
            if result_fixed.get('result'):
                preview = str(result_fixed['result'])[:150]
                print(f"   预览: {preview}...")
        print(f"   耗时: {elapsed_fixed:.2f}秒")
        
        # 分析结果
        if not success_original and success_fixed:
            print(f"\n✅ 修复成功！加'的'解决了问题")
        elif success_original and success_fixed:
            print(f"\n⚠️ 两个查询都成功（原查询可能已被其他方式修复）")
        elif not success_original and not success_fixed:
            print(f"\n❌ 修复失败！加'的'没有解决问题")
        else:
            print(f"\n❓ 异常情况：原查询成功但修改后失败")
        
        results.append({
            "category": test_case['category'],
            "original_query": test_case['original'],
            "fixed_query": test_case['fixed'],
            "original_success": success_original,
            "fixed_success": success_fixed,
            "fixed_worked": not success_original and success_fixed
        })
    
    # 总结
    print(f"\n{'='*80}")
    print("测试总结")
    print("="*80)
    
    fixed_count = sum(1 for r in results if r['fixed_worked'])
    print(f"成功修复: {fixed_count}/{len(results)}")
    
    for result in results:
        status = "✅ 修复成功" if result['fixed_worked'] else "❌ 修复失败"
        print(f"\n{result['category']}: {status}")
        print(f"  原始: {result['original_query']} -> {'成功' if result['original_success'] else '失败'}")
        print(f"  修改: {result['fixed_query']} -> {'成功' if result['fixed_success'] else '失败'}")
    
    return fixed_count == len(results)

if __name__ == "__main__":
    success = test_boundary_cases()
    exit(0 if success else 1)