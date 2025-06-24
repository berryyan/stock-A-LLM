#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
直接测试RAG Agent的query方法
模拟API调用环境
"""

import sys
import os
import traceback
import time
from datetime import datetime

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_rag_agent_directly():
    """直接测试RAG Agent"""
    print("=" * 60)
    print("直接测试RAG Agent")
    print("=" * 60)
    print(f"测试时间: {datetime.now()}")
    print()
    
    try:
        # 加载环境变量
        from dotenv import load_dotenv
        load_dotenv()
        
        print("1. 创建RAG Agent...")
        from agents.rag_agent import RAGAgent
        
        start_time = time.time()
        rag_agent = RAGAgent()
        init_time = time.time() - start_time
        print(f"   ✅ RAG Agent创建成功，耗时: {init_time:.2f}秒")
        print()
        
        # 测试查询
        test_query = "贵州茅台2024年的经营策略"
        print(f"2. 执行RAG查询: {test_query}")
        print("-" * 40)
        
        start_time = time.time()
        result = rag_agent.query(test_query, top_k=5)
        query_time = time.time() - start_time
        
        print(f"   查询耗时: {query_time:.2f}秒")
        print(f"   查询结果:")
        print(f"   - success: {result.get('success', 'N/A')}")
        print(f"   - question: {result.get('question', 'N/A')}")
        
        if result.get('success'):
            print(f"   - answer: {result.get('answer', 'N/A')[:200]}...")
            print(f"   - document_count: {result.get('document_count', 'N/A')}")
            print(f"   - processing_time: {result.get('processing_time', 'N/A'):.2f}s")
            print("   ✅ RAG查询成功")
        else:
            print(f"   - error: {result.get('error', 'N/A')}")
            print(f"   - message: {result.get('message', 'N/A')}")
            print("   ❌ RAG查询失败")
        
        return result.get('success', False)
        
    except Exception as e:
        print(f"   ❌ RAG Agent测试失败: {e}")
        print(f"   异常详情: {traceback.format_exc()}")
        return False

def test_step_by_step():
    """逐步测试RAG Agent的每个环节"""
    print("\n" + "=" * 60)
    print("逐步测试RAG Agent内部流程")
    print("=" * 60)
    
    try:
        from dotenv import load_dotenv
        load_dotenv()
        
        from agents.rag_agent import RAGAgent
        
        print("1. 创建RAG Agent...")
        rag_agent = RAGAgent()
        print("   ✅ RAG Agent创建成功")
        
        test_query = "贵州茅台2024年的经营策略"
        print(f"\n2. 测试查询: {test_query}")
        
        # 步骤1: 日期智能解析
        print("   2.1 日期智能解析...")
        try:
            from utils.date_intelligence import date_intelligence
            parsing_result = date_intelligence.parse_time_expressions(test_query)
            print(f"      ✅ 日期解析完成: {parsing_result}")
        except Exception as e:
            print(f"      ❌ 日期解析失败: {e}")
        
        # 步骤2: 文本编码
        print("   2.2 文本编码...")
        try:
            start_time = time.time()
            query_vector = rag_agent.embedding_model.encode([test_query])[0].tolist()
            encode_time = time.time() - start_time
            print(f"      ✅ 文本编码成功，耗时: {encode_time:.2f}秒，维度: {len(query_vector)}")
        except Exception as e:
            print(f"      ❌ 文本编码失败: {e}")
            return False
            
        # 步骤3: Milvus搜索
        print("   2.3 Milvus向量搜索...")
        try:
            start_time = time.time()
            search_results = rag_agent.milvus.search(
                query_vectors=[query_vector],
                top_k=5,
                filter_expr=None
            )
            search_time = time.time() - start_time
            
            if search_results and len(search_results[0]) > 0:
                print(f"      ✅ 向量搜索成功，耗时: {search_time:.2f}秒，返回: {len(search_results[0])}个结果")
                print(f"      前3个结果相似度: {[hit.score for hit in search_results[0][:3]]}")
            else:
                print(f"      ⚠️  向量搜索无结果，耗时: {search_time:.2f}秒")
                return False
                
        except Exception as e:
            print(f"      ❌ 向量搜索失败: {e}")
            print(f"      异常详情: {traceback.format_exc()}")
            return False
        
        # 步骤4: 文档提取
        print("   2.4 文档内容提取...")
        try:
            documents = rag_agent._extract_documents(search_results[0])
            print(f"      ✅ 文档提取成功，提取了 {len(documents)} 个文档")
            if documents:
                print(f"      第一个文档长度: {len(documents[0].get('content', ''))}")
        except Exception as e:
            print(f"      ❌ 文档提取失败: {e}")
            return False
        
        # 步骤5: 上下文格式化
        print("   2.5 上下文格式化...")
        try:
            context = rag_agent._format_context(documents)
            print(f"      ✅ 上下文格式化成功，长度: {len(context)}")
        except Exception as e:
            print(f"      ❌ 上下文格式化失败: {e}")
            return False
        
        # 步骤6: LLM调用
        print("   2.6 LLM问答链调用...")
        try:
            start_time = time.time()
            answer = rag_agent.qa_chain.invoke({
                "context": context,
                "question": test_query,
                "chat_history": ""
            })
            llm_time = time.time() - start_time
            
            print(f"      ✅ LLM调用成功，耗时: {llm_time:.2f}秒")
            print(f"      答案长度: {len(answer) if answer else 0}")
            print(f"      答案预览: {answer[:100] if answer else 'N/A'}...")
            
        except Exception as e:
            print(f"      ❌ LLM调用失败: {e}")
            print(f"      异常详情: {traceback.format_exc()}")
            return False
        
        print("\n   🎉 所有步骤测试成功！")
        return True
        
    except Exception as e:
        print(f"   ❌ 逐步测试失败: {e}")
        print(f"   异常详情: {traceback.format_exc()}")
        return False

def main():
    """主测试函数"""
    print("RAG Agent直接测试工具")
    print(f"测试时间: {datetime.now()}")
    print()
    
    # 测试1: 直接调用RAG Agent
    success1 = test_rag_agent_directly()
    
    # 测试2: 逐步测试各个环节
    success2 = test_step_by_step()
    
    # 总结
    print("\n" + "=" * 60)
    print("测试总结")
    print("=" * 60)
    print(f"1. RAG Agent直接调用: {'✅ 成功' if success1 else '❌ 失败'}")
    print(f"2. 逐步环节测试: {'✅ 成功' if success2 else '❌ 失败'}")
    
    if success1 and success2:
        print("\n🎉 RAG Agent工作正常！问题可能在API路由层面。")
    elif success2 and not success1:
        print("\n⚠️  各个环节正常，但整体调用失败，可能是query方法内部逻辑问题。")
    else:
        print("\n⚠️  发现问题，请根据上述错误信息进行修复。")

if __name__ == "__main__":
    main()