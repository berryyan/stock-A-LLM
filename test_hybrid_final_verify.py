#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Hybrid Agent最终验证脚本
验证所有功能是否正常工作
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.hybrid_agent_modular import HybridAgentModular
import time
import json


def test_all_scenarios():
    """测试所有场景"""
    print("=" * 80)
    print("Hybrid Agent 最终验证")
    print("=" * 80)
    
    agent = HybridAgentModular()
    
    # 测试用例定义
    test_cases = [
        # 单一路由测试
        {
            "category": "SQL路由",
            "query": "贵州茅台的股价是多少",
            "expected_route": ["sql_only"],
            "description": "股价查询应路由到SQL"
        },
        {
            "category": "SQL路由",
            "query": "今天涨幅前10的股票",
            "expected_route": ["sql_only"],
            "description": "排名查询应路由到SQL"
        },
        {
            "category": "RAG路由",
            "query": "贵州茅台的主要业务是什么",
            "expected_route": ["rag_only"],
            "description": "业务查询应路由到RAG"
        },
        {
            "category": "RAG路由",
            "query": "万科A最新的公告内容",
            "expected_route": ["rag_only"],
            "description": "公告查询应路由到RAG"
        },
        {
            "category": "Financial路由",
            "query": "分析贵州茅台的财务健康度",
            "expected_route": ["financial"],
            "description": "财务分析应路由到Financial"
        },
        {
            "category": "Financial路由",
            "query": "万科A的杜邦分析",
            "expected_route": ["financial"],
            "description": "杜邦分析应路由到Financial"
        },
        {
            "category": "Money Flow路由",
            "query": "贵州茅台的主力资金流向",
            "expected_route": ["sql_only", "money_flow"],  # 可能被优化为SQL
            "description": "资金流向应路由到Money Flow或SQL"
        },
        {
            "category": "Money Flow路由",
            "query": "主力资金净流入前10",
            "expected_route": ["sql_only", "money_flow"],
            "description": "资金排名应路由到Money Flow或SQL"
        },
        # 复合查询测试
        {
            "category": "复合查询",
            "query": "贵州茅台的股价和主要业务",
            "expected_route": ["parallel"],
            "description": "包含SQL和RAG的复合查询"
        },
        {
            "category": "复合查询",
            "query": "万科A的财务状况和最新公告",
            "expected_route": ["parallel"],
            "description": "包含Financial和RAG的复合查询"
        },
        {
            "category": "复合查询",
            "query": "比亚迪的股价及其资金流向",
            "expected_route": ["parallel"],
            "description": "包含SQL和Money Flow的复合查询"
        },
        # 错误处理测试
        {
            "category": "错误处理",
            "query": "",
            "expected_route": ["error"],
            "description": "空查询应返回错误"
        },
        {
            "category": "错误处理",
            "query": "茅台",
            "expected_route": ["error", "rag_only"],  # 可能会尝试搜索
            "description": "股票简称应返回错误或尝试搜索"
        }
    ]
    
    results = {
        "total": len(test_cases),
        "passed": 0,
        "failed": 0,
        "details": []
    }
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n测试 {i}/{len(test_cases)}: {test_case['description']}")
        print(f"类别: {test_case['category']}")
        print(f"查询: {test_case['query']}")
        
        start_time = time.time()
        try:
            # 获取路由决策
            if test_case['query']:  # 非空查询
                routing = agent._route_query(test_case['query'])
                route_type = routing.get('query_type', '').lower()
                print(f"路由决策: {route_type}")
            
            # 执行查询
            result = agent.query(test_case['query'])
            elapsed = time.time() - start_time
            
            # 判断是否成功
            if test_case['category'] == "错误处理":
                # 错误用例应该失败
                test_passed = not result.get('success', True)
                if test_passed:
                    print(f"✅ 正确处理错误: {result.get('error', '')}")
                else:
                    print(f"❌ 未能识别错误")
            else:
                # 正常用例应该成功
                if result.get('success', False):
                    # 检查路由是否正确
                    if test_case['query'] and 'route_type' in locals():
                        if route_type in test_case['expected_route']:
                            print(f"✅ 路由正确: {route_type}")
                            test_passed = True
                        else:
                            print(f"❌ 路由错误: 期望{test_case['expected_route']}, 实际{route_type}")
                            test_passed = False
                    else:
                        test_passed = True
                        print("✅ 查询成功")
                else:
                    print(f"❌ 查询失败: {result.get('error', '未知错误')}")
                    test_passed = False
            
            if test_passed:
                results["passed"] += 1
            else:
                results["failed"] += 1
            
            results["details"].append({
                "test_case": test_case,
                "passed": test_passed,
                "elapsed": elapsed,
                "route_type": route_type if 'route_type' in locals() else None,
                "error": result.get('error') if not result.get('success') else None
            })
            
            print(f"耗时: {elapsed:.2f}秒")
            
        except Exception as e:
            print(f"❌ 异常: {str(e)}")
            results["failed"] += 1
            results["details"].append({
                "test_case": test_case,
                "passed": False,
                "error": str(e)
            })
    
    # 打印总结
    print("\n" + "=" * 80)
    print("测试总结")
    print("=" * 80)
    print(f"总测试数: {results['total']}")
    print(f"通过: {results['passed']} ({results['passed']/results['total']*100:.1f}%)")
    print(f"失败: {results['failed']} ({results['failed']/results['total']*100:.1f}%)")
    
    # 分类统计
    category_stats = {}
    for detail in results["details"]:
        category = detail["test_case"]["category"]
        if category not in category_stats:
            category_stats[category] = {"total": 0, "passed": 0}
        category_stats[category]["total"] += 1
        if detail["passed"]:
            category_stats[category]["passed"] += 1
    
    print("\n按类别统计:")
    for category, stats in category_stats.items():
        pass_rate = stats["passed"] / stats["total"] * 100
        print(f"{category}: {stats['passed']}/{stats['total']} ({pass_rate:.0f}%)")
    
    # 保存结果
    with open('hybrid_agent_final_verify_results.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print(f"\n详细结果已保存到: hybrid_agent_final_verify_results.json")
    
    return results["passed"] / results["total"] >= 0.85  # 85%通过率


if __name__ == "__main__":
    success = test_all_scenarios()
    exit(0 if success else 1)