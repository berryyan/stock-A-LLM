#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Financial Agent 全面测试套件 - 修正版
基于test-guide-comprehensive.md的完整功能测试
覆盖所有财务分析功能，参考SQL Agent的测试标准
"""
import sys
import os
import time
import json
from datetime import datetime
from typing import Dict, List, Tuple, Any

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.financial_agent_modular import FinancialAgentModular


class ComprehensiveTest:
    """综合测试类"""
    
    def __init__(self):
        self.agent = FinancialAgentModular()
        self.test_results = {
            'total': 0,
            'passed': 0,
            'failed': 0,
            'errors': [],
            'details': []
        }
        
    def test_query(self, query: str, expected_success: bool = True, 
                   test_name: str = "", category: str = "") -> Tuple[bool, Dict]:
        """测试单个查询"""
        print(f"\n{'='*60}")
        print(f"测试类别: {category}")
        print(f"测试名称: {test_name}")
        print(f"查询: {query}")
        print(f"预期: {'成功' if expected_success else '失败'}")
        print('-'*60)
        
        start_time = time.time()
        try:
            result = self.agent.analyze(query)
            elapsed_time = time.time() - start_time
            
            # 检查结果
            success = result.get('success', False)
            passed = success == expected_success
            
            # 记录结果
            test_result = {
                'category': category,
                'test_name': test_name,
                'query': query,
                'expected_success': expected_success,
                'actual_success': success,
                'passed': passed,
                'elapsed_time': elapsed_time,
                'error': result.get('error') if not success else None,
                'result_preview': str(result.get('result', ''))[:200] if success else None
            }
            
            self.test_results['total'] += 1
            if passed:
                self.test_results['passed'] += 1
                status = "✅ 通过"
            else:
                self.test_results['failed'] += 1
                status = "❌ 失败"
                self.test_results['errors'].append(test_result)
            
            self.test_results['details'].append(test_result)
            
            # Print results
            print(f"实际: {'成功' if success else '失败'}")
            print(f"状态: {status}")
            print(f"耗时: {elapsed_time:.2f}秒")
            
            if success and result.get('result'):
                print(f"预览: {str(result.get('result'))[:200]}...")
            elif not success:
                print(f"错误: {result.get('error', '未知错误')}")
                
            return passed, result
            
        except Exception as e:
            elapsed_time = time.time() - start_time
            print(f"异常: {str(e)}")
            
            test_result = {
                'category': category,
                'test_name': test_name,
                'query': query,
                'expected_success': expected_success,
                'actual_success': False,
                'passed': False,
                'elapsed_time': elapsed_time,
                'error': f"Exception: {str(e)}",
                'result_preview': None
            }
            
            self.test_results['total'] += 1
            self.test_results['failed'] += 1
            self.test_results['errors'].append(test_result)
            self.test_results['details'].append(test_result)
            
            return False, {'success': False, 'error': str(e)}
    
    def run_all_tests(self):
        """运行所有测试用例"""
        print("="*80)
        print("Financial Agent 模块化版本综合测试")
        print("基于 test-guide-comprehensive.md 和 SQL Agent 测试标准")
        print(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*80)
        
        # 2.1 财务健康度分析
        self.test_financial_health_analysis()
        
        # 2.2 杜邦分析
        self.test_dupont_analysis()
        
        # 2.3 现金流质量分析
        self.test_cashflow_analysis()
        
        # 2.4 多期财务对比
        self.test_multi_period_comparison()
        
        # 2.5 盈利能力分析
        self.test_profitability_analysis()
        
        # 2.6 偿债能力分析
        self.test_solvency_analysis()
        
        # 2.7 运营能力分析
        self.test_operational_analysis()
        
        # 2.8 成长能力分析
        self.test_growth_analysis()
        
        # 生成测试报告
        self.generate_report()
    
    def test_financial_health_analysis(self):
        """2.1 财务健康度分析测试"""
        category = "2.1 财务健康度分析"
        
        # 正常用例
        normal_cases = [
            ("分析贵州茅台的财务健康度", "公司全称"),
            ("分析601318.SH的财务健康度", "股票代码"),
            ("分析万科A的财务状况", "财务状况"),
            ("分析600519的财务健康度", "6位代码"),
            ("分析平安银行的财务健康度", "银行股"),
            ("分析宁德时代的财务健康度", "科技股"),
            ("分析比亚迪的财务健康度", "制造业"),
            ("评估中国平安的财务健康状况", "评估关键词"),
        ]
        
        for query, test_name in normal_cases:
            self.test_query(query, True, test_name, category)
        
        # 边界测试
        boundary_cases = [
            ("贵州茅台财务健康度", "省略分析"),
            ("600519.SH财务状况分析", "代码+分析"),
            ("分析万科的财务健康度", "万科简写"),
            ("中国平安财务健康评分", "评分表达"),
            ("分析贵州茅台财务", "简化表达"),
        ]
        
        for query, test_name in boundary_cases:
            self.test_query(query, True, test_name, f"{category}-边界测试")
        
        # 错误用例
        error_cases = [
            ("茅台的财务健康度", "股票简称错误"),
            ("12345的财务健康度", "5位数字"),
            ("", "空查询"),
            ("不存在公司的财务健康度", "不存在股票"),
            ("分析财务健康度", "无股票指定"),
            ("财务健康度", "不完整查询"),
        ]
        
        for query, test_name in error_cases:
            self.test_query(query, False, test_name, f"{category}-错误用例")
    
    def test_dupont_analysis(self):
        """2.2 杜邦分析测试"""
        category = "2.2 杜邦分析"
        
        # 正常用例
        normal_cases = [
            ("贵州茅台的杜邦分析", "基础查询"),
            ("平安银行ROE分解分析", "ROE分解"),
            ("分析万科A的ROE", "分析ROE"),
            ("对中国平安进行杜邦分析", "对...进行"),
            ("600519.SH的杜邦分析", "股票代码"),
            ("分析宁德时代的权益乘数", "权益乘数"),
            ("比亚迪杜邦分析报告", "分析报告"),
            ("贵州茅台ROE三因素分析", "三因素"),
        ]
        
        for query, test_name in normal_cases:
            self.test_query(query, True, test_name, category)
        
        # 边界测试
        boundary_cases = [
            ("杜邦分析贵州茅台", "倒装语序"),
            ("600519杜邦分析", "6位代码"),
            ("分析茅台集团的ROE", "集团后缀"),
            ("万科ROE分析", "简化表达"),
            ("分析平安银行的净利率和总资产周转率", "部分指标"),
        ]
        
        for query, test_name in boundary_cases:
            self.test_query(query, True, test_name, f"{category}-边界测试")
        
        # 错误用例
        error_cases = [
            ("茅台的杜邦分析", "股票简称错误"),
            ("XYZ公司的杜邦分析", "不存在公司"),
            ("杜邦分析一下", "无股票指定"),
            ("杜邦分析", "不完整查询"),
            ("分析杜邦", "错误表达"),
        ]
        
        for query, test_name in error_cases:
            self.test_query(query, False, test_name, f"{category}-错误用例")
    
    def test_cashflow_analysis(self):
        """2.3 现金流质量分析测试"""
        category = "2.3 现金流质量分析"
        
        # 正常用例
        normal_cases = [
            ("分析贵州茅台的现金流质量", "基础查询"),
            ("万科A现金流状况如何", "状况查询"),
            ("评估平安银行的现金流", "评估"),
            ("比亚迪的现金流分析", "分析"),
            ("分析宁德时代现金流的稳定性", "稳定性"),
            ("贵州茅台的现金含量比率", "含量比率"),
            ("中国平安现金流质量评级", "质量评级"),
            ("分析600519.SH的现金流", "股票代码"),
        ]
        
        for query, test_name in normal_cases:
            self.test_query(query, True, test_name, category)
        
        # 边界测试
        boundary_cases = [
            ("贵州茅台现金流怎么样", "口语化"),
            ("万科现金流分析", "简化名称"),
            ("600519现金流质量", "6位代码"),
            ("分析平安银行经营现金流", "经营现金流"),
            ("比亚迪自由现金流分析", "自由现金流"),
        ]
        
        for query, test_name in boundary_cases:
            self.test_query(query, True, test_name, f"{category}-边界测试")
        
        # 错误用例
        error_cases = [
            ("茅台的现金流", "股票简称错误"),
            ("现金流", "不完整查询"),
            ("分析ABC公司的现金流", "不存在公司"),
            ("现金流质量", "无股票指定"),
            ("分析现金", "错误表达"),
        ]
        
        for query, test_name in error_cases:
            self.test_query(query, False, test_name, f"{category}-错误用例")
    
    def test_multi_period_comparison(self):
        """2.4 多期财务对比测试"""
        category = "2.4 多期财务对比"
        
        # 正常用例
        normal_cases = [
            ("分析贵州茅台的多期财务对比", "基础查询"),
            ("比较万科A不同时期的财务数据", "不同时期"),
            ("600519.SH最近几期的财务变化", "财务变化"),
            ("分析平安银行的财务趋势", "财务趋势"),
            ("宁德时代的同比环比分析", "同比环比"),
            ("比亚迪各期营收增长率", "增长率"),
            ("分析贵州茅台财务数据的波动性", "波动性"),
            ("中国平安历史财务对比", "历史对比"),
            ("万科A季度财务对比分析", "季度对比"),
            ("分析600519近5期财务数据", "近N期"),
        ]
        
        for query, test_name in normal_cases:
            self.test_query(query, True, test_name, category)
        
        # 边界测试
        boundary_cases = [
            ("贵州茅台财务对比", "简化表达"),
            ("600519多期对比", "6位代码"),
            ("分析万科财务走势", "走势表达"),
            ("平安银行年度对比", "年度对比"),
            ("比亚迪财务增长分析", "增长分析"),
            ("贵州茅台连续三年财务", "连续N年"),
            ("分析宁德时代最新5个季度", "最新N季度"),
        ]
        
        for query, test_name in boundary_cases:
            self.test_query(query, True, test_name, f"{category}-边界测试")
        
        # 错误用例
        error_cases = [
            ("茅台的多期对比", "股票简称错误"),
            ("对比一下", "模糊查询"),
            ("贵州茅台2099年的财务对比", "未来时间"),
            ("多期财务对比", "无股票指定"),
            ("财务对比", "不完整查询"),
            ("比较财务", "错误表达"),
        ]
        
        for query, test_name in error_cases:
            self.test_query(query, False, test_name, f"{category}-错误用例")
    
    def test_profitability_analysis(self):
        """2.5 盈利能力分析测试"""
        category = "2.5 盈利能力分析"
        
        # 正常用例
        normal_cases = [
            ("分析贵州茅台的盈利能力", "综合分析"),
            ("万科A的毛利率分析", "毛利率"),
            ("平安银行的净利率情况", "净利率"),
            ("分析宁德时代的ROA", "ROA分析"),
            ("评估比亚迪的利润质量", "利润质量"),
            ("中国平安盈利能力评价", "能力评价"),
            ("分析600519.SH的盈利水平", "盈利水平"),
            ("贵州茅台净资产收益率分析", "ROE分析"),
        ]
        
        for query, test_name in normal_cases:
            self.test_query(query, True, test_name, category)
        
        # 边界测试
        boundary_cases = [
            ("贵州茅台盈利怎么样", "口语化"),
            ("600519盈利能力", "6位代码"),
            ("万科盈利分析", "简化名称"),
            ("分析平安银行赚钱能力", "赚钱能力"),
            ("比亚迪利润率分析", "利润率"),
        ]
        
        for query, test_name in boundary_cases:
            self.test_query(query, True, test_name, f"{category}-边界测试")
        
        # 错误用例
        error_cases = [
            ("盈利能力", "空泛查询"),
            ("茅台盈利怎么样", "股票简称错误"),
            ("贵州茅台的XYZ率", "无效指标"),
            ("分析盈利", "无股票指定"),
            ("盈利分析", "不完整查询"),
        ]
        
        for query, test_name in error_cases:
            self.test_query(query, False, test_name, f"{category}-错误用例")
    
    def test_solvency_analysis(self):
        """2.6 偿债能力分析测试"""
        category = "2.6 偿债能力分析"
        
        # 正常用例
        normal_cases = [
            ("分析万科A的偿债能力", "综合分析"),
            ("贵州茅台的流动比率", "流动比率"),
            ("平安银行的速动比率分析", "速动比率"),
            ("分析宁德时代的资产负债率", "资产负债率"),
            ("比亚迪的利息保障倍数", "利息保障"),
            ("中国平安偿债能力评估", "能力评估"),
            ("分析600519.SH的负债情况", "负债情况"),
            ("万科A短期偿债能力分析", "短期偿债"),
        ]
        
        for query, test_name in normal_cases:
            self.test_query(query, True, test_name, category)
        
        # 边界测试
        boundary_cases = [
            ("贵州茅台偿债怎么样", "口语化"),
            ("600519偿债能力", "6位代码"),
            ("万科负债分析", "负债分析"),
            ("分析平安银行债务风险", "债务风险"),
            ("比亚迪长期偿债能力", "长期偿债"),
        ]
        
        for query, test_name in boundary_cases:
            self.test_query(query, True, test_name, f"{category}-边界测试")
        
        # 错误用例
        error_cases = [
            ("偿债", "不完整查询"),
            ("茅台的负债情况", "股票简称错误"),
            ("贵州茅台的还钱能力", "混淆概念"),
            ("偿债能力", "无股票指定"),
            ("分析偿债", "错误表达"),
        ]
        
        for query, test_name in error_cases:
            self.test_query(query, False, test_name, f"{category}-错误用例")
    
    def test_operational_analysis(self):
        """2.7 运营能力分析测试"""
        category = "2.7 运营能力分析"
        
        # 正常用例
        normal_cases = [
            ("分析贵州茅台的运营能力", "综合分析"),
            ("万科A的存货周转率", "存货周转"),
            ("分析平安银行的应收账款周转率", "应收周转"),
            ("宁德时代的总资产周转率", "资产周转"),
            ("分析比亚迪的营运资本管理", "营运资本"),
            ("中国平安运营效率分析", "运营效率"),
            ("600519.SH的周转率分析", "周转率"),
            ("贵州茅台运营能力评价", "能力评价"),
        ]
        
        for query, test_name in normal_cases:
            self.test_query(query, True, test_name, category)
        
        # 边界测试
        boundary_cases = [
            ("贵州茅台运营怎么样", "口语化"),
            ("600519运营能力", "6位代码"),
            ("万科运营分析", "简化名称"),
            ("分析平安银行运转效率", "运转效率"),
            ("比亚迪资产利用率", "资产利用"),
        ]
        
        for query, test_name in boundary_cases:
            self.test_query(query, True, test_name, f"{category}-边界测试")
        
        # 错误用例
        error_cases = [
            ("运营", "空查询"),
            ("茅台运营效率", "股票简称错误"),
            ("贵州茅台的运转速度", "无效指标"),
            ("运营能力", "无股票指定"),
            ("分析运营", "错误表达"),
        ]
        
        for query, test_name in error_cases:
            self.test_query(query, False, test_name, f"{category}-错误用例")
    
    def test_growth_analysis(self):
        """2.8 成长能力分析测试"""
        category = "2.8 成长能力分析"
        
        # 正常用例
        normal_cases = [
            ("分析宁德时代的成长能力", "综合分析"),
            ("贵州茅台的营收增长率", "营收增长"),
            ("分析比亚迪的利润增长情况", "利润增长"),
            ("万科A的资产增长率", "资产增长"),
            ("平安银行的年复合增长率", "复合增长"),
            ("中国平安成长性分析", "成长性"),
            ("分析600519.SH的增长潜力", "增长潜力"),
            ("宁德时代业绩增长分析", "业绩增长"),
            ("贵州茅台扩张能力分析", "扩张能力"),
            ("分析比亚迪的发展速度", "发展速度"),
        ]
        
        for query, test_name in normal_cases:
            self.test_query(query, True, test_name, category)
        
        # 边界测试
        boundary_cases = [
            ("贵州茅台增长怎么样", "口语化"),
            ("600519成长能力", "6位代码"),
            ("万科成长分析", "简化名称"),
            ("分析平安银行成长", "简化表达"),
            ("比亚迪增速分析", "增速分析"),
            ("宁德时代近三年增长", "近N年增长"),
            ("贵州茅台季度增长率", "季度增长"),
        ]
        
        for query, test_name in boundary_cases:
            self.test_query(query, True, test_name, f"{category}-边界测试")
        
        # 错误用例
        error_cases = [
            ("成长性", "模糊查询"),
            ("茅台增长如何", "股票简称错误"),
            ("贵州茅台明年的增长率", "未来时间"),
            ("成长能力", "无股票指定"),
            ("分析成长", "错误表达"),
            ("增长分析", "不完整查询"),
        ]
        
        for query, test_name in error_cases:
            self.test_query(query, False, test_name, f"{category}-错误用例")
    
    def generate_report(self):
        """生成测试报告"""
        print("\n" + "="*80)
        print("测试报告")
        print("="*80)
        print(f"总测试数: {self.test_results['total']}")
        print(f"通过: {self.test_results['passed']}")
        print(f"失败: {self.test_results['failed']}")
        print(f"通过率: {self.test_results['passed'] / self.test_results['total'] * 100:.1f}%")
        
        if self.test_results['errors']:
            print("\n" + "="*80)
            print("失败测试详情")
            print("="*80)
            for error in self.test_results['errors']:
                print(f"\n类别: {error['category']}")
                print(f"测试: {error['test_name']}")
                print(f"查询: {error['query']}")
                print(f"错误: {error['error']}")
        
        # 保存详细报告
        report_file = f"financial_test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(self.test_results, f, ensure_ascii=False, indent=2)
        print(f"\n详细报告已保存至: {report_file}")
        
        # 分类统计
        print("\n" + "="*80)
        print("分类统计")
        print("="*80)
        category_stats = {}
        for detail in self.test_results['details']:
            category = detail['category']
            if category not in category_stats:
                category_stats[category] = {'total': 0, 'passed': 0, 'failed': 0}
            category_stats[category]['total'] += 1
            if detail['passed']:
                category_stats[category]['passed'] += 1
            else:
                category_stats[category]['failed'] += 1
        
        for category, stats in sorted(category_stats.items()):
            pass_rate = stats['passed'] / stats['total'] * 100 if stats['total'] > 0 else 0
            print(f"{category}: {stats['passed']}/{stats['total']} ({pass_rate:.1f}%)")


if __name__ == "__main__":
    tester = ComprehensiveTest()
    tester.run_all_tests()