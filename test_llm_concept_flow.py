#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试LLM在概念匹配中的完整介入流程
验证三个关键环节：
1. 从用户输入提取概念（LLM第一次介入）
2. 概念扩展（LLM扩展相关概念）
3. 概念匹配到三大数据源（LLM匹配实际概念）
"""

import logging
import sys
import json

# 添加项目根目录到系统路径
sys.path.insert(0, '/mnt/e/PycharmProjects/stock_analysis_system')

from utils.concept.concept_matcher_v2 import ConceptMatcherV2
from utils.concept.concept_data_collector import ConceptDataCollector

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def test_llm_concept_extraction():
    """测试LLM概念提取"""
    logger.info("\n=== 测试LLM概念提取（第一次介入）===")
    
    matcher = ConceptMatcherV2()
    
    test_cases = [
        {
            "input": "储能概念股有哪些？",
            "expected": ["储能"]
        },
        {
            "input": "我想了解一下固态电池和新能源汽车相关的股票",
            "expected": ["固态电池", "新能源汽车"]
        },
        {
            "input": "近期国家发布了关于人工智能产业发展的重要政策，支持AI芯片、算力基础设施建设，请分析相关概念股",
            "expected": ["人工智能", "AI芯片", "算力"]
        }
    ]
    
    for case in test_cases:
        logger.info(f"\n输入: {case['input']}")
        concepts = matcher.extract_concepts(case['input'])
        logger.info(f"提取的概念: {concepts}")
        logger.info(f"期望包含: {case['expected']}")
        
        # 检查是否包含期望的概念
        for exp in case['expected']:
            if any(exp in c for c in concepts):
                logger.info(f"  ✓ 找到概念: {exp}")
            else:
                logger.warning(f"  ✗ 未找到概念: {exp}")


def test_llm_concept_expansion():
    """测试LLM概念扩展"""
    logger.info("\n=== 测试LLM概念扩展 ===")
    
    matcher = ConceptMatcherV2()
    
    test_concepts = [
        ["储能"],
        ["固态电池"],
        ["人工智能", "算力"]
    ]
    
    for concepts in test_concepts:
        logger.info(f"\n原始概念: {concepts}")
        expanded = matcher.expand_concepts(concepts)
        logger.info(f"扩展后: {expanded}")
        logger.info(f"新增概念: {[c for c in expanded if c not in concepts]}")


def test_llm_concept_matching():
    """测试LLM概念匹配到三大数据源"""
    logger.info("\n=== 测试LLM概念匹配（第二次介入）===")
    
    matcher = ConceptMatcherV2()
    
    test_concepts = [
        ["储能", "储能设备"],
        ["固态电池", "新能源电池"],
        ["人工智能", "AI", "算力"]
    ]
    
    for concepts in test_concepts:
        logger.info(f"\n待匹配概念: {concepts}")
        matched = matcher.match_concepts(concepts)
        
        logger.info("匹配结果:")
        logger.info(f"  同花顺: {matched['THS'][:5]}")  # 只显示前5个
        logger.info(f"  东财: {matched['DC'][:5]}")
        logger.info(f"  开盘啦: {matched['KPL'][:5]}")
        
        total = len(matched['THS']) + len(matched['DC']) + len(matched['KPL'])
        logger.info(f"  总计匹配: {total}个概念")


def test_kpl_description_matching():
    """测试开盘啦概念描述匹配"""
    logger.info("\n=== 测试开盘啦概念描述匹配 ===")
    
    matcher = ConceptMatcherV2()
    
    # 加载概念列表看看是否包含描述
    all_concepts = matcher._load_all_concepts()
    
    # 查看开盘啦概念的描述信息
    kpl_with_desc = [c for c in all_concepts['KPL'] if c.get('desc')]
    logger.info(f"开盘啦概念总数: {len(all_concepts['KPL'])}")
    logger.info(f"包含描述的概念数: {len(kpl_with_desc)}")
    
    # 显示几个例子
    if kpl_with_desc:
        logger.info("\n开盘啦概念描述示例:")
        for concept in kpl_with_desc[:3]:
            logger.info(f"  {concept['name']}: {concept['desc'][:100]}...")


def test_complete_flow():
    """测试完整流程"""
    logger.info("\n=== 测试完整概念处理流程 ===")
    
    matcher = ConceptMatcherV2()
    collector = ConceptDataCollector()
    
    # 模拟用户输入
    user_query = "我想了解固态电池概念相关的投资机会，特别是储能方向的"
    
    logger.info(f"用户查询: {user_query}")
    
    # 1. 提取概念
    concepts = matcher.extract_concepts(user_query)
    logger.info(f"\n1. 提取概念: {concepts}")
    
    # 2. 扩展概念
    expanded = matcher.expand_concepts(concepts)
    logger.info(f"\n2. 扩展概念: {expanded}")
    
    # 3. 匹配到数据源
    matched = matcher.match_concepts(expanded)
    logger.info(f"\n3. 概念匹配:")
    logger.info(f"   同花顺: {len(matched['THS'])}个")
    logger.info(f"   东财: {len(matched['DC'])}个")
    logger.info(f"   开盘啦: {len(matched['KPL'])}个")
    
    # 4. 获取概念股（只获取前10只演示）
    all_matched_names = []
    all_matched_names.extend(matched['THS'][:2])
    all_matched_names.extend(matched['DC'][:2])
    all_matched_names.extend(matched['KPL'][:2])
    
    if all_matched_names:
        stocks = collector.get_concept_stocks(all_matched_names)
        logger.info(f"\n4. 获取概念股: {len(stocks)}只")
        
        # 显示前5只股票
        logger.info("\n前5只股票:")
        for i, stock in enumerate(stocks[:5], 1):
            logger.info(f"  {i}. {stock['name']}({stock['ts_code']}) - "
                       f"概念: {stock['concepts']}, 数据源: {stock['data_source']}")


def main():
    """主函数"""
    test_llm_concept_extraction()
    test_llm_concept_expansion()
    test_llm_concept_matching()
    test_kpl_description_matching()
    test_complete_flow()
    
    logger.info("\n=== 测试完成 ===")


if __name__ == "__main__":
    main()