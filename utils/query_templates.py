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
    # Phase 1.3新增字段 - 用于统一处理
    requires_stock: bool = False      # 是否需要股票代码
    requires_date: bool = False       # 是否需要日期
    requires_date_range: bool = False # 是否需要日期范围
    requires_limit: bool = False      # 是否需要数量限制
    default_limit: int = 10          # 默认数量限制
    supports_exclude_st: bool = False # 是否支持排除ST


class QueryTemplateLibrary:
    """查询模板库"""
    
    def __init__(self):
        """初始化模板库"""
        self.templates = self._build_templates()
        
    def _build_templates(self) -> List[QueryTemplate]:
        """构建查询模板"""
        return [
            # 股价查询模板
            # 股价查询模板（支持任意日期）
            QueryTemplate(
                name="股价查询",
                type=TemplateType.PRICE_QUERY,
                pattern=r"(.+?)(?:的)?(?:(\d{8}|\d{4}-\d{2}-\d{2}|\d{4}年\d{2}月\d{2}日|最新|昨天|前天|上个交易日|最近一个交易日))?(?:的)?股价",
                route_type="SQL_ONLY",
                required_fields=["close", "trade_date"],
                optional_fields=["open", "high", "low", "vol", "amount", "pct_chg"],
                default_params={
                    "time_range": "specified",
                    "metrics": ["open", "high", "low", "close", "vol", "amount", "pct_chg"]
                },
                example="贵州茅台20250627的股价",
                requires_stock=True,
                requires_date=True
            ),
            
            # K线查询模板（支持任意时间段）
            QueryTemplate(
                name="K线查询",
                type=TemplateType.PRICE_QUERY,
                # 改进的正则表达式，支持更多日期格式和表达方式
                pattern=r"(.*?)(?:的)?(?:从(\d{4}年?\d{1,2}月?\d{1,2}日?|\d{4}-\d{1,2}-\d{1,2}|\d{4}/\d{1,2}/\d{1,2}|\d{8}|\d{1,2}月\d{1,2}日)到(\d{4}年?\d{1,2}月?\d{1,2}日?|\d{4}-\d{1,2}-\d{1,2}|\d{4}/\d{1,2}/\d{1,2}|\d{8}|\d{1,2}月\d{1,2}日)|最近(\d+)(?:个)?天|过去(\d+)(?:个)?天|最近(\d+)个?月|过去(\d+)个?月|最近一个?月|近(\d+)(?:个)?交易日|最近(\d+)个?交易日)?的?(?:K线|k线|走势|行情)",
                route_type="SQL_ONLY",
                required_fields=["open", "high", "low", "close", "trade_date"],
                optional_fields=["vol", "amount", "pct_chg"],
                default_params={
                    "time_range": "range",
                    "days": 90,
                    "metrics": ["open", "high", "low", "close", "vol", "amount", "pct_chg"]
                },
                example="贵州茅台从2025-06-01到2025-06-27的K线",
                requires_stock=True,
                requires_date_range=True
            ),
            
            # 成交量查询模板（支持任意日期）- 修改为不匹配"成交额排名"
            QueryTemplate(
                name="成交量查询",
                type=TemplateType.PRICE_QUERY,
                pattern=r"(.+?)(?:的)?(?:(\d{8}|\d{4}-\d{2}-\d{2}|\d{4}年\d{2}月\d{2}日|最新|昨天|上个交易日)|最近(\d+)天|过去(\d+)天)?(?:的)?(?:成交量|交易量|成交额)(?!.*(?:排名|排行|前\d+|最大|TOP))",
                route_type="SQL_ONLY",
                required_fields=["vol", "amount", "trade_date"],
                optional_fields=["turnover_rate"],
                default_params={
                    "time_range": "specified",
                    "days": 1,
                    "metrics": ["vol", "amount"]
                },
                example="平安银行昨天的成交量",
                requires_stock=True,
                requires_date=True
            ),
            
            # 利润查询模板 - SQL_ONLY路由，快速返回财务数据
            QueryTemplate(
                name="利润查询",
                type=TemplateType.FINANCIAL_HEALTH,
                pattern=r"(.+?)(?:的)?(?:(\d{4}年(?:第[一二三四]季度)?|\d{4}Q[1-4]|\d{4}年\d{1,2}月|最新))?(?:的)?(?:利润|营收|净利润|营业收入|赚了多少|盈利|收入)(?!.*(?:排名|排行|前\d+|最高|最多))",
                route_type="SQL_ONLY",
                required_fields=["revenue", "net_profit"],
                optional_fields=["operate_profit", "total_profit"],
                default_params={
                    "period_count": 4,
                    "metrics": ["revenue", "net_profit", "operate_profit"]
                },
                example="贵州茅台2024年的净利润",
                requires_stock=True
            ),
            
            # PE/PB查询模板（支持任意日期）
            QueryTemplate(
                name="估值指标查询",
                type=TemplateType.FINANCIAL_HEALTH,
                pattern=r"(.+?)(?:的)?(?:(\d{8}|\d{4}-\d{2}-\d{2}|\d{4}年\d{2}月\d{2}日|最新|昨天|上个交易日))?(?:的)?(?:PE|PB|市盈率|市净率|估值)",
                route_type="SQL_ONLY",
                required_fields=["pe", "pb"],
                optional_fields=["pe_ttm", "ps", "ps_ttm"],
                default_params={
                    "time_range": "specified",
                    "metrics": ["pe", "pe_ttm", "pb", "ps", "ps_ttm"]
                },
                example="中国平安昨天的市盈率",
                requires_stock=True,
                requires_date=True
            ),
            
            # 主力净流入排行模板（必须包含排名相关关键词）
            QueryTemplate(
                name="主力净流入排行",
                type=TemplateType.MONEY_FLOW,
                pattern=r"(?:.*(\d{8}|\d{4}-\d{2}-\d{2}|\d{4}年\d{2}月\d{2}日|今日|今天|昨天|上个交易日|最新).*)?(?:主力|机构|大资金)(?:资金)?(?:净)?流入.*?(?:排名|排行|榜|前(\d+)|最[多大].*?前(\d+)|TOP(\d+))",
                route_type="SQL_ONLY",
                required_fields=["ts_code", "name", "net_mf_amount"],
                optional_fields=["net_mf_amount_rate", "pct_chg"],
                default_params={
                    "order_by": "net_mf_amount DESC",
                    "limit": 10,
                    "time_range": "specified"
                },
                example="昨天主力净流入排行前10"
            ),
            
            # 主力净流出排行模板（仅匹配排名查询）
            QueryTemplate(
                name="主力净流出排行",
                type=TemplateType.MONEY_FLOW,
                pattern=r"(?:.*(\d{8}|\d{4}-\d{2}-\d{2}|\d{4}年\d{2}月\d{2}日|今日|今天|昨天|上个交易日|最新).*)?(?:主力|机构|大资金)(?:资金)?(?:净)?流出.*?(?:排名|排行|榜|前(\d+)|最[多大].*?前(\d+)|TOP(\d+))",
                route_type="SQL_ONLY",
                required_fields=["ts_code", "name", "net_mf_amount"],
                optional_fields=["net_mf_amount_rate", "pct_chg"],
                default_params={
                    "order_by": "net_mf_amount ASC",
                    "limit": 10,
                    "time_range": "specified"
                },
                example="昨天主力净流出排行前10"
            ),
            
            # 成交额排名模板（支持历史日期，支持无数字默认前10）
            QueryTemplate(
                name="成交额排名",
                type=TemplateType.RANKING,
                pattern=r"(?:.*(\d{8}|\d{4}-\d{2}-\d{2}|\d{4}年\d{2}月\d{2}日|今天|昨天|上个交易日|最新).*)?成交额(?:.*前(\d+)|.*最大.*(\d+)|排名|排行|TOP(\d+))?",
                route_type="SQL_ONLY",
                required_fields=["ts_code", "name", "amount"],
                optional_fields=["close", "pct_chg", "vol"],
                default_params={
                    "order_by": "amount DESC",
                    "limit": 10,
                    "time_range": "specified"
                },
                example="成交额最大的前10只股票"
            ),
            
            # 成交量排名模板（支持历史日期，支持无数字默认前10）
            QueryTemplate(
                name="成交量排名",
                type=TemplateType.RANKING,
                pattern=r"(?:.*(\d{8}|\d{4}-\d{2}-\d{2}|\d{4}年\d{2}月\d{2}日|今天|昨天|上个交易日|最新).*)?成交量(?:.*前(\d+)|.*最大.*(\d+)|排名|排行|TOP(\d+))?",
                route_type="SQL_ONLY",
                required_fields=["ts_code", "name", "vol"],
                optional_fields=["close", "pct_chg", "amount"],
                default_params={
                    "order_by": "vol DESC",
                    "limit": 10,
                    "time_range": "specified"
                },
                example="成交量最大的前10只股票"
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
            
            # 板块主力资金查询模板（SQL快速路径）- 优先匹配板块
            QueryTemplate(
                name="板块主力资金",
                type=TemplateType.MONEY_FLOW,
                pattern=r"(.+?)(?:板块|行业)(?:(\d{8}|\d{4}-\d{2}-\d{2}|\d{4}年\d{2}月\d{2}日|今天|昨天|最新))?(?:的)?(?:主力|机构|大资金)(?:资金|净)?(?:流[入出向]|情况|动向)?(?!.*(?:排名|排行|榜|前\d+|最[多大]|TOP|分析|如何))",
                route_type="SQL_ONLY",
                required_fields=["ts_code", "net_amount", "buy_elg_amount"],
                optional_fields=["buy_lg_amount", "buy_md_amount", "buy_sm_amount"],
                default_params={
                    "time_range": "specified",
                    "query_type": "sector"
                },
                example="银行板块昨天的主力资金流入",
                requires_date=True
            ),
            
            # 个股主力资金查询模板（SQL快速路径）
            QueryTemplate(
                name="个股主力资金",
                type=TemplateType.MONEY_FLOW,
                pattern=r"((?!.*(?:板块|行业)).+?)(?:(\d{8}|\d{4}-\d{2}-\d{2}|\d{4}年\d{2}月\d{2}日|今天|昨天|最新))?(?:的)?(?:主力|机构|大资金)(?:资金|净)?(?:流[入出向]|情况|动向)?(?!.*(?:排名|排行|榜|前\d+|最[多大]|TOP|分析|如何|游资|散户))",
                route_type="SQL_ONLY",
                required_fields=["ts_code", "net_amount", "buy_elg_amount"],
                optional_fields=["buy_lg_amount", "buy_md_amount", "buy_sm_amount"],
                default_params={
                    "time_range": "specified"
                },
                example="贵州茅台昨天的主力净流入",
                requires_stock=True,
                requires_date=True
            ),
            
            # 资金流向模板
            QueryTemplate(
                name="资金流向分析",
                type=TemplateType.MONEY_FLOW,
                pattern=r"(?:分析)?(.+?)(?:的)?资金流向(?:如何|怎么样|情况)?|(.+?)(?:的)?主力资金(?:流向|分析|如何|怎么样)",
                route_type="MONEY_FLOW",
                required_fields=["buy_elg_amount", "sell_elg_amount", "net_mf_amount"],
                optional_fields=["buy_lg_amount", "buy_md_amount", "buy_sm_amount"],
                default_params={
                    "days": 30,
                    "focus": "main_force"
                },
                example="茅台的资金流向如何",
                requires_stock=True
            ),
            
            QueryTemplate(
                name="超大单分析",
                type=TemplateType.MONEY_FLOW,
                pattern=r"(?:分析)?(.+?)(?:的)?超大单(?:资金)?(?:流[入出向]|分析|情况|如何)?|(.+?)(?:的)?机构资金(?:流向|分析|如何|情况)",
                route_type="MONEY_FLOW",
                required_fields=["buy_elg_amount", "sell_elg_amount"],
                optional_fields=["elg_vol", "elg_amount"],
                default_params={
                    "days": 30,
                    "focus": "super_large"
                },
                example="贵州茅台的超大单资金流入情况",
                requires_stock=True
            ),
            
            # 公告查询模板（支持灵活的日期描述，包括日期范围）
            QueryTemplate(
                name="公告查询",
                type=TemplateType.ANNOUNCEMENT,
                pattern=r"(.+?)(?:的)?(?:(\d{8}|\d{4}-\d{2}-\d{2}|\d{4}年\d{2}月\d{2}日)(?:到|至)(\d{8}|\d{4}-\d{2}-\d{2}|\d{4}年\d{2}月\d{2}日)|(\d{8}|\d{4}-\d{2}-\d{2}|\d{4}年\d{2}月\d{2}日|最新|最近|昨天|前天|今天|本周|本月|本年|上周|上月|去年|\d+天前|\d+天内|最近\d+天?))?(?:的)?公告(?:列表|信息|标题)?",
                route_type="SQL_ONLY",  # SQL Agent处理公告列表查询
                required_fields=["title", "ann_date", "url"],
                optional_fields=["name", "type"],
                default_params={
                    "limit": 10,
                    "time_range": "latest"
                },
                example="贵州茅台最新公告"
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
            
            # 涨跌幅排名模板（支持历史日期）
            QueryTemplate(
                name="涨跌幅排名",
                type=TemplateType.RANKING,
                pattern=r"(?:(\d{8}|\d{4}-\d{2}-\d{2}|\d{4}年\d{2}月\d{2}日|今天|昨天|上个交易日))?[\s的]?(?:涨幅|跌幅)(?:排名|排行|最大|最小)?(?:前(\d+)|的(?:前)?(\d+))?",
                route_type="SQL_ONLY",
                required_fields=["ts_code", "name", "pct_chg"],
                optional_fields=["close", "vol", "amount"],
                default_params={
                    "order_by": "pct_chg DESC",
                    "limit": 10,
                    "time_range": "specified"
                },
                example="20250627涨幅前10",
                requires_date=True,
                requires_limit=True,
                supports_exclude_st=True
            ),
            
            # 总市值排名模板（支持历史日期，兼容"市值排名"，支持无数字默认前10）
            QueryTemplate(
                name="总市值排名",
                type=TemplateType.RANKING,
                pattern=r"(?:(\d{8}|\d{4}-\d{2}-\d{2}|\d{4}年\d{2}月\d{2}日|今天|昨天|上个交易日|最新))?(?:总市值|(?<!流通)市值)(?:.*前(\d+)|.*最大.*(\d+)|排名|排行|TOP(\d+))?",
                route_type="SQL_ONLY",
                required_fields=["ts_code", "name", "total_mv"],
                optional_fields=["close", "pe_ttm", "pb"],
                default_params={
                    "order_by": "total_mv DESC",
                    "limit": 10,
                    "time_range": "specified"
                },
                example="昨天市值最大的前20只股票",
                requires_stock=False,
                requires_limit=True,
                default_limit=10
            ),
            
            # 流通市值排名模板（支持历史日期，支持无数字默认前10）
            QueryTemplate(
                name="流通市值排名",
                type=TemplateType.RANKING,
                pattern=r"(?:(\d{8}|\d{4}-\d{2}-\d{2}|\d{4}年\d{2}月\d{2}日|今天|昨天|上个交易日|最新))?流通市值(?:.*前(\d+)|.*最大.*(\d+)|排名|排行|TOP(\d+))?",
                route_type="SQL_ONLY",
                required_fields=["ts_code", "name", "circ_mv"],
                optional_fields=["total_mv", "turnover_rate", "volume_ratio"],
                default_params={
                    "order_by": "circ_mv DESC",
                    "limit": 10,
                    "time_range": "specified"
                },
                example="上个交易日流通市值前10",
                requires_stock=False,
                requires_limit=True,
                default_limit=10
            ),
            
            # PE排名模板
            QueryTemplate(
                name="PE排名", 
                type=TemplateType.RANKING,
                pattern=r"(?:PE|市盈率)(?:最高|最低|排名|前).*?(\d+)?|.*前(\d+).*(?:PE|市盈率)",
                route_type="SQL_ONLY",
                required_fields=["ts_code", "name", "pe", "pe_ttm", "close"],
                optional_fields=["pct_chg"],
                default_params={
                    "order_by": "pe DESC",
                    "limit": 10,
                    "time_range": "latest"
                },
                example="PE最高的前10"
            ),
            
            # PB排名模板
            QueryTemplate(
                name="PB排名",
                type=TemplateType.RANKING,
                pattern=r"(?:PB|市净率|破净)(?:最高|最低|排名|前).*?(\d+)?|.*前(\d+).*(?:PB|市净率)",
                route_type="SQL_ONLY",
                required_fields=["ts_code", "name", "pb", "close"],
                optional_fields=["pct_chg"],
                default_params={
                    "order_by": "pb DESC",
                    "limit": 10,
                    "time_range": "latest"
                },
                example="PB最低的前10"
            ),
            
            # 净利润排名模板
            QueryTemplate(
                name="净利润排名",
                type=TemplateType.RANKING,
                pattern=r"(?:净利润|利润|盈利|亏损)(?:最高|最多|排名|前).*?(\d+)?",
                route_type="SQL_ONLY",
                required_fields=["ts_code", "name", "net_profit", "revenue", "end_date"],
                optional_fields=["report_type"],
                default_params={
                    "order_by": "net_profit DESC",
                    "limit": 10,
                    "time_range": "latest_report"
                },
                example="利润排名前20"
            ),
            
            # 营收排名模板
            QueryTemplate(
                name="营收排名",
                type=TemplateType.RANKING,
                pattern=r"(?:营收|营业收入|收入)(?:最高的?|排名|排行|前)(?:.*?(\d+))?(?!.*分析)",
                route_type="SQL_ONLY",
                required_fields=["ts_code", "name", "revenue", "net_profit", "end_date"],
                optional_fields=["report_type"],
                default_params={
                    "order_by": "revenue DESC",
                    "limit": 10,
                    "time_range": "latest_report"
                },
                example="营收排名前10"
            ),
            
            # ROE排名模板
            QueryTemplate(
                name="ROE排名",
                type=TemplateType.RANKING,
                pattern=r"(?:ROE|净资产收益率)(?:最高|排名|前).*?(\d+)?",
                route_type="SQL_ONLY",
                required_fields=["ts_code", "name", "roe", "roa", "end_date"],
                optional_fields=[],
                default_params={
                    "order_by": "roe DESC",
                    "limit": 10,
                    "time_range": "latest_report"
                },
                example="ROE排名前10"
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
                
            # 特殊处理K线查询的天数参数
            if template.name == "K线查询":
                # 改进后的K线查询正则表达式的捕获组：
                # 1: 股票名称
                # 2: 开始日期（从X到Y格式）
                # 3: 结束日期（从X到Y格式）
                # 4: 最近N天
                # 5: 过去N天
                # 6: 最近N月
                # 7: 过去N月
                # 8: 近N交易日
                # 9: 最近N个交易日
                full_groups = match.groups()
                
                # 提取日期范围（从X到Y）
                if full_groups[1] and full_groups[2]:  # 从日期到日期
                    params['start_date'] = full_groups[1]
                    params['end_date'] = full_groups[2]
                    params['time_range'] = 'date_range'
                    # 不设置days，因为是具体日期范围
                else:
                    # 提取天数（各种表达方式）
                    days = None
                    if full_groups[3]:  # 最近N天
                        days = int(full_groups[3])
                    elif full_groups[4]:  # 过去N天
                        days = int(full_groups[4])
                    elif full_groups[5]:  # 最近N月
                        days = int(full_groups[5]) * 21  # 1月约21个交易日
                    elif full_groups[6]:  # 过去N月
                        days = int(full_groups[6]) * 21
                    elif full_groups[7]:  # 近N交易日
                        days = int(full_groups[7])
                    elif full_groups[8]:  # 最近N个交易日
                        days = int(full_groups[8])
                    elif "最近一个月" in query or "最近一月" in query:
                        days = 21  # 一个月约21个交易日
                    
                    if days:
                        params['days'] = days
                        params['time_range'] = 'relative'
        
        # 提取数字参数（如排名数量）
        if template.type == TemplateType.RANKING or template.type == TemplateType.MONEY_FLOW:
            # 优先从"前N"或"最大的N"模式中提取限制数
            limit_patterns = [
                r'前(\d+)',
                r'最.*?(\d+).*?(?:只|个)',
                r'排.*?(\d+)',
                r'top\s*(\d+)'
            ]
            limit_found = False
            for pattern in limit_patterns:
                limit_match = re.search(pattern, query, re.IGNORECASE)
                if limit_match:
                    params['limit'] = int(limit_match.group(1))
                    limit_found = True
                    break
            
            # 对于排名类查询，不要从日期中提取数字
            # 如果没有找到特定模式，保持默认值（通常是10）
        
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