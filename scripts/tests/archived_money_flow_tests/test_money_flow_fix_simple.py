#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试MoneyFlowAgent修复
"""

from agents.money_flow_agent import MoneyFlowAgent

def test_money_flow_fix():
    """测试修复后的MoneyFlowAgent"""
    
    agent = MoneyFlowAgent()
    
    # 测试查询
    test_queries = [
        "分析贵州茅台的资金流向",
        "比亚迪的资金流向如何",
    ]
    
    for query in test_queries:
        print(f"\n{'='*60}")
        print(f"测试: {query}")
        print('='*60)
        
        try:
            result = agent.query(query)
            
            if result['success']:
                # 检查是否有result字段
                if 'result' in result:
                    print("✅ 成功: result字段存在")
                    print(f"返回字段: {list(result.keys())}")
                    # 打印前200个字符
                    print(f"结果预览: {result['result'][:200]}...")
                else:
                    print("❌ 失败: 缺少result字段")
                    print(f"返回字段: {list(result.keys())}")
            else:
                print(f"❌ 查询失败: {result.get('error', '未知错误')}")
                
        except Exception as e:
            print(f"❌ 异常: {str(e)}")
            import traceback
            traceback.print_exc()


if __name__ == "__main__":
    test_money_flow_fix()