#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试优化后的评分算法
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


def test_optimized_scoring():
    """测试优化后的评分"""
    logger.info("=== 测试优化后的评分算法 ===")
    
    # 初始化各组件
    concept_collector = ConceptDataCollector()
    money_collector = MoneyFlowCollector()
    tech_collector = TechnicalCollector()
    scorer = ConceptScorer()
    
    # 获取测试数据
    concepts = ["储能"]
    logger.info(f"获取{concepts}概念股...")
    concept_stocks = concept_collector.get_concept_stocks(concepts)
    
    if not concept_stocks:
        logger.error("未找到概念股")
        return
    
    # 测试前20只
    test_size = 20
    test_stocks = concept_stocks[:test_size]
    ts_codes = [s['ts_code'] for s in test_stocks]
    
    logger.info(f"获取 {test_size} 只股票的数据...")
    money_data = money_collector.get_batch_money_flow(ts_codes, days=5)
    tech_data = tech_collector.get_latest_technical_indicators(ts_codes, days=21)
    
    # 使用默认权重计算评分
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
    
    # 显示评分结果
    print(f"\n优化后的评分结果（储能概念股前20只）:")
    print("=" * 120)
    print(f"{'排名':<6} {'代码':<12} {'名称':<12} {'总分':<8} "
          f"{'概念':<8} {'资金':<8} {'技术':<8} {'评分详情'}")
    print("=" * 120)
    
    # 按总分排序
    sorted_stocks = sorted(scored_stocks, key=lambda x: x['total_score'], reverse=True)
    
    # 统计信息
    total_scores = [s['total_score'] for s in sorted_stocks]
    avg_score = sum(total_scores) / len(total_scores)
    max_score = max(total_scores)
    min_score = min(total_scores)
    
    for i, stock in enumerate(sorted_stocks, 1):
        # 构建评分详情
        details = []
        
        # 概念详情
        concept_details = stock['score_details']['concept']
        if concept_details.get('is_member'):
            details.append(f"成分股")
        
        # 资金详情
        money_details = stock['score_details']['money_flow']
        if money_details.get('daily_inflow'):
            details.append("日流入")
        if money_details.get('continuous_days', 0) >= 3:
            details.append(f"连{money_details['continuous_days']}天")
        
        # 技术详情
        tech_details = stock['score_details']['technical']
        if tech_details.get('macd_above_water'):
            details.append("MACD+")
        if tech_details.get('ma5_gt_ma10'):
            details.append("MA+")
        
        print(f"{i:<6} {stock['ts_code']:<12} {stock['name']:<12} "
              f"{stock['total_score']:<8.1f} {stock['concept_score']:<8.1f} "
              f"{stock['money_score']:<8.1f} {stock['technical_score']:<8.1f} "
              f"{'; '.join(details)}")
    
    # 显示统计信息
    print("\n" + "=" * 120)
    print(f"统计信息:")
    print(f"  平均分: {avg_score:.1f}")
    print(f"  最高分: {max_score:.1f}")
    print(f"  最低分: {min_score:.1f}")
    print(f"  60分以上: {len([s for s in sorted_stocks if s['total_score'] >= 60])}只")
    print(f"  50分以上: {len([s for s in sorted_stocks if s['total_score'] >= 50])}只")
    print(f"  40分以上: {len([s for s in sorted_stocks if s['total_score'] >= 40])}只")
    
    # 验证优化效果
    if max_score > 50:
        logger.info("\n✅ 评分优化成功！最高分超过50分")
    else:
        logger.warning("\n⚠️ 评分仍然偏低，可能需要进一步优化")
    
    return sorted_stocks


def main():
    """主函数"""
    try:
        sorted_stocks = test_optimized_scoring()
        
        # 详细分析前3名
        if sorted_stocks and len(sorted_stocks) >= 3:
            print("\n" + "=" * 120)
            print("前3名详细分析:")
            
            for i, stock in enumerate(sorted_stocks[:3], 1):
                print(f"\n【第{i}名】{stock['name']} ({stock['ts_code']})")
                print(f"  总分: {stock['total_score']:.1f}")
                print(f"  - 概念关联度: {stock['concept_score']:.1f}/40")
                print(f"  - 资金流向: {stock['money_score']:.1f}/30")
                print(f"  - 技术形态: {stock['technical_score']:.1f}/30")
                
                # 详细评分理由
                concept_details = stock['score_details']['concept']
                money_details = stock['score_details']['money_flow']
                tech_details = stock['score_details']['technical']
                
                print(f"  评分理由:")
                if concept_details.get('is_member'):
                    print(f"    - 概念成分股")
                if money_details.get('daily_inflow'):
                    print(f"    - 今日资金净流入")
                if money_details.get('continuous_days', 0) > 0:
                    print(f"    - 连续{money_details['continuous_days']}天资金流入")
                if tech_details.get('macd_above_water'):
                    print(f"    - MACD指标良好")
                if tech_details.get('ma5_gt_ma10'):
                    print(f"    - 均线多头排列")
        
    except Exception as e:
        logger.error(f"测试失败: {e}", exc_info=True)


if __name__ == "__main__":
    main()