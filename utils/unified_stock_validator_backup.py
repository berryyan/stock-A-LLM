#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
统一股票验证器 - 基于Financial Agent的优秀验证逻辑
从Financial Agent提取的股票代码验证和错误处理系统
"""

import re
import sys
import os
import logging
from typing import Optional, Tuple, Dict, Any

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.stock_code_mapper import convert_to_ts_code
from utils.logger import setup_logger


class UnifiedStockValidator:
    """统一股票验证器 - 基于Financial Agent的验证逻辑"""
    
    def __init__(self):
        self.logger = setup_logger("unified_stock_validator")
        
        # Financial Agent的查询模式（用于意图识别）
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
    
    def parse_query_intent_and_extract_stock(self, question: str) -> Tuple[str, Optional[str]]:
        """
        解析查询意图和股票代码 - 基于Financial Agent的逻辑
        
        Returns:
            Tuple[intent, ts_code_or_error_code]
            - intent: 查询意图类型
            - ts_code_or_error_code: 
                - 成功时返回ts_code (如"600519.SH") 
                - 失败时返回错误代码 ("INVALID_FORMAT", "INVALID_LENGTH", None)
        """
        
        # 1. 首先尝试提取完整的ts_code格式 (如 600519.SH)
        # 使用更严格的边界匹配，避免匹配到831726.BJJ中的831726.BJ
        ts_code_pattern = r'(\d{6}\.(SZ|SH|BJ))(?=\s|$|[^A-Z])'
        ts_code_match = re.search(ts_code_pattern, question)
        if ts_code_match:
            extracted_ts_code = ts_code_match.group(0)  # 直接使用完整匹配
            self.logger.info(f"从查询中提取到ts_code: {extracted_ts_code}")
            # 验证ts_code格式
            if not self._validate_ts_code(extracted_ts_code):
                self.logger.warning(f"证券代码格式不正确: {extracted_ts_code}")
                # 先确定intent再返回
                intent = self._determine_intent(question)
                return intent, 'INVALID_FORMAT'
            # 验证股票代码是否真实存在
            if not self._verify_stock_exists(extracted_ts_code):
                self.logger.warning(f"股票代码不存在: {extracted_ts_code}")
                intent = self._determine_intent(question)
                return intent, None  # 返回None表示未找到
        else:
            extracted_ts_code = None
        
        # 2. 如果没有找到完整格式，尝试提取纯数字股票代码
        if not extracted_ts_code:
            # 更严格的数字提取，避免提取到其他数字
            number_pattern = r'(?:^|[\s\u4e00-\u9fa5])(\d+)(?:[\s\u4e00-\u9fa5]|$)'
            numbers = re.findall(number_pattern, question)
            for number in numbers:
                if len(number) == 6:  # 只接受6位数字
                    # 使用股票代码映射器转换
                    extracted_ts_code = convert_to_ts_code(number)
                    if extracted_ts_code:
                        self.logger.info(f"从查询中提取到股票代码 {number}，转换为: {extracted_ts_code}")
                        break
                elif len(number) != 6 and len(number) >= 3:  # 可能是错误的股票代码
                    self.logger.warning(f"股票代码长度不正确: {number} (应为6位)")
                    # 先确定intent再返回
                    intent = self._determine_intent(question)
                    return intent, 'INVALID_LENGTH'
        
        # 3. 如果还没有找到，尝试通过股票名称查找
        if not extracted_ts_code:
            # 使用更智能的名称提取逻辑
            extracted_ts_code = self._extract_stock_by_name(question)
            
        # 4. 验证提取到的ts_code格式
        if extracted_ts_code and not self._validate_ts_code(extracted_ts_code):
            self.logger.warning(f"证券代码格式不正确: {extracted_ts_code}")
            # 先确定intent再返回
            intent = self._determine_intent(question)
            return intent, 'INVALID_FORMAT'
        
        # 匹配查询意图
        intent = self._determine_intent(question)
        
        return intent, extracted_ts_code
    
    def _determine_intent(self, question: str) -> str:
        """确定查询意图"""
        for pattern_type, patterns in self.query_patterns.items():
            if any(pattern in question for pattern in patterns):
                return pattern_type
        return 'comprehensive'  # 默认意图
    
    def _validate_ts_code(self, ts_code: str) -> bool:
        """验证证券代码格式是否正确"""
        # 验证格式：6位数字.SZ/SH/BJ
        pattern = r'^\d{6}\.(SZ|SH|BJ)$'
        return bool(re.match(pattern, ts_code))
    
    def _verify_stock_exists(self, ts_code: str) -> bool:
        """验证股票代码是否真实存在"""
        try:
            # 使用stock_code_mapper的反向查找功能
            from utils.stock_code_mapper import get_stock_mapper
            mapper = get_stock_mapper()
            # 尝试获取股票名称，如果不存在会返回原始ts_code
            stock_name = mapper.get_stock_name(ts_code)
            # 如果返回的名称就是ts_code本身，说明没找到
            return stock_name is not None and stock_name != ts_code
        except Exception as e:
            self.logger.error(f"验证股票代码存在性失败: {e}")
            # 出错时默认认为存在，避免误判
            return True
    
    def _extract_stock_by_name(self, question: str) -> Optional[str]:
        """通过股票名称查找TS代码 - 基于Financial Agent的逻辑"""
        try:
            # 常见的股票名称模式
            # 1. 先尝试提取可能的公司名称（2-6个中文字符）
            name_patterns = [
                r'([一-龥]{2,6}(?:股份|集团|银行|科技|电子|医药|能源|地产|证券|保险|汽车|新材料|新能源))',
                r'([一-龥]{2,6}[A-Z]?(?=的|财务|分析|怎么样|如何))',  # 如 "万科A的财务"
                r'分析([一-龥]{2,6})的',  # 如 "分析茅台的"
                r'([一-龥]{2,4})(?:股价|财务|业绩|年报|公告)'  # 如 "茅台股价"
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
                        return ts_code
            
            # 如果没有找到，尝试整个问题作为输入
            # 去除一些常见的查询词
            clean_question = question
            for word in ['分析', '查询', '的', '财务', '健康度', '状况', '怎么样', '如何', '资金流向', '最新股价', '股价', '年报', '公告']:
                clean_question = clean_question.replace(word, ' ')
            
            # 提取剩余的主要词汇
            words = [w.strip() for w in clean_question.split() if len(w.strip()) >= 2]
            for word in words:
                # 跳过纯数字，因为已经在前面处理过了
                if word.isdigit():
                    continue
                # 跳过看起来像ts_code但格式不对的（如831726.BJJ）
                if re.match(r'\d{6}\.[A-Z]+', word) and not self._validate_ts_code(word):
                    continue
                ts_code = convert_to_ts_code(word)
                if ts_code:
                    self.logger.info(f"从查询词 '{word}' 转换为: {ts_code}")
                    return ts_code
            
            # 如果尝试了但没找到，记录尝试的名称
            if words:
                self.logger.warning(f"未找到股票名称匹配: {', '.join(words)}")
            
            return None
            
        except Exception as e:
            self.logger.error(f"股票名称提取失败: {e}")
            return None
    
    def format_error_response(self, error_type: str, custom_message: str = None) -> Dict[str, Any]:
        """
        格式化错误响应 - 基于Financial Agent的错误处理逻辑
        
        Args:
            error_type: 错误类型 ('INVALID_FORMAT', 'INVALID_LENGTH', 'NOT_FOUND', 'EMPTY_INPUT')
            custom_message: 自定义错误消息
        """
        if error_type == 'INVALID_FORMAT':
            error_message = custom_message or '证券代码格式不正确，后缀应为.SZ/.SH/.BJ'
        elif error_type == 'INVALID_LENGTH':
            error_message = custom_message or '股票代码格式不正确，请输入6位数字'
        elif error_type == 'NOT_FOUND':
            error_message = custom_message or '无法识别输入内容。请输入：1) 6位股票代码（如002047）2) 证券代码（如600519.SH）3) 股票名称（如贵州茅台）'
        elif error_type == 'EMPTY_INPUT':
            error_message = custom_message or '查询内容不能为空'
        else:
            error_message = custom_message or '未知错误'
        
        return {
            'success': False,
            'error': error_message,
            'error_type': error_type,
            'answer': None
        }
    
    def validate_and_extract(self, question: str) -> Tuple[bool, Optional[str], Dict[str, Any]]:
        """
        验证并提取股票信息的完整流程
        
        Returns:
            Tuple[is_success, ts_code, error_response_if_failed]
        """
        # 输入验证
        if not question or not question.strip():
            error_response = self.format_error_response('EMPTY_INPUT')
            return False, None, error_response
        
        # 解析意图和提取股票代码
        intent, ts_code_or_error = self.parse_query_intent_and_extract_stock(question)
        
        # 处理特殊错误码
        if ts_code_or_error == 'INVALID_FORMAT':
            error_response = self.format_error_response('INVALID_FORMAT')
            return False, None, error_response
        elif ts_code_or_error == 'INVALID_LENGTH':
            error_response = self.format_error_response('INVALID_LENGTH')
            return False, None, error_response
        elif not ts_code_or_error:
            error_response = self.format_error_response('NOT_FOUND')
            return False, None, error_response
        
        # 成功提取
        self.logger.info(f"成功提取股票代码: {ts_code_or_error}, 查询意图: {intent}")
        return True, ts_code_or_error, {}


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
    # 测试用例
    test_cases = [
        "贵州茅台财务健康度",
        "600519财务健康度", 
        "600519.SH财务健康度",
        "茅台财务健康度",  # 应该失败
        "60051财务健康度",  # 应该失败
        "600519.XX财务健康度",  # 应该失败
        "",  # 应该失败
    ]
    
    validator = UnifiedStockValidator()
    
    for test_case in test_cases:
        print(f"\n测试: {test_case}")
        success, ts_code, error_response = validator.validate_and_extract(test_case)
        if success:
            print(f"  ✅ 成功: {ts_code}")
        else:
            print(f"  ❌ 失败: {error_response['error']}")