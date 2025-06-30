#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查股票简称映射的歧义性
分析unified_stock_validator.py中的common_short_names是否存在一个简称对应多个股票的情况
"""

import sys
import os
from typing import Dict, List, Tuple
from collections import defaultdict

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.stock_code_mapper import get_stock_mapper
from utils.unified_stock_validator import UnifiedStockValidator
from utils.logger import setup_logger


def clean_company_name(name: str) -> str:
    """清理公司名称，去除常见后缀"""
    if not name:
        return name
    
    # 去除常见后缀
    suffixes = ['股份有限公司', '有限公司', '集团股份', '股份', '集团', '控股']
    clean_name = name
    
    for suffix in suffixes:
        if clean_name.endswith(suffix):
            clean_name = clean_name[:-len(suffix)]
            break
    
    return clean_name.strip()


def check_short_name_ambiguity():
    """检查所有简称映射是否存在歧义"""
    logger = setup_logger("check_short_name_ambiguity")
    
    # 获取股票映射器实例
    mapper = get_stock_mapper()
    
    # 获取验证器中的简称映射
    validator = UnifiedStockValidator()
    common_short_names = validator.common_short_names
    
    # 结果存储
    ambiguous_names = defaultdict(list)  # 有歧义的简称
    unique_mappings = {}  # 唯一映射的简称
    not_found = []  # 找不到任何匹配的简称
    
    logger.info(f"开始检查 {len(common_short_names)} 个简称映射...")
    print(f"\n检查股票简称映射歧义性")
    print("=" * 80)
    print(f"共有 {len(common_short_names)} 个简称需要检查\n")
    
    # 获取所有股票信息（从缓存或数据库）
    # 使用_reverse_cache获取ts_code到name的映射
    with mapper._cache_lock:
        all_stocks = mapper._reverse_cache.copy()
    
    if not all_stocks:
        logger.error("无法获取股票数据")
        print("错误：无法获取股票数据，请检查数据库连接")
        return
    
    logger.info(f"成功获取 {len(all_stocks)} 条股票数据")
    
    # 对每个简称进行检查
    for short_name, expected_full_name in common_short_names.items():
        matches = []
        
        # 搜索所有包含该简称的股票
        for ts_code, name in all_stocks.items():
            # 检查股票名称是否包含简称（忽略后缀）
            clean_name = clean_company_name(name)
            
            # 精确匹配或包含匹配
            if short_name in clean_name or clean_name == short_name:
                matches.append({
                    'ts_code': ts_code,
                    'name': name,
                    'clean_name': clean_name
                })
        
        # 分析结果
        if len(matches) == 0:
            not_found.append((short_name, expected_full_name))
        elif len(matches) == 1:
            unique_mappings[short_name] = {
                'expected': expected_full_name,
                'found': matches[0]
            }
        else:
            # 多个匹配，可能有歧义
            ambiguous_names[short_name] = {
                'expected': expected_full_name,
                'matches': matches
            }
    
    # 输出结果
    print("\n1. 有歧义的简称（一个简称对应多个股票）:")
    print("-" * 80)
    
    if ambiguous_names:
        for short_name, info in ambiguous_names.items():
            print(f"\n简称: '{short_name}' (期望: {info['expected']})")
            print(f"找到 {len(info['matches'])} 个匹配:")
            for match in info['matches']:
                is_expected = match['name'] == info['expected'] or match['clean_name'] == info['expected']
                marker = " ✓ (期望匹配)" if is_expected else ""
                print(f"  - {match['ts_code']}: {match['name']}{marker}")
    else:
        print("✅ 好消息！没有发现有歧义的简称。")
    
    print("\n\n2. 唯一映射的简称:")
    print("-" * 80)
    print(f"共有 {len(unique_mappings)} 个简称有唯一映射")
    
    # 只显示前几个作为示例
    if unique_mappings:
        count = 0
        for short_name, info in unique_mappings.items():
            if count < 5:
                print(f"  '{short_name}' → {info['found']['name']} ({info['found']['ts_code']})")
                count += 1
        if len(unique_mappings) > 5:
            print(f"  ... 还有 {len(unique_mappings) - 5} 个唯一映射")
    
    print("\n\n3. 找不到匹配的简称:")
    print("-" * 80)
    
    if not_found:
        for short_name, expected in not_found:
            print(f"  ❌ '{short_name}' (期望: {expected}) - 未找到任何匹配")
    else:
        print("✅ 所有简称都找到了至少一个匹配。")
    
    # 统计汇总
    print("\n\n统计汇总:")
    print("=" * 80)
    print(f"总简称数: {len(common_short_names)}")
    print(f"有歧义的: {len(ambiguous_names)} ({len(ambiguous_names)/len(common_short_names)*100:.1f}%)")
    print(f"唯一映射: {len(unique_mappings)} ({len(unique_mappings)/len(common_short_names)*100:.1f}%)")
    print(f"未找到的: {len(not_found)} ({len(not_found)/len(common_short_names)*100:.1f}%)")
    
    # 建议
    if ambiguous_names:
        print("\n\n建议:")
        print("-" * 80)
        print("对于有歧义的简称，建议采取以下措施之一：")
        print("1. 使用更精确的简称（如'平安银行'而不是'平安'）")
        print("2. 在映射中指定具体的股票代码")
        print("3. 根据上下文智能选择（如根据行业、市值等）")
        print("4. 提示用户使用完整名称")
    
    return ambiguous_names, unique_mappings, not_found


def analyze_specific_short_name(short_name: str):
    """分析特定简称的所有匹配"""
    logger = setup_logger("analyze_short_name")
    mapper = get_stock_mapper()
    
    print(f"\n分析简称 '{short_name}' 的所有匹配:")
    print("=" * 80)
    
    with mapper._cache_lock:
        all_stocks = mapper._reverse_cache.copy()
    matches = []
    
    for ts_code, name in all_stocks.items():
        clean_name = clean_company_name(name)
        if short_name in clean_name or clean_name == short_name:
            matches.append({
                'ts_code': ts_code,
                'name': name,
                'clean_name': clean_name
            })
    
    if matches:
        print(f"找到 {len(matches)} 个包含 '{short_name}' 的股票:")
        for match in matches:
            print(f"  - {match['ts_code']}: {match['name']}")
    else:
        print(f"没有找到包含 '{short_name}' 的股票")
    
    return matches


def find_stocks_by_keyword(keyword: str):
    """查找包含特定关键词的所有股票"""
    logger = setup_logger("find_stocks")
    mapper = get_stock_mapper()
    
    print(f"\n查找包含 '{keyword}' 的所有股票:")
    print("=" * 80)
    
    with mapper._cache_lock:
        all_stocks = mapper._reverse_cache.copy()
    
    matches = []
    for ts_code, name in all_stocks.items():
        if keyword in name:
            matches.append((ts_code, name))
    
    if matches:
        matches.sort(key=lambda x: x[1])  # 按名称排序
        print(f"找到 {len(matches)} 个包含 '{keyword}' 的股票:")
        for ts_code, name in matches:
            print(f"  - {ts_code}: {name}")
    else:
        print(f"没有找到包含 '{keyword}' 的股票")
    
    return matches


if __name__ == "__main__":
    # 运行主检查
    check_short_name_ambiguity()
    
    # 查找那些找不到的银行股票
    print("\n\n" + "="*80)
    print("查找实际的银行股票名称:")
    print("="*80)
    
    # 查找银行类股票
    bank_keywords = ['建设银行', '工商银行', '农业银行', '中国银行', '招商银行', '银行']
    for keyword in bank_keywords:
        find_stocks_by_keyword(keyword)
    
    # 查找石油石化类股票
    print("\n查找石油石化类股票:")
    oil_keywords = ['中国石油', '中国石化', '石油', '石化']
    for keyword in oil_keywords[:2]:  # 只查前两个避免太多输出
        find_stocks_by_keyword(keyword)