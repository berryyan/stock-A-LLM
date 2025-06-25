#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
RAG查询简单测试 - 验证诺德股份等公司名称查询
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.hybrid_agent import HybridAgent
import time

def test_rag_queries():
    """测试RAG查询功能"""
    agent = HybridAgent()
    
    # 测试查询列表
    test_queries = [
        "分析诺德股份的2024年年报",
        "贵州茅台最新的公告内容",
        "美的集团的经营策略是什么",
        "分析同花顺的业务模式",
    ]
    
    print("RAG查询测试开始")
    print("="*60)
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n测试 {i}: {query}")
        print("-"*40)
        
        start = time.time()
        result = agent.query(query)
        elapsed = time.time() - start
        
        if result.get('success'):
            print(f"✅ 查询成功 (耗时: {elapsed:.2f}秒)")
            print(f"查询类型: {result.get('query_type')}")
            
            # 显示答案预览
            answer = result.get('answer', '')
            if answer:
                preview = answer[:150].replace('\n', ' ')
                print(f"答案预览: {preview}...")
            
            # 显示来源信息
            sources = result.get('sources', {})
            if 'rag' in sources and sources['rag'].get('sources'):
                rag_sources = sources['rag']['sources']
                print(f"文档来源: 找到 {len(rag_sources)} 个相关文档")
        else:
            print(f"❌ 查询失败")
            print(f"错误: {result.get('error', '未知错误')}")
            print(f"消息: {result.get('message', '')}")
    
    print("\n" + "="*60)
    print("测试完成")


if __name__ == "__main__":
    test_rag_queries()