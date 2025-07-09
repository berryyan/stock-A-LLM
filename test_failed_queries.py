#!/usr/bin/env python3
"""测试失败的查询"""

import sys
sys.path.append('.')

from agents.sql_agent_modular import SQLAgentModular

def test_failed_queries():
    """测试失败的查询"""
    agent = SQLAgentModular()
    
    # 失败的查询列表
    queries = [
        ("宁德时代昨天的成交额", "成交额查询-昨天"),
        ("宁德时代今天的成交额", "成交额查询-今天"),
        ("宁德时代从6月1日到6月30日的K线", "K线查询-中文日期"),
        ("PE排行", "PE排名-默认"),
    ]
    
    print("测试失败的查询")
    print("=" * 80)
    
    for query, test_name in queries:
        print(f"\n测试: {test_name}")
        print(f"查询: {query}")
        
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
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    test_failed_queries()