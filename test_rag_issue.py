#!/usr/bin/env python
"""测试RAG问题"""
import time
from datetime import datetime

def test_milvus_connection():
    """测试Milvus连接"""
    print("\n=== 测试Milvus连接 ===")
    try:
        from database.milvus_connector import MilvusConnector
        milvus = MilvusConnector()
        stats = milvus.get_collection_stats()
        print(f"✓ Milvus连接成功，集合行数: {stats['row_count']}")
        return True
    except Exception as e:
        print(f"✗ Milvus连接失败: {e}")
        return False

def test_embedding_model():
    """测试嵌入模型"""
    print("\n=== 测试嵌入模型 ===")
    try:
        from utils.embeddings import BGEEmbeddings
        from config.settings import settings
        
        print("初始化嵌入模型...")
        start_time = time.time()
        embedding_model = BGEEmbeddings(
            model_name=settings.EMBEDDING_MODEL_NAME,
            model_kwargs={'device': 'cpu'},
            encode_kwargs={'normalize_embeddings': True}
        )
        init_time = time.time() - start_time
        print(f"模型初始化耗时: {init_time:.2f}秒")
        
        print("测试文本编码...")
        start_time = time.time()
        test_text = "茅台公告"
        vector = embedding_model.encode([test_text])
        encode_time = time.time() - start_time
        print(f"✓ 文本编码成功，向量维度: {len(vector[0])}, 耗时: {encode_time:.2f}秒")
        return True
    except Exception as e:
        print(f"✗ 嵌入模型错误: {e}")
        return False

def test_simple_rag_search():
    """测试简单RAG搜索"""
    print("\n=== 测试简单RAG搜索 ===")
    try:
        from database.milvus_connector import MilvusConnector
        from utils.embeddings import BGEEmbeddings
        from config.settings import settings
        
        # 初始化连接
        milvus = MilvusConnector()
        embedding_model = BGEEmbeddings(
            model_name=settings.EMBEDDING_MODEL_NAME,
            model_kwargs={'device': 'cpu'},
            encode_kwargs={'normalize_embeddings': True}
        )
        
        # 生成查询向量
        query = "茅台"
        query_vector = embedding_model.encode([query])[0].tolist()
        
        # 搜索
        print("执行向量搜索...")
        start_time = time.time()
        results = milvus.search(
            query_vectors=[query_vector],
            top_k=3
        )
        search_time = time.time() - start_time
        
        if results and len(results[0]) > 0:
            print(f"✓ 搜索成功，找到 {len(results[0])} 个结果，耗时: {search_time:.2f}秒")
            return True
        else:
            print(f"✗ 未找到搜索结果")
            return False
    except Exception as e:
        print(f"✗ RAG搜索错误: {e}")
        return False

def main():
    """主测试函数"""
    print("=== RAG功能问题诊断 ===")
    print(f"开始时间: {datetime.now()}")
    
    # 依次测试各个组件
    test_milvus_connection()
    test_embedding_model()
    test_simple_rag_search()
    
    print(f"\n结束时间: {datetime.now()}")

if __name__ == "__main__":
    main()