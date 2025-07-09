#!/usr/bin/env python3
"""测试宁德时代的股票映射"""

import sys
sys.path.append('.')

from utils.stock_code_mapper import convert_to_ts_code
from utils.unified_stock_validator import UnifiedStockValidator

# 测试股票代码映射
print("测试股票代码映射:")
print("-" * 50)

names = ["宁德时代", "300750", "300750.SZ", "CATL"]

for name in names:
    ts_code = convert_to_ts_code(name)
    print(f"{name} -> {ts_code}")

# 测试股票验证器
print("\n测试统一股票验证器:")
print("-" * 50)

validator = UnifiedStockValidator()
queries = [
    "宁德时代的股价",
    "宁德时代昨天的成交额",
    "宁德时代今天的成交额",
    "宁德时代从6月1日到6月30日的K线"
]

for query in queries:
    print(f"\n查询: {query}")
    stocks = validator.extract_multiple_stocks(query)
    print(f"提取到的股票: {stocks}")
    
    if stocks:
        for stock in stocks:
            result = validator.validate_stock(stock)
            print(f"验证结果: {result}")