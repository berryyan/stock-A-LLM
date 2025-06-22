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
        
        # 时间关键词模式
        self.time_patterns = {
            '最新': ['最新', '最近', '最新的', '最近的', '现在的', '当前的'],
            '最近N日': ['最近(\d+)天', '最近(\d+)日', '近(\d+)天', '近(\d+)日'],
            '最近N月': ['最近(\d+)个月', '近(\d+)个月', '最近(\d+)月', '近(\d+)月'],
            '最近N年': ['最近(\d+)年', '近(\d+)年'],
            '年报': ['年报', '年度报告', '年度业绩'],
            '季报': ['季报', '季度报告', '一季报', '二季报', '三季报', '四季报'],
            '半年报': ['半年报', '中报', '半年度报告'],
            '股价数据': ['股价', '价格', '收盘价', '开盘价', '最高价', '最低价', '成交量', '成交额', '涨跌幅'],
            '财务数据': ['营收', '利润', '净利润', '资产', '负债', '现金流', 'ROE', 'ROA', '毛利率', '财务数据', '财务', '业绩'],
            '公告': ['公告', '披露', '发布', '通知', '声明']
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
                query = """
                SELECT trade_date 
                FROM tu_daily_detail 
                WHERE trade_date < CURDATE()
                ORDER BY trade_date DESC 
                LIMIT 1
                """
                result = self.mysql.execute_query(query)
            
            if result and len(result) > 0:
                latest_date = str(result[0]['trade_date'])
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
            'time_type': None,  # 'latest', 'recent_n', 'specific'
            'data_type': None,  # 'stock_price', 'financial', 'announcement'
            'report_type': None,  # 'annual', 'quarterly', 'interim'
            'time_value': None,
            'keywords': []
        }
        
        question_lower = question.lower()
        
        # 检测时间关键词
        for pattern_type, patterns in self.time_patterns.items():
            for pattern in patterns:
                if pattern_type == '最新':
                    if pattern in question:
                        context['has_time_reference'] = True
                        context['time_type'] = 'latest'
                        context['keywords'].append(pattern)
                
                elif pattern_type.startswith('最近N'):
                    match = re.search(pattern, question)
                    if match:
                        context['has_time_reference'] = True
                        context['time_type'] = 'recent_n'
                        context['time_value'] = int(match.group(1))
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