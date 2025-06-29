#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试统一验证系统 - 验证所有Agent的验证逻辑一致性
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.financial_agent import FinancialAnalysisAgent
from agents.sql_agent import SQLAgent
from agents.money_flow_agent import MoneyFlowAgent


def test_unified_validation():
    """测试统一验证系统的一致性"""
    print("=" * 80)
    print("测试统一验证系统 - 验证所有Agent的验证逻辑一致性")
    print("=" * 80)
    
    # 初始化所有Agent
    try:
        print("初始化Agent...")
        financial_agent = FinancialAnalysisAgent()
        sql_agent = SQLAgent()
        money_flow_agent = MoneyFlowAgent()
        print("✅ 所有Agent初始化成功")
    except Exception as e:
        print(f"❌ Agent初始化失败: {e}")
        return
    
    # 测试用例 - 关键的验证测试
    test_cases = [
        # 正确的用例
        ("贵州茅台财务健康度", "✅应该成功"),
        ("600519财务健康度", "✅应该成功"),
        ("600519.SH财务健康度", "✅应该成功"),
        
        # 错误的用例
        ("茅台财务健康度", "❌应该失败-简称"),
        ("60051财务健康度", "❌应该失败-位数不对"),
        ("600519.XX财务健康度", "❌应该失败-错误后缀"),
        ("", "❌应该失败-空输入"),
        
        # 资金流向测试
        ("贵州茅台资金流向", "✅应该成功"),
        ("茅台资金流向", "❌应该失败-简称"),
        
        # SQL查询测试
        ("贵州茅台最新股价", "✅应该成功"),
        ("茅台最新股价", "❌应该失败-简称"),
    ]
    
    print(f"\n开始测试 {len(test_cases)} 个测试用例...")
    print("=" * 80)
    
    results = {}
    
    for i, (test_case, expectation) in enumerate(test_cases, 1):
        print(f"\n测试用例 {i:2d}: {test_case:<30} | 预期: {expectation}")
        print("-" * 80)
        
        # 测试Financial Agent
        try:
            financial_result = financial_agent.query(test_case)
            financial_success = financial_result.get('success', False)
            financial_error = financial_result.get('error', 'No error')
        except Exception as e:
            financial_success = False
            financial_error = f"异常: {str(e)}"
        
        # 测试SQL Agent（仅测试股票相关查询）
        stock_keywords = ['股价', '股票', '价格', '涨跌', '成交', '市值', '财务', '资金']
        is_stock_query = any(keyword in test_case for keyword in stock_keywords)
        
        if is_stock_query:
            try:
                sql_result = sql_agent.query(test_case)
                sql_success = sql_result.get('success', False)
                sql_error = sql_result.get('error', 'No error')
            except Exception as e:
                sql_success = False
                sql_error = f"异常: {str(e)}"
        else:
            sql_success = financial_success  # 非股票查询跳过
            sql_error = "非股票查询，跳过"
        
        # 测试Money Flow Agent（仅测试资金流向查询）
        money_flow_keywords = ['资金流向', '资金流入', '资金流出', '主力资金']
        is_money_flow_query = any(keyword in test_case for keyword in money_flow_keywords)
        
        if is_money_flow_query:
            try:
                money_flow_result = money_flow_agent.query(test_case)
                money_flow_success = money_flow_result.get('success', False)
                money_flow_error = money_flow_result.get('error', 'No error')
            except Exception as e:
                money_flow_success = False
                money_flow_error = f"异常: {str(e)}"
        else:
            money_flow_success = financial_success  # 非资金流向查询跳过
            money_flow_error = "非资金流向查询，跳过"
        
        # 显示结果
        print(f"  Financial Agent: {'✅' if financial_success else '❌'} - {financial_error if not financial_success else '成功'}")
        print(f"  SQL Agent:       {'✅' if sql_success else '❌'} - {sql_error if not sql_success else '成功'}")
        print(f"  MoneyFlow Agent: {'✅' if money_flow_success else '❌'} - {money_flow_error if not money_flow_success else '成功'}")
        
        # 检查一致性
        # 对于股票查询，Financial和SQL应该一致
        # 对于资金流向查询，Financial和MoneyFlow应该一致
        consistency_check = True
        if is_stock_query and financial_success != sql_success:
            print(f"  ⚠️  警告: Financial Agent和SQL Agent结果不一致!")
            consistency_check = False
        
        if is_money_flow_query and financial_success != money_flow_success:
            print(f"  ⚠️  警告: Financial Agent和MoneyFlow Agent结果不一致!")
            consistency_check = False
        
        if consistency_check:
            print(f"  ✅ 一致性检查通过")
        
        # 记录结果
        results[test_case] = {
            'expectation': expectation,
            'financial': {'success': financial_success, 'error': financial_error},
            'sql': {'success': sql_success, 'error': sql_error},
            'money_flow': {'success': money_flow_success, 'error': money_flow_error},
            'consistent': consistency_check
        }
    
    # 总结报告
    print("\n" + "=" * 80)
    print("统一验证测试总结报告")
    print("=" * 80)
    
    should_succeed = [case for case, exp in test_cases if "✅应该成功" in exp]
    should_fail = [case for case, exp in test_cases if "❌应该失败" in exp]
    
    print(f"\n应该成功的用例 ({len(should_succeed)}个):")
    for case in should_succeed:
        result = results[case]
        financial_ok = result['financial']['success']
        status = "✅ 正确" if financial_ok else "❌ 错误"
        print(f"  {status} | {case}")
    
    print(f"\n应该失败的用例 ({len(should_fail)}个):")
    for case in should_fail:
        result = results[case]
        financial_ok = not result['financial']['success']  # 应该失败
        status = "✅ 正确" if financial_ok else "❌ 错误"
        print(f"  {status} | {case}")
    
    # 一致性统计
    consistent_count = sum(1 for r in results.values() if r['consistent'])
    consistency_rate = consistent_count / len(test_cases) * 100
    
    print(f"\n📊 验证一致性统计:")
    print(f"  一致性用例: {consistent_count}/{len(test_cases)} ({consistency_rate:.1f}%)")
    
    if consistency_rate == 100:
        print("  🎉 所有Agent验证逻辑完全一致!")
    else:
        print("  ⚠️  存在验证逻辑不一致的情况，需要进一步调整")
    
    return results


if __name__ == "__main__":
    test_unified_validation()