#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试财务分析修复

运行方式：
- Windows: venv\\Scripts\\activate && python test_financial_fix.py
- Linux/Mac: source venv/bin/activate && python test_financial_fix.py
"""
import sys
import os

# 检查是否在虚拟环境中
if not hasattr(sys, 'real_prefix') and not (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
    print("警告：请先激活虚拟环境再运行此脚本！")
    print("Windows: venv\\Scripts\\activate")
    print("Linux/Mac: source venv/bin/activate")
    sys.exit(1)

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.financial_agent import FinancialAnalysisAgent
from utils.stock_code_mapper import convert_to_ts_code

def test_stock_mapper():
    """测试股票代码映射器"""
    print("=" * 60)
    print("测试股票代码映射器")
    print("=" * 60)
    
    test_cases = [
        "贵州茅台",
        "国轩高科",  
        "002047",
        "002047.SZ",
        "002074",  # 国轩高科的代码
    ]
    
    for case in test_cases:
        result = convert_to_ts_code(case)
        print(f"{case:15} -> {result}")
    print()

def test_financial_analysis():
    """测试财务分析功能"""
    print("=" * 60)
    print("测试财务分析功能")
    print("=" * 60)
    
    agent = FinancialAnalysisAgent()
    
    # 正常测试用例
    normal_test_queries = [
        "分析贵州茅台的财务健康度",
        "分析国轩高科的财务健康度",
        "分析002047的财务健康度",
        "分析002047.SZ的财务健康度",
        "分析药明康德的财务健康度",
        "分析301120的财务健康度",
        "分析301120.SZ的财务健康度",
    ]
    
    # 破坏性测试用例
    error_test_queries = [
        "分析02359的财务健康度",  # 5位数字
        "分析1234567的财务健康度",  # 7位数字
        "分析999999.BJ的财务健康度",  # 不存在的股票
        "分析000000.SX的财务健康度",  # 错误的后缀
        "分析就不告诉你的财务健康度",  # 无效输入
        "分析建设的财务健康度",  # 不完整的公司名称
        "分析建行的财务健康度",  # 简称
    ]
    
    print("\n### 正常测试用例 ###")
    for query in normal_test_queries:
        print(f"\n查询: {query}")
        print("-" * 40)
        
        result = agent.query(query)
        
        if result['success']:
            print(f"✓ 成功 - 股票代码: {result.get('ts_code')}")
            if 'health_score' in result:
                score = result['health_score']
                print(f"  财务健康度: {score['total_score']}分 ({score['rating']}级)")
        else:
            print(f"✗ 失败 - 错误: {result.get('error')}")
    
    print("\n\n### 破坏性测试用例 ###")
    for query in error_test_queries:
        print(f"\n查询: {query}")
        print("-" * 40)
        
        result = agent.query(query)
        
        if result['success']:
            print(f"✓ 成功 - 股票代码: {result.get('ts_code')}")
        else:
            print(f"✓ 正确拒绝 - 错误提示: {result.get('error')}")

if __name__ == "__main__":
    test_stock_mapper()
    test_financial_analysis()