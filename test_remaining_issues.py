#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试SQL Agent剩余问题
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.sql_agent_modular import SQLAgentModular

def test_remaining_issues():
    """测试剩余问题"""
    agent = SQLAgentModular()
    
    print("=" * 80)
    print("SQL Agent 剩余问题测试")
    print("=" * 80)
    
    test_cases = [
        # K线查询中文数字
        "中国平安前十天的走势",
        
        # 板块主力资金时间指定
        "房地产板块昨天的主力资金",
        "房地产板块2025-06-27的主力资金",
        
        # 市值排名TOP格式
        "市值TOP10",
        "市值TOP20的股票",
        "总市值TOP10",
    ]
    
    for query in test_cases:
        print(f"\n{'='*60}")
        print(f"测试查询: {query}")
        print(f"{'='*60}")
        
        result = agent.query(query)
        
        if result['success']:
            print("✅ 查询成功!")
        else:
            print("❌ 查询失败!")
            print(f"错误信息: {result.get('error')}")
    
    print(f"\n{'='*80}")
    print("测试完成!")
    print(f"{'='*80}")

if __name__ == "__main__":
    test_remaining_issues()