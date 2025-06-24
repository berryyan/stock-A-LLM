#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试嵌入模型修复
"""

import sys
import os
import time
from datetime import datetime

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_embedding_model_initialization():
    """测试嵌入模型初始化"""
    print("=" * 60)
    print("测试嵌入模型初始化")
    print("=" * 60)
    print(f"测试时间: {datetime.now()}")
    print()
    
    try:
        print("1. 导入模块...")
        from dotenv import load_dotenv
        load_dotenv()
        
        from models.embedding_model import EmbeddingModel
        
        print("2. 创建EmbeddingModel实例...")
        start_time = time.time()
        
        embedding_model = EmbeddingModel()
        
        init_time = time.time() - start_time
        print(f"   ✅ 模型初始化成功，耗时: {init_time:.2f}秒")
        
        print("3. 测试编码功能...")
        test_text = "贵州茅台2024年的经营策略"
        
        start_time = time.time()
        embeddings = embedding_model.encode([test_text])
        encode_time = time.time() - start_time
        
        print(f"   ✅ 编码成功，耗时: {encode_time:.2f}秒")
        print(f"   向量维度: {len(embeddings[0])}")
        print(f"   向量前5个值: {embeddings[0][:5]}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ 模型测试失败: {e}")
        import traceback
        print(f"   详细错误: {traceback.format_exc()}")
        return False

def test_rag_agent_with_fixed_model():
    """测试修复后的RAG Agent"""
    print("\n" + "=" * 60)
    print("测试修复后的RAG Agent")
    print("=" * 60)
    
    try:
        print("1. 导入RAG Agent...")
        from agents.rag_agent import RAGAgent
        
        print("2. 创建RAG Agent实例...")
        start_time = time.time()
        
        rag_agent = RAGAgent()
        
        init_time = time.time() - start_time
        print(f"   ✅ RAG Agent初始化成功，耗时: {init_time:.2f}秒")
        
        print("3. 执行RAG查询...")
        query = "贵州茅台2024年的经营策略"
        print(f"   查询: {query}")
        print(f"   开始时间: {datetime.now()}")
        
        start_time = time.time()
        result = rag_agent.query(query)
        query_time = time.time() - start_time
        
        print(f"   查询耗时: {query_time:.2f}秒")
        print(f"   结束时间: {datetime.now()}")
        print()
        
        print("4. 查询结果:")
        print(f"   success: {result.get('success', False)}")
        print(f"   error: {result.get('error', 'None')}")
        
        if result.get('success'):
            answer = result.get('answer', '')
            print(f"   answer_length: {len(answer)}")
            print(f"   answer_preview: {answer[:200]}...")
            print(f"   document_count: {result.get('document_count', 0)}")
            return True
        else:
            print(f"   查询失败")
            return False
            
    except Exception as e:
        print(f"   ❌ RAG Agent测试失败: {e}")
        import traceback
        print(f"   详细错误: {traceback.format_exc()}")
        return False

def main():
    """主测试函数"""
    print("嵌入模型修复测试工具")
    print(f"测试开始时间: {datetime.now()}")
    print()
    
    # 测试1: 嵌入模型初始化
    embedding_success = test_embedding_model_initialization()
    
    # 测试2: RAG Agent
    rag_success = test_rag_agent_with_fixed_model()
    
    # 总结
    print("\n" + "=" * 60)
    print("测试总结")
    print("=" * 60)
    print(f"1. 嵌入模型初始化: {'✅ 成功' if embedding_success else '❌ 失败'}")
    print(f"2. RAG Agent查询: {'✅ 成功' if rag_success else '❌ 失败'}")
    
    if embedding_success and rag_success:
        print("\n🎉 所有测试都成功！RAG功能已修复")
    elif embedding_success:
        print("\n⚠️ 嵌入模型正常，但RAG Agent仍有问题")
    else:
        print("\n❌ 嵌入模型初始化失败，需要进一步排查")

if __name__ == "__main__":
    main()