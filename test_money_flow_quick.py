#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Money Flow Agent 快速测试
验证核心功能是否正常
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.money_flow_agent_modular import MoneyFlowAgentModular


def quick_test():
    """运行Money Flow Agent快速测试"""
    print("\nMoney Flow Agent 快速测试")
    print("=" * 50)
    
    agent = MoneyFlowAgentModular()
    
    # 核心测试用例
    test_cases = [
        ("贵州茅台的主力资金", "个股主力资金"),
        ("主力资金净流入前10", "资金排名"),
        ("银行板块的主力资金", "板块资金"),
        ("分析比亚迪的资金流向", "资金流向分析"),
        ("宁德时代的超大单资金", "超大单查询"),
    ]
    
    passed = 0
    failed = 0
    
    for query, test_name in test_cases:
        print(f"\n测试{passed + failed + 1}: {test_name}")
        print(f"查询: {query}")
        
        try:
            result = agent.query(query)
            if result.get('success'):
                print("✅ 通过")
                passed += 1
            else:
                print(f"❌ 失败: {result.get('error')}")
                failed += 1
        except Exception as e:
            print(f"❌ 异常: {str(e)}")
            failed += 1
    
    print(f"\n{'='*50}")
    print(f"测试总结: {passed}/{len(test_cases)} 通过")
    print(f"通过率: {passed/len(test_cases)*100:.1f}%")
    
    # 期望100%通过
    return passed == len(test_cases)


if __name__ == "__main__":
    success = quick_test()
    exit(0 if success else 1)