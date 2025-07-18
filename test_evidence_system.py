#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试证据收集系统
验证软件收录、互动平台、年报、公告等证据收集功能
"""

import logging
import sys
import json
from datetime import datetime

# 添加项目根目录到系统路径
sys.path.insert(0, '/mnt/e/PycharmProjects/stock_analysis_system')

from utils.concept.evidence_collector import EvidenceCollector
from utils.concept.concept_scorer_v2 import ConceptScorerV2
from agents.concept.concept_agent import ConceptAgent

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def test_evidence_collector():
    """测试证据收集器"""
    logger.info("=== 测试证据收集器 ===")
    
    collector = EvidenceCollector()
    
    # 测试案例
    test_cases = [
        {
            'ts_code': '603421.SH',
            'name': '鼎信通讯',
            'concepts': ['储能'],
            'data_sources': ['THS']
        },
        {
            'ts_code': '300750.SZ',
            'name': '宁德时代',
            'concepts': ['锂电池', '储能'],
            'data_sources': ['THS', 'DC']
        },
        {
            'ts_code': '002594.SZ',
            'name': '比亚迪',
            'concepts': ['新能源汽车', '电池'],
            'data_sources': ['THS', 'DC', 'KPL']
        }
    ]
    
    for case in test_cases:
        logger.info(f"\n测试股票: {case['name']}({case['ts_code']})")
        logger.info(f"概念: {case['concepts']}")
        
        # 收集证据
        evidence = collector.collect_evidence(
            ts_code=case['ts_code'],
            concepts=case['concepts'],
            data_sources=case['data_sources']
        )
        
        # 打印证据
        for evidence_type, evidence_list in evidence.items():
            if evidence_list:
                logger.info(f"\n{evidence_type} 证据:")
                for ev in evidence_list:
                    logger.info(f"  - {ev['source']}: {ev['content']} (得分: {ev.get('score', 0)})")
        
        # 计算得分
        scores = collector.calculate_total_score(evidence)
        logger.info(f"\n得分汇总:")
        logger.info(f"  软件收录: {scores['software']}/40")
        logger.info(f"  财报证据: {scores['report']}/30")
        logger.info(f"  互动平台: {scores['interaction']}/20")
        logger.info(f"  公告证据: {scores['announcement']}/10")
        logger.info(f"  总分: {scores['total']}/100")


def test_concept_scorer_v2():
    """测试新版评分系统"""
    logger.info("\n\n=== 测试ConceptScorerV2 ===")
    
    scorer = ConceptScorerV2()
    
    # 测试股票列表
    test_stocks = [
        {
            'ts_code': '600519.SH',
            'name': '贵州茅台',
            'concepts': ['白酒', '消费'],
            'data_source': ['THS', 'DC']
        },
        {
            'ts_code': '000858.SZ',
            'name': '五粮液',
            'concepts': ['白酒'],
            'data_source': ['THS']
        }
    ]
    
    # 计算得分
    scored_stocks = scorer.calculate_scores_with_evidence(
        test_stocks,
        technical_data={},
        money_flow_data={}
    )
    
    # 打印结果
    for stock in scored_stocks:
        logger.info(f"\n{'='*60}")
        logger.info(scorer.format_evidence_report(stock))


def test_concept_agent_integration():
    """测试ConceptAgent集成"""
    logger.info("\n\n=== 测试ConceptAgent集成 ===")
    
    agent = ConceptAgent()
    
    # 测试查询
    test_query = "概念股分析：储能概念股有哪些？"
    
    logger.info(f"测试查询: {test_query}")
    
    try:
        result = agent.process_query(test_query)
        
        if result.success:
            logger.info("\n查询成功!")
            # 保存结果到文件
            with open('evidence_system_test_result.md', 'w', encoding='utf-8') as f:
                f.write(result.data)
            logger.info("结果已保存到 evidence_system_test_result.md")
        else:
            logger.error(f"查询失败: {result.error}")
            
    except Exception as e:
        logger.error(f"测试失败: {e}", exc_info=True)


def test_interaction_platform():
    """专门测试互动平台数据查询"""
    logger.info("\n\n=== 测试互动平台数据查询 ===")
    
    from database.mysql_connector import MySQLConnector
    db = MySQLConnector()
    
    # 查询包含"储能"的互动记录
    query = """
    SELECT ts_code, name, trade_date, q, a
    FROM tu_irm_qa_sh
    WHERE (q LIKE '%储能%' OR a LIKE '%储能%')
    ORDER BY trade_date DESC
    LIMIT 5
    """
    
    results = db.execute_query(query)
    
    logger.info(f"找到 {len(results)} 条相关记录:")
    for row in results:
        logger.info(f"\n股票: {row['ts_code']} {row['name']}")
        logger.info(f"日期: {row['trade_date']}")
        logger.info(f"问: {row['q'][:100]}...")
        logger.info(f"答: {row['a'][:100]}...")


def main():
    """主函数"""
    # 1. 测试证据收集器
    test_evidence_collector()
    
    # 2. 测试评分系统
    test_concept_scorer_v2()
    
    # 3. 测试互动平台
    test_interaction_platform()
    
    # 4. 测试完整集成（注意：这会调用RAG和LLM，可能较慢）
    # test_concept_agent_integration()
    
    logger.info("\n\n=== 测试完成 ===")


if __name__ == "__main__":
    main()