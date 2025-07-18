#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
概念股系统性能优化模块
提供缓存、并行执行、性能监控等功能
"""

import time
import logging
import functools
from typing import Any, Dict, List, Optional, Callable, Tuple
from collections import OrderedDict
from concurrent.futures import ThreadPoolExecutor, as_completed, TimeoutError
from threading import Lock
import hashlib
import json

logger = logging.getLogger(__name__)


class LRUCache:
    """
    线程安全的LRU缓存实现
    """
    def __init__(self, max_size: int = 1000, ttl: int = 3600):
        """
        初始化LRU缓存
        
        Args:
            max_size: 最大缓存条目数
            ttl: 缓存过期时间（秒）
        """
        self._cache = OrderedDict()
        self._max_size = max_size
        self._ttl = ttl
        self._lock = Lock()
        self._hits = 0
        self._misses = 0
        
        logger.info(f"LRU缓存初始化: max_size={max_size}, ttl={ttl}秒")
    
    def _make_key(self, *args, **kwargs) -> str:
        """生成缓存键"""
        key_data = {
            'args': args,
            'kwargs': sorted(kwargs.items())
        }
        key_str = json.dumps(key_data, sort_keys=True, ensure_ascii=False)
        return hashlib.md5(key_str.encode()).hexdigest()
    
    def get(self, key: str) -> Optional[Any]:
        """获取缓存值"""
        with self._lock:
            if key not in self._cache:
                self._misses += 1
                return None
            
            # 检查是否过期
            value, timestamp = self._cache[key]
            if time.time() - timestamp > self._ttl:
                del self._cache[key]
                self._misses += 1
                return None
            
            # 移到末尾（最近使用）
            self._cache.move_to_end(key)
            self._hits += 1
            return value
    
    def set(self, key: str, value: Any) -> None:
        """设置缓存值"""
        with self._lock:
            # 如果已存在，先删除
            if key in self._cache:
                del self._cache[key]
            
            # 添加到末尾
            self._cache[key] = (value, time.time())
            
            # 检查大小限制
            if len(self._cache) > self._max_size:
                # 删除最老的（第一个）
                self._cache.popitem(last=False)
    
    def clear(self) -> None:
        """清空缓存"""
        with self._lock:
            self._cache.clear()
            self._hits = 0
            self._misses = 0
    
    def get_stats(self) -> Dict[str, Any]:
        """获取缓存统计信息"""
        with self._lock:
            total = self._hits + self._misses
            hit_rate = self._hits / total if total > 0 else 0
            return {
                'size': len(self._cache),
                'max_size': self._max_size,
                'hits': self._hits,
                'misses': self._misses,
                'hit_rate': hit_rate,
                'ttl': self._ttl
            }


class EvidenceCache:
    """
    证据专用缓存管理器
    """
    def __init__(self, ttl: int = 3600):
        """
        初始化证据缓存
        
        Args:
            ttl: 缓存过期时间（秒）
        """
        self._cache = LRUCache(max_size=500, ttl=ttl)
        logger.info("证据缓存管理器初始化完成")
    
    def get_key(self, ts_code: str, concepts: List[str]) -> str:
        """生成证据缓存键"""
        sorted_concepts = sorted(concepts)
        return f"evidence_{ts_code}_{'_'.join(sorted_concepts)}"
    
    def get(self, ts_code: str, concepts: List[str]) -> Optional[Dict]:
        """获取缓存的证据"""
        key = self.get_key(ts_code, concepts)
        return self._cache.get(key)
    
    def set(self, ts_code: str, concepts: List[str], evidence: Dict) -> None:
        """缓存证据"""
        key = self.get_key(ts_code, concepts)
        self._cache.set(key, evidence)
    
    def get_stats(self) -> Dict[str, Any]:
        """获取缓存统计"""
        return self._cache.get_stats()


class ParallelExecutor:
    """
    并行执行器
    """
    def __init__(self, max_workers: int = 4, timeout: int = 10):
        """
        初始化并行执行器
        
        Args:
            max_workers: 最大工作线程数
            timeout: 单个任务超时时间（秒）
        """
        self._max_workers = max_workers
        self._timeout = timeout
        logger.info(f"并行执行器初始化: max_workers={max_workers}, timeout={timeout}秒")
    
    def execute(self, tasks: Dict[str, Callable]) -> Dict[str, Any]:
        """
        并行执行多个任务
        
        Args:
            tasks: 任务字典，格式为 {任务名: 可调用对象}
            
        Returns:
            结果字典，格式为 {任务名: 结果或异常}
        """
        results = {}
        
        with ThreadPoolExecutor(max_workers=self._max_workers) as executor:
            # 提交所有任务
            future_to_name = {
                executor.submit(task): name 
                for name, task in tasks.items()
            }
            
            # 收集结果
            for future in as_completed(future_to_name):
                name = future_to_name[future]
                try:
                    result = future.result(timeout=self._timeout)
                    results[name] = result
                    logger.debug(f"任务 {name} 执行成功")
                except TimeoutError:
                    error_msg = f"任务超时（{self._timeout}秒）"
                    results[name] = {'error': error_msg}
                    logger.warning(f"任务 {name} {error_msg}")
                except Exception as e:
                    error_msg = f"任务执行失败: {str(e)}"
                    results[name] = {'error': error_msg}
                    logger.error(f"任务 {name} {error_msg}")
        
        return results


def monitor_performance(name: str = None):
    """
    性能监控装饰器
    
    Args:
        name: 监控点名称
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            func_name = name or f"{func.__module__}.{func.__name__}"
            
            try:
                result = func(*args, **kwargs)
                duration = time.time() - start_time
                logger.info(f"性能监控 - {func_name}: {duration:.2f}秒")
                
                # 记录慢查询
                if duration > 5:
                    logger.warning(f"慢查询警告 - {func_name}: {duration:.2f}秒")
                
                return result
            except Exception as e:
                duration = time.time() - start_time
                logger.error(f"性能监控 - {func_name} 失败: {duration:.2f}秒, 错误: {str(e)}")
                raise
        
        return wrapper
    return decorator


