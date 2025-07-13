#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
调试Financial Agent的股票名称识别问题
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.stock_code_mapper import convert_to_ts_code

# 测试失败的股票名称
test_stocks = [
    "宁德时代",
    "比亚迪", 
    "恒大",
    "万科A",
    "平安银行",
    "贵州茅台"
]

print("测试stock_code_mapper对这些股票名称的转换：")
print("-" * 50)

for stock in test_stocks:
    result = convert_to_ts_code(stock)
    print(f"{stock} -> {result}")

# 测试Financial Agent的名称提取逻辑
import re

test_queries = [
    "评估宁德时代的投资机会",
    "比亚迪值得投资吗",
    "分析恒大的风险状况",
    "评估万科A的财务风险和股价表现"
]

print("\n\n测试Financial Agent的名称提取模式：")
print("-" * 50)

name_patterns = [
    r'([一-龥]{2,6}(?:股份|集团|银行|科技|电子|医药|能源|地产|证券|保险|汽车|新材料|新能源))',
    r'([一-龥]{2,6}[A-Z]?(?=的|财务|分析|怎么样|如何))',  # 如 "万科A的财务"
    r'分析([一-龥]{2,6})的',  # 如 "分析茅台的"
    r'([一-龥]{2,4})(?:股价|财务|业绩|年报|公告)'  # 如 "茅台股价"
]

for query in test_queries:
    print(f"\n查询: {query}")
    found = False
    for i, pattern in enumerate(name_patterns):
        matches = re.findall(pattern, query)
        if matches:
            print(f"  模式{i+1}匹配到: {matches}")
            found = True
    if not found:
        print(f"  没有模式匹配到任何内容")