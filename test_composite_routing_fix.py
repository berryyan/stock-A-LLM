#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试并修复Hybrid Agent复合查询路由问题
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.hybrid_agent_modular import HybridAgentModular
import json


def test_composite_query_routing():
    """测试复合查询的路由决策"""
    print("=" * 80)
    print("测试Hybrid Agent复合查询路由")
    print("=" * 80)
    
    agent = HybridAgentModular()
    
    # 测试查询
    test_queries = [
        "贵州茅台的股价和主要业务",
        "万科A的财务状况和最新公告",
        "比亚迪的股价及其资金流向",
    ]
    
    for query in test_queries:
        print(f"\n查询: {query}")
        
        # 直接调用私有方法查看路由决策
        try:
            # 1. 检查是否为复合查询
            is_composite = agent._is_composite_query(query)
            print(f"是否复合查询: {is_composite}")
            
            # 2. 查看完整的路由决策
            routing = agent._route_query(query)
            print(f"路由决策: {json.dumps(routing, ensure_ascii=False, indent=2)}")
            
            # 3. 如果是PARALLEL类型，尝试执行
            if routing.get('query_type') == 'PARALLEL':
                print("\n执行并行查询...")
                result = agent.query(query)
                print(f"查询成功: {result.get('success', False)}")
                if result.get('success'):
                    # 检查sources
                    sources = result.get('sources', {})
                    print(f"包含的数据源: {list(sources.keys())}")
                    
                    # 检查结果内容
                    answer = result.get('answer', '')
                    if answer:
                        print(f"结果长度: {len(answer)}")
                        print(f"结果预览: {answer[:200]}...")
                    else:
                        print("⚠️ 结果为空！")
                else:
                    print(f"错误: {result.get('error', '未知错误')}")
            
        except Exception as e:
            print(f"错误: {str(e)}")
        
        print("-" * 80)


def test_routing_priority():
    """测试路由优先级问题"""
    print("\n" + "=" * 80)
    print("测试路由优先级")
    print("=" * 80)
    
    agent = HybridAgentModular()
    
    # 测试一个应该是复合查询的例子
    query = "贵州茅台的股价和主要业务"
    
    print(f"查询: {query}")
    print("\n模拟_route_query方法的执行流程:")
    
    # 1. 触发词检查
    trigger_type = agent._check_trigger_words(query)
    print(f"1. 触发词检查: {trigger_type}")
    
    # 2. 复合查询检查
    if agent._is_composite_query(query):
        parts = agent._analyze_composite_query(query)
        print(f"2. 复合查询检查: True")
        print(f"   查询部分: {parts}")
        
        # 检查是否需要多种查询
        query_types = set()
        for part in parts:
            if any(kw in part for kw in ['股价', '价格', '成交量']):
                query_types.add('SQL')
            if any(kw in part for kw in ['业务', '战略', '公告']):
                query_types.add('RAG')
        
        if len(query_types) > 1:
            print(f"   需要的查询类型: {query_types}")
            print("   ✅ 应该返回PARALLEL")
    
    # 3. 模板匹配（这里可能会覆盖！）
    from utils.query_templates import match_query_template
    template_result = match_query_template(query)
    if template_result:
        template, params = template_result
        print(f"\n3. 模板匹配: {template.name}")
        print(f"   模板路由类型: {template.route_type}")
        print("   ⚠️ 这会覆盖复合查询的PARALLEL决策！")


if __name__ == "__main__":
    # 测试复合查询路由
    test_composite_query_routing()
    
    # 测试路由优先级问题
    test_routing_priority()