def cached(cache: LRUCache):
    """
    缓存装饰器
    
    Args:
        cache: LRU缓存实例
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # 生成缓存键
            cache_key = cache._make_key(*args, **kwargs)
            
            # 尝试从缓存获取
            cached_result = cache.get(cache_key)
            if cached_result is not None:
                logger.debug(f"缓存命中: {func.__name__}")
                return cached_result
            
            # 执行函数
            result = func(*args, **kwargs)
            
            # 存入缓存
            cache.set(cache_key, result)
            logger.debug(f"缓存更新: {func.__name__}")
            
            return result
        
        return wrapper
    return decorator


class QueryOptimizer:
    """
    查询优化器
    """
    def __init__(self):
        """初始化查询优化器"""
        self._query_cache = LRUCache(max_size=200, ttl=1800)  # 30分钟缓存
        logger.info("查询优化器初始化完成")
    
    def optimize_rag_query(self, stock_name: str, concepts: List[str]) -> List[str]:
        """
        优化RAG查询
        
        Args:
            stock_name: 股票名称
            concepts: 概念列表
            
        Returns:
            优化后的查询列表
        """
        optimized_queries = []
        
        # 合并相似概念
        merged_concepts = self._merge_similar_concepts(concepts)
        
        # 生成优化查询
        for concept in merged_concepts:
            # 年报查询
            query = f"{stock_name} {concept} 年报 主营业务"
            optimized_queries.append(query)
            
            # 公告查询（只查最重要的）
            if len(optimized_queries) < 5:  # 限制查询数量
                query = f"{stock_name} {concept} 公告"
                optimized_queries.append(query)
        
        return optimized_queries
    
    def _merge_similar_concepts(self, concepts: List[str]) -> List[str]:
        """合并相似概念"""
        # 简单实现：去重
        return list(set(concepts))
    
    def batch_process(self, items: List[Any], batch_size: int = 50) -> List[List[Any]]:
        """
        批量处理分组
        
        Args:
            items: 待处理项目列表
            batch_size: 批次大小
            
        Returns:
            分组后的批次列表
        """
        batches = []
        for i in range(0, len(items), batch_size):
            batch = items[i:i + batch_size]
            batches.append(batch)
        
        return batches


class PerformanceMonitor:
    """
    性能监控器
    """
    def __init__(self):
        """初始化性能监控器"""
        self._metrics = {}
        self._lock = Lock()
        logger.info("性能监控器初始化完成")
    
    def record(self, metric_name: str, value: float) -> None:
        """记录性能指标"""
        with self._lock:
            if metric_name not in self._metrics:
                self._metrics[metric_name] = []
            self._metrics[metric_name].append({
                'value': value,
                'timestamp': time.time()
            })
            
            # 只保留最近1000条记录
            if len(self._metrics[metric_name]) > 1000:
                self._metrics[metric_name] = self._metrics[metric_name][-1000:]
    
    def get_stats(self, metric_name: str) -> Dict[str, float]:
        """获取指标统计"""
        with self._lock:
            if metric_name not in self._metrics:
                return {}
            
            values = [m['value'] for m in self._metrics[metric_name]]
            if not values:
                return {}
            
            return {
                'count': len(values),
                'min': min(values),
                'max': max(values),
                'avg': sum(values) / len(values),
                'last': values[-1]
            }
    
    def get_all_stats(self) -> Dict[str, Dict[str, float]]:
        """获取所有指标统计"""
        with self._lock:
            return {
                name: self.get_stats(name)
                for name in self._metrics.keys()
            }


# 全局实例
evidence_cache = EvidenceCache()
performance_monitor = PerformanceMonitor()
query_optimizer = QueryOptimizer()


# 测试
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    # 测试LRU缓存
    cache = LRUCache(max_size=3, ttl=5)
    cache.set('key1', 'value1')
    cache.set('key2', 'value2')
    cache.set('key3', 'value3')
    
    print(f"缓存统计: {cache.get_stats()}")
    
    # 测试并行执行
    executor = ParallelExecutor(max_workers=2, timeout=2)
    
    def task1():
        time.sleep(1)
        return "Task 1 完成"
    
    def task2():
        time.sleep(3)  # 会超时
        return "Task 2 完成"
    
    results = executor.execute({
        'task1': task1,
        'task2': task2
    })
    
    print(f"并行执行结果: {results}")