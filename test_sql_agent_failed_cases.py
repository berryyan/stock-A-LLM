#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SQL Agent失败用例专项测试
专注于当前失败的测试场景
"""

import sys
import os
import time
from datetime import datetime

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.sql_agent_modular import SQLAgentModular


def test_failed_cases():
    """测试当前失败的用例"""
    agent = SQLAgentModular()
    
    # 失败的测试用例
    test_cases = [
        # 1. 板块主力资金（数据问题）
        ("银行板块的主力资金", "板块主力资金"),
        
        # 2. LLM查询（AgentFinish错误）
        ("三六零的市值", "特殊股票市值查询"),
        ("比较贵州茅台和五粮液", "多股票比较"),
        ("贵州茅台的市盈率", "估值指标查询"),
        ("市值排名前10", "市值排名"),
        ("涨幅最大的前10只股票", "涨幅排名"),
    ]
    
    results = {
        'total': len(test_cases),
        'passed': 0,
        'failed': 0,
        'errors': []
    }
    
    print("="*80)
    print("SQL Agent失败用例专项测试")
    print(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80)
    
    for i, (query, test_name) in enumerate(test_cases, 1):
        print(f"\n[{i}/{len(test_cases)}] 测试: {test_name}")
        print(f"查询: {query}")
        print("-"*40)
        
        start_time = time.time()
        try:
            result = agent.query(query)
            elapsed_time = time.time() - start_time
            
            success = result.get('success', False)
            
            if success:
                results['passed'] += 1
                status = "✅ 成功"
                # 打印部分结果
                result_text = str(result.get('result', ''))
                if len(result_text) > 200:
                    print(f"结果预览: {result_text[:200]}...")
                else:
                    print(f"结果: {result_text}")
            else:
                results['failed'] += 1
                status = "❌ 失败"
                error_msg = result.get('error', '未知错误')
                print(f"错误: {error_msg}")
                results['errors'].append({
                    'test': test_name,
                    'query': query,
                    'error': error_msg
                })
            
            print(f"状态: {status}")
            print(f"耗时: {elapsed_time:.2f}秒")
            
            # 如果是LLM查询，打印更多调试信息
            if 'LLM' in str(result.get('error', '')):
                print(f"调试信息: {result}")
                
        except Exception as e:
            elapsed_time = time.time() - start_time
            results['failed'] += 1
            print(f"异常: {str(e)}")
            print(f"耗时: {elapsed_time:.2f}秒")
            results['errors'].append({
                'test': test_name,
                'query': query,
                'error': f"异常: {str(e)}"
            })
    
    # 汇总报告
    print("\n" + "="*80)
    print("测试汇总")
    print("="*80)
    print(f"总测试数: {results['total']}")
    print(f"通过数量: {results['passed']}")
    print(f"失败数量: {results['failed']}")
    print(f"通过率: {results['passed'] / results['total'] * 100:.1f}%")
    
    if results['errors']:
        print("\n失败详情:")
        for error in results['errors']:
            print(f"- {error['test']}: {error['error']}")


if __name__ == "__main__":
    test_failed_cases()