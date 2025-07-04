#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
参数处理模块集成测试
测试参数提取和验证的完整流程
"""

import sys
import os
import unittest
from datetime import datetime, timedelta

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.parameter_extractor import ParameterExtractor
from utils.query_validator import QueryValidator
from utils.query_templates import QueryTemplate, TemplateType


class TestRealWorldQueries(unittest.TestCase):
    """真实场景查询测试"""
    
    def setUp(self):
        """测试初始化"""
        self.extractor = ParameterExtractor()
        self.validator = QueryValidator()
    
    def test_daily_price_queries(self):
        """测试日常股价查询"""
        test_cases = [
            {
                "query": "贵州茅台今天的股价",
                "expected": {
                    "stocks": ["600519.SH"],
                    "has_date": True,
                    "is_valid": True
                }
            },
            {
                "query": "昨天平安银行的收盘价是多少",
                "expected": {
                    "stocks": ["000001.SZ"],
                    "has_date": True,
                    "metrics": ["close"],
                    "is_valid": True
                }
            },
            {
                "query": "查看600519最新的开盘价、最高价、最低价和收盘价",
                "expected": {
                    "stocks": ["600519.SH"],
                    "has_date": True,
                    "metrics_include": ["open", "high", "low", "close"],
                    "is_valid": True
                }
            },
        ]
        
        self._run_test_cases(test_cases)
    
    def test_historical_data_queries(self):
        """测试历史数据查询"""
        test_cases = [
            {
                "query": "贵州茅台最近30天的K线走势",
                "expected": {
                    "stocks": ["600519.SH"],
                    "has_date_range": True,
                    "is_valid": True
                }
            },
            {
                "query": "查看宁德时代从2025年1月1日到2025年6月30日的股价走势",
                "expected": {
                    "stocks": ["300750.SZ"],
                    "date_range": ("2025-01-01", "2025-06-30"),
                    "is_valid": True
                }
            },
            {
                "query": "比较贵州茅台和五粮液过去一年的表现",
                "expected": {
                    "stocks": ["600519.SH", "000858.SZ"],
                    "has_date_range": True,
                    "is_valid": True
                }
            },
        ]
        
        self._run_test_cases(test_cases)
    
    def test_ranking_queries(self):
        """测试排名查询"""
        test_cases = [
            {
                "query": "今天涨幅前10的股票",
                "expected": {
                    "limit": 10,
                    "order_by": "DESC",
                    "order_field": "pct_chg",
                    "has_date": True,
                    "is_valid": True
                }
            },
            {
                "query": "市值最大的前20只股票，排除ST",
                "expected": {
                    "limit": 20,
                    "exclude_st": True,
                    "order_by": "DESC",
                    "order_field": "market_cap",
                    "is_valid": True
                }
            },
            {
                "query": "PE最低的前十只股票，不包括北交所",
                "expected": {
                    "limit": 10,
                    "exclude_bj": True,
                    "order_by": "ASC",
                    "order_field": "pe_ttm",
                    "is_valid": True
                }
            },
        ]
        
        self._run_test_cases(test_cases)
    
    def test_sector_queries(self):
        """测试板块查询"""
        test_cases = [
            {
                "query": "银行板块今天的涨跌情况",
                "expected": {
                    "sector": "银行",
                    "has_date": True,
                    "is_valid": True
                }
            },
            {
                "query": "新能源板块市值排名前10的公司",
                "expected": {
                    "sector": "新能源",
                    "limit": 10,
                    "order_field": "market_cap",
                    "is_valid": True
                }
            },
            {
                "query": "白酒行业2024年年报净利润排名",
                "expected": {
                    "industry": "白酒",
                    "period": "20241231",
                    "order_field": "n_income",
                    "is_valid": True
                }
            },
        ]
        
        self._run_test_cases(test_cases)
    
    def test_financial_queries(self):
        """测试财务数据查询"""
        test_cases = [
            {
                "query": "贵州茅台2024年年报的净利润和营收",
                "expected": {
                    "stocks": ["600519.SH"],
                    "period": "20241231",
                    "metrics_include": ["n_income", "total_revenue"],
                    "is_valid": True
                }
            },
            {
                "query": "查询平安银行最新的PE、PB和ROE",
                "expected": {
                    "stocks": ["000001.SZ"],
                    "metrics_include": ["pe_ttm", "pb", "roe"],
                    "is_valid": True
                }
            },
            {
                "query": "宁德时代2025年一季度的财务数据",
                "expected": {
                    "stocks": ["300750.SZ"],
                    "period": "20250331",
                    "is_valid": True
                }
            },
        ]
        
        self._run_test_cases(test_cases)
    
    def test_complex_queries(self):
        """测试复杂查询"""
        test_cases = [
            {
                "query": "比较贵州茅台、五粮液、泸州老窖最近30天的涨跌幅，按涨幅从高到低排序",
                "expected": {
                    "stocks": ["600519.SH", "000858.SZ", "000568.SZ"],
                    "has_date_range": True,
                    "order_by": "DESC",
                    "order_field": "pct_chg",
                    "is_valid": True
                }
            },
            {
                "query": "银行板块2024年年报ROE排名前15的公司，排除ST股票",
                "expected": {
                    "sector": "银行",
                    "period": "20241231",
                    "limit": 15,
                    "exclude_st": True,
                    "order_field": "roe",
                    "is_valid": True
                }
            },
        ]
        
        self._run_test_cases(test_cases)
    
    def _run_test_cases(self, test_cases):
        """运行测试用例的辅助方法"""
        for test_case in test_cases:
            query = test_case["query"]
            expected = test_case["expected"]
            
            with self.subTest(query=query):
                # 提取参数
                params = self.extractor.extract_all_params(query)
                
                # 验证参数
                result = self.validator.validate_params(params)
                
                # 检查验证结果
                self.assertEqual(result.is_valid, expected.get("is_valid", True),
                               f"验证结果不符合预期: {result.error_code}")
                
                # 检查具体参数
                if "stocks" in expected:
                    self.assertEqual(sorted(params.stocks), sorted(expected["stocks"]))
                
                if "has_date" in expected and expected["has_date"]:
                    self.assertIsNotNone(params.date)
                
                if "has_date_range" in expected and expected["has_date_range"]:
                    self.assertIsNotNone(params.date_range)
                
                if "date_range" in expected:
                    self.assertEqual(params.date_range, expected["date_range"])
                
                if "limit" in expected:
                    self.assertEqual(params.limit, expected["limit"])
                
                if "order_by" in expected:
                    self.assertEqual(params.order_by, expected["order_by"])
                
                if "order_field" in expected:
                    self.assertEqual(params.order_field, expected["order_field"])
                
                if "exclude_st" in expected:
                    self.assertEqual(params.exclude_st, expected["exclude_st"])
                
                if "exclude_bj" in expected:
                    self.assertEqual(params.exclude_bj, expected["exclude_bj"])
                
                if "sector" in expected:
                    self.assertEqual(params.sector, expected["sector"])
                
                if "industry" in expected:
                    self.assertEqual(params.industry, expected["industry"])
                
                if "period" in expected:
                    self.assertEqual(params.period, expected["period"])
                
                if "metrics" in expected:
                    self.assertEqual(params.metrics, expected["metrics"])
                
                if "metrics_include" in expected:
                    for metric in expected["metrics_include"]:
                        self.assertIn(metric, params.metrics)


class TestErrorHandlingScenarios(unittest.TestCase):
    """错误处理场景测试"""
    
    def setUp(self):
        """测试初始化"""
        self.extractor = ParameterExtractor()
        self.validator = QueryValidator()
    
    def test_invalid_stock_queries(self):
        """测试无效股票查询"""
        test_cases = [
            "XXXYYY的股价",          # 不存在的股票代码
            "测试公司的市值",         # 不存在的公司名称
            "999999.SH的数据",       # 无效的股票代码
            "60051的股价",           # 位数错误
            "A00001.SZ的走势",       # 包含字母的代码
        ]
        
        for query in test_cases:
            with self.subTest(query=query):
                params = self.extractor.extract_all_params(query)
                result = self.validator.validate_params(params)
                
                self.assertFalse(result.is_valid)
                self.assertTrue(
                    result.error_code in ["PARAM_EXTRACTION_ERROR", "INVALID_STOCK_FORMAT"],
                    f"期望的错误码应该是股票相关错误，实际是: {result.error_code}"
                )
    
    def test_invalid_date_queries(self):
        """测试无效日期查询"""
        test_cases = [
            "查询2025年13月的数据",      # 无效月份
            "2025-02-30的股价",          # 无效日期
            "1985年的股票数据",          # 日期过早
        ]
        
        for query in test_cases:
            with self.subTest(query=query):
                params = self.extractor.extract_all_params(query)
                
                # 如果有日期被提取，验证应该失败
                if params.date or params.date_range:
                    result = self.validator.validate_params(params)
                    self.assertFalse(result.is_valid)
    
    def test_conflicting_parameters(self):
        """测试参数冲突的情况"""
        test_cases = [
            {
                "query": "涨幅最高但跌幅最大的股票",  # 逻辑矛盾
                "check": lambda p: p.order_field is not None  # 应该选择一个
            },
            {
                "query": "所有股票排除所有股票",  # 逻辑矛盾
                "check": lambda p: True  # 这种查询应该被处理，不应该崩溃
            },
        ]
        
        for test_case in test_cases:
            query = test_case["query"]
            check_func = test_case["check"]
            
            with self.subTest(query=query):
                # 不应该抛出异常
                try:
                    params = self.extractor.extract_all_params(query)
                    result = self.validator.validate_params(params)
                    self.assertTrue(check_func(params))
                except Exception as e:
                    self.fail(f"查询 '{query}' 不应该抛出异常: {e}")


class TestTemplateBasedValidation(unittest.TestCase):
    """基于模板的验证测试"""
    
    def setUp(self):
        """测试初始化"""
        self.extractor = ParameterExtractor()
        self.validator = QueryValidator()
    
    def test_stock_price_template(self):
        """测试股价查询模板"""
        # 创建股价查询模板
        template = QueryTemplate(
            name="股价查询",
            type=TemplateType.PRICE_QUERY,
            pattern=r"",
            route_type="SQL_ONLY",
            required_fields=["close", "trade_date"],
            optional_fields=["open", "high", "low", "vol", "amount", "pct_chg"],
            default_params={},
            example="贵州茅台的股价",
            requires_stock=True,
            requires_date=True
        )
        
        # 测试缺少股票
        params = self.extractor.extract_all_params("最新股价")
        result = self.validator.validate_params(params, template)
        self.assertFalse(result.is_valid)
        self.assertEqual(result.error_code, "MISSING_REQUIRED_STOCK")
        
        # 测试缺少日期
        params = self.extractor.extract_all_params("贵州茅台的股价")
        params.date = None  # 清除可能自动添加的日期
        result = self.validator.validate_params(params, template)
        # 如果没有日期，验证应该失败
        if not params.date:
            self.assertFalse(result.is_valid)
            self.assertEqual(result.error_code, "MISSING_REQUIRED_DATE")
    
    def test_ranking_template(self):
        """测试排名查询模板"""
        # 创建排名查询模板
        template = QueryTemplate(
            name="涨跌幅排名",
            type=TemplateType.RANKING,
            pattern=r"",
            route_type="SQL_ONLY",
            required_fields=["ts_code", "name", "pct_chg"],
            optional_fields=["close", "amount"],
            default_params={"limit": 10},
            example="涨幅前10",
            requires_stock=False,
            requires_date=True,
            requires_limit=True,
            supports_exclude_st=True
        )
        
        # 测试正常排名查询
        params = self.extractor.extract_all_params("涨幅前20的股票，排除ST")
        result = self.validator.validate_params(params, template)
        
        self.assertTrue(result.is_valid)
        self.assertEqual(params.limit, 20)
        self.assertTrue(params.exclude_st)


class TestPerformanceAndStress(unittest.TestCase):
    """性能和压力测试"""
    
    def setUp(self):
        """测试初始化"""
        self.extractor = ParameterExtractor()
        self.validator = QueryValidator()
    
    def test_long_query_handling(self):
        """测试长查询处理"""
        # 创建一个很长的查询
        stocks = ["贵州茅台", "五粮液", "泸州老窖", "山西汾酒", "洋河股份"]
        long_query = f"比较{'、'.join(stocks)}这些股票在2025年1月1日到2025年6月30日期间的开盘价、最高价、最低价、收盘价、成交量、成交额、涨跌幅等各项指标，并按照涨幅从高到低排序，同时排除ST股票"
        
        # 测试是否能正确处理
        params = self.extractor.extract_all_params(long_query)
        result = self.validator.validate_params(params)
        
        self.assertTrue(result.is_valid)
        self.assertEqual(len(params.stocks), 5)
        self.assertIsNotNone(params.date_range)
        self.assertTrue(params.exclude_st)
        self.assertGreater(len(params.metrics), 0)
    
    def test_many_validations(self):
        """测试大量验证的性能"""
        import time
        
        # 准备测试查询
        queries = [
            "贵州茅台的股价",
            "涨幅前10",
            "银行板块的数据",
            "PE最低的股票",
            "比较茅台和五粮液",
        ] * 20  # 100个查询
        
        start_time = time.time()
        
        for query in queries:
            params = self.extractor.extract_all_params(query)
            result = self.validator.validate_params(params)
        
        end_time = time.time()
        elapsed_time = end_time - start_time
        
        # 100个查询应该在合理时间内完成（比如5秒）
        self.assertLess(elapsed_time, 5.0, 
                       f"100个查询验证耗时 {elapsed_time:.2f} 秒，超过预期")
    
    def test_edge_case_parameters(self):
        """测试边界参数"""
        # 测试最大数量的股票
        max_stocks = [f"{i:06d}.SZ" for i in range(10)]  # 最大允许10只
        params = ExtractedParams()
        params.stocks = max_stocks
        result = self.validator.validate_params(params)
        self.assertTrue(result.is_valid)
        
        # 测试最大日期范围（10年）
        params = ExtractedParams()
        params.date_range = ("2015-07-05", "2025-07-05")
        result = self.validator.validate_params(params)
        self.assertTrue(result.is_valid)
        
        # 测试最大数量限制
        params = ExtractedParams()
        params.limit = 1000
        result = self.validator.validate_params(params)
        self.assertTrue(result.is_valid)


class TestSpecialCasesAndRegression(unittest.TestCase):
    """特殊情况和回归测试"""
    
    def setUp(self):
        """测试初始化"""
        self.extractor = ParameterExtractor()
        self.validator = QueryValidator()
    
    def test_chinese_english_mixed(self):
        """测试中英文混合查询"""
        test_cases = [
            "查询KWEICHOW MOUTAI的PE ratio",
            "top10涨幅股票",
            "ROE最高的stocks",
        ]
        
        for query in test_cases:
            with self.subTest(query=query):
                # 不应该崩溃
                params = self.extractor.extract_all_params(query)
                result = self.validator.validate_params(params)
                # 至少应该返回结果
                self.assertIsNotNone(result)
    
    def test_special_characters(self):
        """测试特殊字符处理"""
        test_cases = [
            "贵州茅台（600519）的股价",
            "查询【贵州茅台】的数据",
            "贵州茅台/五粮液对比",
            "贵州茅台、五粮液、泸州老窖",
            "贵州茅台 vs 五粮液",
        ]
        
        for query in test_cases:
            with self.subTest(query=query):
                params = self.extractor.extract_all_params(query)
                # 应该能提取到股票
                self.assertGreater(len(params.stocks), 0)
    
    def test_regression_issues(self):
        """回归测试 - 测试之前发现的问题"""
        # 测试年份被误识别为数量的问题
        params = self.extractor.extract_all_params("2024年的数据前10名")
        self.assertEqual(params.limit, 10)  # 不应该是2024
        
        # 测试"平安"简称问题
        params = self.extractor.extract_all_params("平安的股价")
        # 不支持简称，应该报错
        self.assertIsNotNone(params.error)
        self.assertIn("请使用完整公司名称", params.error)
        
        # 测试排名查询不应该要求股票
        params = self.extractor.extract_all_params("涨幅排名前10")
        template = type('MockTemplate', (), {'requires_stock': True})()
        result = self.validator.validate_params(params, template)
        # 即使模板要求股票，排名查询也应该通过
        # （这取决于具体的业务逻辑）


if __name__ == "__main__":
    # 运行测试
    unittest.main(verbosity=2)