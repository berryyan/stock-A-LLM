"""
加载Milvus集合到内存
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pymilvus import connections, Collection, utility
from config.settings import settings


def load_collection():
    """加载集合到内存"""
    print("加载Milvus集合")
    print("=" * 60)
    
    try:
        # 连接Milvus
        connections.connect(
            alias="default",
            host=settings.MILVUS_HOST,
            port=settings.MILVUS_PORT,
            user=settings.MILVUS_USER,
            password=settings.MILVUS_PASSWORD
        )
        print(f"✓ 连接成功: {settings.MILVUS_HOST}:{settings.MILVUS_PORT}")
        
        # 获取集合
        collection_name = settings.MILVUS_COLLECTION_NAME
        collection = Collection(collection_name)
        
        # 检查当前状态
        print(f"\n集合: {collection_name}")
        print(f"文档数: {collection.num_entities}")
        print(f"当前状态: {'已加载' if utility.load_state(collection_name) else '未加载'}")
        
        # 加载集合
        if not utility.load_state(collection_name):
            print("\n开始加载集合到内存...")
            collection.load()
            print("✓ 集合加载成功!")
        else:
            print("\n集合已经在内存中")
        
        # 测试搜索
        print("\n测试搜索功能...")
        test_vector = [0.1] * 1024
        search_params = {
            "metric_type": "IP",
            "params": {"nprobe": 10}
        }
        
        results = collection.search(
            data=[test_vector],
            anns_field="embeddings",
            param=search_params,
            limit=5,
            output_fields=["text", "title", "ts_code"]
        )
        
        print(f"✓ 搜索成功! 找到 {len(results[0])} 个结果")
        
        # 显示搜索结果
        if len(results[0]) > 0:
            print("\n搜索结果示例:")
            for i, hit in enumerate(results[0][:3]):
                entity = hit.entity
                print(f"\n{i+1}. 相似度: {hit.distance:.4f}")
                print(f"   股票: {entity.ts_code if hasattr(entity, 'ts_code') else 'N/A'}")
                print(f"   标题: {entity.title if hasattr(entity, 'title') else 'N/A'}")
                print(f"   文本: {entity.text[:100] if hasattr(entity, 'text') else 'N/A'}...")
        
        return True
        
    except Exception as e:
        print(f"✗ 错误: {e}")
        return False
    finally:
        connections.disconnect("default")


if __name__ == "__main__":
    load_collection()
