"""
测试适配后的Milvus连接器
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.milvus_connector import MilvusConnector
from models.embedding_model import EmbeddingModel
import json
import time


def test_basic_operations():
    """测试基本操作"""
    print("测试适配后的Milvus连接器")
    print("=" * 60)
    
    # 初始化
    print("\n1. 初始化连接器...")
    try:
        milvus = MilvusConnector()
        print("✓ 连接器初始化成功")
        
        # 获取统计信息
        stats = milvus.get_collection_stats()
        print(f"\n集合信息:")
        print(f"  名称: {stats['name']}")
        print(f"  文档数: {stats['row_count']}")
        print(f"  已加载: {stats['loaded']}")
    except Exception as e:
        print(f"✗ 初始化失败: {e}")
        return
    
    # 测试插入
    print("\n2. 测试数据插入...")
    try:
        # 生成测试向量
        model = EmbeddingModel()
        test_text = "这是一个测试文档，用于验证Milvus插入功能"
        embedding = model.encode(test_text)
        
        # 转换为list
        if hasattr(embedding, 'tolist'):
            embedding_list = embedding.tolist()
        else:
            embedding_list = embedding
        
        # 准备测试数据
        test_data = [{
            'id': f'test_doc_{int(time.time())}',  # 使用时间戳确保唯一
            'embedding': embedding_list,
            'text': test_text,
            'ts_code': '000001.SZ',
            'title': '测试公告标题',
            'ann_date': '20250422',
            'chunk_id': 0,
            'metadata': json.dumps({
                "test": True,
                "company_name": "测试公司",
                "source": "test_script"
            })
        }]
        
        success = milvus.insert_data(test_data)
        if success:
            print("✓ 数据插入成功")
        else:
            print("✗ 数据插入失败")
            return
            
    except Exception as e:
        print(f"✗ 插入测试失败: {e}")
        return
    
    # 测试搜索
    print("\n3. 测试向量搜索...")
    try:
        # 使用相同的向量搜索
        query_text = "测试文档 Milvus"
        query_embedding = model.encode(query_text)
        
        if hasattr(query_embedding, 'tolist'):
            query_vec = query_embedding.tolist()
        else:
            query_vec = query_embedding
        
        results = milvus.search([query_vec], top_k=5)
        
        print(f"✓ 搜索完成，找到 {len(results)} 组结果")
        
        if results and len(results) > 0:
            print(f"\n搜索结果（前3个）:")
            for i, hit in enumerate(results[0][:3]):
                print(f"\n  结果 {i+1}:")
                print(f"    相似度: {hit.distance:.4f}")
                # 正确的获取entity属性的方式
                entity = hit.entity
                print(f"    文本: {entity.text[:100] if hasattr(entity, 'text') else 'N/A'}...")
                print(f"    标题: {entity.title if hasattr(entity, 'title') else 'N/A'}")
                print(f"    股票: {entity.ts_code if hasattr(entity, 'ts_code') else 'N/A'}")
                
                # 解析metadata
                metadata = entity.metadata if hasattr(entity, 'metadata') else {}
                if isinstance(metadata, dict):
                    print(f"    元数据: {json.dumps(metadata, ensure_ascii=False)}")
                
    except Exception as e:
        print(f"✗ 搜索测试失败: {e}")
    
    # 清理（可选）
    print("\n4. 测试完成")
    print("=" * 60)
    
    # 关闭连接
    milvus.close()


def test_real_announcement():
    """测试真实公告数据"""
    print("\n\n测试真实公告数据处理")
    print("=" * 60)
    
    try:
        from rag.document_processor import DocumentProcessor
        processor = DocumentProcessor()
        
        # 搜索已存储的公告
        print("\n搜索示例查询:")
        queries = [
            "2024年营业收入",
            "公司主营业务",
            "净利润增长"
        ]
        
        for query in queries:
            print(f"\n查询: '{query}'")
            results = processor.search_similar_documents(query, top_k=3)
            
            if results and len(results) > 0:
                # 处理不同的结果格式
                if isinstance(results[0], list):
                    actual_results = results[0]
                else:
                    actual_results = results
                
                for i, result in enumerate(actual_results[:2]):
                    if hasattr(result, 'entity'):
                        # Milvus Hit对象
                        print(f"  {i+1}. 相似度: {result.distance:.4f}")
                        print(f"     文本: {result.entity.get('text', '')[:100]}...")
                    else:
                        # 字典格式
                        print(f"  {i+1}. {result}")
            else:
                print("  没有找到相关结果")
                
    except Exception as e:
        print(f"测试失败: {e}")


def main():
    """主测试流程"""
    # 基本功能测试
    test_basic_operations()
    
    # 测试真实数据（如果有）
    # test_real_announcement()


if __name__ == "__main__":
    main()
