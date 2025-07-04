#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
参数处理模块单元测试
测试parameter_extractor和query_validator的功能
"""

import sys
import os
import unittest
from datetime import datetime, timedelta

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.parameter_extractor import ParameterExtractor, ExtractedParams
from utils.query_validator import QueryValidator, ValidationResult
from utils.query_templates import QueryTemplate


class TestParameterExtractor(unittest.TestCase):
    """参数提取器测试"""
    
    def setUp(self):
        """测试初始化"""
        self.extractor = ParameterExtractor()
    
    def test_extract_single_stock(self):
        """测试单个股票提取"""
        query = "贵州茅台最新股价"
        params = self.extractor.extract_all_params(query)
        
        self.assertEqual(len(params.stocks), 1)
        self.assertEqual(params.stocks[0], "600519.SH")
        self.assertEqual(params.stock_names[0], "贵州茅台")
        self.assertIsNone(params.error)
    
    def test_extract_multiple_stocks(self):
        """测试多个股票提取"""
        query = "比较贵州茅台和五粮液的市值"
        params = self.extractor.extract_all_params(query)
        
        self.assertEqual(len(params.stocks), 2)
        self.assertIn("600519.SH", params.stocks)
        self.assertIn("000858.SZ", params.stocks)
    
    def test_extract_date(self):
        """测试日期提取"""
        # 测试具体日期
        query = "贵州茅台2025-06-27的股价"
        params = self.extractor.extract_all_params(query)
        self.assertEqual(params.date, "2025-06-27")
        
        # 测试自然语言日期（需要date_intelligence支持）
        query = "贵州茅台最新股价"
        params = self.extractor.extract_all_params(query)
        # 这里应该提取到当前日期或最近交易日
        self.assertIsNotNone(params.date)
    
    def test_extract_date_range(self):
        """测试日期范围提取"""
        query = "贵州茅台从2025-01-01到2025-06-30的K线"
        params = self.extractor.extract_all_params(query)
        
        self.assertIsNotNone(params.date_range)
        self.assertEqual(params.date_range[0], "2025-01-01")
        self.assertEqual(params.date_range[1], "2025-06-30")
    
    def test_extract_limit(self):
        """测试数量限制提取"""
        # 测试数字
        query = "涨幅前10的股票"
        params = self.extractor.extract_all_params(query)
        self.assertEqual(params.limit, 10)
        
        # 测试中文数字
        query = "市值最大的前二十只股票"
        params = self.extractor.extract_all_params(query)
        self.assertEqual(params.limit, 20)
        
        # 测试默认值
        query = "涨幅最高的股票"
        params = self.extractor.extract_all_params(query)
        self.assertEqual(params.limit, 10)  # 默认值
    
    def test_extract_order_params(self):
        """测试排序参数提取"""
        # 测试降序
        query = "市值最大的股票"
        params = self.extractor.extract_all_params(query)
        self.assertEqual(params.order_by, "DESC")
        self.assertEqual(params.order_field, "market_cap")
        
        # 测试升序
        query = "PE最低的股票"
        params = self.extractor.extract_all_params(query)
        self.assertEqual(params.order_by, "ASC")
        self.assertEqual(params.order_field, "pe_ttm")
    
    def test_extract_exclude_conditions(self):
        """测试排除条件提取"""
        query = "市值最大的10只股票，排除ST"
        params = self.extractor.extract_all_params(query)
        self.assertTrue(params.exclude_st)
        self.assertFalse(params.exclude_bj)
        
        query = "涨幅前10，排除ST和北交所"
        params = self.extractor.extract_all_params(query)
        self.assertTrue(params.exclude_st)
        self.assertTrue(params.exclude_bj)
    
    def test_extract_sector(self):
        """测试板块提取"""
        query = "银行板块的主力资金"
        params = self.extractor.extract_all_params(query)
        self.assertEqual(params.sector, "银行")
        
        query = "新能源行业的龙头股"
        params = self.extractor.extract_all_params(query)
        self.assertEqual(params.industry, "新能源")
    
    def test_extract_period(self):
        """测试报告期提取"""
        # 年报
        query = "贵州茅台2024年年报的净利润"
        params = self.extractor.extract_all_params(query)
        self.assertEqual(params.period, "20241231")
        
        # 季报
        query = "贵州茅台2025年一季度的营收"
        params = self.extractor.extract_all_params(query)
        self.assertEqual(params.period, "20250331")
        
        # 中报
        query = "贵州茅台2024年中报数据"
        params = self.extractor.extract_all_params(query)
        self.assertEqual(params.period, "20240630")
    
    def test_error_handling(self):
        """测试错误处理"""
        # 测试无效股票
        query = "XXXYYY的股价"
        params = self.extractor.extract_all_params(query)
        # 应该在提取阶段就发现错误
        self.assertIsNotNone(params.error)


class TestQueryValidator(unittest.TestCase):
    """查询验证器测试"""
    
    def setUp(self):
        """测试初始化"""
        self.extractor = ParameterExtractor()
        self.validator = QueryValidator()
    
    def test_validate_valid_params(self):
        """测试有效参数验证"""
        query = "贵州茅台最新股价"
        params = self.extractor.extract_all_params(query)
        result = self.validator.validate_params(params)
        
        self.assertTrue(result.is_valid)
        self.assertIsNone(result.error_code)
        self.assertEqual(len(result.warnings), 0)
    
    def test_validate_required_stock(self):
        """测试必需股票验证"""
        # 创建需要股票的模板
        template = type('MockTemplate', (), {
            'requires_stock': True,
            'requires_date': False,
            'requires_date_range': False
        })()
        
        # 没有股票的查询
        query = "最新的涨幅排名"
        params = self.extractor.extract_all_params(query)
        result = self.validator.validate_params(params, template)
        
        self.assertFalse(result.is_valid)
        self.assertEqual(result.error_code, "MISSING_REQUIRED_STOCK")
    
    def test_validate_stock_limit(self):
        """测试股票数量限制"""
        # 创建包含过多股票的参数
        params = ExtractedParams()
        params.stocks = [f"00000{i}.SZ" for i in range(15)]  # 15只股票
        
        result = self.validator.validate_params(params)
        
        self.assertFalse(result.is_valid)
        self.assertEqual(result.error_code, "TOO_MANY_STOCKS")
    
    def test_validate_date_format(self):
        """测试日期格式验证"""
        params = ExtractedParams()
        params.date = "2025-13-45"  # 无效日期
        
        result = self.validator.validate_params(params)
        
        self.assertFalse(result.is_valid)
        self.assertEqual(result.error_code, "INVALID_DATE_FORMAT")
    
    def test_validate_date_range(self):
        """测试日期范围验证"""
        # 测试顺序错误
        params = ExtractedParams()
        params.date_range = ("2025-06-30", "2025-01-01")
        
        result = self.validator.validate_params(params)
        
        self.assertFalse(result.is_valid)
        self.assertEqual(result.error_code, "INVALID_DATE_RANGE")
        
        # 测试范围过大
        params = ExtractedParams()
        params.date_range = ("2000-01-01", "2025-12-31")
        
        result = self.validator.validate_params(params)
        
        self.assertFalse(result.is_valid)
        self.assertEqual(result.error_code, "DATE_RANGE_TOO_LARGE")
    
    def test_validate_limit(self):
        """测试数量限制验证"""
        # 测试过小
        params = ExtractedParams()
        params.limit = 0
        
        result = self.validator.validate_params(params)
        
        self.assertFalse(result.is_valid)
        self.assertEqual(result.error_code, "LIMIT_TOO_SMALL")
        
        # 测试过大
        params = ExtractedParams()
        params.limit = 2000
        
        result = self.validator.validate_params(params)
        
        self.assertFalse(result.is_valid)
        self.assertEqual(result.error_code, "LIMIT_TOO_LARGE")
    
    def test_validate_period(self):
        """测试报告期验证"""
        # 测试无效格式
        params = ExtractedParams()
        params.period = "2024-12-31"  # 应该是YYYYMMDD
        
        result = self.validator.validate_params(params)
        
        self.assertFalse(result.is_valid)
        self.assertEqual(result.error_code, "INVALID_PERIOD_FORMAT")
        
        # 测试非标准报告期（应该有警告）
        params = ExtractedParams()
        params.period = "20240615"  # 不是季度末
        
        result = self.validator.validate_params(params)
        
        self.assertTrue(result.is_valid)
        self.assertGreater(len(result.warnings), 0)
    
    def test_user_friendly_messages(self):
        """测试用户友好消息"""
        # 测试各种错误的消息
        test_cases = [
            ("MISSING_REQUIRED_STOCK", "请指定要查询的股票"),
            ("INVALID_DATE_FORMAT", "日期格式错误"),
            ("TOO_MANY_STOCKS", "一次查询的股票数量过多"),
        ]
        
        for error_code, expected_prefix in test_cases:
            result = ValidationResult(is_valid=False, error_code=error_code)
            message = self.validator.get_user_friendly_message(result)
            self.assertTrue(message.startswith(expected_prefix))


class TestIntegration(unittest.TestCase):
    """集成测试"""
    
    def setUp(self):
        """测试初始化"""
        self.extractor = ParameterExtractor()
        self.validator = QueryValidator()
    
    def test_complete_flow(self):
        """测试完整流程"""
        test_queries = [
            {
                "query": "贵州茅台和五粮液最近30天的K线对比",
                "expected": {
                    "stock_count": 2,
                    "has_date_range": True,
                    "is_valid": True
                }
            },
            {
                "query": "市值最大的前50只股票，排除ST",
                "expected": {
                    "stock_count": 0,
                    "limit": 50,
                    "exclude_st": True,
                    "is_valid": True
                }
            },
            {
                "query": "银行板块2024年年报净利润排名",
                "expected": {
                    "sector": "银行",
                    "period": "20241231",
                    "is_valid": True
                }
            }
        ]
        
        for test in test_queries:
            query = test["query"]
            expected = test["expected"]
            
            # 提取参数
            params = self.extractor.extract_all_params(query)
            
            # 验证参数
            result = self.validator.validate_params(params)
            
            # 检查结果
            self.assertEqual(result.is_valid, expected["is_valid"], 
                           f"查询 '{query}' 验证结果不符合预期")
            
            if "stock_count" in expected:
                self.assertEqual(len(params.stocks), expected["stock_count"])
            
            if "has_date_range" in expected:
                self.assertEqual(params.date_range is not None, expected["has_date_range"])
            
            if "limit" in expected:
                self.assertEqual(params.limit, expected["limit"])
            
            if "exclude_st" in expected:
                self.assertEqual(params.exclude_st, expected["exclude_st"])
            
            if "sector" in expected:
                self.assertEqual(params.sector, expected["sector"])
            
            if "period" in expected:
                self.assertEqual(params.period, expected["period"])


if __name__ == "__main__":
    # 运行测试
    unittest.main(verbosity=2)