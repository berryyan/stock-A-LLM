#!/usr/bin/env python
"""简化的RAG测试"""
import time
import sys

# 添加超时装饰器
import signal

def timeout_handler(signum, frame):
    raise TimeoutError("操作超时")

def test_embedding_model():
    """测试嵌入模型初始化"""
    print("\n=== 测试嵌入模型初始化 ===")
    start_time = time.time()
    
    try:
        from models.embedding_model import EmbeddingModel
        print("导入成功，开始初始化...")
        
        # 设置20秒超时
        signal.signal(signal.SIGALRM, timeout_handler)
        signal.alarm(20)
        
        model = EmbeddingModel()
        
        signal.alarm(0)  # 取消超时
        
        elapsed = time.time() - start_time
        print(f"✓ 模型初始化成功，耗时: {elapsed:.2f}秒")
        
        # 测试编码
        test_text = "测试文本"
        vector = model.encode([test_text])
        print(f"✓ 文本编码成功，向量维度: {len(vector[0])}")
        
        return True
        
    except TimeoutError:
        elapsed = time.time() - start_time
        print(f"✗ 模型初始化超时（{elapsed:.0f}秒）")
        return False
    except Exception as e:
        elapsed = time.time() - start_time
        print(f"✗ 错误: {e}, 耗时: {elapsed:.2f}秒")
        import traceback
        traceback.print_exc()
        return False

def test_rag_agent_init():
    """测试RAG Agent初始化"""
    print("\n=== 测试RAG Agent初始化 ===")
    start_time = time.time()
    
    try:
        print("开始导入RAG Agent...")
        from agents.rag_agent import RAGAgent
        
        print("开始初始化RAG Agent...")
        
        # 设置30秒超时
        signal.signal(signal.SIGALRM, timeout_handler)
        signal.alarm(30)
        
        agent = RAGAgent()
        
        signal.alarm(0)  # 取消超时
        
        elapsed = time.time() - start_time
        print(f"✓ RAG Agent初始化成功，耗时: {elapsed:.2f}秒")
        return True
        
    except TimeoutError:
        elapsed = time.time() - start_time
        print(f"✗ RAG Agent初始化超时（{elapsed:.0f}秒）")
        return False
    except Exception as e:
        elapsed = time.time() - start_time
        print(f"✗ 错误: {e}, 耗时: {elapsed:.2f}秒")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主测试函数"""
    print("=== 简化RAG测试 ===")
    
    # 测试嵌入模型
    if not test_embedding_model():
        print("\n嵌入模型初始化失败，停止测试")
        return
    
    # 测试RAG Agent
    test_rag_agent_init()

if __name__ == "__main__":
    main()