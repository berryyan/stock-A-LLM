#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
简化的证据系统测试
"""

import logging
import sys

# 添加项目根目录到系统路径
sys.path.insert(0, '/mnt/e/PycharmProjects/stock_analysis_system')

from utils.concept.evidence_collector import EvidenceCollector
from utils.concept.concept_scorer_v2 import ConceptScorerV2

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def test_evidence_system():
    """测试完整的证据系统"""
    logger.info("=== 测试证据系统 ===")
    
    # 创建收集器和评分器
    collector = EvidenceCollector()
    scorer = ConceptScorerV2()
    
    # 测试股票
    test_stock = {
        'ts_code': '300750.SZ',
        'name': '宁德时代',
        'concepts': ['储能', '锂电池'],
        'data_source': ['THS', 'DC']  # 假设在这两个数据源中
    }
    
    logger.info(f"\n测试股票: {test_stock['name']}({test_stock['ts_code']})")
    logger.info(f"概念: {test_stock['concepts']}")
    
    # 1. 收集证据
    logger.info("\n收集证据...")
    evidence = collector.collect_evidence(
        ts_code=test_stock['ts_code'],
        concepts=test_stock['concepts'],
        data_sources=test_stock['data_source']
    )
    
    # 2. 显示证据
    logger.info("\n收集到的证据:")
    
    # 软件收录证据
    if evidence.get('software'):
        logger.info("\n【软件收录证据】")
        for ev in evidence['software']:
            logger.info(f"  - {ev['source']}: {ev['content']} (得分: {ev['score']}分)")
    
    # 互动平台证据
    if evidence.get('interaction'):
        logger.info("\n【互动平台证据】")
        for ev in evidence['interaction']:
            if ev.get('negative'):
                logger.info(f"  - {ev['source']} [{ev.get('date', '')}]: {ev['content']} (否定证据)")
            else:
                logger.info(f"  - {ev['source']} [{ev.get('date', '')}]: {ev['content']} (得分: {ev['score']}分)")
    else:
        logger.info("\n【互动平台证据】无")
    
    # 3. 计算得分
    scores = collector.calculate_total_score(evidence)
    logger.info(f"\n【得分汇总】")
    logger.info(f"  软件收录: {scores['software']}/40分")
    logger.info(f"  财报证据: {scores['report']}/30分")
    logger.info(f"  互动平台: {scores['interaction']}/20分")
    logger.info(f"  公告证据: {scores['announcement']}/10分")
    logger.info(f"  总分: {scores['total']}/100分")
    
    # 4. 关联强度判定
    if scores['total'] >= 80:
        level = "核心概念股"
    elif scores['total'] >= 60:
        level = "重要概念股"
    elif scores['total'] >= 40:
        level = "相关概念股"
    elif scores['total'] >= 20:
        level = "边缘概念股"
    else:
        level = "无关股票"
    
    logger.info(f"\n【关联强度】{level}")
    
    # 5. 测试评分器格式化
    test_stock['evidence'] = evidence
    test_stock['evidence_list'] = collector.flatten_evidence(evidence)
    test_stock['evidence_scores'] = scores
    test_stock['concept_score'] = scores['total']
    test_stock['relevance_level'] = level
    
    logger.info(f"\n【格式化报告】")
    report = scorer.format_evidence_report(test_stock)
    print("\n" + report)


def test_interaction_search():
    """测试互动平台搜索"""
    logger.info("\n\n=== 测试互动平台搜索 ===")
    
    from database.mysql_connector import MySQLConnector
    db = MySQLConnector()
    
    # 搜索宁德时代的储能相关互动
    query = """
    SELECT trade_date, q, a
    FROM tu_irm_qa_sz
    WHERE ts_code = '300750.SZ'
    AND (q LIKE '%储能%' OR a LIKE '%储能%')
    ORDER BY trade_date DESC
    LIMIT 3
    """
    
    results = db.execute_query(query)
    
    if results:
        logger.info(f"\n找到 {len(results)} 条储能相关互动:")
        for i, row in enumerate(results, 1):
            logger.info(f"\n记录{i}:")
            logger.info(f"  日期: {row['trade_date']}")
            logger.info(f"  问: {row['q'][:100]}...")
            logger.info(f"  答: {row['a'][:150]}...")
    else:
        logger.info("\n未找到储能相关互动")


def main():
    """主函数"""
    try:
        # 1. 测试证据系统
        test_evidence_system()
        
        # 2. 测试互动平台
        test_interaction_search()
        
        logger.info("\n\n=== 测试完成 ===")
        
    except Exception as e:
        logger.error(f"测试失败: {e}", exc_info=True)


if __name__ == "__main__":
    main()