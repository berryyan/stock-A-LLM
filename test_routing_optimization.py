#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试路由机制优化
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.hybrid_agent import HybridAgent

def test_trigger_words():
    """测试触发词路由"""
    print("=== 测试触发词路由 ===\n")
    
    agent = HybridAgent()
    
    test_cases = [
        # 触发词测试
        ("排行分析：今日涨幅前10的股票", "rank"),
        ("查询公告：贵州茅台最新年报", "anns"),
        ("董秘互动：平安银行分红计划", "qa"),
        
        # 常规路由测试
        ("贵州茅台最新股价", "sql"),
        ("分析茅台财务健康度", "financial"),
        ("茅台资金流向分析", "money_flow"),
    ]
    
    for question, expected_type in test_cases:
        print(f"问题: {question}")
        
        # 只测试路由决策，不执行实际查询
        routing_decision = agent._route_query(question)
        actual_type = routing_decision['query_type']
        
        print(f"期望路由: {expected_type}")
        print(f"实际路由: {actual_type}")
        print(f"推理原因: {routing_decision.get('reasoning', 'N/A')}")
        print(f"置信度: {routing_decision.get('confidence', 'N/A')}")
        
        if actual_type == expected_type:
            print("✅ 路由正确")
        else:
            print("❌ 路由错误")
        
        print("-" * 50 + "\n")

def test_rule_based_routing():
    """测试规则路由"""
    print("=== 测试规则路由 ===\n")
    
    agent = HybridAgent()
    
    test_cases = [
        ("A股涨幅榜前十", "rank"),
        ("贵州茅台最新公告列表", "anns"),
        ("董秘回复投资者提问", "qa"),
        ("今日涨幅排行榜", "rank"),
        ("查看年报季报", "anns"),
    ]
    
    for question, expected_type in test_cases:
        print(f"问题: {question}")
        
        # 测试规则路由
        routing_decision = agent._rule_based_routing(question)
        actual_type = routing_decision['query_type']
        
        print(f"期望路由: {expected_type}")
        print(f"实际路由: {actual_type}")
        print(f"推理原因: {routing_decision.get('reasoning', 'N/A')}")
        
        if actual_type == expected_type:
            print("✅ 路由正确")
        else:
            print("❌ 路由错误")
        
        print("-" * 50 + "\n")

def test_new_agent_handling():
    """测试新Agent的处理方法"""
    print("=== 测试新Agent处理方法 ===\n")
    
    agent = HybridAgent()
    
    test_queries = [
        "排行分析：市值前20的股票",
        "查询公告：平安银行2024年年报",
        "董秘互动：贵州茅台产能计划",
    ]
    
    for question in test_queries:
        print(f"查询: {question}")
        
        try:
            result = agent.query(question)
            print(f"成功: {result.get('success', False)}")
            
            if not result.get('success'):
                print(f"错误: {result.get('error', 'Unknown error')}")
            else:
                print(f"结果类型: {result.get('type', 'Unknown')}")
            
        except Exception as e:
            print(f"异常: {e}")
        
        print("-" * 50 + "\n")

if __name__ == "__main__":
    print("开始测试路由机制优化...\n")
    
    # 测试触发词路由
    test_trigger_words()
    
    # 测试规则路由
    test_rule_based_routing()
    
    # 测试新Agent处理
    test_new_agent_handling()
    
    print("\n测试完成！")