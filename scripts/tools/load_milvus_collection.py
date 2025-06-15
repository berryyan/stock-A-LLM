"""
加载 Milvus 集合到内存
"""
from pymilvus import connections, Collection

# 连接 Milvus
connections.connect(
    alias="default",
    host="10.0.0.77",
    port="19530",
    user="root",
    password="Milvus"
)

# 加载集合
collection_name = "stock_announcements"
collection = Collection(collection_name)

print(f"加载集合 {collection_name}...")
collection.load()
print("✅ 集合已加载到内存")

# 检查状态
print(f"集合实体数: {collection.num_entities}")
print(f"是否已加载: {collection.is_empty == False}")
