#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试Concept Agent集成
Day 2测试：概念匹配和数据访问
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import logging
from agents.concept.concept_agent import ConceptAgent

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# 临时注入一个简化的评分方法
def mock_calculate_scores(self, concept_stocks, technical_data, money_flow_data, weights):
    """临时的评分计算方法"""
    scored_stocks = []
    
    for stock in concept_stocks[:50]:  # 只处理前50只
        # 简单的模拟评分
        concept_count = len(stock.get('concepts', []))
        
        # 基于概念数量的简单评分
        concept_score = min(concept_count * 10, 40)  # 最高40分
        money_score = 15  # 固定15分
        technical_score = 15  # 固定15分
        
        scored_stock = {
            **stock,
            'concept_score': concept_score,
            'money_score': money_score,
            'technical_score': technical_score,
            'total_score': concept_score + money_score + technical_score
        }
        
        scored_stocks.append(scored_stock)
    
    # 按总分排序
    scored_stocks.sort(key=lambda x: x['total_score'], reverse=True)
    
    return scored_stocks


def test_concept_agent():
    """测试Concept Agent"""
    print("="*80)
    print("测试Concept Agent集成")
    print("="*80)
    
    try:
        # 创建Agent实例
        print("\n1. 创建Agent实例...")
        agent = ConceptAgent()
        
        # 注入临时的评分方法
        agent.concept_scorer.calculate_scores = lambda *args, **kwargs: mock_calculate_scores(agent.concept_scorer, *args, **kwargs)
        
        print("✅ Agent创建成功")
        
        # 测试查询
        test_queries = [
            "固态电池",
            "新能源汽车概念股有哪些？",
            "充电桩相关板块"
        ]
        
        for i, query in enumerate(test_queries, 1):
            print(f"\n{i}. 测试查询: {query}")
            print("-"*60)
            
            try:
                # 添加触发词
                full_query = f"概念股分析：{query}"
                
                # 执行查询
                result = agent.process_query(full_query)
                
                if result.get('success'):
                    print("✅ 查询成功")
                    
                    # 显示元数据
                    metadata = result.get('metadata', {})
                    print(f"\n查询类型: {metadata.get('query_type')}")
                    print(f"原始概念: {metadata.get('original_concepts')}")
                    print(f"扩展概念: {metadata.get('expanded_concepts')}")
                    print(f"股票数量: {metadata.get('stock_count')}")
                    
                    # 显示部分结果
                    answer = result.get('answer', '')
                    if answer:
                        # 只显示前500个字符
                        preview = answer[:500] + "..." if len(answer) > 500 else answer
                        print(f"\n结果预览:\n{preview}")
                else:
                    print(f"❌ 查询失败: {result.get('error')}")
                    
            except Exception as e:
                print(f"❌ 执行出错: {str(e)}")
                import traceback
                traceback.print_exc()
        
        print("\n\n测试完成！")
        
    except Exception as e:
        print(f"\n❌ 初始化失败: {str(e)}")
        import traceback
        traceback.print_exc()


def test_data_access_integration():
    """测试数据访问层集成"""
    print("\n\n" + "="*80)
    print("测试数据访问层集成")
    print("="*80)
    
    try:
        from utils.concept.concept_data_access import ConceptDataAccess
        
        data_access = ConceptDataAccess()
        
        # 测试搜索概念
        print("\n测试概念搜索:")
        keywords = ["固态电池", "充电"]
        for keyword in keywords:
            results = data_access.search_concepts(keyword)
            print(f"\n'{keyword}' 搜索结果: {len(results)} 个")
            for r in results[:3]:
                print(f"  - {r['name']} ({r['ts_code']}) [{r['source']}]")
        
        print("\n✅ 数据访问层工作正常")
        
    except Exception as e:
        print(f"❌ 数据访问层测试失败: {str(e)}")


def test_concept_matcher_integration():
    """测试概念匹配器集成"""
    print("\n\n" + "="*80)
    print("测试概念匹配器集成")
    print("="*80)
    
    try:
        from utils.concept.concept_matcher import ConceptMatcher
        
        matcher = ConceptMatcher()
        
        # 测试概念扩展
        print("\n测试概念扩展:")
        concepts = ["固态电池", "充电桩"]
        for concept in concepts:
            expanded = matcher.expand_concepts([concept])
            print(f"\n'{concept}' 扩展结果: {expanded}")
        
        print("\n✅ 概念匹配器工作正常")
        
    except Exception as e:
        print(f"❌ 概念匹配器测试失败: {str(e)}")


def main():
    """主测试函数"""
    # 测试各个组件
    test_data_access_integration()
    test_concept_matcher_integration()
    
    # 测试完整的Agent
    test_concept_agent()


if __name__ == "__main__":
    main()