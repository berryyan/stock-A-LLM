#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Concept Agent 端到端测试
测试从查询到结果的完整流程
"""

import logging
import sys
import json
from typing import Dict, Any

# 添加项目根目录到系统路径
sys.path.insert(0, '/mnt/e/PycharmProjects/stock_analysis_system')

from agents.concept.concept_agent import ConceptAgent

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def test_concept_agent_queries():
    """测试各种类型的概念查询"""
    logger.info("=== Concept Agent 端到端测试 ===")
    
    # 初始化Agent
    agent = ConceptAgent()
    
    # 测试用例
    test_cases = [
        {
            'name': '简单概念查询',
            'query': '储能概念股',
            'expected': {
                'success': True,
                'has_data': True,
                'min_stocks': 10
            }
        },
        {
            'name': '概念分析查询',
            'query': '分析储能概念股的投资机会',
            'expected': {
                'success': True,
                'has_data': True,
                'has_analysis': True
            }
        },
        {
            'name': '筛选查询',
            'query': '储能概念股中值得关注的股票',
            'expected': {
                'success': True,
                'has_data': True,
                'has_filter': True
            }
        },
        {
            'name': '多概念查询',
            'query': '新能源和储能概念股',
            'expected': {
                'success': True,
                'has_data': True,
                'concepts': ['新能源', '储能']
            }
        },
        {
            'name': '错误处理测试',
            'query': '',
            'expected': {
                'success': False,
                'has_error': True
            }
        }
    ]
    
    # 执行测试
    results = []
    for i, test_case in enumerate(test_cases, 1):
        logger.info(f"\n测试用例 {i}: {test_case['name']}")
        logger.info(f"查询: {test_case['query']}")
        
        try:
            # 执行查询
            result = agent.run(test_case['query'])
            
            # 验证结果
            passed = verify_result(result, test_case['expected'])
            
            # 记录结果
            test_result = {
                'name': test_case['name'],
                'query': test_case['query'],
                'passed': passed,
                'result': result
            }
            results.append(test_result)
            
            # 输出结果摘要
            if result.get('success'):
                logger.info(f"✅ 成功")
                if 'data' in result:
                    # 尝试解析数据
                    try:
                        if isinstance(result['data'], str):
                            logger.info(f"结果预览: {result['data'][:200]}...")
                        else:
                            logger.info(f"结果类型: {type(result['data'])}")
                    except:
                        pass
            else:
                logger.error(f"❌ 失败: {result.get('error', '未知错误')}")
                
        except Exception as e:
            logger.error(f"❌ 执行异常: {e}")
            results.append({
                'name': test_case['name'],
                'query': test_case['query'],
                'passed': False,
                'error': str(e)
            })
    
    # 总结测试结果
    summarize_results(results)
    
    return results


def verify_result(result: Dict[str, Any], expected: Dict[str, Any]) -> bool:
    """验证结果是否符合预期"""
    passed = True
    
    # 验证成功状态
    if result.get('success') != expected.get('success', True):
        logger.error(f"成功状态不匹配: 期望 {expected.get('success')}, 实际 {result.get('success')}")
        passed = False
    
    # 验证是否有数据
    if expected.get('has_data'):
        if not result.get('data'):
            logger.error("期望有数据但未返回")
            passed = False
    
    # 验证错误信息
    if expected.get('has_error'):
        if not result.get('error'):
            logger.error("期望有错误信息但未返回")
            passed = False
    
    # 验证股票数量
    if 'min_stocks' in expected:
        # 尝试从metadata中获取股票数量
        stock_count = result.get('metadata', {}).get('stock_count', 0)
        if stock_count < expected['min_stocks']:
            logger.error(f"股票数量不足: 期望至少 {expected['min_stocks']}, 实际 {stock_count}")
            passed = False
    
    return passed


def summarize_results(results: list):
    """总结测试结果"""
    total = len(results)
    passed = sum(1 for r in results if r.get('passed', False))
    failed = total - passed
    
    print("\n" + "=" * 80)
    print("测试总结:")
    print(f"  总计: {total}")
    print(f"  通过: {passed} ({passed/total*100:.1f}%)")
    print(f"  失败: {failed}")
    
    if failed > 0:
        print("\n失败的测试:")
        for r in results:
            if not r.get('passed', False):
                print(f"  - {r['name']}: {r.get('error', '未知错误')}")


def test_specific_functionality():
    """测试特定功能"""
    logger.info("\n=== 测试特定功能 ===")
    
    agent = ConceptAgent()
    
    # 测试评分功能
    logger.info("\n1. 测试评分功能")
    query = "储能概念股分析"
    result = agent.process_query(query)
    
    if result.get('success'):
        metadata = result.get('metadata', {})
        logger.info(f"查询类型: {metadata.get('query_type')}")
        logger.info(f"原始概念: {metadata.get('original_concepts')}")
        logger.info(f"扩展概念: {metadata.get('expanded_concepts')}")
        logger.info(f"股票数量: {metadata.get('stock_count')}")
        logger.info(f"数据源: {metadata.get('data_sources')}")
    
    # 测试长文本分析
    logger.info("\n2. 测试新闻文本分析")
    news_text = """
    近日，国家能源局发布《关于加快推进新型储能发展的指导意见》，明确提出到2025年，
    新型储能装机规模达到3000万千瓦以上。业内人士分析，随着政策支持力度加大，
    储能行业将迎来快速发展期。特别是锂电池储能、钠离子电池等新技术有望获得突破。
    相关上市公司如宁德时代、比亚迪、阳光电源等有望受益。
    """
    
    if len(news_text) > 200:
        logger.info("测试新闻文本分析（文本长度>200）")
        result = agent.run(f"概念股分析：{news_text}")
        
        if result.get('success'):
            logger.info("✅ 新闻分析成功")
        else:
            logger.error(f"❌ 新闻分析失败: {result.get('error')}")


def test_performance():
    """测试性能"""
    logger.info("\n=== 性能测试 ===")
    
    import time
    agent = ConceptAgent()
    
    # 测试响应时间
    queries = [
        "储能概念股",
        "新能源概念股分析",
        "锂电池概念股有哪些"
    ]
    
    times = []
    for query in queries:
        start_time = time.time()
        result = agent.process_query(query)
        end_time = time.time()
        
        elapsed = end_time - start_time
        times.append(elapsed)
        
        logger.info(f"查询: {query}")
        logger.info(f"耗时: {elapsed:.2f}秒")
        logger.info(f"成功: {result.get('success')}")
    
    avg_time = sum(times) / len(times)
    logger.info(f"\n平均响应时间: {avg_time:.2f}秒")
    
    if avg_time < 10:
        logger.info("✅ 性能达标（<10秒）")
    else:
        logger.warning("⚠️ 性能需要优化")


def main():
    """主函数"""
    try:
        # 1. 基础功能测试
        results = test_concept_agent_queries()
        
        # 2. 特定功能测试
        test_specific_functionality()
        
        # 3. 性能测试
        test_performance()
        
        logger.info("\n=== 端到端测试完成 ===")
        
    except Exception as e:
        logger.error(f"测试失败: {e}", exc_info=True)


if __name__ == "__main__":
    main()