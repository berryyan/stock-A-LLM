#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
简单测试当前术语处理情况
"""

from agents.money_flow_agent import MoneyFlowAgent


def test_current_behavior():
    """测试当前行为"""
    
    print("测试当前MoneyFlowAgent对非标准术语的处理")
    print("=" * 60)
    
    agent = MoneyFlowAgent()
    
    # 测试是否识别查询
    test_queries = [
        "贵州茅台的游资流入",
        "平安银行的散户资金", 
        "比亚迪的外星人资金",
    ]
    
    for query in test_queries:
        print(f"\n查询: {query}")
        
        # 测试is_money_flow_query
        is_money_flow = agent.is_money_flow_query(query)
        print(f"被识别为资金流向查询: {is_money_flow}")
        
        # 检查是否有标准化函数
        if hasattr(agent, 'standardize_fund_terms'):
            print("✅ 有standardize_fund_terms方法")
        else:
            print("❌ 没有standardize_fund_terms方法")
    
    # 检查是否有术语映射
    if hasattr(agent, 'FUND_TYPE_MAPPING'):
        print(f"\n✅ 有FUND_TYPE_MAPPING: {agent.FUND_TYPE_MAPPING}")
    else:
        print("\n❌ 没有FUND_TYPE_MAPPING")


if __name__ == "__main__":
    test_current_behavior()