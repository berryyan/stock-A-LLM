#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""快速检查Financial Agent的验证行为"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.financial_agent_modular import FinancialAgentModular

def quick_test():
    """快速测试几个关键用例"""
    agent = FinancialAgentModular()
    
    test_cases = [
        # 应该成功的
        ("分析贵州茅台的财务健康度", True),
        ("分析600519.SH的财务健康度", True),
        ("分析平安银行的财务健康度", True),
        
        # 应该失败的（简称）
        ("茅台的财务健康度", False),
        ("平安的财务健康度", False),
        ("万科的财务健康度", False),
        
        # 应该失败的（其他错误）
        ("", False),
        ("12345的财务健康度", False),
        ("600519.sh的财务健康度", False),  # 小写
    ]
    
    print("Financial Agent 快速验证测试")
    print("="*60)
    
    passed = 0
    failed = 0
    
    for query, should_succeed in test_cases:
        print(f"\n测试: {query}")
        print(f"期望: {'成功' if should_succeed else '失败'}")
        
        result = agent.analyze(query)
        actual_success = result.get('success', False)
        
        print(f"实际: {'成功' if actual_success else '失败'}")
        
        if actual_success == should_succeed:
            print("✅ 测试通过")
            passed += 1
        else:
            print("❌ 测试失败")
            if not actual_success:
                print(f"错误: {result.get('error', '未知错误')}")
            failed += 1
    
    print(f"\n{'='*60}")
    print(f"总计: {len(test_cases)} 个测试")
    print(f"通过: {passed} ({passed/len(test_cases)*100:.1f}%)")
    print(f"失败: {failed} ({failed/len(test_cases)*100:.1f}%)")

if __name__ == "__main__":
    quick_test()