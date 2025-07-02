#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试成交量查询快速路由
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.sql_agent import SQLAgent
from utils.query_templates import match_query_template
import time

def test_volume_template_match():
    """测试成交量查询的模板匹配"""
    
    print("成交量查询模板匹配测试")
    print("=" * 80)
    
    test_queries = [
        "贵州茅台的成交量",
        "平安银行昨天的成交量", 
        "万科A最新成交量",
        "600519.SH今天的成交量",
        "中国平安2025-07-01的成交量",
        
        # 对比：成交额排名（应该匹配成交额排名模板）
        "成交额排名",
        "成交量排名",  # 这个应该匹配什么？
    ]
    
    for query in test_queries:
        print(f"\n查询: {query}")
        result = match_query_template(query)
        
        if result:
            template, params = result
            print(f"✅ 匹配模板: {template.name}")
            print(f"   类型: {template.type}")
            print(f"   路由: {template.route_type}")
        else:
            print("❌ 未匹配到任何模板")

def test_volume_quick_route():
    """测试成交量查询的快速路由"""
    
    print("\n\n成交量查询快速路由测试")
    print("=" * 80)
    
    sql_agent = SQLAgent()
    
    test_queries = [
        ("贵州茅台的成交量", "基础成交量查询"),
        ("平安银行昨天的成交量", "带日期成交量查询"),
        ("万科A最新成交量", "最新成交量查询"),
        ("600519.SH今天的成交量", "今天成交量查询"),
    ]
    
    for query, desc in test_queries:
        print(f"\n{'='*60}")
        print(f"测试: {desc}")
        print(f"查询: {query}")
        print("-" * 60)
        
        try:
            start_time = time.time()
            result = sql_agent.query(query)
            end_time = time.time()
            elapsed = end_time - start_time
            
            if result['success']:
                if result.get('quick_path'):
                    print(f"⚡ 快速路由 (耗时: {elapsed:.2f}秒)")
                else:
                    print(f"🐌 慢速路由 (耗时: {elapsed:.2f}秒)")
                    
                # 显示部分结果
                result_text = result['result']
                lines = result_text.split('\n')[:5]
                for line in lines:
                    print(line)
                    
            else:
                print(f"❌ 查询失败: {result.get('error', '未知错误')}")
                
        except Exception as e:
            print(f"❌ 执行异常: {str(e)}")
        
        time.sleep(0.5)

if __name__ == "__main__":
    # 测试模板匹配
    test_volume_template_match()
    
    # 测试快速路由
    test_volume_quick_route()