#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
参数提取器全面测试
覆盖各种边界情况和复杂场景
"""

import sys
import os
import unittest
from datetime import datetime, timedelta

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.parameter_extractor import ParameterExtractor, ExtractedParams


class TestParameterExtractorStockExtraction(unittest.TestCase):
    """股票提取相关测试"""
    
    def setUp(self):
        """测试初始化"""
        self.extractor = ParameterExtractor()
    
    def test_extract_single_stock_with_code(self):
        """测试股票代码提取"""
        test_cases = [
            ("600519的股价", ["600519.SH"]),
            ("000001最新价格", ["000001.SZ"]),
            ("002594的市值", ["002594.SZ"]),
            ("688009的PE", ["688009.SH"]),  # 科创板
            ("300750涨幅", ["300750.SZ"]),   # 创业板
        ]
        
        for query, expected_stocks in test_cases:
            with self.subTest(query=query):
                params = self.extractor.extract_all_params(query)
                self.assertEqual(params.stocks, expected_stocks)
    
    def test_extract_single_stock_with_full_code(self):
        """测试完整股票代码提取"""
        test_cases = [
            ("600519.SH的股价", ["600519.SH"]),
            ("000001.SZ最新价格", ["000001.SZ"]),
            ("688009.SH的市值", ["688009.SH"]),
            ("430047.BJ的成交量", ["430047.BJ"]),  # 北交所
        ]
        
        for query, expected_stocks in test_cases:
            with self.subTest(query=query):
                params = self.extractor.extract_all_params(query)
                self.assertEqual(params.stocks, expected_stocks)
    
    def test_extract_single_stock_with_name(self):
        """测试股票名称提取"""
        test_cases = [
            ("贵州茅台的股价", ["600519.SH"]),
            ("平安银行最新价格", ["000001.SZ"]),
            ("宁德时代的市值", ["300750.SZ"]),
            ("中国平安的涨跌幅", ["601318.SH"]),
        ]
        
        for query, expected_stocks in test_cases:
            with self.subTest(query=query):
                params = self.extractor.extract_all_params(query)
                self.assertEqual(params.stocks, expected_stocks)
    
    def test_extract_multiple_stocks(self):
        """测试多个股票提取"""
        test_cases = [
            ("比较贵州茅台和五粮液", ["600519.SH", "000858.SZ"]),
            ("贵州茅台、五粮液、泸州老窖的对比", ["600519.SH", "000858.SZ", "000568.SZ"]),
            ("600519和000858的走势", ["600519.SH", "000858.SZ"]),
            ("贵州茅台vs五粮液", ["600519.SH", "000858.SZ"]),  # 使用完整名称
        ]
        
        for query, expected_stocks in test_cases:
            with self.subTest(query=query):
                params = self.extractor.extract_all_params(query)
                self.assertEqual(sorted(params.stocks), sorted(expected_stocks))
    
    def test_stock_extraction_edge_cases(self):
        """测试股票提取边界情况"""
        test_cases = [
            # 不应该提取股票的情况
            ("涨幅排名前10", []),
            ("市值最大的股票", []),
            ("所有银行股", []),
            ("ST股票列表", []),
            
            # 完整名称（正确用法）
            ("贵州茅台的股价", ["600519.SH"]),  # 完整名称
            ("中国平安的市值", ["601318.SH"]),  # 完整名称
            
            # 特殊格式
            ("查询600519.sh的股价", []),  # 小写后缀（应该失败）
            ("600519。SH的数据", []),  # 中文句号（应该失败）
        ]
        
        for query, expected_stocks in test_cases:
            with self.subTest(query=query):
                params = self.extractor.extract_all_params(query)
                self.assertEqual(params.stocks, expected_stocks)
    
    def test_invalid_stock_error_capture(self):
        """测试无效股票错误捕获"""
        test_cases = [
            ("XXXYYY的股价", "无法识别"),          # 无效代码
            ("999999的市值", "无法识别"),         # 不存在的代码
            ("测试股票的数据", None),          # 不存在的名称（可能无错误）
            ("茅台的股价", "请使用完整公司名称"),  # 简称（不支持）
            ("平安的市值", "无法识别"),         # 简称（不支持）
        ]
        
        for query, expected_error in test_cases:
            with self.subTest(query=query):
                params = self.extractor.extract_all_params(query)
                
                if expected_error is None:
                    # 有些查询可能不会产生错误
                    continue
                    
                self.assertIsNotNone(params.error, f"查询 '{query}' 应该有错误信息")
                self.assertTrue(
                    any(keyword in params.error for keyword in [expected_error, "无法识别", "请使用完整"]),
                    f"错误信息应包含'{expected_error}'，实际: {params.error}"
                )


    def test_stock_nickname_error_handling(self):
        """测试股票简称错误处理"""
        test_cases = [
            ("茅台的股价", "请使用完整公司名称"),      # 茅台 -> 贵州茅台
            ("五粮液的市值", []),                    # 五粮液本身是完整名称
            ("建行的PE", "请使用完整公司名称"),       # 建行 -> 建设银行
            ("招行的ROE", "请使用完整公司名称"),      # 招行 -> 招商银行
            ("万科的走势", None),                    # 万科可能不会产生错误（需要看映射）
            ("600519.sh的股价", None),               # 小写后缀问题
            ("600519.Sh的股价", None),               # 混合大小写问题
        ]
        
        for query, expected_result in test_cases:
            with self.subTest(query=query):
                params = self.extractor.extract_all_params(query)
                
                if expected_result == "请使用完整公司名称":
                    # 应该有错误信息
                    self.assertIsNotNone(params.error, f"查询 '{query}' 应该有错误信息")
                    self.assertIn("请使用完整公司名称", params.error)
                elif expected_result == []:
                    # 应该成功提取股票
                    self.assertIsNotNone(params.stocks)
                    self.assertGreater(len(params.stocks), 0)
                    self.assertIsNone(params.error)
                else:
                    # 其他情况，可能有错误也可能没有
                    pass


class TestParameterExtractorDateExtraction(unittest.TestCase):
    """日期提取相关测试"""
    
    def setUp(self):
        """测试初始化"""
        self.extractor = ParameterExtractor()
    
    def test_extract_specific_date(self):
        """测试具体日期提取"""
        test_cases = [
            ("2025-06-27的数据", "2025-06-27"),
            ("2025年6月27日的股价", "2025-06-27"),
            ("20250627的行情", "2025-06-27"),
            ("查询2025/06/27的数据", "2025-06-27"),
        ]
        
        for query, expected_date in test_cases:
            with self.subTest(query=query):
                params = self.extractor.extract_all_params(query)
                self.assertEqual(params.date, expected_date)
    
    def test_extract_relative_date(self):
        """测试相对日期提取"""
        # 这些测试依赖于date_intelligence的实现
        test_cases = [
            "最新股价",
            "昨天的数据",
            "上个交易日的行情",
            "前天的股价",
        ]
        
        for query in test_cases:
            with self.subTest(query=query):
                params = self.extractor.extract_all_params(query)
                # 应该提取到日期（具体值依赖于运行时间）
                self.assertIsNotNone(params.date)
                # 验证日期格式
                self.assertRegex(params.date, r'^\d{4}-\d{2}-\d{2}$')
    
    def test_extract_date_range(self):
        """测试日期范围提取"""
        test_cases = [
            ("从2025-01-01到2025-06-30", ("2025-01-01", "2025-06-30")),
            ("2025年1月到6月", None),  # 暂不支持月份范围
            ("最近30天", None),  # 应该有日期范围
            ("过去一周", None),  # 应该有日期范围
        ]
        
        for query, expected_range in test_cases:
            with self.subTest(query=query):
                params = self.extractor.extract_all_params(query)
                if expected_range:
                    self.assertEqual(params.date_range, expected_range)
                elif "最近" in query or "过去" in query:
                    self.assertIsNotNone(params.date_range)
    
    def test_date_vs_date_range_priority(self):
        """测试日期和日期范围的优先级"""
        # 当查询包含日期范围时，不应该提取单个日期
        query = "贵州茅台从2025-01-01到2025-06-30的走势"
        params = self.extractor.extract_all_params(query)
        
        self.assertIsNone(params.date)  # 不应该有单个日期
        self.assertIsNotNone(params.date_range)  # 应该有日期范围
        self.assertEqual(params.date_range, ("2025-01-01", "2025-06-30"))


class TestParameterExtractorLimitExtraction(unittest.TestCase):
    """数量限制提取相关测试"""
    
    def setUp(self):
        """测试初始化"""
        self.extractor = ParameterExtractor()
    
    def test_extract_numeric_limit(self):
        """测试数字形式的数量限制"""
        test_cases = [
            ("前10的股票", 10),
            ("涨幅前20", 20),
            ("市值最大的5只", 5),
            ("成交额前100名", 100),
            ("TOP50", 50),
        ]
        
        for query, expected_limit in test_cases:
            with self.subTest(query=query):
                params = self.extractor.extract_all_params(query)
                self.assertEqual(params.limit, expected_limit)
    
    def test_extract_chinese_number_limit(self):
        """测试中文数字的数量限制"""
        test_cases = [
            ("前十的股票", 10),
            ("涨幅前二十", 20),
            ("市值最大的五只", 5),
            ("前一百名", 100),
            ("前三十只股票", 30),
        ]
        
        for query, expected_limit in test_cases:
            with self.subTest(query=query):
                params = self.extractor.extract_all_params(query)
                self.assertEqual(params.limit, expected_limit)
    
    def test_year_number_exclusion(self):
        """测试年份数字排除"""
        test_cases = [
            ("2024年的数据", 10),  # 默认值，不是2024
            ("2025年报排名前10", 10),  # 应该是10，不是2025
            ("查询2023年年报", 10),  # 默认值，不是2023
        ]
        
        for query, expected_limit in test_cases:
            with self.subTest(query=query):
                params = self.extractor.extract_all_params(query)
                self.assertEqual(params.limit, expected_limit)
    
    def test_default_limit(self):
        """测试默认数量限制"""
        test_cases = [
            "涨幅最高的股票",
            "市值最大的",
            "成交额排名",
            "ROE最高的公司",
        ]
        
        for query in test_cases:
            with self.subTest(query=query):
                params = self.extractor.extract_all_params(query)
                self.assertEqual(params.limit, 10)  # 默认值


class TestParameterExtractorOrderExtraction(unittest.TestCase):
    """排序参数提取相关测试"""
    
    def setUp(self):
        """测试初始化"""
        self.extractor = ParameterExtractor()
    
    def test_extract_desc_order(self):
        """测试降序排序提取"""
        test_cases = [
            ("市值最大的股票", ("DESC", "market_cap")),
            ("涨幅最高的", ("DESC", "pct_chg")),
            ("成交额最多的", ("DESC", "amount")),
            ("ROE最高的公司", ("DESC", "roe")),
            ("利润最多的", ("DESC", "n_income")),
        ]
        
        for query, (expected_order, expected_field) in test_cases:
            with self.subTest(query=query):
                params = self.extractor.extract_all_params(query)
                self.assertEqual(params.order_by, expected_order)
                self.assertEqual(params.order_field, expected_field)
    
    def test_extract_asc_order(self):
        """测试升序排序提取"""
        test_cases = [
            ("PE最低的股票", ("ASC", "pe_ttm")),
            ("跌幅最大的", ("ASC", "pct_chg")),  # 跌幅最大 = 涨幅最小
            ("市值最小的", ("ASC", "market_cap")),
            ("PB最低的公司", ("ASC", "pb")),
        ]
        
        for query, (expected_order, expected_field) in test_cases:
            with self.subTest(query=query):
                params = self.extractor.extract_all_params(query)
                self.assertEqual(params.order_by, expected_order)
                self.assertEqual(params.order_field, expected_field)
    
    def test_market_cap_variants(self):
        """测试市值字段变体"""
        test_cases = [
            ("总市值最大", "market_cap"),
            ("流通市值最大", "circ_market_cap"),
            ("市值最大", "market_cap"),  # 默认总市值
        ]
        
        for query, expected_field in test_cases:
            with self.subTest(query=query):
                params = self.extractor.extract_all_params(query)
                self.assertEqual(params.order_field, expected_field)


class TestParameterExtractorConditionExtraction(unittest.TestCase):
    """条件提取相关测试"""
    
    def setUp(self):
        """测试初始化"""
        self.extractor = ParameterExtractor()
    
    def test_extract_exclude_st(self):
        """测试ST排除条件"""
        test_cases_true = [
            "排除ST的股票",
            "不含ST",
            "剔除ST股票",
            "去除ST",
            "排名前10，排除ST",
        ]
        
        test_cases_false = [
            "ST股票列表",
            "查询ST股票",
            "所有股票",
            "包含ST的排名",
        ]
        
        for query in test_cases_true:
            with self.subTest(query=query):
                params = self.extractor.extract_all_params(query)
                self.assertTrue(params.exclude_st)
        
        for query in test_cases_false:
            with self.subTest(query=query):
                params = self.extractor.extract_all_params(query)
                self.assertFalse(params.exclude_st)
    
    def test_extract_exclude_bj(self):
        """测试北交所排除条件"""
        test_cases_true = [
            "排除北交所的股票",
            "不含北交所",
            "剔除北交所股票",
            "排名前10，排除ST和北交所",
        ]
        
        test_cases_false = [
            "北交所股票列表",
            "查询北交所股票",
            "所有股票包括北交所",
        ]
        
        for query in test_cases_true:
            with self.subTest(query=query):
                params = self.extractor.extract_all_params(query)
                self.assertTrue(params.exclude_bj)
        
        for query in test_cases_false:
            with self.subTest(query=query):
                params = self.extractor.extract_all_params(query)
                self.assertFalse(params.exclude_bj)


class TestParameterExtractorSectorExtraction(unittest.TestCase):
    """板块和行业提取相关测试"""
    
    def setUp(self):
        """测试初始化"""
        self.extractor = ParameterExtractor()
    
    def test_extract_sector(self):
        """测试板块提取"""
        test_cases = [
            ("银行板块的数据", "银行"),
            ("新能源板块排名", "新能源"),
            ("白酒板块的龙头", "白酒"),
            ("科技板块分析", "科技"),
            ("医药板块的市值", "医药"),
        ]
        
        for query, expected_sector in test_cases:
            with self.subTest(query=query):
                params = self.extractor.extract_all_params(query)
                self.assertEqual(params.sector, expected_sector)
                self.assertIsNone(params.industry)  # 板块和行业应该互斥
    
    def test_extract_industry(self):
        """测试行业提取"""
        test_cases = [
            ("银行行业的数据", "银行"),
            ("新能源行业排名", "新能源"),
            ("白酒行业分析", "白酒"),
            ("互联网行业龙头", "互联网"),
        ]
        
        for query, expected_industry in test_cases:
            with self.subTest(query=query):
                params = self.extractor.extract_all_params(query)
                self.assertEqual(params.industry, expected_industry)
                self.assertIsNone(params.sector)  # 板块和行业应该互斥
    
    def test_concept_extraction(self):
        """测试概念提取"""
        test_cases = [
            ("人工智能概念股", "人工智能"),
            ("新能源概念", "新能源"),
            ("元宇宙概念股票", "元宇宙"),
        ]
        
        for query, expected_industry in test_cases:
            with self.subTest(query=query):
                params = self.extractor.extract_all_params(query)
                self.assertEqual(params.industry, expected_industry)


class TestParameterExtractorPeriodExtraction(unittest.TestCase):
    """报告期提取相关测试"""
    
    def setUp(self):
        """测试初始化"""
        self.extractor = ParameterExtractor()
    
    def test_extract_annual_report_period(self):
        """测试年报报告期提取"""
        test_cases = [
            ("2024年年报", "20241231"),
            ("2023年报", "20231231"),
            ("查询2025年年报数据", "20251231"),
        ]
        
        for query, expected_period in test_cases:
            with self.subTest(query=query):
                params = self.extractor.extract_all_params(query)
                self.assertEqual(params.period, expected_period)
    
    def test_extract_quarterly_report_period(self):
        """测试季报报告期提取"""
        test_cases = [
            ("2025年一季度", "20250331"),
            ("2024年二季报", "20240630"),
            ("2025年三季度报告", "20250930"),
            ("2024年四季度", "20241231"),
        ]
        
        for query, expected_period in test_cases:
            with self.subTest(query=query):
                params = self.extractor.extract_all_params(query)
                self.assertEqual(params.period, expected_period)
    
    def test_extract_interim_report_period(self):
        """测试中报报告期提取"""
        test_cases = [
            ("2024年中报", "20240630"),
            ("2025年半年报", "20250630"),
            ("查询2023年中报数据", "20230630"),
        ]
        
        for query, expected_period in test_cases:
            with self.subTest(query=query):
                params = self.extractor.extract_all_params(query)
                self.assertEqual(params.period, expected_period)
    
    def test_extract_specific_date_period(self):
        """测试具体日期格式的报告期"""
        test_cases = [
            ("20240331的财报", "20240331"),
            ("20241231财务数据", "20241231"),
        ]
        
        for query, expected_period in test_cases:
            with self.subTest(query=query):
                params = self.extractor.extract_all_params(query)
                self.assertEqual(params.period, expected_period)


class TestParameterExtractorComplexQueries(unittest.TestCase):
    """复杂查询测试"""
    
    def setUp(self):
        """测试初始化"""
        self.extractor = ParameterExtractor()
    
    def test_complex_stock_query(self):
        """测试复杂的股票查询"""
        query = "比较贵州茅台、五粮液和泸州老窖最近30天的走势，按涨幅降序排列"
        params = self.extractor.extract_all_params(query)
        
        self.assertEqual(len(params.stocks), 3)
        self.assertIn("600519.SH", params.stocks)
        self.assertIn("000858.SZ", params.stocks)
        self.assertIn("000568.SZ", params.stocks)
        self.assertIsNotNone(params.date_range)
        self.assertEqual(params.order_by, "DESC")
        self.assertEqual(params.order_field, "pct_chg")
    
    def test_complex_ranking_query(self):
        """测试复杂的排名查询"""
        query = "银行板块2024年年报净利润排名前20，排除ST"
        params = self.extractor.extract_all_params(query)
        
        self.assertEqual(params.sector, "银行")
        self.assertEqual(params.period, "20241231")
        self.assertEqual(params.limit, 20)
        self.assertTrue(params.exclude_st)
        self.assertEqual(params.order_by, "DESC")
        self.assertEqual(params.order_field, "n_income")
    
    def test_complex_financial_query(self):
        """测试复杂的财务查询"""
        query = "查询贵州茅台2023年到2024年的ROE变化趋势"
        params = self.extractor.extract_all_params(query)
        
        self.assertEqual(params.stocks, ["600519.SH"])
        # 这里可能需要特殊处理年份范围
        self.assertIsNotNone(params.raw_query)  # 至少原始查询应该被保存
    
    def test_ambiguous_query_handling(self):
        """测试歧义查询处理"""
        # 测试可能有歧义的查询
        test_cases = [
            # "平安"是简称，不支持
            ("平安的股价", None),  # 应该报错，提示使用完整名称
            
            # "建行"是简称，不支持
            ("建行的市值", None),  # 应该报错，提示使用完整名称
            
            # "招行"是简称，不支持
            ("招行的PE", None),  # 应该报错，提示使用完整名称
            
            # 数字可能是股票代码或数量
            ("000001", ["000001.SZ"]),  # 应该识别为股票代码
            ("前000001的股票", None),  # 这是错误的表达
        ]
        
        for query, expected_result in test_cases:
            with self.subTest(query=query):
                params = self.extractor.extract_all_params(query)
                if expected_result is None:
                    # 应该有错误或警告
                    self.assertTrue(params.error is not None or len(params.stocks) == 0)
                else:
                    self.assertEqual(params.stocks, expected_result)


class TestParameterExtractorMetricsExtraction(unittest.TestCase):
    """指标提取相关测试"""
    
    def setUp(self):
        """测试初始化"""
        self.extractor = ParameterExtractor()
    
    def test_extract_price_metrics(self):
        """测试价格相关指标提取"""
        query = "贵州茅台的开盘价、最高价、最低价和收盘价"
        params = self.extractor.extract_all_params(query)
        
        expected_metrics = ['open', 'high', 'low', 'close']
        for metric in expected_metrics:
            self.assertIn(metric, params.metrics)
    
    def test_extract_volume_metrics(self):
        """测试成交量相关指标提取"""
        query = "查询成交量和成交额"
        params = self.extractor.extract_all_params(query)
        
        self.assertIn('vol', params.metrics)
        self.assertIn('amount', params.metrics)
    
    def test_extract_financial_metrics(self):
        """测试财务指标提取"""
        query = "分析PE、PB和ROE"
        params = self.extractor.extract_all_params(query)
        
        self.assertIn('pe_ttm', params.metrics)
        self.assertIn('pb', params.metrics)
        self.assertIn('roe', params.metrics)


class TestParameterExtractorEdgeCases(unittest.TestCase):
    """边界情况测试"""
    
    def setUp(self):
        """测试初始化"""
        self.extractor = ParameterExtractor()
    
    def test_empty_query(self):
        """测试空查询"""
        test_cases = [
            "",
            "   ",
            "\n\t",
        ]
        
        for query in test_cases:
            with self.subTest(query=repr(query)):
                params = self.extractor.extract_all_params(query)
                # 应该返回默认值，不应该崩溃
                self.assertEqual(params.limit, 10)
                self.assertEqual(params.stocks, [])
    
    def test_special_characters(self):
        """测试特殊字符"""
        test_cases = [
            "贵州茅台（600519）的股价",  # 中文括号
            "查询600519.SH/贵州茅台",     # 斜杠
            "贵州茅台-白酒龙头",          # 连字符
            "贵州茅台:600519.SH",         # 冒号
        ]
        
        for query in test_cases:
            with self.subTest(query=query):
                params = self.extractor.extract_all_params(query)
                # 应该能正确提取股票
                self.assertEqual(params.stocks, ["600519.SH"])
    
    def test_mixed_language(self):
        """测试中英文混合"""
        test_cases = [
            ("查询TOP10股票", 10),
            ("PE最低的top20", 20),
            ("market cap最大的5只", 5),
        ]
        
        for query, expected_limit in test_cases:
            with self.subTest(query=query):
                params = self.extractor.extract_all_params(query)
                self.assertEqual(params.limit, expected_limit)
    
    def test_typos_and_variations(self):
        """测试拼写错误和变体"""
        test_cases = [
            ("贵州茅台股价", ["600519.SH"]),    # 没有"的"，但使用完整名称
            ("查贵州茅台", ["600519.SH"]),      # 简化表达，但使用完整名称
            ("茅台价格", []),                   # 使用简称（不支持）
            ("五粮液股价", ["000858.SZ"]),      # 完整名称
            ("宁德时代市值", ["300750.SZ"]),    # 完整名称
        ]
        
        for query, expected_stocks in test_cases:
            with self.subTest(query=query):
                params = self.extractor.extract_all_params(query)
                self.assertEqual(params.stocks, expected_stocks)


if __name__ == "__main__":
    # 运行测试
    unittest.main(verbosity=2)