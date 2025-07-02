#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
快速测试术语标准化
"""

from agents.money_flow_agent import MoneyFlowAgent


def quick_test():
    """快速测试"""
    
    print("术语标准化快速测试")
    print("=" * 60)
    
    agent = MoneyFlowAgent()
    
    # 测试标准化
    test_cases = [
        "贵州茅台的游资流入",
        "平安银行的散户资金", 
        "比亚迪的外星人资金",
    ]
    
    for query in test_cases:
        print(f"\n原始: {query}")
        standardized, hints = agent.standardize_fund_terms(query)
        print(f"标准化: {standardized}")
        print(f"提示: {hints}")
        is_money_flow = agent.is_money_flow_query(query)
        print(f"识别为资金查询: {is_money_flow}")
    
    # 测试错误提示
    print("\n\n测试错误提示:")
    print("-" * 60)
    
    # 模拟无法识别的查询
    query = "平安银行的外星人资金流向"
    result = {'success': False}
    
    # 检查是否包含资金关键词
    fund_keywords = ['资金', '流入', '流出', '买入', '卖出']
    if any(keyword in query for keyword in fund_keywords):
        result['error'] = f'无法识别的资金类型查询。\n{agent.STANDARD_FUND_TYPES}'
    
    print(f"查询: {query}")
    print(f"错误信息: {result['error'][:100]}...")
    
    # 显示映射表
    print("\n\n术语映射表:")
    print("-" * 60)
    print(f"共 {len(agent.FUND_TYPE_MAPPING)} 个映射")
    for k, v in list(agent.FUND_TYPE_MAPPING.items())[:5]:
        print(f"  {k} -> {v}")
    print("  ...")


if __name__ == "__main__":
    quick_test()