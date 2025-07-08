#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Financial Agent 全面测试套件
基于test-guide-comprehensive.md的完整功能测试
覆盖所有财务分析功能，每个功能至少5个正向测试，3个负向测试
"""
import sys
import os
import time
import json
from datetime import datetime
from typing import Dict, List, Any

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.financial_agent_modular import FinancialAgentModular


class FinancialAgentTestRunner:
    """Financial Agent专项测试运行器"""
    
    def __init__(self):
        self.results = {
            "agent": "FinancialAgentModular",
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
        print("Financial Agent 测试摘要")
        print('='*80)
        print(f"总测试数: {self.results['total']}")
        print(f"通过: {self.results['passed']} ({self.results['passed']/self.results['total']*100:.1f}%)")
        print(f"失败: {self.results['failed']} ({self.results['failed']/self.results['total']*100:.1f}%)")
        print(f"总耗时: {total_time:.2f}秒")
        
        print("\n各功能测试情况:")
        print("-"*80)
        print(f"{'功能':<30} {'总数':<8} {'通过':<8} {'失败':<8} {'正向通过':<10} {'负向通过':<10}")
        print("-"*80)
        
        for func_name, stats in self.results["functions"].items():
            print(f"{func_name:<30} {stats['total']:<8} {stats['passed']:<8} {stats['failed']:<8} "
                  f"{stats['positive_passed']:<10} {stats['negative_passed']:<10}")
        
        # 保存详细结果
        with open("financial_agent_comprehensive_results.json", "w", encoding="utf-8") as f:
            json.dump(self.results, f, ensure_ascii=False, indent=2)
        
        print(f"\n详细测试结果已保存到: financial_agent_comprehensive_results.json")


# 创建测试运行器
runner = FinancialAgentTestRunner()


# ========== 1. 财务健康度分析功能测试 ==========

# 正向测试
@runner.test_case("财务健康度 - 公司全称", "财务健康度分析", "positive")
def test_health_company_name():
    agent = FinancialAgentModular()
    return agent.query("分析贵州茅台的财务健康度")

@runner.test_case("财务健康度 - 股票代码", "财务健康度分析", "positive")
def test_health_stock_code():
    agent = FinancialAgentModular()
    return agent.query("分析601318.SH的财务健康度")

@runner.test_case("财务健康度 - 财务状况", "财务健康度分析", "positive")
def test_health_financial_status():
    agent = FinancialAgentModular()
    return agent.query("分析万科A的财务状况")

@runner.test_case("财务健康度 - 6位代码", "财务健康度分析", "positive")
def test_health_six_digit_code():
    agent = FinancialAgentModular()
    return agent.query("分析600519的财务健康度")

@runner.test_case("财务健康度 - 银行股", "财务健康度分析", "positive")
def test_health_bank_stock():
    agent = FinancialAgentModular()
    return agent.query("分析平安银行的财务健康度")

@runner.test_case("财务健康度 - 科技股", "财务健康度分析", "positive")
def test_health_tech_stock():
    agent = FinancialAgentModular()
    return agent.query("分析宁德时代的财务健康度")

@runner.test_case("财务健康度 - 制造业", "财务健康度分析", "positive")
def test_health_manufacturing():
    agent = FinancialAgentModular()
    return agent.query("分析比亚迪的财务健康度")

# 负向测试
@runner.test_case("财务健康度 - 简称错误", "财务健康度分析", "negative")
def test_health_abbreviation():
    agent = FinancialAgentModular()
    return agent.query("茅台的财务健康度")

@runner.test_case("财务健康度 - 5位数字", "财务健康度分析", "negative")
def test_health_five_digits():
    agent = FinancialAgentModular()
    return agent.query("12345的财务健康度")

@runner.test_case("财务健康度 - 空查询", "财务健康度分析", "negative")
def test_health_empty():
    agent = FinancialAgentModular()
    return agent.query("")

@runner.test_case("财务健康度 - 不存在股票", "财务健康度分析", "negative")
def test_health_invalid_stock():
    agent = FinancialAgentModular()
    return agent.query("不存在公司的财务健康度")


# ========== 2. 杜邦分析功能测试 ==========

# 正向测试
@runner.test_case("杜邦分析 - 基础", "杜邦分析", "positive")
def test_dupont_basic():
    agent = FinancialAgentModular()
    return agent.query("贵州茅台的杜邦分析")

@runner.test_case("杜邦分析 - ROE分解", "杜邦分析", "positive")
def test_dupont_roe():
    agent = FinancialAgentModular()
    return agent.query("平安银行ROE分解分析")

@runner.test_case("杜邦分析 - 分析ROE", "杜邦分析", "positive")
def test_dupont_analyze_roe():
    agent = FinancialAgentModular()
    return agent.query("分析万科A的ROE")

@runner.test_case("杜邦分析 - 对...进行", "杜邦分析", "positive")
def test_dupont_conduct():
    agent = FinancialAgentModular()
    return agent.query("对中国平安进行杜邦分析")

@runner.test_case("杜邦分析 - 股票代码", "杜邦分析", "positive")
def test_dupont_by_code():
    agent = FinancialAgentModular()
    return agent.query("600519.SH的杜邦分析")

@runner.test_case("杜邦分析 - 权益乘数", "杜邦分析", "positive")
def test_dupont_equity_multiplier():
    agent = FinancialAgentModular()
    return agent.query("分析宁德时代的权益乘数")

# 负向测试
@runner.test_case("杜邦分析 - 简称错误", "杜邦分析", "negative")
def test_dupont_abbreviation():
    agent = FinancialAgentModular()
    return agent.query("茅台的杜邦分析")

@runner.test_case("杜邦分析 - 无效股票", "杜邦分析", "negative")
def test_dupont_invalid():
    agent = FinancialAgentModular()
    return agent.query("XYZ公司的杜邦分析")

@runner.test_case("杜邦分析 - 错误表达", "杜邦分析", "negative")
def test_dupont_wrong_expression():
    agent = FinancialAgentModular()
    return agent.query("杜邦分析一下")


# ========== 3. 现金流质量分析功能测试 ==========

# 正向测试
@runner.test_case("现金流质量 - 基础", "现金流质量分析", "positive")
def test_cashflow_basic():
    agent = FinancialAgentModular()
    return agent.query("分析贵州茅台的现金流质量")

@runner.test_case("现金流质量 - 状况", "现金流质量分析", "positive")
def test_cashflow_status():
    agent = FinancialAgentModular()
    return agent.query("万科A现金流状况如何")

@runner.test_case("现金流质量 - 评估", "现金流质量分析", "positive")
def test_cashflow_evaluate():
    agent = FinancialAgentModular()
    return agent.query("评估平安银行的现金流")

@runner.test_case("现金流质量 - 现金流分析", "现金流质量分析", "positive")
def test_cashflow_analysis():
    agent = FinancialAgentModular()
    return agent.query("比亚迪的现金流分析")

@runner.test_case("现金流质量 - 稳定性", "现金流质量分析", "positive")
def test_cashflow_stability():
    agent = FinancialAgentModular()
    return agent.query("分析宁德时代现金流的稳定性")

@runner.test_case("现金流质量 - 现金含量", "现金流质量分析", "positive")
def test_cashflow_content():
    agent = FinancialAgentModular()
    return agent.query("贵州茅台的现金含量比率")

# 负向测试
@runner.test_case("现金流质量 - 简称错误", "现金流质量分析", "negative")
def test_cashflow_abbreviation():
    agent = FinancialAgentModular()
    return agent.query("茅台的现金流")

@runner.test_case("现金流质量 - 不完整查询", "现金流质量分析", "negative")
def test_cashflow_incomplete():
    agent = FinancialAgentModular()
    return agent.query("现金流")

@runner.test_case("现金流质量 - 无效公司", "现金流质量分析", "negative")
def test_cashflow_invalid():
    agent = FinancialAgentModular()
    return agent.query("分析ABC公司的现金流")


# ========== 4. 多期财务对比功能测试 ==========

# 正向测试
@runner.test_case("多期对比 - 基础", "多期财务对比", "positive")
def test_comparison_basic():
    agent = FinancialAgentModular()
    return agent.query("分析贵州茅台的多期财务对比")

@runner.test_case("多期对比 - 不同时期", "多期财务对比", "positive")
def test_comparison_periods():
    agent = FinancialAgentModular()
    return agent.query("比较万科A不同时期的财务数据")

@runner.test_case("多期对比 - 财务变化", "多期财务对比", "positive")
def test_comparison_changes():
    agent = FinancialAgentModular()
    return agent.query("600519.SH最近几期的财务变化")

@runner.test_case("多期对比 - 趋势分析", "多期财务对比", "positive")
def test_comparison_trend():
    agent = FinancialAgentModular()
    return agent.query("分析平安银行的财务趋势")

@runner.test_case("多期对比 - 同比环比", "多期财务对比", "positive")
def test_comparison_yoy_qoq():
    agent = FinancialAgentModular()
    return agent.query("宁德时代的同比环比分析")

@runner.test_case("多期对比 - 增长率", "多期财务对比", "positive")
def test_comparison_growth():
    agent = FinancialAgentModular()
    return agent.query("比亚迪各期营收增长率")

@runner.test_case("多期对比 - 波动性", "多期财务对比", "positive")
def test_comparison_volatility():
    agent = FinancialAgentModular()
    return agent.query("分析贵州茅台财务数据的波动性")

# 负向测试
@runner.test_case("多期对比 - 简称错误", "多期财务对比", "negative")
def test_comparison_abbreviation():
    agent = FinancialAgentModular()
    return agent.query("茅台的多期对比")

@runner.test_case("多期对比 - 模糊查询", "多期财务对比", "negative")
def test_comparison_vague():
    agent = FinancialAgentModular()
    return agent.query("对比一下")

@runner.test_case("多期对比 - 无效期间", "多期财务对比", "negative")
def test_comparison_invalid_period():
    agent = FinancialAgentModular()
    return agent.query("贵州茅台2099年的财务对比")


# ========== 5. 盈利能力分析功能测试 ==========

# 正向测试
@runner.test_case("盈利能力 - 综合分析", "盈利能力分析", "positive")
def test_profitability_comprehensive():
    agent = FinancialAgentModular()
    return agent.query("分析贵州茅台的盈利能力")

@runner.test_case("盈利能力 - 毛利率", "盈利能力分析", "positive")
def test_profitability_gross_margin():
    agent = FinancialAgentModular()
    return agent.query("万科A的毛利率分析")

@runner.test_case("盈利能力 - 净利率", "盈利能力分析", "positive")
def test_profitability_net_margin():
    agent = FinancialAgentModular()
    return agent.query("平安银行的净利率情况")

@runner.test_case("盈利能力 - ROA分析", "盈利能力分析", "positive")
def test_profitability_roa():
    agent = FinancialAgentModular()
    return agent.query("分析宁德时代的ROA")

@runner.test_case("盈利能力 - 利润质量", "盈利能力分析", "positive")
def test_profitability_quality():
    agent = FinancialAgentModular()
    return agent.query("评估比亚迪的利润质量")

# 负向测试
@runner.test_case("盈利能力 - 空泛查询", "盈利能力分析", "negative")
def test_profitability_vague():
    agent = FinancialAgentModular()
    return agent.query("盈利能力")

@runner.test_case("盈利能力 - 简称错误", "盈利能力分析", "negative")
def test_profitability_abbreviation():
    agent = FinancialAgentModular()
    return agent.query("茅台盈利怎么样")

@runner.test_case("盈利能力 - 无效指标", "盈利能力分析", "negative")
def test_profitability_invalid_metric():
    agent = FinancialAgentModular()
    return agent.query("贵州茅台的XYZ率")


# ========== 6. 偿债能力分析功能测试 ==========

# 正向测试
@runner.test_case("偿债能力 - 综合分析", "偿债能力分析", "positive")
def test_solvency_comprehensive():
    agent = FinancialAgentModular()
    return agent.query("分析万科A的偿债能力")

@runner.test_case("偿债能力 - 流动比率", "偿债能力分析", "positive")
def test_solvency_current_ratio():
    agent = FinancialAgentModular()
    return agent.query("贵州茅台的流动比率")

@runner.test_case("偿债能力 - 速动比率", "偿债能力分析", "positive")
def test_solvency_quick_ratio():
    agent = FinancialAgentModular()
    return agent.query("平安银行的速动比率分析")

@runner.test_case("偿债能力 - 资产负债率", "偿债能力分析", "positive")
def test_solvency_debt_ratio():
    agent = FinancialAgentModular()
    return agent.query("分析宁德时代的资产负债率")

@runner.test_case("偿债能力 - 利息保障倍数", "偿债能力分析", "positive")
def test_solvency_interest_coverage():
    agent = FinancialAgentModular()
    return agent.query("比亚迪的利息保障倍数")

# 负向测试
@runner.test_case("偿债能力 - 不完整查询", "偿债能力分析", "negative")
def test_solvency_incomplete():
    agent = FinancialAgentModular()
    return agent.query("偿债")

@runner.test_case("偿债能力 - 简称错误", "偿债能力分析", "negative")
def test_solvency_abbreviation():
    agent = FinancialAgentModular()
    return agent.query("茅台的负债情况")

@runner.test_case("偿债能力 - 混淆概念", "偿债能力分析", "negative")
def test_solvency_confused():
    agent = FinancialAgentModular()
    return agent.query("贵州茅台的还钱能力")


# ========== 7. 运营能力分析功能测试 ==========

# 正向测试
@runner.test_case("运营能力 - 综合分析", "运营能力分析", "positive")
def test_operational_comprehensive():
    agent = FinancialAgentModular()
    return agent.query("分析贵州茅台的运营能力")

@runner.test_case("运营能力 - 存货周转率", "运营能力分析", "positive")
def test_operational_inventory_turnover():
    agent = FinancialAgentModular()
    return agent.query("万科A的存货周转率")

@runner.test_case("运营能力 - 应收账款周转", "运营能力分析", "positive")
def test_operational_receivable_turnover():
    agent = FinancialAgentModular()
    return agent.query("分析平安银行的应收账款周转率")

@runner.test_case("运营能力 - 总资产周转", "运营能力分析", "positive")
def test_operational_asset_turnover():
    agent = FinancialAgentModular()
    return agent.query("宁德时代的总资产周转率")

@runner.test_case("运营能力 - 营运资本", "运营能力分析", "positive")
def test_operational_working_capital():
    agent = FinancialAgentModular()
    return agent.query("分析比亚迪的营运资本管理")

# 负向测试
@runner.test_case("运营能力 - 空查询", "运营能力分析", "negative")
def test_operational_empty():
    agent = FinancialAgentModular()
    return agent.query("运营")

@runner.test_case("运营能力 - 简称错误", "运营能力分析", "negative")
def test_operational_abbreviation():
    agent = FinancialAgentModular()
    return agent.query("茅台运营效率")

@runner.test_case("运营能力 - 无效指标", "运营能力分析", "negative")
def test_operational_invalid_metric():
    agent = FinancialAgentModular()
    return agent.query("贵州茅台的运转速度")


# ========== 8. 成长能力分析功能测试 ==========

# 正向测试
@runner.test_case("成长能力 - 综合分析", "成长能力分析", "positive")
def test_growth_comprehensive():
    agent = FinancialAgentModular()
    return agent.query("分析宁德时代的成长能力")

@runner.test_case("成长能力 - 营收增长", "成长能力分析", "positive")
def test_growth_revenue():
    agent = FinancialAgentModular()
    return agent.query("贵州茅台的营收增长率")

@runner.test_case("成长能力 - 利润增长", "成长能力分析", "positive")
def test_growth_profit():
    agent = FinancialAgentModular()
    return agent.query("分析比亚迪的利润增长情况")

@runner.test_case("成长能力 - 资产增长", "成长能力分析", "positive")
def test_growth_asset():
    agent = FinancialAgentModular()
    return agent.query("万科A的资产增长率")

@runner.test_case("成长能力 - 复合增长率", "成长能力分析", "positive")
def test_growth_cagr():
    agent = FinancialAgentModular()
    return agent.query("平安银行的年复合增长率")

# 负向测试
@runner.test_case("成长能力 - 模糊查询", "成长能力分析", "negative")
def test_growth_vague():
    agent = FinancialAgentModular()
    return agent.query("成长性")

@runner.test_case("成长能力 - 简称错误", "成长能力分析", "negative")
def test_growth_abbreviation():
    agent = FinancialAgentModular()
    return agent.query("茅台增长如何")

@runner.test_case("成长能力 - 错误时间", "成长能力分析", "negative")
def test_growth_wrong_time():
    agent = FinancialAgentModular()
    return agent.query("贵州茅台明年的增长率")


def main():
    """运行所有Financial Agent测试"""
    print("Financial Agent 全面测试套件")
    print("="*80)
    print(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"测试配置: 8个功能模块，每个至少5个正向测试，3个负向测试")
    print(f"预计测试用例数: 64+")
    
    # 1. 财务健康度分析测试 (11个测试)
    print("\n\n【1. 财务健康度分析功能测试】")
    test_health_company_name()
    test_health_stock_code()
    test_health_financial_status()
    test_health_six_digit_code()
    test_health_bank_stock()
    test_health_tech_stock()
    test_health_manufacturing()
    test_health_abbreviation()
    test_health_five_digits()
    test_health_empty()
    test_health_invalid_stock()
    
    # 2. 杜邦分析测试 (9个测试)
    print("\n\n【2. 杜邦分析功能测试】")
    test_dupont_basic()
    test_dupont_roe()
    test_dupont_analyze_roe()
    test_dupont_conduct()
    test_dupont_by_code()
    test_dupont_equity_multiplier()
    test_dupont_abbreviation()
    test_dupont_invalid()
    test_dupont_wrong_expression()
    
    # 3. 现金流质量分析测试 (9个测试)
    print("\n\n【3. 现金流质量分析功能测试】")
    test_cashflow_basic()
    test_cashflow_status()
    test_cashflow_evaluate()
    test_cashflow_analysis()
    test_cashflow_stability()
    test_cashflow_content()
    test_cashflow_abbreviation()
    test_cashflow_incomplete()
    test_cashflow_invalid()
    
    # 4. 多期财务对比测试 (10个测试)
    print("\n\n【4. 多期财务对比功能测试】")
    test_comparison_basic()
    test_comparison_periods()
    test_comparison_changes()
    test_comparison_trend()
    test_comparison_yoy_qoq()
    test_comparison_growth()
    test_comparison_volatility()
    test_comparison_abbreviation()
    test_comparison_vague()
    test_comparison_invalid_period()
    
    # 5. 盈利能力分析测试 (8个测试)
    print("\n\n【5. 盈利能力分析功能测试】")
    test_profitability_comprehensive()
    test_profitability_gross_margin()
    test_profitability_net_margin()
    test_profitability_roa()
    test_profitability_quality()
    test_profitability_vague()
    test_profitability_abbreviation()
    test_profitability_invalid_metric()
    
    # 6. 偿债能力分析测试 (8个测试)
    print("\n\n【6. 偿债能力分析功能测试】")
    test_solvency_comprehensive()
    test_solvency_current_ratio()
    test_solvency_quick_ratio()
    test_solvency_debt_ratio()
    test_solvency_interest_coverage()
    test_solvency_incomplete()
    test_solvency_abbreviation()
    test_solvency_confused()
    
    # 7. 运营能力分析测试 (8个测试)
    print("\n\n【7. 运营能力分析功能测试】")
    test_operational_comprehensive()
    test_operational_inventory_turnover()
    test_operational_receivable_turnover()
    test_operational_asset_turnover()
    test_operational_working_capital()
    test_operational_empty()
    test_operational_abbreviation()
    test_operational_invalid_metric()
    
    # 8. 成长能力分析测试 (8个测试)
    print("\n\n【8. 成长能力分析功能测试】")
    test_growth_comprehensive()
    test_growth_revenue()
    test_growth_profit()
    test_growth_asset()
    test_growth_cagr()
    test_growth_vague()
    test_growth_abbreviation()
    test_growth_wrong_time()
    
    # 打印测试摘要
    runner.print_summary()
    
    print(f"\n结束时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"实际测试用例数: {runner.results['total']}")


if __name__ == "__main__":
    main()