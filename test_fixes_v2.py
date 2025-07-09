#!/usr/bin/env python3
"""测试v2.2.7修复效果"""

import sys
sys.path.append('.')

from agents.sql_agent_modular import SQLAgentModular

def test_fixes():
    """测试修复的问题"""
    agent = SQLAgentModular()
    
    test_cases = [
        # 板块查询日期解析
        ("银行板块昨天的主力资金", "板块查询成功"),
        ("白酒板块今天的主力资金", "板块查询成功"),
        
        # 非标准术语
        ("贵州茅台的机构资金", "请使用标准术语"),
        ("平安银行的大资金流入", "请使用标准术语"),
        ("万科A的游资", "请使用标准术语"),
    ]
    
    print("测试v2.2.7修复效果")
    print("=" * 80)
    
    for query, expected in test_cases:
        print(f"\n查询: {query}")
        print(f"期望: {expected}")
        
        try:
            result = agent.query(query)
            if result['success']:
                print(f"结果: 成功")
                if expected == "板块查询成功":
                    # 检查是否包含板块数据
                    if '板块' in result.get('result', ''):
                        print("✅ 通过")
                    else:
                        print("❌ 失败 - 未包含板块数据")
                else:
                    print("❌ 失败 - 应该返回错误")
            else:
                error_msg = result.get('error', '')
                print(f"结果: 失败 - {error_msg}")
                if expected in error_msg:
                    print("✅ 通过")
                else:
                    print("❌ 失败 - 错误消息不匹配")
        except Exception as e:
            print(f"异常: {str(e)}")
            print("❌ 失败")

if __name__ == "__main__":
    test_fixes()