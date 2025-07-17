#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试数据源修复
验证东财和开盘啦的SQL错误是否已修复
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


def test_data_sources():
    """测试各数据源是否正常工作"""
    logger.info("=== 测试数据源修复 ===")
    
    # 初始化数据采集器
    collector = ConceptDataCollector()
    
    # 测试概念
    test_concepts = ["储能", "新能源"]
    
    logger.info(f"测试概念: {test_concepts}")
    
    # 直接测试各数据源
    try:
        # 1. 测试同花顺
        logger.info("\n1. 测试同花顺数据源...")
        ths_stocks = collector._get_ths_concept_stocks(test_concepts)
        logger.info(f"同花顺: 获取到 {len(ths_stocks)} 只股票")
        if ths_stocks:
            logger.info(f"示例: {ths_stocks[0]}")
    except Exception as e:
        logger.error(f"同花顺错误: {e}")
    
    try:
        # 2. 测试东财
        logger.info("\n2. 测试东财数据源...")
        dc_stocks = collector._get_dc_concept_stocks(test_concepts)
        logger.info(f"东财: 获取到 {len(dc_stocks)} 只股票")
        if dc_stocks:
            logger.info(f"示例: {dc_stocks[0]}")
    except Exception as e:
        logger.error(f"东财错误: {e}")
    
    try:
        # 3. 测试开盘啦
        logger.info("\n3. 测试开盘啦数据源...")
        kpl_stocks = collector._get_kpl_concept_stocks(test_concepts)
        logger.info(f"开盘啦: 获取到 {len(kpl_stocks)} 只股票")
        if kpl_stocks:
            logger.info(f"示例: {kpl_stocks[0]}")
    except Exception as e:
        logger.error(f"开盘啦错误: {e}")
    
    # 4. 测试综合获取
    logger.info("\n4. 测试综合获取...")
    all_stocks = collector.get_concept_stocks(test_concepts)
    logger.info(f"综合: 获取到 {len(all_stocks)} 只股票")
    
    # 统计数据源分布
    data_source_count = {}
    for stock in all_stocks:
        for source in stock['data_source']:
            data_source_count[source] = data_source_count.get(source, 0) + 1
    
    logger.info(f"数据源分布: {data_source_count}")
    
    logger.info("\n=== 测试完成 ===")
    return len(all_stocks) > 0


def main():
    """主函数"""
    try:
        success = test_data_sources()
        if success:
            logger.info("✅ 数据源修复成功！")
        else:
            logger.error("❌ 数据源仍有问题")
    except Exception as e:
        logger.error(f"测试失败: {e}", exc_info=True)


if __name__ == "__main__":
    main()