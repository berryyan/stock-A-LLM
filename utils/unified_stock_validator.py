#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
统一股票验证器 - 基于Financial Agent的优秀验证逻辑
从Financial Agent提取的股票代码验证和错误处理系统
支持大小写智能提示和精确错误分类
"""

import re
import sys
import os
import logging
from typing import Optional, Tuple, Dict, Any, List

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.stock_code_mapper import convert_to_ts_code, get_stock_mapper
from utils.logger import setup_logger


class UnifiedStockValidator:
    """统一股票验证器 - 支持大小写智能提示"""
    
    def __init__(self):
        self.logger = setup_logger("unified_stock_validator")
        
        # 常见简称映射
        self.common_short_names = {
            '茅台': '贵州茅台',
            '平安': '中国平安',
            '万科': '万科企业',
            '格力': '格力电器',
            '美的': '美的集团',
            '比亚迪': '比亚迪',
            '五粮液': '五粮液',
            '泸州老窖': '泸州老窖',
            '建行': '建设银行',
            '工行': '工商银行',
            '农行': '农业银行',
            '中行': '中国银行',
            '招行': '招商银行',
            '中石油': '中国石油',
            '中石化': '中国石化',
            '中国移动': '中国移动',
            '中国联通': '中国联通',
            '中国电信': '中国电信',
        }
        
        # 查询模式（用于意图识别）
        self.query_patterns = {
            'financial_health': ['财务健康', '财务状况', '经营状况', '财务评级', '健康度'],
            'profitability': ['盈利能力', '赚钱能力', 'ROE', 'ROA', '净利率', '毛利率'],
            'solvency': ['偿债能力', '负债率', '流动比率', '资产负债率', '偿债'],
            'growth': ['成长性', '增长率', '营收增长', '利润增长', '发展速度'],
            'cash_flow': ['现金流', '现金流量', '经营现金流', '现金质量'],
            'dupont': ['杜邦分析', 'ROE分解', '杜邦', '盈利能力分解'],
            'comparison': ['对比', '比较', '同行', '行业对比', '历史对比', '多期', '财务变化', '财务对比'],
            'money_flow': ['资金流向', '资金流入', '资金流出', '主力资金', '机构资金', '大资金'],
            'comprehensive': ['分析', '查询', '怎么样', '如何']
        }
    
    def _check_case_sensitive_suffix(self, suffix: str) -> Optional[str]:
        """
        检查大小写错误的后缀，返回正确的大写格式
        
        Args:
            suffix: 输入的后缀
            
        Returns:
            如果是大小写错误返回正确格式，否则返回None
        """
        # 将后缀转换为大写进行比较
        upper_suffix = suffix.upper()
        
        # 检查是否是正确后缀的大小写变体
        if upper_suffix in ['SZ', 'SH', 'BJ'] and suffix != upper_suffix:
            return f".{upper_suffix}"
        
        return None
    
    def parse_query_intent_and_extract_stock(self, question: str) -> Tuple[str, Optional[str], Optional[str]]:
        """
        解析查询意图和股票代码 - V3版本
        
        Returns:
            Tuple[intent, ts_code_or_error_code, error_detail]
            - intent: 查询意图类型
            - ts_code_or_error_code: 成功时返回ts_code，失败时返回错误代码
            - error_detail: 错误详情（如具体的后缀、位数等）
        """
        
        # 1. 检查疑似ts_code格式（优先级最高）
        # 匹配 "数字." 或 "数字.任意字符" 的格式
        suspect_ts_pattern = r'(\d+)\.([A-Za-z]*)'
        suspect_match = re.search(suspect_ts_pattern, question)
        if suspect_match:
            number_part = suspect_match.group(1)
            suffix_part = suspect_match.group(2) if suspect_match.group(2) else ''
            
            # 检查数字部分长度
            if len(number_part) != 6:
                self.logger.warning(f"股票代码长度不正确: {number_part} (应为6位)")
                intent = self._determine_intent(question)
                return intent, 'INVALID_LENGTH', str(len(number_part))
            
            # 检查后缀
            if not suffix_part:
                self.logger.warning(f"证券代码缺少后缀: {number_part}.")
                intent = self._determine_intent(question)
                return intent, 'INVALID_FORMAT', '缺少后缀'
            
            # 检查是否是大小写错误
            correct_suffix = self._check_case_sensitive_suffix(suffix_part)
            if correct_suffix:
                self.logger.warning(f"证券代码后缀大小写错误: {suffix_part}")
                intent = self._determine_intent(question)
                return intent, 'INVALID_CASE', correct_suffix
            
            # 检查是否是完全错误的后缀
            if suffix_part not in ['SZ', 'SH', 'BJ']:
                self.logger.warning(f"证券代码后缀错误: {suffix_part}")
                intent = self._determine_intent(question)
                return intent, 'INVALID_FORMAT', f"后缀'{suffix_part}'"
            
            # 格式正确，检查是否存在
            full_ts_code = f"{number_part}.{suffix_part}"
            if not self._verify_stock_exists(full_ts_code):
                self.logger.warning(f"股票代码不存在: {full_ts_code}")
                intent = self._determine_intent(question)
                return intent, 'STOCK_NOT_EXISTS', full_ts_code
            
            # 成功
            intent = self._determine_intent(question)
            return intent, full_ts_code, None
        
        # 2. 尝试提取完整的ts_code格式 (如 600519.SH)
        ts_code_pattern = r'(\d{6}\.(SZ|SH|BJ))(?=\s|$|[^A-Z])'
        ts_code_match = re.search(ts_code_pattern, question)
        if ts_code_match:
            extracted_ts_code = ts_code_match.group(0)
            self.logger.info(f"从查询中提取到ts_code: {extracted_ts_code}")
            
            # 验证是否存在
            if not self._verify_stock_exists(extracted_ts_code):
                self.logger.warning(f"股票代码不存在: {extracted_ts_code}")
                intent = self._determine_intent(question)
                return intent, 'STOCK_NOT_EXISTS', extracted_ts_code
            
            intent = self._determine_intent(question)
            return intent, extracted_ts_code, None
        
        # 3. 尝试提取纯数字股票代码
        number_pattern = r'(?:^|[\s\u4e00-\u9fa5])(\d+)(?:[\s\u4e00-\u9fa5]|$)'
        numbers = re.findall(number_pattern, question)
        for number in numbers:
            if len(number) == 6:
                # 使用股票代码映射器转换
                extracted_ts_code = convert_to_ts_code(number)
                if extracted_ts_code:
                    self.logger.info(f"从查询中提取到股票代码 {number}，转换为: {extracted_ts_code}")
                    intent = self._determine_intent(question)
                    return intent, extracted_ts_code, None
            elif len(number) >= 3:  # 可能是错误的股票代码
                self.logger.warning(f"股票代码长度不正确: {number} (应为6位)")
                intent = self._determine_intent(question)
                return intent, 'INVALID_LENGTH', str(len(number))
        
        # 4. 尝试通过股票名称查找（包括简称处理）
        extracted_info = self._extract_stock_by_name_enhanced(question)
        if extracted_info:
            ts_code, suggestion = extracted_info
            if ts_code:
                self.logger.info(f"从查询中提取到股票: {ts_code}")
                intent = self._determine_intent(question)
                return intent, ts_code, None
            elif suggestion:
                # 找到了简称但需要使用完整名称
                self.logger.warning(f"发现简称，建议使用: {suggestion}")
                intent = self._determine_intent(question)
                return intent, 'USE_FULL_NAME', suggestion
        
        # 5. 未找到任何股票信息
        intent = self._determine_intent(question)
        return intent, 'NOT_FOUND', None
    
    def _determine_intent(self, question: str) -> str:
        """确定查询意图"""
        for pattern_type, patterns in self.query_patterns.items():
            if any(pattern in question for pattern in patterns):
                return pattern_type
        return 'comprehensive'
    
    def _verify_stock_exists(self, ts_code: str) -> bool:
        """验证股票代码是否真实存在"""
        try:
            mapper = get_stock_mapper()
            stock_name = mapper.get_stock_name(ts_code)
            return stock_name is not None and stock_name != ts_code
        except Exception as e:
            self.logger.error(f"验证股票代码存在性失败: {e}")
            return True  # 出错时默认认为存在
    
    def _extract_stock_by_name_enhanced(self, question: str) -> Optional[Tuple[Optional[str], Optional[str]]]:
        """
        增强版股票名称提取
        
        Returns:
            Tuple[ts_code, suggestion] 或 None
            - ts_code: 成功找到的股票代码
            - suggestion: 建议使用的完整名称（当发现简称时）
        """
        try:
            # 首先检查常见简称
            for short_name, full_name in self.common_short_names.items():
                if short_name in question:
                    # 尝试用完整名称查找
                    ts_code = convert_to_ts_code(full_name)
                    if ts_code:
                        # 检查用户是否已经使用了完整名称
                        if full_name in question:
                            return (ts_code, None)
                        else:
                            # 用户使用了简称，返回建议
                            return (None, full_name)
            
            # 提取可能的公司名称
            name_patterns = [
                # 支持两字公司名（通过特定上下文）
                r'([一-龥]{2})(?:财务|股价|分析|的|资金|年报|公告)',
                # 带后缀的公司名
                r'([一-龥]{2,6}(?:股份|集团|银行|科技|电子|医药|能源|地产|证券|保险|汽车|新材料|新能源))',
                # "分析XX的"模式
                r'分析([一-龥]{2,6})的',
                # 一般的2-6字中文
                r'([一-龥]{2,6})(?=财务|分析|怎么样|如何|资金流向|最新股价|股价|年报|公告)',
            ]
            
            potential_names = []
            for pattern in name_patterns:
                matches = re.findall(pattern, question)
                potential_names.extend(matches)
            
            # 去重并尝试转换
            seen = set()
            for name in potential_names:
                if name not in seen:
                    seen.add(name)
                    ts_code = convert_to_ts_code(name)
                    if ts_code:
                        self.logger.info(f"从查询中提取到股票名称 '{name}'，转换为: {ts_code}")
                        return (ts_code, None)
            
            # 清理查询词后重试
            clean_question = question
            for word in ['分析', '查询', '的', '财务', '健康度', '状况', '怎么样', '如何', 
                        '资金流向', '最新股价', '股价', '年报', '公告', '和', '对比', '比较']:
                clean_question = clean_question.replace(word, ' ')
            
            # 提取剩余的主要词汇
            words = [w.strip() for w in clean_question.split() if len(w.strip()) >= 2]
            for word in words:
                if word.isdigit():
                    continue
                if re.match(r'\d{6}\.[A-Z]+', word):
                    continue
                    
                ts_code = convert_to_ts_code(word)
                if ts_code:
                    self.logger.info(f"从查询词 '{word}' 转换为: {ts_code}")
                    return (ts_code, None)
            
            return None
            
        except Exception as e:
            self.logger.error(f"股票名称提取失败: {e}")
            return None
    
    def format_error_response(self, error_type: str, error_detail: str = None) -> Dict[str, Any]:
        """
        格式化错误响应 - V3版本，支持大小写错误提示
        """
        if error_type == 'INVALID_FORMAT':
            if error_detail == '缺少后缀':
                error_message = '证券代码格式错误：缺少后缀，应添加.SZ/.SH/.BJ'
            else:
                error_message = f'证券代码格式错误：{error_detail}不正确，应为.SZ/.SH/.BJ'
        
        elif error_type == 'INVALID_CASE':
            # error_detail 包含正确的大写格式，如 ".SH"
            error_message = f'证券代码后缀大小写错误，应为{error_detail}'
        
        elif error_type == 'INVALID_LENGTH':
            error_message = f'股票代码应为6位数字，您输入了{error_detail}位'
        
        elif error_type == 'STOCK_NOT_EXISTS':
            error_message = f'股票代码{error_detail}不存在，请检查是否输入正确'
        
        elif error_type == 'USE_FULL_NAME':
            error_message = f'请使用完整公司名称，如：{error_detail}'
        
        elif error_type == 'NOT_FOUND':
            error_message = '无法识别输入内容。请输入：1) 6位股票代码（如002047）2) 证券代码（如600519.SH）3) 股票名称（如贵州茅台）'
        
        elif error_type == 'EMPTY_INPUT':
            error_message = '查询内容不能为空'
        
        else:
            error_message = '未知错误'
        
        return {
            'success': False,
            'error': error_message,
            'error_type': error_type,
            'answer': None
        }
    
    def validate_and_extract(self, question: str) -> Tuple[bool, Optional[str], Dict[str, Any]]:
        """
        验证并提取股票信息的完整流程
        """
        # 输入验证
        if not question or not question.strip():
            error_response = self.format_error_response('EMPTY_INPUT')
            return False, None, error_response
        
        # 解析意图和提取股票代码
        intent, ts_code_or_error, error_detail = self.parse_query_intent_and_extract_stock(question)
        
        # 处理错误情况
        if ts_code_or_error in ['INVALID_FORMAT', 'INVALID_CASE', 'INVALID_LENGTH', 'STOCK_NOT_EXISTS', 'USE_FULL_NAME', 'NOT_FOUND']:
            error_response = self.format_error_response(ts_code_or_error, error_detail)
            return False, None, error_response
        
        # 成功提取
        self.logger.info(f"成功提取股票代码: {ts_code_or_error}, 查询意图: {intent}")
        return True, ts_code_or_error, {}
    
    def extract_multiple_stocks(self, question: str) -> List[str]:
        """
        提取多个股票代码（用于复合查询）
        """
        stocks = []
        
        # 分割可能的连接词
        parts = re.split(r'[和与及、，,]', question)
        
        for part in parts:
            success, ts_code, _ = self.validate_and_extract(part.strip())
            if success and ts_code:
                stocks.append(ts_code)
        
        return stocks


# 创建全局实例
unified_validator = UnifiedStockValidator()


def validate_stock_input(question: str) -> Tuple[bool, Optional[str], Dict[str, Any]]:
    """便捷函数：验证并提取股票信息"""
    return unified_validator.validate_and_extract(question)


def extract_stock_with_intent(question: str) -> Tuple[str, Optional[str]]:
    """便捷函数：提取股票代码和查询意图"""
    return unified_validator.parse_query_intent_and_extract_stock(question)


# 测试函数
if __name__ == "__main__":
    validator = UnifiedStockValidator()
    
    # 测试用例
    test_cases = [
        # 大小写错误测试
        "600519.sh",
        "600519.sH", 
        "600519.Sh",
        "600519.sz",
        "600519.Sz",
        "600519.sZ",
        "600519.bj",
        "600519.Bj",
        "600519.bJ",
        
        # 其他错误后缀
        "600519.SX",
        "600519.ABC",
        "600519.",
        
        # 正确格式
        "600519.SH",
        "000002.SZ",
        "831726.BJ",
    ]
    
    print("测试统一验证器的功能：")
    print("=" * 80)
    
    for test_case in test_cases:
        print(f"\n测试: {test_case}")
        success, ts_code, error_response = validator.validate_and_extract(test_case)
        
        if success:
            print(f"  ✅ 成功: {ts_code}")
        else:
            print(f"  ❌ 失败: {error_response['error']}")