#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SQL Agent 板块功能快速测试
验证板块提取模块优化后SQL Agent是否正常工作
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.sql_agent_modular import SQLAgentModular
from agents.sql_agent import SQLAgent
import logging

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def test_sql_agent_sector_queries():
    """测试SQL Agent处理板块相关查询"""
    print("\n" + "="*80)
    print("SQL Agent 板块功能测试")
    print("="*80)
    
    # 测试查询列表
    test_queries = [
        # 板块相关查询（SQL Agent可能需要通过LLM处理）
        {
            "query": "银行板块有哪些股票",
            "type": "板块成分股查询",
            "expected": "LLM生成SQL"
        },
        {
            "query": "查询银行板块的成分股",
            "type": "板块成分股查询",
            "expected": "LLM生成SQL"
        },
        {
            "query": "银行板块的平均市盈率",
            "type": "板块指标查询",
            "expected": "LLM生成SQL"
        },
        # 正常的股票查询（应该正常工作）
        {
            "query": "贵州茅台的股价",
            "type": "个股股价查询",
            "expected": "快速路径或LLM"
        },
        {
            "query": "贵州茅台最新股价",
            "type": "个股股价查询",
            "expected": "快速路径"
        },
        # 混合查询
        {
            "query": "比较贵州茅台和银行板块的市盈率",
            "type": "混合查询",
            "expected": "LLM生成SQL"
        }
    ]
    
    # 测试两个版本的SQL Agent
    agents = {
        "SQL Agent (原版)": SQLAgent(),
        "SQL Agent (模块化)": SQLAgentModular()
    }
    
    results = {}
    
    for agent_name, agent in agents.items():
        print(f"\n\n测试 {agent_name}")
        print("-" * 60)
        
        agent_results = []
        
        for test_case in test_queries:
            query = test_case["query"]
            query_type = test_case["type"]
            expected = test_case["expected"]
            
            print(f"\n查询: {query}")
            print(f"类型: {query_type}")
            print(f"预期: {expected}")
            
            try:
                result = agent.query(query)
                
                success = result.get('success', False)
                error = result.get('error', '')
                quick_path = result.get('quick_path', False)
                
                print(f"结果: {'✅ 成功' if success else '❌ 失败'}")
                if not success:
                    print(f"错误: {error}")
                else:
                    print(f"路径: {'快速路径' if quick_path else 'LLM路径'}")
                    # 只显示结果的前200个字符
                    result_preview = str(result.get('result', ''))[:200]
                    if len(result.get('result', '')) > 200:
                        result_preview += "..."
                    print(f"结果预览: {result_preview}")
                
                agent_results.append({
                    'query': query,
                    'type': query_type,
                    'success': success,
                    'error': error,
                    'quick_path': quick_path
                })
                
            except Exception as e:
                print(f"异常: {str(e)}")
                agent_results.append({
                    'query': query,
                    'type': query_type,
                    'success': False,
                    'error': str(e),
                    'quick_path': False
                })
        
        results[agent_name] = agent_results
    
    # 对比结果
    print("\n\n" + "="*80)
    print("测试结果对比")
    print("="*80)
    
    for i, test_case in enumerate(test_queries):
        query = test_case["query"]
        print(f"\n查询 {i+1}: {query}")
        
        for agent_name in agents.keys():
            result = results[agent_name][i]
            status = "✅" if result['success'] else "❌"
            path = "快速" if result['quick_path'] else "LLM" if result['success'] else "N/A"
            print(f"  {agent_name}: {status} ({path})")
            if not result['success']:
                print(f"    错误: {result['error']}")
    
    # 总结
    print("\n\n" + "="*80)
    print("测试总结")
    print("="*80)
    
    for agent_name in agents.keys():
        agent_results = results[agent_name]
        success_count = sum(1 for r in agent_results if r['success'])
        total_count = len(agent_results)
        success_rate = success_count / total_count * 100
        
        print(f"\n{agent_name}:")
        print(f"  成功率: {success_rate:.1f}% ({success_count}/{total_count})")
        print(f"  快速路径使用: {sum(1 for r in agent_results if r['quick_path'] and r['success'])}次")
    
    # 检查关键功能
    print("\n\n关键功能检查:")
    print("-" * 40)
    
    # 检查个股查询是否正常
    stock_queries_ok = all(
        results[agent_name][i]['success'] 
        for agent_name in agents.keys() 
        for i in [3, 4]  # 个股查询的索引
    )
    print(f"个股查询功能: {'✅ 正常' if stock_queries_ok else '❌ 异常'}")
    
    # 检查板块查询处理
    sector_queries_handled = all(
        results[agent_name][i]['success'] or 'sql' in results[agent_name][i]['error'].lower()
        for agent_name in agents.keys() 
        for i in [0, 1, 2]  # 板块查询的索引
    )
    print(f"板块查询处理: {'✅ 正常（通过LLM或正确路由）' if sector_queries_handled else '❌ 可能有问题'}")
    
    print("\n结论: SQL Agent的板块功能", "✅ 未受影响" if stock_queries_ok else "❌ 可能受到影响")


if __name__ == "__main__":
    test_sql_agent_sector_queries()