#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试正则表达式匹配
"""

import re

# 成交额排名的正则表达式
pattern = r"(?:.*(\d{8}|\d{4}-\d{2}-\d{2}|\d{4}年\d{2}月\d{2}日|今天|昨天|上个交易日|最新).*)?成交额(?:.*前(\d+)|.*最大.*(\d+)|排名|排行|TOP(\d+))?"

# 测试查询
test_queries = [
    "成交额排名",                    # ✅ 能匹配
    "成交额TOP10",                   # ✅ 能匹配
    "今天的成交额排名",              # 原始查询
    "2025-07-01的成交额排名",        # 日期解析后
    "2025-07-01成交额排名",          # 日期解析后（无"的"）
    "最新成交额排名",                # 原始查询
    "2025-07-01成交额排名",          # 日期解析后
    "昨天成交额排名前10",            # 原始查询
    "2025-06-30成交额排名前10",      # 日期解析后
]

print("正则表达式测试")
print("=" * 80)
print(f"Pattern: {pattern}")
print()

for query in test_queries:
    match = re.search(pattern, query, re.IGNORECASE)
    if match:
        print(f"✅ '{query}' 匹配成功")
        print(f"   Groups: {match.groups()}")
    else:
        print(f"❌ '{query}' 匹配失败")
    print()

# 测试修改后的正则表达式
print("\n修改后的正则表达式测试")
print("=" * 80)

# 尝试不同的正则表达式
patterns = [
    # 原始模式
    r"(?:.*(\d{8}|\d{4}-\d{2}-\d{2}|\d{4}年\d{2}月\d{2}日|今天|昨天|上个交易日|最新).*)?成交额(?:.*前(\d+)|.*最大.*(\d+)|排名|排行|TOP(\d+))?",
    
    # 改进模式1：允许日期在任意位置
    r"(?:.*?(\d{4}-\d{2}-\d{2}|\d{8}|\d{4}年\d{2}月\d{2}日).*?)?成交额(?:.*前(\d+)|.*最大.*(\d+)|排名|排行|TOP(\d+))?",
    
    # 改进模式2：分离日期匹配
    r"成交额(?:.*前(\d+)|.*最大.*(\d+)|排名|排行|TOP(\d+))?",
]

for i, p in enumerate(patterns, 1):
    print(f"\n模式{i}: {p}")
    print("-" * 60)
    
    for query in ["2025-07-01的成交额排名", "2025-07-01成交额排名", "成交额排名"]:
        match = re.search(p, query, re.IGNORECASE)
        if match:
            print(f"✅ '{query}' 匹配成功")
            print(f"   Groups: {match.groups()}")
        else:
            print(f"❌ '{query}' 匹配失败")