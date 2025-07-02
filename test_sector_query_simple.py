#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
简单测试板块查询
"""

from agents.sql_agent import SQLAgent

def test_sector_query():
    """测试板块查询"""
    agent = SQLAgent()
    
    # 测试查询
    queries = [
        "银行板块的主力资金流入",
        "光伏设备板块的主力资金",
        "半导体板块昨天的主力资金流向"
    ]
    
    for query in queries:
        print(f"\n{'='*60}")
        print(f"查询: {query}")
        print('='*60)
        
        try:
            result = agent.query(query)
            if result['success']:
                print(result['result'])
            else:
                print(f"❌ 查询失败: {result.get('error', '未知错误')}")
        except Exception as e:
            print(f"❌ 执行错误: {str(e)}")
            import traceback
            traceback.print_exc()


if __name__ == "__main__":
    test_sector_query()