#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SQL Agent模块化版本核心测试脚本
测试最重要的功能
"""

import sys
import os
import time
from datetime import datetime

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.sql_agent_modular import SQLAgentModular


def test_essential():
    """测试核心功能"""
    agent = SQLAgentModular()
    
    # 核心测试用例
    test_cases = [
        # 1. 股价查询（快速路径）
        ("贵州茅台的最新股价", "股价查询-快速"),
        ("600519.SH的股价", "股价查询-代码"),
        
        # 2. 成交量查询（快速路径）
        ("平安银行昨天的成交量", "成交量查询"),
        
        # 3. K线查询（快速路径）
        ("贵州茅台最近10天的K线", "K线查询"),
        
        # 4. 成交额排名（快速路径）
        ("成交额排名前10", "成交额排名"),
        
        # 5. 主力资金（快速路径）
        ("贵州茅台的主力资金", "个股主力资金"),
        ("银行板块的主力资金", "板块主力资金"),
        
        # 6. 特殊股票名称
        ("TCL科技的股价", "特殊股票-TCL"),
        ("三六零的市值", "特殊股票-数字"),
        ("万科A的股价", "特殊股票-A后缀"),
        
        # 7. 参数提取边界
        ("比较贵州茅台和五粮液", "多股票提取"),
        ("贵州茅台3年前的股价", "N年前日期"),
        
        # 8. 错误处理
        ("茅台最新股价", "错误-股票简称"),
        ("", "错误-空查询"),
        
        # 9. 复杂查询（LLM路径）
        ("贵州茅台的市盈率", "估值查询-PE"),
        ("市值排名前10", "市值排名"),
        ("涨幅最大的前10只股票", "涨幅排名"),
    ]
    
    results = {
        'total': len(test_cases),
        'passed': 0,
        'failed': 0,
        'fast_queries': 0,
        'errors': []
    }
    
    print("="*80)
    print("SQL Agent模块化版本核心测试")
    print(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80)
    
    for query, test_name in test_cases:
        print(f"\n测试: {test_name}")
        print(f"查询: {query}")
        print("-"*40)
        
        start_time = time.time()
        try:
            result = agent.query(query)
            elapsed_time = time.time() - start_time
            
            success = result.get('success', False)
            
            # 错误测试用例的特殊处理
            if "错误" in test_name:
                # 错误测试应该返回失败
                if not success:
                    results['passed'] += 1
                    status = "✅ 预期失败"
                else:
                    results['failed'] += 1
                    status = "❌ 应该失败但成功了"
                    results['errors'].append({
                        'test': test_name,
                        'query': query,
                        'error': '错误测试未能触发错误'
                    })
            else:
                # 正常测试应该成功
                if success:
                    results['passed'] += 1
                    status = "✅ 成功"
                else:
                    results['failed'] += 1
                    status = "❌ 失败"
                    results['errors'].append({
                        'test': test_name,
                        'query': query,
                        'error': result.get('error', '未知错误')
                    })
            
            # 统计快速查询
            if elapsed_time < 0.5:
                results['fast_queries'] += 1
            
            print(f"状态: {status}")
            print(f"耗时: {elapsed_time:.2f}秒")
            
            if success and result.get('result'):
                result_text = str(result.get('result', ''))
                if len(result_text) > 100:
                    print(f"结果: {result_text[:100]}...")
                else:
                    print(f"结果: {result_text}")
            elif not success and "错误" not in test_name:
                print(f"错误: {result.get('error', '未知错误')}")
                
        except Exception as e:
            elapsed_time = time.time() - start_time
            results['failed'] += 1
            status = "❌ 异常"
            print(f"状态: {status}")
            print(f"异常: {str(e)}")
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
    print(f"快速查询: {results['fast_queries']}/{results['total']} "
          f"({results['fast_queries']/results['total']*100:.1f}%)")
    
    # 失败详情
    if results['errors']:
        print("\n失败测试:")
        for error in results['errors']:
            print(f"- {error['test']}: {error['error']}")


if __name__ == "__main__":
    test_essential()