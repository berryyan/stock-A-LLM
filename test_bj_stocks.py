#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试北交所股票代码处理
"""
import re

def test_validate_ts_code():
    """测试证券代码验证"""
    def _validate_ts_code(ts_code: str) -> bool:
        """验证证券代码格式是否正确"""
        pattern = r'^\d{6}\.(SZ|SH|BJ)$'
        return bool(re.match(pattern, ts_code))
    
    test_cases = [
        ("600519.SH", True, "上海主板"),
        ("000001.SZ", True, "深圳主板"),
        ("999999.BJ", True, "北交所-不存在的股票"),
        ("920819.BJ", True, "北交所-存在的股票"),
        ("833751.BJ", True, "北交所-存在的股票"),
        ("600519.SX", False, "错误的后缀"),
        ("60519.SH", False, "位数不足"),
        ("6005199.SH", False, "位数过多"),
    ]
    
    print("=" * 60)
    print("测试证券代码验证")
    print("=" * 60)
    
    for ts_code, expected, desc in test_cases:
        result = _validate_ts_code(ts_code)
        status = "✓" if result == expected else "✗"
        print(f"{status} {ts_code:12} -> {result:5} ({desc})")
    
def test_parse_query():
    """测试查询解析"""
    ts_code_pattern = r'(\d{6}\.(SZ|SH|BJ))'
    
    queries = [
        "分析999999.BJ的财务健康度",
        "分析920819.BJ的财务健康度",
        "分析833751的财务健康度",
    ]
    
    print("\n" + "=" * 60)
    print("测试查询解析")
    print("=" * 60)
    
    for query in queries:
        ts_code_match = re.search(ts_code_pattern, query)
        if ts_code_match:
            extracted = ts_code_match.group(0)
            print(f"查询: {query}")
            print(f"  -> 提取到: {extracted}")
        else:
            print(f"查询: {query}")
            print(f"  -> 未提取到ts_code")

if __name__ == "__main__":
    test_validate_ts_code()
    test_parse_query()