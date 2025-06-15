"""
强制加载Milvus集合
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pymilvus import connections, Collection, utility
from config.settings import settings
import time


def force_load_collection():
    """强制加载集合"""
    print("强制加载Milvus集合")
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
        print(f"✓ 连接成功")
        
        collection_name = settings.MILVUS_COLLECTION_NAME
        
        # 获取集合
        collection = Collection(collection_name)
        print(f"\n集合信息:")
        print(f"  名称: {collection_name}")
        print(f"  文档数: {collection.num_entities}")
        
        # 尝试释放集合（如果已加载）
        try:
            print("\n1. 尝试释放集合...")
            collection.release()
            print("✓ 集合已释放")
            time.sleep(2)  # 等待释放完成
        except Exception as e:
            print(f"  集合可能未加载: {e}")
        
        # 检查索引
        print("\n2. 检查索引...")
        indexes = collection.indexes
        if indexes:
            for idx in indexes:
                print(f"  ✓ 找到索引: {idx.field_name}")
        else:
            print("  ✗ 没有找到索引，创建索引...")
            index_params = {
                "metric_type": "IP",
                "index_type": "IVF_FLAT",
                "params": {"nlist": 128}
            }
            collection.create_index(
                field_name="embeddings",
                index_params=index_params
            )
            print("  ✓ 索引创建成功")
        
        # 强制加载集合
        print("\n3. 加载集合到内存...")
        collection.load()
        print("✓ 加载命令已发送")
        
        # 等待加载完成
        print("\n4. 等待加载完成...")
        max_wait = 30  # 最多等待30秒
        for i in range(max_wait):
            if utility.load_state(collection_name):
                print(f"✓ 集合加载成功! (耗时 {i+1} 秒)")
                break
            time.sleep(1)
            if i % 5 == 0:
                print(f"  等待中... ({i} 秒)")
        
        # 再次检查状态
        print("\n5. 验证加载状态...")
        load_progress = utility.loading_progress(collection_name)
        print(f"  加载进度: {load_progress}")
        
        # 测试搜索
        print("\n6. 测试搜索功能...")
        try:
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
            
            # 显示结果
            if len(results[0]) > 0:
                print("\n搜索结果示例:")
                for i, hit in enumerate(results[0][:3]):
                    print(f"\n{i+1}. 相似度: {hit.distance:.4f}")
                    entity = hit.entity
                    ts_code = entity.ts_code if hasattr(entity, 'ts_code') else 'N/A'
                    title = entity.title if hasattr(entity, 'title') else 'N/A'
                    text = entity.text[:100] if hasattr(entity, 'text') else 'N/A'
                    print(f"   股票: {ts_code}")
                    print(f"   标题: {title}")
                    print(f"   文本: {text}...")
            
            return True
            
        except Exception as e:
            print(f"✗ 搜索失败: {e}")
            print("\n可能的解决方案:")
            print("1. 重启Milvus服务")
            print("2. 检查Milvus服务器资源（内存、CPU）")
            print("3. 减少加载的数据量")
            return False
        
    except Exception as e:
        print(f"✗ 错误: {e}")
        return False
    finally:
        connections.disconnect("default")


def check_milvus_status():
    """检查Milvus服务状态"""
    print("\n\n检查Milvus服务状态")
    print("=" * 60)
    
    try:
        connections.connect(
            alias="default",
            host=settings.MILVUS_HOST,
            port=settings.MILVUS_PORT,
            user=settings.MILVUS_USER,
            password=settings.MILVUS_PASSWORD
        )
        
        # 获取所有集合
        collections = utility.list_collections()
        print(f"\n所有集合: {collections}")
        
        # 检查每个集合的状态
        for coll_name in collections:
            try:
                coll = Collection(coll_name)
                loaded = utility.load_state(coll_name)
                print(f"\n集合 '{coll_name}':")
                print(f"  实体数: {coll.num_entities}")
                print(f"  加载状态: {'已加载' if loaded else '未加载'}")
                if loaded:
                    progress = utility.loading_progress(coll_name)
                    print(f"  加载进度: {progress}")
            except Exception as e:
                print(f"  错误: {e}")
        
    except Exception as e:
        print(f"连接失败: {e}")
    finally:
        connections.disconnect("default")


if __name__ == "__main__":
    # 强制加载集合
    success = force_load_collection()
    
    # 检查服务状态
    check_milvus_status()
    
    if not success:
        print("\n" + "=" * 60)
        print("加载失败，请尝试以下步骤:")
        print("1. 重启Milvus服务")
        print("2. 在Milvus服务器上执行: docker restart milvus-standalone")
        print("3. 或者联系管理员检查服务器状态")
