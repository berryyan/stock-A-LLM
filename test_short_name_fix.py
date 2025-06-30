#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试简称映射修复效果
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.unified_stock_validator import UnifiedStockValidator
from utils.stock_code_mapper import convert_to_ts_code

def test_short_name_fix():
    """测试简称映射修复"""
    validator = UnifiedStockValidator()
    
    test_cases = [
        # 测试"平安"相关查询
        "平安银行PE",
        "中国平安PE", 
        "平安电工股价",
        
        # 测试"万科"修正
        "万科财务分析",
        
        # 测试银行简称
        "建行股价",
        "工行市盈率",
        "农行财务健康度",
        
        # 测试其他简称
        "茅台最新股价",
        "格力电器分析",
        
        # 测试完整名称
        "贵州茅台财务健康度",
        "格力博股价",
    ]
    
    print("=" * 80)
    print("简称映射修复测试")
    print("=" * 80)
    
    for query in test_cases:
        print(f"\n查询: {query}")
        
        # 解析查询
        intent, ts_code_or_error, error_detail = validator.parse_query_intent_and_extract_stock(query)
        
        if ts_code_or_error in ['INVALID_FORMAT', 'INVALID_CASE', 'INVALID_LENGTH', 
                                'STOCK_NOT_EXISTS', 'USE_FULL_NAME', 'NOT_FOUND']:
            print(f"  ❌ 错误类型: {ts_code_or_error}")
            if error_detail:
                print(f"  错误详情: {error_detail}")
        else:
            # 获取股票名称
            from utils.stock_code_mapper import get_stock_name
            stock_name = get_stock_name(ts_code_or_error)
            print(f"  ✅ 识别成功: {stock_name}({ts_code_or_error})")
            print(f"  查询意图: {intent}")
    
    # 测试直接的股票代码转换
    print("\n" + "=" * 80)
    print("直接股票名称转换测试")
    print("=" * 80)
    
    direct_tests = [
        "平安银行",
        "中国平安",
        "平安电工",
        "万科A",
        "格力电器",
        "格力博",
        "建设银行",
        "工商银行",
    ]
    
    for name in direct_tests:
        ts_code = convert_to_ts_code(name)
        if ts_code:
            print(f"{name} → {ts_code}")
        else:
            print(f"{name} → 未找到")

if __name__ == "__main__":
    test_short_name_fix()