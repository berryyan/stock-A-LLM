#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试日期解析后的模板匹配
"""

from utils.query_templates import match_query_template

def test_template_with_date():
    """测试带日期的查询是否能匹配模板"""
    
    test_queries = [
        # 原始查询
        "总市值最大的前10只股票",
        "今天总市值最大的前10只股票",
        
        # 日期解析后的查询
        "2025-07-01总市值最大的前10只股票",
        "20250701总市值最大的前10只股票",
        "2025年07月01日总市值最大的前10只股票",
    ]
    
    print("日期解析后的模板匹配测试")
    print("=" * 80)
    
    for query in test_queries:
        print(f"\n查询: {query}")
        result = match_query_template(query)
        
        if result:
            template, params = result
            print(f"✅ 匹配成功")
            print(f"   模板名称: {template.name}")
            print(f"   路由类型: {template.route_type}")
            print(f"   提取参数: {params}")
        else:
            print(f"❌ 未匹配到任何模板")
        
        print("-" * 40)


if __name__ == "__main__":
    test_template_with_date()