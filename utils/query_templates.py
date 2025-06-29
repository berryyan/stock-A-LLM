#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
常见查询模板库
为高频查询提供预定义的路由和参数模板
"""

from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import re


class TemplateType(Enum):
    """模板类型"""
    PRICE_QUERY = "price_query"          # 股价查询
    FINANCIAL_HEALTH = "financial_health" # 财务健康度
    MONEY_FLOW = "money_flow"            # 资金流向
    ANNOUNCEMENT = "announcement"         # 公告查询
    COMPARISON = "comparison"            # 比较分析
    RANKING = "ranking"                  # 排名查询
    DUPONT = "dupont"                    # 杜邦分析
    CASH_FLOW = "cash_flow"              # 现金流分析


@dataclass
class QueryTemplate:
    """查询模板"""
    name: str                    # 模板名称
    type: TemplateType          # 模板类型
    pattern: str                # 正则表达式模式
    route_type: str             # 路由类型
    required_fields: List[str]  # 必需字段
    optional_fields: List[str]  # 可选字段
    default_params: Dict        # 默认参数
    example: str               # 示例查询


class QueryTemplateLibrary:
    """查询模板库"""
    
    def __init__(self):
        """初始化模板库"""
        self.templates = self._build_templates()
        
    def _build_templates(self) -> List[QueryTemplate]:
        """构建查询模板"""
        return [
            # 股价查询模板
            QueryTemplate(
                name="最新股价查询",
                type=TemplateType.PRICE_QUERY,
                pattern=r"(.+?)(?:的)?最新股价",
                route_type="SQL_ONLY",
                required_fields=["close", "trade_date"],
                optional_fields=["change", "pct_chg", "vol"],
                default_params={
                    "time_range": "latest",
                    "metrics": ["close", "change", "pct_chg"]
                },
                example="茅台最新股价"
            ),
            
            QueryTemplate(
                name="今日股价查询",
                type=TemplateType.PRICE_QUERY,
                pattern=r"(.+?)(?:的)?今天.*价格|(.+?)今日.*股价",
                route_type="SQL_ONLY",
                required_fields=["close", "trade_date"],
                optional_fields=["open", "high", "low", "vol"],
                default_params={
                    "time_range": "today",
                    "metrics": ["open", "high", "low", "close", "vol"]
                },
                example="贵州茅台今天的价格"
            ),
            
            # 历史K线查询模板
            QueryTemplate(
                name="历史K线查询",
                type=TemplateType.PRICE_QUERY,
                pattern=r"(.+?)(?:的)?(?:最近|过去)(\d+)天.*(?:K线|走势|股价)",
                route_type="SQL_ONLY",
                required_fields=["open", "high", "low", "close", "trade_date"],
                optional_fields=["vol", "amount", "pct_chg"],
                default_params={
                    "time_range": "recent_days",
                    "days": 90,
                    "metrics": ["open", "high", "low", "close", "vol"]
                },
                example="贵州茅台最近90天的K线走势"
            ),
            
            # 历史交易量查询模板
            QueryTemplate(
                name="历史交易量查询",
                type=TemplateType.PRICE_QUERY,
                pattern=r"(.+?)(?:的)?(?:最近|过去)(\d+)天.*(?:成交量|交易量|换手率)",
                route_type="SQL_ONLY",
                required_fields=["vol", "amount", "trade_date"],
                optional_fields=["turnover_rate"],
                default_params={
                    "time_range": "recent_days",
                    "days": 90,
                    "metrics": ["vol", "amount", "turnover_rate"]
                },
                example="平安银行最近30天的成交量"
            ),
            
            # 利润查询模板
            QueryTemplate(
                name="利润查询",
                type=TemplateType.FINANCIAL_HEALTH,
                pattern=r"(.+?)(?:的)?(?:利润|营收|净利润|营业收入)",
                route_type="SQL_ONLY",
                required_fields=["revenue", "net_profit"],
                optional_fields=["operate_profit", "total_profit"],
                default_params={
                    "period_count": 4,
                    "metrics": ["revenue", "net_profit", "operate_profit"]
                },
                example="贵州茅台的净利润"
            ),
            
            # PE/PB查询模板
            QueryTemplate(
                name="估值指标查询",
                type=TemplateType.FINANCIAL_HEALTH,
                pattern=r"(.+?)(?:的)?(?:PE|PB|市盈率|市净率|估值)",
                route_type="SQL_ONLY",
                required_fields=["pe", "pb"],
                optional_fields=["pe_ttm", "ps", "ps_ttm"],
                default_params={
                    "time_range": "latest",
                    "metrics": ["pe", "pe_ttm", "pb", "ps", "ps_ttm"]
                },
                example="中国平安的市盈率"
            ),
            
            # 主力净流入排行模板
            QueryTemplate(
                name="主力净流入排行",
                type=TemplateType.MONEY_FLOW,
                pattern=r"(?:今日|今天)?主力.*净流入.*(?:排行|排名|前(\d+))",
                route_type="SQL_ONLY",
                required_fields=["ts_code", "name", "net_mf_amount"],
                optional_fields=["net_mf_amount_rate", "pct_chg"],
                default_params={
                    "order_by": "net_mf_amount DESC",
                    "limit": 10,
                    "time_range": "today"
                },
                example="今日主力净流入排行前10"
            ),
            
            # 财务健康度模板
            QueryTemplate(
                name="财务健康度分析",
                type=TemplateType.FINANCIAL_HEALTH,
                pattern=r"(?:分析)?(.+?)(?:的)?财务健康.*|(.+?)财务状况",
                route_type="FINANCIAL",
                required_fields=["revenue", "net_profit", "roe", "debt_to_assets"],
                optional_fields=["roa", "current_ratio", "quick_ratio"],
                default_params={
                    "analysis_type": "health_score",
                    "period_count": 4
                },
                example="分析贵州茅台的财务健康度"
            ),
            
            # 杜邦分析模板
            QueryTemplate(
                name="杜邦分析",
                type=TemplateType.DUPONT,
                pattern=r"(.+?)(?:的)?杜邦分析|(.+?)ROE.*分解",
                route_type="FINANCIAL",
                required_fields=["roe", "net_profit_margin", "asset_turnover", "equity_multiplier"],
                optional_fields=["revenue", "net_profit", "total_assets"],
                default_params={
                    "analysis_type": "dupont",
                    "period_count": 4
                },
                example="平安银行的杜邦分析"
            ),
            
            # 资金流向模板
            QueryTemplate(
                name="资金流向分析",
                type=TemplateType.MONEY_FLOW,
                pattern=r"(.+?)(?:的)?资金流向|(.+?)主力资金",
                route_type="MONEY_FLOW",
                required_fields=["buy_elg_amount", "sell_elg_amount", "net_mf_amount"],
                optional_fields=["buy_lg_amount", "buy_md_amount", "buy_sm_amount"],
                default_params={
                    "days": 30,
                    "focus": "main_force"
                },
                example="茅台的资金流向如何"
            ),
            
            QueryTemplate(
                name="超大单分析",
                type=TemplateType.MONEY_FLOW,
                pattern=r"(.+?)(?:的)?超大单.*|(.+?)机构资金",
                route_type="MONEY_FLOW",
                required_fields=["buy_elg_amount", "sell_elg_amount"],
                optional_fields=["elg_vol", "elg_amount"],
                default_params={
                    "days": 30,
                    "focus": "super_large"
                },
                example="贵州茅台的超大单资金流入情况"
            ),
            
            # 公告查询模板
            QueryTemplate(
                name="最新公告",
                type=TemplateType.ANNOUNCEMENT,
                pattern=r"(.+?)(?:的)?最新公告|(.+?)最近.*公告",
                route_type="RAG_ONLY",
                required_fields=["title", "ann_date"],
                optional_fields=["content", "ann_type"],
                default_params={
                    "time_range": "recent_30d",
                    "limit": 5
                },
                example="贵州茅台最新公告内容"
            ),
            
            QueryTemplate(
                name="年报查询",
                type=TemplateType.ANNOUNCEMENT,
                pattern=r"(.+?)(?:的)?(\d{4})?年报|(.+?)年度报告",
                route_type="RAG_ONLY",
                required_fields=["title", "ann_date", "content"],
                optional_fields=["pdf_url"],
                default_params={
                    "ann_type": "年报",
                    "limit": 1
                },
                example="茅台的年报说了什么"
            ),
            
            # 排名查询模板
            QueryTemplate(
                name="涨幅排名",
                type=TemplateType.RANKING,
                pattern=r"(?:今天)?涨幅.*前(\d+)|涨幅最大.*(\d+)",
                route_type="SQL_ONLY",
                required_fields=["ts_code", "name", "pct_chg"],
                optional_fields=["close", "vol", "amount"],
                default_params={
                    "order_by": "pct_chg DESC",
                    "limit": 10,
                    "time_range": "today"
                },
                example="今天涨幅最大的前10只股票"
            ),
            
            # 总市值排名模板
            QueryTemplate(
                name="总市值排名",
                type=TemplateType.RANKING,
                pattern=r"总市值.*前(\d+)|最大.*总市值.*(\d+)",
                route_type="SQL_ONLY",
                required_fields=["ts_code", "name", "total_mv"],
                optional_fields=["close", "pe_ttm", "pb"],
                default_params={
                    "order_by": "total_mv DESC",
                    "limit": 10,
                    "time_range": "latest"
                },
                example="总市值最大的前20只股票"
            ),
            
            # 流通市值排名模板
            QueryTemplate(
                name="流通市值排名",
                type=TemplateType.RANKING,
                pattern=r"流通市值.*前(\d+)|最大.*流通市值.*(\d+)",
                route_type="SQL_ONLY",
                required_fields=["ts_code", "name", "circ_mv"],
                optional_fields=["total_mv", "turnover_rate", "volume_ratio"],
                default_params={
                    "order_by": "circ_mv DESC",
                    "limit": 10,
                    "time_range": "latest"
                },
                example="流通市值最大的前10只股票"
            ),
            
            QueryTemplate(
                name="市值排名",
                type=TemplateType.RANKING,
                pattern=r"市值.*前(\d+)|最大市值.*(\d+)",
                route_type="SQL_ONLY",
                required_fields=["ts_code", "name", "total_mv"],
                optional_fields=["circ_mv", "close"],
                default_params={
                    "order_by": "total_mv DESC",
                    "limit": 10
                },
                example="市值最大的前20只股票"
            ),
            
            # 比较分析模板
            QueryTemplate(
                name="财务比较",
                type=TemplateType.COMPARISON,
                pattern=r"比较(.+?)和(.+?)的(.+)|(.+?)与(.+?).*对比",
                route_type="PARALLEL",
                required_fields=["ts_code", "name"],
                optional_fields=["revenue", "net_profit", "roe"],
                default_params={
                    "comparison_type": "financial",
                    "metrics": ["revenue", "net_profit", "roe", "total_assets"]
                },
                example="比较茅台和五粮液的营业收入"
            ),
            
            # 现金流分析模板
            QueryTemplate(
                name="现金流质量分析",
                type=TemplateType.CASH_FLOW,
                pattern=r"(.+?)(?:的)?现金流.*质量|(.+?)现金流.*分析",
                route_type="FINANCIAL",
                required_fields=["n_cashflow_act", "net_profit", "free_cashflow"],
                optional_fields=["cashflow_ratio", "cash_to_profit"],
                default_params={
                    "analysis_type": "cash_quality",
                    "period_count": 4
                },
                example="万科的现金流质量"
            )
        ]
    
    def match_template(self, query: str) -> Optional[QueryTemplate]:
        """匹配查询模板"""
        for template in self.templates:
            if re.search(template.pattern, query, re.IGNORECASE):
                return template
        return None
    
    def extract_params(self, query: str, template: QueryTemplate) -> Dict[str, Any]:
        """从查询中提取参数"""
        params = template.default_params.copy()
        
        # 提取实体
        match = re.search(template.pattern, query, re.IGNORECASE)
        if match:
            groups = [g for g in match.groups() if g]
            if groups:
                params['entities'] = groups
        
        # 提取数字参数（如排名数量）
        numbers = re.findall(r'\d+', query)
        if numbers and template.type == TemplateType.RANKING:
            params['limit'] = int(numbers[0])
        
        # 提取时间参数
        if '今天' in query or '今日' in query:
            params['time_range'] = 'today'
        elif '昨天' in query or '昨日' in query:
            params['time_range'] = 'yesterday'
        elif '最新' in query or '最近' in query:
            params['time_range'] = 'latest'
        
        # 提取年份
        year_match = re.search(r'(\d{4})年', query)
        if year_match:
            params['year'] = year_match.group(1)
        
        return params
    
    def get_template_by_type(self, template_type: TemplateType) -> List[QueryTemplate]:
        """获取特定类型的所有模板"""
        return [t for t in self.templates if t.type == template_type]
    
    def suggest_query(self, partial_query: str) -> List[str]:
        """基于部分查询建议完整查询"""
        suggestions = []
        
        for template in self.templates:
            # 简单的关键词匹配
            keywords = ['财务', '股价', '资金', '公告', '年报', '涨幅', '市值', '比较']
            for keyword in keywords:
                if keyword in partial_query and keyword in template.example:
                    suggestions.append(template.example)
                    break
        
        return list(set(suggestions))[:5]  # 返回最多5个建议
    
    def get_required_data(self, template: QueryTemplate) -> Dict[str, List[str]]:
        """获取模板所需的数据信息"""
        return {
            'required_fields': template.required_fields,
            'optional_fields': template.optional_fields,
            'tables': self._infer_tables(template.required_fields)
        }
    
    def _infer_tables(self, fields: List[str]) -> List[str]:
        """推断字段所属的表"""
        # 字段到表的映射（简化版）
        field_table_mapping = {
            'close': ['tu_daily_detail'],
            'open': ['tu_daily_detail'],
            'high': ['tu_daily_detail'],
            'low': ['tu_daily_detail'],
            'vol': ['tu_daily_detail'],
            'pct_chg': ['tu_daily_detail'],
            'revenue': ['tu_income'],
            'net_profit': ['tu_income'],
            'roe': ['tu_fina_indicator'],
            'roa': ['tu_fina_indicator'],
            'debt_to_assets': ['tu_fina_indicator'],
            'current_ratio': ['tu_fina_indicator'],
            'buy_elg_amount': ['tu_moneyflow_dc'],
            'sell_elg_amount': ['tu_moneyflow_dc'],
            'net_mf_amount': ['tu_moneyflow_dc'],
            'n_cashflow_act': ['tu_cashflow'],
            'free_cashflow': ['tu_cashflow'],
            'total_mv': ['tu_daily_basic'],
            'circ_mv': ['tu_daily_basic']
        }
        
        tables = set()
        for field in fields:
            if field in field_table_mapping:
                tables.update(field_table_mapping[field])
        
        return list(tables)


# 创建全局实例
query_templates = QueryTemplateLibrary()


# 便捷函数
def match_query_template(query: str) -> Optional[Tuple[QueryTemplate, Dict[str, Any]]]:
    """匹配查询模板并提取参数"""
    template = query_templates.match_template(query)
    if template:
        params = query_templates.extract_params(query, template)
        return template, params
    return None


def get_query_suggestions(partial_query: str) -> List[str]:
    """获取查询建议"""
    return query_templates.suggest_query(partial_query)


# 测试代码
if __name__ == "__main__":
    # 测试查询
    test_queries = [
        "茅台最新股价",
        "分析贵州茅台的财务健康度",
        "平安银行的杜邦分析",
        "茅台的资金流向如何",
        "贵州茅台最新公告内容",
        "今天涨幅最大的前10只股票",
        "比较茅台和五粮液的营业收入",
        "万科的现金流质量"
    ]
    
    print("查询模板匹配测试")
    print("=" * 60)
    
    for query in test_queries:
        print(f"\n查询: {query}")
        result = match_query_template(query)
        
        if result:
            template, params = result
            print(f"  匹配模板: {template.name}")
            print(f"  路由类型: {template.route_type}")
            print(f"  提取参数: {params}")
            print(f"  所需字段: {template.required_fields}")
            print(f"  相关表: {query_templates._infer_tables(template.required_fields)}")
        else:
            print("  未匹配到模板")
    
    print("\n\n查询建议测试")
    print("=" * 60)
    
    partial_queries = ["财务", "股价", "资金"]
    for partial in partial_queries:
        suggestions = get_query_suggestions(partial)
        print(f"\n输入 '{partial}' 的建议:")
        for i, suggestion in enumerate(suggestions, 1):
            print(f"  {i}. {suggestion}")