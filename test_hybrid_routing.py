#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试Hybrid Agent路由决策
验证主力净流入排名等查询的正确路由
"""

from agents.hybrid_agent import HybridAgent

def test_hybrid_routing():
    """测试Hybrid Agent路由"""
    
    print("=" * 60)
    print("Hybrid Agent路由测试")
    print("=" * 60)
    
    agent = HybridAgent()
    
    # 测试用例
    test_cases = [
        # 排名查询（应该路由到SQL）
        ("主力净流入最多的前10只股票", "SQL/RANK", "排名查询"),
        ("今天涨幅最大的前10只股票", "SQL/RANK", "排名查询"),
        ("总市值最大的前20只股票", "SQL/RANK", "排名查询"),
        
        # 个股资金查询（应该路由到SQL_ONLY）
        ("贵州茅台的主力净流入", "SQL_ONLY", "个股资金查询"),
        ("平安银行的主力资金", "SQL_ONLY", "个股资金查询"),
        
        # 资金流向分析（应该路由到MONEY_FLOW）
        ("分析比亚迪的资金流向", "MONEY_FLOW", "资金流向分析"),
        ("茅台的资金流向如何", "MONEY_FLOW", "资金流向分析"),
    ]
    
    for query, expected_route, query_type in test_cases:
        print(f"\n查询: {query}")
        print(f"类型: {query_type}")
        print(f"预期路由: {expected_route}")
        
        try:
            # 获取路由决策
            routing_decision = agent._route_query(query)
            print(f"实际路由: {routing_decision['query_type']}")
            
            if 'reasoning' in routing_decision:
                print(f"推理: {routing_decision['reasoning'][:100]}...")
            
            # 检查是否有Schema覆盖
            if 'override_reason' in routing_decision:
                print(f"⚠️ Schema覆盖: {routing_decision['override_reason']}")
            
            # 判断是否符合预期
            actual_type = routing_decision['query_type'].upper()
            if actual_type in expected_route.upper().split('/'):
                print("✅ 路由正确")
            else:
                print(f"❌ 路由错误！实际: {actual_type}, 预期: {expected_route}")
                
        except Exception as e:
            print(f"❌ 错误: {str(e)}")


if __name__ == "__main__":
    test_hybrid_routing()