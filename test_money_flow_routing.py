#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试资金流向路由修复效果
验证个股资金流向与排名查询的区分
"""

from utils.query_templates import match_query_template
from utils.schema_enhanced_router import schema_router

def test_routing():
    """测试路由决策"""
    
    print("=" * 60)
    print("资金流向路由决策测试")
    print("=" * 60)
    
    # 测试用例
    test_cases = [
        # 排名查询（应该路由到SQL_ONLY）
        ("主力净流入最多的前10只股票", "SQL_ONLY", "排名查询"),
        ("主力净流入排名前20", "SQL_ONLY", "排名查询"),
        ("主力资金流入TOP10", "SQL_ONLY", "排名查询"),
        ("昨天主力净流出最多的前5只股票", "SQL_ONLY", "排名查询"),
        ("主力净流入排行", "SQL_ONLY", "排名查询"),
        ("主力资金排名", "SQL_ONLY", "排名查询"),
        
        # 个股查询（应该路由到个股主力资金模板）
        ("贵州茅台的主力净流入", "SQL_ONLY", "个股资金流向"),  # 个股主力资金模板也是SQL_ONLY
        ("平安银行的主力资金流向", "SQL_ONLY", "个股资金流向"),
        ("600519.SH的主力净流入", "SQL_ONLY", "个股资金流向"),
        
        # 资金流向分析（应该路由到MONEY_FLOW）
        ("分析比亚迪的资金流向", "MONEY_FLOW", "资金流向分析"),
        ("茅台的资金流向如何", "MONEY_FLOW", "资金流向分析"),
    ]
    
    success_count = 0
    
    for query, expected_route, query_type in test_cases:
        print(f"\n查询: {query}")
        print(f"类型: {query_type}")
        
        # 测试模板匹配
        template_result = match_query_template(query)
        if template_result:
            template, params = template_result
            print(f"  模板匹配: {template.name} -> {template.route_type}")
            
            # 提取参数
            if 'limit' in params:
                print(f"  提取数量: {params['limit']}")
            if 'entities' in params:
                print(f"  提取实体: {params['entities']}")
            
            if template.route_type == expected_route:
                print(f"  ✅ 模板路由正确")
                success_count += 1
            else:
                print(f"  ❌ 模板路由错误！预期: {expected_route}")
        else:
            print(f"  ❌ 模板未匹配")
            # 如果没有匹配模板，测试Schema快速路由
            quick_route = schema_router.get_quick_route(query)
            if quick_route:
                print(f"  快速路由: {quick_route}")
    
    print(f"\n\n测试结果: {success_count}/{len(test_cases)} 通过")
    
    # 特别测试：验证"主力净流入最多的前10只股票"的处理
    print("\n" + "=" * 60)
    print("特殊测试：验证具体问题查询")
    print("=" * 60)
    
    problem_query = "主力净流入最多的前10只股票"
    print(f"\n问题查询: {problem_query}")
    
    # 1. 测试模板匹配
    template_result = match_query_template(problem_query)
    if template_result:
        template, params = template_result
        print(f"✅ 模板匹配成功: {template.name}")
        print(f"   路由类型: {template.route_type}")
        print(f"   提取参数: {params}")
    else:
        print("❌ 模板匹配失败")
        
    # 2. 测试Schema增强决策
    mock_llm_decision = {
        'query_type': 'RANK',
        'reasoning': 'LLM识别为排名查询'
    }
    
    enhanced = schema_router.enhance_routing_decision(problem_query, mock_llm_decision)
    print(f"\n增强决策测试:")
    print(f"  原始决策: {mock_llm_decision['query_type']}")
    print(f"  最终决策: {enhanced['query_type']}")
    
    if 'override_reason' in enhanced:
        print(f"  覆盖原因: {enhanced['override_reason']}")
    
    if 'schema_analysis' in enhanced:
        analysis = enhanced['schema_analysis']
        print(f"  Schema分析:")
        print(f"    - 检测字段: {analysis.get('detected_fields', [])}")
        print(f"    - 路由评分: {analysis.get('route_scores', {})}")
        print(f"    - 建议类型: {analysis.get('suggested_type', 'N/A')}")


if __name__ == "__main__":
    test_routing()