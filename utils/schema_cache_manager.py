"""
数据库Schema缓存管理器
动态从数据库读取表结构和字段注释，建立中英文映射缓存
Created: 2025-06-28
Version: 1.0
"""

import time
import re
from typing import Dict, List, Optional, Tuple
from threading import Lock
import logging
from database.mysql_connector import MySQLConnector
from config.settings import settings

logger = logging.getLogger(__name__)

class SchemaCacheManager:
    """
    数据库Schema缓存管理器，单例模式
    负责从数据库动态读取表结构和字段注释，建立中英文映射缓存
    """
    _instance = None
    _lock = Lock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if hasattr(self, 'initialized'):
            return
        
        self.db_connector = MySQLConnector()
        self.schema_cache = {}
        self.field_index = {}  # 中文到英文字段的快速索引
        self.table_index = {}  # 中文到英文表名的索引
        self.reverse_field_index = {}  # 英文到中文的反向索引
        self.last_update = None
        self.cache_ttl = 3600  # 1小时缓存
        self._load_schema_from_db()
        self.initialized = True
    
    def _load_schema_from_db(self):
        """从数据库动态加载Schema信息"""
        logger.info("Loading database schema from INFORMATION_SCHEMA...")
        
        try:
            # 1. 获取所有表信息
            table_query = """
            SELECT 
                TABLE_NAME,
                TABLE_COMMENT,
                TABLE_ROWS
            FROM INFORMATION_SCHEMA.TABLES
            WHERE TABLE_SCHEMA = :database
                AND TABLE_NAME LIKE 'tu_%'
            ORDER BY TABLE_NAME
            """
            
            tables = self.db_connector.execute_query(
                table_query, 
                params={'database': settings.MYSQL_DATABASE}
            )
            
            # 2. 对每个表获取字段信息
            for table in tables:
                table_name = table['TABLE_NAME']
                table_comment = table['TABLE_COMMENT'] or table_name
                table_rows = table['TABLE_ROWS'] or 0
                
                # 解析表注释获取中文名
                table_cn = self._parse_comment(table_comment)['name']
                
                # 获取字段信息
                field_query = """
                SELECT 
                    COLUMN_NAME,
                    COLUMN_COMMENT,
                    DATA_TYPE,
                    COLUMN_TYPE,
                    IS_NULLABLE,
                    COLUMN_DEFAULT
                FROM INFORMATION_SCHEMA.COLUMNS
                WHERE TABLE_SCHEMA = :database
                    AND TABLE_NAME = :table_name
                ORDER BY ORDINAL_POSITION
                """
                
                fields = self.db_connector.execute_query(
                    field_query,
                    params={'database': settings.MYSQL_DATABASE, 'table_name': table_name}
                )
                
                # 构建表信息
                table_info = {
                    'table_cn': table_cn,
                    'description': table_comment,
                    'record_count': table_rows,
                    'fields': {}
                }
                
                # 处理每个字段
                for field in fields:
                    field_name = field['COLUMN_NAME']
                    field_comment = field['COLUMN_COMMENT'] or field_name
                    
                    # 解析字段注释
                    parsed = self._parse_comment(field_comment)
                    
                    field_info = {
                        'cn': parsed['name'],
                        'type': self._map_data_type(field['DATA_TYPE']),
                        'desc': field_comment,
                        'nullable': field['IS_NULLABLE'] == 'YES',
                        'default': field['COLUMN_DEFAULT']
                    }
                    
                    # 添加单位信息（如果有）
                    if parsed.get('unit'):
                        field_info['unit'] = parsed['unit']
                    
                    table_info['fields'][field_name] = field_info
                    
                    # 建立索引
                    self._add_to_index(table_name, field_name, parsed['name'], field_info)
                
                self.schema_cache[table_name] = table_info
                self.table_index[table_cn] = table_name
            
            self.last_update = time.time()
            logger.info(f"Schema loaded: {len(self.schema_cache)} tables, "
                       f"{len(self.field_index)} unique Chinese field names")
            
        except Exception as e:
            logger.error(f"Error loading schema from database: {e}")
            raise
    
    def _parse_comment(self, comment: str) -> Dict:
        """
        解析注释字符串，提取中文名称和单位
        
        支持的格式：
        - "股票代码"
        - "收盘价(元)"
        - "净资产收益率(%)"
        - "营业收入，单位：元"
        """
        result = {'name': comment, 'unit': None}
        
        if not comment:
            return result
        
        # 尝试匹配带括号的单位
        match = re.match(r'^(.+?)[\(（](.+?)[\)）]$', comment)
        if match:
            result['name'] = match.group(1).strip()
            result['unit'] = match.group(2).strip()
            return result
        
        # 尝试匹配"单位："格式
        match = re.match(r'^(.+?)[,，]\s*单位[：:]\s*(.+)$', comment)
        if match:
            result['name'] = match.group(1).strip()
            result['unit'] = match.group(2).strip()
            return result
        
        # 清理常见的后缀
        name = comment.strip()
        for suffix in ['，详见说明', '，详细说明', '(详见说明)']:
            if name.endswith(suffix):
                name = name[:-len(suffix)]
        
        result['name'] = name
        return result
    
    def _map_data_type(self, mysql_type: str) -> str:
        """MySQL数据类型映射"""
        type_mapping = {
            'varchar': 'str',
            'char': 'str',
            'text': 'str',
            'int': 'int',
            'bigint': 'int',
            'float': 'float',
            'double': 'float',
            'decimal': 'float',
            'date': 'date',
            'datetime': 'datetime',
            'timestamp': 'datetime',
            'time': 'time',
            'tinyint': 'bool',
            'boolean': 'bool'
        }
        
        mysql_type_lower = mysql_type.lower()
        for key, value in type_mapping.items():
            if mysql_type_lower.startswith(key):
                return value
        
        return 'str'  # 默认字符串类型
    
    def _add_to_index(self, table_name: str, field_name: str, field_cn: str, field_info: Dict):
        """添加到索引"""
        # 中文到英文索引
        if field_cn not in self.field_index:
            self.field_index[field_cn] = []
        
        self.field_index[field_cn].append({
            'table': table_name,
            'field': field_name,
            'info': field_info
        })
        
        # 英文到中文索引
        key = f"{table_name}.{field_name}"
        self.reverse_field_index[key] = {
            'cn': field_cn,
            'info': field_info
        }
    
    def refresh_cache(self, force: bool = False):
        """刷新缓存"""
        if force or (time.time() - self.last_update > self.cache_ttl):
            logger.info("Refreshing schema cache...")
            self._load_schema_from_db()
    
    def get_field_by_chinese(self, chinese_name: str, table_hint: str = None) -> Optional[Dict]:
        """
        根据中文字段名获取英文字段名
        
        Args:
            chinese_name: 中文字段名
            table_hint: 表名提示（可选）
            
        Returns:
            Dict with 'table', 'field', 'info' or None
        """
        self.refresh_cache()  # 检查是否需要刷新
        
        # 精确匹配
        if chinese_name in self.field_index:
            mappings = self.field_index[chinese_name]
            
            if len(mappings) == 1:
                return mappings[0]
            
            # 如果有多个映射且提供了表名提示
            if table_hint:
                for mapping in mappings:
                    if table_hint in mapping['table'] or \
                       table_hint in self.schema_cache.get(mapping['table'], {}).get('table_cn', ''):
                        return mapping
            
            # 返回第一个匹配
            return mappings[0]
        
        # 模糊匹配
        for cn_name, mappings in self.field_index.items():
            if chinese_name in cn_name or cn_name in chinese_name:
                if table_hint:
                    for mapping in mappings:
                        if table_hint in mapping['table']:
                            return mapping
                return mappings[0]
        
        return None
    
    def get_table_by_chinese(self, chinese_name: str) -> Optional[str]:
        """根据中文表名获取英文表名"""
        self.refresh_cache()
        
        # 精确匹配
        if chinese_name in self.table_index:
            return self.table_index[chinese_name]
        
        # 模糊匹配
        for cn_name, en_name in self.table_index.items():
            if chinese_name in cn_name or cn_name in chinese_name:
                return en_name
        
        return None
    
    def get_table_info(self, table_name: str) -> Optional[Dict]:
        """获取表的完整信息"""
        self.refresh_cache()
        return self.schema_cache.get(table_name)
    
    def get_field_chinese_name(self, table_name: str, field_name: str) -> Optional[str]:
        """获取字段的中文名称"""
        key = f"{table_name}.{field_name}"
        if key in self.reverse_field_index:
            return self.reverse_field_index[key]['cn']
        return None
    
    def get_all_tables(self) -> List[Dict]:
        """获取所有表的信息"""
        self.refresh_cache()
        result = []
        for table_name, table_info in self.schema_cache.items():
            result.append({
                'table_name': table_name,
                'table_cn': table_info['table_cn'],
                'description': table_info['description'],
                'record_count': table_info['record_count'],
                'field_count': len(table_info['fields'])
            })
        return sorted(result, key=lambda x: x['table_name'])
    
    def search_fields(self, keyword: str) -> List[Dict]:
        """搜索包含关键词的字段"""
        self.refresh_cache()
        results = []
        
        keyword_lower = keyword.lower()
        
        # 搜索中文字段名
        for field_cn, mappings in self.field_index.items():
            if keyword in field_cn:
                for mapping in mappings:
                    results.append({
                        'table': mapping['table'],
                        'field': mapping['field'],
                        'field_cn': field_cn,
                        'match_type': 'chinese_name'
                    })
        
        # 搜索英文字段名
        for table_name, table_info in self.schema_cache.items():
            for field_name, field_info in table_info['fields'].items():
                if keyword_lower in field_name.lower():
                    results.append({
                        'table': table_name,
                        'field': field_name,
                        'field_cn': field_info['cn'],
                        'match_type': 'english_name'
                    })
        
        return results
    
    def generate_sql_with_chinese(self, query_intent: Dict) -> Tuple[str, Dict]:
        """
        根据中文查询意图生成SQL
        
        Args:
            query_intent: {
                'tables': ['股票日线行情表'],
                'fields': ['收盘价', '成交量'],
                'conditions': {'股票代码': '600519.SH', 'days': 30}
            }
            
        Returns:
            (sql_query, field_mapping)
        """
        # 转换表名
        tables = []
        for table_cn in query_intent.get('tables', []):
            table_en = self.get_table_by_chinese(table_cn)
            if table_en:
                tables.append(table_en)
        
        if not tables:
            return None, {}
        
        # 转换字段名
        fields = []
        field_mapping = {}
        for field_cn in query_intent.get('fields', []):
            field_info = self.get_field_by_chinese(field_cn, tables[0] if tables else None)
            if field_info:
                field_en = field_info['field']
                fields.append(field_en)
                field_mapping[field_en] = field_cn
        
        # 构建基础SQL
        sql_parts = ["SELECT"]
        sql_parts.append(", ".join(fields) if fields else "*")
        sql_parts.append(f"FROM {tables[0]}")
        
        # 处理条件
        conditions = []
        for cond_cn, value in query_intent.get('conditions', {}).items():
            if cond_cn == 'days':
                # 特殊处理天数条件
                conditions.append(f"trade_date >= DATE_SUB(CURDATE(), INTERVAL {value} DAY)")
            else:
                field_info = self.get_field_by_chinese(cond_cn, tables[0])
                if field_info:
                    field_en = field_info['field']
                    if isinstance(value, str):
                        conditions.append(f"{field_en} = '{value}'")
                    else:
                        conditions.append(f"{field_en} = {value}")
        
        if conditions:
            sql_parts.append("WHERE " + " AND ".join(conditions))
        
        # 添加排序和限制
        if 'order_by' in query_intent:
            order_field = self.get_field_by_chinese(query_intent['order_by'], tables[0])
            if order_field:
                order_dir = query_intent.get('order_dir', 'DESC')
                sql_parts.append(f"ORDER BY {order_field['field']} {order_dir}")
        
        if 'limit' in query_intent:
            sql_parts.append(f"LIMIT {query_intent['limit']}")
        
        return " ".join(sql_parts), field_mapping
    
    def get_stats(self) -> Dict:
        """获取缓存统计信息"""
        return {
            'table_count': len(self.schema_cache),
            'field_count': sum(len(t['fields']) for t in self.schema_cache.values()),
            'chinese_field_count': len(self.field_index),
            'last_update': self.last_update,
            'cache_age_seconds': time.time() - self.last_update if self.last_update else 0
        }