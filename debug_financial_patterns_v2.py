#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
调试Financial Agent的股票名称提取模式 V2
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.stock_code_mapper import convert_to_ts_code
import re

# 第二个模式有问题，它包含了前面的动词
# r'([一-龥]{2,6}[A-Z]?(?=的|财务|分析|怎么样|如何))'

# 测试改进的模式
test_queries = [
    "评估宁德时代的投资机会",
    "比亚迪值得投资吗",
    "分析恒大的风险状况",
    "评估万科A的财务风险和股价表现"
]

print("问题分析：")
print("-" * 50)

# 原始模式2
pattern2 = r'([一-龥]{2,6}[A-Z]?(?=的|财务|分析|怎么样|如何))'

for query in test_queries:
    matches = re.findall(pattern2, query)
    print(f"查询: {query}")
    print(f"  模式2匹配: {matches}")
    
    # 分析为什么会匹配到错误内容
    if matches:
        for match in matches:
            if match.startswith('评估') or match.startswith('分析'):
                print(f"  ❌ 错误：匹配到了动词+股票名称")

print("\n\n改进方案：")
print("-" * 50)

# 改进的模式：使用更精确的边界
improved_patterns = [
    # 模式1: 特定行业后缀
    r'([一-龥]{2,6}(?:股份|集团|银行|科技|电子|医药|能源|地产|证券|保险|汽车|新材料|新能源))',
    
    # 模式2: 改进版 - 不包含动词
    r'(?:评估|分析|查询|对|给|把|将)([一-龥]{2,6}[A-Z]?)(?=的|财务|进行|做)',
    
    # 模式3: "动词+名称+的"结构
    r'(?:分析|评估|查询)([一-龥]{2,6})的',
    
    # 模式4: 名称后跟特定词
    r'([一-龥]{2,6}[A-Z]?)(?:值得|是否|怎么样|如何|股价|财务|业绩)',
    
    # 模式5: 独立的2-6个汉字（作为兜底）
    r'(?:^|\\s)([一-龥]{2,6}[A-Z]?)(?:$|\\s|的|，|。|？|！)'
]

for query in test_queries:
    print(f"\n查询: {query}")
    all_matches = []
    
    for i, pattern in enumerate(improved_patterns):
        matches = re.findall(pattern, query)
        if matches:
            print(f"  模式{i+1}匹配: {matches}")
            all_matches.extend(matches)
    
    # 去重并尝试转换
    unique_matches = list(set(all_matches))
    for match in unique_matches:
        # 过滤掉动词
        if match not in ['评估', '分析', '查询', '对比']:
            ts_code = convert_to_ts_code(match)
            if ts_code:
                print(f"  ✅ 成功转换: {match} -> {ts_code}")
            else:
                print(f"  ❌ 无法转换: {match}")