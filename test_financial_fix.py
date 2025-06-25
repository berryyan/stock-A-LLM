#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试财务分析修复
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.financial_agent import FinancialAnalysisAgent
from utils.stock_code_mapper import convert_to_ts_code

def test_stock_mapper():
    """测试股票代码映射器"""
    print("=" * 60)
    print("测试股票代码映射器")
    print("=" * 60)
    
    test_cases = [
        "贵州茅台",
        "国轩高科",  
        "002047",
        "002047.SZ",
        "002074",  # 国轩高科的代码
    ]
    
    for case in test_cases:
        result = convert_to_ts_code(case)
        print(f"{case:15} -> {result}")
    print()

def test_financial_analysis():
    """测试财务分析功能"""
    print("=" * 60)
    print("测试财务分析功能")
    print("=" * 60)
    
    agent = FinancialAnalysisAgent()
    
    test_queries = [
        "分析贵州茅台的财务健康度",
        "分析国轩高科的财务健康度",
        "分析002047的财务健康度",
        "分析002047.SZ的财务健康度",
    ]
    
    for query in test_queries:
        print(f"\n查询: {query}")
        print("-" * 40)
        
        result = agent.query(query)
        
        if result['success']:
            print(f"✓ 成功 - 股票代码: {result.get('ts_code')}")
            if 'health_score' in result:
                score = result['health_score']
                print(f"  财务健康度: {score['total_score']}分 ({score['rating']}级)")
        else:
            print(f"✗ 失败 - 错误: {result.get('error')}")
            if 'message' in result:
                print(f"  {result['message']}")

if __name__ == "__main__":
    test_stock_mapper()
    test_financial_analysis()