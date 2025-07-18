#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试ConceptDataCollector修复后的功能
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
    """测试三个数据源是否正常工作"""
    logger.info("=== 测试修复后的数据源 ===")
    
    collector = ConceptDataCollector()
    
    # 测试概念
    test_concepts = ["储能", "固态电池", "锂电池"]
    
    for concept in test_concepts:
        logger.info(f"\n测试概念: {concept}")
        
        # 获取概念股
        stocks = collector.get_concept_stocks([concept])
        
        if stocks:
            logger.info(f"找到 {len(stocks)} 只相关股票")
            
            # 统计各数据源贡献
            source_count = {}
            for stock in stocks:
                for source in stock['data_source']:
                    source_count[source] = source_count.get(source, 0) + 1
            
            logger.info(f"数据源贡献: {source_count}")
            
            # 显示前5只股票
            logger.info("前5只股票:")
            for i, stock in enumerate(stocks[:5], 1):
                logger.info(f"  {i}. {stock['name']}({stock['ts_code']}) - 概念: {stock['concepts']}")
                logger.info(f"     数据源: {stock['data_source']}")
        else:
            logger.warning(f"未找到相关股票")
    
    # 测试资金流向数据
    if stocks:
        logger.info("\n测试资金流向数据获取")
        stock_codes = [s['ts_code'] for s in stocks[:10]]
        money_data = collector.get_money_flow_data(stock_codes)
        
        if money_data:
            logger.info(f"成功获取 {len(money_data)} 只股票的资金流向数据")
            for ts_code, data in list(money_data.items())[:3]:
                logger.info(f"  {ts_code}: 日流入={data['daily_net_inflow']/10000:.2f}万")
        else:
            logger.warning("未获取到资金流向数据")


def test_concept_matching():
    """测试概念匹配功能"""
    logger.info("\n=== 测试概念匹配功能 ===")
    
    collector = ConceptDataCollector()
    
    # 测试不同的概念名称变体
    test_cases = [
        ["储能", "储能概念"],  # 测试概念名称差异
        ["人工智能", "AI"],    # 测试同义词
        ["新能源", "新能源汽车"]  # 测试相关概念
    ]
    
    for concepts in test_cases:
        logger.info(f"\n测试概念组: {concepts}")
        stocks = collector.get_concept_stocks(concepts)
        
        if stocks:
            # 统计包含多个概念的股票
            multi_concept_stocks = [s for s in stocks if len(s['concepts']) > 1]
            logger.info(f"总股票数: {len(stocks)}, 多概念股票数: {len(multi_concept_stocks)}")
            
            if multi_concept_stocks:
                logger.info("多概念股票示例:")
                for stock in multi_concept_stocks[:3]:
                    logger.info(f"  {stock['name']}: {stock['concepts']}")
        else:
            logger.info("未找到相关股票")


def main():
    """主函数"""
    try:
        # 测试数据源
        test_data_sources()
        
        # 测试概念匹配
        test_concept_matching()
        
        logger.info("\n=== 测试完成 ===")
        
    except Exception as e:
        logger.error(f"测试失败: {e}", exc_info=True)


if __name__ == "__main__":
    main()