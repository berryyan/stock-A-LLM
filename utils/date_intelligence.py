#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能日期解析模块 v2.0
处理自然语言中的时间表达，智能转换为实际的交易日期或报告期

核心原则：
1. 区分时间点（单一日期）和时间段（日期范围）
2. 使用专业交易日计算规则
3. 优雅处理未知表达
4. 不中断用户体验
"""

import re
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any, Union
from dataclasses import dataclass
from enum import Enum

from database.mysql_connector import MySQLConnector
from utils.logger import setup_logger

logger = setup_logger("date_intelligence")

class TimeExpressionType(Enum):
    """时间表达类型"""
    CURRENT_POINT = "当前时间点"
    RELATIVE_POINT = "相对时间点"
    TIME_RANGE = "时间段"
    YEAR_RELATIVE = "年份相对"
    UNKNOWN = "未知表达"

@dataclass
class TimeExpression:
    """时间表达结构"""
    type: TimeExpressionType
    original_text: str
    start_pos: int
    end_pos: int
    value: Optional[Union[int, float]] = None
    unit: Optional[str] = None
    result_date: Optional[str] = None
    result_range: Optional[Tuple[str, str]] = None
    confidence: float = 1.0

@dataclass
class ParseResult:
    """解析结果"""
    success: bool
    original_question: str
    modified_question: str
    expressions: List[TimeExpression]
    suggestion: Optional[str] = None
    error: Optional[str] = None

class TradingDayCalculator:
    """交易日计算器"""
    
    # 交易日换算规则
    TRADING_DAYS_MAP = {
        "周": 5,
        "月": 21,
        "季": 61,
        "季度": 61,
        "半年": 120,
        "年": 250
    }
    
    def __init__(self, mysql_connector: MySQLConnector):
        self.mysql = mysql_connector
        self._trading_days_cache = {}
        self._cache_timestamp = {}
        
    def _get_cache_key(self, method: str, **kwargs) -> str:
        """生成缓存键"""
        key_parts = [method]
        for k, v in sorted(kwargs.items()):
            key_parts.append(f"{k}={v}")
        return "_".join(key_parts)
    
    def _is_cache_valid(self, cache_key: str, ttl: int = 3600) -> bool:
        """检查缓存是否有效"""
        if cache_key not in self._cache_timestamp:
            return False
        return time.time() - self._cache_timestamp[cache_key] < ttl
    
    def _set_cache(self, cache_key: str, data: Any):
        """设置缓存"""
        self._trading_days_cache[cache_key] = data
        self._cache_timestamp[cache_key] = time.time()
    
    def get_latest_trading_day(self) -> Optional[str]:
        """获取最新交易日"""
        cache_key = "latest_trading_day"
        if self._is_cache_valid(cache_key, ttl=1800):  # 30分钟缓存
            return self._trading_days_cache[cache_key]
        
        try:
            # 首先检查今天是否有交易数据
            today = datetime.now().strftime('%Y-%m-%d')
            query_today = """
            SELECT trade_date 
            FROM tu_daily_detail 
            WHERE trade_date = :today
            LIMIT 1
            """
            
            result_today = self.mysql.execute_query(query_today, {'today': today})
            
            if result_today and len(result_today) > 0:
                latest_date = str(result_today[0]['trade_date'])
                logger.info(f"找到今日交易数据: {latest_date}")
                self._set_cache(cache_key, latest_date)
                return latest_date
            else:
                # 今天没有数据，查找最新的交易日
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
            logger.error(f"获取最新交易日失败: {e}")
            return None
    
    def get_nth_trading_day_before(self, n: int, base_date: str = None) -> Optional[str]:
        """获取前第N个交易日"""
        if base_date is None:
            base_date = self.get_latest_trading_day()
        
        if base_date is None:
            return None
        
        cache_key = self._get_cache_key("nth_before", n=n, base=base_date)
        if self._is_cache_valid(cache_key):
            return self._trading_days_cache[cache_key]
        
        try:
            query = """
            SELECT trade_date 
            FROM tu_daily_detail 
            WHERE trade_date <= :base_date
            ORDER BY trade_date DESC 
            LIMIT :limit
            """
            
            result = self.mysql.execute_query(query, {'base_date': base_date, 'limit': n + 1})
            
            if result and len(result) > n:
                target_date = str(result[n]['trade_date'])
                self._set_cache(cache_key, target_date)
                return target_date
            
            return None
            
        except Exception as e:
            logger.error(f"获取前第{n}个交易日失败: {e}")
            return None
    
    def get_trading_days_range(self, days: int, end_date: str = None) -> Optional[Tuple[str, str]]:
        """获取最近N个交易日的范围"""
        if end_date is None:
            end_date = self.get_latest_trading_day()
        
        if end_date is None:
            return None
        
        cache_key = self._get_cache_key("range", days=days, end=end_date)
        if self._is_cache_valid(cache_key):
            return self._trading_days_cache[cache_key]
        
        try:
            query = """
            SELECT trade_date 
            FROM tu_daily_detail 
            WHERE trade_date <= :end_date
            ORDER BY trade_date DESC 
            LIMIT :limit
            """
            
            result = self.mysql.execute_query(query, {'end_date': end_date, 'limit': days})
            
            if result and len(result) > 0:
                start_date = str(result[-1]['trade_date'])  # 最早的日期
                end_date = str(result[0]['trade_date'])     # 最新的日期
                range_result = (start_date, end_date)
                self._set_cache(cache_key, range_result)
                return range_result
            
            return None
            
        except Exception as e:
            logger.error(f"获取{days}个交易日范围失败: {e}")
            return None
    
    def get_year_relative_date(self, years_offset: int, base_date: str = None) -> Optional[str]:
        """获取年份相对日期"""
        if base_date is None:
            base_date = self.get_latest_trading_day()
        
        if base_date is None:
            return None
        
        try:
            # 解析基准日期
            base_dt = datetime.strptime(base_date, '%Y-%m-%d')
            # 计算目标年份
            target_year = base_dt.year + years_offset
            target_dt = base_dt.replace(year=target_year)
            target_date = target_dt.strftime('%Y-%m-%d')
            
            # 检查目标日期是否为交易日
            query = """
            SELECT trade_date 
            FROM tu_daily_detail 
            WHERE trade_date = :target_date
            LIMIT 1
            """
            
            result = self.mysql.execute_query(query, {'target_date': target_date})
            
            if result and len(result) > 0:
                # 目标日期是交易日
                return target_date
            else:
                # 目标日期不是交易日，向前查找最近的交易日
                query_before = """
                SELECT trade_date 
                FROM tu_daily_detail 
                WHERE trade_date < :target_date
                ORDER BY trade_date DESC 
                LIMIT 1
                """
                
                result_before = self.mysql.execute_query(query_before, {'target_date': target_date})
                
                if result_before and len(result_before) > 0:
                    adjusted_date = str(result_before[0]['trade_date'])
                    logger.info(f"年份相对日期{target_date}非交易日，调整为{adjusted_date}")
                    return adjusted_date
                
                return None
            
        except Exception as e:
            logger.error(f"获取年份相对日期失败: {e}")
            return None

class ChineseTimeParser:
    """中文时间表达解析器"""
    
    # 中文数字映射
    CHINESE_NUMBERS = {
        "一": 1, "二": 2, "三": 3, "四": 4, "五": 5,
        "六": 6, "七": 7, "八": 8, "九": 9, "十": 10,
        "十一": 11, "十二": 12, "十五": 15, "二十": 20,
        "三十": 30, "半": 0.5, "俩": 2, "仨": 3
    }
    
    # 时间表达模式
    TIME_PATTERNS = {
        # 当前时间点
        'current_point': [
            "最新", "今天", "今日", "现在", "当前", "目前", "本交易日"
        ],
        
        # 相对时间点 - 上一个周期
        'previous_cycle': {
            "上一个交易日": 1,
            "昨天": 1,
            "前天": 2,
            "大前天": 3,
            "上周": 5,
            "上个月": 21,
            "上月": 21,
            "上个季度": 61,
            "上季": 61,
        },
        
        # 相对时间点 - N个单位前
        'n_units_ago': [
            (r'(\d+)天前', 'days'),
            (r'(\d+)个?交易日前', 'days'),
            (r'(\d+)周前', 'weeks'),
            (r'(\d+)个?月前', 'months'),
            (r'(\d+)个?季度?前', 'quarters'),
            (r'半年前', 'half_year'),
            (r'一年前', 'year'),
            (r'([一二三四五六七八九十]+)天前', 'chinese_days'),
            (r'([一二三四五六七八九十]+)个?月前', 'chinese_months'),
        ],
        
        # 时间段 - 最近N个周期
        'recent_range': [
            (r'最近(\d+)天', 'days'),
            (r'最近(\d+)个?交易日', 'days'),
            (r'最近(\d+)周', 'weeks'),
            (r'最近(\d+)个?月', 'months'),
            (r'最近(\d+)个?季度?', 'quarters'),
            (r'最近([一二三四五六七八九十]+)天', 'chinese_days'),
            (r'最近([一二三四五六七八九十]+)个?月', 'chinese_months'),
            (r'最近一周', 'one_week'),
            (r'最近一个月', 'one_month'),
            (r'最近一个季度', 'one_quarter'),
            (r'最近半年', 'half_year'),
            (r'最近一年', 'one_year'),
        ],
        
        # 时间段 - 前N个周期
        'past_range': [
            (r'前(\d+)天', 'days'),
            (r'前(\d+)个?交易日', 'days'),
            (r'前(\d+)周', 'weeks'),
            (r'前(\d+)个?月', 'months'),
            (r'前(\d+)个?季度?', 'quarters'),
            (r'过去(\d+)天', 'days'),
            (r'过去(\d+)周', 'weeks'),
            (r'过去(\d+)个?月', 'months'),
        ],
        
        # 年份相对
        'year_relative': {
            "去年": -1,
            "前年": -2,
            "上上年": -2,
            "去年同期": -1,
            "上年同期": -1,
        }
    }
    
    def __init__(self):
        pass
    
    def chinese_to_number(self, chinese_str: str) -> int:
        """中文数字转阿拉伯数字"""
        if chinese_str in self.CHINESE_NUMBERS:
            return self.CHINESE_NUMBERS[chinese_str]
        
        # 处理复合中文数字（如"十五"、"二十"等）
        if "十" in chinese_str:
            if chinese_str == "十":
                return 10
            elif chinese_str.startswith("十"):
                return 10 + self.CHINESE_NUMBERS.get(chinese_str[1:], 0)
            elif chinese_str.endswith("十"):
                return self.CHINESE_NUMBERS.get(chinese_str[0], 0) * 10
            else:
                parts = chinese_str.split("十")
                return self.CHINESE_NUMBERS.get(parts[0], 0) * 10 + self.CHINESE_NUMBERS.get(parts[1], 0)
        
        return 1  # 默认值
    
    def parse_time_expressions(self, text: str) -> List[TimeExpression]:
        """解析文本中的所有时间表达"""
        expressions = []
        
        # 1. 检查当前时间点
        for pattern in self.TIME_PATTERNS['current_point']:
            for match in re.finditer(re.escape(pattern), text):
                expr = TimeExpression(
                    type=TimeExpressionType.CURRENT_POINT,
                    original_text=pattern,
                    start_pos=match.start(),
                    end_pos=match.end()
                )
                expressions.append(expr)
        
        # 2. 检查上一个周期
        for pattern, days in self.TIME_PATTERNS['previous_cycle'].items():
            for match in re.finditer(re.escape(pattern), text):
                expr = TimeExpression(
                    type=TimeExpressionType.RELATIVE_POINT,
                    original_text=pattern,
                    start_pos=match.start(),
                    end_pos=match.end(),
                    value=days,
                    unit='days'
                )
                expressions.append(expr)
        
        # 3. 检查N个单位前
        for pattern, unit in self.TIME_PATTERNS['n_units_ago']:
            for match in re.finditer(pattern, text):
                if unit == 'chinese_days':
                    value = self.chinese_to_number(match.group(1))
                elif unit == 'chinese_months':
                    value = self.chinese_to_number(match.group(1)) * 21
                elif unit == 'days':
                    value = int(match.group(1))
                elif unit == 'weeks':
                    value = int(match.group(1)) * 5
                elif unit == 'months':
                    value = int(match.group(1)) * 21
                elif unit == 'quarters':
                    value = int(match.group(1)) * 61
                elif unit == 'half_year':
                    value = 120
                elif unit == 'year':
                    value = 250
                else:
                    value = 1
                
                expr = TimeExpression(
                    type=TimeExpressionType.RELATIVE_POINT,
                    original_text=match.group(0),
                    start_pos=match.start(),
                    end_pos=match.end(),
                    value=value,
                    unit='days'
                )
                expressions.append(expr)
        
        # 4. 检查最近范围
        for pattern, unit in self.TIME_PATTERNS['recent_range']:
            for match in re.finditer(pattern, text):
                if unit == 'chinese_days':
                    value = self.chinese_to_number(match.group(1))
                elif unit == 'chinese_months':
                    value = self.chinese_to_number(match.group(1)) * 21
                elif unit == 'days':
                    value = int(match.group(1))
                elif unit == 'weeks':
                    value = int(match.group(1)) * 5
                elif unit == 'months':
                    value = int(match.group(1)) * 21
                elif unit == 'quarters':
                    value = int(match.group(1)) * 61
                elif unit == 'one_week':
                    value = 5
                elif unit == 'one_month':
                    value = 21
                elif unit == 'one_quarter':
                    value = 61
                elif unit == 'half_year':
                    value = 120
                elif unit == 'one_year':
                    value = 250
                else:
                    value = 1
                
                expr = TimeExpression(
                    type=TimeExpressionType.TIME_RANGE,
                    original_text=match.group(0),
                    start_pos=match.start(),
                    end_pos=match.end(),
                    value=value,
                    unit='days'
                )
                expressions.append(expr)
        
        # 5. 检查过去范围
        for pattern, unit in self.TIME_PATTERNS['past_range']:
            for match in re.finditer(pattern, text):
                if unit == 'days':
                    value = int(match.group(1))
                elif unit == 'weeks':
                    value = int(match.group(1)) * 5
                elif unit == 'months':
                    value = int(match.group(1)) * 21
                elif unit == 'quarters':
                    value = int(match.group(1)) * 61
                else:
                    value = 1
                
                expr = TimeExpression(
                    type=TimeExpressionType.TIME_RANGE,
                    original_text=match.group(0),
                    start_pos=match.start(),
                    end_pos=match.end(),
                    value=value,
                    unit='days'
                )
                expressions.append(expr)
        
        # 6. 检查年份相对
        for pattern, offset in self.TIME_PATTERNS['year_relative'].items():
            for match in re.finditer(re.escape(pattern), text):
                expr = TimeExpression(
                    type=TimeExpressionType.YEAR_RELATIVE,
                    original_text=pattern,
                    start_pos=match.start(),
                    end_pos=match.end(),
                    value=offset,
                    unit='years'
                )
                expressions.append(expr)
        
        # 按位置排序
        expressions.sort(key=lambda x: x.start_pos)
        
        return expressions

class DateIntelligenceModule:
    """智能日期解析模块 v2.0"""
    
    def __init__(self):
        self.mysql = MySQLConnector()
        self.calculator = TradingDayCalculator(self.mysql)
        self.parser = ChineseTimeParser()
        self._global_cache = {}
        self._cache_timestamp = {}
        self._cache_ttl = 3600  # 1小时缓存
    
    def clear_cache(self, pattern: Optional[str] = None):
        """清理缓存"""
        if pattern is None:
            self._global_cache.clear()
            self._cache_timestamp.clear()
            logger.info("已清理所有日期智能解析缓存")
        else:
            keys_to_remove = []
            for key in self._global_cache.keys():
                if pattern in key:
                    keys_to_remove.append(key)
            
            for key in keys_to_remove:
                self._global_cache.pop(key, None)
                self._cache_timestamp.pop(key, None)
            
            logger.info(f"已清理匹配'{pattern}'的缓存，共{len(keys_to_remove)}条")
    
    def calculate_expression_result(self, expr: TimeExpression) -> TimeExpression:
        """计算时间表达的具体结果"""
        try:
            if expr.type == TimeExpressionType.CURRENT_POINT:
                # 当前时间点
                result_date = self.calculator.get_latest_trading_day()
                expr.result_date = result_date
                
            elif expr.type == TimeExpressionType.RELATIVE_POINT:
                # 相对时间点
                if expr.value and expr.unit == 'days':
                    result_date = self.calculator.get_nth_trading_day_before(expr.value)
                    expr.result_date = result_date
                    
            elif expr.type == TimeExpressionType.TIME_RANGE:
                # 时间段
                if expr.value and expr.unit == 'days':
                    result_range = self.calculator.get_trading_days_range(expr.value)
                    expr.result_range = result_range
                    
            elif expr.type == TimeExpressionType.YEAR_RELATIVE:
                # 年份相对
                if expr.value and expr.unit == 'years':
                    result_date = self.calculator.get_year_relative_date(expr.value)
                    expr.result_date = result_date
            
            return expr
            
        except Exception as e:
            logger.error(f"计算时间表达结果失败: {e}")
            expr.confidence = 0.0
            return expr
    
    def generate_replacement_text(self, expr: TimeExpression) -> str:
        """生成替换文本"""
        if expr.type in [TimeExpressionType.CURRENT_POINT, 
                        TimeExpressionType.RELATIVE_POINT, 
                        TimeExpressionType.YEAR_RELATIVE]:
            # 时间点 → 单一日期
            if expr.result_date:
                return expr.result_date
        
        elif expr.type == TimeExpressionType.TIME_RANGE:
            # 时间段 → 日期范围
            if expr.result_range:
                start_date, end_date = expr.result_range
                return f"{start_date}至{end_date}"
        
        # 如果没有结果，返回原文
        return expr.original_text
    
    def replace_expressions_in_text(self, text: str, expressions: List[TimeExpression]) -> str:
        """在文本中替换时间表达"""
        # 从后往前替换，避免位置偏移
        for expr in sorted(expressions, key=lambda x: x.start_pos, reverse=True):
            if expr.confidence > 0.5:  # 只替换高置信度的表达
                replacement = self.generate_replacement_text(expr)
                text = text[:expr.start_pos] + replacement + text[expr.end_pos:]
        
        return text
    
    def intelligent_date_parsing(self, question: str) -> ParseResult:
        """智能日期解析主函数"""
        try:
            # 1. 解析时间表达
            expressions = self.parser.parse_time_expressions(question)
            
            if not expressions:
                return ParseResult(
                    success=True,
                    original_question=question,
                    modified_question=question,
                    expressions=[]
                )
            
            # 2. 计算每个表达的结果
            for i, expr in enumerate(expressions):
                expressions[i] = self.calculate_expression_result(expr)
            
            # 3. 替换文本中的表达
            modified_question = self.replace_expressions_in_text(question, expressions)
            
            # 4. 记录日志
            for expr in expressions:
                if expr.confidence > 0.5:
                    if expr.result_date:
                        logger.info(f"日期智能解析: '{question}' -> '{modified_question}'")
                        logger.info(f"解析详情: 将'{expr.original_text}'解析为{expr.type.value}: {expr.result_date}")
                    elif expr.result_range:
                        logger.info(f"日期智能解析: '{question}' -> '{modified_question}'")
                        logger.info(f"解析详情: 将'{expr.original_text}'解析为{expr.type.value}: {expr.result_range[0]}至{expr.result_range[1]}")
            
            return ParseResult(
                success=True,
                original_question=question,
                modified_question=modified_question,
                expressions=expressions
            )
            
        except Exception as e:
            logger.error(f"智能日期解析失败: {e}")
            return ParseResult(
                success=False,
                original_question=question,
                modified_question=question,
                expressions=[],
                error=str(e)
            )
    
    def preprocess_question(self, question: str) -> Tuple[str, Dict[str, Any]]:
        """
        预处理问题，将时间表达转换为具体日期
        
        Args:
            question: 原始问题
            
        Returns:
            (处理后的问题, 解析结果)
        """
        parsing_result = self.intelligent_date_parsing(question)
        
        if parsing_result.success and parsing_result.modified_question != question:
            processed_question = parsing_result.modified_question
        else:
            processed_question = question
        
        # 转换为兼容的字典格式
        result_dict = {
            'success': parsing_result.success,
            'original_question': parsing_result.original_question,
            'modified_question': parsing_result.modified_question,
            'expressions_count': len(parsing_result.expressions),
            'suggestion': parsing_result.suggestion,
            'error': parsing_result.error
        }
        
        return processed_question, result_dict

# 全局实例
date_intelligence = DateIntelligenceModule()

# 清理缓存以确保新逻辑生效
date_intelligence.clear_cache()

# 兼容性函数（保持向后兼容）
def get_latest_trading_day() -> Optional[str]:
    """获取最新交易日（兼容函数）"""
    return date_intelligence.calculator.get_latest_trading_day()