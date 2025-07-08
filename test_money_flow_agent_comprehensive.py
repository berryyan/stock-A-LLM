#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Money Flow Agent 全面测试套件
基于test-guide-comprehensive.md的完整功能测试
覆盖所有资金流向分析功能，每个功能至少5个正向测试，3个负向测试
"""
import sys
import os
import time
import json
from datetime import datetime
from typing import Dict, List, Any

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.money_flow_agent_modular import MoneyFlowAgentModular


class MoneyFlowAgentTestRunner:
    """Money Flow Agent专项测试运行器"""
    
    def __init__(self):
        self.results = {
            "agent": "MoneyFlowAgentModular",
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
        print("Money Flow Agent 测试摘要")
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
        with open("money_flow_agent_comprehensive_results.json", "w", encoding="utf-8") as f:
            json.dump(self.results, f, ensure_ascii=False, indent=2)
        
        print(f"\n详细测试结果已保存至: money_flow_agent_comprehensive_results.json")


# 创建测试运行器
runner = MoneyFlowAgentTestRunner()


# ========== 1. 个股资金流向分析功能测试 ==========

# 正向测试
@runner.test_case("资金流向分析 - 基础", "个股资金流向分析", "positive")
def test_flow_analysis_basic():
    agent = MoneyFlowAgentModular()
    return agent.query("分析贵州茅台的资金流向")

@runner.test_case("资金流向分析 - 如何表达", "个股资金流向分析", "positive")
def test_flow_analysis_how():
    agent = MoneyFlowAgentModular()
    return agent.query("茅台的资金流向如何")

@runner.test_case("资金流向分析 - 最近30天", "个股资金流向分析", "positive")
def test_flow_analysis_30days():
    agent = MoneyFlowAgentModular()
    return agent.query("分析宁德时代最近30天资金流向")

@runner.test_case("资金流向分析 - 分析关键词", "个股资金流向分析", "positive")
def test_flow_analysis_keyword():
    agent = MoneyFlowAgentModular()
    return agent.query("比亚迪资金流向分析")

@runner.test_case("资金流向分析 - 股票代码", "个股资金流向分析", "positive")
def test_flow_analysis_code():
    agent = MoneyFlowAgentModular()
    return agent.query("分析600519.SH的资金流向")

@runner.test_case("资金流向分析 - 最近5天", "个股资金流向分析", "positive")
def test_flow_analysis_5days():
    agent = MoneyFlowAgentModular()
    return agent.query("分析平安银行最近5天的资金流向")

@runner.test_case("资金流向分析 - 最近10天", "个股资金流向分析", "positive")
def test_flow_analysis_10days():
    agent = MoneyFlowAgentModular()
    return agent.query("万科A最近10天资金流向如何")

# 负向测试
@runner.test_case("资金流向分析 - 缺少分析关键词", "个股资金流向分析", "negative")
def test_flow_analysis_no_keyword():
    agent = MoneyFlowAgentModular()
    # 应该路由到SQL_ONLY
    return agent.query("贵州茅台的资金流向")

@runner.test_case("资金流向分析 - 简称错误", "个股资金流向分析", "negative")
def test_flow_analysis_abbreviation():
    agent = MoneyFlowAgentModular()
    return agent.query("分析茅台的资金流向")

@runner.test_case("资金流向分析 - 空查询", "个股资金流向分析", "negative")
def test_flow_analysis_empty():
    agent = MoneyFlowAgentModular()
    return agent.query("")


# ========== 2. 主力资金分析功能测试 ==========

# 正向测试
@runner.test_case("主力资金查询 - 基础", "主力资金分析", "positive")
def test_main_fund_basic():
    agent = MoneyFlowAgentModular()
    return agent.query("贵州茅台的主力资金")

@runner.test_case("主力资金查询 - 净流入", "主力资金分析", "positive")
def test_main_fund_net_inflow():
    agent = MoneyFlowAgentModular()
    return agent.query("万科A的主力净流入")

@runner.test_case("主力资金分析 - 深度分析", "主力资金分析", "positive")
def test_main_fund_analysis():
    agent = MoneyFlowAgentModular()
    return agent.query("分析宁德时代的主力资金动向")

@runner.test_case("主力资金 - 时间指定", "主力资金分析", "positive")
def test_main_fund_with_time():
    agent = MoneyFlowAgentModular()
    return agent.query("比亚迪昨天的主力资金")

@runner.test_case("主力资金 - 行为模式", "主力资金分析", "positive")
def test_main_fund_behavior():
    agent = MoneyFlowAgentModular()
    return agent.query("分析贵州茅台主力资金的行为模式")

# 负向测试
@runner.test_case("主力资金 - 非标准术语", "主力资金分析", "negative")
def test_main_fund_nonstandard():
    agent = MoneyFlowAgentModular()
    return agent.query("贵州茅台的机构资金")

@runner.test_case("主力资金 - 游资术语", "主力资金分析", "negative")
def test_main_fund_hot_money():
    agent = MoneyFlowAgentModular()
    return agent.query("分析万科A的游资动向")

@runner.test_case("主力资金 - 不存在股票", "主力资金分析", "negative")
def test_main_fund_invalid_stock():
    agent = MoneyFlowAgentModular()
    return agent.query("xyz123的主力资金")


# ========== 3. 超大单分析功能测试 ==========

# 正向测试
@runner.test_case("超大单分析 - 基础", "超大单分析", "positive")
def test_super_large_basic():
    agent = MoneyFlowAgentModular()
    return agent.query("分析贵州茅台的超大单资金")

@runner.test_case("超大单分析 - 行为分析", "超大单分析", "positive")
def test_super_large_behavior():
    agent = MoneyFlowAgentModular()
    return agent.query("比亚迪超大单资金分析")

@runner.test_case("超大单分析 - 机构行为", "超大单分析", "positive")
def test_super_large_institutional():
    agent = MoneyFlowAgentModular()
    return agent.query("分析宁德时代的超大单行为")

@runner.test_case("超大单分析 - 买卖分析", "超大单分析", "positive")
def test_super_large_trade():
    agent = MoneyFlowAgentModular()
    return agent.query("分析万科A超大单买卖情况")

@runner.test_case("超大单分析 - 占比分析", "超大单分析", "positive")
def test_super_large_ratio():
    agent = MoneyFlowAgentModular()
    return agent.query("分析平安银行超大单占比")

# 负向测试
@runner.test_case("超大单分析 - 混淆概念", "超大单分析", "negative")
def test_super_large_confused():
    agent = MoneyFlowAgentModular()
    return agent.query("分析比亚迪机构资金动向")

@runner.test_case("超大单分析 - 不支持类型", "超大单分析", "negative")
def test_super_large_unsupported():
    agent = MoneyFlowAgentModular()
    return agent.query("茅台的游资分析")

@runner.test_case("超大单分析 - 简称错误", "超大单分析", "negative")
def test_super_large_abbreviation():
    agent = MoneyFlowAgentModular()
    return agent.query("分析茅台的超大单")


# ========== 4. 资金流向对比功能测试 ==========

# 正向测试
@runner.test_case("资金对比 - 两股对比", "资金流向对比", "positive")
def test_flow_comparison_two():
    agent = MoneyFlowAgentModular()
    return agent.query("对比茅台和五粮液的资金流向")

@runner.test_case("资金对比 - 比较关键词", "资金流向对比", "positive")
def test_flow_comparison_compare():
    agent = MoneyFlowAgentModular()
    return agent.query("比较平安银行和招商银行的资金")

@runner.test_case("资金对比 - vs格式", "资金流向对比", "positive")
def test_flow_comparison_vs():
    agent = MoneyFlowAgentModular()
    return agent.query("宁德时代vs比亚迪资金流向")

@runner.test_case("资金对比 - 分析对比", "资金流向对比", "positive")
def test_flow_comparison_analysis():
    agent = MoneyFlowAgentModular()
    return agent.query("分析对比贵州茅台和万科A的资金流向")

@runner.test_case("资金对比 - 主力偏好", "资金流向对比", "positive")
def test_flow_comparison_preference():
    agent = MoneyFlowAgentModular()
    return agent.query("对比茅台和五粮液的主力资金偏好")

# 负向测试
@runner.test_case("资金对比 - 单个股票", "资金流向对比", "negative")
def test_flow_comparison_single():
    agent = MoneyFlowAgentModular()
    return agent.query("对比贵州茅台的资金流向")

@runner.test_case("资金对比 - 过多股票", "资金流向对比", "negative")
def test_flow_comparison_too_many():
    agent = MoneyFlowAgentModular()
    return agent.query("对比茅台、五粮液、泸州老窖、洋河股份的资金")

@runner.test_case("资金对比 - 无效股票", "资金流向对比", "negative")
def test_flow_comparison_invalid():
    agent = MoneyFlowAgentModular()
    return agent.query("对比ABC和XYZ的资金流向")


# ========== 5. 板块资金分析功能测试 ==========

# 正向测试
@runner.test_case("板块资金 - 银行板块", "板块资金分析", "positive")
def test_sector_fund_bank():
    agent = MoneyFlowAgentModular()
    return agent.query("银行板块的主力资金")

@runner.test_case("板块资金 - 新能源板块", "板块资金分析", "positive")
def test_sector_fund_new_energy():
    agent = MoneyFlowAgentModular()
    return agent.query("新能源板块的资金流向")

@runner.test_case("板块资金分析 - 白酒板块", "板块资金分析", "positive")
def test_sector_fund_liquor():
    agent = MoneyFlowAgentModular()
    return agent.query("分析白酒板块的主力资金")

@runner.test_case("板块资金 - 证券板块", "板块资金分析", "positive")
def test_sector_fund_securities():
    agent = MoneyFlowAgentModular()
    return agent.query("证券板块主力净流入")

@runner.test_case("板块资金 - 房地产板块", "板块资金分析", "positive")
def test_sector_fund_real_estate():
    agent = MoneyFlowAgentModular()
    return agent.query("房地产板块的资金动向")

# 负向测试
@runner.test_case("板块资金 - 缺少板块后缀", "板块资金分析", "negative")
def test_sector_fund_no_suffix():
    agent = MoneyFlowAgentModular()
    return agent.query("银行的主力资金")

@runner.test_case("板块资金 - 不存在板块", "板块资金分析", "negative")
def test_sector_fund_invalid():
    agent = MoneyFlowAgentModular()
    return agent.query("火箭板块的资金流向")

@runner.test_case("板块资金 - 模糊板块", "板块资金分析", "negative")
def test_sector_fund_vague():
    agent = MoneyFlowAgentModular()
    return agent.query("板块资金")


# ========== 6. 资金级别分析功能测试 ==========

# 正向测试
@runner.test_case("大单资金分析", "资金级别分析", "positive")
def test_level_large_order():
    agent = MoneyFlowAgentModular()
    return agent.query("分析贵州茅台的大单资金")

@runner.test_case("中单资金分析", "资金级别分析", "positive")
def test_level_medium_order():
    agent = MoneyFlowAgentModular()
    return agent.query("万科A的中单资金流向")

@runner.test_case("小单资金分析", "资金级别分析", "positive")
def test_level_small_order():
    agent = MoneyFlowAgentModular()
    return agent.query("分析宁德时代的小单资金")

@runner.test_case("四级资金分布", "资金级别分析", "positive")
def test_level_four_tier():
    agent = MoneyFlowAgentModular()
    return agent.query("分析比亚迪的四级资金分布")

@runner.test_case("资金结构分析", "资金级别分析", "positive")
def test_level_structure():
    agent = MoneyFlowAgentModular()
    return agent.query("分析平安银行的资金结构")

# 负向测试
@runner.test_case("资金级别 - 错误级别", "资金级别分析", "negative")
def test_level_wrong_tier():
    agent = MoneyFlowAgentModular()
    return agent.query("分析贵州茅台的特大单资金")

@runner.test_case("资金级别 - 混淆术语", "资金级别分析", "negative")
def test_level_confused_term():
    agent = MoneyFlowAgentModular()
    return agent.query("万科A的散户资金")

@runner.test_case("资金级别 - 无效表达", "资金级别分析", "negative")
def test_level_invalid_expression():
    agent = MoneyFlowAgentModular()
    return agent.query("大中小资金")


# ========== 7. 时间维度分析功能测试 ==========

# 正向测试
@runner.test_case("时间维度 - 今天", "时间维度分析", "positive")
def test_time_today():
    agent = MoneyFlowAgentModular()
    return agent.query("分析贵州茅台今天的资金流向")

@runner.test_case("时间维度 - 最近60天", "时间维度分析", "positive")
def test_time_60days():
    agent = MoneyFlowAgentModular()
    return agent.query("分析万科A最近60天的资金流向")

@runner.test_case("时间维度 - 昨天", "时间维度分析", "positive")
def test_time_yesterday():
    agent = MoneyFlowAgentModular()
    return agent.query("宁德时代昨天的主力资金如何")

@runner.test_case("时间维度 - 本周", "时间维度分析", "positive")
def test_time_this_week():
    agent = MoneyFlowAgentModular()
    return agent.query("分析比亚迪本周的资金流向")

@runner.test_case("时间维度 - 连续流入", "时间维度分析", "positive")
def test_time_continuous():
    agent = MoneyFlowAgentModular()
    return agent.query("分析贵州茅台连续净流入情况")

# 负向测试
@runner.test_case("时间维度 - 未来时间", "时间维度分析", "negative")
def test_time_future():
    agent = MoneyFlowAgentModular()
    return agent.query("分析贵州茅台明天的资金流向")

@runner.test_case("时间维度 - 过长时间", "时间维度分析", "negative")
def test_time_too_long():
    agent = MoneyFlowAgentModular()
    return agent.query("分析万科A最近365天的资金流向")

@runner.test_case("时间维度 - 无效时间", "时间维度分析", "negative")
def test_time_invalid():
    agent = MoneyFlowAgentModular()
    return agent.query("分析宁德时代上个世纪的资金")


# ========== 8. 资金行为模式分析功能测试 ==========

# 正向测试
@runner.test_case("行为模式 - 建仓", "资金行为模式分析", "positive")
def test_behavior_accumulation():
    agent = MoneyFlowAgentModular()
    return agent.query("分析贵州茅台是否有主力建仓")

@runner.test_case("行为模式 - 减仓", "资金行为模式分析", "positive")
def test_behavior_distribution():
    agent = MoneyFlowAgentModular()
    return agent.query("分析万科A的主力减仓行为")

@runner.test_case("行为模式 - 洗盘", "资金行为模式分析", "positive")
def test_behavior_shakeout():
    agent = MoneyFlowAgentModular()
    return agent.query("分析宁德时代是否在洗盘")

@runner.test_case("行为模式 - 吸筹", "资金行为模式分析", "positive")
def test_behavior_collection():
    agent = MoneyFlowAgentModular()
    return agent.query("分析比亚迪的主力吸筹情况")

@runner.test_case("行为模式 - 综合分析", "资金行为模式分析", "positive")
def test_behavior_comprehensive():
    agent = MoneyFlowAgentModular()
    return agent.query("分析平安银行的资金行为模式")

# 负向测试
@runner.test_case("行为模式 - 空泛查询", "资金行为模式分析", "negative")
def test_behavior_vague():
    agent = MoneyFlowAgentModular()
    return agent.query("建仓")

@runner.test_case("行为模式 - 错误术语", "资金行为模式分析", "negative")
def test_behavior_wrong_term():
    agent = MoneyFlowAgentModular()
    return agent.query("分析贵州茅台的炒作行为")

@runner.test_case("行为模式 - 无关查询", "资金行为模式分析", "negative")
def test_behavior_irrelevant():
    agent = MoneyFlowAgentModular()
    return agent.query("分析茅台的生产行为")


def main():
    """运行所有Money Flow Agent测试"""
    print("Money Flow Agent Comprehensive Test Suite")
    print("="*80)
    print(f"Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Test Config: 8 function modules, at least 5 positive and 3 negative tests each")
    print(f"Expected test cases: 64+")
    
    # 1. 个股资金流向分析测试 (10个测试)
    print("\n\n【1. 个股资金流向分析功能测试】")
    test_flow_analysis_basic()
    test_flow_analysis_how()
    test_flow_analysis_30days()
    test_flow_analysis_keyword()
    test_flow_analysis_code()
    test_flow_analysis_5days()
    test_flow_analysis_10days()
    test_flow_analysis_no_keyword()
    test_flow_analysis_abbreviation()
    test_flow_analysis_empty()
    
    # 2. 主力资金分析测试 (8个测试)
    print("\n\n【2. 主力资金分析功能测试】")
    test_main_fund_basic()
    test_main_fund_net_inflow()
    test_main_fund_analysis()
    test_main_fund_with_time()
    test_main_fund_behavior()
    test_main_fund_nonstandard()
    test_main_fund_hot_money()
    test_main_fund_invalid_stock()
    
    # 3. 超大单分析测试 (8个测试)
    print("\n\n【3. 超大单分析功能测试】")
    test_super_large_basic()
    test_super_large_behavior()
    test_super_large_institutional()
    test_super_large_trade()
    test_super_large_ratio()
    test_super_large_confused()
    test_super_large_unsupported()
    test_super_large_abbreviation()
    
    # 4. 资金流向对比测试 (8个测试)
    print("\n\n【4. 资金流向对比功能测试】")
    test_flow_comparison_two()
    test_flow_comparison_compare()
    test_flow_comparison_vs()
    test_flow_comparison_analysis()
    test_flow_comparison_preference()
    test_flow_comparison_single()
    test_flow_comparison_too_many()
    test_flow_comparison_invalid()
    
    # 5. 板块资金分析测试 (8个测试)
    print("\n\n【5. 板块资金分析功能测试】")
    test_sector_fund_bank()
    test_sector_fund_new_energy()
    test_sector_fund_liquor()
    test_sector_fund_securities()
    test_sector_fund_real_estate()
    test_sector_fund_no_suffix()
    test_sector_fund_invalid()
    test_sector_fund_vague()
    
    # 6. 资金级别分析测试 (8个测试)
    print("\n\n【6. 资金级别分析功能测试】")
    test_level_large_order()
    test_level_medium_order()
    test_level_small_order()
    test_level_four_tier()
    test_level_structure()
    test_level_wrong_tier()
    test_level_confused_term()
    test_level_invalid_expression()
    
    # 7. 时间维度分析测试 (8个测试)
    print("\n\n【7. 时间维度分析功能测试】")
    test_time_today()
    test_time_60days()
    test_time_yesterday()
    test_time_this_week()
    test_time_continuous()
    test_time_future()
    test_time_too_long()
    test_time_invalid()
    
    # 8. 资金行为模式分析测试 (8个测试)
    print("\n\n【8. 资金行为模式分析功能测试】")
    test_behavior_accumulation()
    test_behavior_distribution()
    test_behavior_shakeout()
    test_behavior_collection()
    test_behavior_comprehensive()
    test_behavior_vague()
    test_behavior_wrong_term()
    test_behavior_irrelevant()
    
    # 打印测试摘要
    runner.print_summary()
    
    print(f"\nEnd Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Actual test cases: {runner.results['total']}")


if __name__ == "__main__":
    main()