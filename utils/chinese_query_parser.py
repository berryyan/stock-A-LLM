"""
中文查询解析器
将自然语言查询转换为结构化查询意图
Created: 2025-06-28
Version: 1.0
"""

import re
from typing import Dict, List, Optional
from utils.schema_cache_manager import SchemaCacheManager
from utils.stock_code_mapper import convert_to_ts_code
import logging

logger = logging.getLogger(__name__)

class ChineseQueryParser:
    """
    中文查询解析器，将自然语言转换为结构化查询
    """
    
    def __init__(self):
        self.schema_manager = SchemaCacheManager()
        self._init_patterns()
    
    def _init_patterns(self):
        """初始化查询模式"""
        # 查询类型模式
        self.query_patterns = {
            # 股价查询模式
            'stock_price': {
                'keywords': ['股价', '价格', '收盘价', '开盘价', '最高价', '最低价', '涨跌', '行情', '走势'],
                'patterns': [
                    r'(.+?)的?(?:最新|最近|今天|昨天)?(?:股价|收盘价|开盘价|最高价|最低价)',
                    r'(.+?)(?:最近|过去)?(\d+)天的(?:股价|走势|行情)',
                ],
                'default_table': '日线行情',
                'default_fields': ['开盘价', '最高价', '最低价', '收盘价', '成交量', '成交额']
            },
            
            # 财务分析模式
            'financial': {
                'keywords': ['财务', '财报', '年报', '季报', '利润', '营收', '净利润', '资产', '负债'],
                'patterns': [
                    r'(.+?)的?(?:财务|财报|年报|季报|利润|营收|净利润)',
                    r'分析(.+?)的?(?:财务状况|经营状况|盈利能力)',
                ],
                'default_table': '利润表',
                'default_fields': ['营业收入', '净利润', '净资产收益率', '总资产']
            },
            
            # 资金流向模式
            'money_flow': {
                'keywords': ['资金', '主力', '大单', '超大单', '流入', '流出', '资金流向'],
                'patterns': [
                    r'(.+?)的?(?:资金流向|主力资金|大单|超大单)',
                    r'(.+?)(?:最近|过去)?(\d+)天的资金流向',
                ],
                'default_table': '资金流向',
                'default_fields': ['特大单买入金额', '特大单卖出金额', '净流入金额']
            },
            
            # 估值指标模式
            'valuation': {
                'keywords': ['市盈率', '市净率', '市销率', 'PE', 'PB', 'PS', '估值', '市值'],
                'patterns': [
                    r'(.+?)的?(?:市盈率|市净率|市销率|PE|PB|PS)',
                    r'(.+?)的?(?:估值|总市值|流通市值)',
                ],
                'default_table': '每日基本面',
                'default_fields': ['市盈率', '市净率', '市销率', '总市值', '流通市值']
            },
            
            # 基本信息模式
            'basic_info': {
                'keywords': ['基本信息', '上市', '行业', '地域', '板块'],
                'patterns': [
                    r'(.+?)的?基本信息',
                    r'(.+?)是?(?:什么时候|何时)上市',
                    r'(.+?)属于什么(?:行业|板块)',
                ],
                'default_table': '股票基本信息',
                'default_fields': ['股票名称', '所属行业', '所在地域', '市场类型', '上市日期']
            }
        }
        
        # 时间模式
        self.time_patterns = {
            '最新|今天|今日': 0,
            '昨天|昨日': 1,
            '前天': 2,
            '最近(\d+)天': lambda m: int(m.group(1)),
            '过去(\d+)天': lambda m: int(m.group(1)),
            '(\d+)天前': lambda m: int(m.group(1)),
            '本周': 5,
            '上周': 10,
            '本月': 22,
            '上个月': 44,
            '今年': 250,
            '去年': 500
        }
        
        # 排序模式
        self.order_patterns = {
            '最高|最大|第一': ('DESC', 1),
            '最低|最小|倒数第一': ('ASC', 1),
            '前(\d+)': lambda m: ('DESC', int(m.group(1))),
            '后(\d+)': lambda m: ('ASC', int(m.group(1))),
            '排名|排行|排序': ('DESC', 10)
        }
    
    def parse_query(self, query: str) -> Dict:
        """
        解析中文查询，返回结构化查询意图
        
        Args:
            query: 中文查询语句
            
        Returns:
            {
                "query_type": "stock_price",
                "tables": ["tu_daily_detail"],
                "fields": ["close", "vol"],
                "conditions": {"ts_code": "600519.SH", "days": 30},
                "order_by": "trade_date",
                "order_dir": "DESC",
                "limit": 10,
                "original_query": "茅台最近30天的收盘价和成交量"
            }
        """
        result = {
            "original_query": query,
            "query_type": None,
            "tables": [],
            "fields": [],
            "conditions": {},
            "explain": []  # 解析说明
        }
        
        # 1. 识别查询类型
        query_type = self._identify_query_type(query)
        if query_type:
            result['query_type'] = query_type
            pattern_config = self.query_patterns[query_type]
            
            # 设置默认表
            default_table = self.schema_manager.get_table_by_chinese(pattern_config['default_table'])
            if default_table:
                result['tables'] = [default_table]
                result['explain'].append(f"识别到{pattern_config['default_table']}查询")
        
        # 2. 提取股票信息
        stock_info = self._extract_stock_info(query)
        if stock_info:
            result['conditions']['ts_code'] = stock_info['ts_code']
            result['explain'].append(f"识别到股票: {stock_info['name']}({stock_info['ts_code']})")
        
        # 3. 提取时间条件
        time_info = self._extract_time_condition(query)
        if time_info:
            result['conditions'].update(time_info)
            result['explain'].append(f"时间条件: {time_info}")
        
        # 4. 提取字段
        fields = self._extract_fields(query, result.get('tables', []))
        if fields:
            result['fields'] = fields
            result['explain'].append(f"查询字段: {fields}")
        elif query_type and pattern_config:
            # 使用默认字段
            default_fields = []
            for field_cn in pattern_config['default_fields']:
                field_info = self.schema_manager.get_field_by_chinese(
                    field_cn, 
                    result['tables'][0] if result['tables'] else None
                )
                if field_info:
                    default_fields.append(field_info['field'])
            result['fields'] = default_fields
            result['explain'].append(f"使用默认字段")
        
        # 5. 提取排序和限制
        order_info = self._extract_order_info(query)
        if order_info:
            result.update(order_info)
            result['explain'].append(f"排序: {order_info}")
        
        # 6. 如果没有识别到查询类型，尝试通用解析
        if not result['query_type']:
            result = self._generic_parse(query, result)
        
        logger.info(f"Parsed query: {query} -> {result}")
        return result
    
    def _identify_query_type(self, query: str) -> Optional[str]:
        """识别查询类型"""
        query_lower = query.lower()
        
        # 基于关键词匹配
        for query_type, config in self.query_patterns.items():
            for keyword in config['keywords']:
                if keyword in query:
                    return query_type
        
        # 基于模式匹配
        for query_type, config in self.query_patterns.items():
            for pattern in config['patterns']:
                if re.search(pattern, query):
                    return query_type
        
        return None
    
    def _extract_stock_info(self, query: str) -> Optional[Dict]:
        """提取股票信息"""
        # 常见的股票提取模式
        patterns = [
            r'([^的\s]+?)(?:的|股票|公司)',  # 茅台的、贵州茅台的
            r'(\d{6})(?:\.SH|\.SZ)?',  # 600519或600519.SH
            r'查询(.+?)的',  # 查询XX的
            r'分析(.+?)的',  # 分析XX的
        ]
        
        for pattern in patterns:
            match = re.search(pattern, query)
            if match:
                stock_str = match.group(1)
                # 过滤掉一些非股票词
                if stock_str not in ['最新', '今天', '昨天', '最近', '过去']:
                    ts_code = convert_to_ts_code(stock_str)
                    if ts_code:
                        # 获取股票名称
                        stock_basic = self.schema_manager.get_table_info('tu_stock_basic')
                        if stock_basic:
                            # 这里应该查询数据库获取股票名称，暂时返回原始输入
                            return {
                                'ts_code': ts_code,
                                'name': stock_str,
                                'original': stock_str
                            }
        
        return None
    
    def _extract_time_condition(self, query: str) -> Optional[Dict]:
        """提取时间条件"""
        for pattern, value in self.time_patterns.items():
            match = re.search(pattern, query)
            if match:
                if callable(value):
                    days = value(match)
                else:
                    days = value
                
                return {'days': days}
        
        # 检查具体日期
        date_match = re.search(r'(\d{4})[-年](\d{1,2})[-月](\d{1,2})', query)
        if date_match:
            year, month, day = date_match.groups()
            return {'date': f"{year}-{month:0>2}-{day:0>2}"}
        
        return None
    
    def _extract_fields(self, query: str, tables: List[str]) -> List[str]:
        """提取查询字段"""
        fields = []
        
        # 从缓存中搜索匹配的字段
        all_fields = self.schema_manager.field_index
        
        for field_cn in all_fields:
            if field_cn in query:
                # 如果已经确定了表，优先使用该表的字段
                if tables:
                    field_info = self.schema_manager.get_field_by_chinese(field_cn, tables[0])
                    if field_info:
                        fields.append(field_info['field'])
                else:
                    # 使用第一个匹配的字段
                    field_mappings = all_fields[field_cn]
                    if field_mappings:
                        fields.append(field_mappings[0]['field'])
        
        return list(set(fields))  # 去重
    
    def _extract_order_info(self, query: str) -> Optional[Dict]:
        """提取排序信息"""
        for pattern, value in self.order_patterns.items():
            match = re.search(pattern, query)
            if match:
                if callable(value):
                    order_dir, limit = value(match)
                else:
                    order_dir, limit = value
                
                result = {'order_dir': order_dir, 'limit': limit}
                
                # 尝试识别排序字段
                if '市值' in query:
                    result['order_by'] = 'total_mv'
                elif '涨幅' in query or '涨跌' in query:
                    result['order_by'] = 'pct_chg'
                elif '成交额' in query:
                    result['order_by'] = 'amount'
                elif '成交量' in query:
                    result['order_by'] = 'vol'
                else:
                    # 默认按日期排序
                    result['order_by'] = 'trade_date'
                
                return result
        
        return None
    
    def _generic_parse(self, query: str, result: Dict) -> Dict:
        """通用查询解析"""
        result['query_type'] = 'generic'
        
        # 尝试识别表名
        tables = self.schema_manager.get_all_tables()
        for table_info in tables:
            if table_info['table_cn'] in query:
                result['tables'] = [table_info['table_name']]
                result['explain'].append(f"识别到表: {table_info['table_cn']}")
                break
        
        # 如果没有找到表，搜索字段来推断表
        if not result['tables']:
            field_results = self.schema_manager.search_fields(query)
            if field_results:
                # 统计每个表出现的次数
                table_count = {}
                for field_result in field_results:
                    table = field_result['table']
                    table_count[table] = table_count.get(table, 0) + 1
                
                # 选择出现次数最多的表
                if table_count:
                    best_table = max(table_count.items(), key=lambda x: x[1])[0]
                    result['tables'] = [best_table]
                    result['explain'].append(f"根据字段推断表: {best_table}")
        
        # 提取字段
        if result['tables']:
            fields = self._extract_fields(query, result['tables'])
            if fields:
                result['fields'] = fields
        
        return result
    
    def generate_sql(self, query_intent: Dict) -> str:
        """根据解析结果生成SQL查询"""
        sql, field_mapping = self.schema_manager.generate_sql_with_chinese(query_intent)
        return sql
    
    def explain_query(self, query: str) -> str:
        """解释查询的解析过程"""
        result = self.parse_query(query)
        
        explanation = [
            f"原始查询: {query}",
            f"查询类型: {result.get('query_type', '未识别')}",
        ]
        
        if result.get('tables'):
            table_info = self.schema_manager.get_table_info(result['tables'][0])
            if table_info:
                explanation.append(f"查询表: {table_info['table_cn']} ({result['tables'][0]})")
        
        if result.get('fields'):
            field_names = []
            for field in result['fields']:
                field_cn = self.schema_manager.get_field_chinese_name(
                    result['tables'][0] if result.get('tables') else None,
                    field
                )
                field_names.append(f"{field_cn}({field})" if field_cn else field)
            explanation.append(f"查询字段: {', '.join(field_names)}")
        
        if result.get('conditions'):
            explanation.append(f"查询条件: {result['conditions']}")
        
        if result.get('explain'):
            explanation.append("解析过程:")
            for step in result['explain']:
                explanation.append(f"  - {step}")
        
        return '\n'.join(explanation)