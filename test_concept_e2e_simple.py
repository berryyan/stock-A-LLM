#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Concept Agent简化的端到端测试
避免长时间运行和超时
"""

import logging
import sys
import time

# 添加项目根目录到系统路径
sys.path.insert(0, '/mnt/e/PycharmProjects/stock_analysis_system')

from agents.concept.concept_agent import ConceptAgent

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def test_basic_functionality():
    """测试基本功能"""
    logger.info("=== Concept Agent基本功能测试 ===")
    
    agent = ConceptAgent()
    
    # 测试用例
    test_cases = [
        {
            'name': '简单概念查询',
            'query': '概念股分析：充电宝概念股',
            'timeout': 30
        },
        {
            'name': '多概念查询',
            'query': '概念股分析：白酒和消费概念股有哪些？',
            'timeout': 30
        }
    ]
    
    results = []
    
    for case in test_cases:
        logger.info(f"\n测试: {case['name']}")
        logger.info(f"查询: {case['query']}")
        
        start = time.time()
        try:
            result = agent.process_query(case['query'])
            duration = time.time() - start
            
            if result.success:
                metadata = result.metadata or {}
                logger.info(f"✅ 成功")
                logger.info(f"  - 查询类型: {metadata.get('query_type')}")
                logger.info(f"  - 识别概念: {metadata.get('original_concepts')}")
                logger.info(f"  - 股票数量: {metadata.get('stock_count')}")
                logger.info(f"  - 耗时: {duration:.2f}秒")
                
                # 显示部分结果
                if result.data:
                    lines = result.data.split('\n')
                    logger.info(f"\n结果预览:")
                    for line in lines[:10]:
                        if line.strip():
                            logger.info(f"  {line}")
                
                results.append({
                    'test': case['name'],
                    'success': True,
                    'duration': duration,
                    'stock_count': metadata.get('stock_count', 0)
                })
            else:
                logger.error(f"❌ 失败: {result.error}")
                results.append({
                    'test': case['name'],
                    'success': False,
                    'error': result.error,
                    'duration': duration
                })
                
        except Exception as e:
            duration = time.time() - start
            logger.error(f"❌ 异常: {str(e)}")
            results.append({
                'test': case['name'],
                'success': False,
                'error': str(e),
                'duration': duration
            })
        
        # 避免请求过快
        time.sleep(2)
    
    # 汇总结果
    logger.info("\n=== 测试汇总 ===")
    success_count = sum(1 for r in results if r['success'])
    logger.info(f"总测试数: {len(results)}")
    logger.info(f"成功: {success_count}")
    logger.info(f"失败: {len(results) - success_count}")
    
    if success_count > 0:
        success_results = [r for r in results if r['success']]
        avg_duration = sum(r['duration'] for r in success_results) / len(success_results)
        logger.info(f"平均耗时: {avg_duration:.2f}秒")


def test_integration_with_optimized_collector():
    """测试与优化版收集器的集成"""
    logger.info("\n\n=== 测试优化版收集器集成 ===")
    
    # 修改ConceptAgent使用优化版收集器
    from utils.concept.evidence_collector_optimized import EvidenceCollectorOptimized
    
    # 临时替换
    agent = ConceptAgent()
    if hasattr(agent, 'concept_scorer'):
        original_collector = getattr(agent.concept_scorer, 'evidence_collector', None)
        
        # 创建优化版收集器
        optimized_collector = EvidenceCollectorOptimized()
        
        # 测试单个股票
        test_stock = {
            'ts_code': '600519.SH',
            'name': '贵州茅台',
            'concepts': ['白酒', '消费']
        }
        
        logger.info(f"测试股票: {test_stock['name']}")
        
        # 测试原版
        if original_collector:
            start = time.time()
            evidence_v1 = original_collector.collect_evidence(
                test_stock['ts_code'],
                test_stock['concepts']
            )
            v1_time = time.time() - start
            logger.info(f"原版收集器耗时: {v1_time:.2f}秒")
        
        # 测试优化版
        start = time.time()
        evidence_v2 = optimized_collector.collect_evidence(
            test_stock['ts_code'],
            test_stock['concepts']
        )
        v2_time = time.time() - start
        logger.info(f"优化版收集器耗时: {v2_time:.2f}秒")
        
        # 测试缓存
        start = time.time()
        evidence_v2_cached = optimized_collector.collect_evidence(
            test_stock['ts_code'],
            test_stock['concepts']
        )
        v2_cached_time = time.time() - start
        logger.info(f"缓存查询耗时: {v2_cached_time:.2f}秒")
        
        # 显示缓存统计
        stats = optimized_collector.get_performance_stats()
        cache_stats = stats['cache_stats']
        logger.info(f"\n缓存统计:")
        logger.info(f"  命中率: {cache_stats['hit_rate']:.1%}")
        logger.info(f"  缓存大小: {cache_stats['size']}")


def test_error_cases():
    """测试错误处理"""
    logger.info("\n\n=== 错误处理测试 ===")
    
    agent = ConceptAgent()
    
    error_cases = [
        '概念股分析：',  # 空查询
        '概念股分析：xyz123abc',  # 无效概念
        '概念股分析：' + 'a' * 500  # 超长查询
    ]
    
    for i, query in enumerate(error_cases, 1):
        logger.info(f"\n错误测试{i}: {query[:50]}...")
        
        result = agent.process_query(query)
        if not result.success:
            logger.info(f"✅ 正确处理错误: {result.error}")
        else:
            logger.warning(f"⚠️ 应该失败但成功了")


def main():
    """主函数"""
    try:
        # 1. 基本功能测试
        test_basic_functionality()
        
        # 2. 集成测试
        test_integration_with_optimized_collector()
        
        # 3. 错误处理测试
        test_error_cases()
        
        logger.info("\n\n=== 简化E2E测试完成 ===")
        
    except Exception as e:
        logger.error(f"测试失败: {e}", exc_info=True)


if __name__ == "__main__":
    main()