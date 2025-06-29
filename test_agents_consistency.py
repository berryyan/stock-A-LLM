#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试Agent验证逻辑一致性 - 只验证关键测试用例
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.financial_agent import FinancialAnalysisAgent
from agents.sql_agent import SQLAgent
from agents.money_flow_agent import MoneyFlowAgent
import logging

# 设置日志级别为ERROR，减少输出
logging.getLogger().setLevel(logging.ERROR)


def test_agents_consistency():
    """测试三个Agent的验证逻辑一致性"""
    print("=" * 80)
    print("测试Agent验证逻辑一致性")
    print("=" * 80)
    
    # 初始化Agent
    try:
        print("初始化Agent...")
        financial_agent = FinancialAnalysisAgent()
        sql_agent = SQLAgent()
        money_flow_agent = MoneyFlowAgent()
        print("✅ 所有Agent初始化成功\n")
    except Exception as e:
        print(f"❌ Agent初始化失败: {e}")
        return
    
    # 关键测试用例
    test_cases = [
        # 成功案例
        ("贵州茅台财务健康度", True, "financial"),
        ("600519最新股价", True, "sql"),
        ("贵州茅台资金流向", True, "money_flow"),
        
        # 失败案例（简称）
        ("茅台财务健康度", False, "financial"),
        ("茅台最新股价", False, "sql"),
        ("茅台资金流向", False, "money_flow"),
        
        # 失败案例（错误代码）
        ("123456.SH财务健康度", False, "financial"),
        ("123456.SH最新股价", False, "sql"),
        ("123456.SH资金流向", False, "money_flow"),
    ]
    
    results = []
    
    for test_case, should_succeed, agent_type in test_cases:
        print(f"测试: {test_case:<30} (预期: {'成功' if should_succeed else '失败'})")
        
        # 根据类型选择Agent
        if agent_type == "financial":
            try:
                result = financial_agent.query(test_case)
                success = result.get('success', False)
                error = result.get('error', '')
            except Exception as e:
                success = False
                error = str(e)
        
        elif agent_type == "sql":
            try:
                result = sql_agent.query(test_case)
                success = result.get('success', False)
                error = result.get('error', '')
            except Exception as e:
                success = False
                error = str(e)
        
        elif agent_type == "money_flow":
            try:
                result = money_flow_agent.query(test_case)
                success = result.get('success', False)
                error = result.get('error', '')
            except Exception as e:
                success = False
                error = str(e)
        
        # 判断结果
        is_correct = (success == should_succeed)
        status = "✅ 正确" if is_correct else "❌ 错误"
        
        if success:
            print(f"  {status} - 查询成功")
        else:
            print(f"  {status} - 查询失败: {error[:50]}...")
        
        results.append({
            'test_case': test_case,
            'agent_type': agent_type,
            'should_succeed': should_succeed,
            'actual_success': success,
            'is_correct': is_correct
        })
        print()
    
    # 统计结果
    print("=" * 80)
    print("测试结果统计")
    print("=" * 80)
    
    correct_count = sum(1 for r in results if r['is_correct'])
    total_count = len(results)
    
    print(f"\n总测试用例: {total_count}")
    print(f"通过测试: {correct_count}")
    print(f"失败测试: {total_count - correct_count}")
    print(f"通过率: {correct_count/total_count*100:.1f}%")
    
    if correct_count == total_count:
        print("\n🎉 所有Agent验证逻辑完全一致！")
    else:
        print("\n⚠️  存在验证逻辑不一致的情况：")
        for r in results:
            if not r['is_correct']:
                print(f"  - {r['test_case']} ({r['agent_type']})")


if __name__ == "__main__":
    test_agents_consistency()