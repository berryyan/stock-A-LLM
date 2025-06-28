#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
路由决策分析工具
分析系统中所有的路由判断机制和对应的Agent
"""

import json
from typing import Dict, List
from agents.hybrid_agent import QueryType

def analyze_routing_system():
    """分析路由系统"""
    print("="*70)
    print("股票分析系统路由决策机制分析")
    print("="*70)
    
    # 1. 查询类型枚举
    print("\n1. 支持的查询类型 (QueryType):")
    print("-"*50)
    query_types = [
        ("SQL_ONLY", "仅SQL查询", "SQLAgent"),
        ("RAG_ONLY", "仅RAG查询", "RAGAgent"),
        ("FINANCIAL", "财务分析", "FinancialAnalysisAgent"),
        ("MONEY_FLOW", "资金流向分析", "MoneyFlowAgent"),
        ("SQL_FIRST", "先SQL后RAG", "SQLAgent + RAGAgent"),
        ("RAG_FIRST", "先RAG后SQL", "RAGAgent + SQLAgent"),
        ("PARALLEL", "并行查询", "SQLAgent || RAGAgent"),
        ("COMPLEX", "复杂查询", "多Agent协同")
    ]
    
    for query_type, desc, agent in query_types:
        print(f"  {query_type:<15} - {desc:<15} -> {agent}")
    
    # 2. 路由决策机制
    print("\n\n2. 路由决策机制:")
    print("-"*50)
    print("a) 主路由器 (HybridAgent)")
    print("   - LLM智能路由（主要）")
    print("   - 规则匹配路由（降级）")
    print("   - 关键词评分机制")
    
    # 3. 关键词映射
    print("\n\n3. 各类查询的关键词映射:")
    print("-"*50)
    
    patterns = {
        'SQL查询': {
            'keywords': ['股价', '市值', '涨跌', '成交量', '市盈率', '总资产', '营收', '净利润', '排名', '统计'],
            'patterns': ['最新.*价格', '.*排名前\\d+', '.*最高.*最低']
        },
        'RAG查询': {
            'keywords': ['公告', '报告', '说明', '解释', '原因', '计划', '战略', '风险', '优势'],
            'patterns': ['.*报告.*内容', '.*公告.*说', '.*未来.*计划']
        },
        '财务分析': {
            'keywords': ['财务健康', '财务状况', '经营状况', '财务评级', '健康度', '盈利能力', 'ROE', 'ROA', '杜邦分析', '现金流质量'],
            'patterns': ['.*财务.*分析', '.*杜邦.*分析', 'ROE.*分解']
        },
        '资金流向': {
            'keywords': ['资金流向', '资金流入', '资金流出', '主力资金', '机构资金', '超大单', '大单'],
            'patterns': ['.*资金.*流向', '.*主力.*资金', '.*机构.*行为']
        }
    }
    
    for category, info in patterns.items():
        print(f"\n{category}:")
        print(f"  关键词: {', '.join(info['keywords'][:5])}...")
        print(f"  模式数: {len(info['patterns'])}")
    
    # 4. Agent映射关系
    print("\n\n4. Agent映射关系:")
    print("-"*50)
    agents = {
        'SQLAgent': '处理结构化数据查询（股价、财务数据、排名等）',
        'RAGAgent': '处理文档检索（公告、报告、新闻等）',
        'FinancialAnalysisAgent': '专业财务分析（健康度评分、杜邦分析、现金流分析）',
        'MoneyFlowAgent': '资金流向分析（主力行为、资金分布、买卖力量）',
        'HybridAgent': '智能路由和结果整合'
    }
    
    for agent, desc in agents.items():
        print(f"  {agent:<25} - {desc}")
    
    # 5. 决策流程
    print("\n\n5. 路由决策流程:")
    print("-"*50)
    print("  1. 用户查询 -> HybridAgent")
    print("  2. LLM分析查询意图")
    print("  3. 返回JSON格式决策:")
    print("     - query_type: 查询类型")
    print("     - reasoning: 决策理由")
    print("     - sql_needed: 是否需要SQL")
    print("     - rag_needed: 是否需要RAG")
    print("     - entities: 识别的实体")
    print("  4. 根据query_type路由到对应Agent")
    print("  5. 整合结果返回用户")
    
    # 6. 优化建议
    print("\n\n6. 当前系统优化建议:")
    print("-"*50)
    print("  ✓ Schema知识库已集成，提升SQL查询性能")
    print("  ⚠ LLM输出格式需要优化，避免解析错误")
    print("  ⚡ 可以基于Schema知识库增强路由决策")
    print("  📊 需要路由决策统计和可视化")
    
    print("\n" + "="*70)


def generate_routing_stats_template():
    """生成路由统计模板"""
    stats_template = {
        "total_queries": 0,
        "routing_distribution": {
            "SQL_ONLY": 0,
            "RAG_ONLY": 0,
            "FINANCIAL": 0,
            "MONEY_FLOW": 0,
            "SQL_FIRST": 0,
            "RAG_FIRST": 0,
            "PARALLEL": 0,
            "COMPLEX": 0
        },
        "success_rate": {
            "SQL_ONLY": 0.0,
            "RAG_ONLY": 0.0,
            "FINANCIAL": 0.0,
            "MONEY_FLOW": 0.0
        },
        "avg_response_time": {
            "SQL_ONLY": 0.0,
            "RAG_ONLY": 0.0,
            "FINANCIAL": 0.0,
            "MONEY_FLOW": 0.0
        },
        "keyword_hits": {},
        "common_queries": []
    }
    
    print("\n\n路由统计模板（用于未来的监控）:")
    print(json.dumps(stats_template, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    analyze_routing_system()
    generate_routing_stats_template()