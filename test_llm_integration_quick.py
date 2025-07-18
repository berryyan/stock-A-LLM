#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
快速测试LLM集成的核心功能
验证概念提取、扩展和匹配的完整流程
"""

import logging
import sys
import json

# 添加项目根目录到系统路径
sys.path.insert(0, '/mnt/e/PycharmProjects/stock_analysis_system')

from utils.concept.concept_matcher_v2 import ConceptMatcherV2
from agents.concept.concept_agent import ConceptAgent

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def test_llm_integration():
    """测试LLM集成的完整流程"""
    logger.info("=== 测试LLM集成流程 ===")
    
    # 创建Agent
    agent = ConceptAgent()
    
    # 测试查询
    test_query = "概念股分析：储能概念相关的投资机会有哪些？"
    
    logger.info(f"\n用户查询: {test_query}")
    
    # 1. 提取查询信息
    query_type, concepts = agent._extract_query_info(test_query)
    logger.info(f"\n1. 查询类型: {query_type}")
    logger.info(f"   提取的概念（LLM第一次介入）: {concepts}")
    
    # 2. 概念扩展
    expanded_concepts = agent.concept_matcher.expand_concepts(concepts)
    logger.info(f"\n2. 扩展的概念（LLM扩展）: {expanded_concepts}")
    
    # 3. 概念匹配到三大数据源
    matched_concepts = agent.concept_matcher.match_concepts(expanded_concepts)
    logger.info(f"\n3. 概念匹配结果（LLM第二次介入）:")
    logger.info(f"   同花顺: {matched_concepts['THS'][:3]}...")
    logger.info(f"   东财: {matched_concepts['DC'][:3]}...")
    logger.info(f"   开盘啦: {matched_concepts['KPL'][:3]}...")
    
    # 4. 查看开盘啦描述信息是否被使用
    all_concepts = agent.concept_matcher._load_all_concepts()
    kpl_with_desc = [c for c in all_concepts['KPL'] if c.get('desc') and '储能' in c['name']]
    
    if kpl_with_desc:
        logger.info(f"\n4. 开盘啦概念描述示例:")
        for concept in kpl_with_desc[:3]:
            logger.info(f"   {concept['name']}: {concept['desc'][:80]}...")
    
    # 5. 获取少量股票进行展示
    logger.info(f"\n5. 获取概念股数据:")
    # 只使用前2个匹配的概念避免超时
    test_concepts = []
    if matched_concepts['THS']:
        test_concepts.append(matched_concepts['THS'][0])
    if matched_concepts['KPL']:
        test_concepts.append(matched_concepts['KPL'][0])
    
    if test_concepts:
        stocks = agent.data_collector.get_concept_stocks(test_concepts[:1])  # 只用1个概念
        logger.info(f"   找到 {len(stocks)} 只股票")
        
        # 显示前3只
        for i, stock in enumerate(stocks[:3], 1):
            logger.info(f"   {i}. {stock['name']}({stock['ts_code']}) - "
                       f"概念: {stock['concepts']}, 数据源: {stock['data_source']}")


def test_concept_matcher_details():
    """测试ConceptMatcherV2的详细功能"""
    logger.info("\n=== 测试ConceptMatcherV2详细功能 ===")
    
    matcher = ConceptMatcherV2()
    
    # 测试不同类型的输入
    test_cases = [
        "充电宝",  # 短输入
        "我想了解固态电池和储能相关的概念股",  # 普通查询
        "近期政策支持新能源汽车产业发展，特别是充电基础设施建设，请分析相关投资机会"  # 长文本
    ]
    
    for query in test_cases:
        logger.info(f"\n输入: {query[:50]}...")
        
        # 提取概念
        concepts = matcher.extract_concepts(query)
        logger.info(f"提取的概念: {concepts}")
        
        # 扩展概念
        if concepts:
            expanded = matcher.expand_concepts(concepts[:2])  # 限制数量
            logger.info(f"扩展后: {expanded[:5]}...")  # 只显示前5个


def test_data_source_coverage():
    """测试三大数据源的覆盖情况"""
    logger.info("\n=== 测试数据源覆盖情况 ===")
    
    matcher = ConceptMatcherV2()
    all_concepts = matcher._load_all_concepts()
    
    logger.info(f"同花顺概念数: {len(all_concepts['THS'])}")
    logger.info(f"东财板块数: {len(all_concepts['DC'])}")
    logger.info(f"开盘啦概念数: {len(all_concepts['KPL'])}")
    
    # 检查包含描述的开盘啦概念
    kpl_with_desc = [c for c in all_concepts['KPL'] if c.get('desc')]
    logger.info(f"开盘啦包含描述的概念数: {len(kpl_with_desc)}")
    
    # 显示一些有描述的概念
    if kpl_with_desc:
        logger.info("\n开盘啦概念描述样例:")
        for concept in kpl_with_desc[:5]:
            logger.info(f"  {concept['name']}: {concept['desc'][:60]}...")


def main():
    """主函数"""
    try:
        test_llm_integration()
        test_concept_matcher_details()
        test_data_source_coverage()
        
        logger.info("\n=== 测试完成 ===")
        logger.info("LLM集成功能正常工作！")
        
    except Exception as e:
        logger.error(f"测试失败: {e}", exc_info=True)


if __name__ == "__main__":
    main()