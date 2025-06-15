"""
Milvus向量数据库连接器 - 修复版本
"""
from typing import List, Dict, Any, Optional
import logging
import json
from pymilvus import (
    connections, Collection, utility,
    FieldSchema, CollectionSchema, DataType
)

from config.settings import settings
from utils.logger import setup_logger


class MilvusConnector:
    """Milvus向量数据库连接器"""
    
    def __init__(self):
        self.logger = setup_logger("milvus_connector")
        self.collection_name = settings.MILVUS_COLLECTION_NAME
        self.collection = None
        
        # 连接到Milvus
        self._connect()
        
        # 初始化集合
        self._init_collection()
    
    def _connect(self):
        """连接到Milvus服务器"""
        try:
            connections.connect(
                alias="default",
                host=settings.MILVUS_HOST,
                port=settings.MILVUS_PORT,
                user=settings.MILVUS_USER,
                password=settings.MILVUS_PASSWORD
            )
            self.logger.info(f"Milvus连接成功: {settings.MILVUS_HOST}:{settings.MILVUS_PORT}")
        except Exception as e:
            self.logger.error(f"Milvus连接失败: {e}")
            raise
    
    def _init_collection(self):
        """初始化集合"""
        try:
            if utility.has_collection(self.collection_name):
                # 集合存在，直接加载
                self.collection = Collection(self.collection_name)
                self.logger.info(f"集合 '{self.collection_name}' 已存在")
                
                # 打印现有schema信息
                schema = self.collection.schema
                self.logger.info("现有字段:")
                for field in schema.fields:
                    self.logger.info(f"  - {field.name}: {field.dtype.name}")
                
                # 确保集合已加载 - 修复的关键部分
                self._ensure_collection_loaded()
            else:
                # 集合不存在，创建新集合
                self.logger.info(f"集合 '{self.collection_name}' 不存在，开始创建...")
                self._create_collection()
                
        except Exception as e:
            self.logger.error(f"初始化集合失败: {e}")
            raise
    
    def _ensure_collection_loaded(self):
        """确保集合已加载到内存"""
        try:
            # 获取加载状态
            load_state = utility.load_state(self.collection_name)
            self.logger.info(f"集合加载状态: {load_state}")
            
            # 检查是否需要加载
            if load_state.name != "Loaded":
                self.logger.info("集合未加载，正在加载到内存...")
                self.collection.load()
                self.logger.info("集合已成功加载到内存")
            else:
                self.logger.info("集合已在内存中")
                
        except Exception as e:
            # 如果出现"already loaded"错误，这是正常的
            if "loaded" in str(e).lower():
                self.logger.info("集合已在内存中")
            else:
                self.logger.error(f"加载集合时出错: {e}")
                raise
    
    def _create_collection(self):
        """创建新集合 - 使用与现有集合相同的schema"""
        try:
            # 定义字段 - 匹配现有schema
            fields = [
                FieldSchema(name="id", dtype=DataType.INT64, is_primary=True, auto_id=True),
                FieldSchema(name="doc_id", dtype=DataType.VARCHAR, max_length=100),
                FieldSchema(name="chunk_id", dtype=DataType.INT64),
                FieldSchema(name="ts_code", dtype=DataType.VARCHAR, max_length=20),
                FieldSchema(name="ann_date", dtype=DataType.VARCHAR, max_length=20),
                FieldSchema(name="title", dtype=DataType.VARCHAR, max_length=500),
                FieldSchema(name="text", dtype=DataType.VARCHAR, max_length=2000),
                FieldSchema(name="embeddings", dtype=DataType.FLOAT_VECTOR, dim=1024),
                FieldSchema(name="metadata", dtype=DataType.JSON)
            ]
            
            # 创建schema
            schema = CollectionSchema(
                fields=fields,
                description="Stock announcements and documents collection"
            )
            
            # 创建集合
            self.collection = Collection(
                name=self.collection_name,
                schema=schema
            )
            self.logger.info("集合创建成功")
            
            # 创建索引
            index_params = {
                "metric_type": "IP",
                "index_type": "IVF_FLAT",
                "params": {"nlist": 128}
            }
            self.collection.create_index(
                field_name="embeddings",
                index_params=index_params
            )
            self.logger.info("向量索引创建成功")
            
            # 加载集合
            self.collection.load()
            self.logger.info("集合已加载到内存")
            
        except Exception as e:
            self.logger.error(f"创建集合失败: {e}")
            raise
    
    def query(self, expr: str, output_fields: List[str] = None, limit: int = 10000) -> List[Dict[str, Any]]:
        """查询数据 - 添加了重试机制"""
        if not self.collection:
            self.logger.error("集合未初始化")
            return []
        
        try:
            # 确保集合已加载
            self._ensure_collection_loaded()
            
            if output_fields is None:
                output_fields = ["doc_id", "ts_code", "ann_date", "title"]
            
            # 执行查询
            results = self.collection.query(
                expr=expr,
                output_fields=output_fields,
                limit=limit
            )
            
            return results
            
        except Exception as e:
            self.logger.error(f"查询失败: {e}")
            
            # 如果是集合未加载错误，尝试重新加载并重试
            if "not loaded" in str(e).lower() or "code=101" in str(e):
                self.logger.info("检测到集合未加载，尝试重新加载...")
                try:
                    self._ensure_collection_loaded()
                    # 重试查询
                    results = self.collection.query(
                        expr=expr,
                        output_fields=output_fields,
                        limit=limit
                    )
                    return results
                except Exception as retry_e:
                    self.logger.error(f"重试查询失败: {retry_e}")
            
            return []
    
    def insert_data(self, data: List[Dict[str, Any]]) -> bool:
        """插入数据到集合"""
        if not self.collection:
            self.logger.error("集合未初始化")
            raise RuntimeError("集合未初始化")
        
        try:
            # 确保集合已加载
            self._ensure_collection_loaded()
            
            # 准备数据
            doc_ids = []
            chunk_ids = []
            ts_codes = []
            ann_dates = []
            titles = []
            texts = []
            embeddings = []
            metadatas = []
            
            for item in data:
                doc_ids.append(item['id'])
                chunk_ids.append(item['chunk_id'])
                ts_codes.append(item['ts_code'])
                ann_dates.append(str(item['ann_date']))
                titles.append(item['title'][:500])
                texts.append(item['text'][:2000])
                embeddings.append(item['embedding'])
                
                if isinstance(item['metadata'], str):
                    try:
                        metadata_json = json.loads(item['metadata'])
                    except:
                        metadata_json = {"raw": item['metadata']}
                else:
                    metadata_json = item['metadata']
                metadatas.append(metadata_json)
            
            # 插入数据
            insert_data = [
                doc_ids,
                chunk_ids,
                ts_codes,
                ann_dates,
                titles,
                texts,
                embeddings,
                metadatas
            ]
            
            self.collection.insert(insert_data)
            self.collection.flush()
            
            self.logger.info(f"成功插入 {len(data)} 条数据")
            return True
            
        except Exception as e:
            self.logger.error(f"插入数据失败: {e}")
            raise
    
    def search(self, 
              query_vectors: List[List[float]], 
              top_k: int = 5,
              filter_expr: Optional[str] = None) -> List[List[Dict[str, Any]]]:
        """向量搜索"""
        if not self.collection:
            self.logger.error("集合未初始化")
            raise RuntimeError("集合未初始化")
        
        try:
            # 确保集合已加载
            self._ensure_collection_loaded()
            
            # 搜索参数
            search_params = {
                "metric_type": "IP",
                "params": {"nprobe": 10}
            }
            
            # 输出字段
            output_fields = [
                "doc_id", "text", "ts_code", "title", 
                "ann_date", "chunk_id", "metadata"
            ]
            
            # 执行搜索
            results = self.collection.search(
                data=query_vectors,
                anns_field="embeddings",
                param=search_params,
                limit=top_k,
                expr=filter_expr,
                output_fields=output_fields
            )
            
            self.logger.debug(f"搜索完成，返回 {len(results)} 组结果")
            return results
            
        except Exception as e:
            self.logger.error(f"搜索失败: {e}")
            if "not loaded" in str(e).lower():
                self.logger.info("尝试重新加载集合...")
                self._ensure_collection_loaded()
                # 可以选择重试搜索
            raise
    
    def delete_by_expr(self, expr: str) -> bool:
        """根据表达式删除数据"""
        if not self.collection:
            self.logger.error("集合未初始化")
            raise RuntimeError("集合未初始化")
        
        try:
            self._ensure_collection_loaded()
            self.collection.delete(expr)
            self.collection.flush()
            self.logger.info(f"删除数据成功: {expr}")
            return True
        except Exception as e:
            self.logger.error(f"删除数据失败: {e}")
            return False
    
    def get_collection_stats(self) -> Dict[str, Any]:
        """获取集合统计信息"""
        if not self.collection:
            return {"error": "集合未初始化"}
        
        try:
            # 获取加载状态
            load_state = utility.load_state(self.collection_name)
            
            return {
                "name": self.collection.name,
                "row_count": self.collection.num_entities,
                "loaded": load_state.name == "Loaded",
                "load_state": load_state.name
            }
        except Exception as e:
            self.logger.error(f"获取统计信息失败: {e}")
            return {"error": str(e)}
    
    def close(self):
        """关闭连接"""
        try:
            if self.collection:
                self.collection.release()
            connections.disconnect("default")
            self.logger.info("Milvus连接已关闭")
        except Exception as e:
            self.logger.error(f"关闭连接失败: {e}")


# 测试代码保持不变
if __name__ == "__main__":
    # 测试连接器
    connector = MilvusConnector()
    
    # 获取统计信息
    stats = connector.get_collection_stats()
    print(f"集合统计: {stats}")
    
    # 测试查询已处理的公告
    print("\n测试查询已处理的公告...")
    results = connector.query("chunk_id == 0", limit=10)
    print(f"查询到 {len(results)} 条记录")
    
    connector.close()