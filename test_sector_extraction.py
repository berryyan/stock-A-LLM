#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""测试板块提取功能"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.unified_sector_validator import extract_sector, extract_multiple_sectors

def test_sector_extraction():
    """测试板块提取"""
    test_queries = [
        "评估光伏设备板块的资金趋势",
        "银行板块的主力资金",
        "光伏设备板块主力资金",
        "房地产开发板块的超大单",
        "分析银行板块的资金流向",
        "研究房地产开发板块的主力行为",
    ]
    
    print("测试板块提取功能")
    print("="*60)
    
    for query in test_queries:
        print(f"\n查询: {query}")
        
        # 测试单板块提取
        result = extract_sector(query)
        if result:
            sector_name, sector_code = result
            print(f"提取到板块: {sector_name} ({sector_code})")
        else:
            print("未提取到板块")
        
        # 测试多板块提取
        sectors = extract_multiple_sectors(query)
        print(f"多板块提取: {len(sectors)}个板块")
        for sector_name, sector_code in sectors:
            print(f"  - {sector_name} ({sector_code})")

if __name__ == "__main__":
    test_sector_extraction()