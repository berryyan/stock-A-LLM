#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
统一板块验证器
类似于unified_stock_validator，提供板块提取、验证和映射功能
"""

import re
import logging
from typing import Optional, Tuple, List, Dict
from functools import lru_cache
import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.sector_name_mapper import map_sector_name
from utils.sector_code_mapper import SectorCodeMapper
from utils.logger import setup_logger

logger = setup_logger("unified_sector_validator")


class UnifiedSectorValidator:
    """统一的板块验证器"""
    
    def __init__(self):
        """初始化板块验证器"""
        self.logger = logger
        self.sector_mapper = SectorCodeMapper()
        
        # 常见动词列表
        self.action_verbs = [
            '分析', '评估', '研究', '查询', '查看', 
            '了解', '评价', '判断', '解析', '看',
            '追踪', '关注', '监控', '统计', '计算'
        ]
        
        # 板块关键词
        self.sector_keywords = ['板块', '行业', '概念']
        
        # 已知的板块名称（高频使用）
        self.known_sectors = {
            '银行', '证券', '保险', '白酒', '医药',
            '新能源', '半导体', '钢铁', '煤炭', '有色',
            '汽车', '家电', '食品', '建筑', '电力',
            '交通', '通信', '计算机', '传媒', '化工',
            '农业', '房地产', '石油', '军工', '旅游',
            '零售', '纺织', '造纸', '水泥', '玻璃',
            '光伏设备', '医疗器械', '房地产开发', '房地产服务',
            '酿酒行业', '新能源汽车'
        }
    
    def extract_sector(self, query: str) -> Optional[Tuple[str, str]]:
        """
        从查询中提取板块信息
        
        Args:
            query: 查询字符串
            
        Returns:
            Tuple[板块名称（带"板块"后缀）, 板块代码] 或 None
        """
        if not query:
            return None
        
        # 策略0：首先检查是否包含板块代码（BKxxxx.DC格式）
        sector_code_pattern = r'(BK\d{4}\.DC)'
        sector_code_match = re.search(sector_code_pattern, query)
        if sector_code_match:
            sector_code = sector_code_match.group(1)
            # 通过板块代码反查板块名称
            sector_name = self.sector_mapper.get_sector_name(sector_code)
            if sector_name:
                self.logger.info(f"通过板块代码 {sector_code} 找到板块名称: {sector_name}")
                # 统一返回带"板块"后缀的名称
                if not sector_name.endswith('板块'):
                    sector_name = sector_name + '板块'
                return (sector_name, sector_code)
            else:
                self.logger.warning(f"未找到板块代码 {sector_code} 对应的板块名称")
                # 返回板块代码作为名称
                return (sector_code, sector_code)
        
        # 策略1：尝试精确提取板块名称
        # 使用更精确的模式，避免匹配到动词
        patterns = [
            # 匹配"XX板块"格式（2-6个中文字符）
            # 不使用负向后瞻，改为直接匹配并在后续处理中过滤
            r'([一-龥]{2,6})(?=板块)',
            # 匹配"XX行业"格式
            r'([一-龥]{2,6})(?=行业)',
            # 匹配"XX概念"格式
            r'([一-龥]{2,6})(?=概念)'
        ]
        
        best_match = None
        best_score = -1
        best_suffix = None
        
        for pattern_idx, pattern in enumerate(patterns):
            suffix = self.sector_keywords[pattern_idx]
            matches = list(re.finditer(pattern, query))
            
            for match in matches:
                sector_name = match.group(1)
                
                # 特殊处理0：检查是否是动词的一部分
                # 例如："研究房地产开发板块"中的"究房地产开发"
                if len(sector_name) > 3 and sector_name[0] in '究析估价断看查解':
                    # 尝试去掉第一个字
                    potential_sector = sector_name[1:]
                    if potential_sector in self.known_sectors or self._get_sector_code(potential_sector):
                        sector_name = potential_sector
                        self.logger.debug(f"去除动词尾字，板块名称调整为: {sector_name}")
                
                # 特殊处理1：如果板块名称以动词结尾，尝试去掉最后一个字
                # 例如："析银行" -> "银行"
                if len(sector_name) > 2:
                    last_char = sector_name[-1]
                    if last_char in '析看查究估解价断':
                        # 检查去掉最后一个字后是否是有效板块
                        cleaned_name = sector_name[:-1]
                        if cleaned_name in self.known_sectors or map_sector_name(cleaned_name):
                            sector_name = cleaned_name
                            self.logger.debug(f"去除动词后缀，板块名称调整为: {sector_name}")
                
                # 特殊处理2：如果板块名称包含动词前缀，尝试提取后面的部分
                # 例如："分析银行" -> "银行"
                for verb in self.action_verbs:
                    if sector_name.startswith(verb) and len(sector_name) > len(verb):
                        potential_sector = sector_name[len(verb):]
                        if potential_sector in self.known_sectors or map_sector_name(potential_sector):
                            sector_name = potential_sector
                            self.logger.debug(f"去除动词前缀'{verb}'，板块名称调整为: {sector_name}")
                            break
                
                score = self._evaluate_sector_match(sector_name, match.start(), query)
                
                self.logger.debug(f"评估板块匹配: '{sector_name}{suffix}' 得分: {score}")
                
                if score > best_score:
                    best_score = score
                    best_match = sector_name
                    best_suffix = suffix
        
        # 策略2：如果精确匹配失败，尝试更宽松的匹配
        if not best_match or best_score < 1:
            # 直接搜索已知板块名称
            for sector in self.known_sectors:
                if sector + '板块' in query:
                    best_match = sector
                    best_suffix = '板块'
                    best_score = 10  # 已知板块给高分
                    break
        
        # 如果找到了有效的板块
        if best_match and best_score > 0:
            full_sector_name = best_match + best_suffix
            self.logger.info(f"提取到板块: {full_sector_name} (得分: {best_score})")
            
            # 获取板块代码
            sector_code = self._get_sector_code(best_match)
            if sector_code:
                self.logger.info(f"板块代码映射: {best_match} -> {sector_code}")
                return (full_sector_name, sector_code)
            else:
                self.logger.warning(f"未找到板块代码: {best_match}")
                return (full_sector_name, None)
        
        return None
    
    def _evaluate_sector_match(self, sector_name: str, start_pos: int, query: str) -> int:
        """
        评估板块匹配的质量
        
        Args:
            sector_name: 板块名称（不含后缀）
            start_pos: 匹配起始位置
            query: 原始查询
            
        Returns:
            得分（越高越好）
        """
        score = 1  # 基础分
        
        # 1. 检查是否包含动词（包含动词扣分）
        for verb in self.action_verbs:
            if verb in sector_name:
                score -= 3
                self.logger.debug(f"  包含动词 '{verb}'，扣3分")
                break
        
        # 2. 长度检查（2-4个字最合理）
        if 2 <= len(sector_name) <= 4:
            score += 2
        elif len(sector_name) > 4:
            score -= 1
        
        # 3. 是否是已知板块（大加分）
        if sector_name in self.known_sectors:
            score += 5
            self.logger.debug(f"  是已知板块 '{sector_name}'，加5分")
        
        # 4. 检查板块名称映射
        if map_sector_name(sector_name):
            score += 3
            self.logger.debug(f"  有板块映射，加3分")
        
        # 5. 位置检查（开头或前有分隔符加分）
        if start_pos == 0:
            score += 1
        elif start_pos > 0:
            prev_char = query[start_pos - 1]
            if prev_char in ' 　，。！？、的和与及':
                score += 2
        
        # 6. 检查是否是完整的词（后面有明确的边界）
        end_pos = start_pos + len(sector_name)
        if end_pos < len(query):
            next_chars = query[end_pos:end_pos+2]
            if next_chars.startswith('板块') or next_chars.startswith('行业') or next_chars.startswith('概念'):
                score += 1
        
        return score
    
    def _get_sector_code(self, sector_name: str) -> Optional[str]:
        """
        获取板块代码
        
        Args:
            sector_name: 板块名称（不含"板块"后缀）
            
        Returns:
            板块代码或None
        """
        # 先尝试映射板块名称
        mapped_name = map_sector_name(sector_name)
        if mapped_name:
            sector_name = mapped_name
        
        # 获取板块代码
        return self.sector_mapper.get_sector_code(sector_name)
    
    def extract_multiple_sectors(self, query: str) -> List[Tuple[str, str]]:
        """
        提取多个板块（用于对比查询等）
        
        Args:
            query: 查询字符串
            
        Returns:
            板块列表，每个元素为(板块名称, 板块代码)
        """
        sectors = []
        
        # 将查询按常见分隔符分割
        separators = ['和', '与', '及', '、', '，', ',', '对比', '比较']
        segments = [query]
        
        for sep in separators:
            new_segments = []
            for segment in segments:
                new_segments.extend(segment.split(sep))
            segments = new_segments
        
        # 对每个片段尝试提取板块
        for segment in segments:
            result = self.extract_sector(segment.strip())
            if result:
                sectors.append(result)
        
        # 去重
        unique_sectors = []
        seen = set()
        for sector_name, sector_code in sectors:
            if sector_name not in seen:
                seen.add(sector_name)
                unique_sectors.append((sector_name, sector_code))
        
        return unique_sectors
    
    def validate_sector_name(self, sector_name: str) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        验证板块名称是否有效
        
        Args:
            sector_name: 板块名称
            
        Returns:
            (是否有效, 标准板块名称, 板块代码)
        """
        if not sector_name:
            return (False, None, None)
        
        # 移除"板块"后缀进行验证
        clean_name = sector_name.replace('板块', '').replace('行业', '').replace('概念', '')
        
        # 检查是否是已知板块
        if clean_name in self.known_sectors:
            full_name = clean_name + '板块'
            sector_code = self._get_sector_code(clean_name)
            return (True, full_name, sector_code)
        
        # 尝试映射
        mapped_name = map_sector_name(clean_name)
        if mapped_name:
            full_name = mapped_name + '板块' if not mapped_name.endswith('板块') else mapped_name
            sector_code = self._get_sector_code(mapped_name)
            return (True, full_name, sector_code)
        
        # 直接查询板块代码
        sector_code = self._get_sector_code(clean_name)
        if sector_code:
            full_name = clean_name + '板块'
            return (True, full_name, sector_code)
        
        return (False, None, None)


