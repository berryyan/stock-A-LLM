#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SQL Agent 快速测试
验证核心功能是否正常
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.sql_agent_modular import SQLAgentModular


def quick_test():
    """运行SQL Agent快速测试"""
    print("\nSQL Agent 快速测试")
    print("=" * 50)
    
    agent = SQLAgentModular()
    
    # 核心测试用例
    test_cases = [
        ("贵州茅台的股价", "股价查询"),
        ("今天涨幅前10的股票", "排名查询"),
        ("万科A的成交量", "成交量查询"),
        ("比亚迪的市值", "市值查询"),
        ("中国平安最近5天的K线", "K线查询"),
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