#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
特殊股票名称提取测试
测试各种特殊格式的股票名称
"""

import unittest
import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.parameter_extractor import ParameterExtractor
from utils.unified_stock_validator import UnifiedStockValidator


class TestSpecialStockNames(unittest.TestCase):
    """特殊股票名称测试"""
    
    def setUp(self):
        """测试初始化"""
        self.extractor = ParameterExtractor()
        self.validator = UnifiedStockValidator()
    
    def test_extract_special_suffix_stocks(self):
        """测试带特殊后缀的股票提取"""
        test_cases = [
            # -U后缀
            ("埃夫特-U的股价", ["688165.SH"]),
            ("裕太微-U的市值", ["688515.SH"]),
            ("星环科技-U的财务", ["688031.SH"]),
            # -W后缀
            ("思特威-W的走势", ["688213.SH"]),
            # -UW后缀
            ("奥比中光-UW的成交量", ["688322.SH"]),
            # A/B后缀
            ("渝三峡A的涨跌", ["000565.SZ"]),
            ("万科A和南玻A", ["000002.SZ", "000012.SZ"]),
        ]
        
        for query, expected_stocks in test_cases:
            with self.subTest(query=query):
                params = self.extractor.extract_all_params(query)
                self.assertEqual(sorted(params.stocks), sorted(expected_stocks),
                               f"查询'{query}'应该提取到{expected_stocks}，实际: {params.stocks}")
    
    def test_extract_english_prefix_stocks(self):
        """测试英文前缀股票提取"""
        test_cases = [
            # 英文+中文组合
            ("GQY视讯的股价", ["300076.SZ"]),
            ("TCL科技的PE", ["000100.SZ"]),
            ("TCL智家的ROE", ["002668.SZ"]),
            ("TCL中环的市值", ["002129.SZ"]),
            # C开头
            ("C信通的财务", ["001388.SZ"]),
            # 多个TCL系列
            ("比较TCL科技、TCL智家和TCL中环", ["000100.SZ", "002668.SZ", "002129.SZ"]),
        ]
        
        for query, expected_stocks in test_cases:
            with self.subTest(query=query):
                params = self.extractor.extract_all_params(query)
                self.assertEqual(sorted(params.stocks), sorted(expected_stocks),
                               f"查询'{query}'应该提取到{expected_stocks}，实际: {params.stocks}")
    
    def test_extract_st_and_s_stocks(self):
        """测试ST/*ST/S/XD股票提取"""
        test_cases = [
            # ST股票
            ("ST葫芦娃的股价", ["605199.SH"]),
            ("ST新动力的市值", ["300152.SZ"]),
            # *ST股票
            ("*ST国华的财务", ["000004.SZ"]),
            # S股票
            ("S佳通的走势", ["600182.SH"]),
            # XD股票（临时除息标记，实际股票名称不含XD）
            ("国睿科技的股价", ["600562.SH"]),  # XD国睿科实际上是国睿科技
            ("常青股份的市值", ["603768.SH"]),  # XD常青股实际上是常青股份
            # 多个ST股票
            ("ST葫芦娃和ST新动力", ["605199.SH", "300152.SZ"]),
        ]
        
        for query, expected_stocks in test_cases:
            with self.subTest(query=query):
                params = self.extractor.extract_all_params(query)
                self.assertEqual(sorted(params.stocks), sorted(expected_stocks),
                               f"查询'{query}'应该提取到{expected_stocks}，实际: {params.stocks}")
    
    def test_extract_number_name_stocks(self):
        """测试数字名称股票提取"""
        test_cases = [
            # 中文数字股票
            ("三六零的股价", ["601360.SH"]),
            ("七一二的市值", ["603712.SH"]),
            ("六九一二的PE", ["301592.SZ"]),
            ("七匹狼的走势", ["002029.SZ"]),
            ("三人行的财务", ["605168.SH"]),
            ("三羊马的成交量", ["001317.SZ"]),
            ("三一重工的涨跌", ["600031.SH"]),
            # 多个数字股票
            ("比较三六零和七一二", ["601360.SH", "603712.SH"]),
        ]
        
        for query, expected_stocks in test_cases:
            with self.subTest(query=query):
                params = self.extractor.extract_all_params(query)
                self.assertEqual(sorted(params.stocks), sorted(expected_stocks),
                               f"查询'{query}'应该提取到{expected_stocks}，实际: {params.stocks}")
    
    def test_extract_common_prefix_stocks(self):
        """测试相同前缀股票提取"""
        test_cases = [
            # 大字开头
            ("大北农的股价", ["002385.SZ"]),
            ("大东方的市值", ["600327.SH"]),
            ("大东南的PE", ["002263.SZ"]),
            # 多个大字开头
            ("比较大北农、大东方和大东南", ["002385.SZ", "600327.SH", "002263.SZ"]),
            # 其他常见股票
            ("阿尔特的财务", ["300825.SZ"]),
            ("埃斯顿的走势", ["002747.SZ"]),
            ("艾力斯的成交量", ["688578.SH"]),
            ("白云山的涨跌", ["600332.SH"]),
            ("朱老六的股价", ["831726.BJ"]),
        ]
        
        for query, expected_stocks in test_cases:
            with self.subTest(query=query):
                params = self.extractor.extract_all_params(query)
                self.assertEqual(sorted(params.stocks), sorted(expected_stocks),
                               f"查询'{query}'应该提取到{expected_stocks}，实际: {params.stocks}")
    
    def test_complex_special_queries(self):
        """测试复杂的特殊股票组合查询"""
        test_cases = [
            # 混合不同类型
            ("比较TCL科技、ST葫芦娃和三六零", ["000100.SZ", "605199.SH", "601360.SH"]),
            ("分析埃夫特-U、思特威-W和奥比中光-UW", ["688165.SH", "688213.SH", "688322.SH"]),
            ("GQY视讯、七一二和大北农的对比", ["300076.SZ", "603712.SH", "002385.SZ"]),
            # 带日期的复杂查询
            ("TCL科技和TCL智家2025年一季度财务对比", ["000100.SZ", "002668.SZ"]),
            ("*ST国华、ST新动力最近30天的走势", ["000004.SZ", "300152.SZ"]),
        ]
        
        for query, expected_stocks in test_cases:
            with self.subTest(query=query):
                params = self.extractor.extract_all_params(query)
                self.assertEqual(sorted(params.stocks), sorted(expected_stocks),
                               f"查询'{query}'应该提取到{expected_stocks}，实际: {params.stocks}")
    
    def test_special_stock_validation(self):
        """测试特殊股票的验证功能"""
        test_cases = [
            # 测试各种格式的股票验证
            ("GQY视讯", True, "300076.SZ"),
            ("TCL科技", True, "000100.SZ"),
            ("埃夫特-U", True, "688165.SH"),
            ("思特威-W", True, "688213.SH"),
            ("奥比中光-UW", True, "688322.SH"),
            ("ST葫芦娃", True, "605199.SH"),
            ("*ST国华", True, "000004.SZ"),
            ("S佳通", True, "600182.SH"),
            ("三六零", True, "601360.SH"),
            ("七一二", True, "603712.SH"),
            # 错误的股票名称
            ("不存在的股票", False, None),
            ("XD国睿科", False, None),  # XD是临时标记，不应该在查询中使用
        ]
        
        for stock_name, should_succeed, expected_code in test_cases:
            with self.subTest(stock_name=stock_name):
                success, ts_code, error_response = self.validator.validate_and_extract(stock_name)
                self.assertEqual(success, should_succeed,
                               f"股票'{stock_name}'验证应该{'成功' if should_succeed else '失败'}")
                if should_succeed:
                    self.assertEqual(ts_code, expected_code,
                                   f"股票'{stock_name}'应该返回{expected_code}，实际: {ts_code}")


if __name__ == "__main__":
    unittest.main(verbosity=2)