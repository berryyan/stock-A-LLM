#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RAG Agent 基础功能检查
快速验证RAG Agent是否能正常工作
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.rag_agent_modular import RAGAgentModular
import time


def basic_check():
    """基础功能检查"""
    print("="*60)
    print("RAG Agent 基础功能检查")
    print("="*60)
    
    agent = RAGAgentModular()
    
    # 只测试2个最基本的查询
    test_queries = [
        "贵州茅台的主要业务",
        "万科A的发展战略"
    ]
    
    passed = 0
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n测试 {i}: {query}")
        
        start_time = time.time()
        try:
            result = agent.query(query)
            elapsed = time.time() - start_time
            
            if result.get('success'):
                answer = result.get('answer', '')
                if answer and len(answer) > 30:
                    print(f"✅ 成功 (耗时: {elapsed:.1f}秒)")
                    print(f"回答长度: {len(answer)}字符")
                    passed += 1
                else:
                    print(f"❌ 失败: 回答内容不足")
            else:
                print(f"❌ 失败: {result.get('error', '未知错误')}")
                
        except Exception as e:
            print(f"❌ 异常: {str(e)}")
    
    print(f"\n结果: {passed}/{len(test_queries)} 通过")
    
    if passed > 0:
        print("✅ RAG Agent基本功能正常")
        return True
    else:
        print("❌ RAG Agent存在问题")
        return False


if __name__ == "__main__":
    success = basic_check()
    exit(0 if success else 1)