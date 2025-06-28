#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试优化效果
1. 测试输出格式优化
2. 测试路由决策
3. 测试灵活解析器
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.sql_agent import SQLAgent
from agents.hybrid_agent import HybridAgent
from utils.flexible_parser import FlexibleSQLOutputParser, test_parser
from utils.logger import setup_logger

logger = setup_logger("test_optimizations")


def test_output_format_optimization():
    """测试输出格式优化"""
    print("="*60)
    print("1. 测试SQL Agent输出格式优化")
    print("="*60)
    
    agent = SQLAgent()
    
    test_queries = [
        "贵州茅台最新股价是多少？",
        "查询比亚迪今天的成交量",
        "平安银行最近5天的涨跌幅"
    ]
    
    for query in test_queries:
        print(f"\n测试查询: {query}")
        print("-"*40)
        
        try:
            result = agent.query(query)
            
            if result['success']:
                print("✅ 查询成功!")
                print(f"结果: {result['result'][:200]}...")
            else:
                print("❌ 查询失败!")
                print(f"错误: {result.get('error', 'Unknown error')}")
                
        except Exception as e:
            print(f"❌ 异常: {e}")


def test_flexible_parser():
    """测试灵活解析器"""
    print("\n\n" + "="*60)
    print("2. 测试灵活解析器")
    print("="*60)
    
    test_parser()


def test_routing_decisions():
    """测试路由决策"""
    print("\n\n" + "="*60)
    print("3. 测试路由决策")
    print("="*60)
    
    agent = HybridAgent()
    
    test_queries = [
        ("贵州茅台最新股价", "SQL_ONLY"),
        ("分析茅台的财务健康度", "FINANCIAL"),
        ("茅台最近30天的资金流向", "MONEY_FLOW"),
        ("贵州茅台最新公告内容", "RAG_ONLY"),
        ("分析茅台的业绩和股价表现", "PARALLEL或COMPLEX")
    ]
    
    for query, expected in test_queries:
        print(f"\n查询: {query}")
        print(f"预期路由: {expected}")
        
        try:
            # 测试路由决策
            decision = agent._route_query(query)
            print(f"实际路由: {decision.get('query_type', 'Unknown')}")
            print(f"决策理由: {decision.get('reasoning', 'N/A')[:100]}...")
            
            if 'entities' in decision:
                print(f"识别实体: {decision['entities']}")
                
        except Exception as e:
            print(f"路由失败: {e}")


def test_schema_enhanced_routing():
    """测试Schema增强的路由决策"""
    print("\n\n" + "="*60)
    print("4. 测试Schema知识库增强路由")
    print("="*60)
    
    from utils.schema_knowledge_base import schema_kb
    
    # 测试基于字段匹配的路由建议
    test_cases = [
        ("查询营业收入和净利润", ["营业收入", "净利润"]),
        ("分析总资产和负债率", ["总资产", "负债"]),
        ("查看市盈率和市净率", ["市盈率", "市净率"]),
        ("大单净流入情况", ["大单", "净流入"])
    ]
    
    for query, keywords in test_cases:
        print(f"\n查询: {query}")
        print(f"关键词: {keywords}")
        
        # 使用Schema知识库建议
        suggestions = schema_kb.suggest_fields_for_query(keywords)
        if suggestions:
            print("Schema知识库建议:")
            for table, fields in suggestions.items():
                print(f"  表: {table}, 字段: {fields}")
                
            # 根据表名推断路由
            if any('income' in t or 'balancesheet' in t for t in suggestions):
                print("  → 建议路由: FINANCIAL")
            elif any('moneyflow' in t for t in suggestions):
                print("  → 建议路由: MONEY_FLOW")
            elif any('daily' in t for t in suggestions):
                print("  → 建议路由: SQL_ONLY")
        else:
            print("  Schema知识库无建议")


def summarize_test_results():
    """总结测试结果"""
    print("\n\n" + "="*60)
    print("优化效果总结")
    print("="*60)
    
    print("\n已完成的优化:")
    print("1. ✅ SQL Agent prompt优化 - 强化Final Answer格式要求")
    print("2. ✅ 创建灵活解析器 - 支持多种输出格式")
    print("3. ✅ 路由分析工具 - 明确系统路由机制")
    print("4. ✅ Schema知识库集成 - 可用于增强路由决策")
    
    print("\n路由决策机制总结:")
    print("- 8种查询类型（SQL_ONLY, RAG_ONLY, FINANCIAL等）")
    print("- 5个专门Agent（SQL, RAG, Financial, MoneyFlow, Hybrid）")
    print("- 2层路由机制（LLM智能路由 + 规则降级）")
    print("- 4类关键词模式（SQL, RAG, 财务, 资金流向）")
    
    print("\n下一步建议:")
    print("1. 集成灵活解析器到SQL Agent")
    print("2. 增加路由决策的监控和统计")
    print("3. 基于Schema知识库优化路由规则")
    print("4. 为常见查询创建快速路由模板")


if __name__ == "__main__":
    # 运行所有测试
    test_output_format_optimization()
    test_flexible_parser()
    test_routing_decisions()
    test_schema_enhanced_routing()
    summarize_test_results()
    
    print("\n\n测试完成！请检查结果并进行实际查询测试。")