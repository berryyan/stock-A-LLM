#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
参数提取器模块
统一处理所有查询的参数提取逻辑
"""

import sys
import os
import re
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.unified_stock_validator import UnifiedStockValidator
from utils.date_intelligence import date_intelligence
from utils.chinese_number_converter import extract_limit_from_query, normalize_quantity_expression
from utils.logger import setup_logger
from utils.query_templates import QueryTemplate

logger = setup_logger("parameter_extractor")


@dataclass
class ExtractedParams:
    """提取的参数数据类"""
    stocks: List[str] = field(default_factory=list)     # 股票列表（ts_code格式）
    stock_names: List[str] = field(default_factory=list) # 股票名称列表
    date: Optional[str] = None                           # 单个日期
    date_range: Optional[Tuple[str, str]] = None        # 日期范围
    limit: int = 10                                      # 数量限制
    order_by: str = 'DESC'                               # 排序方式
    order_field: Optional[str] = None                    # 排序字段
    metrics: List[str] = field(default_factory=list)     # 指标列表
    period: Optional[str] = None                         # 报告期
    exclude_st: bool = False                             # 排除ST
    exclude_bj: bool = False                             # 排除北交所
    sector: Optional[str] = None                         # 板块名称
    industry: Optional[str] = None                       # 行业名称
    raw_query: str = ""                                  # 原始查询
    error: Optional[str] = None                          # 错误信息


class ParameterExtractor:
    """统一的参数提取器"""
    
    def __init__(self):
        """初始化参数提取器"""
        self.stock_validator = UnifiedStockValidator()
        self.logger = logger
        
    def extract_all_params(self, query: str, template: Optional[QueryTemplate] = None) -> ExtractedParams:
        """
        从查询中提取所有参数
        
        Args:
            query: 原始查询字符串
            template: 查询模板（可选）
            
        Returns:
            ExtractedParams: 提取的参数对象
        """
        params = ExtractedParams(raw_query=query)
        
        try:
            # 清理查询字符串
            cleaned_query = self._clean_query(query)
            
            # 根据模板需求提取相应参数
            if template:
                if template.requires_stock:
                    self._extract_stocks(cleaned_query, params)
                    
                if template.requires_date:
                    self._extract_date(cleaned_query, params)
                    
                if template.requires_date_range:
                    self._extract_date_range(cleaned_query, params)
                    
                if template.requires_limit:
                    self._extract_limit(cleaned_query, params, template.default_limit)
                    
                if template.supports_exclude_st:
                    self._check_exclude_conditions(cleaned_query, params)
                    
                # 提取其他特定参数
                if hasattr(template, 'required_fields'):
                    self._extract_metrics(cleaned_query, params, template.required_fields)
            else:
                # 没有模板时，尝试提取所有可能的参数
                self._extract_stocks(cleaned_query, params)
                self._extract_date(cleaned_query, params)
                self._extract_date_range(cleaned_query, params)
                self._extract_limit(cleaned_query, params)
                self._check_exclude_conditions(cleaned_query, params)
                self._extract_sector_or_industry(cleaned_query, params)
                
            # 提取排序相关参数
            self._extract_order_params(cleaned_query, params)
            
            # 提取报告期
            self._extract_period(cleaned_query, params)
            
        except Exception as e:
            self.logger.error(f"参数提取失败: {e}")
            params.error = f"参数提取失败: {str(e)}"
            
        return params
    
    def _clean_query(self, query: str) -> str:
        """清理查询字符串"""
        # 去除多余空格
        query = re.sub(r'\s+', ' ', query.strip())
        return query
    
    def _extract_stocks(self, query: str, params: ExtractedParams) -> None:
        """提取股票信息"""
        # 使用UnifiedStockValidator提取多个股票
        stock_list = self.stock_validator.extract_multiple_stocks(query)
        
        if stock_list:
            # 验证并转换每个股票
            from utils.stock_validation_helper import validate_and_convert_stock
            
            valid_count = 0
            for stock in stock_list:
                success, ts_code, stock_name, error_msg = validate_and_convert_stock(stock)
                if success:
                    params.stocks.append(ts_code)
                    params.stock_names.append(stock_name)
                    valid_count += 1
                else:
                    # 记录第一个错误
                    if not params.error:
                        params.error = error_msg
            
            # 如果没有有效的股票，保留错误信息            
            if valid_count > 0:
                self.logger.info(f"提取到股票: {params.stocks}")
            else:
                self.logger.warning(f"未能提取到有效股票，错误: {params.error}")
        else:
            # 如果查询中可能包含股票但没有提取到，尝试识别
            # 首先排除明显的非股票查询（排名查询等）
            non_stock_patterns = [
                r'排名|排行|前\d+|最[大小高低]的?\d*只?股票',
                r'涨幅榜|跌幅榜|龙虎榜',
                r'板块|行业|概念'
            ]
            
            is_non_stock_query = any(re.search(pattern, query) for pattern in non_stock_patterns)
            
            # 检查是否包含股票相关的关键词且需要特定股票
            specific_stock_keywords = [
                '的股价', '的K线', '的成交量', '的市值', '的涨跌',
                '的PE', '的PB', '的ROE', '的市盈率', '的市净率',
                '的走势', '的价格', '的数据', '的行情', '的分析'
            ]
            needs_specific_stock = any(keyword in query for keyword in specific_stock_keywords)
            
            if needs_specific_stock and not is_non_stock_query:
                # 尝试提取可能的股票名称或代码
                # 匹配中文字符后跟"的"模式
                pattern = r'([\u4e00-\u9fa5A-Z0-9]+)的'
                match = re.search(pattern, query)
                if match:
                    potential_stock = match.group(1)
                    # 验证这个潜在的股票
                    from utils.stock_validation_helper import validate_and_convert_stock
                    success, ts_code, stock_name, error_msg = validate_and_convert_stock(potential_stock)
                    if not success:
                        params.error = error_msg
                        self.logger.warning(f"股票验证失败: {potential_stock} - {error_msg}")
    
    def _extract_date(self, query: str, params: ExtractedParams) -> None:
        """提取单个日期"""
        # 首先检查是否是日期范围查询
        date_range_patterns = [
            r'从.*?到',
            r'最近\d+天',
            r'过去\d+天',
            r'最近\d+个?月',
            r'前\d+天',
            r'\d{4}年?\d{1,2}月?到'
        ]
        
        for pattern in date_range_patterns:
            if re.search(pattern, query):
                # 这是日期范围查询，不提取单个日期
                return
        
        # 使用date_intelligence处理自然语言日期
        processed_query, result_dict = date_intelligence.preprocess_question(query)
        
        # 提取处理后的日期
        date_pattern = r'\d{4}-\d{2}-\d{2}'
        dates = re.findall(date_pattern, processed_query)
        
        if dates:
            # 取最后一个日期（通常是最相关的）
            params.date = dates[-1]
            self.logger.info(f"提取到日期: {params.date}")
    
    def _extract_date_range(self, query: str, params: ExtractedParams) -> None:
        """提取日期范围"""
        # 首先尝试提取明确的日期范围格式
        # 格式1: 从YYYY-MM-DD到YYYY-MM-DD
        pattern1 = r'从(\d{4}-\d{2}-\d{2})到(\d{4}-\d{2}-\d{2})'
        match1 = re.search(pattern1, query)
        if match1:
            params.date_range = (match1.group(1), match1.group(2))
            self.logger.info(f"提取到日期范围: {params.date_range[0]} 至 {params.date_range[1]}")
            return
            
        # 格式2: 最近N天
        pattern2 = r'最近(\d+)天'
        match2 = re.search(pattern2, query)
        if match2:
            days = int(match2.group(1))
            # 使用date_intelligence获取交易日范围
            if hasattr(date_intelligence.calculator, 'get_trading_days_range'):
                result = date_intelligence.calculator.get_trading_days_range(days)
                if result:
                    params.date_range = result
                    self.logger.info(f"提取到日期范围（最近{days}天）: {result[0]} 至 {result[1]}")
                    return
        
        # 格式3: 过去N天
        pattern3 = r'过去(\d+)天'
        match3 = re.search(pattern3, query)
        if match3:
            days = int(match3.group(1))
            if hasattr(date_intelligence.calculator, 'get_trading_days_range'):
                result = date_intelligence.calculator.get_trading_days_range(days)
                if result:
                    params.date_range = result
                    self.logger.info(f"提取到日期范围（过去{days}天）: {result[0]} 至 {result[1]}")
                    return
        
        # 如果都没匹配到，尝试使用date_intelligence预处理
        processed_query, _ = date_intelligence.preprocess_question(query)
        
        # 再次尝试提取处理后的日期范围
        dates = re.findall(r'\d{4}-\d{2}-\d{2}', processed_query)
        if len(dates) >= 2:
            params.date_range = (dates[0], dates[1])
            self.logger.info(f"提取到日期范围: {dates[0]} 至 {dates[1]}")
    
    def _extract_limit(self, query: str, params: ExtractedParams, default: int = 10) -> None:
        """提取数量限制"""
        # 首先排除年份（4位数字且在合理年份范围内）
        # 移除所有年份相关的内容，避免干扰
        year_pattern = r'(19\d{2}|20\d{2})年'
        query_without_year = re.sub(year_pattern, '', query)
        
        # 使用chinese_number_converter提取数量
        limit = extract_limit_from_query(query_without_year)
        
        if limit:
            params.limit = limit
        else:
            params.limit = default
            
        self.logger.info(f"数量限制: {params.limit}")
    
    def _check_exclude_conditions(self, query: str, params: ExtractedParams) -> None:
        """检查排除条件"""
        # 检查是否排除ST股票
        if any(keyword in query for keyword in ['排除ST', '不含ST', '剔除ST', '去除ST']):
            params.exclude_st = True
            self.logger.info("排除ST股票")
            
        # 检查是否排除北交所
        if any(keyword in query for keyword in ['排除北交所', '不含北交所', '剔除北交所', '去除北交所', '北交所']):
            # 额外检查是否真的是排除语境
            if '排除' in query or '不含' in query or '剔除' in query or '去除' in query:
                params.exclude_bj = True
                self.logger.info("排除北交所股票")
    
    def _extract_order_params(self, query: str, params: ExtractedParams) -> None:
        """提取排序参数"""
        # 排序方向
        if any(keyword in query for keyword in ['最高', '最大', '最多', '降序', '从高到低']):
            params.order_by = 'DESC'
        elif any(keyword in query for keyword in ['最低', '最小', '最少', '升序', '从低到高']):
            params.order_by = 'ASC'
            
        # 排序字段（根据查询内容推断）
        if '总市值' in query:
            params.order_field = 'market_cap'
        elif '流通市值' in query:
            params.order_field = 'circ_market_cap'
        elif '市值' in query:
            # 默认使用总市值
            params.order_field = 'market_cap'
        elif '涨幅' in query or '涨跌幅' in query:
            params.order_field = 'pct_chg'
        elif '成交额' in query:
            params.order_field = 'amount'
        elif '成交量' in query:
            params.order_field = 'vol'
        elif 'PE' in query or '市盈率' in query:
            params.order_field = 'pe_ttm'
        elif 'PB' in query or '市净率' in query:
            params.order_field = 'pb'
        elif 'ROE' in query:
            params.order_field = 'roe'
        elif '利润' in query:
            params.order_field = 'n_income'
        elif '营收' in query or '营业收入' in query:
            params.order_field = 'total_revenue'
    
    def _extract_metrics(self, query: str, params: ExtractedParams, available_metrics: List[str]) -> None:
        """提取需要的指标列表"""
        # 根据查询内容和可用指标提取需要的指标
        extracted_metrics = []
        
        # 常见指标映射
        metric_keywords = {
            '开盘价': 'open',
            '最高价': 'high',
            '最低价': 'low',
            '收盘价': 'close',
            '成交量': 'vol',
            '成交额': 'amount',
            '涨跌幅': 'pct_chg',
            '换手率': 'turnover_rate',
            '市盈率': 'pe_ttm',
            'PE': 'pe_ttm',
            '市净率': 'pb',
            'PB': 'pb',
            'ROE': 'roe',
            '总市值': 'market_cap',
            '流通市值': 'circ_market_cap'
        }
        
        for keyword, metric in metric_keywords.items():
            if keyword in query and metric in available_metrics:
                extracted_metrics.append(metric)
                
        # 如果没有提取到任何指标，使用默认指标
        if not extracted_metrics and available_metrics:
            # 根据查询类型选择默认指标
            if '股价' in query:
                default_metrics = ['close', 'pct_chg', 'vol', 'amount']
            elif 'K线' in query or '走势' in query:
                default_metrics = ['open', 'high', 'low', 'close', 'vol', 'amount', 'pct_chg']
            elif '财务' in query:
                default_metrics = ['total_revenue', 'n_income', 'roe', 'pe_ttm', 'pb']
            else:
                default_metrics = available_metrics[:5]  # 默认取前5个
                
            extracted_metrics = [m for m in default_metrics if m in available_metrics]
            
        params.metrics = extracted_metrics
        
    def _extract_sector_or_industry(self, query: str, params: ExtractedParams) -> None:
        """提取板块或行业信息"""
        # 板块关键词
        sector_pattern = r'([\u4e00-\u9fa5]+)(板块|行业|概念)'
        match = re.search(sector_pattern, query)
        
        if match:
            sector_name = match.group(1)
            if match.group(2) == '板块':
                params.sector = sector_name
                self.logger.info(f"提取到板块: {sector_name}")
            else:
                params.industry = sector_name
                self.logger.info(f"提取到行业: {sector_name}")
    
    def _extract_period(self, query: str, params: ExtractedParams) -> None:
        """提取报告期"""
        # 报告期模式
        period_patterns = [
            (r'(\d{4})年?年报', lambda m: f"{m.group(1)}1231"),
            (r'(\d{4})年?一季[度报]?', lambda m: f"{m.group(1)}0331"),
            (r'(\d{4})年?二季[度报]?', lambda m: f"{m.group(1)}0630"),
            (r'(\d{4})年?三季[度报]?', lambda m: f"{m.group(1)}0930"),
            (r'(\d{4})年?四季[度报]?', lambda m: f"{m.group(1)}1231"),
            (r'(\d{4})年?中报', lambda m: f"{m.group(1)}0630"),
            (r'(\d{4})年?半年报', lambda m: f"{m.group(1)}0630"),
            (r'(\d{8})', lambda m: m.group(1))  # 直接的8位日期
        ]
        
        for pattern, formatter in period_patterns:
            match = re.search(pattern, query)
            if match:
                params.period = formatter(match)
                self.logger.info(f"提取到报告期: {params.period}")
                break


# 测试代码
if __name__ == "__main__":
    # 创建提取器实例
    extractor = ParameterExtractor()
    
    # 测试用例
    test_queries = [
        "贵州茅台最新股价",
        "贵州茅台和五粮液的对比",
        "银行板块的主力资金",
        "涨幅前10的股票",
        "市值最大的20只股票，排除ST",
        "贵州茅台从2025-01-01到2025-06-30的K线",
        "最近30天茅台的走势",
        "贵州茅台2024年年报的净利润",
        "PE最低的前十只股票"
    ]
    
    print("参数提取测试")
    print("=" * 80)
    
    for query in test_queries:
        print(f"\n查询: {query}")
        params = extractor.extract_all_params(query)
        
        print(f"股票: {params.stocks}")
        print(f"日期: {params.date}")
        print(f"日期范围: {params.date_range}")
        print(f"数量: {params.limit}")
        print(f"排序: {params.order_by} by {params.order_field}")
        print(f"板块: {params.sector}")
        print(f"报告期: {params.period}")
        print(f"排除ST: {params.exclude_st}")
        
        if params.error:
            print(f"错误: {params.error}")