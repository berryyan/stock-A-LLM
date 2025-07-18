#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
简化的性能测试脚本
只测试软件收录和互动平台，不测试RAG
"""

import logging
import sys
import time

# 添加项目根目录到系统路径
sys.path.insert(0, '/mnt/e/PycharmProjects/stock_analysis_system')

from utils.concept.evidence_collector_optimized import EvidenceCollectorOptimized

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def test_performance_without_rag():
    """测试不包含RAG的性能"""
    logger.info("=== 性能测试（不含RAG） ===")
    
    collector = EvidenceCollectorOptimized()
    
    # 测试股票
    test_stocks = [
        {'ts_code': '300750.SZ', 'name': '宁德时代', 'concepts': ['储能', '锂电池']},
        {'ts_code': '002594.SZ', 'name': '比亚迪', 'concepts': ['新能源汽车', '电池']},
        {'ts_code': '600519.SH', 'name': '贵州茅台', 'concepts': ['白酒', '消费']}
    ]
    
    logger.info(f"测试{len(test_stocks)}只股票")
    
    # 第一轮：测试首次查询
    logger.info("\n第一轮：首次查询")
    first_round_times = []
    
    for stock in test_stocks:
        start = time.time()
        
        # 只收集软件和互动证据
        software_ev = collector._collect_software_evidence(
            stock['ts_code'], stock['concepts']
        )
        interaction_ev = collector._collect_interaction_evidence(
            stock['ts_code'], stock['concepts']
        )
        
        duration = time.time() - start
        first_round_times.append(duration)
        
        logger.info(f"{stock['name']}: {duration:.3f}秒 "
                   f"(软件{len(software_ev)}条, 互动{len(interaction_ev)}条)")
    
    # 第二轮：测试缓存效果
    logger.info("\n第二轮：缓存查询")
    second_round_times = []
    
    for stock in test_stocks:
        start = time.time()
        
        # 使用完整的collect_evidence方法测试缓存
        evidence = collector.collect_evidence(
            stock['ts_code'], 
            stock['concepts']
        )
        
        duration = time.time() - start
        second_round_times.append(duration)
        
        logger.info(f"{stock['name']}: {duration:.3f}秒 (从缓存)")
    
    # 统计结果
    logger.info("\n=== 性能统计 ===")
    logger.info(f"首次查询平均: {sum(first_round_times) / len(first_round_times):.3f}秒")
    logger.info(f"缓存查询平均: {sum(second_round_times) / len(second_round_times):.3f}秒")
    
    # 显示缓存统计
    stats = collector.get_performance_stats()
    cache_stats = stats['cache_stats']
    logger.info(f"\n缓存统计:")
    logger.info(f"  命中率: {cache_stats['hit_rate']:.1%}")
    logger.info(f"  缓存大小: {cache_stats['size']}/{cache_stats['max_size']}")
    logger.info(f"  命中次数: {cache_stats['hits']}")
    logger.info(f"  未命中次数: {cache_stats['misses']}")


def test_parallel_performance():
    """测试并行性能"""
    logger.info("\n\n=== 并行性能测试 ===")
    
    collector = EvidenceCollectorOptimized()
    
    test_params = {
        'ts_code': '000001.SZ',
        'concepts': ['银行', '金融', '大型商业银行']
    }
    
    # 测试并行收集（包含所有4种证据类型）
    logger.info("测试并行收集所有证据类型")
    
    start = time.time()
    evidence = collector._collect_evidence_parallel(
        test_params['ts_code'],
        test_params['concepts']
    )
    parallel_time = time.time() - start
    
    logger.info(f"并行收集耗时: {parallel_time:.3f}秒")
    logger.info(f"收集到的证据:")
    for ev_type, ev_list in evidence.items():
        if isinstance(ev_list, list):
            logger.info(f"  {ev_type}: {len(ev_list)}条")
        else:
            logger.info(f"  {ev_type}: 错误")


def test_cache_hit_rate():
    """测试缓存命中率"""
    logger.info("\n\n=== 缓存命中率测试 ===")
    
    collector = EvidenceCollectorOptimized()
    
    # 模拟真实使用场景
    queries = [
        {'ts_code': '600519.SH', 'concepts': ['白酒']},
        {'ts_code': '000858.SZ', 'concepts': ['白酒']},
        {'ts_code': '600519.SH', 'concepts': ['白酒']},  # 重复
        {'ts_code': '002304.SZ', 'concepts': ['白酒']},
        {'ts_code': '000858.SZ', 'concepts': ['白酒']},  # 重复
        {'ts_code': '600519.SH', 'concepts': ['白酒', '消费']},  # 不同概念
    ]
    
    for i, query in enumerate(queries, 1):
        logger.info(f"\n查询{i}: {query['ts_code']} - {query['concepts']}")
        collector.collect_evidence(**query)
        
        # 显示当前缓存状态
        stats = collector.get_performance_stats()['cache_stats']
        logger.info(f"  当前命中率: {stats['hit_rate']:.1%} "
                   f"(命中{stats['hits']}, 未命中{stats['misses']})")


def main():
    """主函数"""
    try:
        # 1. 基础性能测试
        test_performance_without_rag()
        
        # 2. 并行性能测试
        test_parallel_performance()
        
        # 3. 缓存命中率测试
        test_cache_hit_rate()
        
        logger.info("\n\n=== 性能测试完成 ===")
        
    except Exception as e:
        logger.error(f"测试失败: {e}", exc_info=True)


if __name__ == "__main__":
    main()