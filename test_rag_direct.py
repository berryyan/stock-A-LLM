#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
直接测试RAG Agent的查询功能
用于诊断API调用和直接调用的差异
"""

import sys
import os
import traceback
from datetime import datetime

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.rag_agent import RAGAgent
from utils.logger import setup_logger

def test_rag_direct():
    """直接测试RAG Agent"""
    print("=" * 80)
    print("直接测试RAG Agent - 诊断API调用差异")
    print("=" * 80)
    print(f"测试时间: {datetime.now()}")
    print()
    
    try:
        print("1. 初始化RAG Agent...")
        rag_agent = RAGAgent()
        print("   ✅ RAG Agent初始化成功")
        print()
        
        # 测试同样的查询
        test_queries = [
            "贵州茅台2024年的经营策略",
            "贵州茅台最新年报的主要内容", 
            "茅台最近的重要公告",
            "平安银行的经营风险"
        ]
        
        for i, question in enumerate(test_queries, 1):
            print(f"2.{i} 测试查询: {question}")
            print("-" * 60)
            
            try:
                # 执行查询
                result = rag_agent.query(question, top_k=5)
                
                print(f"   查询结果:")
                print(f"   - success: {result.get('success', 'N/A')}")
                print(f"   - question: {result.get('question', 'N/A')}")
                
                if result.get('success'):
                    print(f"   - answer: {result.get('answer', 'N/A')[:200]}...")
                    print(f"   - document_count: {result.get('document_count', 'N/A')}")
                    print(f"   - processing_time: {result.get('processing_time', 'N/A'):.2f}s")
                    print("   ✅ 查询成功")
                else:
                    print(f"   - error: {result.get('error', 'N/A')}")
                    print(f"   - message: {result.get('message', 'N/A')}")
                    print("   ❌ 查询失败")
                
            except Exception as e:
                print(f"   ❌ 查询异常: {e}")
                print(f"   异常详情: {traceback.format_exc()}")
            
            print()
        
        # 测试统计信息
        print("3. 检查统计信息:")
        print(f"   - 总查询数: {rag_agent.query_count}")
        print(f"   - 成功查询数: {rag_agent.success_count}")
        if rag_agent.query_count > 0:
            success_rate = (rag_agent.success_count / rag_agent.query_count) * 100
            print(f"   - 成功率: {success_rate:.1f}%")
        print()
        
        # 测试Milvus连接
        print("4. 检查Milvus连接:")
        try:
            stats = rag_agent.milvus.get_collection_stats()
            print(f"   - 集合统计: {stats}")
            print("   ✅ Milvus连接正常")
        except Exception as e:
            print(f"   ❌ Milvus连接异常: {e}")
        print()
        
        # 测试embedding模型
        print("5. 检查Embedding模型:")
        try:
            test_text = "测试文本"
            embedding = rag_agent.embedding_model.encode([test_text])
            print(f"   - 测试文本: {test_text}")
            print(f"   - 向量维度: {len(embedding[0]) if embedding else 'N/A'}")
            print("   ✅ Embedding模型正常")
        except Exception as e:
            print(f"   ❌ Embedding模型异常: {e}")
            print(f"   异常详情: {traceback.format_exc()}")
        
    except Exception as e:
        print(f"❌ 初始化失败: {e}")
        print(f"异常详情: {traceback.format_exc()}")
    
    print("\n" + "=" * 80)
    print("测试完成")
    print("=" * 80)

if __name__ == "__main__":
    test_rag_direct()