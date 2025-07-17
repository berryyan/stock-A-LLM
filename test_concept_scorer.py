#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试概念股评分计算器
"""

import logging
import sys
from typing import Dict, List, Any
from datetime import datetime

# 添加项目根目录到系统路径
sys.path.insert(0, '/mnt/e/PycharmProjects/stock_analysis_system')

from utils.concept.concept_scorer import ConceptScorer
from utils.concept.money_flow_collector import MoneyFlowCollector
from utils.concept.technical_collector import TechnicalCollector
from utils.concept.concept_data_collector import ConceptDataCollector
from database.mysql_connector import MySQLConnector

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def test_basic_scoring():
    """测试基础评分功能"""
    logger.info("=== 测试基础评分功能 ===")
    
    scorer = ConceptScorer()
    
    # 准备测试数据
    concept_stocks = [
        {
            'ts_code': '000001.SZ',
            'name': '平安银行',
            'concepts': ['金融科技', '银行'],
            'data_source': ['THS', 'DC'],
            'first_limit_date': '2025-07-10',
            'financial_report_mention': True,
            'interaction_mention': False,
            'announcement_mention': True,
            'sector_rank_pct': 0.15
        },
        {
            'ts_code': '600519.SH',
            'name': '贵州茅台',
            'concepts': ['白酒'],
            'data_source': ['THS'],
            'first_limit_date': None,
            'financial_report_mention': False,
            'interaction_mention': False,
            'announcement_mention': False,
            'sector_rank_pct': 0.5
        },
        {
            'ts_code': '002415.SZ',
            'name': '海康威视',
            'concepts': ['安防', 'AI'],
            'data_source': ['DC'],
            'first_limit_date': '2025-07-15',
            'financial_report_mention': True,
            'interaction_mention': True,
            'announcement_mention': True,
            'sector_rank_pct': 0.05
        }
    ]
    
    technical_data = {
        '000001.SZ': {
            'latest_macd': 0.15,
            'latest_dif': 0.20,
            'ma5': 12.5,
            'ma10': 12.3,
            'macd_above_water_date': '2025-07-16'
        },
        '600519.SH': {
            'latest_macd': -0.05,
            'latest_dif': -0.10,
            'ma5': 1800,
            'ma10': 1850
        },
        '002415.SZ': {
            'latest_macd': 0.25,
            'latest_dif': 0.30,
            'ma5': 45.8,
            'ma10': 44.2,
            'macd_above_water_date': '2025-07-17'
        }
    }
    
    money_flow_data = {
        '000001.SZ': {
            'daily_net_inflow': 5000000,
            'weekly_net_inflow': 25000000,
            'continuous_inflow_days': 4,
            'net_inflow_pct': 0.85
        },
        '600519.SH': {
            'daily_net_inflow': -10000000,
            'weekly_net_inflow': -50000000,
            'continuous_inflow_days': 0,
            'net_inflow_pct': 0.15
        },
        '002415.SZ': {
            'daily_net_inflow': 15000000,
            'weekly_net_inflow': 80000000,
            'continuous_inflow_days': 6,
            'net_inflow_pct': 0.95
        }
    }
    
    # 测试不同权重配置
    weight_configs = [
        {
            'name': '默认权重',
            'weights': {
                'concept_relevance': 0.4,
                'money_flow': 0.3,
                'technical': 0.3
            }
        },
        {
            'name': '概念优先',
            'weights': {
                'concept_relevance': 0.6,
                'money_flow': 0.2,
                'technical': 0.2
            }
        },
        {
            'name': '资金优先',
            'weights': {
                'concept_relevance': 0.2,
                'money_flow': 0.5,
                'technical': 0.3
            }
        }
    ]
    
    for config in weight_configs:
        logger.info(f"\n使用权重配置: {config['name']}")
        logger.info(f"权重: {config['weights']}")
        
        # 计算得分
        scored_stocks = scorer.calculate_scores(
            concept_stocks,
            technical_data,
            money_flow_data,
            config['weights']
        )
        
        # 显示结果
        print(f"\n{config['name']}评分结果:")
        print("-" * 80)
        print(f"{'股票':<10} {'总分':<8} {'概念':<8} {'资金':<8} {'技术':<8} {'详情'}")
        print("-" * 80)
        
        for stock in scored_stocks:
            details = []
            
            # 概念详情
            concept_details = stock['score_details']['concept']
            if concept_details['is_member']:
                details.append('成分股')
            if concept_details['first_limit']:
                details.append('率先涨停')
            if concept_details['financial_mention']:
                details.append('财报提及')
            if concept_details['sector_active']:
                details.append('板块活跃')
            
            # 资金详情
            money_details = stock['score_details']['money_flow']
            if money_details.get('daily_inflow'):
                details.append('日流入')
            if money_details.get('weekly_inflow'):
                details.append('周流入')
            if money_details.get('continuous_days', 0) >= 3:
                details.append(f"连续{money_details['continuous_days']}天")
            
            # 技术详情
            tech_details = stock['score_details']['technical']
            if tech_details.get('macd_above_water'):
                details.append('MACD水上')
            if tech_details.get('ma5_gt_ma10'):
                details.append('MA5>MA10')
            
            print(f"{stock['name']:<10} {stock['total_score']:<8.1f} "
                  f"{stock['concept_score']:<8.1f} {stock['money_score']:<8.1f} "
                  f"{stock['technical_score']:<8.1f} {', '.join(details)}")
    
    # 测试过滤功能
    logger.info("\n=== 测试过滤功能 ===")
    
    # 使用默认权重计算
    scored_stocks = scorer.calculate_scores(
        concept_stocks,
        technical_data,
        money_flow_data,
        {'concept_relevance': 0.4, 'money_flow': 0.3, 'technical': 0.3}
    )
    
    # 测试不同过滤条件
    filter_tests = [
        {'min_total_score': 60, 'desc': '总分>=60'},
        {'min_concept_score': 20, 'desc': '概念得分>=20'},
        {'min_money_score': 20, 'desc': '资金得分>=20'},
        {'min_technical_score': 20, 'desc': '技术得分>=20'},
        {
            'min_total_score': 70,
            'min_concept_score': 20,
            'min_money_score': 15,
            'desc': '总分>=70 且 概念>=20 且 资金>=15'
        }
    ]
    
    for test in filter_tests:
        desc = test.pop('desc')
        filtered = scorer.filter_by_score(scored_stocks, **test)
        
        print(f"\n过滤条件: {desc}")
        print(f"符合条件的股票: {len(filtered)}只")
        for stock in filtered:
            print(f"  - {stock['name']}: 总分{stock['total_score']:.1f} "
                  f"(概念{stock['concept_score']:.1f}, "
                  f"资金{stock['money_score']:.1f}, "
                  f"技术{stock['technical_score']:.1f})")


def test_with_real_data():
    """使用真实数据测试"""
    logger.info("\n=== 使用真实数据测试 ===")
    
    # 初始化各组件
    concept_collector = ConceptDataCollector()  # 不需要参数
    money_collector = MoneyFlowCollector()  # 不需要参数
    tech_collector = TechnicalCollector()  # 不需要参数
    scorer = ConceptScorer()
    
    # 获取"储能"概念股
    concept_name = "储能"
    logger.info(f"获取{concept_name}概念股...")
    
    concept_stocks = concept_collector.get_concept_stocks([concept_name])
    if not concept_stocks:
        logger.error("未找到概念股数据")
        return
    
    logger.info(f"找到 {len(concept_stocks)} 只{concept_name}概念股")
    
    # 限制测试数量
    test_stocks = concept_stocks[:10]
    ts_codes = [s['ts_code'] for s in test_stocks]
    
    # 获取资金流向数据
    logger.info("获取资金流向数据...")
    money_data = money_collector.get_batch_money_flow(ts_codes)
    
    # 获取技术指标数据
    logger.info("获取技术指标数据...")
    tech_data = tech_collector.get_latest_technical_indicators(ts_codes)
    
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
    print(f"\n{concept_name}概念股评分结果 (前10只):")
    print("=" * 100)
    print(f"{'排名':<6} {'代码':<10} {'名称':<10} {'总分':<8} "
          f"{'概念':<8} {'资金':<8} {'技术':<8} {'评分理由'}")
    print("=" * 100)
    
    for i, stock in enumerate(scored_stocks, 1):
        # 构建评分理由
        reasons = []
        
        # 概念关联理由
        if stock['concept_score'] >= 20:
            reasons.append("概念关联强")
        
        # 资金流向理由
        money_details = stock['score_details']['money_flow']
        if money_details.get('daily_inflow') and money_details.get('weekly_inflow'):
            reasons.append("日周双流入")
        if money_details.get('continuous_days', 0) >= 5:
            reasons.append(f"连续{money_details['continuous_days']}天流入")
        
        # 技术形态理由
        tech_details = stock['score_details']['technical']
        if tech_details.get('macd_above_water'):
            reasons.append("MACD水上")
        if tech_details.get('ma5_gt_ma10'):
            reasons.append("均线多头")
        
        print(f"{i:<6} {stock['ts_code']:<10} {stock['name']:<10} "
              f"{stock['total_score']:<8.1f} {stock['concept_score']:<8.1f} "
              f"{stock['money_score']:<8.1f} {stock['technical_score']:<8.1f} "
              f"{'; '.join(reasons)}")
    
    # 筛选优质股票
    print("\n优质股票筛选 (总分>=60):")
    high_score_stocks = scorer.filter_by_score(scored_stocks, min_total_score=60)
    
    if high_score_stocks:
        for stock in high_score_stocks[:5]:
            print(f"\n【{stock['name']}】{stock['ts_code']}")
            print(f"  总分: {stock['total_score']:.1f}")
            print(f"  概念关联: {stock['concept_score']:.1f}/40")
            print(f"  资金流向: {stock['money_score']:.1f}/30")
            print(f"  技术形态: {stock['technical_score']:.1f}/30")
            
            # 详细分析
            money_details = stock['score_details']['money_flow']
            tech_details = stock['score_details']['technical']
            
            if money_details.get('daily_inflow'):
                print(f"  - 日资金净流入")
            if money_details.get('weekly_inflow'):
                print(f"  - 周资金净流入")
            if tech_details.get('macd_above_water'):
                print(f"  - MACD指标水上")
            if tech_details.get('ma5_gt_ma10'):
                print(f"  - 均线多头排列")
    else:
        print("  暂无符合条件的股票")


def main():
    """主函数"""
    try:
        # 测试基础评分功能
        test_basic_scoring()
        
        # 测试真实数据
        print("\n" + "="*80 + "\n")
        # 自动运行真实数据测试
        test_with_real_data()
            
    except Exception as e:
        logger.error(f"测试失败: {e}", exc_info=True)


if __name__ == "__main__":
    main()