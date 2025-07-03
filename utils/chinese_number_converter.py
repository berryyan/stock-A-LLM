"""
中文数字转换工具

支持将中文数字表达转换为阿拉伯数字，主要用于查询中的数量表达。
例如："前十" -> 10, "前二十" -> 20, "TOP十" -> 10

Author: Claude
Date: 2025-07-04
Version: 1.0.0
"""

import re
from typing import Optional, Dict, Tuple
import logging

logger = logging.getLogger(__name__)

# 中文数字映射表
CHINESE_NUM_MAP: Dict[str, int] = {
    '零': 0, '〇': 0, '0': 0,
    '一': 1, '壹': 1, '1': 1,
    '二': 2, '贰': 2, '两': 2, '俩': 2, '2': 2,
    '三': 3, '叁': 3, '3': 3,
    '四': 4, '肆': 4, '4': 4,
    '五': 5, '伍': 5, '5': 5,
    '六': 6, '陆': 6, '6': 6,
    '七': 7, '柒': 7, '7': 7,
    '八': 8, '捌': 8, '8': 8,
    '九': 9, '玖': 9, '9': 9,
    '十': 10, '拾': 10,
    '百': 100, '佰': 100,
    '千': 1000, '仟': 1000,
    '万': 10000, '萬': 10000,
}

# 中文单位映射表
CHINESE_UNIT_MAP: Dict[str, int] = {
    '十': 10, '拾': 10,
    '百': 100, '佰': 100,
    '千': 1000, '仟': 1000,
    '万': 10000, '萬': 10000,
}

# 常用表达模式
COMMON_PATTERNS = [
    # "前N"模式
    (r'前([零一二三四五六七八九十百千万壹贰叁肆伍陆柒捌玖拾佰仟萬两俩〇0-9]+)', 'prefix'),
    # "TOP N"模式
    (r'[Tt][Oo][Pp]\s*([零一二三四五六七八九十百千万壹贰叁肆伍陆柒捌玖拾佰仟萬两俩〇0-9]+)', 'top'),
    # "第N"模式
    (r'第([零一二三四五六七八九十百千万壹贰叁肆伍陆柒捌玖拾佰仟萬两俩〇0-9]+)', 'ordinal'),
    # "N名"模式
    (r'([零一二三四五六七八九十百千万壹贰叁肆伍陆柒捌玖拾佰仟萬两俩〇0-9]+)名', 'suffix'),
    # "N个"模式
    (r'([零一二三四五六七八九十百千万壹贰叁肆伍陆柒捌玖拾佰仟萬两俩〇0-9]+)个', 'suffix'),
    # "N只"模式（股票专用）
    (r'([零一二三四五六七八九十百千万壹贰叁肆伍陆柒捌玖拾佰仟萬两俩〇0-9]+)只', 'suffix'),
]


def chinese_to_arabic(chinese_num: str) -> int:
    """
    将中文数字转换为阿拉伯数字
    
    Args:
        chinese_num: 中文数字字符串，如"二十三"、"一百零五"
        
    Returns:
        对应的阿拉伯数字
        
    Examples:
        >>> chinese_to_arabic("二十三")
        23
        >>> chinese_to_arabic("一百零五")
        105
        >>> chinese_to_arabic("三千五百")
        3500
    """
    # 如果已经是纯数字，直接返回
    if chinese_num.isdigit():
        return int(chinese_num)
    
    # 处理特殊情况
    if chinese_num == "十":
        return 10
    if chinese_num == "一十":
        return 10
        
    result = 0
    temp = 0
    
    for char in chinese_num:
        if char in CHINESE_NUM_MAP:
            num = CHINESE_NUM_MAP[char]
            
            # 如果是单位
            if num >= 10:
                if temp == 0:
                    temp = 1  # "十" -> 10, not 0*10
                result += temp * num
                temp = 0
            else:
                # 如果是数字
                temp = temp * 10 + num
        else:
            # 忽略未知字符
            continue
    
    # 加上最后的个位数
    result += temp
    
    return result


def extract_number_from_chinese(text: str) -> Optional[int]:
    """
    从包含中文数字的文本中提取数字
    
    Args:
        text: 可能包含中文数字的文本
        
    Returns:
        提取出的数字，如果没有找到则返回None
        
    Examples:
        >>> extract_number_from_chinese("前十名")
        10
        >>> extract_number_from_chinese("TOP二十")
        20
        >>> extract_number_from_chinese("第三个")
        3
    """
    # 尝试匹配常用模式
    for pattern, pattern_type in COMMON_PATTERNS:
        match = re.search(pattern, text)
        if match:
            chinese_num = match.group(1)
            try:
                number = chinese_to_arabic(chinese_num)
                logger.debug(f"从'{text}'中提取到数字: {number} (模式: {pattern_type})")
                return number
            except Exception as e:
                logger.warning(f"转换中文数字'{chinese_num}'时出错: {e}")
                continue
    
    # 如果没有匹配到模式，尝试直接查找中文数字
    chinese_chars = []
    for char in text:
        if char in CHINESE_NUM_MAP:
            chinese_chars.append(char)
        elif chinese_chars:
            # 遇到非中文数字字符，尝试转换已收集的字符
            chinese_num = ''.join(chinese_chars)
            try:
                number = chinese_to_arabic(chinese_num)
                if number > 0:
                    logger.debug(f"从'{text}'中提取到数字: {number} (直接提取)")
                    return number
            except:
                pass
            chinese_chars = []
    
    # 处理最后的字符
    if chinese_chars:
        chinese_num = ''.join(chinese_chars)
        try:
            number = chinese_to_arabic(chinese_num)
            if number > 0:
                logger.debug(f"从'{text}'中提取到数字: {number} (直接提取)")
                return number
        except:
            pass
    
    return None


