#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
专门测试"平安"相关查询的修复效果
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.sql_agent import SQLAgent

def test_pingan_queries():
    """测试平安相关查询"""
    sql_agent = SQLAgent()
    
    test_queries = [
        "平安银行PE",
        "中国平安PE",
        "平安电工市盈率",
        "平安银行最新股价",
        "中国平安市盈率",
    ]
    
    print("=" * 80)
    print("测试'平安'相关查询修复效果")
    print("=" * 80)
    
    for query in test_queries:
        print(f"\n查询: {query}")
        print("-" * 40)
        
        try:
            result = sql_agent.query(query)
            
            if result['success']:
                print("✅ 查询成功")
                print(f"结果: {result['result'][:200]}...")  # 只显示前200字符
            else:
                print("❌ 查询失败")
                print(f"错误: {result['error']}")
                
        except Exception as e:
            print(f"❌ 异常: {str(e)}")

if __name__ == "__main__":
    test_pingan_queries()