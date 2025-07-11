#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Financial Agent 快速验证脚本
验证方法名修复和参数验证是否正常工作
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.financial_agent_modular import FinancialAgentModular
import time

def quick_verify():
    """快速验证核心功能"""
    print("=" * 80)
    print("Financial Agent 模块化版本 - 快速验证")
    print("=" * 80)
    
    agent = FinancialAgentModular()
    
    # 测试用例：每个分析类型选2个用例
    test_cases = [
        # 财务健康度（应该成功）
        ("分析贵州茅台的财务健康度", True, "财务健康度-完整名称"),
        ("茅台的财务健康度", False, "财务健康度-简称拒绝"),
        
        # 杜邦分析（验证方法名修复）
        ("贵州茅台的杜邦分析", True, "杜邦分析-完整名称"),
        ("600519.sh的杜邦分析", False, "杜邦分析-小写后缀"),
        
        # 现金流分析（验证方法名修复）
        ("分析万科A的现金流质量", True, "现金流-完整名称"),
        ("万科的现金流", False, "现金流-简称拒绝"),
        
        # 多期对比
        ("贵州茅台最近3期财务对比", True, "多期对比-完整名称"),
        ("", False, "多期对比-空查询"),
        
        # 盈利能力
        ("分析比亚迪的盈利能力", True, "盈利能力-完整名称"),
        ("比亚迪的盈利", True, "盈利能力-比亚迪特殊"),
        
        # 偿债能力
        ("分析万科A的偿债能力", True, "偿债能力-完整名称"),
        ("建行的偿债", False, "偿债能力-简称拒绝"),
        
        # 运营能力
        ("分析海尔智家的运营效率", True, "运营能力-完整名称"),
        ("格力的运营", False, "运营能力-简称拒绝"),
        
        # 成长能力
        ("分析宁德时代的成长性", True, "成长能力-完整名称"),
        ("宁德的成长性", False, "成长能力-简称拒绝"),
    ]
    
    passed = 0
    failed = 0
    
    for query, expected_success, test_name in test_cases:
        print(f"\n测试: {test_name}")
        print(f"查询: {query}")
        print(f"期望: {'成功' if expected_success else '失败'}")
        
        start_time = time.time()
        try:
            result = agent.analyze(query)
            elapsed_time = time.time() - start_time
            
            actual_success = result.get('success', False)
            test_passed = actual_success == expected_success
            
            print(f"实际: {'成功' if actual_success else '失败'}")
            print(f"耗时: {elapsed_time:.2f}秒")
            
            if not actual_success and result.get('error'):
                print(f"错误: {result['error']}")
            
            if test_passed:
                print("✅ 测试通过")
                passed += 1
            else:
                print("❌ 测试失败")
                failed += 1
                if actual_success and expected_success:
                    # 如果都是成功但测试失败，可能是结果问题
                    print(f"结果预览: {str(result.get('result', ''))[:100]}...")
                    
        except Exception as e:
            print(f"❌ 异常: {str(e)}")
            failed += 1
    
    print(f"\n{'='*80}")
    print(f"总计: {len(test_cases)} 个测试")
    print(f"通过: {passed} ({passed/len(test_cases)*100:.1f}%)")
    print(f"失败: {failed} ({failed/len(test_cases)*100:.1f}%)")
    
    # 返回是否全部通过
    return failed == 0

if __name__ == "__main__":
    success = quick_verify()
    exit(0 if success else 1)