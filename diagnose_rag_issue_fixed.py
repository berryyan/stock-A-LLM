#!/usr/bin/env python3
"""
修复后的RAG Agent答案生成问题诊断工具
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.rag_agent import RAGAgent
import logging

# 设置详细日志
logging.basicConfig(level=logging.DEBUG)

def test_rag_components():
    """测试RAG组件的各个部分"""
    
    print("=== RAG组件诊断 ===\n")
    
    try:
        # 1. 初始化RAG Agent
        print("1. 初始化RAG Agent...")
        rag_agent = RAGAgent()
        print("✓ 初始化成功\n")
        
        # 2. 测试文档检索
        print("2. 测试文档检索...")
        question = "贵州茅台最新财报"
        
        # 直接测试向量搜索
        from models.embedding_model import EmbeddingModel
        embedding_model = EmbeddingModel()
        query_embedding = embedding_model.encode(question)
        
        # 修复：使用正确的参数名 query_vectors 而不是 vectors
        search_results = rag_agent.milvus.search(
            query_vectors=[query_embedding],  # 修改这里
            top_k=3
        )
        
        if search_results and len(search_results[0]) > 0:
            print(f"✓ 找到 {len(search_results[0])} 个文档")
            
            # 提取文档
            documents = rag_agent._extract_documents(search_results[0])
            print(f"✓ 成功提取 {len(documents)} 个文档\n")
            
            # 3. 测试上下文格式化
            print("3. 测试上下文格式化...")
            context = rag_agent._format_context(documents)
            print(f"✓ 上下文长度: {len(context)} 字符")
            print(f"上下文预览:\n{context[:500]}...\n")
            
            # 4. 测试LLM调用
            print("4. 测试LLM调用...")
            
            # 直接测试LLM
            try:
                from langchain_openai import ChatOpenAI
                from config.settings import settings
                
                llm = ChatOpenAI(
                    model="deepseek-chat",
                    temperature=0.7,
                    api_key=settings.DEEPSEEK_API_KEY,
                    base_url=settings.DEEPSEEK_BASE_URL
                )
                
                # 简单测试
                test_response = llm.invoke("你好，请回答：1+1等于几？")
                print(f"✓ LLM响应正常: {test_response.content}\n")
                
            except Exception as e:
                print(f"✗ LLM调用失败: {e}\n")
                
            # 5. 测试QA Chain
            print("5. 测试QA Chain...")
            
            # 测试memory
            chat_history = rag_agent._get_chat_history()
            print(f"对话历史: {chat_history}")
            
            # 手动构建输入
            qa_input = {
                'context': context,
                'question': question,
                'chat_history': chat_history
            }
            
            try:
                # 使用invoke替代run（虽然run仍然可用）
                result = rag_agent.qa_chain.invoke(qa_input)
                print(f"✓ QA Chain执行成功")
                print(f"结果类型: {type(result)}")
                
                # 提取答案
                if isinstance(result, dict):
                    answer = result.get('text', str(result))
                else:
                    answer = str(result)
                    
                print(f"答案: {answer[:200]}...")
                
            except Exception as e:
                print(f"✗ QA Chain执行失败: {e}")
                import traceback
                traceback.print_exc()
                
        else:
            print("✗ 未找到相关文档")
            
    except Exception as e:
        print(f"✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()

def test_simple_query():
    """测试简单查询"""
    print("\n\n=== 简单查询测试 ===\n")
    
    try:
        rag_agent = RAGAgent()
        
        # 使用更简单的问题
        result = rag_agent.query("贵州茅台", filters={"ts_code": "600519.SH"})
        
        print(f"查询结果:")
        print(f"- 成功: {result.get('success')}")
        print(f"- 文档数: {result.get('document_count', 0)}")
        print(f"- 答案长度: {len(result.get('answer', ''))}")
        print(f"- 答案预览: {result.get('answer', '')[:200]}...")
        
        # 如果答案为空，检查其他字段
        if not result.get('answer'):
            print("\n⚠️ 答案为空，检查其他字段:")
            for key, value in result.items():
                if value:
                    print(f"- {key}: {str(value)[:100]}...")
                    
    except Exception as e:
        print(f"✗ 查询失败: {e}")
        import traceback
        traceback.print_exc()

def check_logs():
    """检查日志文件位置"""
    print("\n\n=== 检查日志文件 ===\n")
    
    import os
    
    # 检查可能的日志目录
    possible_log_dirs = [
        'logs',
        'data/logs',
        os.path.join(os.path.dirname(__file__), 'logs'),
        os.path.join(os.path.dirname(__file__), 'data', 'logs'),
    ]
    
    for log_dir in possible_log_dirs:
        if os.path.exists(log_dir):
            print(f"✓ 找到日志目录: {os.path.abspath(log_dir)}")
            # 列出日志文件
            for file in os.listdir(log_dir):
                if file.endswith('.log'):
                    file_path = os.path.join(log_dir, file)
                    size = os.path.getsize(file_path) / 1024  # KB
                    print(f"  - {file} ({size:.2f} KB)")
            break
    else:
        print("✗ 未找到日志目录")
        print("建议创建 logs 目录来存储日志文件")

if __name__ == "__main__":
    print("RAG答案生成问题诊断工具 (修复版)\n")
    
    # 运行诊断
    test_rag_components()
    test_simple_query()
    check_logs()
    
    print("\n诊断完成！")
