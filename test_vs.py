#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试vs连接词的股票提取
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.unified_stock_validator import UnifiedStockValidator

validator = UnifiedStockValidator()

queries = [
    "贵州茅台vs五粮液",
    "贵州茅台VS五粮液",
    "比较贵州茅台、五粮液和泸州老窖最近30天的走势，按涨幅降序排列，排除ST"
]

for query in queries:
    print(f"\n查询: {query}")
    stocks = validator.extract_multiple_stocks(query)
    print(f"提取到的股票: {stocks}")