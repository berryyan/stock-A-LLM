#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试模板匹配问题
"""

from utils.query_templates import match_query_template

def test_template_matching():
    """测试各个模板的匹配情况"""
    
    test_queries = [
        # 估值指标查询
        ("中国平安的市盈率", "估值指标查询"),
        ("贵州茅台的PE", "估值指标查询"),
        ("平安银行的市净率", "估值指标查询"),
        ("比亚迪的PB", "估值指标查询"),
        
        # 市值排名
        ("总市值最大的前20只股票", "总市值排名"),
        ("市值排名前50", "总市值排名"),
        ("流通市值最大的前10只股票", "流通市值排名"),
        
        # 主力净流入
        ("主力净流入最多的前10只股票", "主力净流入排行"),
        ("主力净流出最多的前10只股票", "主力净流入排行"),
        
        # 成交额排名
        ("成交额最大的前10只股票", "成交额排名"),
        ("成交额排名前20", "成交额排名"),
    ]
    
    print("模板匹配测试结果：")
    print("=" * 80)
    
    for query, expected_template in test_queries:
        result = match_query_template(query)
        
        if result:
            template, params = result
            matched_name = template.name
            route_type = template.route_type
            
            status = "✅" if matched_name == expected_template else "❌"
            print(f"{status} 查询: {query}")
            print(f"   期望模板: {expected_template}")
            print(f"   实际模板: {matched_name}")
            print(f"   路由类型: {route_type}")
            print(f"   提取参数: {params}")
        else:
            print(f"❌ 查询: {query}")
            print(f"   期望模板: {expected_template}")
            print(f"   实际模板: 未匹配到任何模板")
        
        print("-" * 40)


if __name__ == "__main__":
    test_template_matching()