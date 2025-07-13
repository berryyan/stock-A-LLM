#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试Financial Agent股票名称提取修复
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.financial_agent import FinancialAnalysisAgent

# 测试查询
test_queries = [
    "评估宁德时代的投资机会",
    "比亚迪值得投资吗",
    "分析恒大的风险状况",
    "评估万科A的财务风险和股价表现",
    "分析贵州茅台的财务健康度"
]

print("测试Financial Agent股票名称提取修复")
print("=" * 50)

agent = FinancialAnalysisAgent()

for query in test_queries:
    print(f"\n查询: {query}")
    
    # 调用内部方法测试股票名称提取
    intent, ts_code = agent._parse_query_intent(query)
    
    print(f"  意图: {intent}")
    print(f"  提取的ts_code: {ts_code}")
    
    if ts_code and ts_code not in ['INVALID_FORMAT', 'INVALID_LENGTH']:
        print(f"  ✅ 成功提取股票代码")
    else:
        print(f"  ❌ 提取失败")