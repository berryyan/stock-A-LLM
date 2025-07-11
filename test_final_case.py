#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""测试最后的失败用例"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.money_flow_agent import MoneyFlowAgent

# 测试板块分析
test_cases = [
    "评估光伏设备板块的资金趋势",
    "分析银行板块的资金流向", 
    "房地产开发板块的超大单",
    "医疗器械板块主力净流入"
]

agent = MoneyFlowAgent()

for query in test_cases:
    print(f"\n测试: {query}")
    result = agent.query(query)
    if result.get('success'):
        print(f"✓ 成功 - 类型: {result.get('query_type', 'unknown')}")
        if 'sector' in result.get('query_type', ''):
            print(f"  板块: {result.get('sector_name')} ({result.get('sector_code')})")
    else:
        print(f"✗ 失败 - 错误: {result.get('error')}")