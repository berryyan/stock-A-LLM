#!/usr/bin/env python3
"""测试PE排行查询"""

import sys
sys.path.append('.')

from agents.sql_agent_modular import SQLAgentModular

def test_pe_ranking():
    """测试PE排行"""
    agent = SQLAgentModular()
    
    query = "PE排行"
    print(f"查询: {query}")
    
    try:
        result = agent.query(query)
        if result['success']:
            print("✅ 成功")
            print(f"结果预览: {str(result.get('result', ''))[:200]}...")
        else:
            print("❌ 失败")
            print(f"错误: {result.get('error', '')}")
    except Exception as e:
        print(f"异常: {str(e)}")

if __name__ == "__main__":
    test_pe_ranking()