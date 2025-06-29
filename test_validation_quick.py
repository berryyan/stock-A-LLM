#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快速测试统一验证系统 - 只测试验证逻辑，不调用LLM
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.unified_stock_validator import UnifiedStockValidator
from agents.financial_agent import FinancialAnalysisAgent
from agents.sql_agent import SQLAgent  
from agents.money_flow_agent import MoneyFlowAgent


def test_validator_only():
    """只测试验证逻辑"""
    print("=" * 80)
    print("快速测试统一验证逻辑")
    print("=" * 80)
    
    # 创建统一验证器
    validator = UnifiedStockValidator()
    
    # 测试用例
    test_cases = [
        # 正确的用例
        ("贵州茅台财务健康度", "✅应该成功"),
        ("600519财务健康度", "✅应该成功"),
        ("600519.SH财务健康度", "✅应该成功"),
        ("中国平安财务健康度", "✅应该成功"),
        ("831726.BJ财务健康度", "✅应该成功"),
        
        # 错误的用例
        ("茅台财务健康度", "❌应该失败-简称"),
        ("平安财务健康度", "❌应该失败-简称"),
        ("贵州茅财务健康度", "❌应该失败-不完整"),
        ("60051财务健康度", "❌应该失败-位数不对"),
        ("600519.XX财务健康度", "❌应该失败-错误后缀"),
        ("831726.BJJ财务健康度", "❌应该失败-BJ错拼"),
        ("123456.SH财务健康度", "❌应该失败-代码不存在"),
        ("", "❌应该失败-空输入"),
    ]
    
    print("\n测试统一验证器:")
    print("-" * 80)
    
    correct_count = 0
    
    for test_case, expectation in test_cases:
        success, ts_code, error_response = validator.validate_and_extract(test_case)
        
        # 判断是否符合预期
        if "✅应该成功" in expectation:
            expected_success = True
        else:
            expected_success = False
        
        is_correct = (success == expected_success)
        status = "✅ 正确" if is_correct else "❌ 错误"
        
        if success:
            print(f"{status} | {test_case:<30} => {ts_code}")
        else:
            print(f"{status} | {test_case:<30} => {error_response.get('error', 'Unknown error')}")
        
        if is_correct:
            correct_count += 1
    
    print(f"\n总结: {correct_count}/{len(test_cases)} 测试通过 ({correct_count/len(test_cases)*100:.1f}%)")


def test_extraction_logic():
    """测试Financial Agent的提取逻辑"""
    print("\n" + "=" * 80)
    print("测试Financial Agent的_parse_query_intent逻辑")
    print("=" * 80)
    
    try:
        agent = FinancialAnalysisAgent()
        
        # 测试用例
        test_queries = [
            "贵州茅台财务健康度",
            "600519财务健康度",
            "600519.SH财务健康度",
            "茅台财务健康度",
            "60051财务健康度",
            "600519.XX财务健康度",
            "831726.BJ现金流分析",  # 测试BJ股票
        ]
        
        for query in test_queries:
            intent, ts_code = agent._parse_query_intent(query)
            print(f"查询: {query:<30} => 意图: {intent:<20} 代码: {ts_code}")
            
    except Exception as e:
        print(f"测试失败: {e}")


def compare_validation_logic():
    """比较不同Agent的验证逻辑（不实际调用查询）"""
    print("\n" + "=" * 80)
    print("比较Agent验证逻辑的一致性")
    print("=" * 80)
    
    # 初始化验证器
    validator = UnifiedStockValidator()
    
    # 测试用例
    test_cases = [
        "贵州茅台最新股价",  # SQL查询
        "贵州茅台资金流向",  # 资金流向查询
        "茅台最新股价",     # 应该失败
        "茅台资金流向",     # 应该失败
    ]
    
    print("\n统一验证器测试结果:")
    print("-" * 60)
    
    for test_case in test_cases:
        success, ts_code, error_response = validator.validate_and_extract(test_case)
        if success:
            print(f"✅ {test_case:<20} => {ts_code}")
        else:
            print(f"❌ {test_case:<20} => {error_response['error']}")


if __name__ == "__main__":
    # 测试验证器
    test_validator_only()
    
    # 测试提取逻辑
    test_extraction_logic()
    
    # 比较验证逻辑
    compare_validation_logic()