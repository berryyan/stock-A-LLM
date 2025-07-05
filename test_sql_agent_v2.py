#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试SQL Agent V2模块化版本
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.sql_agent_v2 import SQLAgentV2
from utils.logger import setup_logger
import time

logger = setup_logger("test_sql_agent_v2")


def test_queries():
    """测试各种查询"""
    # 初始化SQL Agent V2
    agent = SQLAgentV2()
    
    # 测试用例
    test_cases = [
        # 股价查询
        "贵州茅台的最新股价",
        "比亚迪昨天的股价是多少",
        
        # 市值排名
        "市值排名前5",
        "A股市值最大的10家公司",
        
        # K线查询
        "贵州茅台最近30天的K线",
        "宁德时代本月的走势",
        
        # 成交量查询
        "中国平安今天的成交量",
        
        # 财务数据查询
        "贵州茅台的财务数据",
        "伊利股份的净利润",
        
        # 涨跌幅排名
        "今天涨幅最大的10只股票",
        
        # PE排名
        "PE最低的5只股票",
        
        # 资金流向
        "贵州茅台的主力资金",
        "银行板块的主力资金",
        
        # 错误测试
        "不存在的股票XXXXX的股价",
        "",  # 空查询
        "茅台",  # 不完整的股票名称
    ]
    
    results = []
    
    for i, query in enumerate(test_cases, 1):
        print(f"\n{'='*60}")
        print(f"测试 {i}/{len(test_cases)}: {query}")
        print('='*60)
        
        start_time = time.time()
        
        try:
            result = agent.query(query)
            elapsed_time = time.time() - start_time
            
            print(f"成功: {result.get('success', False)}")
            print(f"耗时: {elapsed_time:.2f}秒")
            print(f"快速路径: {result.get('quick_path', False)}")
            
            if result.get('success'):
                print("结果:")
                print(result.get('result', '无结果'))
            else:
                print(f"错误: {result.get('error', '未知错误')}")
            
            results.append({
                'query': query,
                'success': result.get('success', False),
                'time': elapsed_time,
                'quick_path': result.get('quick_path', False),
                'error': result.get('error') if not result.get('success') else None
            })
            
        except Exception as e:
            print(f"异常: {str(e)}")
            results.append({
                'query': query,
                'success': False,
                'time': time.time() - start_time,
                'quick_path': False,
                'error': str(e)
            })
    
    # 打印测试总结
    print(f"\n{'='*60}")
    print("测试总结")
    print('='*60)
    
    success_count = sum(1 for r in results if r['success'])
    quick_count = sum(1 for r in results if r['quick_path'])
    avg_time = sum(r['time'] for r in results) / len(results)
    
    print(f"总测试数: {len(test_cases)}")
    print(f"成功数: {success_count} ({success_count/len(test_cases)*100:.1f}%)")
    print(f"快速路径数: {quick_count} ({quick_count/len(test_cases)*100:.1f}%)")
    print(f"平均耗时: {avg_time:.2f}秒")
    
    print("\n失败的查询:")
    for r in results:
        if not r['success']:
            print(f"- {r['query']}: {r['error']}")


def test_specific_template():
    """测试特定模板的参数提取和验证"""
    agent = SQLAgentV2()
    
    print("\n测试参数提取器:")
    
    test_query = "比较贵州茅台、五粮液和泸州老窖的市值"
    params = agent.param_extractor.extract_all_params(test_query)
    
    print(f"查询: {test_query}")
    print(f"提取的股票: {params.stocks}")
    print(f"股票名称: {params.stock_names}")
    print(f"错误: {params.error}")


if __name__ == "__main__":
    print("开始测试SQL Agent V2...")
    
    # 测试参数提取
    test_specific_template()
    
    # 测试各种查询
    test_queries()
    
    print("\n测试完成！")