"""
测试Milvus连接和集合状态
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pymilvus import connections, Collection, utility
from config.settings import settings
import json


def test_basic_connection():
    """测试基本连接"""
    print("1. 测试Milvus基本连接")
    print("-" * 60)
    
    try:
        # 连接到Milvus
        connections.connect(
            alias="default",
            host=settings.MILVUS_HOST,
            port=settings.MILVUS_PORT,
            user=settings.MILVUS_USER,
            password=settings.MILVUS_PASSWORD
        )
        print(f"✓ 连接成功: {settings.MILVUS_HOST}:{settings.MILVUS_PORT}")
        
        # 列出所有集合
        collections = utility.list_collections()
        print(f"\n现有集合: {collections}")
        
        return True
    except Exception as e:
        print(f"✗ 连接失败: {e}")
        return False


def test_collection_status():
    """测试集合状态"""
    print("\n\n2. 测试集合状态")
    print("-" * 60)
    
    collection_name = settings.MILVUS_COLLECTION_NAME
    print(f"目标集合: {collection_name}")
    
    try:
        # 检查集合是否存在
        if utility.has_collection(collection_name):
            print("✓ 集合存在")
            
            # 获取集合
            collection = Collection(collection_name)
            
            # 获取集合信息
            print(f"\n集合信息:")
            print(f"  名称: {collection.name}")
            print(f"  描述: {collection.description}")
            print(f"  实体数: {collection.num_entities}")
            
            # 获取schema
            schema = collection.schema
            print(f"\n字段信息:")
            for field in schema.fields:
                print(f"  - {field.name}: {field.dtype.name}")
                if field.name == "embedding":
                    print(f"    维度: {field.params.get('dim', 'N/A')}")
            
            # 检查索引
            print(f"\n索引信息:")
            indexes = collection.indexes
            for index in indexes:
                print(f"  - 字段: {index.field_name}")
                print(f"    参数: {index.params}")
            
            # 检查是否已加载
            print(f"\n集合是否已加载: {'是' if utility.load_state(collection_name) else '否'}")
            
            return collection
        else:
            print(f"✗ 集合 '{collection_name}' 不存在")
            return None
            
    except Exception as e:
        print(f"✗ 检查集合失败: {e}")
        return None


def create_collection_if_needed():
    """如果需要，创建集合"""
    print("\n\n3. 创建集合（如果需要）")
    print("-" * 60)
    
    collection_name = settings.MILVUS_COLLECTION_NAME
    
    if utility.has_collection(collection_name):
        print(f"集合 '{collection_name}' 已存在，跳过创建")
        return Collection(collection_name)
    
    print(f"集合不存在，开始创建...")
    
    try:
        from pymilvus import FieldSchema, CollectionSchema, DataType
        
        # 定义字段
        fields = [
            FieldSchema(name="id", dtype=DataType.VARCHAR, is_primary=True, max_length=100),
            FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=1024),
            FieldSchema(name="text", dtype=DataType.VARCHAR, max_length=2000),
            FieldSchema(name="ts_code", dtype=DataType.VARCHAR, max_length=20),
            FieldSchema(name="company_name", dtype=DataType.VARCHAR, max_length=100),
            FieldSchema(name="title", dtype=DataType.VARCHAR, max_length=500),
            FieldSchema(name="ann_date", dtype=DataType.VARCHAR, max_length=20),
            FieldSchema(name="chunk_id", dtype=DataType.INT64),
            FieldSchema(name="metadata", dtype=DataType.VARCHAR, max_length=2000)
        ]
        
        # 创建schema
        schema = CollectionSchema(
            fields=fields,
            description="Stock announcements for RAG"
        )
        
        # 创建集合
        collection = Collection(
            name=collection_name,
            schema=schema
        )
        
        print(f"✓ 集合创建成功")
        
        # 创建索引
        print("\n创建向量索引...")
        index_params = {
            "metric_type": "IP",  # 内积
            "index_type": "IVF_FLAT",
            "params": {"nlist": 128}
        }
        collection.create_index(
            field_name="embedding",
            index_params=index_params
        )
        print("✓ 索引创建成功")
        
        # 加载集合
        print("\n加载集合...")
        collection.load()
        print("✓ 集合加载成功")
        
        return collection
        
    except Exception as e:
        print(f"✗ 创建集合失败: {e}")
        return None


def test_simple_operations(collection):
    """测试简单的操作"""
    print("\n\n4. 测试简单操作")
    print("-" * 60)
    
    if not collection:
        print("没有可用的集合")
        return
    
    try:
        # 确保集合已加载
        if not utility.load_state(collection.name):
            print("加载集合...")
            collection.load()
        
        # 测试插入单条数据
        print("\n测试插入...")
        test_data = [
            ["test_simple_1"],  # id
            [[0.1] * 1024],  # embedding
            ["这是一个简单的测试文档"],  # text
            ["000001.SZ"],  # ts_code
            ["测试公司"],  # company_name
            ["测试公告标题"],  # title
            ["20250422"],  # ann_date
            [0],  # chunk_id
            ['{"test": "data"}']  # metadata
        ]
        
        collection.insert(test_data)
        collection.flush()
        print("✓ 插入成功")
        
        # 测试查询
        print("\n测试查询...")
        results = collection.query(
            expr='id == "test_simple_1"',
            output_fields=["id", "text", "company_name"]
        )
        
        if results:
            print("✓ 查询成功:")
            print(f"  找到 {len(results)} 条记录")
            for r in results:
                print(f"  - ID: {r['id']}, 公司: {r['company_name']}, 文本: {r['text'][:30]}...")
        
        # 删除测试数据
        print("\n清理测试数据...")
        collection.delete('id == "test_simple_1"')
        collection.flush()
        print("✓ 清理完成")
        
    except Exception as e:
        print(f"✗ 操作失败: {e}")


def main():
    """主测试流程"""
    print("Milvus连接诊断工具")
    print("=" * 60)
    
    # 打印配置
    print("当前配置:")
    print(f"  主机: {settings.MILVUS_HOST}")
    print(f"  端口: {settings.MILVUS_PORT}")
    print(f"  用户: {settings.MILVUS_USER}")
    print(f"  集合: {settings.MILVUS_COLLECTION_NAME}")
    
    # 测试连接
    if not test_basic_connection():
        print("\n请检查Milvus服务是否运行，以及网络连接是否正常")
        return
    
    # 测试集合
    collection = test_collection_status()
    
    # 创建集合（如果需要）
    if not collection:
        collection = create_collection_if_needed()
    
    # 测试操作
    test_simple_operations(collection)
    
    print("\n" + "=" * 60)
    print("诊断完成!")


if __name__ == "__main__":
    main()
