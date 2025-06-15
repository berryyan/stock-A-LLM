"""
测试Milvus存储功能
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.milvus_connector import MilvusConnector
from models.embedding_model import EmbeddingModel
import numpy as np


def test_embedding_format():
    """测试嵌入向量格式"""
    print("1. 测试嵌入向量格式")
    print("-" * 60)
    
    model = EmbeddingModel()
    
    # 测试单个文本
    text1 = "这是一个测试文本"
    embedding1 = model.encode(text1)
    
    print(f"单个嵌入:")
    print(f"  类型: {type(embedding1)}")
    print(f"  形状: {embedding1.shape if hasattr(embedding1, 'shape') else 'N/A'}")
    print(f"  是否有tolist方法: {hasattr(embedding1, 'tolist')}")
    
    # 测试批量文本
    texts = ["测试文本1", "测试文本2", "测试文本3"]
    embeddings = model.encode_batch(texts)
    
    print(f"\n批量嵌入:")
    print(f"  类型: {type(embeddings)}")
    print(f"  长度: {len(embeddings)}")
    print(f"  第一个嵌入类型: {type(embeddings[0])}")
    print(f"  第一个嵌入是否有tolist: {hasattr(embeddings[0], 'tolist')}")
    
    # 转换测试
    if hasattr(embeddings[0], 'tolist'):
        embedding_list = embeddings[0].tolist()
    else:
        embedding_list = embeddings[0]
    
    print(f"\n转换后:")
    print(f"  类型: {type(embedding_list)}")
    print(f"  长度: {len(embedding_list) if isinstance(embedding_list, list) else 'N/A'}")
    
    return embeddings


def test_milvus_insert(embeddings):
    """测试Milvus插入"""
    print("\n\n2. 测试Milvus插入")
    print("-" * 60)
    
    milvus = MilvusConnector()
    
    # 准备测试数据
    test_data = []
    for i in range(3):
        # 处理嵌入格式
        if hasattr(embeddings[i], 'tolist'):
            embedding_list = embeddings[i].tolist()
        else:
            embedding_list = embeddings[i]
        
        data = {
            'id': f'test_doc_{i}',
            'embedding': embedding_list,
            'text': f'测试文档{i}的内容',
            'ts_code': f'00000{i}.SZ',
            'company_name': f'测试公司{i}',
            'title': f'测试公告{i}',
            'ann_date': '20250422',
            'chunk_id': 0,
            'metadata': f'{{"test": "data_{i}"}}'
        }
        test_data.append(data)
    
    print(f"准备插入 {len(test_data)} 条数据")
    
    try:
        # 先删除测试数据（如果存在）
        for i in range(3):
            milvus.delete_by_expr(f'id == "test_doc_{i}"')
        
        # 插入数据
        milvus.insert_data(test_data)
        print("✓ 插入成功!")
        
        # 验证插入
        stats = milvus.get_collection_stats()
        print(f"\n集合统计:")
        print(f"  总文档数: {stats['row_count']}")
        
        return True
    except Exception as e:
        print(f"✗ 插入失败: {e}")
        return False


def test_milvus_search():
    """测试Milvus搜索"""
    print("\n\n3. 测试Milvus搜索")
    print("-" * 60)
    
    milvus = MilvusConnector()
    model = EmbeddingModel()
    
    # 生成查询向量
    query_text = "测试查询"
    query_embedding = model.encode(query_text)
    
    if hasattr(query_embedding, 'tolist'):
        query_vec = query_embedding.tolist()
    else:
        query_vec = query_embedding
    
    print(f"查询文本: '{query_text}'")
    print(f"查询向量类型: {type(query_vec)}")
    
    try:
        # 搜索
        results = milvus.search(
            query_vectors=[query_vec],
            top_k=5
        )
        
        print(f"\n搜索结果:")
        if results and len(results) > 0:
            for i, hits in enumerate(results):
                print(f"\n查询 {i+1} 的结果:")
                for j, hit in enumerate(hits[:3]):  # 只显示前3个
                    print(f"  {j+1}. ID: {hit.id}")
                    print(f"     距离: {hit.distance}")
                    print(f"     文本: {hit.entity.get('text', 'N/A')[:50]}...")
        else:
            print("  没有找到结果")
            
        return True
    except Exception as e:
        print(f"✗ 搜索失败: {e}")
        return False


def cleanup_test_data():
    """清理测试数据"""
    print("\n\n4. 清理测试数据")
    print("-" * 60)
    
    milvus = MilvusConnector()
    
    try:
        for i in range(3):
            milvus.delete_by_expr(f'id == "test_doc_{i}"')
        print("✓ 测试数据已清理")
    except Exception as e:
        print(f"✗ 清理失败: {e}")


def main():
    """主测试流程"""
    print("Milvus存储功能测试")
    print("=" * 60)
    
    # 测试嵌入格式
    embeddings = test_embedding_format()
    
    # 测试插入
    if test_milvus_insert(embeddings):
        # 测试搜索
        test_milvus_search()
    
    # 清理
    cleanup_test_data()
    
    print("\n" + "=" * 60)
    print("测试完成!")


if __name__ == "__main__":
    main()