def extract_limit_from_query(query: str, default: Optional[int] = None) -> Optional[int]:
    """
    从查询语句中提取数量限制
    
    专门用于SQL查询中的LIMIT参数提取，支持中文和阿拉伯数字
    
    Args:
        query: 查询语句
        default: 默认值，当无法提取时返回
        
    Returns:
        提取出的数量限制
        
    Examples:
        >>> extract_limit_from_query("涨幅前十")
        10
        >>> extract_limit_from_query("市值排名前20")
        20
        >>> extract_limit_from_query("TOP二十的股票")
        20
    """
    # 首先尝试提取阿拉伯数字
    arabic_match = re.search(r'(?:前|[Tt][Oo][Pp])\s*(\d+)', query)
    if arabic_match:
        return int(arabic_match.group(1))
    
    # 然后尝试提取中文数字
    chinese_number = extract_number_from_chinese(query)
    if chinese_number:
        return chinese_number
    
    # 检查是否有默认的表达
    if any(keyword in query for keyword in ['排名', '排行', '前几', 'TOP', 'top']):
        return default if default else 10
    
    return default


def normalize_quantity_expression(query: str) -> str:
    """
    将查询中的中文数字表达规范化为阿拉伯数字
    
    用于预处理查询语句，将中文数字转换为阿拉伯数字，
    以便后续的正则表达式匹配
    
    Args:
        query: 原始查询语句
        
    Returns:
        规范化后的查询语句
        
    Examples:
        >>> normalize_quantity_expression("涨幅前十")
        '涨幅前10'
        >>> normalize_quantity_expression("TOP二十股票")
        'TOP20股票'
    """
    normalized = query
    
    # 处理每个匹配的模式
    for pattern, pattern_type in COMMON_PATTERNS:
        def replace_func(match):
            chinese_num = match.group(1)
            try:
                arabic_num = chinese_to_arabic(chinese_num)
                # 根据模式类型重建字符串
                if pattern_type == 'prefix':
                    return f'前{arabic_num}'
                elif pattern_type == 'top':
                    return f'TOP{arabic_num}'
                elif pattern_type == 'ordinal':
                    return f'第{arabic_num}'
                elif pattern_type == 'suffix':
                    # 保留原有后缀
                    suffix = match.group(0)[-1]  # 获取"名"、"个"、"只"
                    return f'{arabic_num}{suffix}'
                else:
                    return str(arabic_num)
            except:
                return match.group(0)  # 转换失败则保持原样
        
        normalized = re.sub(pattern, replace_func, normalized)
    
    return normalized


# 测试函数
if __name__ == "__main__":
    # 设置日志级别
    logging.basicConfig(level=logging.DEBUG)
    
    # 测试用例
    test_cases = [
        # 基本中文数字
        ("二", 2),
        ("十", 10),
        ("十五", 15),
        ("二十", 20),
        ("二十三", 23),
        ("一百", 100),
        ("一百零五", 105),
        ("三千五百", 3500),
        ("一万", 10000),
        
        # 常用查询表达
        ("前十", 10),
        ("前二十", 20),
        ("前一百", 100),
        ("TOP十", 10),
        ("TOP二十", 20),
        ("第三", 3),
        ("十名", 10),
        ("二十个", 20),
        ("三十只", 30),
        
        # 混合表达
        ("涨幅前十的股票", 10),
        ("市值排名前二十", 20),
        ("TOP三十只股票", 30),
        
        # 阿拉伯数字
        ("前10", 10),
        ("TOP20", 20),
        ("前100名", 100),
    ]
    
    print("=== 中文数字转换测试 ===")
    for text, expected in test_cases:
        result = extract_limit_from_query(text)
        status = "✓" if result == expected else "✗"
        print(f"{status} '{text}' -> {result} (期望: {expected})")
    
    print("\n=== 查询规范化测试 ===")
    normalize_tests = [
        "涨幅前十的股票",
        "市值排名前二十",
        "TOP三十只股票",
        "第五个交易日",
        "前一百名公司",
    ]
    
    for text in normalize_tests:
        normalized = normalize_quantity_expression(text)
        print(f"'{text}' -> '{normalized}'")