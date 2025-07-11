#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Hybrid Agent 全面测试套件
基于test-guide-comprehensive.md的完整功能测试
覆盖所有混合查询和路由功能，每个功能至少5个正向测试，3个负向测试
"""
import sys
import os
import time
import json
from datetime import datetime
from typing import Dict, List, Any

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.hybrid_agent_modular import HybridAgentModular


class HybridAgentTestRunner:
    """Hybrid Agent专项测试运行器"""
    
    def __init__(self):
        self.results = {
            "agent": "HybridAgentModular",
            "total": 0,
            "passed": 0,
            "failed": 0,
            "functions": {},
            "details": []
        }
        self.start_time = datetime.now()
        
    def test_case(self, name: str, function: str, category: str = "positive"):
        """测试用例装饰器"""
        def decorator(func):
            def wrapper(*args, **kwargs):
                self.results["total"] += 1
                
                # 初始化功能统计
                if function not in self.results["functions"]:
                    self.results["functions"][function] = {
                        "total": 0,
                        "passed": 0,
                        "failed": 0,
                        "positive_passed": 0,
                        "positive_failed": 0,
                        "negative_passed": 0,
                        "negative_failed": 0
                    }
                
                self.results["functions"][function]["total"] += 1
                
                print(f"\n{'='*80}")
                print(f"测试用例: {name}")
                print(f"功能: {function} | 类型: {'正向测试' if category == 'positive' else '负向测试'}")
                print(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                print('-'*80)
                
                start_time = time.time()
                try:
                    result = func(*args, **kwargs)
                    elapsed = time.time() - start_time
                    
                    # 判断测试是否通过
                    if category == "positive":
                        test_passed = result.get("success", False)
                    else:
                        test_passed = not result.get("success", True) and "error" in result
                    
                    if test_passed:
                        self.results["passed"] += 1
                        self.results["functions"][function]["passed"] += 1
                        if category == "positive":
                            self.results["functions"][function]["positive_passed"] += 1
                        else:
                            self.results["functions"][function]["negative_passed"] += 1
                        status = "✅ 通过"
                    else:
                        self.results["failed"] += 1
                        self.results["functions"][function]["failed"] += 1
                        if category == "positive":
                            self.results["functions"][function]["positive_failed"] += 1
                        else:
                            self.results["functions"][function]["negative_failed"] += 1
                        status = "❌ 失败"
                    
                    detail = {
                        "name": name,
                        "function": function,
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
                    self.results["functions"][function]["failed"] += 1
                    if category == "positive":
                        self.results["functions"][function]["positive_failed"] += 1
                    else:
                        self.results["functions"][function]["negative_failed"] += 1
                    
                    detail = {
                        "name": name,
                        "function": function,
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
        print("Hybrid Agent 测试摘要")
        print('='*80)
        print(f"总测试数: {self.results['total']}")
        print(f"通过: {self.results['passed']} ({self.results['passed']/self.results['total']*100:.1f}%)")
        print(f"失败: {self.results['failed']} ({self.results['failed']/self.results['total']*100:.1f}%)")
        print(f"总耗时: {total_time:.2f}秒")
        
        print("\n按功能分类的测试结果:")
        print("-"*80)
        print(f"{'功能':<30} {'总计':<8} {'通过':<8} {'失败':<8} {'正向通过':<10} {'负向通过':<10}")
        print("-"*80)
        
        for func_name, stats in self.results["functions"].items():
            print(f"{func_name:<30} {stats['total']:<8} {stats['passed']:<8} {stats['failed']:<8} "
                  f"{stats['positive_passed']:<10} {stats['negative_passed']:<10}")
        
        # 保存详细结果
        with open("hybrid_agent_comprehensive_results.json", "w", encoding="utf-8") as f:
            json.dump(self.results, f, ensure_ascii=False, indent=2)
        
        print(f"\n详细测试结果已保存至: hybrid_agent_comprehensive_results.json")


# 创建测试运行器
runner = HybridAgentTestRunner()


# ========== 1. 智能路由功能测试 ==========

# 正向测试
@runner.test_case("SQL路由 - 股价查询", "智能路由", "positive")
def test_routing_sql_price():
    agent = HybridAgentModular()
    return agent.query("贵州茅台最新股价")

@runner.test_case("RAG路由 - 公司战略", "智能路由", "positive")
def test_routing_rag_strategy():
    agent = HybridAgentModular()
    return agent.query("贵州茅台的公司战略是什么")

@runner.test_case("Financial路由 - 财务分析", "智能路由", "positive")
def test_routing_financial():
    agent = HybridAgentModular()
    return agent.query("分析贵州茅台的财务状况")

@runner.test_case("MoneyFlow路由 - 资金流向", "智能路由", "positive")
def test_routing_money_flow():
    agent = HybridAgentModular()
    return agent.query("分析贵州茅台的资金流向")

@runner.test_case("SQL路由 - K线查询", "智能路由", "positive")
def test_routing_sql_kline():
    agent = HybridAgentModular()
    return agent.query("万科A最近30天的K线")

@runner.test_case("RAG路由 - 年报分析", "智能路由", "positive")
def test_routing_rag_report():
    agent = HybridAgentModular()
    return agent.query("分析贵州茅台最新年报")

@runner.test_case("Financial路由 - 杜邦分析", "智能路由", "positive")
def test_routing_financial_dupont():
    agent = HybridAgentModular()
    return agent.query("对平安银行进行杜邦分析")

# 负向测试
@runner.test_case("路由错误 - 空查询", "智能路由", "negative")
def test_routing_empty():
    agent = HybridAgentModular()
    return agent.query("")

@runner.test_case("路由错误 - 无效查询", "智能路由", "negative")
def test_routing_invalid():
    agent = HybridAgentModular()
    return agent.query("!@#$%^&*()")

@runner.test_case("路由错误 - 模糊查询", "智能路由", "negative")
def test_routing_ambiguous():
    agent = HybridAgentModular()
    return agent.query("查询一下")


# ========== 2. 复合查询功能测试 ==========

# 正向测试
@runner.test_case("复合查询 - 股价和业务", "复合查询", "positive")
def test_composite_price_business():
    agent = HybridAgentModular()
    return agent.query("贵州茅台的股价和主要业务")

@runner.test_case("复合查询 - 财务以及战略", "复合查询", "positive")
def test_composite_finance_strategy():
    agent = HybridAgentModular()
    return agent.query("比亚迪的财务状况以及发展战略")

@runner.test_case("复合查询 - 市值还有技术", "复合查询", "positive")
def test_composite_cap_tech():
    agent = HybridAgentModular()
    return agent.query("宁德时代的市值还有技术优势")

@runner.test_case("复合查询 - 业绩同时风险", "复合查询", "positive")
def test_composite_performance_risk():
    agent = HybridAgentModular()
    return agent.query("中国平安的业绩同时分析其风险")

@runner.test_case("复合查询 - 多连接词", "复合查询", "positive")
def test_composite_multiple_connectors():
    agent = HybridAgentModular()
    return agent.query("万科A的股价及其财务状况和发展前景")

@runner.test_case("复合查询 - 并且连接", "复合查询", "positive")
def test_composite_and():
    agent = HybridAgentModular()
    return agent.query("贵州茅台的营收并且分析其竞争优势")

# 负向测试
@runner.test_case("复合查询 - 单一内容", "复合查询", "negative")
def test_composite_single():
    agent = HybridAgentModular()
    return agent.query("贵州茅台和")

@runner.test_case("复合查询 - 重复内容", "复合查询", "negative")
def test_composite_duplicate():
    agent = HybridAgentModular()
    return agent.query("股价和股价")

@runner.test_case("复合查询 - 无效组合", "复合查询", "negative")
def test_composite_invalid_combo():
    agent = HybridAgentModular()
    return agent.query("xyz和abc")


# ========== 3. 投资价值分析功能测试 ==========

# 正向测试
@runner.test_case("投资价值 - 基础分析", "投资价值分析", "positive")
def test_investment_basic():
    agent = HybridAgentModular()
    return agent.query("分析贵州茅台的投资价值")

@runner.test_case("投资价值 - 评估机会", "投资价值分析", "positive")
def test_investment_opportunity():
    agent = HybridAgentModular()
    return agent.query("评估宁德时代的投资机会")

@runner.test_case("投资价值 - 是否值得", "投资价值分析", "positive")
def test_investment_worth():
    agent = HybridAgentModular()
    return agent.query("比亚迪值得投资吗")

@runner.test_case("投资价值 - 投资潜力", "投资价值分析", "positive")
def test_investment_potential():
    agent = HybridAgentModular()
    return agent.query("万科A的投资潜力如何")

@runner.test_case("投资价值 - 综合评估", "投资价值分析", "positive")
def test_investment_comprehensive():
    agent = HybridAgentModular()
    return agent.query("综合评估平安银行的投资价值")

@runner.test_case("投资价值 - 长期价值", "投资价值分析", "positive")
def test_investment_long_term():
    agent = HybridAgentModular()
    return agent.query("分析贵州茅台的长期投资价值")

# 负向测试
@runner.test_case("投资价值 - 空泛查询", "投资价值分析", "negative")
def test_investment_vague():
    agent = HybridAgentModular()
    return agent.query("投资价值")

@runner.test_case("投资价值 - 无股票", "投资价值分析", "negative")
def test_investment_no_stock():
    agent = HybridAgentModular()
    return agent.query("分析投资价值")

@runner.test_case("投资价值 - 简称错误", "投资价值分析", "negative")
def test_investment_abbreviation():
    agent = HybridAgentModular()
    return agent.query("茅台值得买吗")


# ========== 4. 风险评估分析功能测试 ==========

# 正向测试
@runner.test_case("风险评估 - 财务风险", "风险评估分析", "positive")
def test_risk_financial():
    agent = HybridAgentModular()
    return agent.query("评估万科A的财务风险和股价表现")

@runner.test_case("风险评估 - 风险状况", "风险评估分析", "positive")
def test_risk_status():
    agent = HybridAgentModular()
    return agent.query("分析恒大的风险状况")

@runner.test_case("风险评估 - 经营风险", "风险评估分析", "positive")
def test_risk_operational():
    agent = HybridAgentModular()
    return agent.query("评估中国平安的经营风险")

@runner.test_case("风险评估 - 系统性风险", "风险评估分析", "positive")
def test_risk_systematic():
    agent = HybridAgentModular()
    return agent.query("分析银行股的系统性风险")

@runner.test_case("风险评估 - 股价波动", "风险评估分析", "positive")
def test_risk_volatility():
    agent = HybridAgentModular()
    return agent.query("评估宁德时代的股价波动风险")

# 负向测试
@runner.test_case("风险评估 - 无具体内容", "风险评估分析", "negative")
def test_risk_no_content():
    agent = HybridAgentModular()
    return agent.query("风险")

@runner.test_case("风险评估 - 错误类型", "风险评估分析", "negative")
def test_risk_wrong_type():
    agent = HybridAgentModular()
    return agent.query("贵州茅台的天气风险")

@runner.test_case("风险评估 - 不相关查询", "风险评估分析", "negative")
def test_risk_irrelevant():
    agent = HybridAgentModular()
    return agent.query("评估风险收益比")


# ========== 5. 综合对比分析功能测试 ==========

# 正向测试
@runner.test_case("综合对比 - 两股对比", "综合对比分析", "positive")
def test_comparison_two_stocks():
    agent = HybridAgentModular()
    return agent.query("对比茅台和五粮液的综合实力")

@runner.test_case("综合对比 - 各方面表现", "综合对比分析", "positive")
def test_comparison_all_aspects():
    agent = HybridAgentModular()
    return agent.query("比较宁德时代和比亚迪的各方面表现")

@runner.test_case("综合对比 - vs格式", "综合对比分析", "positive")
def test_comparison_vs():
    agent = HybridAgentModular()
    return agent.query("平安银行 vs 招商银行全面对比")

@runner.test_case("综合对比 - 多维度", "综合对比分析", "positive")
def test_comparison_multi_dimension():
    agent = HybridAgentModular()
    return agent.query("从财务、技术、市场等角度对比茅台和五粮液")

@runner.test_case("综合对比 - 投资角度", "综合对比分析", "positive")
def test_comparison_investment():
    agent = HybridAgentModular()
    return agent.query("从投资角度对比万科A和保利地产")

# 负向测试
@runner.test_case("综合对比 - 单一股票", "综合对比分析", "negative")
def test_comparison_single():
    agent = HybridAgentModular()
    return agent.query("对比贵州茅台")

@runner.test_case("综合对比 - 过多股票", "综合对比分析", "negative")
def test_comparison_too_many():
    agent = HybridAgentModular()
    return agent.query("对比茅台、五粮液、泸州老窖、洋河、剑南春")

@runner.test_case("综合对比 - 无效股票", "综合对比分析", "negative")
def test_comparison_invalid_stocks():
    agent = HybridAgentModular()
    return agent.query("对比ABC和XYZ")


# ========== 6. 错误传递功能测试 ==========

# 正向测试
@runner.test_case("错误传递 - SQL错误", "错误传递", "positive")
def test_error_sql():
    agent = HybridAgentModular()
    result = agent.query("xyz123的股价")
    # 应该返回具体的错误信息
    return {"success": not result.get("success", True) and "error" in result}

@runner.test_case("错误传递 - RAG错误", "错误传递", "positive")
def test_error_rag():
    agent = HybridAgentModular()
    result = agent.query("不存在公司的年报")
    return {"success": not result.get("success", True) and "error" in result}

@runner.test_case("错误传递 - Financial错误", "错误传递", "positive")
def test_error_financial():
    agent = HybridAgentModular()
    result = agent.query("分析xyz的财务健康度")
    return {"success": not result.get("success", True) and "error" in result}

@runner.test_case("错误传递 - 股票简称", "错误传递", "positive")
def test_error_abbreviation():
    agent = HybridAgentModular()
    result = agent.query("茅台的股价")
    return {"success": not result.get("success", True) and "error" in result}

@runner.test_case("错误传递 - 无效日期", "错误传递", "positive")
def test_error_invalid_date():
    agent = HybridAgentModular()
    result = agent.query("贵州茅台2099年的股价")
    return {"success": not result.get("success", True) and "error" in result}

# 负向测试（这里的负向是指错误传递失败的情况）
@runner.test_case("错误传递失败 - 隐藏错误", "错误传递", "negative")
def test_error_hidden():
    agent = HybridAgentModular()
    # 正常查询不应该有错误
    result = agent.query("贵州茅台的股价")
    return {"success": result.get("success", False), "error": "不应该有错误"}

@runner.test_case("错误传递失败 - 错误格式", "错误传递", "negative")
def test_error_format():
    agent = HybridAgentModular()
    # 测试是否正确格式化错误
    result = agent.query("")
    if not result.get("success", True):
        return {"success": True, "error": result.get("error", "")}
    return {"success": False, "error": "应该返回错误"}

@runner.test_case("错误传递失败 - 通用错误", "错误传递", "negative")
def test_error_generic():
    agent = HybridAgentModular()
    # 测试是否返回具体错误而非通用错误
    result = agent.query("123456")
    if not result.get("success", True) and "error" in result:
        # 检查是否有具体错误信息
        error_msg = result.get("error", "")
        if "股票" in error_msg or "不存在" in error_msg:
            return {"success": True, "error": error_msg}
    return {"success": False, "error": "错误信息不够具体"}


# ========== 7. 特殊场景处理功能测试 ==========

# 正向测试
@runner.test_case("特殊场景 - 长查询", "特殊场景处理", "positive")
def test_special_long_query():
    agent = HybridAgentModular()
    query = "请详细分析贵州茅台的股价走势、财务健康状况、主力资金流向、发展战略以及投资价值"
    return agent.query(query)

@runner.test_case("特殊场景 - 多股票查询", "特殊场景处理", "positive")
def test_special_multi_stock():
    agent = HybridAgentModular()
    return agent.query("查询贵州茅台、五粮液、泸州老窖的股价")

@runner.test_case("特殊场景 - 中英混合", "特殊场景处理", "positive")
def test_special_mixed_language():
    agent = HybridAgentModular()
    return agent.query("分析BYD比亚迪的PE ratio")

@runner.test_case("特殊场景 - 特殊字符", "特殊场景处理", "positive")
def test_special_characters():
    agent = HybridAgentModular()
    return agent.query("ST股票的风险如何？")

@runner.test_case("特殊场景 - 口语化查询", "特殊场景处理", "positive")
def test_special_colloquial():
    agent = HybridAgentModular()
    return agent.query("茅台最近咋样")

# 负向测试
@runner.test_case("特殊场景 - 超长查询", "特殊场景处理", "negative")
def test_special_too_long():
    agent = HybridAgentModular()
    query = "贵州茅台" * 100
    return agent.query(query)

@runner.test_case("特殊场景 - 纯标点", "特殊场景处理", "negative")
def test_special_punctuation():
    agent = HybridAgentModular()
    return agent.query("，。！？")

@runner.test_case("特殊场景 - SQL注入", "特殊场景处理", "negative")
def test_special_sql_injection():
    agent = HybridAgentModular()
    return agent.query("'; DROP TABLE stocks; --")


# ========== 8. 并行查询功能测试 ==========

# 正向测试
@runner.test_case("并行查询 - SQL+RAG", "并行查询", "positive")
def test_parallel_sql_rag():
    agent = HybridAgentModular()
    return agent.query("贵州茅台的最新股价和发展战略")

@runner.test_case("并行查询 - SQL+Financial", "并行查询", "positive")
def test_parallel_sql_financial():
    agent = HybridAgentModular()
    return agent.query("万科A的市值和财务健康度")

@runner.test_case("并行查询 - RAG+Financial", "并行查询", "positive")
def test_parallel_rag_financial():
    agent = HybridAgentModular()
    return agent.query("分析宁德时代的技术优势和财务状况")

@runner.test_case("并行查询 - 三种类型", "并行查询", "positive")
def test_parallel_three_types():
    agent = HybridAgentModular()
    return agent.query("比亚迪的股价、主要业务和财务健康度")

@runner.test_case("并行查询 - 全面分析", "并行查询", "positive")
def test_parallel_comprehensive():
    agent = HybridAgentModular()
    return agent.query("全面分析贵州茅台的投资价值")

# 负向测试
@runner.test_case("并行查询 - 冲突查询", "并行查询", "negative")
def test_parallel_conflict():
    agent = HybridAgentModular()
    return agent.query("贵州茅台的股价和不存在公司的业务")

@runner.test_case("并行查询 - 部分失败", "并行查询", "negative")
def test_parallel_partial_fail():
    agent = HybridAgentModular()
    return agent.query("xyz123的股价和业务分析")

@runner.test_case("并行查询 - 无效组合", "并行查询", "negative")
def test_parallel_invalid_combo():
    agent = HybridAgentModular()
    return agent.query("和以及还有")


def main():
    """运行所有Hybrid Agent测试"""
    print("Hybrid Agent Comprehensive Test Suite")
    print("="*80)
    print(f"Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Test Config: 8 function modules, at least 5 positive and 3 negative tests each")
    print(f"Expected test cases: 64+")
    
    # 1. 智能路由功能测试 (10个测试)
    print("\n\n【1. 智能路由功能测试】")
    test_routing_sql_price()
    test_routing_rag_strategy()
    test_routing_financial()
    test_routing_money_flow()
    test_routing_sql_kline()
    test_routing_rag_report()
    test_routing_financial_dupont()
    test_routing_empty()
    test_routing_invalid()
    test_routing_ambiguous()
    
    # 2. 复合查询功能测试 (9个测试)
    print("\n\n【2. 复合查询功能测试】")
    test_composite_price_business()
    test_composite_finance_strategy()
    test_composite_cap_tech()
    test_composite_performance_risk()
    test_composite_multiple_connectors()
    test_composite_and()
    test_composite_single()
    test_composite_duplicate()
    test_composite_invalid_combo()
    
    # 3. 投资价值分析测试 (9个测试)
    print("\n\n【3. 投资价值分析功能测试】")
    test_investment_basic()
    test_investment_opportunity()
    test_investment_worth()
    test_investment_potential()
    test_investment_comprehensive()
    test_investment_long_term()
    test_investment_vague()
    test_investment_no_stock()
    test_investment_abbreviation()
    
    # 4. 风险评估分析测试 (8个测试)
    print("\n\n【4. 风险评估分析功能测试】")
    test_risk_financial()
    test_risk_status()
    test_risk_operational()
    test_risk_systematic()
    test_risk_volatility()
    test_risk_no_content()
    test_risk_wrong_type()
    test_risk_irrelevant()
    
    # 5. 综合对比分析测试 (8个测试)
    print("\n\n【5. 综合对比分析功能测试】")
    test_comparison_two_stocks()
    test_comparison_all_aspects()
    test_comparison_vs()
    test_comparison_multi_dimension()
    test_comparison_investment()
    test_comparison_single()
    test_comparison_too_many()
    test_comparison_invalid_stocks()
    
    # 6. 错误传递功能测试 (8个测试)
    print("\n\n【6. 错误传递功能测试】")
    test_error_sql()
    test_error_rag()
    test_error_financial()
    test_error_abbreviation()
    test_error_invalid_date()
    test_error_hidden()
    test_error_format()
    test_error_generic()
    
    # 7. 特殊场景处理测试 (8个测试)
    print("\n\n【7. 特殊场景处理功能测试】")
    test_special_long_query()
    test_special_multi_stock()
    test_special_mixed_language()
    test_special_characters()
    test_special_colloquial()
    test_special_too_long()
    test_special_punctuation()
    test_special_sql_injection()
    
    # 8. 并行查询功能测试 (8个测试)
    print("\n\n【8. 并行查询功能测试】")
    test_parallel_sql_rag()
    test_parallel_sql_financial()
    test_parallel_rag_financial()
    test_parallel_three_types()
    test_parallel_comprehensive()
    test_parallel_conflict()
    test_parallel_partial_fail()
    test_parallel_invalid_combo()
    
    # 打印测试摘要
    runner.print_summary()
    
    print(f"\nEnd Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Actual test cases: {runner.results['total']}")


if __name__ == "__main__":
    main()