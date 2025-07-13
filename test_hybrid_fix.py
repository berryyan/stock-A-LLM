#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试Hybrid Agent修复后的效果
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.hybrid_agent_modular import HybridAgentModular

# 测试之前失败的查询
test_queries = [
    ("评估宁德时代的投资机会", "投资价值分析"),
    ("比亚迪值得投资吗", "投资价值分析"),
    ("分析恒大的风险状况", "风险评估分析"),
    ("评估万科A的财务风险和股价表现", "风险评估分析"),
    ("分析贵州茅台的投资价值", "投资价值分析")
]

print("测试Financial Agent股票名称识别修复后的效果")
print("=" * 80)

agent = HybridAgentModular()
success_count = 0

for query, expected_type in test_queries:
    print(f"\n查询: {query}")
    print(f"期望类型: {expected_type}")
    print("-" * 50)
    
    result = agent.query(query)
    
    if result.get('success'):
        success_count += 1
        print(f"✅ 成功")
        print(f"路由类型: {result.get('query_type', 'Unknown')}")
        if result.get('answer'):
            preview = str(result['answer'])[:100]
            print(f"答案预览: {preview}...")
    else:
        print(f"❌ 失败")
        print(f"错误: {result.get('error', '未知错误')}")
        print(f"路由类型: {result.get('query_type', 'Unknown')}")

print(f"\n\n总结: {success_count}/{len(test_queries)} 成功")