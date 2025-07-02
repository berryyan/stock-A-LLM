#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试板块主力资金查询功能
"""

from agents.sql_agent import SQLAgent
from utils.query_templates import match_query_template

def test_sector_money_flow():
    """测试板块主力资金查询"""
    
    print("=" * 60)
    print("板块主力资金查询测试")
    print("=" * 60)
    
    # 测试模板匹配
    test_queries = [
        "银行板块的主力资金流入",
        "汽车板块主力资金",
        "医药板块的主力资金流向",
        "房地产行业的主力资金",
        "新能源板块主力资金流入情况",
        "银行行业的机构资金",
        "半导体板块的大资金动向",
    ]
    
    print("\n1. 模板匹配测试:")
    print("-" * 40)
    for query in test_queries:
        result = match_query_template(query)
        if result:
            template, params = result
            print(f"查询: {query}")
            print(f"  匹配模板: {template.name}")
            print(f"  路由类型: {template.route_type}")
            print(f"  提取参数: {params}")
            print()
        else:
            print(f"查询: {query}")
            print(f"  ❌ 未匹配到模板")
            print()
    
    # 测试SQL执行
    print("\n2. SQL执行测试:")
    print("-" * 40)
    
    agent = SQLAgent()
    
    # 测试一个具体的板块查询
    test_query = "银行板块的主力资金流入"
    print(f"测试查询: {test_query}")
    
    try:
        result = agent.query(test_query)
        if result['success']:
            print("✅ 查询成功")
            print("\n查询结果:")
            print(result['result'])
        else:
            print(f"❌ 查询失败: {result.get('error', '未知错误')}")
    except Exception as e:
        print(f"❌ 执行错误: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    test_sector_money_flow()