#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试单个查询
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.sql_agent_modular import SQLAgentModular
import json


def main():
    print("初始化SQL Agent模块化版本...")
    agent = SQLAgentModular()
    
    # 测试市值排名查询
    query = "市值排名前3"
    print(f"\n测试查询: {query}")
    print("="*60)
    
    result = agent.query(query)
    
    print(f"成功: {result.get('success')}")
    print(f"查询类型: {result.get('query_type', 'unknown')}")
    
    if result.get('success'):
        print(f"\n结果:")
        print(result.get('result'))
    else:
        print(f"\n错误: {result.get('error')}")
        
    # 测试板块主力资金
    query2 = "银行板块的主力资金"
    print(f"\n\n测试查询: {query2}")
    print("="*60)
    
    result2 = agent.query(query2)
    
    print(f"成功: {result2.get('success')}")
    
    if result2.get('success'):
        print(f"\n结果:")
        print(result2.get('result'))
    else:
        print(f"\n错误: {result2.get('error')}")


if __name__ == "__main__":
    main()