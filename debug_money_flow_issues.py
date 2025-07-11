#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
调试 Money Flow Agent 测试失败问题
重点分析："评估平安银行的主力资金"、"游资→主力"等失败测试
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.money_flow_agent_modular import MoneyFlowAgentModular
from utils.unified_stock_validator import validate_stock_input, UnifiedStockValidator
from utils.parameter_extractor import ParameterExtractor

def debug_stock_validation():
    """调试股票验证问题"""
    print("=== 调试股票验证 ===\n")
    
    # 测试问题查询
    test_queries = [
        "评估平安银行的主力资金",
        "评估平安银行的游资行为",
        "研究宁德时代的资金趋势",
        "分析茅台的大资金流向",
        "如何看待茅台的资金流出"
    ]
    
    validator = UnifiedStockValidator()
    extractor = ParameterExtractor()
    
    for query in test_queries:
        print(f"\n查询: {query}")
        print("-" * 50)
        
        # 1. 先测试参数提取器
        params = extractor.extract_all_params(query)
        print(f"参数提取器结果:")
        print(f"  股票: {params.stocks}")
        print(f"  股票名称: {params.stock_names}")
        print(f"  板块: {params.sector}")
        
        # 2. 测试股票验证器
        success, ts_code, error_response = validate_stock_input(query)
        print(f"\n股票验证器结果:")
        print(f"  成功: {success}")
        print(f"  股票代码: {ts_code}")
        print(f"  错误信息: {error_response.get('error', 'None')}")
        
        # 3. 测试查询类型识别
        agent = MoneyFlowAgentModular()
        query_type = agent._identify_query_type(query)
        print(f"\n查询类型: {query_type}")
        
        # 4. 测试是否是资金流向查询
        is_money_flow = agent.is_money_flow_query(query)
        print(f"是否资金流向查询: {is_money_flow}")


def debug_full_flow():
    """调试完整的处理流程"""
    print("\n\n=== 调试完整处理流程 ===\n")
    
    agent = MoneyFlowAgentModular()
    
    # 测试失败的查询
    test_queries = [
        ("评估平安银行的主力资金", "应该成功，深度分析"),
        ("评估平安银行的游资行为", "应该成功，术语转换"),
        ("研究宁德时代的资金趋势", "应该成功，深度分析"),
        ("分析茅台的大资金流向", "应该失败，提示使用完整名称"),
        ("如何看待茅台的资金流出", "应该失败，提示使用完整名称")
    ]
    
    for query, expected in test_queries:
        print(f"\n查询: {query}")
        print(f"期望: {expected}")
        print("-" * 50)
        
        result = agent.analyze(query)
        
        print(f"结果:")
        print(f"  成功: {result.get('success')}")
        print(f"  错误: {result.get('error', 'None')}")
        if result.get('success'):
            preview = result.get('result', '')[:200]
            print(f"  预览: {preview}...")


def analyze_specific_issue():
    """分析特定问题：为什么"评估平安银行的主力资金"失败"""
    print("\n\n=== 分析特定问题 ===\n")
    
    query = "评估平安银行的主力资金"
    print(f"问题查询: {query}")
    
    # 1. 检查各种名称提取模式
    import re
    
    # 测试不同的模式
    patterns = [
        (r'([一-龥]{2,6})(?=[和与及、，,]|$|\s|的)', "普通中文股票名"),
        (r'([一-龥]{2,6})的', "中文名+的"),
        (r'评估([一-龥]{2,6})的', "评估+中文名+的"),
        (r'([一-龥]{2,6})(?=的主力)', "中文名+的主力"),
    ]
    
    for pattern, desc in patterns:
        matches = re.findall(pattern, query)
        print(f"\n模式 '{desc}': {pattern}")
        print(f"匹配结果: {matches}")
    
    # 2. 测试extract_stock_by_name_enhanced
    validator = UnifiedStockValidator()
    
    # 手动调试_extract_stock_by_name_enhanced
    print("\n\n手动测试股票名称提取:")
    # 尝试直接提取"平安银行"
    test_names = ["平安银行", "平安", "茅台", "贵州茅台"]
    for name in test_names:
        success, ts_code, error = validate_stock_input(name)
        print(f"\n'{name}': 成功={success}, 代码={ts_code}, 错误={error}")


if __name__ == "__main__":
    debug_stock_validation()
    debug_full_flow()
    analyze_specific_issue()