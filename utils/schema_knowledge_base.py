"""
数据库Schema知识库 - 性能优化核心模块
为所有Agent提供即时的数据定位服务，避免重复查询数据库Schema
Created: 2025-06-28
Version: 2.0
"""

import time
import json
from typing import Dict, List, Optional, Set, Tuple
from datetime import datetime, timedelta
import threading
from pathlib import Path

from database.mysql_connector import MySQLConnector
from utils.logger import setup_logger


class SchemaKnowledgeBase:
    """
    数据库Schema知识库 - 让Agent直接知道数据在哪里
    核心价值：将Schema查询时间从3-5秒降低到<10ms
    """
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if hasattr(self, 'initialized'):
            return
            
        self.logger = setup_logger("schema_knowledge_base")
        self.mysql = MySQLConnector()
        
        # 核心知识库
        self.table_knowledge = {}  # 表级知识
        self.field_knowledge = {}  # 字段级知识
        self.topic_knowledge = {}  # 主题知识（如"财务"、"股价"等）
        self.common_queries = {}   # 常用查询模式
        
        # 加载知识库
        self._load_knowledge_base()
        self.initialized = True
        
    def _load_knowledge_base(self):
        """加载完整的Schema知识库"""
        start_time = time.time()
        self.logger.info("开始构建Schema知识库...")
        
        # 1. 加载表结构
        self._load_table_structures()
        
        # 2. 构建主题分类
        self._build_topic_classification()
        
        # 3. 加载常用查询模式
        self._load_common_query_patterns()
        
        # 4. 构建快速索引
        self._build_fast_indexes()
        
        elapsed = time.time() - start_time
        self.logger.info(f"Schema知识库构建完成，耗时: {elapsed:.2f}秒")
        
    def _load_table_structures(self):
        """加载所有表结构信息"""
        # 获取所有表
        table_query = """
        SELECT 
            TABLE_NAME,
            TABLE_COMMENT,
            TABLE_ROWS
        FROM INFORMATION_SCHEMA.TABLES
        WHERE TABLE_SCHEMA = :database
            AND TABLE_NAME LIKE 'tu_%'
        """
        
        tables = self.mysql.execute_query(
            table_query,
            params={'database': 'Tushare'}
        )
        
        for table in tables:
            table_name = table['TABLE_NAME']
            
            # 获取字段信息
            field_query = """
            SELECT 
                COLUMN_NAME,
                COLUMN_COMMENT,
                DATA_TYPE,
                IS_NULLABLE,
                COLUMN_KEY
            FROM INFORMATION_SCHEMA.COLUMNS
            WHERE TABLE_SCHEMA = :database
                AND TABLE_NAME = :table_name
            ORDER BY ORDINAL_POSITION
            """
            
            fields = self.mysql.execute_query(
                field_query,
                params={'database': 'Tushare', 'table_name': table_name}
            )
            
            # 构建表知识
            self.table_knowledge[table_name] = {
                'comment': table['TABLE_COMMENT'],
                'row_count': table['TABLE_ROWS'],
                'fields': {f['COLUMN_NAME']: {
                    'comment': f['COLUMN_COMMENT'],
                    'type': f['DATA_TYPE'],
                    'nullable': f['IS_NULLABLE'] == 'YES',
                    'key': f['COLUMN_KEY']
                } for f in fields},
                'primary_fields': [],  # 主要字段
                'common_filters': [],  # 常用过滤条件
                'join_keys': []       # 关联键
            }
            
            # 识别主要字段
            self._identify_primary_fields(table_name)
            
    def _identify_primary_fields(self, table_name: str):
        """识别表的主要字段"""
        table_info = self.table_knowledge[table_name]
        fields = table_info['fields']
        
        # 根据表类型识别主要字段
        if table_name == 'tu_daily_detail':
            table_info['primary_fields'] = ['ts_code', 'trade_date', 'open', 'high', 'low', 'close', 'vol', 'amount']
            table_info['common_filters'] = ['ts_code', 'trade_date']
            
        elif table_name == 'tu_income':
            table_info['primary_fields'] = ['ts_code', 'end_date', 'revenue', 'n_income', 'total_revenue']
            table_info['common_filters'] = ['ts_code', 'end_date']
            
        elif table_name == 'tu_balancesheet':
            table_info['primary_fields'] = ['ts_code', 'end_date', 'total_assets', 'total_liab', 'total_hldr_eqy_inc_min_int']
            table_info['common_filters'] = ['ts_code', 'end_date']
            
        elif table_name == 'tu_cashflow':
            table_info['primary_fields'] = ['ts_code', 'end_date', 'n_cashflow_act', 'n_cashflow_inv_act', 'n_cash_flows_fnc_act']
            table_info['common_filters'] = ['ts_code', 'end_date']
            
        elif table_name == 'tu_fina_indicator':
            table_info['primary_fields'] = ['ts_code', 'end_date', 'roe', 'roa', 'net_profit_margin', 'gross_profit_margin']
            table_info['common_filters'] = ['ts_code', 'end_date']
            
        elif table_name == 'tu_moneyflow_dc':
            table_info['primary_fields'] = ['ts_code', 'trade_date', 'buy_elg_vol', 'sell_elg_vol', 'net_mf_vol']
            table_info['common_filters'] = ['ts_code', 'trade_date']
            
    def _build_topic_classification(self):
        """构建主题分类知识"""
        self.topic_knowledge = {
            '股价': {
                'tables': ['tu_daily_detail', 'tu_daily_basic'],
                'key_fields': ['open', 'high', 'low', 'close', 'vol', 'amount', 'pct_chg'],
                'description': '股票日线行情数据'
            },
            '财务': {
                'tables': ['tu_income', 'tu_balancesheet', 'tu_cashflow', 'tu_fina_indicator'],
                'key_fields': ['revenue', 'n_income', 'total_assets', 'roe', 'roa'],
                'description': '财务报表数据'
            },
            '资金流向': {
                'tables': ['tu_moneyflow_dc'],
                'key_fields': ['buy_elg_vol', 'sell_elg_vol', 'net_mf_vol'],
                'description': '个股资金流向数据'
            },
            '公告': {
                'tables': ['tu_anns_d'],
                'key_fields': ['ann_date', 'title', 'content'],
                'description': '上市公司公告数据'
            },
            '基本信息': {
                'tables': ['tu_stock_basic'],
                'key_fields': ['name', 'industry', 'market', 'list_date'],
                'description': '股票基本信息'
            },
            '估值': {
                'tables': ['tu_daily_basic'],
                'key_fields': ['pe', 'pb', 'ps', 'total_mv', 'circ_mv'],
                'description': '估值和市值数据'
            }
        }
        
    def _load_common_query_patterns(self):
        """加载常用查询模式"""
        self.common_queries = {
            '最新股价': {
                'table': 'tu_daily_detail',
                'fields': ['open', 'high', 'low', 'close', 'vol', 'amount'],
                'filter': 'trade_date = (SELECT MAX(trade_date) FROM tu_daily_detail WHERE ts_code = :ts_code)',
                'description': '查询最新交易日的股价'
            },
            '历史股价': {
                'table': 'tu_daily_detail',
                'fields': ['trade_date', 'open', 'high', 'low', 'close', 'vol', 'amount'],
                'filter': 'ts_code = :ts_code AND trade_date BETWEEN :start_date AND :end_date',
                'order': 'trade_date DESC',
                'description': '查询历史股价走势'
            },
            '财务健康度': {
                'tables': ['tu_income', 'tu_balancesheet', 'tu_cashflow', 'tu_fina_indicator'],
                'join_key': 'ts_code, end_date',
                'fields': {
                    'tu_income': ['revenue', 'n_income'],
                    'tu_balancesheet': ['total_assets', 'total_liab'],
                    'tu_cashflow': ['n_cashflow_act'],
                    'tu_fina_indicator': ['roe', 'roa', 'debt_to_assets']
                },
                'description': '财务健康度分析所需数据'
            },
            '资金流向分析': {
                'table': 'tu_moneyflow_dc',
                'fields': ['trade_date', 'buy_elg_vol', 'sell_elg_vol', 'buy_lg_vol', 'sell_lg_vol', 'net_mf_vol'],
                'filter': 'ts_code = :ts_code AND trade_date >= :start_date',
                'order': 'trade_date DESC',
                'description': '资金流向分析数据'
            }
        }
        
    def _build_fast_indexes(self):
        """构建快速索引"""
        # 字段到表的反向索引
        self.field_to_tables = {}
        for table_name, table_info in self.table_knowledge.items():
            for field_name in table_info['fields']:
                if field_name not in self.field_to_tables:
                    self.field_to_tables[field_name] = []
                self.field_to_tables[field_name].append(table_name)
                
        # 中文到英文的映射（核心字段）
        self.chinese_mapping = {
            # 股价相关
            '股票代码': 'ts_code',
            '交易日期': 'trade_date',
            '开盘价': 'open',
            '最高价': 'high',
            '最低价': 'low',
            '收盘价': 'close',
            '成交量': 'vol',
            '成交额': 'amount',
            '涨跌幅': 'pct_chg',
            
            # 财务相关
            '报告期': 'end_date',
            '营业收入': 'revenue',
            '净利润': 'n_income',
            '总资产': 'total_assets',
            '总负债': 'total_liab',
            '净资产收益率': 'roe',
            '总资产收益率': 'roa',
            
            # 资金流向
            '特大单买入': 'buy_elg_vol',
            '特大单卖出': 'sell_elg_vol',
            '大单买入': 'buy_lg_vol',
            '大单卖出': 'sell_lg_vol',
            '净流入': 'net_mf_vol',
            
            # 估值相关
            '市盈率': 'pe',
            '市净率': 'pb',
            '市销率': 'ps',
            '总市值': 'total_mv',
            '流通市值': 'circ_mv'
        }
        
    # ========== 核心API：快速数据定位 ==========
    
    def locate_data(self, data_name: str) -> Optional[Dict]:
        """
        快速定位数据位置
        输入：数据名称（中文或英文）
        输出：{'table': 'tu_xxx', 'field': 'xxx', 'type': 'float', 'comment': 'xxx'}
        """
        # 尝试中文映射
        field_name = self.chinese_mapping.get(data_name, data_name)
        
        # 查找字段所在的表
        if field_name in self.field_to_tables:
            tables = self.field_to_tables[field_name]
            # 返回第一个匹配的表（通常最常用）
            table_name = tables[0]
            field_info = self.table_knowledge[table_name]['fields'].get(field_name, {})
            
            return {
                'table': table_name,
                'field': field_name,
                'type': field_info.get('type', 'unknown'),
                'comment': field_info.get('comment', ''),
                'all_tables': tables  # 所有包含此字段的表
            }
        
        return None
        
    def get_tables_for_topic(self, topic: str) -> List[str]:
        """
        获取主题相关的表
        输入：主题名称（如"股价"、"财务"）
        输出：相关表列表
        """
        topic_info = self.topic_knowledge.get(topic, {})
        return topic_info.get('tables', [])
        
    def get_query_template(self, query_type: str) -> Optional[Dict]:
        """
        获取常用查询模板
        输入：查询类型（如"最新股价"）
        输出：查询模板信息
        """
        return self.common_queries.get(query_type)
        
    def get_financial_analysis_tables(self) -> Dict[str, List[str]]:
        """
        获取财务分析所需的表和字段
        专门为Financial Agent优化
        """
        return {
            'tu_income': ['ts_code', 'end_date', 'revenue', 'n_income', 'total_revenue'],
            'tu_balancesheet': ['ts_code', 'end_date', 'total_assets', 'total_liab', 'total_hldr_eqy_inc_min_int'],
            'tu_cashflow': ['ts_code', 'end_date', 'n_cashflow_act', 'n_cashflow_inv_act'],
            'tu_fina_indicator': ['ts_code', 'end_date', 'roe', 'roa', 'debt_to_assets', 'current_ratio']
        }
        
    def get_money_flow_fields(self) -> List[str]:
        """
        获取资金流向分析字段
        专门为MoneyFlow Agent优化
        """
        return [
            'ts_code', 'trade_date',
            'buy_elg_vol', 'sell_elg_vol',  # 特大单
            'buy_lg_vol', 'sell_lg_vol',    # 大单
            'buy_md_vol', 'sell_md_vol',    # 中单
            'buy_sm_vol', 'sell_sm_vol',    # 小单
            'net_mf_vol'                     # 净流入
        ]
        
    def suggest_fields_for_query(self, query_keywords: List[str]) -> Dict[str, List[str]]:
        """
        根据查询关键词建议需要的字段
        输入：查询关键词列表
        输出：{table: [fields]}
        """
        suggested = {}
        
        for keyword in query_keywords:
            # 检查是否是已知的数据名称
            location = self.locate_data(keyword)
            if location:
                table = location['table']
                if table not in suggested:
                    suggested[table] = []
                suggested[table].append(location['field'])
                
            # 检查是否匹配主题
            for topic, info in self.topic_knowledge.items():
                if keyword in topic or topic in keyword:
                    for table in info['tables']:
                        if table not in suggested:
                            suggested[table] = []
                        # 添加该主题的关键字段
                        table_info = self.table_knowledge.get(table, {})
                        suggested[table].extend(table_info.get('primary_fields', []))
                        
        # 去重
        for table in suggested:
            suggested[table] = list(set(suggested[table]))
            
        return suggested
        
    def get_join_strategy(self, tables: List[str]) -> Optional[Dict]:
        """
        获取多表连接策略
        输入：需要连接的表列表
        输出：连接策略
        """
        if len(tables) < 2:
            return None
            
        # 财务表连接策略
        financial_tables = {'tu_income', 'tu_balancesheet', 'tu_cashflow', 'tu_fina_indicator'}
        if set(tables).issubset(financial_tables):
            return {
                'join_key': ['ts_code', 'end_date'],
                'join_type': 'LEFT JOIN',
                'base_table': 'tu_income'  # 以利润表为基准
            }
            
        # 其他连接策略...
        return None
        
    def get_performance_stats(self) -> Dict:
        """获取性能统计信息"""
        return {
            'table_count': len(self.table_knowledge),
            'field_count': sum(len(t['fields']) for t in self.table_knowledge.values()),
            'topic_count': len(self.topic_knowledge),
            'query_template_count': len(self.common_queries),
            'chinese_mapping_count': len(self.chinese_mapping)
        }


# 单例实例
schema_kb = SchemaKnowledgeBase()


if __name__ == "__main__":
    # 测试知识库
    kb = SchemaKnowledgeBase()
    
    # 测试数据定位
    print("测试数据定位:")
    print(f"营业收入 -> {kb.locate_data('营业收入')}")
    print(f"收盘价 -> {kb.locate_data('收盘价')}")
    
    # 测试主题查询
    print("\n测试主题查询:")
    print(f"财务相关表: {kb.get_tables_for_topic('财务')}")
    
    # 测试查询模板
    print("\n测试查询模板:")
    print(f"最新股价: {kb.get_query_template('最新股价')}")
    
    # 性能统计
    print("\n性能统计:")
    print(kb.get_performance_stats())