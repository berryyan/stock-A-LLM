#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试K线查询天数修复
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.sql_agent import SQLAgent

def test_kline_days():
    """测试K线查询天数是否正确"""
    sql_agent = SQLAgent()
    
    test_cases = [
        ("中国平安最近10天的K线", 10),
        ("万科A最近5天的K线", 5),
        ("茅台过去20天的K线", 20),
        ("比亚迪近30天的K线", 30),
        ("中国平安的K线", 90),  # 默认值
    ]
    
    print("K线查询天数修复测试")
    print("=" * 50)
    
    for query, expected_days in test_cases:
        print(f"\n查询: {query}")
        print(f"期望天数: {expected_days}")
        
        # 测试天数提取
        extracted_days = sql_agent._extract_days_from_original_query(query)
        print(f"提取天数: {extracted_days}")
        
        if extracted_days == expected_days:
            print("✅ 天数提取正确")
        else:
            print("❌ 天数提取错误")
        
        # 测试完整快速路由
        result = sql_agent._try_quick_query(query)
        if result and result.get('success'):
            print("✅ 快速路由成功")
            # 检查结果中是否包含正确的天数描述
            content = result['result']
            if f"最近{expected_days}天" in content:
                print("✅ 输出描述正确")
            else:
                print("❌ 输出描述可能不正确")
                print(f"结果预览: {content[:200]}...")
        else:
            print("❌ 快速路由失败")
        
        print("-" * 30)

if __name__ == "__main__":
    test_kline_days()