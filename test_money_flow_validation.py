#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Money Flow Agent 测试用例验证脚本
验证测试用例的合理性和预期设置是否正确
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.money_flow_agent_modular import MoneyFlowAgentModular
from database.mysql_connector import MySQLConnector
import logging

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def validate_money_flow_test_cases():
    """验证Money Flow测试用例的预期是否正确"""
    print("\n" + "="*80)
    print("Money Flow Agent 测试用例验证")
    print("="*80)
    
    mysql_conn = MySQLConnector()
    agent = MoneyFlowAgentModular(mysql_conn)
    
    # 测试1：验证板块深度分析是否真的支持
    print("\n### 验证板块深度分析功能")
    print("-" * 60)
    
    sector_analysis_cases = [
        "分析银行板块的资金流向",
        "评估新能源板块的资金趋势",
        "研究白酒板块的主力行为",
    ]
    
    for query in sector_analysis_cases:
        print(f"\n测试查询: {query}")
        try:
            result = agent.query(query)
            success = result.get('success', False)
            if success:
                print(f"✅ 成功执行")
                # 检查结果是否包含板块分析内容
                result_str = str(result.get('result', ''))
                if '板块' in result_str and '资金' in result_str:
                    print("✅ 结果包含板块资金分析内容")
                else:
                    print("⚠️ 结果可能不完整")
            else:
                print(f"❌ 执行失败: {result.get('error', 'Unknown error')}")
        except Exception as e:
            print(f"❌ 异常: {str(e)}")
    
    # 测试2：验证板块简单查询是否正确路由到SQL
    print("\n\n### 验证板块简单查询路由")
    print("-" * 60)
    
    sql_route_cases = [
        "银行板块的主力资金",
        "新能源板块主力资金",
        "白酒板块资金流向",
    ]
    
    for query in sql_route_cases:
        print(f"\n测试查询: {query}")
        try:
            result = agent.query(query)
            success = result.get('success', False)
            error = result.get('error', '')
            
            if not success and '应该由SQL Agent处理' in error:
                print(f"✅ 正确识别为SQL查询")
            elif success:
                print(f"⚠️ 可能错误地处理了SQL查询")
            else:
                print(f"❌ 未识别查询类型: {error}")
        except Exception as e:
            print(f"❌ 异常: {str(e)}")
    
    # 测试3：验证个股深度分析
    print("\n\n### 验证个股深度分析功能")
    print("-" * 60)
    
    stock_analysis_cases = [
        "分析贵州茅台的资金流向",
        "评估平安银行的主力资金",
    ]
    
    for query in stock_analysis_cases:
        print(f"\n测试查询: {query}")
        try:
            result = agent.query(query)
            success = result.get('success', False)
            if success:
                print(f"✅ 成功执行")
                result_str = str(result.get('result', ''))
                # 检查关键内容
                keywords = ['主力资金', '超大单', '资金流向', '投资建议']
                found_keywords = [kw for kw in keywords if kw in result_str]
                if found_keywords:
                    print(f"✅ 包含关键内容: {found_keywords}")
                else:
                    print("⚠️ 可能缺少关键分析内容")
            else:
                print(f"❌ 执行失败: {result.get('error', 'Unknown error')}")
        except Exception as e:
            print(f"❌ 异常: {str(e)}")
    
    # 测试4：验证术语标准化
    print("\n\n### 验证术语标准化功能")
    print("-" * 60)
    
    term_cases = [
        ("分析贵州茅台的机构资金", "机构资金"),
        ("评估平安银行的游资", "游资"),
        ("研究比亚迪的散户资金", "散户资金"),
    ]
    
    for query, term in term_cases:
        print(f"\n测试查询: {query} (术语: {term})")
        try:
            result = agent.query(query)
            success = result.get('success', False)
            if success:
                print(f"✅ 成功执行")
                result_str = str(result.get('result', ''))
                if '术语提示' in result_str or '标准术语' in result_str:
                    print("✅ 包含术语标准化提示")
                else:
                    print("⚠️ 可能缺少术语提示")
            else:
                print(f"❌ 执行失败: {result.get('error', 'Unknown error')}")
        except Exception as e:
            print(f"❌ 异常: {str(e)}")
    
    print("\n\n" + "="*80)
    print("验证结论：")
    print("1. 板块深度分析功能是否正常？")
    print("2. 板块简单查询是否正确路由到SQL Agent？")
    print("3. 个股深度分析是否包含完整内容？")
    print("4. 术语标准化是否正常工作？")
    print("="*80)


if __name__ == "__main__":
    validate_money_flow_test_cases()