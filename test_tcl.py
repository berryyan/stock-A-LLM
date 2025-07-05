#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试TCL股票提取
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.unified_stock_validator import UnifiedStockValidator

validator = UnifiedStockValidator()

query = "TCL科技和TCL智家2025年一季度财务对比"
print(f"查询: {query}")

# 测试extract_multiple_stocks
stocks = validator.extract_multiple_stocks(query)
print(f"extract_multiple_stocks结果: {stocks}")

# 手动测试每个股票
for name in ["TCL科技", "TCL智家"]:
    print(f"\n手动测试 '{name}':")
    success, ts_code, error = validator.validate_and_extract(name)
    print(f"  成功: {success}, 代码: {ts_code}")