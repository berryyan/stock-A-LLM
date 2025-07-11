#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试板块深度分析功能
"""

import sys
sys.path.append('.')

from agents.money_flow_agent_modular import MoneyFlowAgentModular

def test_sector_analysis():
    """测试板块分析"""
    agent = MoneyFlowAgentModular()
    
    # 测试1: 板块深度分析
    print("="*60)
    print("测试1: 分析银行板块的资金流向")
    result = agent.query("分析银行板块的资金流向")
    print(f"成功: {result.get('success')}")
    if result.get('success'):
        print(f"结果预览:\n{result.get('result', '')[:500]}")
    else:
        print(f"错误: {result.get('error')}")
    
    # 测试2: 板块简单数据查询（应该路由到SQL）
    print("\n" + "="*60)
    print("测试2: 银行板块的主力资金")
    result = agent.query("银行板块的主力资金")
    print(f"成功: {result.get('success')}")
    if not result.get('success'):
        print(f"错误: {result.get('error')}")
        if "应该由SQL Agent处理" in str(result.get('error')):
            print("✓ 正确识别为SQL查询")
    
    # 测试3: 板块趋势评估
    print("\n" + "="*60)
    print("测试3: 评估新能源板块的资金趋势")
    result = agent.query("评估新能源板块的资金趋势")
    print(f"成功: {result.get('success')}")
    if result.get('success'):
        print(f"板块数据: {result.get('sector_data')}")
    else:
        print(f"错误: {result.get('error')}")

if __name__ == "__main__":
    test_sector_analysis()