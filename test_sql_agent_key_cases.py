#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SQL Agent模块化版本关键测试用例
只测试最核心的功能
"""

import sys
import os
import time
from datetime import datetime

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.sql_agent_modular import SQLAgentModular

def test_key_cases():
    """测试关键用例"""
    agent = SQLAgentModular()
    
    # 关键测试用例
    test_cases = [
        # 股价查询
        ("贵州茅台的最新股价", "股价查询-最新"),
        ("600519.SH的股价", "股价查询-代码"),
        ("中国平安昨天的股价", "股价查询-昨天"),
        
        # 成交量查询
        ("平安银行昨天的成交量", "成交量查询"),
        ("万科A前天的成交量", "成交量查询-v2.1.17"),
        
        # 估值查询
        ("中国平安的市盈率", "估值查询-PE"),
        
        # K线查询
        ("贵州茅台最近10天的K线", "K线查询"),
        
        # 涨跌幅排名
        ("今天涨幅最大的前10只股票", "涨幅排名"),
        
        # 市值排名
        ("市值排名前3", "市值排名"),
        ("总市值排名", "市值排名-默认"),
        
        # 成交额排名
        ("成交额排名前10", "成交额排名"),
        
        # 主力资金
        ("贵州茅台的主力资金", "个股主力资金"),
        ("银行板块的主力资金", "板块主力资金"),
        
        # 错误测试
        ("茅台最新股价", "错误-股票简称"),
        ("", "错误-空查询"),
    ]
    
    success_count = 0
    fail_count = 0
    results = []
    
    print("="*80)
    print("SQL Agent模块化版本关键测试")
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
            if success:
                success_count += 1
                status = "✅ 成功"
                print(f"状态: {status}")
                print(f"耗时: {elapsed_time:.2f}秒")
                # 显示结果预览
                result_text = str(result.get('result', ''))
                if len(result_text) > 200:
                    print(f"结果: {result_text[:200]}...")
                else:
                    print(f"结果: {result_text}")
            else:
                # 如果是错误测试，期望失败
                if "错误" in test_name:
                    success_count += 1
                    status = "✅ 预期失败"
                else:
                    fail_count += 1
                    status = "❌ 失败"
                print(f"状态: {status}")
                print(f"错误: {result.get('error', '未知错误')}")
            
            results.append({
                'test_name': test_name,
                'query': query,
                'success': success,
                'status': status,
                'elapsed_time': elapsed_time,
                'error': result.get('error') if not success else None
            })
            
        except Exception as e:
            fail_count += 1
            elapsed_time = time.time() - start_time
            status = "❌ 异常"
            print(f"状态: {status}")
            print(f"异常: {str(e)}")
            
            results.append({
                'test_name': test_name,
                'query': query,
                'success': False,
                'status': status,
                'elapsed_time': elapsed_time,
                'error': str(e)
            })
    
    # 汇总报告
    print("\n" + "="*80)
    print("测试汇总")
    print("="*80)
    print(f"总测试数: {len(test_cases)}")
    print(f"成功数量: {success_count}")
    print(f"失败数量: {fail_count}")
    print(f"成功率: {success_count / len(test_cases) * 100:.1f}%")
    
    # 失败详情
    if fail_count > 0:
        print("\n失败测试:")
        for result in results:
            if "❌" in result['status']:
                print(f"- {result['test_name']}: {result['error']}")
    
    # 性能统计
    print("\n性能统计:")
    total_time = sum(r['elapsed_time'] for r in results)
    avg_time = total_time / len(results)
    print(f"总耗时: {total_time:.2f}秒")
    print(f"平均耗时: {avg_time:.2f}秒")
    
    # 快速路径统计
    quick_count = 0
    for result in results:
        if result['elapsed_time'] < 0.5:
            quick_count += 1
    print(f"快速响应(<0.5秒): {quick_count}/{len(results)} ({quick_count/len(results)*100:.1f}%)")


if __name__ == "__main__":
    test_key_cases()