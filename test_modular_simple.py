#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简单测试模块化Agent基本功能
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.parameter_extractor import ParameterExtractor
from utils.query_validator import QueryValidator
from utils.result_formatter import ResultFormatter, ResultType, TableData
from utils.error_handler import ErrorHandler
from utils.logger import setup_logger

logger = setup_logger("test_modular_simple")


def test_parameter_extractor():
    """测试参数提取器"""
    print("\n测试参数提取器...")
    extractor = ParameterExtractor()
    
    test_queries = [
        "贵州茅台的最新股价",
        "比较贵州茅台和五粮液的市值",
        "市值排名前10",
        "银行板块的主力资金",
        "最近30天的K线数据"
    ]
    
    for query in test_queries:
        print(f"\n查询: {query}")
        params = extractor.extract_all_params(query)
        print(f"  股票: {params.stocks}")
        print(f"  股票名称: {params.stock_names}")
        print(f"  日期: {params.date}")
        print(f"  数量限制: {params.limit}")
        print(f"  板块: {params.sector}")
        if params.error:
            print(f"  错误: {params.error}")


def test_query_validator():
    """测试查询验证器"""
    print("\n\n测试查询验证器...")
    validator = QueryValidator()
    extractor = ParameterExtractor()
    
    # 测试股票验证
    query = "ABC123的股价"  # 无效股票
    params = extractor.extract_all_params(query)
    errors = validator.validate_params(params)
    print(f"\n无效股票查询验证:")
    print(f"  查询: {query}")
    print(f"  验证错误: {errors}")
    
    # 测试日期验证
    query = "贵州茅台2025-13-45的股价"  # 无效日期
    params = extractor.extract_all_params(query)
    params.date = "2025-13-45"  # 手动设置无效日期
    errors = validator.validate_params(params)
    print(f"\n无效日期查询验证:")
    print(f"  查询: {query}")
    print(f"  验证错误: {errors}")


def test_result_formatter():
    """测试结果格式化器"""
    print("\n\n测试结果格式化器...")
    formatter = ResultFormatter()
    
    # 测试SQL结果格式化
    sql_result = [
        {"ts_code": "600519.SH", "name": "贵州茅台", "close": 1850.00, "pct_chg": 2.35},
        {"ts_code": "000858.SZ", "name": "五粮液", "close": 168.50, "pct_chg": 1.82}
    ]
    
    formatted = formatter.format_sql_result(sql_result, "price_query")
    print(f"\nSQL结果格式化:")
    print(f"  类型: {formatted.result_type}")
    print(f"  成功: {formatted.success}")
    if formatted.result_type == ResultType.TABLE and isinstance(formatted.data, TableData):
        print(f"  表格Markdown预览:")
        markdown_text = formatted.data.to_markdown()
        print(markdown_text[:200] + "..." if len(markdown_text) > 200 else markdown_text)


def test_error_handler():
    """测试错误处理器"""
    print("\n\n测试错误处理器...")
    handler = ErrorHandler()
    
    # 测试空输入错误
    error = ValueError("查询内容不能为空")
    error_info = handler.handle_error(error, "EMPTY_INPUT")
    print(f"\n空输入错误处理:")
    print(f"  用户消息: {error_info.user_message}")
    print(f"  建议: {error_info.suggestion}")
    print(f"  严重程度: {error_info.severity}")
    
    # 测试股票不存在错误
    error = ValueError("股票代码123456不存在")
    error_info = handler.handle_error(error, "STOCK_NOT_FOUND")
    print(f"\n股票不存在错误处理:")
    print(f"  用户消息: {error_info.user_message}")
    print(f"  建议: {error_info.suggestion}")


def main():
    """主测试函数"""
    print("="*60)
    print("模块化组件基础功能测试")
    print("="*60)
    
    try:
        test_parameter_extractor()
        test_query_validator()
        test_result_formatter()
        test_error_handler()
        
        print("\n\n" + "="*60)
        print("✅ 所有基础测试完成！")
        print("="*60)
        
    except Exception as e:
        print(f"\n❌ 测试失败: {str(e)}")
        logger.error("测试异常", exc_info=True)


if __name__ == "__main__":
    main()