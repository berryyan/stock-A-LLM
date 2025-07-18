#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
性能优化测试脚本
对比优化前后的性能差异
"""

import logging
import sys
import time
from typing import List, Dict, Any

# 添加项目根目录到系统路径
sys.path.insert(0, '/mnt/e/PycharmProjects/stock_analysis_system')

from utils.concept.evidence_collector import EvidenceCollector
from utils.concept.evidence_collector_optimized import EvidenceCollectorOptimized
from utils.concept.performance_optimizer import performance_monitor

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def test_single_stock_performance():
    """测试单只股票的性能"""
    logger.info("=== 单只股票性能测试 ===")
    
    # 测试参数
    test_stock = {
        'ts_code': '300750.SZ',
        'name': '宁德时代',
        'concepts': ['储能', '锂电池', '新能源']
    }
    
    # 测试原版收集器
    logger.info("\n1. 测试原版证据收集器")
    collector_v1 = EvidenceCollector()
    
    start_time = time.time()
    evidence_v1 = collector_v1.collect_evidence(
        ts_code=test_stock['ts_code'],
        concepts=test_stock['concepts'][:2]  # 只测试2个概念，避免RAG超时
    )
    v1_time = time.time() - start_time
    
    logger.info(f"原版耗时: {v1_time:.2f}秒")
    logger.info(f"证据数量: 软件{len(evidence_v1.get('software', []))}条, "
               f"互动{len(evidence_v1.get('interaction', []))}条")
    
    # 测试优化版收集器
    logger.info("\n2. 测试优化版证据收集器（首次查询）")
    collector_v2 = EvidenceCollectorOptimized()
    
    start_time = time.time()
    evidence_v2 = collector_v2.collect_evidence(
        ts_code=test_stock['ts_code'],
        concepts=test_stock['concepts'][:2]
    )
    v2_time_first = time.time() - start_time
    
    logger.info(f"优化版首次耗时: {v2_time_first:.2f}秒")
    logger.info(f"证据数量: 软件{len(evidence_v2.get('software', []))}条, "
               f"互动{len(evidence_v2.get('interaction', []))}条")
    
    # 测试缓存效果
    logger.info("\n3. 测试缓存效果（第二次查询）")
    start_time = time.time()
    evidence_v2_cached = collector_v2.collect_evidence(
        ts_code=test_stock['ts_code'],
        concepts=test_stock['concepts'][:2]
    )
    v2_time_cached = time.time() - start_time
    
    logger.info(f"优化版缓存查询耗时: {v2_time_cached:.2f}秒")
    
    # 性能对比
    logger.info("\n=== 性能对比 ===")
    logger.info(f"原版耗时: {v1_time:.2f}秒")
    logger.info(f"优化版首次: {v2_time_first:.2f}秒 (提升{((v1_time - v2_time_first) / v1_time * 100):.1f}%)")
    logger.info(f"优化版缓存: {v2_time_cached:.2f}秒 (提升{((v1_time - v2_time_cached) / v1_time * 100):.1f}%)")
    
    # 显示缓存统计
    stats = collector_v2.get_performance_stats()
    logger.info(f"\n缓存统计: {stats['cache_stats']}")


def test_batch_performance():
    """测试批量股票的性能"""
    logger.info("\n\n=== 批量股票性能测试 ===")
    
    # 测试股票列表
    test_stocks = [
        {'ts_code': '300750.SZ', 'concepts': ['储能', '锂电池']},
        {'ts_code': '002594.SZ', 'concepts': ['新能源汽车', '电池']},
        {'ts_code': '600519.SH', 'concepts': ['白酒', '消费']},
        {'ts_code': '000858.SZ', 'concepts': ['白酒', '品牌']},
        {'ts_code': '002714.SZ', 'concepts': ['牛肉', '食品']}
    ]
    
    # 使用优化版收集器
    collector = EvidenceCollectorOptimized()
    
    logger.info(f"测试{len(test_stocks)}只股票的证据收集")
    
    total_start = time.time()
    results = []
    
    for i, stock in enumerate(test_stocks, 1):
        logger.info(f"\n处理第{i}只股票: {stock['ts_code']}")
        
        start_time = time.time()
        evidence = collector.collect_evidence(
            ts_code=stock['ts_code'],
            concepts=stock['concepts']
        )
        duration = time.time() - start_time
        
        scores = collector.calculate_total_score(evidence)
        
        results.append({
            'ts_code': stock['ts_code'],
            'concepts': stock['concepts'],
            'duration': duration,
            'total_score': scores['total'],
            'evidence_count': sum(len(v) for v in evidence.values())
        })
        
        logger.info(f"  耗时: {duration:.2f}秒, 总分: {scores['total']}, "
                   f"证据数: {results[-1]['evidence_count']}")
    
    total_duration = time.time() - total_start
    
    # 汇总统计
    logger.info(f"\n=== 批量处理统计 ===")
    logger.info(f"总耗时: {total_duration:.2f}秒")
    logger.info(f"平均耗时: {total_duration / len(test_stocks):.2f}秒/股票")
    
    # 显示性能指标
    perf_stats = collector.get_performance_stats()
    logger.info(f"\n性能指标:")
    for metric_name, stats in perf_stats['performance_metrics'].items():
        if stats:
            logger.info(f"  {metric_name}: 平均={stats['avg']:.2f}, "
                       f"最小={stats['min']:.2f}, 最大={stats['max']:.2f}")
    
    # 缓存效果
    cache_stats = perf_stats['cache_stats']
    logger.info(f"\n缓存效果:")
    logger.info(f"  命中率: {cache_stats['hit_rate']:.1%}")
    logger.info(f"  缓存大小: {cache_stats['size']}/{cache_stats['max_size']}")


def test_parallel_vs_serial():
    """测试并行vs串行的性能差异"""
    logger.info("\n\n=== 并行vs串行性能测试 ===")
    
    from utils.concept.evidence_collector import EvidenceCollector
    
    test_params = {
        'ts_code': '000001.SZ',
        'concepts': ['银行', '金融']
    }
    
    # 原版（串行）
    collector_serial = EvidenceCollector()
    
    # 修改为公开方法以便测试
    logger.info("1. 串行收集证据")
    start_time = time.time()
    
    # 模拟串行收集
    software_ev = collector_serial._collect_software_evidence(
        test_params['ts_code'], test_params['concepts']
    )
    interaction_ev = collector_serial._collect_interaction_evidence(
        test_params['ts_code'], test_params['concepts']
    )
    
    serial_time = time.time() - start_time
    logger.info(f"串行耗时: {serial_time:.2f}秒")
    
    # 优化版（并行）
    collector_parallel = EvidenceCollectorOptimized()
    
    logger.info("\n2. 并行收集证据")
    start_time = time.time()
    evidence = collector_parallel.collect_evidence(
        test_params['ts_code'], test_params['concepts']
    )
    parallel_time = time.time() - start_time
    
    logger.info(f"并行耗时: {parallel_time:.2f}秒")
    logger.info(f"性能提升: {((serial_time - parallel_time) / serial_time * 100):.1f}%")


def test_cache_effectiveness():
    """测试缓存有效性"""
    logger.info("\n\n=== 缓存有效性测试 ===")
    
    collector = EvidenceCollectorOptimized()
    
    # 测试相同查询
    test_params = {
        'ts_code': '600519.SH',
        'concepts': ['白酒', '消费']
    }
    
    times = []
    for i in range(5):
        start = time.time()
        evidence = collector.collect_evidence(**test_params)
        duration = time.time() - start
        times.append(duration)
        logger.info(f"第{i+1}次查询: {duration:.2f}秒")
    
    logger.info(f"\n平均耗时: {sum(times) / len(times):.2f}秒")
    logger.info(f"首次查询: {times[0]:.2f}秒")
    logger.info(f"缓存查询平均: {sum(times[1:]) / len(times[1:]):.2f}秒")
    logger.info(f"缓存加速比: {times[0] / (sum(times[1:]) / len(times[1:])):.1f}x")


def main():
    """主函数"""
    try:
        # 1. 单只股票性能测试
        test_single_stock_performance()
        
        # 2. 批量股票性能测试
        test_batch_performance()
        
        # 3. 并行vs串行测试
        test_parallel_vs_serial()
        
        # 4. 缓存有效性测试
        test_cache_effectiveness()
        
        logger.info("\n\n=== 性能测试完成 ===")
        
    except Exception as e:
        logger.error(f"测试失败: {e}", exc_info=True)


if __name__ == "__main__":
    main()