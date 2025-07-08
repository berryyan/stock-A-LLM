#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
板块名称映射工具
将用户输入的板块简称映射到数据库中的完整板块名称
"""

import logging
from typing import Optional, Dict, List
from functools import lru_cache

logger = logging.getLogger(__name__)

# 板块名称映射表
SECTOR_NAME_MAPPING = {
    # 房地产相关
    "房地产": "房地产开发",
    "地产": "房地产开发",
    "房产": "房地产开发",
    "房地产板块": "房地产开发",
    "地产板块": "房地产开发",
    "房地产开发板块": "房地产开发",
    
    # 银行相关
    "银行": "银行",
    "银行板块": "银行",
    "银行业": "银行",
    
    # 证券相关
    "证券": "证券",
    "券商": "证券",
    "证券板块": "证券",
    "券商板块": "证券",
    
    # 保险相关
    "保险": "保险",
    "保险板块": "保险",
    "保险业": "保险",
    
    # 白酒相关
    "白酒": "白酒",
    "酒类": "白酒",
    "白酒板块": "白酒",
    "酿酒": "白酒",
    
    # 医药相关
    "医药": "医药生物",
    "医药板块": "医药生物",
    "生物医药": "医药生物",
    "医药生物板块": "医药生物",
    
    # 新能源相关
    "新能源": "新能源",
    "新能源板块": "新能源",
    "新能源车": "新能源车",
    "新能源汽车": "新能源车",
    
    # 半导体相关
    "半导体": "半导体",
    "芯片": "半导体",
    "半导体板块": "半导体",
    "芯片板块": "半导体",
    
    # 钢铁相关
    "钢铁": "钢铁",
    "钢铁板块": "钢铁",
    "钢铁行业": "钢铁",
    
    # 煤炭相关
    "煤炭": "煤炭",
    "煤炭板块": "煤炭",
    "煤炭行业": "煤炭",
    
    # 有色金属相关
    "有色": "有色金属",
    "有色板块": "有色金属",
    "有色金属板块": "有色金属",
    
    # 汽车相关
    "汽车": "汽车",
    "汽车板块": "汽车",
    "汽车行业": "汽车",
    "汽车整车": "汽车整车",
    
    # 家电相关
    "家电": "家用电器",
    "家电板块": "家用电器",
    "家用电器板块": "家用电器",
    
    # 食品饮料相关
    "食品": "食品饮料",
    "饮料": "食品饮料",
    "食品饮料板块": "食品饮料",
    
    # 建筑相关
    "建筑": "建筑装饰",
    "建筑板块": "建筑装饰",
    "建筑装饰板块": "建筑装饰",
    "建材": "建筑材料",
    "建材板块": "建筑材料",
    
    # 电力相关
    "电力": "电力",
    "电力板块": "电力",
    "电力行业": "电力",
    
    # 交通运输相关
    "交通": "交通运输",
    "运输": "交通运输",
    "交通运输板块": "交通运输",
    "航空": "航空运输",
    "航运": "航运港口",
    
    # 通信相关
    "通信": "通信",
    "通讯": "通信",
    "通信板块": "通信",
    "5G": "5G概念",
    
    # 计算机相关
    "计算机": "计算机",
    "软件": "软件服务",
    "IT": "计算机",
    "计算机板块": "计算机",
    
    # 传媒相关
    "传媒": "传媒",
    "传媒板块": "传媒",
    "文化传媒": "传媒",
    
    # 化工相关
    "化工": "化工",
    "化工板块": "化工",
    "化工行业": "化工",
    
    # 农业相关
    "农业": "农林牧渔",
    "农林牧渔板块": "农林牧渔",
    "养殖": "养殖业",
    "种植": "种植业",
}

@lru_cache(maxsize=256)
def map_sector_name(user_input: str) -> Optional[str]:
    """
    将用户输入的板块名称映射到数据库中的标准名称
    
    Args:
        user_input: 用户输入的板块名称
        
    Returns:
        标准的板块名称，如果没有映射则返回None
    """
    if not user_input:
        return None
    
    # 先尝试直接匹配
    if user_input in SECTOR_NAME_MAPPING:
        mapped_name = SECTOR_NAME_MAPPING[user_input]
        logger.info(f"板块名称映射: {user_input} -> {mapped_name}")
        return mapped_name
    
    # 尝试去除"板块"后缀后匹配
    if user_input.endswith("板块"):
        base_name = user_input[:-2]
        if base_name in SECTOR_NAME_MAPPING:
            mapped_name = SECTOR_NAME_MAPPING[base_name]
            logger.info(f"板块名称映射: {user_input} -> {mapped_name}")
            return mapped_name
    
    # 没有找到映射，返回None
    logger.warning(f"未找到板块名称映射: {user_input}")
    return None

def get_all_sector_mappings() -> Dict[str, str]:
    """获取所有板块名称映射"""
    return SECTOR_NAME_MAPPING.copy()

def get_sector_aliases(standard_name: str) -> List[str]:
    """
    获取某个标准板块名称的所有别名
    
    Args:
        standard_name: 标准板块名称
        
    Returns:
        所有指向该标准名称的别名列表
    """
    aliases = []
    for alias, standard in SECTOR_NAME_MAPPING.items():
        if standard == standard_name:
            aliases.append(alias)
    return aliases

def add_sector_mapping(alias: str, standard_name: str) -> None:
    """
    添加新的板块名称映射
    
    Args:
        alias: 别名
        standard_name: 标准名称
    """
    SECTOR_NAME_MAPPING[alias] = standard_name
    # 清除缓存
    map_sector_name.cache_clear()
    logger.info(f"添加板块名称映射: {alias} -> {standard_name}")

# 测试代码
if __name__ == "__main__":
    # 设置日志
    logging.basicConfig(level=logging.INFO)
    
    # 测试映射
    test_cases = [
        "房地产",
        "房地产板块",
        "地产",
        "地产板块",
        "房地产开发板块",
        "银行",
        "银行板块",
        "新能源",
        "不存在的板块"
    ]
    
    print("板块名称映射测试：")
    print("-" * 50)
    
    for test in test_cases:
        result = map_sector_name(test)
        print(f"{test:15s} -> {result if result else '无映射'}")
    
    print("\n房地产开发板块的所有别名：")
    print("-" * 50)
    aliases = get_sector_aliases("房地产开发")
    for alias in aliases:
        print(f"- {alias}")