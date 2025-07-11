#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""调试Financial Agent的问题"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.financial_agent_modular import FinancialAgentModular
from utils.parameter_extractor import ParameterExtractor

def debug_specific_queries():
    """调试具体失败的查询"""
    
    # 失败的正向测试
    failed_queries = [
        "贵州茅台的杜邦分析",
        "分析万科A的现金流质量",
        "贵州茅台2025年一季度与去年同期对比",
        "分析比亚迪的盈利能力"
    ]
    
    agent = FinancialAgentModular()
    extractor = ParameterExtractor()
    
    for query in failed_queries:
        print(f"\n{'='*60}")
        print(f"调试查询: {query}")
        print('-'*60)
        
        # 1. 测试参数提取
        print("\n1. 参数提取测试:")
        params = extractor.extract_all_params(query)
        print(f"   提取的股票: {params.stocks}")
        print(f"   股票名称: {params.stock_names}")
        print(f"   错误信息: {params.error}")
        
        # 2. 测试分析类型识别
        print("\n2. 分析类型识别:")
        analysis_type = agent._identify_analysis_type(query)
        print(f"   识别的类型: {analysis_type}")
        
        # 3. 执行完整查询
        print("\n3. 执行查询:")
        result = agent.analyze(query)
        print(f"   成功: {result.get('success', False)}")
        if not result.get('success'):
            print(f"   错误: {result.get('error', '未知错误')}")
        else:
            print(f"   结果类型: {type(result.get('result', None))}")
            print(f"   有数据: {'data' in result}")
            print(f"   有raw_data: {'raw_data' in result}")

def test_parent_methods():
    """测试父类方法是否正常"""
    print("\n" + "="*60)
    print("测试父类方法")
    print("="*60)
    
    from agents.financial_agent import FinancialAnalysisAgent
    base_agent = FinancialAnalysisAgent()
    
    # 测试父类的分析方法
    test_cases = [
        ("analyze_financial_health", "600519.SH"),
        ("analyze_dupont", "600519.SH"),
        ("analyze_cash_flow_quality", "000001.SZ"),
        ("analyze_profitability", "002594.SZ")
    ]
    
    for method_name, ts_code in test_cases:
        print(f"\n测试 {method_name}({ts_code}):")
        try:
            method = getattr(base_agent, method_name)
            result = method(ts_code)
            print(f"   成功: {result.get('success', False)}")
            if not result.get('success'):
                print(f"   错误: {result.get('error', '未知错误')}")
        except Exception as e:
            print(f"   异常: {str(e)}")

if __name__ == "__main__":
    debug_specific_queries()
    test_parent_methods()