#\!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""测试单个查询"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.money_flow_agent import MoneyFlowAgent

def test_single_query():
    """测试单个查询"""
    query = "评估光伏设备板块的资金趋势"
    
    print(f"测试查询: {query}")
    print("="*60)
    
    agent = MoneyFlowAgent()
    result = agent.query(query)
    
    print(f"成功: {result.get('success', False)}")
    if result.get('success'):
        print(f"结果预览: {result.get('result', '')[:500]}...")
    else:
        print(f"错误: {result.get('error', '未知错误')}")

if __name__ == "__main__":
    test_single_query()
