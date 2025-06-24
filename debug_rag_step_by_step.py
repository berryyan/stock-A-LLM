#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
逐步诊断RAG查询的每个环节
"""

import sys
import os
import traceback
import time
from datetime import datetime

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_embedding_model():
    """测试嵌入模型"""
    print("=" * 60)
    print("1. 测试嵌入模型")
    print("=" * 60)
    
    try:
        from models.embedding_model import EmbeddingModel
        
        print("1.1 初始化嵌入模型...")
        start_time = time.time()
        embedding_model = EmbeddingModel()
        init_time = time.time() - start_time
        print(f"   ✅ 模型初始化成功，耗时: {init_time:.2f}秒")
        
        print("1.2 测试文本编码...")
        test_text = "贵州茅台2024年的经营策略"
        start_time = time.time()
        
        # 测试编码
        vector = embedding_model.encode([test_text])
        encode_time = time.time() - start_time
        
        print(f"   ✅ 文本编码成功，耗时: {encode_time:.2f}秒")
        print(f"   - 输入文本: {test_text}")
        print(f"   - 向量维度: {len(vector[0]) if vector is not None and len(vector) > 0 else 'N/A'}")
        print(f"   - 向量类型: {type(vector)}")
        
        return embedding_model, vector[0].tolist()
        
    except Exception as e:
        print(f"   ❌ 嵌入模型测试失败: {e}")
        print(f"   异常详情: {traceback.format_exc()}")
        return None, None

def test_milvus_connection():
    """测试Milvus连接"""
    print("\n" + "=" * 60)
    print("2. 测试Milvus连接")
    print("=" * 60)
    
    try:
        from database.milvus_connector import MilvusConnector
        
        print("2.1 初始化Milvus连接...")
        milvus = MilvusConnector()
        print("   ✅ Milvus连接初始化成功")
        
        print("2.2 检查集合状态...")
        try:
            stats = milvus.get_collection_stats()
            print(f"   ✅ 集合统计: {stats}")
        except Exception as e:
            print(f"   ⚠️  集合统计失败: {e}")
            
        print("2.3 测试集合是否加载...")
        try:
            # 尝试执行一个简单的搜索来测试集合是否可用
            test_vector = [0.0] * 1024  # BGE-M3的维度
            
            search_results = milvus.search(
                query_vectors=[test_vector],
                top_k=1,
                filter_expr=None
            )
            print(f"   ✅ 集合可正常搜索，返回结果数: {len(search_results[0]) if search_results else 0}")
            
        except Exception as e:
            print(f"   ❌ 集合搜索测试失败: {e}")
            return None
            
        return milvus
        
    except Exception as e:
        print(f"   ❌ Milvus连接测试失败: {e}")
        print(f"   异常详情: {traceback.format_exc()}")
        return None

def test_vector_search(milvus, query_vector):
    """测试向量搜索"""
    print("\n" + "=" * 60)
    print("3. 测试向量搜索")
    print("=" * 60)
    
    if not milvus or not query_vector:
        print("   ⚠️  跳过向量搜索测试（依赖项测试失败）")
        return None
        
    try:
        print("3.1 执行向量搜索...")
        start_time = time.time()
        
        search_results = milvus.search(
            query_vectors=[query_vector],
            top_k=5,
            filter_expr=None
        )
        
        search_time = time.time() - start_time
        print(f"   ✅ 向量搜索成功，耗时: {search_time:.2f}秒")
        print(f"   - 返回结果数: {len(search_results[0]) if search_results else 0}")
        
        if search_results and len(search_results[0]) > 0:
            print("   - 前3个结果:")
            for i, hit in enumerate(search_results[0][:3]):
                print(f"     {i+1}. 相似度: {hit.score:.4f}, ID: {hit.id}")
                
        return search_results
        
    except Exception as e:
        print(f"   ❌ 向量搜索失败: {e}")
        print(f"   异常详情: {traceback.format_exc()}")
        return None

def test_llm_call():
    """测试LLM调用"""
    print("\n" + "=" * 60)
    print("4. 测试LLM调用")
    print("=" * 60)
    
    try:
        from langchain_openai import ChatOpenAI
        from langchain.prompts import PromptTemplate
        from langchain_core.output_parsers import StrOutputParser
        from config.settings import settings
        
        print("4.1 初始化LLM...")
        llm = ChatOpenAI(
            model="deepseek-chat",
            temperature=0.7,
            api_key=settings.DEEPSEEK_API_KEY,
            base_url=settings.DEEPSEEK_BASE_URL
        )
        print("   ✅ LLM初始化成功")
        
        print("4.2 创建测试链...")
        test_prompt = PromptTemplate(
            input_variables=["question"],
            template="请简短回答这个问题：{question}"
        )
        
        test_chain = test_prompt | llm | StrOutputParser()
        print("   ✅ 测试链创建成功")
        
        print("4.3 执行LLM调用...")
        start_time = time.time()
        
        response = test_chain.invoke({"question": "你好，请说一句话。"})
        
        llm_time = time.time() - start_time
        print(f"   ✅ LLM调用成功，耗时: {llm_time:.2f}秒")
        print(f"   - 响应: {response[:100]}...")
        
        return True
        
    except Exception as e:
        print(f"   ❌ LLM调用失败: {e}")
        print(f"   异常详情: {traceback.format_exc()}")
        return False

def main():
    """主测试函数"""
    print("RAG系统逐步诊断工具")
    print(f"测试时间: {datetime.now()}")
    print("\n")
    
    # 测试1: 嵌入模型
    embedding_model, query_vector = test_embedding_model()
    
    # 测试2: Milvus连接
    milvus = test_milvus_connection()
    
    # 测试3: 向量搜索
    search_results = test_vector_search(milvus, query_vector)
    
    # 测试4: LLM调用
    llm_success = test_llm_call()
    
    # 总结
    print("\n" + "=" * 60)
    print("诊断总结")
    print("=" * 60)
    print(f"1. 嵌入模型: {'✅ 正常' if embedding_model else '❌ 失败'}")
    print(f"2. Milvus连接: {'✅ 正常' if milvus else '❌ 失败'}")
    print(f"3. 向量搜索: {'✅ 正常' if search_results else '❌ 失败'}")
    print(f"4. LLM调用: {'✅ 正常' if llm_success else '❌ 失败'}")
    
    if all([embedding_model, milvus, search_results, llm_success]):
        print("\n🎉 所有组件测试通过！RAG系统应该可以正常工作。")
        print("如果API调用仍然失败，可能是API层面的问题。")
    else:
        print("\n⚠️  发现问题组件，请根据上述错误信息进行修复。")

if __name__ == "__main__":
    main()