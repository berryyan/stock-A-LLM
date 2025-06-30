#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
SQL Agent快速路由诊断脚本
测试各个模板的快速路由是否正常工作
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.sql_agent import SQLAgent
from utils.query_templates import match_query_template
from utils.logger import setup_logger
import time
from datetime import datetime

logger = setup_logger("sql_quick_route_test")

def test_quick_route():
    """测试SQL Agent的快速路由功能"""
    
    # 初始化SQL Agent
    sql_agent = SQLAgent()
    
    # 测试用例
    test_cases = [
        # 股价查询（已实现快速路由）
        {"query": "贵州茅台最新股价", "expected": "股价查询"},
        {"query": "平安银行昨天的股价", "expected": "股价查询"},
        
        # K线查询（应该触发快速路由）
        {"query": "贵州茅台最近30天的K线", "expected": "K线查询"},
        {"query": "平安银行从2025-06-01到2025-06-27的走势", "expected": "K线查询"},
        
        # 成交量查询（应该触发快速路由）
        {"query": "茅台昨天的成交量", "expected": "成交量查询"},
        {"query": "平安银行最新成交额", "expected": "成交量查询"},
        
        # 利润查询（应该触发快速路由）
        {"query": "贵州茅台的净利润", "expected": "利润查询"},
        {"query": "平安银行的营业收入", "expected": "利润查询"},
        
        # 估值指标查询（应该触发快速路由）
        {"query": "贵州茅台的市盈率", "expected": "估值指标查询"},
        {"query": "平安银行最新PE", "expected": "估值指标查询"},
        {"query": "茅台的市净率", "expected": "估值指标查询"},
        
        # 涨跌幅排名（应该触发快速路由）
        {"query": "今天涨幅前10", "expected": "涨跌幅排名"},
        {"query": "昨天跌幅最大的5只股票", "expected": "涨跌幅排名"},
        
        # 市值排名（应该触发快速路由）
        {"query": "总市值前10", "expected": "总市值排名"},
        {"query": "市值最大的前20只股票", "expected": "总市值排名"},
        {"query": "流通市值前10", "expected": "流通市值排名"},
        
        # 主力净流入（应该触发快速路由）
        {"query": "今天主力净流入排行前10", "expected": "主力净流入排行"},
        {"query": "茅台的主力净流入", "expected": "主力净流入排行"},
        
        # 板块查询（应该触发快速路由）
        {"query": "银行板块的股票", "expected": None},  # 暂未实现
        {"query": "白酒行业的成分股", "expected": None},  # 暂未实现
    ]
    
    results = []
    
    print("\n=== SQL Agent快速路由诊断 ===\n")
    
    for case in test_cases:
        query = case["query"]
        expected = case["expected"]
        
        print(f"\n测试查询: {query}")
        print(f"期望模板: {expected}")
        
        # 1. 测试模板匹配
        template_match = match_query_template(query)
        if template_match:
            template, params = template_match
            print(f"匹配到模板: {template.name}")
            print(f"路由类型: {template.route_type}")
            print(f"提取参数: {params}")
        else:
            print("未匹配到任何模板")
        
        # 2. 测试_try_quick_query方法
        start_time = time.time()
        quick_result = sql_agent._try_quick_query(query)
        elapsed_time = time.time() - start_time
        
        if quick_result and quick_result.get('success'):
            print(f"✅ 快速路由成功！耗时: {elapsed_time:.3f}秒")
            print(f"结果预览: {quick_result['result'][:100]}...")
            
            results.append({
                "query": query,
                "template": template.name if template_match else None,
                "success": True,
                "time": elapsed_time,
                "quick_path": True
            })
        else:
            print(f"❌ 快速路由失败或未实现")
            
            # 尝试完整查询看是否能成功
            print("尝试完整查询...")
            start_time = time.time()
            full_result = sql_agent.query(query)
            elapsed_time = time.time() - start_time
            
            if full_result.get('success'):
                print(f"完整查询成功，耗时: {elapsed_time:.3f}秒")
            else:
                print(f"完整查询也失败: {full_result.get('error')}")
            
            results.append({
                "query": query,
                "template": template.name if template_match else None,
                "success": full_result.get('success', False),
                "time": elapsed_time,
                "quick_path": False
            })
        
        print("-" * 60)
    
    # 打印总结
    print("\n\n=== 测试总结 ===\n")
    print(f"总测试数: {len(results)}")
    
    quick_count = sum(1 for r in results if r['quick_path'])
    print(f"快速路由成功: {quick_count}")
    print(f"快速路由失败: {len(results) - quick_count}")
    
    print("\n快速路由详情:")
    for r in results:
        status = "✅ 快速" if r['quick_path'] else "❌ 完整"
        print(f"{status} | {r['query'][:30]:30s} | {r['time']:.3f}s | 模板: {r['template']}")
    
    # 找出问题
    print("\n\n=== 问题分析 ===\n")
    
    failed_quick = [r for r in results if not r['quick_path'] and r['template']]
    if failed_quick:
        print("以下查询匹配到模板但未触发快速路由:")
        for r in failed_quick:
            print(f"- {r['query']} (模板: {r['template']})")
    
    no_template = [r for r in results if not r['template']]
    if no_template:
        print("\n以下查询未匹配到任何模板:")
        for r in no_template:
            print(f"- {r['query']}")


if __name__ == "__main__":
    test_quick_route()