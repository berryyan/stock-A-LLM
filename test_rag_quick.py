#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
快速测试RAGAgentModular的query方法
验证修复是否正确
"""

import logging
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)


def test_rag_query():
    """测试RAG查询"""
    print("=== 测试RAGAgentModular.query方法 ===\n")
    
    try:
        from agents.rag_agent_modular import RAGAgentModular
        
        print("1. 初始化RAGAgentModular...")
        rag_agent = RAGAgentModular()
        print("   ✓ 初始化成功\n")
        
        # 简单查询测试
        query = "贵州茅台的主营业务"
        print(f"2. 执行查询: {query}")
        
        result = rag_agent.query(query)
        
        print(f"\n3. 返回结果类型: {type(result)}")
        
        if isinstance(result, dict):
            print("   ✓ 返回类型正确（字典）")
            print(f"   - success: {result.get('success', False)}")
            print(f"   - 包含的键: {list(result.keys())}")
            
            if result.get('success'):
                content = result.get('result', '')
                print(f"   - 结果长度: {len(content)}字符")
                print(f"   - 结果预览: {content[:100]}...")
            else:
                print(f"   - 错误信息: {result.get('error', '未知')}")
        else:
            print(f"   ✗ 返回类型错误: {type(result)}")
            
    except Exception as e:
        print(f"\n✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()


def test_evidence_collector():
    """测试证据收集器的RAG调用"""
    print("\n\n=== 测试证据收集器调用RAG ===\n")
    
    try:
        from utils.concept.evidence_collector_optimized import EvidenceCollectorOptimized
        
        collector = EvidenceCollectorOptimized()
        
        # 模拟财报证据收集
        print("测试财报证据收集...")
        
        # 直接测试私有方法
        evidence = collector._collect_report_evidence_optimized(
            ts_code='600519.SH',
            concepts=['白酒']
        )
        
        print(f"\n收集到 {len(evidence)} 条财报证据")
        for i, ev in enumerate(evidence, 1):
            print(f"\n证据{i}:")
            print(f"  - 来源: {ev.get('source', 'N/A')}")
            print(f"  - 得分: {ev.get('score', 0)}分")
            print(f"  - 内容: {ev.get('content', 'N/A')[:100]}...")
            
    except Exception as e:
        print(f"\n✗ 证据收集测试失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    test_rag_query()
    test_evidence_collector()
    print("\n测试结束！")