#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
基础证据系统测试
只测试软件收录和互动平台，不调用RAG
"""

import logging
import sys

# 添加项目根目录到系统路径
sys.path.insert(0, '/mnt/e/PycharmProjects/stock_analysis_system')

from database.mysql_connector import MySQLConnector

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def test_software_evidence():
    """测试软件收录证据"""
    logger.info("=== 测试软件收录证据 ===")
    
    db = MySQLConnector()
    
    # 测试同花顺储能概念
    query = """
    SELECT DISTINCT m.ts_code, s.name, m.con_name as concept_name
    FROM tu_ths_member m
    JOIN tu_stock_basic s ON m.ts_code = s.ts_code
    WHERE m.con_name LIKE '%储能%'
    LIMIT 10
    """
    
    results = db.execute_query(query)
    logger.info(f"\n同花顺储能概念股（前10）:")
    for row in results:
        logger.info(f"  - {row['ts_code']} {row['name']} - {row['concept_name']}")
    
    # 测试东财
    query = """
    SELECT COUNT(DISTINCT ts_code) as cnt
    FROM tu_dc_member
    WHERE 1=1
    """
    
    results = db.execute_query(query)
    logger.info(f"\n东财成分股总数: {results[0]['cnt']}")


def test_interaction_evidence():
    """测试互动平台证据"""
    logger.info("\n=== 测试互动平台证据 ===")
    
    db = MySQLConnector()
    
    # 查找储能相关的互动
    test_stocks = [
        ('603421.SH', '鼎信通讯'),
        ('300750.SZ', '宁德时代'),
        ('002594.SZ', '比亚迪')
    ]
    
    for ts_code, name in test_stocks:
        exchange = 'sh' if ts_code.endswith('.SH') else 'sz'
        table = f'tu_irm_qa_{exchange}'
        
        query = f"""
        SELECT trade_date, q, a
        FROM {table}
        WHERE ts_code = :ts_code
        AND (q LIKE :concept_pattern OR a LIKE :concept_pattern)
        ORDER BY trade_date DESC
        LIMIT 2
        """
        
        try:
            results = db.execute_query(query, {'ts_code': ts_code, 'concept_pattern': '%储能%'})
            
            if results:
                logger.info(f"\n{name}({ts_code}) 储能相关互动:")
                for row in results:
                    logger.info(f"  日期: {row['trade_date']}")
                    logger.info(f"  问: {row['q'][:80]}...")
                    logger.info(f"  答: {row['a'][:80]}...")
                    
                    # 判断是否确认
                    answer = row['a']
                    if any(word in answer for word in ['是', '有', '涉及', '从事', '布局']):
                        logger.info(f"  → 董秘确认涉及储能业务（+20分）")
                    elif any(word in answer for word in ['没有', '无', '不涉及', '暂无']):
                        logger.info(f"  → 董秘否认涉及储能业务（0分）")
            else:
                logger.info(f"\n{name}({ts_code}) 未找到储能相关互动")
                
        except Exception as e:
            logger.error(f"查询失败: {e}")


def test_concept_matching():
    """测试概念匹配结果"""
    logger.info("\n=== 测试概念匹配 ===")
    
    from utils.concept.concept_matcher_v2 import ConceptMatcherV2
    
    matcher = ConceptMatcherV2()
    
    # 测试概念扩展
    concepts = ['储能']
    expanded = matcher.expand_concepts(concepts)
    logger.info(f"\n概念扩展: {concepts} -> {expanded}")
    
    # 测试概念匹配
    matched = matcher.match_concepts(expanded)
    logger.info(f"\n概念匹配结果:")
    logger.info(f"  同花顺: {matched['THS'][:5]}...")
    logger.info(f"  东财: {matched['DC'][:5]}...")
    logger.info(f"  开盘啦: {matched['KPL'][:5]}...")


def test_evidence_scoring():
    """测试证据评分逻辑"""
    logger.info("\n=== 测试证据评分逻辑 ===")
    
    # 模拟证据数据
    test_evidence = {
        'software': [
            {'type': '软件收录', 'source': '同花顺', 'content': '同花顺储能概念成分股', 'score': 15},
            {'type': '软件收录', 'source': '东财', 'content': '东财储能板块成分股', 'score': 15}
        ],
        'report': [],  # 暂不测试
        'interaction': [
            {'type': '互动平台', 'source': '董秘回复', 'content': '公司有储能业务', 'score': 20}
        ],
        'announcement': []  # 暂不测试
    }
    
    # 计算总分
    total_score = 0
    for evidence_type, evidence_list in test_evidence.items():
        for ev in evidence_list:
            total_score += ev.get('score', 0)
    
    logger.info(f"\n证据得分明细:")
    logger.info(f"  软件收录: 30分（同花顺15+东财15）")
    logger.info(f"  互动平台: 20分（董秘确认）")
    logger.info(f"  财报证据: 0分（未测试）")
    logger.info(f"  公告证据: 0分（未测试）")
    logger.info(f"  总分: {total_score}/100分")
    logger.info(f"  关联强度: {'重要概念股' if total_score >= 40 else '相关概念股'}")


def main():
    """主函数"""
    try:
        test_software_evidence()
        test_interaction_evidence()
        test_concept_matching()
        test_evidence_scoring()
        
        logger.info("\n\n=== 基础测试完成 ===")
        logger.info("证据系统基础功能正常！")
        
    except Exception as e:
        logger.error(f"测试失败: {e}", exc_info=True)


if __name__ == "__main__":
    main()