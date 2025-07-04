#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
查询验证器全面测试
覆盖各种验证场景和边界情况
"""

import sys
import os
import unittest
from datetime import datetime, timedelta

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.parameter_extractor import ExtractedParams
from utils.query_validator import QueryValidator, ValidationResult
from utils.query_templates import QueryTemplate


class TestQueryValidatorStockValidation(unittest.TestCase):
    """股票验证相关测试"""
    
    def setUp(self):
        """测试初始化"""
        self.validator = QueryValidator()
    
    def test_validate_valid_stock_codes(self):
        """测试有效股票代码验证"""
        params = ExtractedParams()
        params.stocks = [
            "600519.SH",  # 上海主板
            "000001.SZ",  # 深圳主板
            "300750.SZ",  # 创业板
            "688009.SH",  # 科创板
            "430047.BJ",  # 北交所
        ]
        
        result = self.validator.validate_params(params)
        self.assertTrue(result.is_valid)
        self.assertIsNone(result.error_code)
    
    def test_validate_invalid_stock_format(self):
        """测试无效股票格式验证"""
        test_cases = [
            (["600519"], "股票代码格式错误"),           # 缺少后缀
            (["600519.sh"], "股票代码格式错误"),        # 小写后缀
            (["60051.SH"], "股票代码格式错误"),         # 位数不对
            (["A00001.SZ"], "股票代码格式错误"),        # 包含字母
            (["600519.XX"], "股票代码格式错误"),        # 无效后缀
        ]
        
        for stocks, expected_error in test_cases:
            with self.subTest(stocks=stocks):
                params = ExtractedParams()
                params.stocks = stocks
                result = self.validator.validate_params(params)
                
                self.assertFalse(result.is_valid)
                self.assertEqual(result.error_code, "INVALID_STOCK_FORMAT")
                self.assertIn(expected_error, result.error_detail.get("message", ""))
    
    def test_validate_stock_count_limit(self):
        """测试股票数量限制验证"""
        # 创建超过限制的股票列表
        params = ExtractedParams()
        params.stocks = [f"{i:06d}.SZ" for i in range(15)]  # 15只股票
        
        result = self.validator.validate_params(params)
        
        self.assertFalse(result.is_valid)
        self.assertEqual(result.error_code, "TOO_MANY_STOCKS")
        self.assertEqual(result.error_detail["count"], 15)
        self.assertEqual(result.error_detail["max"], 10)
    
    def test_validate_required_stock_missing(self):
        """测试缺少必需股票验证"""
        template = type('MockTemplate', (), {
            'requires_stock': True,
            'requires_date': False,
            'requires_date_range': False
        })()
        
        params = ExtractedParams()
        params.stocks = []  # 没有股票
        
        result = self.validator.validate_params(params, template)
        
        self.assertFalse(result.is_valid)
        self.assertEqual(result.error_code, "MISSING_REQUIRED_STOCK")
    
    def test_param_extraction_error_handling(self):
        """测试参数提取错误处理"""
        params = ExtractedParams()
        params.error = "无法识别股票: XXXYYY"
        
        result = self.validator.validate_params(params)
        
        self.assertFalse(result.is_valid)
        self.assertEqual(result.error_code, "PARAM_EXTRACTION_ERROR")
        self.assertEqual(result.error_detail["message"], "无法识别股票: XXXYYY")


class TestQueryValidatorDateValidation(unittest.TestCase):
    """日期验证相关测试"""
    
    def setUp(self):
        """测试初始化"""
        self.validator = QueryValidator()
    
    def test_validate_valid_dates(self):
        """测试有效日期验证"""
        test_dates = [
            "2025-07-04",
            "2020-01-01",
            "1990-01-01",  # 边界值
            datetime.now().strftime("%Y-%m-%d"),  # 今天
        ]
        
        for date in test_dates:
            with self.subTest(date=date):
                params = ExtractedParams()
                params.date = date
                result = self.validator.validate_params(params)
                
                self.assertTrue(result.is_valid)
    
    def test_validate_invalid_date_format(self):
        """测试无效日期格式验证"""
        test_cases = [
            "2025-13-01",      # 无效月份
            "2025-02-30",      # 无效日期
            "25-07-04",        # 年份格式错误
            "2025/07/04",      # 错误分隔符
            "20250704",        # 无分隔符
            "2025年7月4日",    # 中文格式
        ]
        
        for date in test_cases:
            with self.subTest(date=date):
                params = ExtractedParams()
                params.date = date
                result = self.validator.validate_params(params)
                
                self.assertFalse(result.is_valid)
                self.assertEqual(result.error_code, "INVALID_DATE_FORMAT")
    
    def test_validate_date_boundaries(self):
        """测试日期边界验证"""
        # 测试过早的日期
        params = ExtractedParams()
        params.date = "1989-12-31"  # 早于1990年
        result = self.validator.validate_params(params)
        
        self.assertFalse(result.is_valid)
        self.assertEqual(result.error_code, "DATE_TOO_EARLY")
        
        # 测试未来日期（应该有警告）
        params = ExtractedParams()
        future_date = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")
        params.date = future_date
        result = self.validator.validate_params(params)
        
        self.assertTrue(result.is_valid)  # 仍然有效
        self.assertGreater(len(result.warnings), 0)  # 但有警告
        self.assertIn("未来日期", result.warnings[0])
    
    def test_validate_date_range(self):
        """测试日期范围验证"""
        # 测试有效的日期范围
        params = ExtractedParams()
        params.date_range = ("2025-01-01", "2025-06-30")
        result = self.validator.validate_params(params)
        
        self.assertTrue(result.is_valid)
        
        # 测试顺序错误的日期范围
        params = ExtractedParams()
        params.date_range = ("2025-06-30", "2025-01-01")
        result = self.validator.validate_params(params)
        
        self.assertFalse(result.is_valid)
        self.assertEqual(result.error_code, "INVALID_DATE_RANGE")
        
        # 测试过大的日期范围
        params = ExtractedParams()
        params.date_range = ("2000-01-01", "2025-12-31")  # 25年
        result = self.validator.validate_params(params)
        
        self.assertFalse(result.is_valid)
        self.assertEqual(result.error_code, "DATE_RANGE_TOO_LARGE")
    
    def test_validate_required_date(self):
        """测试必需日期验证"""
        template = type('MockTemplate', (), {
            'requires_stock': False,
            'requires_date': True,
            'requires_date_range': False
        })()
        
        # 没有日期
        params = ExtractedParams()
        result = self.validator.validate_params(params, template)
        
        self.assertFalse(result.is_valid)
        self.assertEqual(result.error_code, "MISSING_REQUIRED_DATE")
        
        # 有日期范围也算满足
        params = ExtractedParams()
        params.date_range = ("2025-01-01", "2025-06-30")
        result = self.validator.validate_params(params, template)
        
        self.assertTrue(result.is_valid)


class TestQueryValidatorLimitValidation(unittest.TestCase):
    """数量限制验证相关测试"""
    
    def setUp(self):
        """测试初始化"""
        self.validator = QueryValidator()
    
    def test_validate_valid_limits(self):
        """测试有效数量限制验证"""
        valid_limits = [1, 10, 50, 100, 500, 1000]
        
        for limit in valid_limits:
            with self.subTest(limit=limit):
                params = ExtractedParams()
                params.limit = limit
                result = self.validator.validate_params(params)
                
                self.assertTrue(result.is_valid)
    
    def test_validate_limit_boundaries(self):
        """测试数量限制边界验证"""
        # 测试下界
        params = ExtractedParams()
        params.limit = 0
        result = self.validator.validate_params(params)
        
        self.assertFalse(result.is_valid)
        self.assertEqual(result.error_code, "LIMIT_TOO_SMALL")
        
        # 测试上界
        params = ExtractedParams()
        params.limit = 1001
        result = self.validator.validate_params(params)
        
        self.assertFalse(result.is_valid)
        self.assertEqual(result.error_code, "LIMIT_TOO_LARGE")
        
        # 测试边界值
        for limit in [1, 1000]:
            params = ExtractedParams()
            params.limit = limit
            result = self.validator.validate_params(params)
            self.assertTrue(result.is_valid)
    
    def test_validate_negative_limit(self):
        """测试负数限制验证"""
        params = ExtractedParams()
        params.limit = -10
        result = self.validator.validate_params(params)
        
        self.assertFalse(result.is_valid)
        self.assertEqual(result.error_code, "LIMIT_TOO_SMALL")


class TestQueryValidatorPeriodValidation(unittest.TestCase):
    """报告期验证相关测试"""
    
    def setUp(self):
        """测试初始化"""
        self.validator = QueryValidator()
    
    def test_validate_valid_periods(self):
        """测试有效报告期验证"""
        valid_periods = [
            "20241231",  # 年报
            "20240331",  # 一季报
            "20240630",  # 中报
            "20240930",  # 三季报
        ]
        
        for period in valid_periods:
            with self.subTest(period=period):
                params = ExtractedParams()
                params.period = period
                result = self.validator.validate_params(params)
                
                self.assertTrue(result.is_valid)
    
    def test_validate_invalid_period_format(self):
        """测试无效报告期格式验证"""
        test_cases = [
            "2024-12-31",   # 包含分隔符
            "24123",        # 位数不对
            "202412311",    # 位数过多
            "2024Q4",       # 季度格式
            "2024年报",     # 中文格式
        ]
        
        for period in test_cases:
            with self.subTest(period=period):
                params = ExtractedParams()
                params.period = period
                result = self.validator.validate_params(params)
                
                self.assertFalse(result.is_valid)
                self.assertEqual(result.error_code, "INVALID_PERIOD_FORMAT")
    
    def test_validate_non_standard_period(self):
        """测试非标准报告期验证"""
        # 非季度末日期应该有警告
        params = ExtractedParams()
        params.period = "20240615"  # 6月15日，不是季度末
        result = self.validator.validate_params(params)
        
        self.assertTrue(result.is_valid)  # 仍然有效
        self.assertGreater(len(result.warnings), 0)  # 但有警告
        self.assertIn("可能不是标准的季度报告日期", result.warnings[0])


class TestQueryValidatorMetricsValidation(unittest.TestCase):
    """指标验证相关测试"""
    
    def setUp(self):
        """测试初始化"""
        self.validator = QueryValidator()
    
    def test_validate_metrics_with_template(self):
        """测试基于模板的指标验证"""
        template = type('MockTemplate', (), {
            'requires_stock': False,
            'requires_date': False,
            'requires_date_range': False,
            'required_fields': ['close', 'vol', 'amount'],
            'optional_fields': ['open', 'high', 'low', 'pct_chg']
        })()
        
        # 测试有效指标
        params = ExtractedParams()
        params.metrics = ['close', 'vol', 'open']
        result = self.validator.validate_params(params, template)
        
        self.assertTrue(result.is_valid)
        
        # 测试包含无效指标
        params = ExtractedParams()
        params.metrics = ['close', 'vol', 'invalid_metric']
        result = self.validator.validate_params(params, template)
        
        self.assertTrue(result.is_valid)  # 仍然有效
        self.assertGreater(len(result.warnings), 0)  # 但有警告
        self.assertIn("invalid_metric", result.warnings[0])
    
    def test_validate_metrics_without_template(self):
        """测试无模板的指标验证"""
        params = ExtractedParams()
        params.metrics = ['close', 'vol', 'pe_ttm', 'pb', 'roe']
        result = self.validator.validate_params(params)
        
        # 没有模板时，所有指标都应该被接受
        self.assertTrue(result.is_valid)
        self.assertEqual(len(result.warnings), 0)


class TestQueryValidatorSectorValidation(unittest.TestCase):
    """板块和行业验证相关测试"""
    
    def setUp(self):
        """测试初始化"""
        self.validator = QueryValidator()
    
    def test_validate_normal_sectors(self):
        """测试正常板块名称验证"""
        normal_sectors = ["银行", "新能源", "白酒", "科技", "医药", "房地产"]
        
        for sector in normal_sectors:
            with self.subTest(sector=sector):
                params = ExtractedParams()
                params.sector = sector
                result = self.validator.validate_params(params)
                
                self.assertTrue(result.is_valid)
                self.assertEqual(len(result.warnings), 0)
    
    def test_validate_long_sector_names(self):
        """测试过长的板块名称验证"""
        params = ExtractedParams()
        params.sector = "这是一个非常非常非常非常长的板块名称超过了二十个字符"
        result = self.validator.validate_params(params)
        
        self.assertTrue(result.is_valid)  # 仍然有效
        self.assertGreater(len(result.warnings), 0)  # 但有警告
        self.assertIn("可能过长", result.warnings[0])
    
    def test_validate_industry_names(self):
        """测试行业名称验证"""
        params = ExtractedParams()
        params.industry = "互联网"
        result = self.validator.validate_params(params)
        
        self.assertTrue(result.is_valid)
        
        # 测试过长的行业名称
        params = ExtractedParams()
        params.industry = "超级无敌霹雳长的行业名称测试用例"
        result = self.validator.validate_params(params)
        
        self.assertTrue(result.is_valid)
        self.assertGreater(len(result.warnings), 0)


class TestQueryValidatorComplexScenarios(unittest.TestCase):
    """复杂场景验证测试"""
    
    def setUp(self):
        """测试初始化"""
        self.validator = QueryValidator()
    
    def test_validate_complex_stock_query(self):
        """测试复杂股票查询验证"""
        params = ExtractedParams()
        params.stocks = ["600519.SH", "000858.SZ", "000568.SZ"]
        params.date_range = ("2025-01-01", "2025-06-30")
        params.limit = 10
        params.order_by = "DESC"
        params.order_field = "pct_chg"
        params.metrics = ["open", "high", "low", "close", "vol", "amount", "pct_chg"]
        
        result = self.validator.validate_params(params)
        
        self.assertTrue(result.is_valid)
        self.assertEqual(len(result.warnings), 0)
    
    def test_validate_complex_ranking_query(self):
        """测试复杂排名查询验证"""
        params = ExtractedParams()
        params.sector = "银行"
        params.period = "20241231"
        params.limit = 20
        params.exclude_st = True
        params.order_by = "DESC"
        params.order_field = "n_income"
        
        result = self.validator.validate_params(params)
        
        self.assertTrue(result.is_valid)
    
    def test_validate_multiple_errors(self):
        """测试多个错误的情况"""
        params = ExtractedParams()
        params.stocks = ["INVALID"]  # 无效股票格式
        params.date = "2025-13-45"   # 无效日期
        params.limit = 2000          # 超过限制
        params.period = "2024Q4"     # 无效格式
        
        result = self.validator.validate_params(params)
        
        # 应该在第一个错误处停止
        self.assertFalse(result.is_valid)
        self.assertIn(result.error_code, ["INVALID_STOCK_FORMAT", "INVALID_DATE_FORMAT", 
                                          "LIMIT_TOO_LARGE", "INVALID_PERIOD_FORMAT"])
    
    def test_validate_with_all_optional_params(self):
        """测试包含所有可选参数的验证"""
        params = ExtractedParams()
        params.stocks = ["600519.SH"]
        params.stock_names = ["贵州茅台"]
        params.date = "2025-07-04"
        params.date_range = None
        params.limit = 10
        params.order_by = "DESC"
        params.order_field = "close"
        params.metrics = ["close", "vol"]
        params.period = "20241231"
        params.exclude_st = True
        params.exclude_bj = False
        params.sector = None
        params.industry = None
        params.raw_query = "贵州茅台2025-07-04的股价"
        params.error = None
        
        result = self.validator.validate_params(params)
        
        self.assertTrue(result.is_valid)


class TestQueryValidatorUserMessages(unittest.TestCase):
    """用户友好消息测试"""
    
    def setUp(self):
        """测试初始化"""
        self.validator = QueryValidator()
    
    def test_all_error_messages(self):
        """测试所有错误消息"""
        error_cases = [
            ("PARAM_EXTRACTION_ERROR", "参数提取失败"),
            ("MISSING_REQUIRED_STOCK", "请指定要查询的股票"),
            ("MISSING_REQUIRED_DATE", "请指定查询日期"),
            ("MISSING_REQUIRED_DATE_RANGE", "请指定查询的日期范围"),
            ("TOO_MANY_STOCKS", "一次查询的股票数量过多"),
            ("INVALID_STOCK_FORMAT", "股票代码格式错误"),
            ("INVALID_DATE_FORMAT", "日期格式错误"),
            ("DATE_TOO_EARLY", "查询日期过早"),
            ("INVALID_DATE_RANGE", "日期范围无效"),
            ("DATE_RANGE_TOO_LARGE", "日期范围过大"),
            ("LIMIT_TOO_SMALL", "查询数量过少"),
            ("LIMIT_TOO_LARGE", "查询数量过多"),
            ("INVALID_PERIOD_FORMAT", "报告期格式错误"),
            ("VALIDATION_ERROR", "参数验证失败"),
        ]
        
        for error_code, expected_prefix in error_cases:
            with self.subTest(error_code=error_code):
                result = ValidationResult(is_valid=False, error_code=error_code)
                message = self.validator.get_user_friendly_message(result)
                self.assertTrue(message.startswith(expected_prefix))
    
    def test_error_messages_with_details(self):
        """测试带详细信息的错误消息"""
        # 测试包含详细信息的错误
        result = ValidationResult(
            is_valid=False,
            error_code="TOO_MANY_STOCKS",
            error_detail={"message": "您查询了15只股票，最多支持10只"}
        )
        message = self.validator.get_user_friendly_message(result)
        self.assertIn("15只股票", message)
        self.assertIn("最多支持10只", message)
        
        # 测试未知错误码
        result = ValidationResult(
            is_valid=False,
            error_code="UNKNOWN_ERROR_CODE"
        )
        message = self.validator.get_user_friendly_message(result)
        self.assertEqual(message, "参数验证失败")


class TestQueryValidatorEdgeCases(unittest.TestCase):
    """边界情况测试"""
    
    def setUp(self):
        """测试初始化"""
        self.validator = QueryValidator()
    
    def test_validate_empty_params(self):
        """测试空参数验证"""
        params = ExtractedParams()
        result = self.validator.validate_params(params)
        
        # 空参数应该通过验证（除非有必需字段）
        self.assertTrue(result.is_valid)
    
    def test_validate_none_values(self):
        """测试None值验证"""
        params = ExtractedParams()
        params.date = None
        params.date_range = None
        params.stocks = []
        params.metrics = []
        
        result = self.validator.validate_params(params)
        
        self.assertTrue(result.is_valid)
    
    def test_validate_exception_handling(self):
        """测试异常处理"""
        # 创建一个会导致异常的参数
        params = ExtractedParams()
        params.date = "not-a-date"  # 这会在strptime中引发异常
        
        result = self.validator.validate_params(params)
        
        # 应该捕获异常并返回验证失败
        self.assertFalse(result.is_valid)
        self.assertEqual(result.error_code, "INVALID_DATE_FORMAT")
    
    def test_validate_boundary_dates(self):
        """测试边界日期验证"""
        # 测试1990年1月1日（边界值）
        params = ExtractedParams()
        params.date = "1990-01-01"
        result = self.validator.validate_params(params)
        self.assertTrue(result.is_valid)
        
        # 测试1989年12月31日（超出边界）
        params = ExtractedParams()
        params.date = "1989-12-31"
        result = self.validator.validate_params(params)
        self.assertFalse(result.is_valid)
        self.assertEqual(result.error_code, "DATE_TOO_EARLY")


if __name__ == "__main__":
    # 运行测试
    unittest.main(verbosity=2)