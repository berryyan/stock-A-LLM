#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
模块化Agent综合测试脚本 - 扩展版
基于test-guide-comprehensive.md设计的全面测试用例
每个Agent至少5个正向测试，3个负向测试
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


class ComprehensiveTestRunner:
    """综合测试运行器"""
    
    def __init__(self):
        self.results = {
            "total": 0,
            "passed": 0,
            "failed": 0,
            "by_agent": {},
            "details": []
        }
        self.start_time = datetime.now()
        
    def test_case(self, name: str, agent_name: str, category: str = "positive"):
        """测试用例装饰器"""
        def decorator(func):
            def wrapper(*args, **kwargs):
                self.results["total"] += 1
                
                # 初始化Agent统计
                if agent_name not in self.results["by_agent"]:
                    self.results["by_agent"][agent_name] = {
                        "total": 0,
                        "passed": 0,
                        "failed": 0,
                        "positive_passed": 0,
                        "positive_failed": 0,
                        "negative_passed": 0,
                        "negative_failed": 0
                    }
                
                self.results["by_agent"][agent_name]["total"] += 1
                
                print(f"\n{'='*80}")
                print(f"测试用例: {name}")
                print(f"Agent: {agent_name} | 类型: {'正向测试' if category == 'positive' else '负向测试'}")
                print(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                print('-'*80)
                
                start_time = time.time()
                try:
                    result = func(*args, **kwargs)
                    elapsed = time.time() - start_time
                    
                    # 判断测试是否通过
                    if category == "positive":
                        # 正向测试：成功为通过
                        test_passed = result.get("success", False)
                    else:
                        # 负向测试：正确处理错误为通过
                        test_passed = not result.get("success", True) and "error" in result
                    
                    if test_passed:
                        self.results["passed"] += 1
                        self.results["by_agent"][agent_name]["passed"] += 1
                        if category == "positive":
                            self.results["by_agent"][agent_name]["positive_passed"] += 1
                        else:
                            self.results["by_agent"][agent_name]["negative_passed"] += 1
                        status = "✅ 通过"
                    else:
                        self.results["failed"] += 1
                        self.results["by_agent"][agent_name]["failed"] += 1
                        if category == "positive":
                            self.results["by_agent"][agent_name]["positive_failed"] += 1
                        else:
                            self.results["by_agent"][agent_name]["negative_failed"] += 1
                        status = "❌ 失败"
                    
                    detail = {
                        "name": name,
                        "agent": agent_name,
                        "category": category,
                        "status": status,
                        "elapsed": f"{elapsed:.2f}s",
                        "result": result
                    }
                    self.results["details"].append(detail)
                    
                    print(f"状态: {status}")
                    print(f"耗时: {elapsed:.2f}秒")
                    if not test_passed:
                        print(f"详情: {result.get('error', '未知错误')}")
                    
                except Exception as e:
                    elapsed = time.time() - start_time
                    self.results["failed"] += 1
                    self.results["by_agent"][agent_name]["failed"] += 1
                    if category == "positive":
                        self.results["by_agent"][agent_name]["positive_failed"] += 1
                    else:
                        self.results["by_agent"][agent_name]["negative_failed"] += 1
                    
                    detail = {
                        "name": name,
                        "agent": agent_name,
                        "category": category,
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
        total_time = (datetime.now() - self.start_time).total_seconds()
        
        print(f"\n{'='*80}")
        print("测试摘要")
        print('='*80)
        print(f"总测试数: {self.results['total']}")
        print(f"通过: {self.results['passed']} ({self.results['passed']/self.results['total']*100:.1f}%)")
        print(f"失败: {self.results['failed']} ({self.results['failed']/self.results['total']*100:.1f}%)")
        print(f"总耗时: {total_time:.2f}秒")
        
        print("\n各Agent测试情况:")
        print("-"*80)
        print(f"{'Agent':<20} {'总数':<8} {'通过':<8} {'失败':<8} {'正向通过':<10} {'负向通过':<10}")
        print("-"*80)
        
        for agent_name, stats in self.results["by_agent"].items():
            print(f"{agent_name:<20} {stats['total']:<8} {stats['passed']:<8} {stats['failed']:<8} "
                  f"{stats['positive_passed']:<10} {stats['negative_passed']:<10}")
        
        # 保存详细结果
        with open("comprehensive_test_results.json", "w", encoding="utf-8") as f:
            json.dump(self.results, f, ensure_ascii=False, indent=2)
        
        print(f"\n详细测试结果已保存到: comprehensive_test_results.json")


# 创建测试运行器
runner = ComprehensiveTestRunner()


# ========== SQL Agent 测试 ==========

# SQL Agent 正向测试

@runner.test_case("股价查询 - 基础", "SQLAgentModular", "positive")
def test_sql_basic_price():
    agent = SQLAgentModular()
    return agent.query("贵州茅台的最新股价")


@runner.test_case("股价查询 - 指定日期", "SQLAgentModular", "positive")
def test_sql_price_with_date():
    agent = SQLAgentModular()
    return agent.query("平安银行2025-07-01的股价")


@runner.test_case("成交量查询", "SQLAgentModular", "positive")
def test_sql_volume():
    agent = SQLAgentModular()
    return agent.query("万科A昨天的成交量")


@runner.test_case("估值指标查询 - PE", "SQLAgentModular", "positive")
def test_sql_pe_ratio():
    agent = SQLAgentModular()
    return agent.query("中国平安的市盈率")


@runner.test_case("K线查询 - 日期范围", "SQLAgentModular", "positive")
def test_sql_kline_range():
    agent = SQLAgentModular()
    return agent.query("贵州茅台从2025-06-01到2025-06-30的K线")


@runner.test_case("涨跌幅排名", "SQLAgentModular", "positive")
def test_sql_ranking_change():
    agent = SQLAgentModular()
    return agent.query("涨幅前10的股票")


@runner.test_case("市值排名", "SQLAgentModular", "positive")
def test_sql_ranking_market_cap():
    agent = SQLAgentModular()
    return agent.query("市值最大的前5")


@runner.test_case("营收排名", "SQLAgentModular", "positive")
def test_sql_ranking_revenue():
    agent = SQLAgentModular()
    return agent.query("营收排名前10")


# SQL Agent 负向测试

@runner.test_case("错误查询 - 空查询", "SQLAgentModular", "negative")
def test_sql_empty_query():
    agent = SQLAgentModular()
    return agent.query("")


@runner.test_case("错误查询 - 无效股票", "SQLAgentModular", "negative")
def test_sql_invalid_stock():
    agent = SQLAgentModular()
    return agent.query("不存在的股票的股价")


@runner.test_case("错误查询 - 股票简称", "SQLAgentModular", "negative")
def test_sql_stock_abbreviation():
    agent = SQLAgentModular()
    return agent.query("茅台的股价")


@runner.test_case("错误查询 - 未来日期", "SQLAgentModular", "negative")
def test_sql_future_date():
    agent = SQLAgentModular()
    return agent.query("贵州茅台2099年的股价")


# ========== RAG Agent 测试 ==========

# RAG Agent 正向测试

@runner.test_case("公告查询 - 年报", "RAGAgentModular", "positive")
def test_rag_annual_report():
    agent = RAGAgentModular()
    return agent.query("贵州茅台最新年报")


@runner.test_case("公告查询 - 季报", "RAGAgentModular", "positive")
def test_rag_quarterly_report():
    agent = RAGAgentModular()
    return agent.query("宁德时代2024年第三季度报告")


@runner.test_case("主题分析 - 发展战略", "RAGAgentModular", "positive")
def test_rag_development_strategy():
    agent = RAGAgentModular()
    return agent.query("贵州茅台的发展战略")


@runner.test_case("主题分析 - 技术优势", "RAGAgentModular", "positive")
def test_rag_tech_advantage():
    agent = RAGAgentModular()
    return agent.query("宁德时代的技术优势")


@runner.test_case("关键词搜索 - 新能源", "RAGAgentModular", "positive")
def test_rag_keyword_search():
    agent = RAGAgentModular()
    return agent.query("新能源汽车相关公告")


# RAG Agent 负向测试

@runner.test_case("错误查询 - 空查询", "RAGAgentModular", "negative")
def test_rag_empty_query():
    agent = RAGAgentModular()
    return agent.query("")


@runner.test_case("错误查询 - 数值查询", "RAGAgentModular", "negative")
def test_rag_numeric_query():
    agent = RAGAgentModular()
    return agent.query("贵州茅台的股价是多少")


@runner.test_case("错误查询 - 无关内容", "RAGAgentModular", "negative")
def test_rag_irrelevant_query():
    agent = RAGAgentModular()
    return agent.query("天气怎么样")


# ========== Financial Agent 测试 ==========

# Financial Agent 正向测试

@runner.test_case("财务健康度分析", "FinancialAgentModular", "positive")
def test_financial_health():
    agent = FinancialAgentModular()
    return agent.query("分析贵州茅台的财务健康度")


@runner.test_case("杜邦分析", "FinancialAgentModular", "positive")
def test_financial_dupont():
    agent = FinancialAgentModular()
    return agent.query("对平安银行进行杜邦分析")


@runner.test_case("现金流质量分析", "FinancialAgentModular", "positive")
def test_financial_cash_flow():
    agent = FinancialAgentModular()
    return agent.query("分析万科A的现金流质量")


@runner.test_case("多期财务对比", "FinancialAgentModular", "positive")
def test_financial_comparison():
    agent = FinancialAgentModular()
    return agent.query("分析贵州茅台的多期财务对比")


@runner.test_case("财务健康度 - 代码查询", "FinancialAgentModular", "positive")
def test_financial_by_code():
    agent = FinancialAgentModular()
    return agent.query("分析600519.SH的财务健康度")


# Financial Agent 负向测试

@runner.test_case("错误查询 - 空查询", "FinancialAgentModular", "negative")
def test_financial_empty_query():
    agent = FinancialAgentModular()
    return agent.query("")


@runner.test_case("错误查询 - 股票简称", "FinancialAgentModular", "negative")
def test_financial_abbreviation():
    agent = FinancialAgentModular()
    return agent.query("茅台的财务健康度")


@runner.test_case("错误查询 - 无效股票", "FinancialAgentModular", "negative")
def test_financial_invalid_stock():
    agent = FinancialAgentModular()
    return agent.query("分析不存在公司的财务健康度")


# ========== Money Flow Agent 测试 ==========

# Money Flow Agent 正向测试

@runner.test_case("主力资金查询", "MoneyFlowAgentModular", "positive")
def test_money_flow_main():
    agent = MoneyFlowAgentModular()
    return agent.query("贵州茅台的主力资金")


@runner.test_case("资金流向分析", "MoneyFlowAgentModular", "positive")
def test_money_flow_analysis():
    agent = MoneyFlowAgentModular()
    return agent.query("分析宁德时代的资金流向")


@runner.test_case("超大单分析", "MoneyFlowAgentModular", "positive")
def test_money_flow_super_large():
    agent = MoneyFlowAgentModular()
    return agent.query("分析比亚迪的超大单资金")


@runner.test_case("板块资金流向", "MoneyFlowAgentModular", "positive")
def test_money_flow_sector():
    agent = MoneyFlowAgentModular()
    return agent.query("银行板块的主力资金")


@runner.test_case("资金流向对比", "MoneyFlowAgentModular", "positive")
def test_money_flow_comparison():
    agent = MoneyFlowAgentModular()
    return agent.query("对比茅台和五粮液的资金流向")


# Money Flow Agent 负向测试

@runner.test_case("错误查询 - 空查询", "MoneyFlowAgentModular", "negative")
def test_money_flow_empty():
    agent = MoneyFlowAgentModular()
    return agent.query("")


@runner.test_case("错误查询 - 非标准术语", "MoneyFlowAgentModular", "negative")
def test_money_flow_nonstandard():
    agent = MoneyFlowAgentModular()
    return agent.query("贵州茅台的游资分析")


@runner.test_case("错误查询 - 无效股票", "MoneyFlowAgentModular", "negative")
def test_money_flow_invalid():
    agent = MoneyFlowAgentModular()
    return agent.query("分析xyz123的资金流向")


# ========== Hybrid Agent 测试 ==========

# Hybrid Agent 正向测试

@runner.test_case("SQL路由测试", "HybridAgentModular", "positive")
def test_hybrid_sql_routing():
    agent = HybridAgentModular()
    return agent.query("贵州茅台的最新股价")


@runner.test_case("RAG路由测试", "HybridAgentModular", "positive")
def test_hybrid_rag_routing():
    agent = HybridAgentModular()
    return agent.query("贵州茅台的公司战略是什么")


@runner.test_case("Financial路由测试", "HybridAgentModular", "positive")
def test_hybrid_financial_routing():
    agent = HybridAgentModular()
    return agent.query("分析贵州茅台的财务状况")


@runner.test_case("复合查询测试", "HybridAgentModular", "positive")
def test_hybrid_composite():
    agent = HybridAgentModular()
    return agent.query("贵州茅台的股价和主要业务")


@runner.test_case("投资价值分析", "HybridAgentModular", "positive")
def test_hybrid_investment():
    agent = HybridAgentModular()
    return agent.query("分析贵州茅台的投资价值")


@runner.test_case("复合查询 - 财务与战略", "HybridAgentModular", "positive")
def test_hybrid_composite_finance():
    agent = HybridAgentModular()
    return agent.query("比亚迪的财务状况以及发展战略")


# Hybrid Agent 负向测试

@runner.test_case("错误传递测试", "HybridAgentModular", "negative")
def test_hybrid_error_propagation():
    agent = HybridAgentModular()
    return agent.query("xyz123")


@runner.test_case("空查询处理", "HybridAgentModular", "negative")
def test_hybrid_empty():
    agent = HybridAgentModular()
    return agent.query("")


@runner.test_case("无效复合查询", "HybridAgentModular", "negative")
def test_hybrid_invalid_composite():
    agent = HybridAgentModular()
    return agent.query("不存在的股票的价格和业务")


def main():
    """运行所有测试"""
    print("模块化Agent综合测试 - 扩展版")
    print("="*80)
    print(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"测试配置: 每个Agent至少5个正向测试，3个负向测试")
    
    # SQL Agent 测试
    print("\n\n【SQL Agent 测试】")
    # 正向测试
    test_sql_basic_price()
    test_sql_price_with_date()
    test_sql_volume()
    test_sql_pe_ratio()
    test_sql_kline_range()
    test_sql_ranking_change()
    test_sql_ranking_market_cap()
    test_sql_ranking_revenue()
    # 负向测试
    test_sql_empty_query()
    test_sql_invalid_stock()
    test_sql_stock_abbreviation()
    test_sql_future_date()
    
    # RAG Agent 测试
    print("\n\n【RAG Agent 测试】")
    # 正向测试
    test_rag_annual_report()
    test_rag_quarterly_report()
    test_rag_development_strategy()
    test_rag_tech_advantage()
    test_rag_keyword_search()
    # 负向测试
    test_rag_empty_query()
    test_rag_numeric_query()
    test_rag_irrelevant_query()
    
    # Financial Agent 测试
    print("\n\n【Financial Agent 测试】")
    # 正向测试
    test_financial_health()
    test_financial_dupont()
    test_financial_cash_flow()
    test_financial_comparison()
    test_financial_by_code()
    # 负向测试
    test_financial_empty_query()
    test_financial_abbreviation()
    test_financial_invalid_stock()
    
    # Money Flow Agent 测试
    print("\n\n【Money Flow Agent 测试】")
    # 正向测试
    test_money_flow_main()
    test_money_flow_analysis()
    test_money_flow_super_large()
    test_money_flow_sector()
    test_money_flow_comparison()
    # 负向测试
    test_money_flow_empty()
    test_money_flow_nonstandard()
    test_money_flow_invalid()
    
    # Hybrid Agent 测试
    print("\n\n【Hybrid Agent 测试】")
    # 正向测试
    test_hybrid_sql_routing()
    test_hybrid_rag_routing()
    test_hybrid_financial_routing()
    test_hybrid_composite()
    test_hybrid_investment()
    test_hybrid_composite_finance()
    # 负向测试
    test_hybrid_error_propagation()
    test_hybrid_empty()
    test_hybrid_invalid_composite()
    
    # 打印测试摘要
    runner.print_summary()
    
    print(f"\n结束时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")


if __name__ == "__main__":
    main()