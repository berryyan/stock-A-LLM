#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快速测试Hybrid Agent修复效果
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.hybrid_agent_modular import HybridAgentModular
import time

# 只测试之前失败的投资价值分析查询
test_queries = [
    "评估宁德时代的投资机会",
    "比亚迪值得投资吗",
    "分析贵州茅台的投资价值"
]

print("快速测试Hybrid Agent投资价值分析修复")
print("=" * 80)

agent = HybridAgentModular()
success_count = 0
total_time = 0

for query in test_queries:
    print(f"\n查询: {query}")
    print("-" * 50)
    
    start = time.time()
    try:
        result = agent.query(query)
        elapsed = time.time() - start
        total_time += elapsed
        
        if result.get('success'):
            success_count += 1
            print(f"✅ 成功 (耗时: {elapsed:.1f}秒)")
            print(f"路由: {result.get('query_type', 'Unknown')}")
        else:
            print(f"❌ 失败 (耗时: {elapsed:.1f}秒)")
            print(f"错误: {result.get('error', '未知错误')}")
            print(f"路由: {result.get('query_type', 'Unknown')}")
    except Exception as e:
        print(f"❌ 异常: {str(e)}")

print(f"\n\n总结:")
print(f"成功率: {success_count}/{len(test_queries)} ({success_count/len(test_queries)*100:.0f}%)")
print(f"平均耗时: {total_time/len(test_queries):.1f}秒")