#!/usr/bin/env python3
"""测试板块查询修复"""

import sys
sys.path.append('.')

from agents.sql_agent_modular import SQLAgentModular

def test_sector_queries():
    """测试各种板块查询"""
    agent = SQLAgentModular()
    
    test_cases = [
        "银行板块昨天的主力资金",
        "银行昨天的主力资金",
        "房地产板块的主力资金",
        "房地产的主力资金",
        "新能源板块最新的主力资金",
        "白酒板块的主力资金"
    ]
    
    print("测试板块主力资金查询修复")
    print("=" * 80)
    
    for i, query in enumerate(test_cases, 1):
        print(f"\n测试用例 {i}: {query}")
        print("-" * 60)
        
        try:
            result = agent.query(query)
            
            if result.get('success'):
                print("✅ 查询成功")
                # 只显示结果的前200个字符
                result_text = result.get('result', '')
                if len(result_text) > 200:
                    print(f"结果预览: {result_text[:200]}...")
                else:
                    print(f"结果: {result_text}")
            else:
                print("❌ 查询失败")
                print(f"错误: {result.get('error')}")
                
        except Exception as e:
            print(f"❌ 异常: {str(e)}")
    
    print("\n" + "=" * 80)
    print("测试完成！")

if __name__ == "__main__":
    test_sector_queries()