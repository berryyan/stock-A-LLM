#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试LLM扩展步骤的必要性
对比有无概念扩展的查询效果
"""

import logging
import sys
import json
from typing import List, Dict
import time

# 添加项目根目录到系统路径
sys.path.insert(0, '/mnt/e/PycharmProjects/stock_analysis_system')

from utils.concept.concept_matcher_v2 import ConceptMatcherV2
from utils.concept.concept_data_collector import ConceptDataCollector

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ConceptMatcherWithoutExpansion(ConceptMatcherV2):
    """不使用LLM扩展的概念匹配器"""
    
    def expand_concepts(self, concepts: List[str]) -> List[str]:
        """跳过扩展步骤，直接返回原始概念"""
        logger.info(f"跳过概念扩展，直接使用原始概念: {concepts}")
        return concepts


def compare_matching_results(query: str):
    """对比有无扩展的匹配结果"""
    logger.info(f"\n{'='*80}")
    logger.info(f"测试查询: {query}")
    logger.info(f"{'='*80}")
    
    # 创建两个匹配器
    matcher_with_expansion = ConceptMatcherV2()
    matcher_without_expansion = ConceptMatcherWithoutExpansion()
    data_collector = ConceptDataCollector()
    
    # 1. 提取概念（两者相同）
    concepts = matcher_with_expansion.extract_concepts(query)
    logger.info(f"\n1. 提取的概念: {concepts}")
    
    # 2. 有扩展的流程
    logger.info(f"\n2. 【有扩展】的处理流程:")
    start_time = time.time()
    
    # 扩展概念
    expanded_concepts = matcher_with_expansion.expand_concepts(concepts)
    logger.info(f"   扩展后的概念: {expanded_concepts}")
    logger.info(f"   新增概念: {[c for c in expanded_concepts if c not in concepts]}")
    
    # 匹配概念
    matched_with_expansion = matcher_with_expansion.match_concepts(expanded_concepts)
    expansion_time = time.time() - start_time
    
    logger.info(f"   匹配结果:")
    logger.info(f"   - 同花顺: {len(matched_with_expansion['THS'])}个 - {matched_with_expansion['THS'][:3]}...")
    logger.info(f"   - 东财: {len(matched_with_expansion['DC'])}个 - {matched_with_expansion['DC'][:3]}...")
    logger.info(f"   - 开盘啦: {len(matched_with_expansion['KPL'])}个 - {matched_with_expansion['KPL'][:3]}...")
    logger.info(f"   处理时间: {expansion_time:.2f}秒")
    
    # 3. 无扩展的流程
    logger.info(f"\n3. 【无扩展】的处理流程:")
    start_time = time.time()
    
    # 跳过扩展，直接匹配
    no_expanded_concepts = matcher_without_expansion.expand_concepts(concepts)
    matched_without_expansion = matcher_without_expansion.match_concepts(no_expanded_concepts)
    no_expansion_time = time.time() - start_time
    
    logger.info(f"   匹配结果:")
    logger.info(f"   - 同花顺: {len(matched_without_expansion['THS'])}个 - {matched_without_expansion['THS'][:3]}...")
    logger.info(f"   - 东财: {len(matched_without_expansion['DC'])}个 - {matched_without_expansion['DC'][:3]}...")
    logger.info(f"   - 开盘啦: {len(matched_without_expansion['KPL'])}个 - {matched_without_expansion['KPL'][:3]}...")
    logger.info(f"   处理时间: {no_expansion_time:.2f}秒")
    
    # 4. 对比分析
    logger.info(f"\n4. 对比分析:")
    
    # 统计差异
    total_with = len(matched_with_expansion['THS']) + len(matched_with_expansion['DC']) + len(matched_with_expansion['KPL'])
    total_without = len(matched_without_expansion['THS']) + len(matched_without_expansion['DC']) + len(matched_without_expansion['KPL'])
    
    logger.info(f"   总匹配数: 有扩展={total_with}, 无扩展={total_without}, 差异={total_with - total_without}")
    logger.info(f"   处理时间: 有扩展={expansion_time:.2f}秒, 无扩展={no_expansion_time:.2f}秒")
    
    # 找出额外匹配的概念
    extra_ths = set(matched_with_expansion['THS']) - set(matched_without_expansion['THS'])
    extra_dc = set(matched_with_expansion['DC']) - set(matched_without_expansion['DC'])
    extra_kpl = set(matched_with_expansion['KPL']) - set(matched_without_expansion['KPL'])
    
    if extra_ths or extra_dc or extra_kpl:
        logger.info(f"\n   通过扩展额外匹配到的概念:")
        if extra_ths:
            logger.info(f"   - 同花顺: {list(extra_ths)[:5]}")
        if extra_dc:
            logger.info(f"   - 东财: {list(extra_dc)[:5]}")
        if extra_kpl:
            logger.info(f"   - 开盘啦: {list(extra_kpl)[:5]}")
    
    # 5. 获取股票数量对比
    logger.info(f"\n5. 股票数量对比:")
    
    # 收集概念名称
    concepts_with = []
    concepts_with.extend(matched_with_expansion['THS'][:2])
    concepts_with.extend(matched_with_expansion['DC'][:1])
    concepts_with.extend(matched_with_expansion['KPL'][:1])
    
    concepts_without = []
    concepts_without.extend(matched_without_expansion['THS'][:2])
    concepts_without.extend(matched_without_expansion['DC'][:1])
    concepts_without.extend(matched_without_expansion['KPL'][:1])
    
    if concepts_with:
        stocks_with = data_collector.get_concept_stocks(concepts_with[:3])
        logger.info(f"   有扩展: 使用{len(concepts_with)}个概念，找到{len(stocks_with)}只股票")
    
    if concepts_without:
        stocks_without = data_collector.get_concept_stocks(concepts_without[:3])
        logger.info(f"   无扩展: 使用{len(concepts_without)}个概念，找到{len(stocks_without)}只股票")
    
    return {
        "query": query,
        "with_expansion": {
            "expanded_concepts": expanded_concepts,
            "matched_count": total_with,
            "time": expansion_time
        },
        "without_expansion": {
            "concepts": concepts,
            "matched_count": total_without,
            "time": no_expansion_time
        }
    }


def explain_llm_matching_logic():
    """详细解释LLM匹配的逻辑"""
    logger.info(f"\n{'='*80}")
    logger.info("LLM匹配逻辑详解")
    logger.info(f"{'='*80}")
    
    matcher = ConceptMatcherV2()
    
    # 测试案例
    test_concept = "储能"
    
    logger.info(f"\n测试概念: '{test_concept}'")
    
    # 1. 加载所有概念
    all_concepts = matcher._load_all_concepts()
    
    logger.info(f"\n1. 数据库中的概念总览:")
    logger.info(f"   - 同花顺: {len(all_concepts['THS'])}个概念")
    logger.info(f"   - 东财: {len(all_concepts['DC'])}个板块")
    logger.info(f"   - 开盘啦: {len(all_concepts['KPL'])}个概念")
    
    # 2. 展示包含"储能"的概念
    logger.info(f"\n2. 直接包含'{test_concept}'的概念:")
    
    ths_direct = [c for c in all_concepts['THS'] if test_concept in c['name']]
    dc_direct = [c for c in all_concepts['DC'] if test_concept in c['name']]
    kpl_direct = [c for c in all_concepts['KPL'] if test_concept in c['name']]
    
    logger.info(f"   - 同花顺: {[c['name'] for c in ths_direct[:5]]}")
    logger.info(f"   - 东财: {[c['name'] for c in dc_direct[:5]]}")
    logger.info(f"   - 开盘啦: {[c['name'] for c in kpl_direct[:5]]}")
    
    # 3. LLM匹配逻辑
    logger.info(f"\n3. LLM匹配逻辑:")
    logger.info(f"   a) LLM会分析语义相似性，不仅仅是字符串包含")
    logger.info(f"   b) 例如：'储能' 可能匹配到:")
    logger.info(f"      - '储能概念'（直接相关）")
    logger.info(f"      - '储能设备'（设备类）")
    logger.info(f"      - '储能技术'（技术类）")
    logger.info(f"      - '新型储能'（细分类型）")
    logger.info(f"      - '电化学储能'（技术路线）")
    
    # 4. 实际LLM匹配
    logger.info(f"\n4. 实际LLM匹配结果:")
    matched = matcher.match_concepts([test_concept])
    
    for source, concepts in matched.items():
        if concepts:
            logger.info(f"   {source}: {concepts[:8]}")
    
    # 5. 开盘啦描述匹配
    logger.info(f"\n5. 开盘啦描述匹配示例:")
    kpl_with_desc = [c for c in all_concepts['KPL'] if c.get('desc') and '储能' in c.get('desc', '')]
    
    if kpl_with_desc:
        logger.info(f"   描述中包含'{test_concept}'的概念:")
        for concept in kpl_with_desc[:3]:
            logger.info(f"   - {concept['name']}: {concept['desc'][:80]}...")


def test_multiple_cases():
    """测试多个案例"""
    test_cases = [
        "充电宝",
        "固态电池概念股",
        "新能源汽车产业链相关的投资机会",
        "人工智能和算力基础设施",
        "近期储能政策利好，分析相关概念股投资价值"
    ]
    
    results = []
    for query in test_cases:
        result = compare_matching_results(query)
        results.append(result)
    
    # 保存结果
    with open('llm_expansion_comparison_results.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    # 总结分析
    logger.info(f"\n{'='*80}")
    logger.info("总结分析")
    logger.info(f"{'='*80}")
    
    total_improvement = 0
    time_cost = 0
    
    for result in results:
        with_count = result['with_expansion']['matched_count']
        without_count = result['without_expansion']['matched_count']
        improvement = ((with_count - without_count) / without_count * 100) if without_count > 0 else 0
        
        time_diff = result['with_expansion']['time'] - result['without_expansion']['time']
        
        logger.info(f"\n查询: {result['query'][:30]}...")
        logger.info(f"  匹配数提升: {without_count} → {with_count} (+{improvement:.1f}%)")
        logger.info(f"  时间成本: +{time_diff:.2f}秒")
        
        total_improvement += improvement
        time_cost += time_diff
    
    avg_improvement = total_improvement / len(results)
    avg_time_cost = time_cost / len(results)
    
    logger.info(f"\n平均效果:")
    logger.info(f"  匹配数平均提升: {avg_improvement:.1f}%")
    logger.info(f"  平均时间成本: +{avg_time_cost:.2f}秒")
    
    logger.info(f"\n结论:")
    if avg_improvement > 20:
        logger.info(f"  ✓ LLM扩展显著提升了概念匹配的召回率（+{avg_improvement:.1f}%）")
        logger.info(f"  ✓ 虽然增加了{avg_time_cost:.2f}秒的处理时间，但对于提升查全率是值得的")
        logger.info(f"  ✓ 建议保留LLM扩展步骤，特别是对于模糊查询和复杂查询")
    elif avg_improvement > 10:
        logger.info(f"  ✓ LLM扩展有一定效果（+{avg_improvement:.1f}%），建议保留")
        logger.info(f"  ✓ 可以考虑优化扩展策略，减少时间开销")
    else:
        logger.info(f"  ✗ LLM扩展效果有限（+{avg_improvement:.1f}%）")
        logger.info(f"  ✗ 考虑到时间成本，可以考虑移除或优化")


def main():
    """主函数"""
    try:
        # 1. 解释LLM匹配逻辑
        explain_llm_matching_logic()
        
        # 2. 测试多个案例
        test_multiple_cases()
        
        logger.info(f"\n{'='*80}")
        logger.info("测试完成！")
        logger.info(f"{'='*80}")
        
    except Exception as e:
        logger.error(f"测试失败: {e}", exc_info=True)


if __name__ == "__main__":
    main()