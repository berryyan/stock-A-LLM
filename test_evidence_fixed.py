#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
修复后的证据系统测试脚本
修复了RAGAgentModular的方法调用问题
"""

import logging
import sys
import os

# 添加项目根目录到系统路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from utils.concept.evidence_collector import EvidenceCollector
from utils.concept.evidence_collector_optimized import EvidenceCollectorOptimized

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def test_evidence_collector_basic():
    """测试基础证据收集功能（不包含RAG）"""
    logger.info("=== 测试基础证据收集功能 ===")
    
    # 测试原版收集器
    collector = EvidenceCollector()
    
    test_cases = [
        {
            'ts_code': '300750.SZ',
            'name': '宁德时代',
            'concepts': ['储能', '锂电池']
        },
        {
            'ts_code': '600519.SH',
            'name': '贵州茅台',
            'concepts': ['白酒', '消费']
        }
    ]
    
    for case in test_cases:
        logger.info(f"\n测试: {case['name']}({case['ts_code']})")
        
        # 只测试软件收录和互动平台
        try:
            # 软件收录证据
            software_ev = collector._collect_software_evidence(
                case['ts_code'], case['concepts']
            )
            logger.info(f"  软件收录证据: {len(software_ev)}条")
            for ev in software_ev[:2]:
                logger.info(f"    - {ev['source']}: {ev['content']}")
            
            # 互动平台证据
            interaction_ev = collector._collect_interaction_evidence(
                case['ts_code'], case['concepts']
            )
            logger.info(f"  互动平台证据: {len(interaction_ev)}条")
            for ev in interaction_ev[:2]:
                logger.info(f"    - {ev['source']}: {ev['content'][:50]}...")
            
        except Exception as e:
            logger.error(f"  收集证据失败: {e}")


def test_rag_agent_query():
    """测试RAGAgentModular的query方法"""
    logger.info("\n=== 测试RAGAgentModular查询 ===")
    
    try:
        from agents.rag_agent_modular import RAGAgentModular
        
        rag_agent = RAGAgentModular()
        
        # 测试查询
        test_queries = [
            "贵州茅台2023年年报中提到的主营业务是什么？",
            "宁德时代最新的公告内容"
        ]
        
        for query in test_queries:
            logger.info(f"\n查询: {query}")
            
            try:
                result = rag_agent.query(query)
                
                if isinstance(result, dict):
                    logger.info(f"  返回类型: 字典")
                    logger.info(f"  成功: {result.get('success', False)}")
                    
                    if result.get('success'):
                        content = result.get('result', '')
                        logger.info(f"  结果长度: {len(content)}字符")
                        logger.info(f"  结果预览: {content[:100]}...")
                    else:
                        logger.info(f"  错误: {result.get('error', '未知错误')}")
                else:
                    logger.warning(f"  意外的返回类型: {type(result)}")
                    
            except Exception as e:
                logger.error(f"  查询异常: {e}")
                
    except Exception as e:
        logger.error(f"RAGAgentModular初始化失败: {e}")


def test_evidence_with_rag():
    """测试包含RAG的完整证据收集"""
    logger.info("\n=== 测试完整证据收集（含RAG）===")
    
    collector_v2 = EvidenceCollectorOptimized()
    
    # 只测试一个股票，避免长时间运行
    test_stock = {
        'ts_code': '600519.SH',
        'name': '贵州茅台',
        'concepts': ['白酒']
    }
    
    logger.info(f"测试股票: {test_stock['name']}")
    
    try:
        # 收集所有证据
        evidence = collector_v2.collect_evidence(
            ts_code=test_stock['ts_code'],
            concepts=test_stock['concepts']
        )
        
        # 显示各类证据
        logger.info("\n证据收集结果:")
        for ev_type, ev_list in evidence.items():
            logger.info(f"\n{ev_type}证据 ({len(ev_list)}条):")
            for i, ev in enumerate(ev_list[:2], 1):
                logger.info(f"  {i}. {ev.get('source', 'N/A')}: {ev.get('content', 'N/A')[:80]}...")
                if 'score' in ev:
                    logger.info(f"     得分: {ev['score']}分")
        
        # 计算总分
        scores = collector_v2.calculate_total_score(evidence)
        logger.info(f"\n评分汇总:")
        logger.info(f"  软件收录: {scores['software']}/40")
        logger.info(f"  财报证据: {scores['report']}/30")
        logger.info(f"  互动平台: {scores['interaction']}/20")
        logger.info(f"  公告证据: {scores['announcement']}/10")
        logger.info(f"  总分: {scores['total']}/100")
        
    except Exception as e:
        logger.error(f"证据收集失败: {e}", exc_info=True)


def test_performance_comparison():
    """对比原版和优化版的性能"""
    logger.info("\n=== 性能对比测试 ===")
    
    import time
    
    test_params = {
        'ts_code': '000001.SZ',
        'concepts': ['银行', '金融']
    }
    
    # 测试原版
    collector_v1 = EvidenceCollector()
    start = time.time()
    
    # 只测试非RAG部分
    software_ev = collector_v1._collect_software_evidence(
        test_params['ts_code'], test_params['concepts']
    )
    interaction_ev = collector_v1._collect_interaction_evidence(
        test_params['ts_code'], test_params['concepts']
    )
    
    v1_time = time.time() - start
    logger.info(f"原版收集耗时: {v1_time:.3f}秒")
    logger.info(f"  证据数: 软件{len(software_ev)}, 互动{len(interaction_ev)}")
    
    # 测试优化版
    collector_v2 = EvidenceCollectorOptimized()
    start = time.time()
    
    # 完整的并行收集（不含RAG）
    evidence = collector_v2._collect_evidence_parallel(
        test_params['ts_code'], test_params['concepts']
    )
    
    v2_time = time.time() - start
    logger.info(f"\n优化版收集耗时: {v2_time:.3f}秒")
    logger.info(f"  证据数: 软件{len(evidence.get('software', []))}, "
               f"互动{len(evidence.get('interaction', []))}")
    
    if v1_time > 0 and v2_time > 0:
        speedup = v1_time / v2_time
        logger.info(f"\n性能提升: {speedup:.1f}倍")


def main():
    """主函数"""
    logger.info("修复后的证据系统测试开始")
    logger.info("="*60)
    
    try:
        # 1. 基础功能测试
        test_evidence_collector_basic()
        
        # 2. 测试RAG查询
        test_rag_agent_query()
        
        # 3. 完整证据收集测试
        test_evidence_with_rag()
        
        # 4. 性能对比
        test_performance_comparison()
        
        logger.info("\n" + "="*60)
        logger.info("测试完成！")
        
    except Exception as e:
        logger.error(f"测试过程出错: {e}", exc_info=True)


if __name__ == "__main__":
    main()