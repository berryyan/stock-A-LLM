#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
结果处理模块集成测试
测试结果格式化和错误处理的完整流程
"""

import sys
import os
import unittest
from datetime import datetime

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.result_formatter import (
    ResultFormatter, FormattedResult, TableData, ResultType,
    format_sql_result, format_rag_result, format_financial_result, format_error
)
from utils.error_handler import (
    ErrorHandler, ErrorInfo, ErrorCategory, ErrorSeverity,
    handle_error, get_user_friendly_message, format_error_response,
    InputError, ValidationError, handle_query_errors
)


class TestResultFormatter(unittest.TestCase):
    """结果格式化器测试"""
    
    def setUp(self):
        """测试初始化"""
        self.formatter = ResultFormatter()
    
    def test_format_sql_result_with_data(self):
        """测试有数据的SQL结果格式化"""
        # 准备测试数据
        sql_data = [
            {
                "ts_code": "600519.SH",
                "name": "贵州茅台",
                "close": 1800.5,
                "pct_chg": 2.35,
                "amount": 5678900000,
                "trade_date": datetime(2025, 7, 4)
            },
            {
                "ts_code": "000858.SZ",
                "name": "五粮液",
                "close": 165.8,
                "pct_chg": -1.23,
                "amount": 2345600000,
                "trade_date": datetime(2025, 7, 4)
            }
        ]
        
        # 格式化结果
        result = format_sql_result(sql_data, "stock_price")
        
        # 验证结果
        self.assertTrue(result.success)
        self.assertEqual(result.result_type, ResultType.TABLE)
        self.assertIsInstance(result.data, TableData)
        self.assertEqual(len(result.data.rows), 2)
        self.assertEqual(result.data.total_count, 2)
        
        # 验证Markdown表格
        markdown = result.data.to_markdown()
        self.assertIn("贵州茅台", markdown)
        self.assertIn("1,800.50", markdown)  # 测试千分符
        self.assertIn("2.35%", markdown)     # 测试百分比
        
    def test_format_sql_result_empty(self):
        """测试空SQL结果格式化"""
        result = format_sql_result([], "stock_price")
        
        self.assertTrue(result.success)
        self.assertEqual(result.result_type, ResultType.TEXT)
        self.assertEqual(result.data, "查询无结果")
        
    def test_format_rag_result(self):
        """测试RAG结果格式化"""
        # 准备测试数据
        documents = [
            {
                "title": "2024年年度报告",
                "stock_name": "贵州茅台",
                "ts_code": "600519.SH",
                "date": "2024-03-15",
                "score": 0.95,
                "content": "公司2024年实现营业收入1500亿元，同比增长15%..."
            },
            {
                "title": "2024年一季度报告",
                "stock_name": "贵州茅台",
                "ts_code": "600519.SH",
                "date": "2024-04-20",
                "score": 0.88,
                "content": "一季度业绩表现良好，营收同比增长18%..."
            }
        ]
        answer = "根据财报显示，贵州茅台2024年业绩表现优异，营收和利润均实现双位数增长。"
        
        # 格式化结果
        result = format_rag_result(documents, answer)
        
        # 验证结果
        self.assertTrue(result.success)
        self.assertEqual(result.result_type, ResultType.TEXT)
        self.assertIn("根据财报显示", result.data)
        self.assertIn("2024年年度报告", result.data)
        self.assertIn("相关度：0.95", result.data)
        self.assertEqual(result.metadata["document_count"], 2)
        
    def test_format_financial_result(self):
        """测试财务分析结果格式化"""
        # 准备测试数据
        analysis = {
            "title": "贵州茅台财务健康度分析",
            "analysis_type": "financial_health",
            "stock_info": {
                "name": "贵州茅台",
                "code": "600519.SH",
                "period": "2024年年报"
            },
            "key_metrics": {
                "ROE": "28.5%",
                "净利润率": "51.2%",
                "资产负债率": "23.8%",
                "流动比率": "4.2"
            },
            "analysis_content": "公司财务状况非常健康，盈利能力强劲...",
            "conclusion": "公司财务健康度评级：AAA",
            "suggestions": [
                "继续保持稳健的财务政策",
                "适度提高分红比例回馈投资者",
                "关注市场变化，保持竞争优势"
            ]
        }
        
        # 格式化结果
        result = format_financial_result(analysis)
        
        # 验证结果
        self.assertTrue(result.success)
        self.assertEqual(result.result_type, ResultType.TEXT)
        self.assertIn("贵州茅台财务健康度分析", result.data)
        self.assertIn("ROE", result.data)
        self.assertIn("AAA", result.data)
        self.assertTrue(result.metadata["has_suggestions"])
        
    def test_column_type_formatting(self):
        """测试不同列类型的格式化"""
        # 创建包含各种类型数据的表格
        table = TableData(
            headers=["股票", "价格", "涨幅", "成交额", "日期"],
            rows=[
                ["贵州茅台", 1800.5, 2.35, 5678900000, datetime(2025, 7, 4)],
                ["五粮液", 165.8, -1.23, 234560000, datetime(2025, 7, 4)]
            ],
            column_types={
                "价格": "number",
                "涨幅": "percent",
                "成交额": "money",
                "日期": "date"
            }
        )
        
        markdown = table.to_markdown()
        
        # 验证格式化效果
        self.assertIn("1,800.50", markdown)    # 数字格式
        self.assertIn("2.35%", markdown)       # 百分比格式
        self.assertIn("56.79亿", markdown)     # 金额格式（亿）
        self.assertIn("2.35亿", markdown)      # 金额格式（亿）
        self.assertIn("2025-07-04", markdown)  # 日期格式


class TestErrorHandler(unittest.TestCase):
    """错误处理器测试"""
    
    def setUp(self):
        """测试初始化"""
        self.handler = ErrorHandler(debug_mode=True)
    
    def test_handle_known_error(self):
        """测试已知错误处理"""
        # 测试股票格式错误
        error_info = handle_error("格式错误", "INVALID_STOCK_FORMAT", 
                                 {"invalid_value": "600519.sh"})
        
        self.assertEqual(error_info.error_code, "INVALID_STOCK_FORMAT")
        self.assertEqual(error_info.category, ErrorCategory.INPUT_ERROR)
        self.assertEqual(error_info.severity, ErrorSeverity.LOW)
        self.assertIsNotNone(error_info.suggestion)
        
        # 获取用户友好消息
        user_msg = get_user_friendly_message(error_info)
        self.assertIn("股票代码格式不正确", user_msg)
        self.assertIn("建议", user_msg)
        
    def test_handle_unknown_error(self):
        """测试未知错误处理"""
        error_info = handle_error("未知错误", "UNKNOWN_CODE")
        
        self.assertEqual(error_info.error_code, "UNKNOWN_CODE")
        self.assertEqual(error_info.category, ErrorCategory.UNKNOWN_ERROR)
        self.assertEqual(error_info.severity, ErrorSeverity.HIGH)
        
    def test_handle_exception(self):
        """测试异常处理"""
        try:
            raise ValueError("测试异常")
        except Exception as e:
            # 使用实例的handler（调试模式）
            error_info = self.handler.handle_error(e, "INTERNAL_ERROR")
            
        self.assertEqual(error_info.error_code, "INTERNAL_ERROR")
        self.assertIsNotNone(error_info.traceback)  # 调试模式下应该有堆栈信息
        
    def test_error_response_formatting(self):
        """测试错误响应格式化"""
        error_info = ErrorInfo(
            error_code="USE_FULL_NAME",
            error_message="需要使用完整公司名称",
            user_message="请使用完整的公司名称",
            category=ErrorCategory.INPUT_ERROR,
            severity=ErrorSeverity.LOW,
            suggestion="系统不支持股票简称，请使用完整的公司名称，如：贵州茅台",
            details={"input": "茅台"}
        )
        
        response = format_error_response(error_info)
        
        self.assertFalse(response.success)
        self.assertEqual(response.result_type, ResultType.ERROR)
        self.assertIn("请使用完整的公司名称", response.data)
        self.assertEqual(response.metadata["error_code"], "USE_FULL_NAME")
        
    def test_query_error_decorator(self):
        """测试查询错误装饰器"""
        @handle_query_errors
        def test_query_success():
            return FormattedResult(
                success=True,
                result_type=ResultType.TEXT,
                data="查询成功"
            )
        
        @handle_query_errors
        def test_query_fail():
            raise InputError("股票不存在", "STOCK_NOT_EXISTS", 
                           {"stock": "999999"})
        
        # 测试成功情况
        result1 = test_query_success()
        self.assertTrue(result1.success)
        
        # 测试失败情况
        result2 = test_query_fail()
        self.assertFalse(result2.success)
        self.assertEqual(result2.result_type, ResultType.ERROR)
        self.assertEqual(result2.metadata["error_code"], "STOCK_NOT_EXISTS")


class TestIntegration(unittest.TestCase):
    """集成测试"""
    
    def test_complete_flow_success(self):
        """测试完整的成功流程"""
        # 模拟查询成功并格式化结果
        sql_data = [
            {"ts_code": "600519.SH", "name": "贵州茅台", "close": 1800.5}
        ]
        
        result = format_sql_result(sql_data)
        
        # 验证结果
        self.assertTrue(result.success)
        self.assertEqual(result.result_type, ResultType.TABLE)
        
        # 转换为字典和JSON
        result_dict = result.to_dict()
        self.assertIn("headers", result_dict["data"])
        self.assertIn("rows", result_dict["data"])
        self.assertIn("markdown", result_dict)
        
        result_json = result.to_json()
        self.assertIsInstance(result_json, str)
        self.assertIn("600519.SH", result_json)
        
    def test_complete_flow_error(self):
        """测试完整的错误流程"""
        # 模拟错误处理
        try:
            # 模拟输入验证失败
            raise ValidationError("日期格式错误", "INVALID_DATE_FORMAT",
                                {"input": "2025-13-45", "expected": "YYYY-MM-DD"})
        except Exception as e:
            # 处理错误
            error_info = handle_error(e, e.error_code, e.details)
            
            # 格式化错误响应
            result = format_error_response(error_info)
            
        # 验证结果
        self.assertFalse(result.success)
        self.assertEqual(result.result_type, ResultType.ERROR)
        self.assertIn("日期格式不正确", result.data)
        self.assertEqual(result.metadata["error_code"], "INVALID_DATE_FORMAT")
        
        # 转换为JSON
        result_json = result.to_json()
        self.assertIn("INVALID_DATE_FORMAT", result_json)
        
    def test_error_categories(self):
        """测试不同类别的错误处理"""
        error_codes = [
            ("EMPTY_QUERY", ErrorCategory.INPUT_ERROR),
            ("INVALID_DATE_FORMAT", ErrorCategory.VALIDATION_ERROR),
            ("DATABASE_CONNECTION_ERROR", ErrorCategory.DATABASE_ERROR),
            ("LLM_ERROR", ErrorCategory.PROCESSING_ERROR),
            ("INTERNAL_ERROR", ErrorCategory.SYSTEM_ERROR)
        ]
        
        for error_code, expected_category in error_codes:
            with self.subTest(error_code=error_code):
                error_info = handle_error(f"测试{error_code}", error_code)
                self.assertEqual(error_info.category, expected_category)


if __name__ == "__main__":
    # 运行测试
    unittest.main(verbosity=2)