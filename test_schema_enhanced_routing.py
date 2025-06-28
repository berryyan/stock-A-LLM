#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试Schema增强路由功能
"""

import sys
import os
from datetime import datetime
import json

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.hybrid_agent import HybridAgent
from utils.schema_enhanced_router import schema_router
from utils.routing_monitor import routing_monitor
from utils.logger import setup_logger

logger = setup_logger("test_schema_routing")


def test_schema_routing():
    """测试Schema增强路由功能"""
    print("=" * 80)
    print("Schema增强路由功能测试")
    print("=" * 80)
    
    # 测试查询
    test_queries = [
        # 财务分析查询
        "分析贵州茅台的财务健康度",
        "茅台的ROE分解分析",
        "平安银行的杜邦分析",
        
        # 资金流向查询
        "茅台的资金流向如何",
        "分析银行板块的主力资金",
        "贵州茅台的超大单资金流入情况",
        
        # SQL查询
        "茅台最新股价是多少",
        "今天涨幅最大的前10只股票",
        "贵州茅台的市值是多少",
        
        # RAG查询
        "贵州茅台最新公告内容",
        "茅台的年报说了什么",
        "解释茅台最近的战略计划",
        
        # 复合查询
        "比较茅台和五粮液的营业收入",
        "分析银行板块的整体表现和资金流向"
    ]
    
    # 初始化HybridAgent
    agent = HybridAgent()
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n{i}. 测试查询: {query}")
        print("-" * 60)
        
        try:
            # 测试快速路由
            quick_route = schema_router.get_quick_route(query)
            if quick_route:
                print(f"   快速路由: {quick_route}")
            
            # 测试字段分析
            field_analysis = schema_router.analyze_query_fields(query)
            if field_analysis['detected_fields'] or field_analysis['chinese_fields']:
                print(f"   检测到的字段:")
                if field_analysis['chinese_fields']:
                    print(f"     中文: {field_analysis['chinese_fields']}")
                if field_analysis['detected_fields']:
                    print(f"     英文: {field_analysis['detected_fields']}")
                if field_analysis['detected_tables']:
                    print(f"     相关表: {list(field_analysis['detected_tables'])}")
            
            # 测试路由得分
            scores = schema_router.calculate_route_scores(query)
            if scores:
                print(f"   路由得分: {dict(sorted(scores.items(), key=lambda x: x[1], reverse=True))}")
            
            # 模拟LLM决策
            mock_llm_decision = {
                'query_type': 'SQL_ONLY',  # 故意设置为SQL_ONLY来测试Schema覆盖
                'entities': [],
                'reasoning': '测试决策'
            }
            
            # 测试增强决策
            enhanced = schema_router.enhance_routing_decision(query, mock_llm_decision)
            print(f"   原始决策: {mock_llm_decision['query_type']}")
            print(f"   增强决策: {enhanced['query_type']}")
            
            if enhanced.get('override_reason'):
                print(f"   覆盖原因: {enhanced['override_reason']}")
            
            if enhanced.get('recommended_tables'):
                print(f"   推荐表: {enhanced['recommended_tables']}")
            
            # 验证路由
            is_valid, warning = schema_router.validate_routing(query, enhanced['query_type'])
            if not is_valid:
                print(f"   ⚠️ 验证警告: {warning}")
            
        except Exception as e:
            print(f"   ❌ 错误: {e}")
            import traceback
            traceback.print_exc()


def test_routing_statistics():
    """测试路由统计功能"""
    print("\n" + "=" * 80)
    print("路由统计信息")
    print("=" * 80)
    
    # 获取统计信息
    stats = routing_monitor.get_statistics()
    
    print(f"\n总查询数: {stats['total_queries']}")
    print(f"成功率: {stats['success_rate']:.1%}")
    print(f"平均响应时间: {stats['avg_response_time']:.2f}秒")
    
    print("\n路由类型分布:")
    for route_type, count in stats['route_distribution'].items():
        percentage = (count / stats['total_queries'] * 100) if stats['total_queries'] > 0 else 0
        print(f"  {route_type}: {count} ({percentage:.1f}%)")
    
    print("\n最近的路由决策:")
    recent = routing_monitor.get_recent_decisions(5)
    for i, decision in enumerate(recent, 1):
        print(f"  {i}. {decision['query'][:50]}...")
        print(f"     类型: {decision['route_type']} | 时间: {decision['timestamp']}")


def test_hybrid_query_with_schema():
    """测试带Schema增强的实际查询"""
    print("\n" + "=" * 80)
    print("实际查询测试（带Schema增强）")
    print("=" * 80)
    
    agent = HybridAgent()
    
    # 测试一个应该走财务分析的查询
    test_query = "分析贵州茅台的财务健康度"
    print(f"\n测试查询: {test_query}")
    
    start_time = datetime.now()
    result = agent.query(test_query)
    elapsed = (datetime.now() - start_time).total_seconds()
    
    print(f"查询耗时: {elapsed:.2f}秒")
    print(f"查询成功: {result.get('success', False)}")
    print(f"路由类型: {result.get('query_type', 'unknown')}")
    
    if result.get('success'):
        print(f"答案预览: {result.get('answer', '')[:200]}...")
    else:
        print(f"错误信息: {result.get('error', '未知错误')}")


if __name__ == "__main__":
    try:
        # 运行测试
        test_schema_routing()
        test_routing_statistics()
        test_hybrid_query_with_schema()
        
        print("\n" + "=" * 80)
        print("✅ Schema增强路由测试完成！")
        print("=" * 80)
        
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()