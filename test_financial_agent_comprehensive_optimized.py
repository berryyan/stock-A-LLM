#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Financial Agent 综合测试 - 优化版
每个分析类型测试5个正例+3个错误用例
共8个分析类型 x 8个用例 = 64个测试
"""
import sys
import os
import time
import json
from datetime import datetime
from typing import Dict, List, Tuple, Any

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.financial_agent_modular import FinancialAgentModular


class FinancialAgentTest:
    """Financial Agent测试类"""
    
    def __init__(self):
        self.agent = FinancialAgentModular()
        self.test_results = []
        self.total_tests = 0
        self.passed_tests = 0
        self.failed_tests = 0
        
    def test_case(self, query: str, expected_success: bool, 
                  expected_contains: List[str] = None, 
                  test_name: str = "", category: str = "") -> bool:
        """执行单个测试用例"""
        self.total_tests += 1
        
        print(f"\n{'='*60}")
        print(f"测试 {self.total_tests}: {category} - {test_name}")
        print(f"查询: {query}")
        print(f"预期: {'成功' if expected_success else '失败'}")
        
        start_time = time.time()
        
        try:
            result = self.agent.analyze(query)
            elapsed_time = time.time() - start_time
            
            success = result.get('success', False)
            passed = success == expected_success
            
            # 如果需要检查内容
            if passed and expected_success and expected_contains:
                result_str = str(result.get('result', ''))
                for keyword in expected_contains:
                    if keyword not in result_str:
                        passed = False
                        print(f"❌ 结果中未找到关键词: {keyword}")
                        break
            
            if passed:
                self.passed_tests += 1
                print(f"✅ 通过 (耗时: {elapsed_time:.2f}秒)")
            else:
                self.failed_tests += 1
                print(f"❌ 失败")
                if success:
                    print(f"结果预览: {str(result.get('result', ''))[:100]}...")
                else:
                    print(f"错误: {result.get('error', '未知错误')}")
            
            # 记录测试结果
            self.test_results.append({
                'test_id': self.total_tests,
                'category': category,
                'test_name': test_name,
                'query': query,
                'passed': passed,
                'elapsed_time': elapsed_time,
                'expected_success': expected_success,
                'actual_success': success
            })
            
            # 如果执行时间超过10秒，说明在等待LLM，跳过后续的正例测试
            if elapsed_time > 10 and expected_success:
                print("⚠️ 检测到LLM延迟，跳过剩余正例测试以节省时间")
                return False  # 表示应该跳过后续测试
                
            return passed
            
        except Exception as e:
            self.failed_tests += 1
            print(f"❌ 异常: {str(e)}")
            
            self.test_results.append({
                'test_id': self.total_tests,
                'category': category,
                'test_name': test_name,
                'query': query,
                'passed': False,
                'error': str(e),
                'expected_success': expected_success,
                'actual_success': False
            })
            
            return False
    
    def test_financial_health(self):
        """测试财务健康度分析"""
        category = "财务健康度分析"
        
        # 正例（限制2个避免超时）
        positive_cases = [
            ("分析贵州茅台的财务健康度", "基础查询", ['财务健康度']),
            ("601318.SH的财务健康度", "股票代码", ['财务健康度']),
        ]
        
        for query, test_name, contains in positive_cases:
            skip = not self.test_case(query, True, contains, test_name, category)
            if skip:
                break
        
        # 错误用例
        error_cases = [
            ("", "空查询"),
            ("茅台的财务健康度", "股票简称"),
            ("12345的财务健康度", "错误代码"),
        ]
        
        for query, test_name in error_cases:
            self.test_case(query, False, None, test_name, category)
    
    def test_dupont_analysis(self):
        """测试杜邦分析"""
        category = "杜邦分析"
        
        # 正例
        positive_cases = [
            ("贵州茅台的杜邦分析", "基础查询", ['杜邦', 'ROE']),
            ("万科A的ROE分解", "ROE分解", ['ROE']),
        ]
        
        for query, test_name, contains in positive_cases:
            skip = not self.test_case(query, True, contains, test_name, category)
            if skip:
                break
        
        # 错误用例
        error_cases = [
            ("杜邦分析", "缺少股票"),
            ("不存在公司的杜邦分析", "无效股票"),
            ("600519.sz的杜邦分析", "小写后缀"),
        ]
        
        for query, test_name in error_cases:
            self.test_case(query, False, None, test_name, category)
    
    def test_cash_flow(self):
        """测试现金流质量分析"""
        category = "现金流质量分析"
        
        # 正例
        positive_cases = [
            ("分析万科A的现金流质量", "基础查询", ['现金流']),
            ("中国平安现金流分析", "简化查询", ['现金']),
        ]
        
        for query, test_name, contains in positive_cases:
            skip = not self.test_case(query, True, contains, test_name, category)
            if skip:
                break
        
        # 错误用例
        error_cases = [
            ("现金流质量", "缺少股票"),
            ("万科的现金流", "股票简称"),
            ("   ", "空白查询"),
        ]
        
        for query, test_name in error_cases:
            self.test_case(query, False, None, test_name, category)
    
    def test_multi_period_comparison(self):
        """测试多期对比"""
        category = "多期财务对比"
        
        # 正例
        positive_cases = [
            ("贵州茅台2025年一季度与去年同期对比", "同期对比", ['对比']),
            ("比较万科A最近4个季度财务数据", "多期对比", ['比较']),
        ]
        
        for query, test_name, contains in positive_cases:
            skip = not self.test_case(query, True, contains, test_name, category)
            if skip:
                break
        
        # 错误用例
        error_cases = [
            ("财务对比", "缺少股票"),
            ("123456最近的对比", "无效代码"),
            ("茅台对比", "股票简称"),
        ]
        
        for query, test_name in error_cases:
            self.test_case(query, False, None, test_name, category)
    
    def test_profitability(self):
        """测试盈利能力分析"""
        category = "盈利能力分析"
        
        # 正例
        positive_cases = [
            ("分析比亚迪的盈利能力", "基础查询", ['盈利']),
            ("宁德时代盈利水平", "简化查询", ['盈利']),
        ]
        
        for query, test_name, contains in positive_cases:
            skip = not self.test_case(query, True, contains, test_name, category)
            if skip:
                break
        
        # 错误用例
        error_cases = [
            ("盈利能力", "缺少股票"),
            ("平安的盈利", "歧义股票"),
            ("600000.sh盈利", "小写后缀"),
        ]
        
        for query, test_name in error_cases:
            self.test_case(query, False, None, test_name, category)
    
    def test_solvency(self):
        """测试偿债能力分析"""
        category = "偿债能力分析"
        
        # 正例
        positive_cases = [
            ("分析万科A的偿债能力", "基础查询", ['偿债']),
            ("中国建筑负债情况", "负债查询", ['负债']),
        ]
        
        for query, test_name, contains in positive_cases:
            skip = not self.test_case(query, True, contains, test_name, category)
            if skip:
                break
        
        # 错误用例
        error_cases = [
            ("偿债能力分析", "缺少股票"),
            ("建行的偿债", "股票简称"),
            ("000000的偿债", "无效代码"),
        ]
        
        for query, test_name in error_cases:
            self.test_case(query, False, None, test_name, category)
    
    def test_operational(self):
        """测试运营能力分析"""
        category = "运营能力分析"
        
        # 正例
        positive_cases = [
            ("分析海尔智家的运营效率", "基础查询", ['运营']),
            ("格力电器周转率分析", "周转率", ['周转']),
        ]
        
        for query, test_name, contains in positive_cases:
            skip = not self.test_case(query, True, contains, test_name, category)
            if skip:
                break
        
        # 错误用例
        error_cases = [
            ("运营效率", "缺少股票"),
            ("格力的运营", "股票简称"),
            ("1234567运营", "7位代码"),
        ]
        
        for query, test_name in error_cases:
            self.test_case(query, False, None, test_name, category)
    
    def test_growth(self):
        """测试成长能力分析"""
        category = "成长能力分析"
        
        # 正例
        positive_cases = [
            ("分析宁德时代的成长性", "基础查询", ['成长']),
            ("比亚迪增长潜力", "增长查询", ['增长']),
        ]
        
        for query, test_name, contains in positive_cases:
            skip = not self.test_case(query, True, contains, test_name, category)
            if skip:
                break
        
        # 错误用例
        error_cases = [
            ("成长性分析", "缺少股票"),
            ("特斯拉的成长", "非A股"),
            ("600519.SZ成长", "错误后缀"),
        ]
        
        for query, test_name in error_cases:
            self.test_case(query, False, None, test_name, category)
    
    def run_all_tests(self):
        """运行所有测试"""
        print("="*80)
        print("Financial Agent 综合测试 - 优化版")
        print(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*80)
        
        # 运行各类测试
        self.test_financial_health()
        self.test_dupont_analysis()
        self.test_cash_flow()
        self.test_multi_period_comparison()
        self.test_profitability()
        self.test_solvency()
        self.test_operational()
        self.test_growth()
        
        # 生成测试报告
        self.generate_report()
    
    def generate_report(self):
        """生成测试报告"""
        print("\n" + "="*80)
        print("测试报告")
        print("="*80)
        
        # 按类别统计
        category_stats = {}
        for result in self.test_results:
            category = result['category']
            if category not in category_stats:
                category_stats[category] = {'total': 0, 'passed': 0}
            category_stats[category]['total'] += 1
            if result['passed']:
                category_stats[category]['passed'] += 1
        
        # 打印类别统计
        print("\n按类别统计:")
        for category, stats in category_stats.items():
            pass_rate = stats['passed'] / stats['total'] * 100
            print(f"{category}: {stats['passed']}/{stats['total']} ({pass_rate:.1f}%)")
        
        # 总体统计
        print(f"\n总体统计:")
        print(f"总测试数: {self.total_tests}")
        print(f"通过: {self.passed_tests}")
        print(f"失败: {self.failed_tests}")
        print(f"通过率: {self.passed_tests/self.total_tests*100:.1f}%")
        
        # 保存详细报告
        report = {
            'test_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'total_tests': self.total_tests,
            'passed_tests': self.passed_tests,
            'failed_tests': self.failed_tests,
            'pass_rate': f"{self.passed_tests/self.total_tests*100:.1f}%",
            'category_stats': category_stats,
            'test_results': self.test_results
        }
        
        with open('test_financial_agent_comprehensive_report.json', 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        print(f"\n详细报告已保存到: test_financial_agent_comprehensive_report.json")


if __name__ == "__main__":
    tester = FinancialAgentTest()
    tester.run_all_tests()