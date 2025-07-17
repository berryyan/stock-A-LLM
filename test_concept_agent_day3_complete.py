#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Concept Agent Day 3 完整评分流程测试
测试集成了技术指标和资金流向数据的完整评分系统
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.concept.concept_agent import ConceptAgent
import logging
import time
import json

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def test_complete_scoring_flow():
    """测试完整的评分流程"""
    print("\n" + "="*80)
    print("Concept Agent Day 3 完整评分流程测试")
    print("="*80)
    
    # 初始化Agent
    print("\n初始化Concept Agent...")
    agent = ConceptAgent()
    print("✅ Agent初始化成功")
    
    # 测试用例
    test_cases = [
        {
            "name": "固态电池概念评分测试",
            "query": "概念股分析：固态电池"
        },
        {
            "name": "新能源汽车概念评分测试",
            "query": "概念股分析：新能源汽车概念股有哪些？"
        },
        {
            "name": "人工智能概念评分测试",
            "query": "概念股分析：人工智能"
        }
    ]
    
    for idx, test_case in enumerate(test_cases, 1):
        print(f"\n{'='*60}")
        print(f"测试 {idx}: {test_case['name']}")
        print(f"查询: {test_case['query']}")
        print("="*60)
        
        start_time = time.time()
        
        try:
            # 执行查询
            result = agent.process_query(test_case['query'])
            elapsed_time = time.time() - start_time
            
            if result.success:
                print(f"\n✅ 查询成功 (耗时: {elapsed_time:.2f}秒)")
                
                # 解析元数据
                metadata = result.metadata if hasattr(result, 'metadata') else result.get('metadata', {})
                if metadata:
                    print(f"\n元数据:")
                    print(f"  - 查询类型: {metadata.get('query_type', 'N/A')}")
                    print(f"  - 股票数量: {metadata.get('stock_count', 'N/A')}")
                    print(f"  - 原始概念: {metadata.get('original_concepts', [])}")
                    print(f"  - 扩展概念: {len(metadata.get('expanded_concepts', []))}个")
                    
                    # 检查是否包含评分数据
                    has_scoring = metadata.get('has_technical_data', False) or metadata.get('has_money_flow_data', False)
                    if has_scoring:
                        print(f"  - 技术指标数据: {'✅' if metadata.get('has_technical_data') else '❌'}")
                        print(f"  - 资金流向数据: {'✅' if metadata.get('has_money_flow_data') else '❌'}")
                
                # 显示部分结果
                data = result.data if hasattr(result, 'data') else result.get('data', '')
                if data:
                    lines = str(data).split('\n')
                    print("\n结果预览:")
                    
                    # 查找评分表格
                    in_score_table = False
                    score_lines = []
                    for line in lines:
                        if '综合得分' in line or '股票名称' in line:
                            in_score_table = True
                        if in_score_table:
                            score_lines.append(line)
                            if len(score_lines) > 15:  # 显示前15行
                                break
                    
                    if score_lines:
                        print("评分表格:")
                        for line in score_lines:
                            print(line)
                    else:
                        # 显示前10行
                        for line in lines[:10]:
                            print(line)
                        if len(lines) > 10:
                            print(f"... (还有 {len(lines)-10} 行)")
                
            else:
                print(f"\n❌ 查询失败: {result.error if hasattr(result, 'error') else result.get('error')}")
                
        except Exception as e:
            print(f"\n❌ 测试异常: {str(e)}")
            import traceback
            traceback.print_exc()
    
    print("\n" + "="*80)
    print("测试完成！")
    print("="*80)


def test_scoring_components():
    """测试评分组件是否正常工作"""
    print("\n测试评分组件...")
    
    from utils.concept.technical_collector import TechnicalCollector
    from utils.concept.money_flow_collector import MoneyFlowCollector
    from utils.concept.concept_scorer import ConceptScorer
    
    # 测试股票
    test_stocks = ['600519.SH', '000002.SZ', '002594.SZ']
    
    # 测试技术指标采集
    print("\n1. 测试技术指标采集器:")
    tech_collector = TechnicalCollector()
    tech_data = tech_collector.get_latest_technical_indicators(test_stocks[:1])  # 只测试一只
    if tech_data and '600519.SH' in tech_data:
        data = tech_data['600519.SH']
        print(f"   ✅ 贵州茅台技术指标:")
        print(f"      - MACD状态: {data.get('macd_trend', 'N/A')}")
        print(f"      - KDJ状态: {data.get('kdj_status', 'N/A')}")
        print(f"      - 均线排列: {data.get('ma_trend', 'N/A')}")
    
    # 测试资金流向采集
    print("\n2. 测试资金流向采集器:")
    flow_collector = MoneyFlowCollector()
    flow_data = flow_collector.get_stock_money_flow('600519.SH', days=3)
    if flow_data and flow_data['latest_data']['trade_date']:
        latest = flow_data['latest_data']
        stats = flow_data['statistics']
        print(f"   ✅ 贵州茅台资金流向:")
        print(f"      - 净流入: {latest['net_amount']:.2f}万元")
        print(f"      - 主力净流入: {latest['main_net_amount']:.2f}万元")
        print(f"      - 连续流入天数: {stats['continuous_inflow_days']}天")
    
    # 测试评分器
    print("\n3. 测试概念评分器:")
    scorer = ConceptScorer()
    test_concept_stocks = [
        {'ts_code': '600519.SH', 'name': '贵州茅台', 'concepts': ['白酒', '消费']}
    ]
    
    # 准备评分数据
    tech_data_for_score = {'600519.SH': tech_data.get('600519.SH', {})} if tech_data else {}
    flow_data_for_score = {'600519.SH': flow_data} if flow_data else {}
    
    scored = scorer.calculate_scores(
        test_concept_stocks,
        tech_data_for_score,
        flow_data_for_score,
        {'concept_relevance': 0.4, 'money_flow': 0.3, 'technical': 0.3}
    )
    
    if scored:
        stock = scored[0]
        print(f"   ✅ 评分结果:")
        print(f"      - 总分: {stock.get('total_score', 0):.1f}")
        print(f"      - 概念关联: {stock.get('concept_score', 0):.1f}/40")
        print(f"      - 资金流向: {stock.get('money_flow_score', 0):.1f}/30")
        print(f"      - 技术形态: {stock.get('technical_score', 0):.1f}/30")


def main():
    """主函数"""
    print("="*80)
    print("v2.4.0 Concept Agent Day 3 完整测试")
    print("="*80)
    
    # 先测试组件
    test_scoring_components()
    
    # 再测试完整流程
    print("\n" + "-"*80)
    print("继续测试完整评分流程...")
    test_complete_scoring_flow()
    
    print("\n🎉 Day 3 测试完成！")
    print("如果看到了包含实际评分数据的表格，说明集成成功！")


if __name__ == "__main__":
    main()