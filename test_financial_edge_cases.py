#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试财务分析边缘案例
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.financial_agent import FinancialAnalysisAgent

def test_edge_cases():
    """测试边缘案例"""
    agent = FinancialAnalysisAgent()
    
    test_cases = [
        ("分析999999.BJ的财务健康度", "不存在的北交所股票"),
        ("分析920819.BJ的财务健康度", "存在的北交所股票"), 
        ("分析833751的财务健康度", "不带后缀的北交所股票"),
        ("分析000000.SX的财务健康度", "错误的后缀"),
    ]
    
    print("=" * 80)
    print("财务分析边缘案例测试")
    print("=" * 80)
    
    for query, desc in test_cases:
        print(f"\n测试: {query} ({desc})")
        print("-" * 60)
        
        result = agent.query(query)
        
        if result['success']:
            print(f"✓ 成功 - 股票代码: {result.get('ts_code')}")
            if 'health_score' in result:
                score = result['health_score']
                print(f"  财务健康度: {score['total_score']}分 ({score['rating']}级)")
        else:
            print(f"✓ 正确处理 - 错误提示: {result.get('error')}")

if __name__ == "__main__":
    test_edge_cases()