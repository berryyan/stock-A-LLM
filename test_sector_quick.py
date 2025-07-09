#!/usr/bin/env python3
"""快速测试板块查询问题"""

import sys
sys.path.append('.')

from agents.sql_agent_modular import SQLAgentModular

def test_sector_queries():
    """测试板块查询"""
    agent = SQLAgentModular()
    
    # 测试两个失败的查询
    queries = [
        "银行板块昨天的主力资金",
        "白酒板块今天的主力资金"
    ]
    
    for query in queries:
        print(f"\n查询: {query}")
        try:
            result = agent.query(query)
            if result['success']:
                print("✅ 成功")
                print(f"结果预览: {str(result.get('result', ''))[:100]}...")
            else:
                print("❌ 失败")
                print(f"错误: {result.get('error', '')}")
        except Exception as e:
            print(f"异常: {str(e)}")

if __name__ == "__main__":
    test_sector_queries()