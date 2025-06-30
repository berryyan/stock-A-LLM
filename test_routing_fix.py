#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试路由修复是否生效
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.query_templates import match_query_template
from config.routing_config import routing_config

def test_routing_fix():
    """测试路由修复"""
    test_cases = [
        "今天涨幅最大的前10只股票",
        "总市值最大的前20只股票", 
        "流通市值排名前10",
        "市值排名前20",
        "最新公告",
        "排行分析：今日涨幅前10"  # 触发词测试
    ]
    
    print("测试模板路由覆盖修复:\n")
    print(f"当前TEMPLATE_ROUTE_OVERRIDE配置: {routing_config.TEMPLATE_ROUTE_OVERRIDE}\n")
    
    for query in test_cases:
        template_match = match_query_template(query)
        if template_match:
            template, params = template_match
            # 检查是否有路由覆盖
            override = routing_config.TEMPLATE_ROUTE_OVERRIDE.get(template.name)
            
            print(f"查询: {query}")
            print(f"  匹配模板: {template.name}")
            print(f"  原始路由: {template.route_type}")
            print(f"  覆盖路由: {override if override else '无'}")
            print(f"  最终路由: {override if override else template.route_type}")
            print()
        else:
            print(f"查询: {query}")
            print(f"  未匹配到模板")
            print()

if __name__ == "__main__":
    test_routing_fix()