# 创建全局实例
_sector_validator_instance = None


def get_sector_validator() -> UnifiedSectorValidator:
    """获取板块验证器单例"""
    global _sector_validator_instance
    if _sector_validator_instance is None:
        _sector_validator_instance = UnifiedSectorValidator()
    return _sector_validator_instance


# 便捷函数
def extract_sector(query: str) -> Optional[Tuple[str, str]]:
    """
    从查询中提取板块信息
    
    Args:
        query: 查询字符串
        
    Returns:
        Tuple[板块名称, 板块代码] 或 None
    """
    validator = get_sector_validator()
    return validator.extract_sector(query)


def extract_multiple_sectors(query: str) -> List[Tuple[str, str]]:
    """
    提取多个板块
    
    Args:
        query: 查询字符串
        
    Returns:
        板块列表
    """
    validator = get_sector_validator()
    return validator.extract_multiple_sectors(query)


def validate_sector_name(sector_name: str) -> Tuple[bool, Optional[str], Optional[str]]:
    """
    验证板块名称
    
    Args:
        sector_name: 板块名称
        
    Returns:
        (是否有效, 标准板块名称, 板块代码)
    """
    validator = get_sector_validator()
    return validator.validate_sector_name(sector_name)


# 测试代码
if __name__ == "__main__":
    # 设置日志级别为DEBUG以查看详细信息
    logging.getLogger("unified_sector_validator").setLevel(logging.DEBUG)
    
    # 测试用例
    test_queries = [
        "银行板块的主力资金",
        "分析银行板块的资金流向",
        "评估新能源板块的资金趋势",
        "研究白酒板块的主力行为",
        "房地产板块和银行板块的对比",
        "钢铁行业的发展前景",
        "半导体概念股的表现",
        "看一下医药板块",
        "了解汽车板块的情况",
        "新能源汽车板块分析"
    ]
    
    print("板块提取测试")
    print("=" * 60)
    
    for query in test_queries:
        print(f"\n查询: {query}")
        result = extract_sector(query)
        if result:
            sector_name, sector_code = result
            print(f"  板块名称: {sector_name}")
            print(f"  板块代码: {sector_code}")
        else:
            print("  未提取到板块")
    
    print("\n\n多板块提取测试")
    print("=" * 60)
    
    multi_queries = [
        "银行板块和房地产板块的对比",
        "新能源、半导体、医药板块的资金流向",
        "比较钢铁板块与煤炭板块"
    ]
    
    for query in multi_queries:
        print(f"\n查询: {query}")
        sectors = extract_multiple_sectors(query)
        for i, (name, code) in enumerate(sectors, 1):
            print(f"  板块{i}: {name} ({code})")