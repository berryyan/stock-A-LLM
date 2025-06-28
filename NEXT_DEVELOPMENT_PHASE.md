# 下一步开发计划 - Stock Analysis System v2.0

**文档版本**: v4.0  
**更新日期**: 2025-06-28  
**当前版本**: v1.5.4 (流式响应完成，准备v2.0后端优化)  
**当前分支**: dev-react-frontend-v2  
**重大决策**: 优先实施数据库Schema中文映射缓存系统

## 📋 目录

1. [当前状态总结](#当前状态总结)
2. [Phase 1: 数据库Schema中文映射缓存系统](#phase-1-数据库schema中文映射缓存系统)
3. [Phase 2: 性能优化与缓存系统](#phase-2-性能优化与缓存系统)
4. [Phase 3: 技术分析系统](#phase-3-技术分析系统)
5. [Phase 4: 智能分析增强](#phase-4-智能分析增强)
6. [实施优先级和预期成果](#实施优先级和预期成果)
7. [技术栈确认](#技术栈确认)
8. [已完成功能总结](#已完成功能总结)

## 当前状态总结

### v1.5.4 成就回顾
- ✅ React前端MVP完成95%（Claude.ai风格界面）
- ✅ 流式响应功能完整实现（WebSocket + 打字效果）
- ✅ 停止查询按钮功能
- ✅ 深色主题优化和分屏布局一致性
- ✅ 双环境开发方案成熟（WSL2开发 + Windows测试）

### 系统现状
- **前端**: 功能完整，待添加数据可视化组件
- **后端**: 功能完整但存在性能优化空间
- **性能瓶颈**: 
  - SQL查询5-30秒（需要缓存优化）
  - RAG查询3-15秒（需要智能降级）
  - 每次查询都重新获取数据库Schema（需要缓存）

## 🎯 Phase 1: 数据库Schema中文映射缓存系统（第1-2周）⭐最高优先级

### 1.1 Schema映射配置系统（3-4天）

#### 创建核心配置文件
**文件**: `config/db_schema_chinese_mapping.py`

```python
# 完整的数据库表和字段中文映射
DB_SCHEMA_CHINESE = {
    # 基础信息表
    "tu_stock_basic": {
        "table_cn": "股票基本信息表",
        "description": "所有股票的基础信息，包含5418只股票",
        "fields": {
            "ts_code": {"cn": "股票代码", "type": "str", "example": "600519.SH"},
            "symbol": {"cn": "股票符号", "type": "str", "example": "600519"},
            "name": {"cn": "股票名称", "type": "str", "example": "贵州茅台"},
            "area": {"cn": "所在地域", "type": "str", "example": "贵州"},
            "industry": {"cn": "所属行业", "type": "str", "example": "白酒"},
            "market": {"cn": "市场类型", "type": "str", "values": ["主板", "创业板", "科创板", "北交所"]},
            "list_status": {"cn": "上市状态", "type": "str", "values": {"L": "上市", "D": "退市", "P": "暂停上市"}},
            "list_date": {"cn": "上市日期", "type": "date", "format": "YYYYMMDD"}
        }
    },
    
    # 日线行情表
    "tu_daily_detail": {
        "table_cn": "股票日线行情表",
        "description": "每日价格和成交数据，1564万条记录",
        "fields": {
            "ts_code": {"cn": "股票代码", "type": "str"},
            "trade_date": {"cn": "交易日期", "type": "date"},
            "open": {"cn": "开盘价", "type": "float", "unit": "元"},
            "high": {"cn": "最高价", "type": "float", "unit": "元"},
            "low": {"cn": "最低价", "type": "float", "unit": "元"},
            "close": {"cn": "收盘价", "type": "float", "unit": "元"},
            "pre_close": {"cn": "昨收价", "type": "float", "unit": "元"},
            "change": {"cn": "涨跌额", "type": "float", "unit": "元"},
            "pct_chg": {"cn": "涨跌幅", "type": "float", "unit": "%"},
            "vol": {"cn": "成交量", "type": "float", "unit": "手"},
            "amount": {"cn": "成交额", "type": "float", "unit": "千元"}
        }
    },
    
    # 每日基本面表
    "tu_daily_basic": {
        "table_cn": "每日基本面指标表",
        "description": "每日估值和基本面指标，630万条记录",
        "fields": {
            "turnover_rate": {"cn": "换手率", "type": "float", "unit": "%"},
            "turnover_rate_f": {"cn": "换手率(自由流通股)", "type": "float", "unit": "%"},
            "volume_ratio": {"cn": "量比", "type": "float"},
            "pe": {"cn": "市盈率", "type": "float"},
            "pe_ttm": {"cn": "市盈率TTM", "type": "float"},
            "pb": {"cn": "市净率", "type": "float"},
            "ps": {"cn": "市销率", "type": "float"},
            "ps_ttm": {"cn": "市销率TTM", "type": "float"},
            "dv_ratio": {"cn": "股息率", "type": "float", "unit": "%"},
            "dv_ttm": {"cn": "股息率TTM", "type": "float", "unit": "%"},
            "total_share": {"cn": "总股本", "type": "float", "unit": "万股"},
            "float_share": {"cn": "流通股本", "type": "float", "unit": "万股"},
            "free_share": {"cn": "自由流通股本", "type": "float", "unit": "万股"},
            "total_mv": {"cn": "总市值", "type": "float", "unit": "万元"},
            "circ_mv": {"cn": "流通市值", "type": "float", "unit": "万元"}
        }
    },
    
    # 财务报表映射（460个字段）
    "tu_income": {
        "table_cn": "利润表",
        "description": "公司损益数据，83个字段，12.9万条记录",
        "fields": {
            "ts_code": {"cn": "股票代码", "type": "str"},
            "ann_date": {"cn": "公告日期", "type": "date"},
            "f_ann_date": {"cn": "实际公告日期", "type": "date"},
            "end_date": {"cn": "报告期", "type": "date"},
            "report_type": {"cn": "报告类型", "type": "str"},
            "comp_type": {"cn": "公司类型", "type": "str"},
            "end_type": {"cn": "报告期类型", "type": "str"},
            "total_revenue": {"cn": "营业总收入", "type": "float", "unit": "元"},
            "revenue": {"cn": "营业收入", "type": "float", "unit": "元"},
            "int_income": {"cn": "利息收入", "type": "float", "unit": "元"},
            "comm_income": {"cn": "手续费及佣金收入", "type": "float", "unit": "元"},
            "total_cogs": {"cn": "营业总成本", "type": "float", "unit": "元"},
            "oper_cost": {"cn": "营业成本", "type": "float", "unit": "元"},
            "sell_exp": {"cn": "销售费用", "type": "float", "unit": "元"},
            "admin_exp": {"cn": "管理费用", "type": "float", "unit": "元"},
            "fin_exp": {"cn": "财务费用", "type": "float", "unit": "元"},
            "rd_exp": {"cn": "研发费用", "type": "float", "unit": "元"},
            "operate_profit": {"cn": "营业利润", "type": "float", "unit": "元"},
            "total_profit": {"cn": "利润总额", "type": "float", "unit": "元"},
            "income_tax": {"cn": "所得税费用", "type": "float", "unit": "元"},
            "n_income": {"cn": "净利润", "type": "float", "unit": "元"},
            "n_income_attr_p": {"cn": "归属母公司净利润", "type": "float", "unit": "元"},
            "basic_eps": {"cn": "基本每股收益", "type": "float", "unit": "元"},
            "diluted_eps": {"cn": "稀释每股收益", "type": "float", "unit": "元"}
            # ... 其他字段省略
        }
    },
    
    "tu_balancesheet": {
        "table_cn": "资产负债表",
        "description": "资产负债数据，161个字段，12.7万条记录",
        "fields": {
            "money_cap": {"cn": "货币资金", "type": "float", "unit": "元"},
            "accounts_receiv": {"cn": "应收账款", "type": "float", "unit": "元"},
            "inventories": {"cn": "存货", "type": "float", "unit": "元"},
            "total_cur_assets": {"cn": "流动资产合计", "type": "float", "unit": "元"},
            "fix_assets": {"cn": "固定资产", "type": "float", "unit": "元"},
            "total_assets": {"cn": "资产总计", "type": "float", "unit": "元"},
            "st_borr": {"cn": "短期借款", "type": "float", "unit": "元"},
            "accounts_pay": {"cn": "应付账款", "type": "float", "unit": "元"},
            "total_cur_liab": {"cn": "流动负债合计", "type": "float", "unit": "元"},
            "lt_borr": {"cn": "长期借款", "type": "float", "unit": "元"},
            "total_liab": {"cn": "负债合计", "type": "float", "unit": "元"},
            "total_share": {"cn": "期末总股本", "type": "float", "unit": "股"},
            "cap_rese": {"cn": "资本公积金", "type": "float", "unit": "元"},
            "surplus_rese": {"cn": "盈余公积金", "type": "float", "unit": "元"},
            "undistr_porfit": {"cn": "未分配利润", "type": "float", "unit": "元"},
            "total_hldr_eqy_inc_min_int": {"cn": "股东权益合计", "type": "float", "unit": "元"}
            # ... 其他字段省略
        }
    },
    
    "tu_cashflow": {
        "table_cn": "现金流量表",
        "description": "现金流量数据，73个字段，12.2万条记录",
        "fields": {
            "c_fr_sale_sg": {"cn": "销售商品提供劳务收到的现金", "type": "float", "unit": "元"},
            "c_paid_goods_s": {"cn": "购买商品接受劳务支付的现金", "type": "float", "unit": "元"},
            "c_paid_to_for_empl": {"cn": "支付给职工的现金", "type": "float", "unit": "元"},
            "n_cashflow_act": {"cn": "经营活动现金流量净额", "type": "float", "unit": "元"},
            "c_disp_withdrwl_invest": {"cn": "收回投资收到的现金", "type": "float", "unit": "元"},
            "c_pay_acq_const_fiolta": {"cn": "购建固定资产支付的现金", "type": "float", "unit": "元"},
            "n_cashflow_inv_act": {"cn": "投资活动现金流量净额", "type": "float", "unit": "元"},
            "c_proc_borrow": {"cn": "取得借款收到的现金", "type": "float", "unit": "元"},
            "c_prepay_amt_borr": {"cn": "偿还债务支付的现金", "type": "float", "unit": "元"},
            "c_pay_dist_dpcp_int_exp": {"cn": "分配股利支付的现金", "type": "float", "unit": "元"},
            "n_cash_flows_fnc_act": {"cn": "筹资活动现金流量净额", "type": "float", "unit": "元"}
            # ... 其他字段省略
        }
    },
    
    "tu_fina_indicator": {
        "table_cn": "财务指标表",
        "description": "计算好的财务指标，143个字段，13.8万条记录",
        "fields": {
            "roe": {"cn": "净资产收益率", "type": "float", "unit": "%"},
            "roe_waa": {"cn": "加权平均净资产收益率", "type": "float", "unit": "%"},
            "roe_dt": {"cn": "净资产收益率(扣非)", "type": "float", "unit": "%"},
            "roa": {"cn": "总资产报酬率", "type": "float", "unit": "%"},
            "roa2": {"cn": "总资产净利润率", "type": "float", "unit": "%"},
            "debt_to_assets": {"cn": "资产负债率", "type": "float", "unit": "%"},
            "assets_to_eqt": {"cn": "权益乘数", "type": "float"},
            "current_ratio": {"cn": "流动比率", "type": "float"},
            "quick_ratio": {"cn": "速动比率", "type": "float"},
            "ar_turn": {"cn": "应收账款周转率", "type": "float", "unit": "次"},
            "inv_turn": {"cn": "存货周转率", "type": "float", "unit": "次"},
            "turn_days": {"cn": "营业周期", "type": "float", "unit": "天"}
            # ... 其他字段省略
        }
    },
    
    "tu_moneyflow_dc": {
        "table_cn": "资金流向表",
        "description": "个股资金流向数据，16个字段，241万条记录",
        "fields": {
            "trade_date": {"cn": "交易日期", "type": "date"},
            "ts_code": {"cn": "股票代码", "type": "str"},
            "buy_sm_amount": {"cn": "小单买入金额", "type": "float", "unit": "万元"},
            "buy_md_amount": {"cn": "中单买入金额", "type": "float", "unit": "万元"},
            "buy_lg_amount": {"cn": "大单买入金额", "type": "float", "unit": "万元"},
            "buy_elg_amount": {"cn": "特大单买入金额", "type": "float", "unit": "万元"},
            "sell_sm_amount": {"cn": "小单卖出金额", "type": "float", "unit": "万元"},
            "sell_md_amount": {"cn": "中单卖出金额", "type": "float", "unit": "万元"},
            "sell_lg_amount": {"cn": "大单卖出金额", "type": "float", "unit": "万元"},
            "sell_elg_amount": {"cn": "特大单卖出金额", "type": "float", "unit": "万元"},
            "net_mf_amount": {"cn": "净流入金额", "type": "float", "unit": "万元"}
        }
    },
    
    "tu_anns_d": {
        "table_cn": "公告数据表",
        "description": "上市公司公告，7个字段，209万条记录",
        "fields": {
            "ann_date": {"cn": "公告日期", "type": "date"},
            "ts_code": {"cn": "股票代码", "type": "str"},
            "name": {"cn": "公司名称", "type": "str"},
            "title": {"cn": "公告标题", "type": "str"},
            "content": {"cn": "公告内容", "type": "str"},
            "url": {"cn": "公告链接", "type": "str"},
            "rec_time": {"cn": "录入时间", "type": "datetime"}
        }
    }
}

# 常用查询模板
QUERY_TEMPLATES = {
    "股价查询": {
        "tables": ["tu_daily_detail"],
        "common_fields": ["open", "high", "low", "close", "vol", "amount"],
        "conditions": ["ts_code", "trade_date"]
    },
    "财务分析": {
        "tables": ["tu_income", "tu_balancesheet", "tu_cashflow", "tu_fina_indicator"],
        "common_fields": ["revenue", "n_income_attr_p", "total_assets", "roe"],
        "conditions": ["ts_code", "end_date"]
    },
    "资金流向": {
        "tables": ["tu_moneyflow_dc"],
        "common_fields": ["buy_elg_amount", "sell_elg_amount", "net_mf_amount"],
        "conditions": ["ts_code", "trade_date"]
    }
}
```

### 1.2 缓存管理器实现（2-3天）

**文件**: `utils/schema_cache_manager.py`

```python
import time
from typing import Dict, List, Optional, Tuple
from threading import Lock
import logging
from config.db_schema_chinese_mapping import DB_SCHEMA_CHINESE, QUERY_TEMPLATES

logger = logging.getLogger(__name__)

class SchemaCacheManager:
    """
    数据库Schema缓存管理器，单例模式
    负责管理数据库表结构的中英文映射缓存
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
        
        self.schema_cache = {}
        self.field_index = {}  # 中文到英文字段的快速索引
        self.table_index = {}  # 中文到英文表名的索引
        self.reverse_field_index = {}  # 英文到中文的反向索引
        self.last_update = None
        self.cache_ttl = 604800  # 7天
        self._load_schema()
        self.initialized = True
        
    def _load_schema(self):
        """启动时加载所有Schema到内存"""
        logger.info("Loading database schema mappings...")
        
        # 加载基础映射
        self.schema_cache = DB_SCHEMA_CHINESE.copy()
        
        # 建立索引
        for table_name, table_info in DB_SCHEMA_CHINESE.items():
            # 表名索引
            table_cn = table_info.get('table_cn', '')
            self.table_index[table_cn] = table_name
            
            # 字段索引
            fields = table_info.get('fields', {})
            for field_name, field_info in fields.items():
                field_cn = field_info.get('cn', '')
                
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
        
        self.last_update = time.time()
        logger.info(f"Schema loaded: {len(self.schema_cache)} tables, "
                   f"{len(self.field_index)} unique Chinese field names")
    
    def get_field_by_chinese(self, chinese_name: str, table_hint: str = None) -> Optional[Dict]:
        """
        根据中文字段名获取英文字段名
        
        Args:
            chinese_name: 中文字段名
            table_hint: 表名提示（可选）
            
        Returns:
            Dict with 'table', 'field', 'info' or None
        """
        if chinese_name not in self.field_index:
            # 尝试模糊匹配
            for cn_name, mappings in self.field_index.items():
                if chinese_name in cn_name or cn_name in chinese_name:
                    if table_hint:
                        # 如果有表名提示，优先返回匹配的表
                        for mapping in mappings:
                            if table_hint in mapping['table']:
                                return mapping
                    return mappings[0]
            return None
        
        mappings = self.field_index[chinese_name]
        
        # 如果只有一个映射，直接返回
        if len(mappings) == 1:
            return mappings[0]
        
        # 如果有多个映射且提供了表名提示
        if table_hint:
            for mapping in mappings:
                if table_hint in mapping['table'] or table_hint in self.schema_cache.get(mapping['table'], {}).get('table_cn', ''):
                    return mapping
        
        # 返回第一个匹配
        return mappings[0]
    
    def get_table_by_chinese(self, chinese_name: str) -> Optional[str]:
        """根据中文表名获取英文表名"""
        # 精确匹配
        if chinese_name in self.table_index:
            return self.table_index[chinese_name]
        
        # 模糊匹配
        for cn_name, en_name in self.table_index.items():
            if chinese_name in cn_name or cn_name in chinese_name:
                return en_name
        
        return None
    
    def get_table_info(self, table_name: str) -> Optional[Dict]:
        """获取表的完整中文信息"""
        return self.schema_cache.get(table_name)
    
    def get_field_chinese_name(self, table_name: str, field_name: str) -> Optional[str]:
        """获取字段的中文名称"""
        key = f"{table_name}.{field_name}"
        if key in self.reverse_field_index:
            return self.reverse_field_index[key]['cn']
        return None
    
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
        
        return " ".join(sql_parts), field_mapping
    
    def get_query_template(self, query_type: str) -> Optional[Dict]:
        """获取查询模板"""
        return QUERY_TEMPLATES.get(query_type)
    
    def refresh_cache(self):
        """刷新缓存（如果需要）"""
        if time.time() - self.last_update > self.cache_ttl:
            self._load_schema()
```

### 1.3 智能查询解析器（2-3天）

**文件**: `utils/chinese_query_parser.py`

```python
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
        self.query_patterns = {
            # 股价查询模式
            'stock_price': {
                'patterns': [
                    r'(.+?)的?(?:最新|最近|今天|昨天)?(?:股价|收盘价|开盘价|最高价|最低价)',
                    r'(.+?)(?:最近|过去)?(\d+)天的(?:股价|走势|行情)',
                ],
                'default_fields': ['open', 'high', 'low', 'close', 'vol', 'amount'],
                'table': 'tu_daily_detail'
            },
            
            # 财务分析模式
            'financial': {
                'patterns': [
                    r'(.+?)的?(?:财务|财报|年报|季报|利润|营收|净利润)',
                    r'分析(.+?)的?(?:财务状况|经营状况|盈利能力)',
                ],
                'default_fields': ['revenue', 'n_income_attr_p', 'roe', 'total_assets'],
                'table': 'tu_income'
            },
            
            # 资金流向模式
            'money_flow': {
                'patterns': [
                    r'(.+?)的?(?:资金流向|主力资金|大单|超大单)',
                    r'(.+?)(?:最近|过去)?(\d+)天的资金流向',
                ],
                'default_fields': ['buy_elg_amount', 'sell_elg_amount', 'net_mf_amount'],
                'table': 'tu_moneyflow_dc'
            },
            
            # 技术指标模式
            'technical': {
                'patterns': [
                    r'(.+?)的?(?:MA|均线|MACD|KDJ|RSI|布林带)',
                    r'(.+?)的?技术(?:指标|分析)',
                ],
                'default_fields': ['close', 'vol'],
                'table': 'tu_daily_detail'
            }
        }
        
        # 时间模式
        self.time_patterns = {
            '最新': 0,
            '今天': 0,
            '昨天': 1,
            '前天': 2,
            '最近(\d+)天': lambda m: int(m.group(1)),
            '过去(\d+)天': lambda m: int(m.group(1)),
            '(\d+)天前': lambda m: int(m.group(1)),
        }
        
        # 字段映射
        self.field_keywords = {
            '股价': ['close'],
            '收盘价': ['close'],
            '开盘价': ['open'],
            '最高价': ['high'],
            '最低价': ['low'],
            '成交量': ['vol'],
            '成交额': ['amount'],
            '涨跌幅': ['pct_chg'],
            '换手率': ['turnover_rate'],
            '市盈率': ['pe', 'pe_ttm'],
            '市净率': ['pb'],
            '营收': ['revenue', 'total_revenue'],
            '净利润': ['n_income_attr_p'],
            '总资产': ['total_assets'],
            '净资产收益率': ['roe'],
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
                "original_query": "茅台最近30天的收盘价和成交量"
            }
        """
        result = {
            "original_query": query,
            "query_type": None,
            "tables": [],
            "fields": [],
            "conditions": {}
        }
        
        # 1. 识别查询类型
        for query_type, config in self.query_patterns.items():
            for pattern in config['patterns']:
                match = re.search(pattern, query)
                if match:
                    result['query_type'] = query_type
                    result['tables'] = [config['table']]
                    
                    # 提取股票信息
                    stock_info = match.group(1) if match.lastindex >= 1 else None
                    if stock_info:
                        ts_code = convert_to_ts_code(stock_info)
                        if ts_code:
                            result['conditions']['ts_code'] = ts_code
                    
                    # 提取时间信息
                    if match.lastindex >= 2:
                        try:
                            days = int(match.group(2))
                            result['conditions']['days'] = days
                        except:
                            pass
                    
                    break
            
            if result['query_type']:
                break
        
        # 2. 提取字段
        fields = set()
        
        # 检查是否有特定字段需求
        field_found = False
        for keyword, field_list in self.field_keywords.items():
            if keyword in query:
                fields.update(field_list)
                field_found = True
        
        # 如果没有特定字段，使用默认字段
        if not field_found and result['query_type']:
            config = self.query_patterns.get(result['query_type'], {})
            fields.update(config.get('default_fields', []))
        
        result['fields'] = list(fields)
        
        # 3. 提取时间条件
        for time_pattern, time_value in self.time_patterns.items():
            match = re.search(time_pattern, query)
            if match:
                if callable(time_value):
                    result['conditions']['days'] = time_value(match)
                else:
                    result['conditions']['days'] = time_value
                break
        
        # 4. 智能字段映射
        if result['tables'] and result['fields']:
            # 验证字段是否存在于表中
            table_name = result['tables'][0]
            table_info = self.schema_manager.get_table_info(table_name)
            
            if table_info:
                valid_fields = []
                for field in result['fields']:
                    if field in table_info.get('fields', {}):
                        valid_fields.append(field)
                result['fields'] = valid_fields
        
        # 5. 如果没有识别到查询类型，尝试通用解析
        if not result['query_type']:
            result = self._generic_parse(query, result)
        
        logger.info(f"Parsed query: {query} -> {result}")
        return result
    
    def _generic_parse(self, query: str, result: Dict) -> Dict:
        """通用查询解析"""
        # 尝试识别表名
        for table_cn, table_en in self.schema_manager.table_index.items():
            if table_cn in query:
                result['tables'] = [table_en]
                result['query_type'] = 'generic'
                break
        
        # 尝试识别字段名
        fields = []
        for field_cn, field_mappings in self.schema_manager.field_index.items():
            if field_cn in query:
                # 如果已经确定了表，优先使用该表的字段
                if result['tables']:
                    for mapping in field_mappings:
                        if mapping['table'] in result['tables']:
                            fields.append(mapping['field'])
                            break
                else:
                    # 使用第一个匹配的字段
                    fields.append(field_mappings[0]['field'])
                    if not result['tables']:
                        result['tables'] = [field_mappings[0]['table']]
        
        result['fields'] = fields
        
        # 尝试提取股票代码
        stock_match = re.search(r'([^\s]+?)(?:的|股票|公司)', query)
        if stock_match:
            stock_info = stock_match.group(1)
            ts_code = convert_to_ts_code(stock_info)
            if ts_code:
                result['conditions']['ts_code'] = ts_code
        
        return result
    
    def generate_sql(self, query_intent: Dict) -> str:
        """根据解析结果生成SQL查询"""
        sql, _ = self.schema_manager.generate_sql_with_chinese(query_intent)
        return sql
```

## 🚀 Phase 2: 性能优化与缓存系统（第3-4周）

### 2.1 Redis缓存层（3-4天）

#### Redis配置
**文件**: `config/redis_config.py`
```python
REDIS_CONFIG = {
    "host": "localhost",
    "port": 6379,
    "db": 0,
    "decode_responses": True,
    "cache_policies": {
        "stock_price": {
            "ttl": 300,  # 5分钟
            "key_pattern": "stock:price:{ts_code}:{date}"
        },
        "financial_data": {
            "ttl": 86400,  # 24小时
            "key_pattern": "stock:financial:{ts_code}:{period}"
        },
        "rag_results": {
            "ttl": 3600,  # 1小时
            "key_pattern": "rag:{query_hash}"
        },
        "schema_mapping": {
            "ttl": 604800,  # 7天
            "key_pattern": "schema:{table_name}"
        },
        "technical_indicators": {
            "ttl": 1800,  # 30分钟
            "key_pattern": "tech:{ts_code}:{indicator}:{period}"
        }
    }
}
```

#### 缓存服务实现
**文件**: `utils/cache_service.py`
```python
import redis
import json
import hashlib
from typing import Any, Optional
from config.redis_config import REDIS_CONFIG

class CacheService:
    def __init__(self):
        self.client = redis.Redis(**REDIS_CONFIG)
        self.policies = REDIS_CONFIG['cache_policies']
    
    def get(self, cache_type: str, **kwargs) -> Optional[Any]:
        key = self._generate_key(cache_type, **kwargs)
        data = self.client.get(key)
        return json.loads(data) if data else None
    
    def set(self, cache_type: str, data: Any, **kwargs):
        key = self._generate_key(cache_type, **kwargs)
        ttl = self.policies[cache_type]['ttl']
        self.client.setex(key, ttl, json.dumps(data))
    
    def _generate_key(self, cache_type: str, **kwargs) -> str:
        pattern = self.policies[cache_type]['key_pattern']
        return pattern.format(**kwargs)
```

### 2.2 查询优化器（3-4天）

**数据库索引优化**:
```sql
-- 优化常用查询的索引
CREATE INDEX idx_daily_ts_date ON tu_daily_detail(ts_code, trade_date);
CREATE INDEX idx_income_ts_end ON tu_income(ts_code, end_date);
CREATE INDEX idx_moneyflow_ts_date ON tu_moneyflow_dc(ts_code, trade_date);
```

### 2.3 异步任务队列（3-4天）

**Celery配置**:
```python
# config/celery_config.py
CELERY_BROKER_URL = 'amqp://guest@localhost//'
CELERY_RESULT_BACKEND = 'redis://localhost:6379'
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
```

## 🔧 Phase 3: 技术分析系统（第5-6周）

### 3.1 技术指标计算引擎（4-5天）

**文件**: `utils/technical_indicators.py`

```python
import numpy as np
import pandas as pd
from typing import Dict, Union, List

class TechnicalIndicatorEngine:
    """高性能技术指标计算引擎"""
    
    @staticmethod
    def calculate_ma(prices: np.array, period: int) -> np.array:
        """简单移动平均线"""
        return pd.Series(prices).rolling(window=period).mean().values
    
    @staticmethod
    def calculate_ema(prices: np.array, period: int) -> np.array:
        """指数移动平均线"""
        return pd.Series(prices).ewm(span=period, adjust=False).mean().values
    
    @staticmethod
    def calculate_macd(prices: np.array, fast=12, slow=26, signal=9) -> Dict:
        """MACD指标"""
        ema_fast = TechnicalIndicatorEngine.calculate_ema(prices, fast)
        ema_slow = TechnicalIndicatorEngine.calculate_ema(prices, slow)
        macd_line = ema_fast - ema_slow
        signal_line = TechnicalIndicatorEngine.calculate_ema(macd_line, signal)
        histogram = macd_line - signal_line
        
        return {
            'macd': macd_line,
            'signal': signal_line,
            'histogram': histogram
        }
    
    @staticmethod
    def calculate_rsi(prices: np.array, period: int = 14) -> np.array:
        """相对强弱指标"""
        deltas = np.diff(prices)
        seed = deltas[:period+1]
        up = seed[seed >= 0].sum() / period
        down = -seed[seed < 0].sum() / period
        rs = up / down
        rsi = np.zeros_like(prices)
        rsi[:period] = 100. - 100. / (1. + rs)
        
        for i in range(period, len(prices)):
            delta = deltas[i-1]
            if delta > 0:
                upval = delta
                downval = 0.
            else:
                upval = 0.
                downval = -delta
            
            up = (up * (period - 1) + upval) / period
            down = (down * (period - 1) + downval) / period
            rs = up / down
            rsi[i] = 100. - 100. / (1. + rs)
        
        return rsi
    
    @staticmethod
    def calculate_bollinger_bands(prices: np.array, period: int = 20, std_dev: int = 2) -> Dict:
        """布林带指标"""
        sma = TechnicalIndicatorEngine.calculate_ma(prices, period)
        std = pd.Series(prices).rolling(window=period).std().values
        
        return {
            'upper': sma + (std_dev * std),
            'middle': sma,
            'lower': sma - (std_dev * std)
        }
```

### 3.2 TechnicalAnalysisAgent（3-4天）

**文件**: `agents/technical_agent.py`

```python
from typing import Dict, List
from utils.technical_indicators import TechnicalIndicatorEngine
from database.mysql_connector import MySQLConnector
import numpy as np

class TechnicalAnalysisAgent:
    """技术分析专用Agent"""
    
    def __init__(self):
        self.indicator_engine = TechnicalIndicatorEngine()
        self.db_connector = MySQLConnector()
    
    def analyze_trend(self, ts_code: str, period: int = 30) -> Dict:
        """趋势分析：识别上升/下降/横盘"""
        # 获取历史数据
        data = self._get_price_data(ts_code, period)
        prices = data['close'].values
        
        # 计算趋势
        ma_short = self.indicator_engine.calculate_ma(prices, 5)
        ma_long = self.indicator_engine.calculate_ma(prices, 20)
        
        # 判断趋势
        if ma_short[-1] > ma_long[-1] and ma_short[-5] < ma_long[-5]:
            trend = "上升突破"
        elif ma_short[-1] < ma_long[-1] and ma_short[-5] > ma_long[-5]:
            trend = "下降突破"
        elif ma_short[-1] > ma_long[-1]:
            trend = "上升趋势"
        elif ma_short[-1] < ma_long[-1]:
            trend = "下降趋势"
        else:
            trend = "横盘震荡"
        
        return {
            "trend": trend,
            "ma5": ma_short[-1],
            "ma20": ma_long[-1],
            "price": prices[-1]
        }
    
    def generate_signals(self, ts_code: str, indicators: List[str] = None) -> Dict:
        """生成买卖信号"""
        if not indicators:
            indicators = ['MACD', 'RSI', 'BOLL']
        
        signals = {}
        data = self._get_price_data(ts_code, 60)
        
        # MACD信号
        if 'MACD' in indicators:
            macd_result = self.indicator_engine.calculate_macd(data['close'].values)
            if macd_result['histogram'][-1] > 0 and macd_result['histogram'][-2] < 0:
                signals['MACD'] = 'BUY'
            elif macd_result['histogram'][-1] < 0 and macd_result['histogram'][-2] > 0:
                signals['MACD'] = 'SELL'
            else:
                signals['MACD'] = 'HOLD'
        
        # RSI信号
        if 'RSI' in indicators:
            rsi = self.indicator_engine.calculate_rsi(data['close'].values)
            if rsi[-1] < 30:
                signals['RSI'] = 'BUY'
            elif rsi[-1] > 70:
                signals['RSI'] = 'SELL'
            else:
                signals['RSI'] = 'HOLD'
        
        return signals
    
    def _get_price_data(self, ts_code: str, period: int):
        """获取价格数据"""
        query = f"""
        SELECT trade_date, open, high, low, close, vol
        FROM tu_daily_detail
        WHERE ts_code = '{ts_code}'
        ORDER BY trade_date DESC
        LIMIT {period}
        """
        return self.db_connector.execute_query(query)
```

## 📊 Phase 4: 智能分析增强（第7-8周）

### 4.1 多维度融合分析（3-4天）

**文件**: `agents/comprehensive_analysis_agent.py`

```python
class ComprehensiveAnalysisAgent:
    """综合分析Agent，融合基本面、技术面、资金面"""
    
    def calculate_comprehensive_score(self, ts_code: str) -> Dict:
        """
        综合评分 = 基本面(50%) + 技术面(30%) + 资金面(20%)
        """
        # 基本面分析
        fundamental = self.financial_agent.analyze_financial_health(ts_code)
        fundamental_score = self._normalize_score(fundamental['total_score'])
        
        # 技术面分析
        technical = self.technical_agent.analyze_trend(ts_code)
        technical_signals = self.technical_agent.generate_signals(ts_code)
        technical_score = self._calculate_technical_score(technical, technical_signals)
        
        # 资金面分析
        money_flow = self.money_flow_agent.analyze_money_flow(ts_code)
        money_flow_score = self._normalize_score(money_flow['score'])
        
        # 综合评分
        total_score = (
            fundamental_score * 0.5 +
            technical_score * 0.3 +
            money_flow_score * 0.2
        )
        
        return {
            "total_score": total_score,
            "fundamental_score": fundamental_score,
            "technical_score": technical_score,
            "money_flow_score": money_flow_score,
            "recommendation": self._generate_recommendation(total_score),
            "risk_level": self._assess_risk(fundamental, technical, money_flow)
        }
```

### 4.2 监控与告警系统（2-3天）

**Prometheus配置**:
```yaml
# prometheus.yml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'stock_analysis'
    static_configs:
      - targets: ['localhost:8000']
```

### 4.3 测试覆盖提升（2-3天）

**测试框架**:
```python
# tests/test_schema_cache.py
import pytest
from utils.schema_cache_manager import SchemaCacheManager

def test_chinese_field_mapping():
    manager = SchemaCacheManager()
    
    # 测试精确匹配
    result = manager.get_field_by_chinese("收盘价")
    assert result['field'] == 'close'
    
    # 测试模糊匹配
    result = manager.get_field_by_chinese("营业收入")
    assert result['field'] in ['revenue', 'total_revenue']
```

## 实施优先级和预期成果

### 🚀 立即开始（第1-2周）
1. **数据库Schema中文映射** ⭐⭐⭐⭐⭐
   - 减少50%的数据库结构查询
   - 提升路由准确率至95%以上
   - 响应速度提升30%

2. **智能查询解析器** ⭐⭐⭐⭐⭐
   - 支持纯中文自然语言查询
   - 查询意图识别准确率>90%

### 📈 中期实施（第3-4周）
1. **Redis缓存系统** ⭐⭐⭐⭐
   - 热门查询响应时间<1秒
   - 系统并发能力提升3倍
   - 缓存命中率>70%

2. **查询优化** ⭐⭐⭐⭐
   - 复杂查询性能提升50%
   - 数据库负载降低40%

### 🔧 后期完成（第5-8周）
1. **技术分析系统** ⭐⭐⭐⭐
   - 30+技术指标实时计算
   - K线形态自动识别
   - 买卖信号生成

2. **综合分析系统** ⭐⭐⭐
   - 多维度投资评分
   - 风险等级评估
   - 个性化投资建议

## 技术栈确认

- **缓存**: Redis 7.0+
- **任务队列**: Celery + RabbitMQ
- **技术分析**: TA-Lib + NumPy + Pandas
- **监控**: Prometheus + Grafana
- **测试**: pytest + locust
- **文档**: Sphinx

## 成功指标

### 性能指标
- ✅ 平均查询响应时间 < 5秒
- ✅ 系统并发用户数 > 100
- ✅ 缓存命中率 > 70%
- ✅ 数据库查询优化率 > 50%

### 功能指标
- ✅ 中文查询理解准确率 > 95%
- ✅ 技术指标计算准确率 100%
- ✅ 综合分析报告完整率 > 90%
- ✅ Schema映射覆盖率 100%

### 用户体验
- ✅ 自然语言查询支持率 100%
- ✅ 错误率 < 1%
- ✅ 用户满意度 > 90%
- ✅ 查询结果可解释性 100%

## 已完成功能总结（v1.5.4）

### 前端功能 ✅
- React + TypeScript + Claude.ai风格界面
- 流式响应 + 打字效果 + 停止按钮
- 完整Markdown渲染（代码高亮、表格、公式）
- 分屏布局 + 侧边栏折叠
- 深色主题优化

### 后端功能 ✅
- 五大Agent系统（SQL、RAG、Financial、MoneyFlow、Hybrid）
- 智能日期解析v2.0
- 股票代码映射器
- WebSocket实时通信
- 完整错误处理

### 系统特性 ✅
- Windows兼容性100%
- 双环境开发支持
- 完整测试框架
- API文档完善

---

**下一步行动**: 开始实施Phase 1 - 数据库Schema中文映射缓存系统