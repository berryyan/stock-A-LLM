#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RAG Agent 快速测试
验证核心功能是否正常
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.rag_agent_modular import RAGAgentModular


def quick_test():
    """运行RAG Agent快速测试"""
    print("\nRAG Agent 快速测试")
    print("=" * 50)
    
    agent = RAGAgentModular()
    
    # 核心测试用例（使用更通用的查询）
    test_cases = [
        ("贵州茅台的主要业务是什么", "业务查询"),
        ("万科A的发展战略", "战略查询"),
        ("比亚迪的竞争优势", "优势分析"),
        ("宁德时代的技术特点", "技术查询"),
        ("中国平安的经营状况", "经营分析"),
    ]
    
    passed = 0
    failed = 0
    
    for query, test_name in test_cases:
        print(f"\n测试{passed + failed + 1}: {test_name}")
        print(f"查询: {query}")
        
        try:
            result = agent.query(query)
            if result.get('success'):
                answer = result.get('answer', '')
                if answer and len(answer) > 50:
                    print("✅ 通过")
                    passed += 1
                else:
                    print("❌ 失败: 回答内容不足")
                    failed += 1
            else:
                print(f"❌ 失败: {result.get('error')}")
                failed += 1
        except Exception as e:
            print(f"❌ 异常: {str(e)}")
            failed += 1
    
    print(f"\n{'='*50}")
    print(f"测试总结: {passed}/{len(test_cases)} 通过")
    print(f"通过率: {passed/len(test_cases)*100:.1f}%")
    
    # RAG Agent期望至少60%通过
    return passed / len(test_cases) >= 0.6


if __name__ == "__main__":
    success = quick_test()
    exit(0 if success else 1)