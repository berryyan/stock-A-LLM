#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试模板匹配逻辑
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.query_templates import match_query_template

# 测试查询
test_queries = [
    "成交额排名",
    "成交额TOP10", 
    "2025-07-01的成交额排名",
    "2025-07-01成交额排名",
    "最新成交额排名",
    "2025-06-30成交额排名前10",
]

print("模板匹配测试")
print("=" * 80)

for query in test_queries:
    print(f"\n查询: {query}")
    result = match_query_template(query)
    
    if result:
        template, params = result
        print(f"✅ 匹配到模板: {template.name}")
        print(f"   类型: {template.type}")
        print(f"   路由: {template.route_type}")
        print(f"   参数: {params}")
    else:
        print("❌ 未匹配到任何模板")