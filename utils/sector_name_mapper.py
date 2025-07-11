#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
板块名称映射工具
根据设计原则：板块只接受完整板块名称和板块代码，不接受任何简称和昵称
这个模块仅用于处理用户输入中的"板块"、"行业"、"概念"后缀问题
"""

import logging
from typing import Optional, Dict, List
from functools import lru_cache

logger = logging.getLogger(__name__)

# 从money_flow_config导入板块名称标准化映射
try:
    from utils.money_flow_config import SECTOR_NAME_NORMALIZATION
except ImportError:
    SECTOR_NAME_NORMALIZATION = {}


@lru_cache(maxsize=512)
def map_sector_name(user_input: str) -> Optional[str]:
    """
    处理板块名称
    1. 首先检查是否有标准化映射（如"地产"→"房地产板块"）
    2. 如果没有映射，则去除"板块"、"行业"、"概念"等后缀
    
    Args:
        user_input: 用户输入的板块名称
        
    Returns:
        处理后的板块名称，如果无需处理则返回None
    """
    if not user_input:
        return None
    
    # 首先检查是否有标准化映射
    if user_input in SECTOR_NAME_NORMALIZATION:
        mapped = SECTOR_NAME_NORMALIZATION[user_input]
        logger.debug(f"板块名称标准化：{user_input} -> {mapped}")
        return mapped
    
    # 对于已经有"板块"后缀的，直接返回去除后缀的名称
    # 例如："银行板块" -> "银行"
    if user_input.endswith("板块"):
        cleaned = user_input[:-2]
        logger.debug(f"去除'板块'后缀：{user_input} -> {cleaned}")
        return cleaned
    
    # 去除其他常见后缀
    suffixes = ["行业", "概念", "类", "业"]
    
    for suffix in suffixes:
        if user_input.endswith(suffix):
            # 去除后缀
            cleaned = user_input[:-len(suffix)]
            logger.debug(f"去除后缀 '{suffix}'：{user_input} -> {cleaned}")
            return cleaned
    
    # 如果没有需要去除的后缀，返回None表示无需处理
    return None


def get_all_mappings() -> Dict[str, str]:
    """
    获取所有映射关系
    由于不再做简称映射，这个函数返回空字典
    """
    return {}


def search_sector_names(keyword: str) -> List[str]:
    """
    搜索包含关键词的板块名称
    由于不再维护映射表，这个功能应该通过数据库查询实现
    """
    logger.warning("search_sector_names已弃用，请使用SectorCodeMapper的搜索功能")
    return []


# 测试代码
if __name__ == "__main__":
    # 测试用例
    test_cases = [
        "银行板块",
        "白酒板块", 
        "银行",
        "白酒",
        "新能源板块",
        "酿酒行业",
        "5G概念"
    ]
    
    print("板块名称处理测试")
    print("=" * 50)
    
    for test in test_cases:
        result = map_sector_name(test)
        if result:
            print(f"{test} -> {result}")
        else:
            print(f"{test} -> 无需处理")