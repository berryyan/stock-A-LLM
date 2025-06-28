#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
快速测试灵活解析器是否工作
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.sql_agent import SQLAgent
import logging

# 设置日志级别为DEBUG以查看详细信息
logging.basicConfig(level=logging.INFO)

def test_parser():
    print("测试灵活解析器是否正常工作...")
    
    # 初始化SQL Agent
    agent = SQLAgent()
    
    # 测试查询
    test_queries = [
        "贵州茅台最新股价",
        "查询茅台的营业收入"
    ]
    
    for query in test_queries:
        print(f"\n测试: {query}")
        result = agent.query(query)
        
        if result['success']:
            print(f"✅ 成功")
            print(f"结果: {str(result['result'])[:100]}...")
        else:
            print(f"❌ 失败: {result.get('error', 'Unknown')}")
    
    # 检查是否有灵活解析器实例
    print(f"\n灵活解析器实例: {hasattr(agent, 'flexible_parser')}")
    if hasattr(agent, 'flexible_parser'):
        print(f"解析器类型: {type(agent.flexible_parser)}")

if __name__ == "__main__":
    test_parser()