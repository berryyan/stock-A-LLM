#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SQL Agent 回归测试
确保板块功能增强没有破坏其他功能
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.sql_agent_modular import SQLAgentModular
import logging

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def test_sql_agent_no_regression():
    """测试SQL Agent确保没有功能退化"""
    print("\n" + "="*80)
    print("SQL Agent 回归测试")
    print("="*80)
    
    # 测试用例分类
    test_categories = {
        "股价查询": [
            ("贵州茅台的股价", True),
            ("中国平安最新股价", True),
            ("600519.SH的股价", True),
            ("比亚迪昨天的股价", True),
        ],
        "板块查询（增强后）": [
            ("银行板块的主力资金", True),
            ("BK0475.DC的主力资金", True),  # 新增支持
            ("BK1036.DC今天的主力资金", True),  # 新增支持
            ("银行的主力资金", False),  # 应该失败
        ],
        "排名查询": [
            ("涨幅排名前10", True),
            ("市值排名前5", True),
            ("主力净流入排名", True),
            ("PE最低的10只股票", True),
        ],
        "财务查询": [
            ("贵州茅台的净利润", True),
            ("万科A的营收", True),
            ("中国平安2024年的利润", True),
        ],
        "K线查询": [
            ("贵州茅台最近5天的K线", True),
            ("比亚迪最近一个月的走势", True),
        ],
        "成交量查询": [
            ("贵州茅台的成交量", True),
            ("中国平安昨天的成交量", True),
        ]
    }
    
    # 初始化Agent
    agent = SQLAgentModular()
    
    # 统计结果
    total_passed = 0
    total_failed = 0
    category_results = {}
    
    # 执行测试
    for category, test_cases in test_categories.items():
        print(f"\n\n### {category}")
        print("-" * 60)
        
        passed = 0
        failed = 0
        
        for query, expected_success in test_cases:
            print(f"\n查询: {query}")
            print(f"预期: {'成功' if expected_success else '失败'}")
            
            try:
                result = agent.query(query)
                actual_success = result.get('success', False)
                
                if actual_success == expected_success:
                    print(f"结果: ✅ 符合预期")
                    passed += 1
                    total_passed += 1
                else:
                    print(f"结果: ❌ 不符合预期")
                    print(f"  实际: {'成功' if actual_success else '失败'}")
                    if not actual_success:
                        print(f"  错误: {result.get('error', 'Unknown')}")
                    failed += 1
                    total_failed += 1
                    
            except Exception as e:
                print(f"结果: ❌ 异常")
                print(f"  异常: {str(e)}")
                failed += 1
                total_failed += 1
        
        category_results[category] = {
            'passed': passed,
            'failed': failed,
            'total': len(test_cases)
        }
        
        print(f"\n{category}小结: {passed}/{len(test_cases)} 通过")
    
    # 总结报告
    print("\n\n" + "="*80)
    print("测试总结")
    print("="*80)
    
    for category, results in category_results.items():
        success_rate = results['passed'] / results['total'] * 100
        status = "✅" if results['failed'] == 0 else "⚠️"
        print(f"{status} {category}: {results['passed']}/{results['total']} ({success_rate:.0f}%)")
    
    print(f"\n总体结果: {total_passed}/{total_passed + total_failed} 通过")
    
    # 判断是否有回归
    if total_failed == 0:
        print("\n✅ 没有功能退化，所有测试通过！")
    else:
        print(f"\n⚠️ 发现 {total_failed} 个测试失败，请检查是否有功能退化。")
    
    # 特别检查板块功能
    sector_results = category_results.get("板块查询（增强后）", {})
    if sector_results.get('passed', 0) == sector_results.get('total', 0):
        print("\n✅ 板块功能增强成功，没有破坏原有功能！")
    
    return total_failed == 0


if __name__ == "__main__":
    test_sql_agent_no_regression()