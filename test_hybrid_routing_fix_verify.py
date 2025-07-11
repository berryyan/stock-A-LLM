#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
验证Hybrid Agent复合查询路由修复效果
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.hybrid_agent_modular import HybridAgentModular
import json
import time


def test_composite_queries():
    """测试复合查询是否正确路由到PARALLEL"""
    print("=" * 80)
    print("验证复合查询路由修复")
    print("=" * 80)
    
    agent = HybridAgentModular()
    
    # 测试用例
    test_cases = [
        {
            "query": "贵州茅台的股价和主要业务",
            "expected_type": "PARALLEL",
            "expected_sources": ["sql", "rag"]
        },
        {
            "query": "万科A的财务状况和最新公告",
            "expected_type": "PARALLEL", 
            "expected_sources": ["financial", "rag"]
        },
        {
            "query": "比亚迪的股价及其资金流向",
            "expected_type": "PARALLEL",
            "expected_sources": ["sql", "money_flow"]
        },
        {
            "query": "宁德时代的财务健康度以及发展战略",
            "expected_type": "PARALLEL",
            "expected_sources": ["financial", "rag"]
        }
    ]
    
    results = {
        "total": len(test_cases),
        "passed": 0,
        "failed": 0,
        "details": []
    }
    
    for i, test_case in enumerate(test_cases, 1):
        query = test_case["query"]
        print(f"\n测试{i}: {query}")
        print("-" * 40)
        
        try:
            # 先测试路由决策
            routing = agent._route_query(query)
            print(f"路由决策: {routing.get('query_type')}")
            
            if routing.get('query_type') == 'PARALLEL':
                print("✅ 正确识别为PARALLEL查询")
                
                # 执行实际查询
                print("\n执行查询...")
                start_time = time.time()
                result = agent.query(query)
                elapsed = time.time() - start_time
                
                if result.get('success'):
                    # 检查sources
                    sources = result.get('sources', {})
                    print(f"返回的数据源: {list(sources.keys())}")
                    
                    # 检查是否包含预期的sources
                    has_expected_sources = any(
                        source_type in str(sources.keys()).lower() 
                        for source_type in test_case["expected_sources"]
                    )
                    
                    if has_expected_sources and len(sources) > 1:
                        print("✅ 包含多个数据源，并行查询成功")
                        results["passed"] += 1
                        test_passed = True
                    else:
                        print("❌ 数据源不符合预期")
                        results["failed"] += 1
                        test_passed = False
                    
                    # 检查answer
                    answer = result.get('answer', '')
                    if answer:
                        print(f"结果长度: {len(answer)}")
                        # 分析结果内容
                        has_price = any(word in answer for word in ['股价', '元/股', '市值'])
                        has_business = any(word in answer for word in ['业务', '主营', '战略'])
                        has_financial = any(word in answer for word in ['财务', '健康度', 'ROE'])
                        has_money = any(word in answer for word in ['资金', '主力', '流向'])
                        
                        info_types = []
                        if has_price: info_types.append("股价信息")
                        if has_business: info_types.append("业务信息")
                        if has_financial: info_types.append("财务信息")
                        if has_money: info_types.append("资金信息")
                        
                        print(f"包含的信息类型: {info_types}")
                else:
                    print(f"❌ 查询失败: {result.get('error')}")
                    results["failed"] += 1
                    test_passed = False
                
                print(f"耗时: {elapsed:.2f}秒")
            else:
                print(f"❌ 路由类型错误: {routing.get('query_type')}")
                results["failed"] += 1
                test_passed = False
            
            results["details"].append({
                "query": query,
                "routing_type": routing.get('query_type'),
                "expected_type": test_case["expected_type"],
                "passed": test_passed,
                "error": result.get('error') if not result.get('success') else None
            })
            
        except Exception as e:
            print(f"❌ 异常: {str(e)}")
            results["failed"] += 1
            results["details"].append({
                "query": query,
                "error": str(e),
                "passed": False
            })
    
    # 打印总结
    print("\n" + "=" * 80)
    print("测试总结")
    print("=" * 80)
    print(f"总测试数: {results['total']}")
    print(f"通过: {results['passed']} ({results['passed']/results['total']*100:.1f}%)")
    print(f"失败: {results['failed']} ({results['failed']/results['total']*100:.1f}%)")
    
    # 保存结果
    with open('hybrid_routing_fix_verify_results.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print(f"\n详细结果已保存到: hybrid_routing_fix_verify_results.json")
    
    return results["passed"] == results["total"]


def test_single_queries():
    """测试单一查询是否正常工作"""
    print("\n" + "=" * 80)
    print("验证单一查询路由")
    print("=" * 80)
    
    agent = HybridAgentModular()
    
    # 单一查询测试
    single_queries = [
        ("贵州茅台的股价", "sql"),
        ("万科A的主要业务", "rag"),
        ("比亚迪的财务健康度", "financial"),
        ("宁德时代的主力资金", "money_flow")
    ]
    
    for query, expected_type in single_queries:
        print(f"\n测试: {query}")
        routing = agent._route_query(query)
        actual_type = routing.get('query_type', '').lower()
        
        if actual_type == expected_type:
            print(f"✅ 正确路由到: {actual_type}")
        else:
            print(f"❌ 错误路由: 期望{expected_type}, 实际{actual_type}")


if __name__ == "__main__":
    # 测试复合查询
    composite_success = test_composite_queries()
    
    # 测试单一查询
    test_single_queries()
    
    exit(0 if composite_success else 1)