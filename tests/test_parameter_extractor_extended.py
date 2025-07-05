#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
参数提取器扩展测试用例
根据设计原则和反馈补充的完整测试集
"""

import sys
import os
import unittest
from datetime import datetime, timedelta

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.parameter_extractor import ParameterExtractor, ExtractedParams


class TestStockExtractionExtended(unittest.TestCase):
    """股票提取扩展测试"""
    
    def setUp(self):
        """测试初始化"""
        self.extractor = ParameterExtractor()
    
    def test_extract_single_stock_with_code_extended(self):
        """测试股票代码提取 - 包含北交所"""
        test_cases = [
            # 主板
            ("600519的股价", ["600519.SH"]),
            ("000001最新价格", ["000001.SZ"]),
            # 中小板
            ("002594的市值", ["002594.SZ"]),
            # 创业板
            ("300750涨幅", ["300750.SZ"]),
            # 科创板
            ("688009的PE", ["688009.SH"]),
            # 北交所
            ("430047的成交量", ["430047.BJ"]),
            ("831726的市值", ["831726.BJ"]),
            ("920002的涨跌", ["920002.BJ"]),
        ]
        
        for query, expected_stocks in test_cases:
            with self.subTest(query=query):
                params = self.extractor.extract_all_params(query)
                self.assertEqual(params.stocks, expected_stocks)
    
    def test_extract_single_stock_with_full_code_all_exchanges(self):
        """测试完整股票代码提取 - 覆盖所有交易所"""
        test_cases = [
            # 上交所
            ("600519.SH的股价", ["600519.SH"]),
            ("688009.SH的市值", ["688009.SH"]),
            # 深交所
            ("000001.SZ最新价格", ["000001.SZ"]),
            ("002594.SZ的成交额", ["002594.SZ"]),
            ("300750.SZ的涨幅", ["300750.SZ"]),
            # 北交所
            ("430047.BJ的成交量", ["430047.BJ"]),
            ("831726.BJ的PE", ["831726.BJ"]),
        ]
        
        for query, expected_stocks in test_cases:
            with self.subTest(query=query):
                params = self.extractor.extract_all_params(query)
                self.assertEqual(params.stocks, expected_stocks)
    
    def test_extract_single_stock_with_name_extended(self):
        """测试股票名称提取 - 包含3字股票、ST和*ST"""
        test_cases = [
            # 正常名称
            ("贵州茅台的股价", ["600519.SH"]),
            ("平安银行最新价格", ["000001.SZ"]),
            # 三个字股票
            ("万科A的市值", ["000002.SZ"]),
            ("特力A的涨跌幅", ["000025.SZ"]),
            ("南玻A的成交量", ["000012.SZ"]),
            # ST股票
            ("ST特信的股价", ["000070.SZ"]),
            ("ST张家界的市值", ["000430.SZ"]),
            # *ST股票
            ("*ST国华的涨幅", ["000004.SZ"]),
            ("*ST生物的成交额", ["000504.SZ"]),
        ]
        
        for query, expected_stocks in test_cases:
            with self.subTest(query=query):
                params = self.extractor.extract_all_params(query)
                self.assertEqual(params.stocks, expected_stocks)
    
    def test_extract_multiple_stocks_all_connectors(self):
        """测试多股票提取 - 覆盖所有连接词"""
        test_cases = [
            # 和
            ("比较贵州茅台和五粮液", ["600519.SH", "000858.SZ"]),
            # 与
            ("贵州茅台与五粮液的对比", ["600519.SH", "000858.SZ"]),
            # 及
            ("分析贵州茅台及五粮液", ["600519.SH", "000858.SZ"]),
            # 顿号
            ("贵州茅台、五粮液、泸州老窖", ["600519.SH", "000858.SZ", "000568.SZ"]),
            # 逗号（中文）
            ("贵州茅台，五粮液", ["600519.SH", "000858.SZ"]),
            # 逗号（英文）
            ("贵州茅台,五粮液", ["600519.SH", "000858.SZ"]),
            # vs（小写）
            ("贵州茅台vs五粮液", ["600519.SH", "000858.SZ"]),
            # VS（大写）
            ("贵州茅台VS五粮液", ["600519.SH", "000858.SZ"]),
            # 空格
            ("贵州茅台 五粮液", ["600519.SH", "000858.SZ"]),
            # 混合连接词
            ("贵州茅台、五粮液和泸州老窖", ["600519.SH", "000858.SZ", "000568.SZ"]),
        ]
        
        for query, expected_stocks in test_cases:
            with self.subTest(query=query):
                params = self.extractor.extract_all_params(query)
                self.assertEqual(sorted(params.stocks), sorted(expected_stocks))
    
    def test_stock_error_messages_specific(self):
        """测试具体的错误信息指导"""
        test_cases = [
            # 大小写错误
            ("600519.sh的股价", "大小写错误", "应为.SH"),
            ("600519.Sh的市值", "大小写错误", "应为.SH"),
            ("000001.sz的走势", "大小写错误", "应为.SZ"),
            ("430047.bj的成交量", "大小写错误", "应为.BJ"),
            
            # 位数错误
            ("60051的股价", "位数", "6位"),
            ("00001的市值", "位数", "6位"),
            ("60051900的走势", "位数", "6位"),
            
            # 简称错误
            ("茅台的股价", "完整公司名称", "贵州茅台"),
            ("建行的PE", "完整公司名称", "建设银行"),
            ("招行的ROE", "完整公司名称", "招商银行"),
            ("中行的市值", "完整公司名称", "中国银行"),
            
            # 不存在的股票
            ("999999的股价", "不存在", None),
            ("123456的市值", "不存在", None),
        ]
        
        for query, error_type, expected_hint in test_cases:
            with self.subTest(query=query):
                params = self.extractor.extract_all_params(query)
                if error_type == "完整公司名称":
                    # 简称错误
                    self.assertIsNotNone(params.error)
                    self.assertIn("请使用完整公司名称", params.error)
                    if expected_hint:
                        self.assertIn(expected_hint, params.error)
                elif error_type == "大小写错误":
                    # 大小写错误
                    self.assertIsNotNone(params.error)
                    self.assertTrue(
                        any(keyword in params.error for keyword in ["大小写", expected_hint]),
                        f"错误信息应包含大小写提示，实际: {params.error}"
                    )
                elif error_type == "位数":
                    # 位数错误
                    self.assertIsNotNone(params.error)
                    self.assertIn(expected_hint, params.error)
                elif error_type == "不存在":
                    # 股票不存在
                    self.assertIsNotNone(params.error)
                    self.assertTrue(
                        any(keyword in params.error for keyword in ["不存在", "无法识别"]),
                        f"错误信息应提示股票不存在，实际: {params.error}"
                    )


class TestDateExtractionExtended(unittest.TestCase):
    """日期提取扩展测试"""
    
    def setUp(self):
        """测试初始化"""
        self.extractor = ParameterExtractor()
    
    def test_extract_relative_date_comprehensive(self):
        """测试相对日期提取 - 全面覆盖"""
        test_cases = [
            # 最新/最后相关
            "最新股价",
            "招商银行最后的价格",
            "最后一个交易日",
            "最近一个交易日的数据",
            
            # 前/上N个交易日
            "前1个交易日",
            "前5个交易日",
            "上3个交易日",
            "上10个交易日",
            
            # 今天、昨天等
            "今天的股价",
            "昨天的数据",
            "前天的行情",
            "大前天的走势",
            
            # 相对月份
            "上个月今天",
            "上上个月今天",
            "3个月前的今天",
            
            # 相对年份
            "去年今天",
            "前年今天",
            "3年前的今天",
            
            # N天/月/年前
            "5天前",
            "10天前的数据",
            "2个月前",
            "6个月前的股价",
            "广东宏大1年前的PE",
            "元隆雅图2年前的利润率数据",
        ]
        
        for query in test_cases:
            with self.subTest(query=query):
                params = self.extractor.extract_all_params(query)
                # 应该提取到日期
                self.assertIsNotNone(params.date, f"查询'{query}'应该提取到日期")
                # 验证日期格式
                self.assertRegex(params.date, r'^\d{4}-\d{2}-\d{2}$', 
                               f"日期格式应为YYYY-MM-DD，实际: {params.date}")
    
    def test_extract_date_range_comprehensive(self):
        """测试日期范围提取 - 全面覆盖"""
        test_cases = [
            # 从...到...格式
            ("从2025-01-01到2025-06-30", ("2025-01-01", "2025-06-30")),
            ("从2025年1月1日到2025年6月30日", ("2025-01-01", "2025-06-30")),
            
            # 至连接
            ("2025-01-01至2025-06-30", ("2025-01-01", "2025-06-30")),
            ("2025年1月1日至2025年6月30日", ("2025-01-01", "2025-06-30")),
            
            # -连接
            ("2025-01-01-2025-06-30", ("2025-01-01", "2025-06-30")),
            
            # ~连接
            ("2025-01-01~2025-06-30", ("2025-01-01", "2025-06-30")),
            
            # /连接
            ("2025/01/01-2025/06/30", ("2025-01-01", "2025-06-30")),
            ("2025/01/01~2025/06/30", ("2025-01-01", "2025-06-30")),
        ]
        
        for query, expected_range in test_cases:
            with self.subTest(query=query):
                params = self.extractor.extract_all_params(query)
                self.assertEqual(params.date_range, expected_range)
    
    def test_extract_relative_date_range(self):
        """测试相对日期范围提取"""
        test_cases = [
            # 最近N天/周/月/年
            "最近5天",
            "最近1周",
            "最近7天",
            "最近1个月",
            "最近30天",
            "最近3个月",
            "最近90天",
            "最近1年",
            "最近365天",
            
            # 前N天/周/月/年
            "前5天",
            "前1周",
            "前7天",
            "前1个月",
            "前30天",
            "前3个月",
            "前90天",
            "前1年",
            "前365天",
            
            # 过去N天/周/月/年
            "过去5天",
            "过去一周",
            "过去一个月",
            "过去三个月",
            "过去半年",
            "过去一年",
        ]
        
        for query in test_cases:
            with self.subTest(query=query):
                params = self.extractor.extract_all_params(query)
                # 应该提取到日期范围
                self.assertIsNotNone(params.date_range, f"查询'{query}'应该提取到日期范围")
                # 验证是元组
                self.assertIsInstance(params.date_range, tuple)
                self.assertEqual(len(params.date_range), 2)
                # 验证日期格式
                self.assertRegex(params.date_range[0], r'^\d{4}-\d{2}-\d{2}$')
                self.assertRegex(params.date_range[1], r'^\d{4}-\d{2}-\d{2}$')
    
    def test_extract_month_year_range(self):
        """测试月份和年份范围提取"""
        test_cases = [
            # 单月
            ("1月的数据", None),  # 需要年份上下文
            ("2025年1月的数据", ("2025-01-01", "2025-01-31")),
            
            # 月份范围
            ("1月到3月", None),  # 需要年份上下文
            ("2025年1月到3月", ("2025-01-01", "2025-03-31")),
            ("2025年1月到2025年3月", ("2025-01-01", "2025-03-31")),
            
            # 跨年月份范围
            ("2024年10月到2025年3月", ("2024-10-01", "2025-03-31")),
            
            # 年份
            ("2024年的数据", ("2024-01-01", "2024-12-31")),
            
            # 年份范围
            ("2023年到2024年", ("2023-01-01", "2024-12-31")),
            ("2023到2024", ("2023-01-01", "2024-12-31")),
        ]
        
        for query, expected_range in test_cases:
            with self.subTest(query=query):
                params = self.extractor.extract_all_params(query)
                if expected_range:
                    self.assertEqual(params.date_range, expected_range)
                else:
                    # 某些查询可能无法提取范围
                    pass


class TestLimitExtractionExtended(unittest.TestCase):
    """数量限制提取扩展测试"""
    
    def setUp(self):
        """测试初始化"""
        self.extractor = ParameterExtractor()
    
    def test_extract_limit_variations(self):
        """测试各种数量表达方式"""
        test_cases = [
            # 前N格式
            ("前5的股票", 5),
            ("前10只股票", 10),
            ("前20名", 20),
            ("前100家公司", 100),
            
            # TOP N格式
            ("TOP10", 10),
            ("top20", 20),
            ("Top 50", 50),
            
            # 最X的N只
            ("最大的5只", 5),
            ("最高的10只股票", 10),
            ("涨幅最大的20只", 20),
            
            # 排名前N
            ("排名前10", 10),
            ("排行前20", 20),
            ("位列前50", 50),
            
            # 中文数字
            ("前五", 5),
            ("前十", 10),
            ("前二十", 20),
            ("前三十", 30),
            ("前五十", 50),
            ("前一百", 100),
            
            # 混合表达
            ("市值最大的前十只股票", 10),
            ("涨幅排名前二十的公司", 20),
        ]
        
        for query, expected_limit in test_cases:
            with self.subTest(query=query):
                params = self.extractor.extract_all_params(query)
                self.assertEqual(params.limit, expected_limit)


class TestOrderExtractionExtended(unittest.TestCase):
    """排序参数提取扩展测试"""
    
    def setUp(self):
        """测试初始化"""
        self.extractor = ParameterExtractor()
    
    def test_extract_order_comprehensive(self):
        """测试全面的排序参数提取"""
        test_cases = [
            # 降序关键词
            ("市值最大的股票", ("DESC", "market_cap")),
            ("涨幅最高的", ("DESC", "pct_chg")),
            ("成交额最多的", ("DESC", "amount")),
            ("ROE最高的公司", ("DESC", "roe")),
            ("利润最多的", ("DESC", "n_income")),
            ("营收最大的", ("DESC", "total_revenue")),
            ("PE最高的", ("DESC", "pe_ttm")),
            
            # 升序关键词
            ("PE最低的股票", ("ASC", "pe_ttm")),
            ("PB最小的", ("ASC", "pb")),
            ("市值最小的公司", ("ASC", "market_cap")),
            ("跌幅最大的", ("ASC", "pct_chg")),
            
            # 特殊排序逻辑
            ("涨幅榜", ("DESC", "pct_chg")),
            ("跌幅榜", ("ASC", "pct_chg")),
            
            # 从高到低/从低到高
            ("按市值从高到低", ("DESC", "market_cap")),
            ("按PE从低到高", ("ASC", "pe_ttm")),
            
            # 总市值vs流通市值
            ("总市值最大", ("DESC", "market_cap")),
            ("流通市值最大", ("DESC", "circ_market_cap")),
            
            # 其他指标
            ("换手率最高", ("DESC", "turnover_rate")),
            ("成交量最大", ("DESC", "vol")),
        ]
        
        for query, (expected_order, expected_field) in test_cases:
            with self.subTest(query=query):
                params = self.extractor.extract_all_params(query)
                self.assertEqual(params.order_by, expected_order)
                self.assertEqual(params.order_field, expected_field)


class TestConditionExtractionExtended(unittest.TestCase):
    """条件提取扩展测试"""
    
    def setUp(self):
        """测试初始化"""
        self.extractor = ParameterExtractor()
    
    def test_exclude_conditions_comprehensive(self):
        """测试全面的排除条件"""
        test_cases = [
            # ST排除
            ("排除ST的股票", {"exclude_st": True, "exclude_bj": False}),
            ("不含ST", {"exclude_st": True, "exclude_bj": False}),
            ("剔除ST股票", {"exclude_st": True, "exclude_bj": False}),
            ("去除ST", {"exclude_st": True, "exclude_bj": False}),
            ("非ST股票", {"exclude_st": True, "exclude_bj": False}),
            ("排除*ST和ST", {"exclude_st": True, "exclude_bj": False}),
            
            # 北交所排除
            ("排除北交所的股票", {"exclude_st": False, "exclude_bj": True}),
            ("不含北交所", {"exclude_st": False, "exclude_bj": True}),
            ("剔除北交所股票", {"exclude_st": False, "exclude_bj": True}),
            ("去除北交所", {"exclude_st": False, "exclude_bj": True}),
            ("非北交所股票", {"exclude_st": False, "exclude_bj": True}),
            
            # 同时排除
            ("排除ST和北交所", {"exclude_st": True, "exclude_bj": True}),
            ("不含ST和北交所股票", {"exclude_st": True, "exclude_bj": True}),
            
            # 不应该触发排除的情况
            ("ST股票列表", {"exclude_st": False, "exclude_bj": False}),
            ("北交所股票排名", {"exclude_st": False, "exclude_bj": False}),
            ("查询ST股票", {"exclude_st": False, "exclude_bj": False}),
        ]
        
        for query, expected_conditions in test_cases:
            with self.subTest(query=query):
                params = self.extractor.extract_all_params(query)
                self.assertEqual(params.exclude_st, expected_conditions["exclude_st"])
                self.assertEqual(params.exclude_bj, expected_conditions["exclude_bj"])


class TestSectorExtractionExtended(unittest.TestCase):
    """板块和行业提取扩展测试"""
    
    def setUp(self):
        """测试初始化"""
        self.extractor = ParameterExtractor()
    
    def test_extract_sector_comprehensive(self):
        """测试板块提取 - 需要验证是否能映射到板块代码"""
        test_cases = [
            # 板块
            ("银行板块的数据", "银行"),
            ("新能源板块排名", "新能源"),
            ("白酒板块的龙头", "白酒"),
            ("科技板块分析", "科技"),
            ("医药板块的市值", "医药"),
            ("半导体板块", "半导体"),
            ("汽车板块的资金流向", "汽车"),
            
            # 行业
            ("银行行业的数据", "银行"),
            ("互联网行业分析", "互联网"),
            ("软件开发行业", "软件开发"),
            
            # 概念
            ("人工智能概念股", "人工智能"),
            ("新能源概念", "新能源"),
            ("元宇宙概念股票", "元宇宙"),
            ("碳中和概念", "碳中和"),
        ]
        
        for query, expected_sector_name in test_cases:
            with self.subTest(query=query):
                params = self.extractor.extract_all_params(query)
                if "板块" in query:
                    self.assertEqual(params.sector, expected_sector_name)
                    self.assertIsNone(params.industry)
                else:
                    self.assertEqual(params.industry, expected_sector_name)
                    self.assertIsNone(params.sector)


class TestPeriodExtractionExtended(unittest.TestCase):
    """报告期提取扩展测试"""
    
    def setUp(self):
        """测试初始化"""
        self.extractor = ParameterExtractor()
    
    def test_extract_period_comprehensive(self):
        """测试全面的报告期提取"""
        test_cases = [
            # 年报
            ("2024年年报", "20241231"),
            ("2024年报", "20241231"),
            ("2023年度报告", "20231231"),
            ("2023年全年", "20231231"),
            
            # 季报
            ("2025年一季度", "20250331"),
            ("2025年一季报", "20250331"),
            ("2025年第一季度", "20250331"),
            ("2025年Q1", "20250331"),
            ("2024年二季度", "20240630"),
            ("2024年二季报", "20240630"),
            ("2024年三季度", "20240930"),
            ("2024年三季报", "20240930"),
            ("2024年四季度", "20241231"),
            ("2024年四季报", "20241231"),
            
            # 中报/半年报
            ("2024年中报", "20240630"),
            ("2024年半年报", "20240630"),
            ("2024年中期报告", "20240630"),
            ("2024年上半年", "20240630"),
            
            # 直接日期格式
            ("20240331的财报", "20240331"),
            ("20241231财务数据", "20241231"),
            
            # 最新报告期（相对表达）
            ("最新财报", None),  # 需要动态确定
            ("最新年报", None),  # 需要动态确定
            ("最新季报", None),  # 需要动态确定
        ]
        
        for query, expected_period in test_cases:
            with self.subTest(query=query):
                params = self.extractor.extract_all_params(query)
                if expected_period:
                    self.assertEqual(params.period, expected_period)
                # 对于需要动态确定的，只要不报错即可


class TestComplexQueriesExtended(unittest.TestCase):
    """复杂查询扩展测试"""
    
    def setUp(self):
        """测试初始化"""
        self.extractor = ParameterExtractor()
    
    def test_complex_mixed_queries(self):
        """测试复杂的混合查询"""
        test_cases = [
            {
                "query": "比较贵州茅台、五粮液和泸州老窖最近30天的走势，按涨幅降序排列，排除ST",
                "expected": {
                    "stocks": ["600519.SH", "000858.SZ", "000568.SZ"],
                    "has_date_range": True,
                    "order_by": "DESC",
                    "order_field": "pct_chg",
                    "exclude_st": True
                }
            },
            {
                "query": "银行板块2024年年报净利润排名前20，排除ST和北交所",
                "expected": {
                    "sector": "银行",
                    "period": "20241231",
                    "limit": 20,
                    "order_by": "DESC",
                    "order_field": "n_income",
                    "exclude_st": True,
                    "exclude_bj": True
                }
            },
            {
                "query": "查询*ST国华和ST特信2025年一季度的财务数据",
                "expected": {
                    "stocks": ["000004.SZ", "000070.SZ"],
                    "period": "20250331"
                }
            },
            {
                "query": "分析万科A、南玻A、特力A从2024年10月到2025年3月的ROE变化",
                "expected": {
                    "stocks": ["000002.SZ", "000012.SZ", "000025.SZ"],
                    "date_range": ("2024-10-01", "2025-03-31"),
                    "metrics": ["roe"]
                }
            }
        ]
        
        for test_case in test_cases:
            query = test_case["query"]
            expected = test_case["expected"]
            
            with self.subTest(query=query):
                params = self.extractor.extract_all_params(query)
                
                # 验证股票
                if "stocks" in expected:
                    self.assertEqual(sorted(params.stocks), sorted(expected["stocks"]))
                
                # 验证日期范围
                if "has_date_range" in expected and expected["has_date_range"]:
                    self.assertIsNotNone(params.date_range)
                elif "date_range" in expected:
                    self.assertEqual(params.date_range, expected["date_range"])
                
                # 验证其他参数
                for key in ["sector", "period", "limit", "order_by", "order_field", 
                           "exclude_st", "exclude_bj"]:
                    if key in expected:
                        self.assertEqual(getattr(params, key), expected[key])
                
                # 验证指标
                if "metrics" in expected:
                    for metric in expected["metrics"]:
                        self.assertIn(metric, params.metrics)


if __name__ == "__main__":
    # 运行测试
    unittest.main(verbosity=2)