#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
基础性能测试脚本
测试缓存和并行优化效果
"""

import logging
import sys
import time

# 添加项目根目录到系统路径
sys.path.insert(0, '/mnt/e/PycharmProjects/stock_analysis_system')

from utils.concept.performance_optimizer import LRUCache, ParallelExecutor, evidence_cache

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def test_lru_cache():
    """测试LRU缓存功能"""
    logger.info("=== 测试LRU缓存 ===")
    
    cache = LRUCache(max_size=3, ttl=60)
    
    # 测试基本功能
    cache.set('key1', 'value1')
    cache.set('key2', 'value2')
    cache.set('key3', 'value3')
    
    # 测试获取
    assert cache.get('key1') == 'value1'
    assert cache.get('key2') == 'value2'
    assert cache.get('key3') == 'value3'
    assert cache.get('key4') is None  # 不存在
    
    logger.info(f"缓存基本功能正常")
    
    # 测试LRU淘汰
    cache.set('key4', 'value4')  # 应该淘汰key1
    assert cache.get('key1') is None
    assert cache.get('key4') == 'value4'
    
    logger.info(f"LRU淘汰机制正常")
    
    # 测试统计
    stats = cache.get_stats()
    logger.info(f"缓存统计: {stats}")


def test_parallel_executor():
    """测试并行执行器"""
    logger.info("\n=== 测试并行执行器 ===")
    
    executor = ParallelExecutor(max_workers=3, timeout=2)
    
    # 定义测试任务
    def task1():
        time.sleep(0.5)
        return "Task 1 完成"
    
    def task2():
        time.sleep(0.8)
        return "Task 2 完成"
    
    def task3():
        time.sleep(0.3)
        return "Task 3 完成"
    
    def task_timeout():
        time.sleep(3)  # 会超时
        return "不会返回"
    
    # 测试正常执行
    start = time.time()
    results = executor.execute({
        'task1': task1,
        'task2': task2,
        'task3': task3
    })
    duration = time.time() - start
    
    logger.info(f"并行执行耗时: {duration:.2f}秒 (串行需要1.6秒)")
    logger.info(f"执行结果: {results}")
    
    # 测试超时处理
    results = executor.execute({
        'normal': task1,
        'timeout': task_timeout
    })
    
    logger.info(f"超时测试结果: {results}")
    assert 'error' in results['timeout']
    logger.info("超时处理正常")


def test_evidence_cache():
    """测试证据缓存"""
    logger.info("\n=== 测试证据缓存 ===")
    
    # 模拟证据数据
    test_evidence = {
        'software': [{'source': '同花顺', 'score': 15}],
        'interaction': [{'source': '董秘回复', 'score': 20}],
        'report': [],
        'announcement': []
    }
    
    # 测试缓存操作
    ts_code = '600519.SH'
    concepts = ['白酒', '消费']
    
    # 首次获取（未命中）
    result = evidence_cache.get(ts_code, concepts)
    assert result is None
    logger.info("首次查询：缓存未命中")
    
    # 存入缓存
    evidence_cache.set(ts_code, concepts, test_evidence)
    logger.info("存入缓存")
    
    # 再次获取（命中）
    result = evidence_cache.get(ts_code, concepts)
    assert result == test_evidence
    logger.info("第二次查询：缓存命中")
    
    # 测试不同顺序的概念
    concepts_reorder = ['消费', '白酒']
    result = evidence_cache.get(ts_code, concepts_reorder)
    assert result == test_evidence  # 应该命中，因为内部会排序
    logger.info("不同顺序概念：缓存命中")
    
    # 显示统计
    stats = evidence_cache.get_stats()
    logger.info(f"证据缓存统计: {stats}")


def test_performance_comparison():
    """性能对比测试"""
    logger.info("\n=== 性能对比测试 ===")
    
    # 模拟串行处理
    def serial_process():
        results = []
        for i in range(5):
            time.sleep(0.2)  # 模拟处理
            results.append(f"Result {i}")
        return results
    
    # 模拟并行处理
    def parallel_process():
        executor = ParallelExecutor(max_workers=5)
        tasks = {}
        for i in range(5):
            tasks[f'task{i}'] = lambda x=i: (time.sleep(0.2), f"Result {x}")[1]
        
        results = executor.execute(tasks)
        return list(results.values())
    
    # 测试串行
    start = time.time()
    serial_results = serial_process()
    serial_time = time.time() - start
    logger.info(f"串行处理耗时: {serial_time:.2f}秒")
    
    # 测试并行
    start = time.time()
    parallel_results = parallel_process()
    parallel_time = time.time() - start
    logger.info(f"并行处理耗时: {parallel_time:.2f}秒")
    
    # 计算加速比
    speedup = serial_time / parallel_time
    logger.info(f"并行加速比: {speedup:.1f}x")


def main():
    """主函数"""
    try:
        # 1. 测试LRU缓存
        test_lru_cache()
        
        # 2. 测试并行执行器
        test_parallel_executor()
        
        # 3. 测试证据缓存
        test_evidence_cache()
        
        # 4. 性能对比测试
        test_performance_comparison()
        
        logger.info("\n\n=== 所有测试通过 ===")
        
    except Exception as e:
        logger.error(f"测试失败: {e}", exc_info=True)


if __name__ == "__main__":
    main()