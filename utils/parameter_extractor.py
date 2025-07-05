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
    sector_code: Optional[str] = None                    # 板块代码（如BK1036.DC）
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
            
            # 提取指标（无论有没有模板都应该尝试提取）
            # 获取默认可用指标列表
            default_metrics = [
                'open', 'high', 'low', 'close', 'vol', 'amount', 
                'pct_chg', 'turnover_rate', 'pe_ttm', 'pb', 'roe',
                'market_cap', 'circ_market_cap', 'total_revenue', 'n_income'
            ]
            self._extract_metrics(cleaned_query, params, default_metrics)
            
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
        # 先尝试提取ST股票（包括*ST）
        # 使用更准确的模式，匹配ST后面的中文字符，但不包含连接词
        # 使用负向预查来停止在连接词前
        st_pattern = r'\*?ST[\u4e00-\u9fa5]+?(?=[和与及、，,]|$|\s|的|最|从)'
        st_matches = re.findall(st_pattern, query)
        
        # 如果找到ST股票，先处理它们
        if st_matches:
            from utils.stock_validation_helper import validate_and_convert_stock
            for st_stock in st_matches:
                success, ts_code, stock_name, error_msg = validate_and_convert_stock(st_stock)
                if success:
                    params.stocks.append(ts_code)
                    params.stock_names.append(stock_name)
                    self.logger.info(f"提取到ST股票: {st_stock} -> {ts_code}")
            
            # 如果成功提取了ST股票，检查是否还有其他股票
            # 从查询中移除已提取的ST股票，避免重复
            remaining_query = query
            for st_stock in st_matches:
                remaining_query = remaining_query.replace(st_stock, '')
            
            # 使用剩余查询继续提取其他股票
            if remaining_query.strip():
                stock_list = self.stock_validator.extract_multiple_stocks(remaining_query)
                if stock_list:
                    from utils.stock_validation_helper import validate_and_convert_stock
                    for stock in stock_list:
                        if stock not in params.stocks:  # 避免重复
                            success, ts_code, stock_name, error_msg = validate_and_convert_stock(stock)
                            if success:
                                params.stocks.append(ts_code)
                                params.stock_names.append(stock_name)
        else:
            # 没有ST股票，使用正常流程
            # 直接使用extract_multiple_stocks，它会处理多个股票的情况
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
                # extract_multiple_stocks返回空列表，可能是单个股票验证失败
                # 尝试使用validate_and_extract获取具体错误信息
                success, ts_code_or_error, error_response = self.stock_validator.validate_and_extract(query)
                if not success and error_response and 'error' in error_response:
                    params.error = error_response['error']
                    self.logger.warning(f"股票验证失败: {params.error}")
        
        # 如果成功提取了股票，记录日志
        if params.stocks:
            self.logger.info(f"提取到股票: {params.stocks}")
        elif not params.error:
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
                '的走势', '的价格', '的数据', '的行情', '的分析',
                '股价', 'K线', '成交量', '市值', '涨跌',
                'PE', 'PB', 'ROE', '市盈率', '市净率',
                '走势', '价格', '数据', '行情', '分析'
            ]
            needs_specific_stock = any(keyword in query for keyword in specific_stock_keywords)
            
            if needs_specific_stock and not is_non_stock_query:
                # 尝试提取可能的股票名称或代码
                # 添加专门匹配ST股票的模式
                st_pattern = r'(\*?ST[\u4e00-\u9fa5]+)'
                st_matches = re.findall(st_pattern, query)
                
                # 先尝试匹配中文字符后跟"的"模式
                pattern1 = r'([\u4e00-\u9fa5A-Z0-9]+)的'
                match1 = re.search(pattern1, query)
                
                # 如果没有"的"，尝试匹配"股票名+关键词"模式
                pattern2 = r'^([\u4e00-\u9fa5A-Z0-9]+)(股价|市值|K线|成交量|走势|价格|涨跌|PE|PB|ROE)'
                match2 = re.search(pattern2, query)
                
                # 优先处理ST股票
                if st_matches:
                    for st_stock in st_matches:
                        from utils.stock_validation_helper import validate_and_convert_stock
                        success, ts_code, stock_name, error_msg = validate_and_convert_stock(st_stock)
                        if not success and not params.error:
                            params.error = error_msg
                            self.logger.warning(f"股票验证失败: {st_stock} - {error_msg}")
                else:
                    match = match1 or match2
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
            r'\d{4}年?\d{1,2}月?到',
            r'最近一[周月年]',
            r'过去一[周月年]'
        ]
        
        for pattern in date_range_patterns:
            if re.search(pattern, query):
                # 这是日期范围查询，不提取单个日期
                return
        
        # 首先尝试直接匹配常见日期格式
        date_patterns = [
            # YYYY-MM-DD格式
            (r'(\d{4})-(\d{1,2})-(\d{1,2})', lambda m: f"{m.group(1)}-{m.group(2).zfill(2)}-{m.group(3).zfill(2)}"),
            # YYYY年MM月DD日格式
            (r'(\d{4})年(\d{1,2})月(\d{1,2})日', lambda m: f"{m.group(1)}-{m.group(2).zfill(2)}-{m.group(3).zfill(2)}"),
            # YYYYMMDD格式
            (r'(\d{4})(\d{2})(\d{2})(?![.\d])', lambda m: f"{m.group(1)}-{m.group(2)}-{m.group(3)}"),
            # YYYY/MM/DD格式
            (r'(\d{4})/(\d{1,2})/(\d{1,2})', lambda m: f"{m.group(1)}-{m.group(2).zfill(2)}-{m.group(3).zfill(2)}")
        ]
        
        for pattern, formatter in date_patterns:
            match = re.search(pattern, query)
            if match:
                params.date = formatter(match)
                self.logger.info(f"提取到日期: {params.date}")
                return
        
        # 处理相对日期（昨天、前天、上个交易日等）
        # 这些相对日期应该被识别为单个日期，而不是日期范围
        single_date_keywords = [
            '昨天', '前天', '今天', '最新', '最后', '上个交易日', '最近交易日', '最近一个交易日',
            '最后一个交易日', '最后的', '大前天'
        ]
        
        # 检查是否包含"前N个交易日"或"上N个交易日"的模式
        trading_day_pattern = r'[前上](\d+)个交易日'
        trading_day_match = re.search(trading_day_pattern, query)
        if trading_day_match:
            single_date_keywords.append(trading_day_match.group(0))
            
        # 检查是否包含"N天前"、"N个月前"、"N年前"的模式
        time_ago_pattern = r'(\d+)个?[天月年]前'
        time_ago_match = re.search(time_ago_pattern, query)
        if time_ago_match:
            single_date_keywords.append(time_ago_match.group(0))
            
        contains_single_date = any(keyword in query for keyword in single_date_keywords)
        
        if contains_single_date or '股价' in query or '价格' in query:
            # 如果包含单日期关键词或查询股价（通常是单日），使用date_intelligence处理
            processed_query, result_dict = date_intelligence.preprocess_question(query)
            
            # 提取处理后的日期
            date_pattern = r'\d{4}-\d{2}-\d{2}'
            dates = re.findall(date_pattern, processed_query)
            
            if dates:
                # 取最后一个日期（通常是最相关的）
                params.date = dates[-1]
                self.logger.info(f"提取到日期: {params.date}")
            elif result_dict.get('success') and result_dict.get('modified_question'):
                # 检查处理后的查询本身是否就是一个日期
                modified = result_dict['modified_question']
                if re.match(r'^\d{4}-\d{2}-\d{2}$', modified):
                    params.date = modified
                    self.logger.info(f"提取到日期: {params.date}")
            elif contains_single_date:
                # 如果包含单日期关键词但没有提取到日期，使用最新交易日
                if hasattr(date_intelligence, 'calculator') and hasattr(date_intelligence.calculator, 'get_latest_trading_day'):
                    latest_date = date_intelligence.calculator.get_latest_trading_day()
                    if latest_date:
                        params.date = latest_date
                        self.logger.info(f"使用最新交易日: {params.date}")
    
    def _extract_date_range(self, query: str, params: ExtractedParams) -> None:
        """提取日期范围"""
        # 首先尝试提取明确的日期范围格式
        # 支持多种日期格式和连接符
        # 包括中文日期格式
        date_pattern = r'(\d{4}[-/]?\d{1,2}[-/]?\d{1,2}|\d{4}年\d{1,2}月\d{1,2}日)'
        
        # 格式1: 从...到...
        pattern1 = rf'从{date_pattern}到{date_pattern}'
        match1 = re.search(pattern1, query)
        if match1:
            start_date = self._normalize_date(match1.group(1))
            end_date = self._normalize_date(match1.group(2))
            if start_date and end_date:
                params.date_range = (start_date, end_date)
                self.logger.info(f"提取到日期范围: {params.date_range[0]} 至 {params.date_range[1]}")
                return
        
        # 格式2: ...至...
        pattern2 = rf'{date_pattern}至{date_pattern}'
        match2 = re.search(pattern2, query)
        if match2:
            start_date = self._normalize_date(match2.group(1))
            end_date = self._normalize_date(match2.group(2))
            if start_date and end_date:
                params.date_range = (start_date, end_date)
                self.logger.info(f"提取到日期范围: {params.date_range[0]} 至 {params.date_range[1]}")
                return
        
        # 格式3: ...-... (连字符连接)
        pattern3 = rf'{date_pattern}-{date_pattern}'
        match3 = re.search(pattern3, query)
        if match3:
            start_date = self._normalize_date(match3.group(1))
            end_date = self._normalize_date(match3.group(2))
            if start_date and end_date and start_date != end_date:  # 避免误识别单个日期
                params.date_range = (start_date, end_date)
                self.logger.info(f"提取到日期范围: {params.date_range[0]} 至 {params.date_range[1]}")
                return
        
        # 格式4: ...~... (波浪号连接)
        pattern4 = rf'{date_pattern}~{date_pattern}'
        match4 = re.search(pattern4, query)
        if match4:
            start_date = self._normalize_date(match4.group(1))
            end_date = self._normalize_date(match4.group(2))
            if start_date and end_date:
                params.date_range = (start_date, end_date)
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
        
        # 格式4: 自然语言时间表达
        time_mappings = {
            "一周": 7,
            "1周": 7,
            "一个月": 30,
            "1个月": 30,
            "三个月": 90,
            "3个月": 90,
            "半年": 180,
            "一年": 365,
            "1年": 365,
            "2年": 730
        }
        
        for time_word, days in time_mappings.items():
            if f"最近{time_word}" in query or f"过去{time_word}" in query or f"前{time_word}" in query:
                if hasattr(date_intelligence.calculator, 'get_trading_days_range'):
                    result = date_intelligence.calculator.get_trading_days_range(days)
                    if result:
                        params.date_range = result
                        self.logger.info(f"提取到日期范围（{time_word}）: {result[0]} 至 {result[1]}")
                        return
        
        # 处理月份范围
        # 格式1: "2025年1月到3月"
        month_range_pattern1 = r'(\d{4})年(\d{1,2})月到(\d{1,2})月'
        match1 = re.search(month_range_pattern1, query)
        if match1:
            year = int(match1.group(1))
            start_month = int(match1.group(2))
            end_month = int(match1.group(3))
            import calendar
            start_date = f"{year}-{start_month:02d}-01"
            last_day = calendar.monthrange(year, end_month)[1]
            end_date = f"{year}-{end_month:02d}-{last_day:02d}"
            params.date_range = (start_date, end_date)
            self.logger.info(f"提取到月份范围: {start_date} 至 {end_date}")
            return
            
        # 格式2: "2025年1月到2025年3月"
        month_range_pattern2 = r'(\d{4})年(\d{1,2})月到(\d{4})年(\d{1,2})月'
        match2 = re.search(month_range_pattern2, query)
        if match2:
            start_year = int(match2.group(1))
            start_month = int(match2.group(2))
            end_year = int(match2.group(3))
            end_month = int(match2.group(4))
            import calendar
            start_date = f"{start_year}-{start_month:02d}-01"
            last_day = calendar.monthrange(end_year, end_month)[1]
            end_date = f"{end_year}-{end_month:02d}-{last_day:02d}"
            params.date_range = (start_date, end_date)
            self.logger.info(f"提取到月份范围: {start_date} 至 {end_date}")
            return
        
        # 处理单个月份（如"2025年1月的数据"）
        month_pattern = r'(\d{4})年(\d{1,2})月'
        month_match = re.search(month_pattern, query)
        if month_match and '到' not in query and '至' not in query:
            year = int(month_match.group(1))
            month = int(month_match.group(2))
            # 计算该月的第一天和最后一天
            import calendar
            last_day = calendar.monthrange(year, month)[1]
            start_date = f"{year}-{month:02d}-01"
            end_date = f"{year}-{month:02d}-{last_day:02d}"
            params.date_range = (start_date, end_date)
            self.logger.info(f"提取到月份范围: {start_date} 至 {end_date}")
            return
            
        # 处理年份范围
        # 格式1: "2023年到2024年"
        year_range_pattern1 = r'(\d{4})年?到(\d{4})年?'
        match1 = re.search(year_range_pattern1, query)
        if match1:
            start_year = int(match1.group(1))
            end_year = int(match1.group(2))
            start_date = f"{start_year}-01-01"
            end_date = f"{end_year}-12-31"
            params.date_range = (start_date, end_date)
            self.logger.info(f"提取到年份范围: {start_date} 至 {end_date}")
            return
            
        # 处理单个年份（如"2024年的数据"）
        year_pattern = r'(\d{4})年的'
        year_match = re.search(year_pattern, query)
        if year_match and '到' not in query and '至' not in query:
            year = int(year_match.group(1))
            start_date = f"{year}-01-01"
            end_date = f"{year}-12-31"
            params.date_range = (start_date, end_date)
            self.logger.info(f"提取到年份范围: {start_date} 至 {end_date}")
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
        
        # 排除股票代码（6位数字）
        # 如果已经提取到股票，不应该再把股票代码当作数量
        if params.stocks:
            # 移除已识别的股票代码
            for stock in params.stocks:
                # 提取股票代码的数字部分
                code_match = re.match(r'(\d{6})', stock)
                if code_match:
                    code = code_match.group(1)
                    query_without_year = re.sub(rf'\b{code}\b', '', query_without_year)
        
        # 排除股票名称，避免"万科A"的"万"被识别为10000
        if params.stock_names:
            for stock_name in params.stock_names:
                query_without_year = query_without_year.replace(stock_name, '')
        
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
        if any(keyword in query for keyword in ['排除ST', '不含ST', '剔除ST', '去除ST', '非ST股票', '排除*ST']):
            params.exclude_st = True
            self.logger.info("排除ST股票")
            
        # 检查是否排除北交所
        # 注意：也要处理"和北交所"这种情况（当与ST一起排除时）
        if any(keyword in query for keyword in ['排除北交所', '不含北交所', '剔除北交所', '去除北交所', '非北交所股票']):
            params.exclude_bj = True
            self.logger.info("排除北交所股票")
        elif params.exclude_st and '北交所' in query:
            # 处理"排除ST和北交所"这种组合情况
            params.exclude_bj = True
            self.logger.info("排除北交所股票")
    
    def _extract_order_params(self, query: str, params: ExtractedParams) -> None:
        """提取排序参数"""
        # 排序方向
        # 注意：某些指标的"最低"实际上应该是降序（如跌幅最大）
        # 先检查特殊情况
        if '跌幅' in query and any(keyword in query for keyword in ['最大', '最多', '榜']):
            # 跌幅最大 = 涨幅最小 = ASC
            # 跌幅榜 = 跌幅从大到小 = ASC
            params.order_by = 'ASC'
        elif any(keyword in query for keyword in ['最高', '最大', '最多', '降序', '从高到低']):
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
        elif '涨幅' in query or '涨跌幅' in query or '跌幅' in query:
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
        elif '利润' in query or '净利润' in query:
            params.order_field = 'n_income'
        elif '营收' in query or '营业收入' in query or '收入' in query:
            params.order_field = 'total_revenue'
        elif '换手率' in query:
            params.order_field = 'turnover_rate'
    
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
                
                # 尝试获取板块代码
                try:
                    from utils.sector_code_mapper import get_sector_code
                    sector_code = get_sector_code(sector_name)
                    if sector_code:
                        # 在params中添加板块代码字段
                        if not hasattr(params, 'sector_code'):
                            params.sector_code = sector_code
                        else:
                            params.sector_code = sector_code
                        self.logger.info(f"板块代码映射: {sector_name} -> {sector_code}")
                    else:
                        self.logger.warning(f"未找到板块代码映射: {sector_name}")
                except Exception as e:
                    self.logger.warning(f"板块代码映射失败: {e}")
            else:
                params.industry = sector_name
                self.logger.info(f"提取到行业: {sector_name}")
    
    def _extract_period(self, query: str, params: ExtractedParams) -> None:
        """提取报告期"""
        # 报告期模式
        period_patterns = [
            (r'(\d{4})年?年报', lambda m: f"{m.group(1)}1231"),
            (r'(\d{4})年?度报告', lambda m: f"{m.group(1)}1231"),
            (r'(\d{4})年?全年', lambda m: f"{m.group(1)}1231"),
            (r'(\d{4})年?一季[度报]?', lambda m: f"{m.group(1)}0331"),
            (r'(\d{4})年?第一季度', lambda m: f"{m.group(1)}0331"),
            (r'(\d{4})年?Q1', lambda m: f"{m.group(1)}0331"),
            (r'(\d{4})年?二季[度报]?', lambda m: f"{m.group(1)}0630"),
            (r'(\d{4})年?第二季度', lambda m: f"{m.group(1)}0630"),
            (r'(\d{4})年?Q2', lambda m: f"{m.group(1)}0630"),
            (r'(\d{4})年?三季[度报]?', lambda m: f"{m.group(1)}0930"),
            (r'(\d{4})年?第三季度', lambda m: f"{m.group(1)}0930"),
            (r'(\d{4})年?Q3', lambda m: f"{m.group(1)}0930"),
            (r'(\d{4})年?四季[度报]?', lambda m: f"{m.group(1)}1231"),
            (r'(\d{4})年?第四季度', lambda m: f"{m.group(1)}1231"),
            (r'(\d{4})年?Q4', lambda m: f"{m.group(1)}1231"),
            (r'(\d{4})年?中报', lambda m: f"{m.group(1)}0630"),
            (r'(\d{4})年?半年报', lambda m: f"{m.group(1)}0630"),
            (r'(\d{4})年?中期报告', lambda m: f"{m.group(1)}0630"),
            (r'(\d{4})年?上半年', lambda m: f"{m.group(1)}0630"),
            (r'(\d{8})', lambda m: m.group(1))  # 直接的8位日期
        ]
        
        for pattern, formatter in period_patterns:
            match = re.search(pattern, query)
            if match:
                params.period = formatter(match)
                self.logger.info(f"提取到报告期: {params.period}")
                break
    
    def _normalize_date(self, date_str: str) -> Optional[str]:
        """
        标准化日期格式为YYYY-MM-DD
        
        Args:
            date_str: 日期字符串
            
        Returns:
            标准化的日期字符串
        """
        try:
            # 首先检查中文日期格式
            chinese_match = re.match(r'(\d{4})年(\d{1,2})月(\d{1,2})日', date_str)
            if chinese_match:
                year = chinese_match.group(1)
                month = chinese_match.group(2).zfill(2)
                day = chinese_match.group(3).zfill(2)
                return f"{year}-{month}-{day}"
            
            # 移除所有分隔符
            digits = re.sub(r'[-/]', '', date_str)
            
            # 如果是8位数字
            if len(digits) == 8 and digits.isdigit():
                year = digits[:4]
                month = digits[4:6]
                day = digits[6:8]
                return f"{year}-{month}-{day}"
            
            # 如果包含分隔符，尝试解析
            match = re.match(r'(\d{4})[-/](\d{1,2})[-/](\d{1,2})', date_str)
            if match:
                year = match.group(1)
                month = match.group(2).zfill(2)
                day = match.group(3).zfill(2)
                return f"{year}-{month}-{day}"
                
        except Exception as e:
            self.logger.warning(f"日期标准化失败: {date_str}, 错误: {e}")
            
        return None


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