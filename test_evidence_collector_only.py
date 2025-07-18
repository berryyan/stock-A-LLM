#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试证据收集器（不包含RAG）
"""

import logging
import sys

# 添加项目根目录到系统路径
sys.path.insert(0, '/mnt/e/PycharmProjects/stock_analysis_system')

from utils.concept.evidence_collector import EvidenceCollector

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
    
    # 测试股票
    test_cases = [
        {
            'ts_code': '300750.SZ',
            'name': '宁德时代',
            'concepts': ['储能', '锂电池']
        },
        {
            'ts_code': '002594.SZ',
            'name': '比亚迪',
            'concepts': ['新能源汽车', '电池']
        }
    ]
    
    for case in test_cases:
        logger.info(f"\n测试股票: {case['name']}({case['ts_code']})")
        logger.info(f"概念: {case['concepts']}")
        
        # 只测试软件收录和互动平台（不调用RAG）
        evidence = {
            'software': [],
            'report': [],
            'interaction': [],
            'announcement': []
        }
        
        try:
            # 收集软件收录证据
            evidence['software'] = collector._collect_software_evidence(
                case['ts_code'], case['concepts']
            )
            logger.info(f"软件收录证据: {len(evidence['software'])}条")
            for ev in evidence['software']:
                logger.info(f"  - {ev['source']}: {ev['content']} (得分: {ev['score']})")
            
            # 收集互动平台证据
            evidence['interaction'] = collector._collect_interaction_evidence(
                case['ts_code'], case['concepts']
            )
            logger.info(f"互动平台证据: {len(evidence['interaction'])}条")
            for ev in evidence['interaction'][:3]:  # 只显示前3条
                if ev.get('negative'):
                    logger.info(f"  - {ev['source']}: {ev['content']} (否定证据)")
                else:
                    logger.info(f"  - {ev['source']}: {ev['content'][:50]}... (得分: {ev['score']})")
            
            # 计算得分
            scores = collector.calculate_total_score(evidence)
            logger.info(f"\n得分汇总:")
            logger.info(f"  软件收录: {scores['software']}/40")
            logger.info(f"  互动平台: {scores['interaction']}/20")
            logger.info(f"  总分（不含财报/公告）: {scores['software'] + scores['interaction']}/60")
            
        except Exception as e:
            logger.error(f"收集证据失败: {e}", exc_info=True)


def main():
    """主函数"""
    try:
        test_evidence_collector()
        logger.info("\n\n=== 测试完成 ===")
    except Exception as e:
        logger.error(f"测试失败: {e}", exc_info=True)


if __name__ == "__main__":
    main()