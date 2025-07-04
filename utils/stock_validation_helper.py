#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
股票验证辅助模块
提供统一的股票验证和转换功能，确保所有Agent使用相同的验证逻辑
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from typing import Optional, Tuple, Dict, Any
from utils.unified_stock_validator import UnifiedStockValidator
from utils.stock_code_mapper import convert_to_ts_code, get_stock_name
from utils.logger import setup_logger

logger = setup_logger("stock_validation_helper")

# 创建全局验证器实例
validator = UnifiedStockValidator()

def validate_and_convert_stock(stock_input: str) -> Tuple[bool, Optional[str], Optional[str], Optional[str]]:
    """
    验证并转换股票输入
    
    Args:
        stock_input: 用户输入的股票信息（名称、代码等）
        
    Returns:
        Tuple[success, ts_code, stock_name, error_message]
        - success: 验证是否成功
        - ts_code: 成功时返回标准的ts_code格式
        - stock_name: 成功时返回股票名称
        - error_message: 失败时返回用户友好的错误信息
    """
    if not stock_input or not stock_input.strip():
        return False, None, None, "股票信息不能为空"
    
    stock_input = stock_input.strip()
    
    # 使用UnifiedStockValidator进行验证
    intent, result, detail = validator.parse_query_intent_and_extract_stock(stock_input)
    
    # 处理验证结果
    if result in ['INVALID_FORMAT', 'INVALID_CASE', 'INVALID_LENGTH', 'STOCK_NOT_EXISTS', 'USE_FULL_NAME', 'NOT_FOUND']:
        # 验证失败，返回错误信息
        error_response = validator.format_error_response(result, detail)
        error_message = error_response.get('error', '无法识别股票信息')
        logger.warning(f"股票验证失败: {stock_input} -> {error_message}")
        return False, None, None, error_message
    
    # 验证成功，result就是ts_code
    ts_code = result
    stock_name = get_stock_name(ts_code)
    
    logger.info(f"股票验证成功: {stock_input} -> {ts_code} ({stock_name})")
    return True, ts_code, stock_name, None

def validate_stock_list(stock_inputs: list) -> list:
    """
    批量验证股票列表
    
    Args:
        stock_inputs: 股票输入列表
        
    Returns:
        验证结果列表，每个元素为(success, ts_code, stock_name, error_message)
    """
    results = []
    for stock_input in stock_inputs:
        result = validate_and_convert_stock(stock_input)
        results.append(result)
    return results

def extract_and_validate_stock_from_entities(entities: list) -> Tuple[bool, Optional[str], Optional[str], Optional[str]]:
    """
    从entities列表中提取并验证第一个有效的股票
    
    Args:
        entities: 实体列表（可能包含股票和其他信息）
        
    Returns:
        Tuple[success, ts_code, stock_name, error_message]
    """
    if not entities:
        return False, None, None, "未提供股票信息"
    
    # 遍历entities，找到第一个可以成功验证的股票
    for entity in entities:
        if not entity or not isinstance(entity, str):
            continue
            
        # 跳过明显不是股票的实体（如日期）
        import re
        if re.match(r'^\d{4}-\d{2}-\d{2}$', entity.strip()):
            continue
            
        success, ts_code, stock_name, error_message = validate_and_convert_stock(entity)
        if success:
            return True, ts_code, stock_name, None
    
    # 如果所有entities都验证失败，返回第一个entity的错误信息
    if entities:
        _, _, _, error_message = validate_and_convert_stock(entities[0])
        return False, None, None, error_message
    
    return False, None, None, "未找到有效的股票信息"

# 测试代码
if __name__ == "__main__":
    # 测试用例
    test_cases = [
        "600519.SH",      # 正确格式
        "600519.sh",      # 大小写错误
        "600519",         # 缺少后缀
        "贵州茅台",       # 股票名称
        "茅台",           # 简称
        "999999.SH",      # 不存在的股票
        "",               # 空输入
        "abc",            # 无效输入
    ]
    
    print("股票验证测试")
    print("=" * 60)
    
    for test_input in test_cases:
        success, ts_code, stock_name, error_message = validate_and_convert_stock(test_input)
        if success:
            print(f"✅ '{test_input}' -> {ts_code} ({stock_name})")
        else:
            print(f"❌ '{test_input}' -> {error_message}")