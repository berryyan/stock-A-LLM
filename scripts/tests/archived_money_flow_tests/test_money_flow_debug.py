#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Money Flow Agent 调试脚本
用于调试板块查询问题
"""
import sys
sys.path.append('.')

from agents.money_flow_agent_modular import MoneyFlowAgentModular
from utils.parameter_extractor import ParameterExtractor

def test_sector_query():
    """测试板块查询参数提取"""
    print("="*60)
    print("测试板块查询参数提取")
    print("="*60)
    
    # 初始化参数提取器
    extractor = ParameterExtractor()
    
    # 测试查询
    test_queries = [
        "银行板块的主力资金",
        "新能源板块的主力资金",
        "白酒板块主力资金",
        "房地产板块资金流向"
    ]
    
    for query in test_queries:
        print(f"\n查询: {query}")
        params = extractor.extract_all_params(query)
        print(f"提取的参数:")
        print(f"  - stocks: {params.stocks}")
        print(f"  - stock_names: {params.stock_names}")
        print(f"  - sector: {params.sector}")
        print(f"  - error: {params.error}")
        
        # 如果没有提取到板块，尝试直接使用Money Flow Agent
        if not params.sector:
            print("\n使用Money Flow Agent测试:")
            agent = MoneyFlowAgentModular()
            result = agent.query(query)
            print(f"  - success: {result.get('success')}")
            print(f"  - error: {result.get('error')}")
            if result.get('success'):
                print(f"  - result preview: {str(result.get('result'))[:100]}...")

def test_ranking_query():
    """测试排名查询"""
    print("\n" + "="*60)
    print("测试排名查询")
    print("="*60)
    
    agent = MoneyFlowAgentModular()
    
    test_queries = [
        "主力净流入最多的前10只股票",
        "主力净流入排名",
        "主力净流出排名前20"
    ]
    
    for query in test_queries:
        print(f"\n查询: {query}")
        result = agent.query(query)
        print(f"  - success: {result.get('success')}")
        print(f"  - error: {result.get('error')}")
        if result.get('success'):
            print(f"  - result preview: {str(result.get('result'))[:100]}...")

def test_non_standard_terms():
    """测试非标准术语"""
    print("\n" + "="*60)
    print("测试非标准术语")
    print("="*60)
    
    agent = MoneyFlowAgentModular()
    
    test_queries = [
        "贵州茅台的机构资金",
        "平安银行的大资金流入",
        "万科A的游资"
    ]
    
    for query in test_queries:
        print(f"\n查询: {query}")
        result = agent.query(query)
        print(f"  - success: {result.get('success')}")
        print(f"  - 期望: 失败（非标准术语）")
        print(f"  - error: {result.get('error')}")
        if result.get('success'):
            # 检查是否有术语转换提示
            result_str = str(result.get('result', ''))
            if '术语提示' in result_str:
                print(f"  - 包含术语转换提示")

if __name__ == "__main__":
    test_sector_query()
    test_ranking_query()
    test_non_standard_terms()