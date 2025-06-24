#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能日期解析模块
处理自然语言中的"最新"、"最近"等时间表达，智能转换为实际的交易日期或报告期
"""

import re
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from database.mysql_connector import MySQLConnector
from utils.logger import setup_logger
import time

logger = setup_logger("date_intelligence")

class DateIntelligenceModule:
    """智能日期解析模块"""
    
    def __init__(self):
        self.mysql = MySQLConnector()
        self._cache = {}
        self._cache_timestamp = {}
        self._cache_ttl = 3600  # 缓存1小时
        
        # 时间关键词模式 (增强版)
        self.time_patterns = {
            # 基于最近交易日的当前时间
            '最新': ['最新', '最近', '最新的', '最近的', '现在的', '当前的', '现在', '当前', '今天'],
            # 相对于最近交易日的历史时间
            '上一个': ['上一个交易日', '上个交易日', '昨天', '前一天', '上一天'],
            '前N个': ['前(\d+)个交易日', '前(\d+)天', '(\d+)天前', '(\d+)个交易日前'],
            # 时间段（基于最近交易日倒推）
            '最近N日': ['最近(\d+)天', '最近(\d+)日', '近(\d+)天', '近(\d+)日', '最近(\d+)个交易日'],
            '最近一周': ['最近一周', '最近1周', '近一周', '近1周', '最近7天', '最近5个交易日'],
            '最近N周': ['最近(\d+)周', '近(\d+)周', '最近(\d+)个星期'],
            '最近一月': ['最近一月', '最近1月', '近一月', '近1月', '最近一个月', '最近20个交易日'],
            '最近N月': ['最近(\d+)个月', '近(\d+)个月', '最近(\d+)月', '近(\d+)月'],
            '最近一季': ['最近一季', '最近1季', '近一季', '近1季', '最近一个季度', '最近3个月'],
            '最近N季': ['最近(\d+)季', '近(\d+)季', '最近(\d+)个季度'],
            '最近半年': ['最近半年', '近半年', '最近6个月'],
            '最近一年': ['最近一年', '最近1年', '近一年', '近1年', '最近12个月'],
            '最近N年': ['最近(\d+)年', '近(\d+)年'],
            # 报告期类型
            '年报': ['年报', '年度报告', '年度业绩', '年度财报'],
            '季报': ['季报', '季度报告', '一季报', '二季报', '三季报', '四季报', '季度业绩', '季度财报'],
            '半年报': ['半年报', '中报', '半年度报告', '半年度业绩'],
            # 数据类型识别
            '股价数据': ['股价', '价格', '收盘价', '开盘价', '最高价', '最低价', '成交量', '成交额', '涨跌幅', '市值', '换手率'],
            '财务数据': ['营收', '利润', '净利润', '资产', '负债', '现金流', 'ROE', 'ROA', '毛利率', '财务数据', '财务', '业绩', '盈利'],
            '公告': ['公告', '披露', '发布', '通知', '声明', '公布', '宣布']
        }
    
    def _is_cache_valid(self, cache_key: str) -> bool:
        """检查缓存是否有效"""
        if cache_key not in self._cache_timestamp:
            return False
        return time.time() - self._cache_timestamp[cache_key] < self._cache_ttl
    
    def _get_cache(self, cache_key: str) -> Optional[Any]:
        """获取缓存数据"""
        if self._is_cache_valid(cache_key):
            return self._cache.get(cache_key)
        return None
    
    def _set_cache(self, cache_key: str, data: Any):
        """设置缓存数据"""
        self._cache[cache_key] = data
        self._cache_timestamp[cache_key] = time.time()
    
    def clear_cache(self, pattern: Optional[str] = None):
        """
        清理缓存
        
        Args:
            pattern: 可选，清理匹配模式的缓存key，为None则清理全部
        """
        if pattern is None:
            self._cache.clear()
            self._cache_timestamp.clear()
            logger.info("已清理所有日期智能解析缓存")
        else:
            keys_to_remove = []
            for key in self._cache.keys():
                if pattern in key:
                    keys_to_remove.append(key)
            
            for key in keys_to_remove:
                self._cache.pop(key, None)
                self._cache_timestamp.pop(key, None)
            
            logger.info(f"已清理匹配'{pattern}'的缓存，共{len(keys_to_remove)}条")
    
    def get_latest_trading_day(self, before_date: Optional[str] = None) -> Optional[str]:
        """
        获取最近的交易日
        
        Args:
            before_date: 在此日期之前的最近交易日，格式YYYY-MM-DD，默认为当前日期
            
        Returns:
            最近交易日，格式YYYY-MM-DD
        """
        cache_key = f"latest_trading_day_{before_date or 'current'}"
        cached_result = self._get_cache(cache_key)
        if cached_result:
            return cached_result
        
        try:
            if before_date:
                # 格式化日期
                if len(before_date) == 8:  # YYYYMMDD格式
                    formatted_date = f"{before_date[:4]}-{before_date[4:6]}-{before_date[6:8]}"
                else:
                    formatted_date = before_date
                
                query = """
                SELECT trade_date 
                FROM tu_daily_detail 
                WHERE trade_date < :before_date
                ORDER BY trade_date DESC 
                LIMIT 1
                """
                result = self.mysql.execute_query(query, {'before_date': formatted_date})
            else:
                # 修复BUG: 查找最新的可用交易日，包括今天的数据
                # 首先尝试获取今天的数据
                today = datetime.now().strftime('%Y-%m-%d')
                query_today = """
                SELECT trade_date 
                FROM tu_daily_detail 
                WHERE trade_date = :today
                LIMIT 1
                """
                result_today = self.mysql.execute_query(query_today, {'today': today})
                
                if result_today and len(result_today) > 0:
                    # 今天有数据，返回今天
                    latest_date = str(result_today[0]['trade_date'])
                    logger.info(f"找到今日交易数据: {latest_date}")
                    self._set_cache(cache_key, latest_date)
                    return latest_date
                else:
                    # 今天没有数据，查找最近的交易日
                    query = """
                    SELECT trade_date 
                    FROM tu_daily_detail 
                    WHERE trade_date <= CURDATE()
                    ORDER BY trade_date DESC 
                    LIMIT 1
                    """
                    result = self.mysql.execute_query(query)
                    
                    if result and len(result) > 0:
                        latest_date = str(result[0]['trade_date'])
                        logger.info(f"找到最近交易日: {latest_date}")
                        self._set_cache(cache_key, latest_date)
                        return latest_date
            
            return None
            
        except Exception as e:
            logger.error(f"获取最近交易日失败: {e}")
            return None
    
    def get_latest_report_period(self, ts_code: Optional[str] = None, 
                               report_type: str = '1') -> Optional[str]:
        """
        获取最新报告期
        
        Args:
            ts_code: 股票代码，为空则获取全市场最新报告期
            report_type: 报告类型，'1'=年报，'2'=半年报，'3'=季报
            
        Returns:
            最新报告期，格式YYYYMMDD
        """
        cache_key = f"latest_report_{ts_code or 'all'}_{report_type}"
        cached_result = self._get_cache(cache_key)
        if cached_result:
            return cached_result
        
        try:
            if ts_code:
                query = """
                SELECT end_date 
                FROM tu_income 
                WHERE ts_code = :ts_code AND report_type = :report_type
                ORDER BY end_date DESC 
                LIMIT 1
                """
                result = self.mysql.execute_query(query, {'ts_code': ts_code, 'report_type': report_type})
            else:
                query = """
                SELECT end_date 
                FROM tu_income 
                WHERE report_type = :report_type
                ORDER BY end_date DESC 
                LIMIT 1
                """
                result = self.mysql.execute_query(query, {'report_type': report_type})
            
            if result and len(result) > 0:
                latest_period = str(result[0]['end_date'])
                self._set_cache(cache_key, latest_period)
                return latest_period
            
            return None
            
        except Exception as e:
            logger.error(f"获取最新报告期失败: {e}")
            return None
    
    def get_latest_announcement_date(self, ts_code: Optional[str] = None, 
                                   keywords: Optional[List[str]] = None) -> Optional[str]:
        """
        获取最新公告日期
        
        Args:
            ts_code: 股票代码
            keywords: 公告标题关键词列表
            
        Returns:
            最新公告日期，格式YYYY-MM-DD
        """
        cache_key = f"latest_ann_{ts_code or 'all'}_{'-'.join(keywords or [])}"
        cached_result = self._get_cache(cache_key)
        if cached_result:
            return cached_result
        
        try:
            # 构建查询条件
            conditions = []
            params = {}
            
            if ts_code:
                conditions.append("ts_code = :ts_code")
                params['ts_code'] = ts_code
            
            if keywords:
                keyword_conditions = []
                for i, keyword in enumerate(keywords):
                    param_key = f"keyword_{i}"
                    keyword_conditions.append(f"title LIKE :{param_key}")
                    params[param_key] = f"%{keyword}%"
                if keyword_conditions:
                    conditions.append(f"({' OR '.join(keyword_conditions)})")
            
            where_clause = ""
            if conditions:
                where_clause = "WHERE " + " AND ".join(conditions)
            
            query = f"""
            SELECT ann_date 
            FROM tu_anns_d 
            {where_clause}
            ORDER BY ann_date DESC 
            LIMIT 1
            """
            
            result = self.mysql.execute_query(query, params if params else None)
            
            if result and len(result) > 0:
                latest_date = str(result[0]['ann_date'])
                # 转换格式 YYYYMMDD -> YYYY-MM-DD
                if len(latest_date) == 8:
                    formatted_date = f"{latest_date[:4]}-{latest_date[4:6]}-{latest_date[6:8]}"
                else:
                    formatted_date = latest_date
                
                self._set_cache(cache_key, formatted_date)
                return formatted_date
            
            return None
            
        except Exception as e:
            logger.error(f"获取最新公告日期失败: {e}")
            return None
    
    def get_previous_trading_day(self, before_date: Optional[str] = None) -> Optional[str]:
        """
        获取上一个交易日
        
        Args:
            before_date: 基准日期，默认为最近交易日
            
        Returns:
            上一个交易日，格式YYYY-MM-DD
        """
        if before_date is None:
            before_date = self.get_latest_trading_day()
            
        if before_date is None:
            return None
            
        cache_key = f"previous_trading_day_{before_date}"
        cached_result = self._get_cache(cache_key)
        if cached_result:
            return cached_result
        
        try:
            query = """
            SELECT trade_date 
            FROM tu_daily_detail 
            WHERE trade_date < :before_date
            ORDER BY trade_date DESC 
            LIMIT 1
            """
            
            result = self.mysql.execute_query(query, {'before_date': before_date})
            
            if result and len(result) > 0:
                previous_date = result[0]['trade_date'].strftime('%Y-%m-%d')
                self._set_cache(cache_key, previous_date)
                return previous_date
                
            return None
            
        except Exception as e:
            logger.error(f"获取上一个交易日失败: {e}")
            return None
    
    def get_trading_days_before(self, days: int, before_date: Optional[str] = None) -> List[str]:
        """
        获取指定天数之前的交易日列表
        
        Args:
            days: 天数
            before_date: 基准日期，默认为最近交易日
            
        Returns:
            交易日列表，按时间倒序排列
        """
        if before_date is None:
            before_date = self.get_latest_trading_day()
            
        if before_date is None:
            return []
            
        cache_key = f"trading_days_before_{days}_{before_date}"
        cached_result = self._get_cache(cache_key)
        if cached_result:
            return cached_result
        
        try:
            query = f"""
            SELECT trade_date 
            FROM tu_daily_detail 
            WHERE trade_date <= :before_date
            ORDER BY trade_date DESC 
            LIMIT {days}
            """
            
            result = self.mysql.execute_query(query, {'before_date': before_date})
            
            if result:
                trading_days = [row['trade_date'].strftime('%Y-%m-%d') for row in result]
                self._set_cache(cache_key, trading_days)
                return trading_days
                
            return []
            
        except Exception as e:
            logger.error(f"获取前{days}个交易日失败: {e}")
            return []
    
    def get_date_range_by_period(self, period_type: str, period_value: int = 1, 
                                end_date: Optional[str] = None) -> Tuple[Optional[str], Optional[str]]:
        """
        根据时间段类型获取日期范围
        
        Args:
            period_type: 时间段类型 ('week', 'month', 'quarter', 'year')
            period_value: 时间段数量
            end_date: 结束日期，默认为最近交易日
            
        Returns:
            (开始日期, 结束日期) 元组
        """
        if end_date is None:
            end_date = self.get_latest_trading_day()
            
        if end_date is None:
            return None, None
            
        cache_key = f"date_range_{period_type}_{period_value}_{end_date}"
        cached_result = self._get_cache(cache_key)
        if cached_result:
            return cached_result
        
        try:
            # 根据时间段类型计算交易日数量
            if period_type == 'week':
                trading_days_needed = period_value * 5  # 1周约5个交易日
            elif period_type == 'month':
                trading_days_needed = period_value * 20  # 1月约20个交易日
            elif period_type == 'quarter':
                trading_days_needed = period_value * 60  # 1季度约60个交易日
            elif period_type == 'year':
                trading_days_needed = period_value * 240  # 1年约240个交易日
            else:
                return None, None
            
            # 获取指定数量的交易日
            trading_days = self.get_trading_days_before(trading_days_needed, end_date)
            
            if trading_days:
                start_date = trading_days[-1]  # 最早的日期
                result = (start_date, end_date)
                self._set_cache(cache_key, result)
                return result
                
            return None, None
            
        except Exception as e:
            logger.error(f"获取{period_type}期间日期范围失败: {e}")
            return None, None
    
    def detect_time_context(self, question: str) -> Dict[str, Any]:
        """
        检测问题中的时间上下文
        
        Args:
            question: 用户问题
            
        Returns:
            时间上下文信息
        """
        context = {
            'has_time_reference': False,
            'time_type': None,  # 'latest', 'previous', 'recent_n', 'recent_period', 'specific'
            'data_type': None,  # 'stock_price', 'financial', 'announcement'
            'report_type': None,  # 'annual', 'quarterly', 'interim'
            'time_value': None,
            'period_type': None,  # 'day', 'week', 'month', 'quarter', 'year'
            'keywords': []
        }
        
        question_lower = question.lower()
        
        # 检测时间关键词 (增强版)
        for pattern_type, patterns in self.time_patterns.items():
            for pattern in patterns:
                if pattern_type == '最新':
                    if pattern in question:
                        context['has_time_reference'] = True
                        context['time_type'] = 'latest'
                        context['keywords'].append(pattern)
                
                elif pattern_type == '上一个':
                    if pattern in question:
                        context['has_time_reference'] = True
                        context['time_type'] = 'previous'
                        context['keywords'].append(pattern)
                
                elif pattern_type == '前N个':
                    match = re.search(pattern, question)
                    if match:
                        context['has_time_reference'] = True
                        context['time_type'] = 'previous_n'
                        context['time_value'] = int(match.group(1))
                        context['period_type'] = 'day'
                        context['keywords'].append(match.group(0))
                
                elif pattern_type.startswith('最近N'):
                    match = re.search(pattern, question)
                    if match:
                        context['has_time_reference'] = True
                        context['time_type'] = 'recent_n'
                        context['time_value'] = int(match.group(1))
                        if '日' in pattern or '天' in pattern:
                            context['period_type'] = 'day'
                        elif '周' in pattern:
                            context['period_type'] = 'week'
                        elif '月' in pattern:
                            context['period_type'] = 'month'
                        elif '季' in pattern:
                            context['period_type'] = 'quarter'
                        elif '年' in pattern:
                            context['period_type'] = 'year'
                        context['keywords'].append(match.group(0))
                
                elif pattern_type in ['最近一周', '最近一月', '最近一季', '最近半年', '最近一年']:
                    if pattern in question:
                        context['has_time_reference'] = True
                        context['time_type'] = 'recent_period'
                        context['keywords'].append(pattern)
                        if '周' in pattern:
                            context['period_type'] = 'week'
                            context['time_value'] = 1
                        elif '月' in pattern:
                            context['period_type'] = 'month'
                            context['time_value'] = 1 if '一月' in pattern else 6 if '半年' in pattern else 1
                        elif '季' in pattern:
                            context['period_type'] = 'quarter'
                            context['time_value'] = 1
                        elif '年' in pattern:
                            context['period_type'] = 'year'
                            context['time_value'] = 1
                
                elif pattern_type == '最近N周':
                    match = re.search(pattern, question)
                    if match:
                        context['has_time_reference'] = True
                        context['time_type'] = 'recent_n'
                        context['time_value'] = int(match.group(1))
                        context['period_type'] = 'week'
                        context['keywords'].append(match.group(0))
        
        # 检测数据类型
        for keyword in self.time_patterns['股价数据']:
            if keyword in question:
                context['data_type'] = 'stock_price'
                break
        
        for keyword in self.time_patterns['财务数据']:
            if keyword in question:
                context['data_type'] = 'financial'
                break
        
        for keyword in self.time_patterns['公告']:
            if keyword in question:
                context['data_type'] = 'announcement'
                break
        
        # 检测报告类型
        if any(keyword in question for keyword in self.time_patterns['年报']):
            context['report_type'] = 'annual'
            if not context['data_type']:
                context['data_type'] = 'financial'
        elif any(keyword in question for keyword in self.time_patterns['季报']):
            context['report_type'] = 'quarterly'
            if not context['data_type']:
                context['data_type'] = 'financial'
        elif any(keyword in question for keyword in self.time_patterns['半年报']):
            context['report_type'] = 'interim'
            if not context['data_type']:
                context['data_type'] = 'financial'
        
        return context
    
    def extract_stock_code(self, question: str) -> Optional[str]:
        """
        从问题中提取股票代码
        
        Args:
            question: 用户问题
            
        Returns:
            股票代码或None
        """
        # 标准股票代码格式：6位数字.SH/SZ
        code_pattern = r'(\d{6}\.(SH|SZ))'
        match = re.search(code_pattern, question.upper())
        if match:
            return match.group(1)
        
        # 常见股票名称到代码的映射
        name_to_code = {
            '茅台': '600519.SH',
            '贵州茅台': '600519.SH',
            '五粮液': '000858.SZ',
            '平安银行': '000001.SZ',
            '招商银行': '600036.SH',
            '工商银行': '601398.SH',
            '建设银行': '601939.SH',
            '中国平安': '601318.SH',
            '万科': '000002.SZ',
            '比亚迪': '002594.SZ'
        }
        
        for name, code in name_to_code.items():
            if name in question:
                return code
        
        return None
    
    def intelligent_date_parsing(self, question: str) -> Dict[str, Any]:
        """
        智能日期解析主函数
        
        Args:
            question: 用户问题
            
        Returns:
            解析结果，包含具体日期和上下文信息
        """
        result = {
            'original_question': question,
            'parsed_date': None,
            'date_type': None,  # 'trading_day', 'report_period', 'announcement_date'
            'context': None,
            'stock_code': None,
            'suggestion': None,
            'modified_question': None
        }
        
        # 检测时间上下文
        context = self.detect_time_context(question)
        result['context'] = context
        
        # 提取股票代码
        stock_code = self.extract_stock_code(question)
        result['stock_code'] = stock_code
        
        # 如果没有时间引用，直接返回
        if not context['has_time_reference']:
            return result
        
        # 根据数据类型和时间类型解析具体日期
        if context['time_type'] == 'latest':
            if context['data_type'] == 'stock_price':
                # 股价数据 -> 最近交易日
                latest_date = self.get_latest_trading_day()
                if latest_date:
                    result['parsed_date'] = latest_date
                    result['date_type'] = 'trading_day'
                    result['suggestion'] = f"将'最新'解析为最近交易日: {latest_date}"
                    
                    # 生成修改后的问题
                    modified = question
                    for keyword in context['keywords']:
                        modified = modified.replace(keyword, latest_date)
                    result['modified_question'] = modified
            
            elif context['data_type'] == 'financial':
                # 财务数据 -> 最新报告期
                if context['report_type'] == 'annual':
                    report_type = '1'  # 年报
                elif context['report_type'] == 'interim':
                    report_type = '2'  # 半年报
                else:
                    report_type = '3'  # 季报（默认）
                
                latest_period = self.get_latest_report_period(stock_code, report_type)
                if latest_period:
                    result['parsed_date'] = latest_period
                    result['date_type'] = 'report_period'
                    result['suggestion'] = f"将'最新'解析为最新报告期: {latest_period}"
                    
                    # 生成修改后的问题
                    modified = question
                    for keyword in context['keywords']:
                        modified = modified.replace(keyword, f"{latest_period}期")
                    result['modified_question'] = modified
            
            elif context['data_type'] == 'announcement':
                # 公告数据 -> 最新公告日期
                latest_ann_date = self.get_latest_announcement_date(stock_code)
                if latest_ann_date:
                    result['parsed_date'] = latest_ann_date
                    result['date_type'] = 'announcement_date'
                    result['suggestion'] = f"将'最新'解析为最新公告日期: {latest_ann_date}"
                    
                    # 生成修改后的问题
                    modified = question
                    for keyword in context['keywords']:
                        modified = modified.replace(keyword, latest_ann_date)
                    result['modified_question'] = modified
        
        elif context['time_type'] == 'previous':
            # 上一个交易日
            if context['data_type'] == 'stock_price':
                previous_date = self.get_previous_trading_day()
                if previous_date:
                    result['parsed_date'] = previous_date
                    result['date_type'] = 'trading_day'
                    result['suggestion'] = f"将'上一个交易日'解析为: {previous_date}"
                    
                    modified = question
                    for keyword in context['keywords']:
                        modified = modified.replace(keyword, previous_date)
                    result['modified_question'] = modified
        
        elif context['time_type'] == 'previous_n':
            # 前N个交易日
            if context['data_type'] == 'stock_price' and context['time_value']:
                trading_days = self.get_trading_days_before(context['time_value'])
                if trading_days:
                    target_date = trading_days[-1]  # 第N个交易日
                    result['parsed_date'] = target_date
                    result['date_type'] = 'trading_day'
                    result['suggestion'] = f"将'前{context['time_value']}个交易日'解析为: {target_date}"
                    
                    modified = question
                    for keyword in context['keywords']:
                        modified = modified.replace(keyword, target_date)
                    result['modified_question'] = modified
        
        elif context['time_type'] in ['recent_n', 'recent_period']:
            # 最近N天/周/月等时间段
            if context['data_type'] == 'stock_price':
                if context['time_type'] == 'recent_period':
                    # 固定时间段（一周/一月/一季/半年/一年）
                    period_type = context['period_type']
                    period_value = context['time_value']
                else:
                    # 数值时间段（最近N天/周/月）
                    period_type = context['period_type']
                    period_value = context['time_value']
                
                if period_type and period_value:
                    start_date, end_date = self.get_date_range_by_period(period_type, period_value)
                    if start_date and end_date:
                        result['parsed_date'] = f"{start_date}至{end_date}"
                        result['date_type'] = 'date_range'
                        result['suggestion'] = f"将'{context['keywords'][0]}'解析为时间范围: {start_date}至{end_date}"
                        
                        modified = question
                        for keyword in context['keywords']:
                            modified = modified.replace(keyword, f"{start_date}至{end_date}期间")
                        result['modified_question'] = modified
        
        return result
    
    def preprocess_question(self, question: str) -> Tuple[str, Dict[str, Any]]:
        """
        预处理问题，将时间表达转换为具体日期
        
        Args:
            question: 原始问题
            
        Returns:
            (处理后的问题, 解析结果)
        """
        parsing_result = self.intelligent_date_parsing(question)
        
        if parsing_result['modified_question']:
            processed_question = parsing_result['modified_question']
            logger.info(f"日期智能解析: '{question}' -> '{processed_question}'")
            logger.info(f"解析详情: {parsing_result['suggestion']}")
        else:
            processed_question = question
        
        return processed_question, parsing_result

# 全局实例
date_intelligence = DateIntelligenceModule()

# 清理缓存以修复BUG
date_intelligence.clear_cache("latest_trading_day")