#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试修复后的数据源查询
"""

import logging
import sys

# 添加项目根目录到系统路径
sys.path.insert(0, '/mnt/e/PycharmProjects/stock_analysis_system')

from utils.concept.concept_data_collector import ConceptDataCollector

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def test_fixed_data_sources():
    """测试修复后的数据源"""
    logger.info("=== 测试修复后的数据源查询 ===")
    
    # 初始化数据采集器
    collector = ConceptDataCollector()
    
    # 测试案例
    test_cases = [
        {
            "name": "储能概念测试",
            "concepts": ["储能"],
            "expect": "所有数据源都应该有数据"
        },
        {
            "name": "新能源测试",
            "concepts": ["新能源"],
            "expect": "至少同花顺应该有数据"
        },
        {
            "name": "人工智能测试",
            "concepts": ["人工智能"],
            "expect": "多个数据源应该有数据"
        }
    ]
    
    for test_case in test_cases:
        logger.info(f"\n=== {test_case['name']} ===")
        logger.info(f"测试概念: {test_case['concepts']}")
        logger.info(f"期望结果: {test_case['expect']}")
        
        # 获取概念股
        stocks = collector.get_concept_stocks(test_case['concepts'])
        
        # 统计各数据源的结果
        source_stats = {}
        for stock in stocks:
            for source in stock.get('data_source', []):
                source_stats[source] = source_stats.get(source, 0) + 1
        
        # 显示结果
        logger.info(f"总计找到: {len(stocks)} 只股票")
        logger.info(f"数据源分布: {source_stats}")
        
        # 显示前5只股票
        if stocks:
            logger.info("前5只股票:")
            for i, stock in enumerate(stocks[:5], 1):
                logger.info(f"  {i}. {stock['name']} ({stock['ts_code']}) - {stock['data_source']}")
        
        # 分别测试各数据源
        logger.info("\n各数据源详细测试:")
        
        # 测试同花顺
        ths_stocks = collector._get_ths_concept_stocks(test_case['concepts'])
        logger.info(f"同花顺: {len(ths_stocks)} 只")
        
        # 测试东财
        dc_stocks = collector._get_dc_concept_stocks(test_case['concepts'])
        logger.info(f"东财: {len(dc_stocks)} 只")
        
        # 测试开盘啦
        kpl_stocks = collector._get_kpl_concept_stocks(test_case['concepts'])
        logger.info(f"开盘啦: {len(kpl_stocks)} 只")


def test_specific_concepts():
    """测试特定概念"""
    logger.info("\n\n=== 测试特定概念（基于调查结果）===")
    
    collector = ConceptDataCollector()
    
    # 测试应该在多个数据源都有的概念
    common_concepts = ["智能电网", "宠物经济"]
    
    for concept in common_concepts:
        logger.info(f"\n测试通用概念: {concept}")
        stocks = collector.get_concept_stocks([concept])
        
        # 统计数据源
        sources = set()
        for stock in stocks:
            sources.update(stock.get('data_source', []))
        
        logger.info(f"找到 {len(stocks)} 只股票，数据源: {sources}")


def main():
    """主函数"""
    # 基础测试
    test_fixed_data_sources()
    
    # 特定概念测试
    test_specific_concepts()
    
    logger.info("\n=== 测试完成 ===")


if __name__ == "__main__":
    main()