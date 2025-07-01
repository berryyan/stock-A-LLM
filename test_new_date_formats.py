#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试新增的K线查询日期格式
- YYYY/MM/DD格式
- MM月DD日格式（无年份默认今年）
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.query_templates import QueryTemplateLibrary
from agents.sql_agent import SQLAgent
from datetime import datetime

def test_new_date_formats():
    """测试新增的日期格式支持"""
    print("K线查询新日期格式测试")
    print("=" * 80)
    
    # 初始化组件
    query_templates = QueryTemplateLibrary()
    sql_agent = SQLAgent()
    current_year = datetime.now().year
    
    # 新增格式测试用例
    test_cases = [
        # YYYY/MM/DD格式
        ("宁德时代从2025/06/01到2025/06/30的K线", "2025/06/01", "2025/06/30"),
        ("贵州茅台从2025/6/1到2025/6/30的K线", "2025/6/1", "2025/6/30"),
        
        # MM月DD日格式（无年份）
        ("宁德时代从6月1日到6月30日的K线", "6月1日", "6月30日"),
        ("比亚迪从12月1日到12月31日的K线", "12月1日", "12月31日"),
        
        # 混合格式
        ("中国平安从6月1日到2025/06/30的K线", "6月1日", "2025/06/30"),
        ("万科A从2025-06-01到6月30日的K线", "2025-06-01", "6月30日"),
    ]
    
    print("1. 模板匹配和参数提取测试")
    print("-" * 60)
    
    for query, expected_start, expected_end in test_cases:
        print(f"\n查询: {query}")
        
        # 测试模板匹配
        template = query_templates.match_template(query)
        if template:
            print(f"✅ 匹配模板: {template.name}")
            
            # 测试参数提取
            params = query_templates.extract_params(query, template)
            print(f"提取参数:")
            print(f"  - time_range: {params.get('time_range')}")
            print(f"  - start_date: {params.get('start_date')} (期望: {expected_start})")
            print(f"  - end_date: {params.get('end_date')} (期望: {expected_end})")
            
            # 验证参数提取
            if params.get('start_date') == expected_start and params.get('end_date') == expected_end:
                print("✅ 日期提取正确")
            else:
                print("❌ 日期提取错误")
        else:
            print("❌ 模板匹配失败")
    
    print("\n\n2. 日期格式归一化测试")
    print("-" * 60)
    
    # 测试日期格式归一化
    date_formats_test = [
        ("2025/06/01", "20250601"),
        ("2025/6/1", "20250601"),
        ("6月1日", f"{current_year}0601"),
        ("12月31日", f"{current_year}1231"),
        ("2025-06-01", "20250601"),
        ("2025年6月1日", "20250601"),
        ("20250601", "20250601"),
    ]
    
    for date_str, expected in date_formats_test:
        normalized = sql_agent._normalize_date_format(date_str)
        print(f"{date_str} -> {normalized} (期望: {expected})")
        if normalized == expected:
            print("✅ 归一化正确")
        else:
            print("❌ 归一化错误")
    
    print("\n\n3. 完整查询测试")
    print("-" * 60)
    
    # 测试关键用例的完整查询
    key_test_cases = [
        "宁德时代从2025/06/01到2025/06/30的K线",
        "宁德时代从6月1日到6月30日的K线",
    ]
    
    for query in key_test_cases:
        print(f"\n查询: {query}")
        
        result = sql_agent._try_quick_query(query)
        
        if result and result.get('success'):
            print("✅ 快速路由成功")
            
            # 检查结构化数据中的日期
            if 'structured_data' in result:
                period = result['structured_data']['period']
                print(f"周期描述: {period}")
                
                # 验证日期是否正确处理
                if "6月1日" in query and str(current_year) not in query:
                    if str(current_year) in period:
                        print(f"✅ 无年份日期默认使用今年({current_year})")
                    else:
                        print("❌ 无年份日期处理错误")
                        
        else:
            print("❌ 快速路由失败")
    
    print("\n" + "=" * 80)
    print("测试完成！")

if __name__ == "__main__":
    test_new_date_formats()