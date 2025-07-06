#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
模块化Agent冒烟测试脚本
测试所有5个模块化Agent的核心功能
"""
import sys
import os
import time
import json
from datetime import datetime
from typing import Dict, List, Any

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 导入所有模块化Agent
from agents.sql_agent_modular import SQLAgentModular
from agents.rag_agent_modular import RAGAgentModular
from agents.financial_agent_modular import FinancialAgentModular
from agents.money_flow_agent_modular import MoneyFlowAgentModular
from agents.hybrid_agent_modular import HybridAgentModular


class SmokeTestRunner:
    """冒烟测试运行器"""
    
    def __init__(self):
        self.results = {
            "total": 0,
            "passed": 0,
            "failed": 0,
            "details": []
        }
        
    def test_case(self, name: str, agent_name: str):
        """测试用例装饰器"""
        def decorator(func):
            def wrapper(*args, **kwargs):
                self.results["total"] += 1
                print(f"\n{'='*80}")
                print(f"测试用例: {name}")
                print(f"Agent: {agent_name}")
                print(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                print('-'*80)
                
                start_time = time.time()
                try:
                    result = func(*args, **kwargs)
                    elapsed = time.time() - start_time
                    
                    if result.get("success", False):
                        self.results["passed"] += 1
                        status = "✅ 通过"
                    else:
                        self.results["failed"] += 1
                        status = "❌ 失败"
                    
                    detail = {
                        "name": name,
                        "agent": agent_name,
                        "status": status,
                        "elapsed": f"{elapsed:.2f}s",
                        "result": result
                    }
                    self.results["details"].append(detail)
                    
                    print(f"状态: {status}")
                    print(f"耗时: {elapsed:.2f}秒")
                    if not result.get("success", False):
                        print(f"错误: {result.get('error', '未知错误')}")
                    
                except Exception as e:
                    elapsed = time.time() - start_time
                    self.results["failed"] += 1
                    detail = {
                        "name": name,
                        "agent": agent_name,
                        "status": "❌ 异常",
                        "elapsed": f"{elapsed:.2f}s",
                        "error": str(e)
                    }
                    self.results["details"].append(detail)
                    
                    print(f"状态: ❌ 异常")
                    print(f"错误: {str(e)}")
                    
            return wrapper
        return decorator
    
    def print_summary(self):
        """打印测试摘要"""
        print(f"\n{'='*80}")
        print("测试摘要")
        print('='*80)
        print(f"总测试数: {self.results['total']}")
        print(f"通过: {self.results['passed']} ({self.results['passed']/self.results['total']*100:.1f}%)")
        print(f"失败: {self.results['failed']} ({self.results['failed']/self.results['total']*100:.1f}%)")
        print("\n详细结果:")
        print("-"*80)
        print(f"{'测试名称':<30} {'Agent':<20} {'状态':<10} {'耗时':<10}")
        print("-"*80)
        
        for detail in self.results["details"]:
            print(f"{detail['name']:<30} {detail['agent']:<20} {detail['status']:<10} {detail['elapsed']:<10}")


# 创建测试运行器
runner = SmokeTestRunner()


# SQL Agent 测试
@runner.test_case("股价查询", "SQLAgentModular")
def test_sql_stock_price():
    agent = SQLAgentModular()
    return agent.query("贵州茅台的最新股价")


@runner.test_case("财务数据查询", "SQLAgentModular")
def test_sql_financial_data():
    agent = SQLAgentModular()
    return agent.query("比亚迪的市盈率是多少")


@runner.test_case("排名查询", "SQLAgentModular")
def test_sql_ranking():
    agent = SQLAgentModular()
    return agent.query("市值排名前5的股票")


@runner.test_case("错误处理测试", "SQLAgentModular")
def test_sql_error_handling():
    agent = SQLAgentModular()
    return agent.query("abc")


# RAG Agent 测试
@runner.test_case("公告搜索", "RAGAgentModular")
def test_rag_announcement():
    agent = RAGAgentModular()
    return agent.query("贵州茅台最新的年报")


@runner.test_case("关键词搜索", "RAGAgentModular")
def test_rag_keyword():
    agent = RAGAgentModular()
    return agent.query("新能源汽车相关公告")


# Financial Agent 测试
@runner.test_case("财务健康度分析", "FinancialAgentModular")
def test_financial_health():
    agent = FinancialAgentModular()
    return agent.query("分析贵州茅台的财务健康度")


@runner.test_case("杜邦分析", "FinancialAgentModular")
def test_financial_dupont():
    agent = FinancialAgentModular()
    return agent.query("对贵州茅台进行杜邦分析")


# Money Flow Agent 测试
@runner.test_case("主力资金分析", "MoneyFlowAgentModular")
def test_money_flow_main():
    agent = MoneyFlowAgentModular()
    return agent.query("贵州茅台的主力资金")


@runner.test_case("资金流向分析", "MoneyFlowAgentModular")
def test_money_flow_analysis():
    agent = MoneyFlowAgentModular()
    return agent.query("分析贵州茅台的资金流向")


# Hybrid Agent 测试
@runner.test_case("SQL路由测试", "HybridAgentModular")
def test_hybrid_sql_routing():
    agent = HybridAgentModular()
    return agent.query("贵州茅台的股价")


@runner.test_case("RAG路由测试", "HybridAgentModular")
def test_hybrid_rag_routing():
    agent = HybridAgentModular()
    return agent.query("贵州茅台的公司战略是什么")


@runner.test_case("Financial路由测试", "HybridAgentModular")
def test_hybrid_financial_routing():
    agent = HybridAgentModular()
    return agent.query("分析贵州茅台的财务状况")


@runner.test_case("MoneyFlow路由测试", "HybridAgentModular")
def test_hybrid_money_routing():
    agent = HybridAgentModular()
    return agent.query("分析贵州茅台的资金流向")


@runner.test_case("错误传递测试", "HybridAgentModular")
def test_hybrid_error_propagation():
    agent = HybridAgentModular()
    return agent.query("xyz123")


def main():
    """运行所有测试"""
    print("模块化Agent冒烟测试")
    print("="*80)
    print(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # SQL Agent 测试
    print("\n\n【SQL Agent 测试】")
    test_sql_stock_price()
    test_sql_financial_data()
    test_sql_ranking()
    test_sql_error_handling()
    
    # RAG Agent 测试
    print("\n\n【RAG Agent 测试】")
    test_rag_announcement()
    test_rag_keyword()
    
    # Financial Agent 测试
    print("\n\n【Financial Agent 测试】")
    test_financial_health()
    test_financial_dupont()
    
    # Money Flow Agent 测试
    print("\n\n【Money Flow Agent 测试】")
    test_money_flow_main()
    test_money_flow_analysis()
    
    # Hybrid Agent 测试
    print("\n\n【Hybrid Agent 测试】")
    test_hybrid_sql_routing()
    test_hybrid_rag_routing()
    test_hybrid_financial_routing()
    test_hybrid_money_routing()
    test_hybrid_error_propagation()
    
    # 打印测试摘要
    runner.print_summary()
    
    # 保存测试结果
    with open("smoke_test_results.json", "w", encoding="utf-8") as f:
        json.dump(runner.results, f, ensure_ascii=False, indent=2)
    
    print(f"\n测试结果已保存到: smoke_test_results.json")
    print(f"结束时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")


if __name__ == "__main__":
    main()