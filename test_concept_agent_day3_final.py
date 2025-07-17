#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Concept Agent Day 3 综合测试
"""

import logging
import sys

# 添加项目根目录到系统路径
sys.path.insert(0, '/mnt/e/PycharmProjects/stock_analysis_system')

from utils.concept.concept_scorer import ConceptScorer
from utils.concept.money_flow_collector import MoneyFlowCollector
from utils.concept.technical_collector import TechnicalCollector
from utils.concept.concept_data_collector import ConceptDataCollector

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    """主函数"""
    logger.info("=== Concept Agent Day 3 综合测试 ===")
    
    try:
        # 初始化各组件
        concept_collector = ConceptDataCollector()
        money_collector = MoneyFlowCollector()
        tech_collector = TechnicalCollector()
        scorer = ConceptScorer()
        
        # 获取储能概念股
        concepts = ["储能"]
        logger.info(f"获取{concepts}概念股...")
        concept_stocks = concept_collector.get_concept_stocks(concepts)
        
        logger.info(f"找到 {len(concept_stocks)} 只概念股")
        
        # 测试前20只
        test_stocks = concept_stocks[:20]
        ts_codes = [s['ts_code'] for s in test_stocks]
        
        # 获取数据
        logger.info("获取资金流向和技术指标...")
        money_data = money_collector.get_batch_money_flow(ts_codes, days=5)
        tech_data = tech_collector.get_latest_technical_indicators(ts_codes, days=21)
        
        # 计算评分
        weights = {
            'concept_relevance': 0.4,
            'money_flow': 0.3,
            'technical': 0.3
        }
        
        scored_stocks = scorer.calculate_scores(
            test_stocks,
            tech_data,
            money_data,
            weights
        )
        
        # 显示结果
        print(f"\n储能概念股评分结果:")
        print("=" * 100)
        print(f"{'排名':<6} {'代码':<10} {'名称':<10} {'总分':<8} "
              f"{'概念':<8} {'资金':<8} {'技术':<8}")
        print("=" * 100)
        
        # 按总分排序
        sorted_stocks = sorted(scored_stocks, key=lambda x: x['total_score'], reverse=True)
        
        for i, stock in enumerate(sorted_stocks[:10], 1):
            print(f"{i:<6} {stock['ts_code']:<10} {stock['name']:<10} "
                  f"{stock['total_score']:<8.1f} {stock['concept_score']:<8.1f} "
                  f"{stock['money_score']:<8.1f} {stock['technical_score']:<8.1f}")
        
        # 统计
        high_score_count = len([s for s in scored_stocks if s['total_score'] >= 50])
        logger.info(f"\n高分股票(>=50分): {high_score_count}只")
        
        logger.info("\n=== Day 3 测试完成 ===")
        
    except Exception as e:
        logger.error(f"测试失败: {e}", exc_info=True)


if __name__ == "__main__":
    main()