#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""测试多股票提取功能"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.unified_stock_validator import unified_validator

def test_multi_stock_extraction():
    """测试多股票提取"""
    test_queries = [
        "评估平安银行和招商银行的主力差异",
        "研究比亚迪与宁德时代的资金流向",
        "分析贵州茅台和五粮液的资金对比",
        "万科A和保利发展的资金对比研究",
        "贵州茅台vs五粮液资金分析",
    ]
    
    print("测试多股票提取功能")
    print("="*60)
    
    for query in test_queries:
        print(f"\n查询: {query}")
        stocks = unified_validator.extract_multiple_stocks(query)
        print(f"提取到的股票: {stocks}")
        print(f"股票数量: {len(stocks)}")
        
        # 详细验证每个股票
        if stocks:
            from utils.stock_code_mapper import get_stock_mapper
            mapper = get_stock_mapper()
            for ts_code in stocks:
                stock_name = mapper.get_stock_name(ts_code)
                print(f"  - {ts_code}: {stock_name}")

if __name__ == "__main__":
    test_multi_stock_extraction()