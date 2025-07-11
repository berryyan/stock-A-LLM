#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Financial Agent 综合测试脚本 - Windows版本
为Windows环境优化，考虑LLM响应时间
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import time
import json
from datetime import datetime
from agents.financial_agent_modular import FinancialAgentModular

# 测试用例配置
TEST_CATEGORIES = {
    "1.财务健康度分析": {
        "positive": [
            ("分析贵州茅台的财务健康度", "完整名称"),
            ("分析600519.SH的财务健康度", "股票代码"),
            ("分析平安银行的财务健康度", "银行股"),
            ("分析万科A的财务状况", "财务状况"),
        ],
        "negative": [
            ("茅台的财务健康度", "股票简称"),
            ("", "空查询"),
            ("12345的财务健康度", "错误代码"),
            ("600519.sh的财务健康度", "小写后缀"),
        ]
    },
    
    "2.杜邦分析": {
        "positive": [
            ("贵州茅台的杜邦分析", "完整名称"),
            ("平安银行ROE分解分析", "ROE分解"),
            ("600519.SH的杜邦分析", "股票代码"),
            ("分析万科A的ROE", "分析ROE"),
        ],
        "negative": [
            ("茅台的杜邦分析", "股票简称"),
            ("杜邦分析", "缺少股票"),
            ("600519.sz的杜邦分析", "小写后缀"),
            ("不存在公司的杜邦分析", "无效股票"),
        ]
    },
    
    "3.现金流质量分析": {
        "positive": [
            ("分析万科A的现金流质量", "完整名称"),
            ("分析000002.SZ的现金流质量", "股票代码"),
            ("评估平安银行的现金流", "评估"),
            ("贵州茅台的现金含量比率", "含量比率"),
        ],
        "negative": [
            ("万科的现金流", "股票简称"),
            ("现金流质量", "缺少股票"),
            ("   ", "空白查询"),
            ("000002.SH的现金流", "错误后缀"),
        ]
    },
    
    "4.多期财务对比": {
        "positive": [
            ("贵州茅台最近3期财务对比", "指定期数"),
            ("600519.SH最近几期的财务变化", "财务变化"),
            ("分析平安银行的财务趋势", "财务趋势"),
            ("万科A的季度财务对比分析", "季度对比"),
        ],
        "negative": [
            ("茅台对比", "股票简称"),
            ("财务对比", "缺少股票"),
            ("123456最近的对比", "无效代码"),
            ("600519.sz财务对比", "小写后缀"),
        ]
    },
    
    "5.盈利能力分析": {
        "positive": [
            ("分析比亚迪的盈利能力", "完整名称"),
            ("分析002594.SZ的盈利能力", "股票代码"),
            ("万科A的毛利率分析", "毛利率"),
            ("贵州茅台的净资产收益率分析", "ROE分析"),
        ],
        "negative": [
            ("平安的盈利", "歧义简称"),
            ("盈利能力", "缺少股票"),
            ("600000.sh盈利", "小写后缀"),
            ("特斯拉的盈利能力", "非A股"),
        ]
    },
    
    "6.偿债能力分析": {
        "positive": [
            ("分析万科A的偿债能力", "完整名称"),
            ("分析601939.SH的偿债能力", "股票代码"),
            ("贵州茅台的流动比率", "流动比率"),
            ("平安银行的资产负债率", "负债率"),
        ],
        "negative": [
            ("建行的偿债", "股票简称"),
            ("偿债能力分析", "缺少股票"),
            ("000000的偿债", "无效代码"),
            ("60051的偿债能力", "错误长度"),
        ]
    },
    
    "7.运营能力分析": {
        "positive": [
            ("分析海尔智家的运营效率", "完整名称"),
            ("分析600690.SH的运营能力", "股票代码"),
            ("万科A的存货周转率", "存货周转"),
            ("贵州茅台的运营能力评价", "能力评价"),
        ],
        "negative": [
            ("格力的运营", "股票简称"),
            ("运营效率", "缺少股票"),
            ("1234567运营", "7位代码"),
            ("600690.BJ的运营", "错误后缀"),
        ]
    },
    
    "8.成长能力分析": {
        "positive": [
            ("分析宁德时代的成长性", "完整名称"),
            ("分析300750.SZ的成长能力", "股票代码"),
            ("贵州茅台的营收增长率", "营收增长"),
            ("比亚迪的利润增长情况", "利润增长"),
        ],
        "negative": [
            ("宁德的成长性", "股票简称"),
            ("成长性分析", "缺少股票"),
            ("特斯拉的成长", "非A股"),
            ("600519.SZ成长", "错误后缀"),
        ]
    }
}

class FinancialAgentTester:
    def __init__(self):
        self.agent = FinancialAgentModular()
        self.results = []
        self.category_stats = {}
        
    def test_single_query(self, query, expected_success, test_name, category):
        """测试单个查询"""
        print(f"\n[{category}] {test_name}")
        print(f"查询: {query}")
        print(f"期望: {'成功' if expected_success else '失败'}")
        
        start_time = time.time()
        try:
            result = self.agent.analyze(query)
            elapsed_time = time.time() - start_time
            
            actual_success = result.get('success', False)
            test_passed = actual_success == expected_success
            
            test_result = {
                "category": category,
                "test_name": test_name,
                "query": query,
                "expected_success": expected_success,
                "actual_success": actual_success,
                "passed": test_passed,
                "elapsed_time": elapsed_time,
                "error": result.get('error') if not actual_success else None
            }
            
            self.results.append(test_result)
            
            # 更新分类统计
            if category not in self.category_stats:
                self.category_stats[category] = {"total": 0, "passed": 0}
            self.category_stats[category]["total"] += 1
            if test_passed:
                self.category_stats[category]["passed"] += 1
            
            # 打印结果
            print(f"实际: {'成功' if actual_success else '失败'}")
            print(f"结果: {'✅ 通过' if test_passed else '❌ 失败'}")
            print(f"耗时: {elapsed_time:.2f}秒")
            
            if not actual_success and result.get('error'):
                print(f"错误: {result['error']}")
            
            return test_passed
            
        except Exception as e:
            print(f"异常: {str(e)}")
            test_result = {
                "category": category,
                "test_name": test_name,
                "query": query,
                "expected_success": expected_success,
                "actual_success": False,
                "passed": False,
                "elapsed_time": time.time() - start_time,
                "error": f"Exception: {str(e)}"
            }
            self.results.append(test_result)
            
            if category not in self.category_stats:
                self.category_stats[category] = {"total": 0, "passed": 0}
            self.category_stats[category]["total"] += 1
            
            return False
    
    def run_tests(self, run_positive=True, run_negative=True, categories=None):
        """运行测试"""
        print("=" * 80)
        print("Financial Agent 综合测试 - Windows优化版")
        print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 80)
        
        test_categories = categories if categories else TEST_CATEGORIES.keys()
        
        for category in test_categories:
            if category not in TEST_CATEGORIES:
                continue
                
            print(f"\n{'='*60}")
            print(f"测试类别: {category}")
            print(f"{'='*60}")
            
            test_data = TEST_CATEGORIES[category]
            
            # 正向测试
            if run_positive and "positive" in test_data:
                print("\n正向测试用例:")
                for query, test_name in test_data["positive"]:
                    self.test_single_query(query, True, test_name, category)
            
            # 负向测试
            if run_negative and "negative" in test_data:
                print("\n负向测试用例:")
                for query, test_name in test_data["negative"]:
                    self.test_single_query(query, False, test_name, category)
    
    def generate_report(self):
        """生成测试报告"""
        total_tests = len(self.results)
        passed_tests = sum(1 for r in self.results if r["passed"])
        failed_tests = total_tests - passed_tests
        
        print("\n" + "=" * 80)
        print("测试总结")
        print("=" * 80)
        print(f"总测试数: {total_tests}")
        print(f"通过: {passed_tests}")
        print(f"失败: {failed_tests}")
        print(f"通过率: {passed_tests/total_tests*100:.1f}%")
        
        # 分类统计
        print("\n分类统计:")
        for category, stats in self.category_stats.items():
            pass_rate = stats["passed"] / stats["total"] * 100 if stats["total"] > 0 else 0
            print(f"{category}: {stats['passed']}/{stats['total']} ({pass_rate:.1f}%)")
        
        # 失败详情
        failures = [r for r in self.results if not r["passed"]]
        if failures:
            print("\n失败测试详情:")
            for i, failure in enumerate(failures, 1):
                print(f"\n{i}. [{failure['category']}] {failure['test_name']}")
                print(f"   查询: {failure['query']}")
                print(f"   期望: {'成功' if failure['expected_success'] else '失败'}")
                print(f"   实际: {'成功' if failure['actual_success'] else '失败'}")
                if failure['error']:
                    print(f"   错误: {failure['error']}")
        
        # 保存报告
        report = {
            "test_time": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "failed_tests": failed_tests,
            "pass_rate": f"{passed_tests/total_tests*100:.1f}%",
            "category_stats": self.category_stats,
            "test_results": self.results
        }
        
        report_file = f"test_financial_agent_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        print(f"\n测试报告已保存到: {report_file}")
        
        return passed_tests == total_tests

def main():
    """主函数"""
    import argparse
    parser = argparse.ArgumentParser(description='Financial Agent 测试脚本')
    parser.add_argument('--positive', action='store_true', help='只运行正向测试')
    parser.add_argument('--negative', action='store_true', help='只运行负向测试')
    parser.add_argument('--categories', nargs='+', help='指定测试类别')
    parser.add_argument('--quick', action='store_true', help='快速测试（每类2个用例）')
    
    args = parser.parse_args()
    
    # 如果没有指定positive或negative，则都运行
    run_positive = True
    run_negative = True
    if args.positive and not args.negative:
        run_negative = False
    elif args.negative and not args.positive:
        run_positive = False
    
    # 快速测试模式
    if args.quick:
        # 修改测试用例，每类只保留2个
        for category in TEST_CATEGORIES:
            if "positive" in TEST_CATEGORIES[category]:
                TEST_CATEGORIES[category]["positive"] = TEST_CATEGORIES[category]["positive"][:1]
            if "negative" in TEST_CATEGORIES[category]:
                TEST_CATEGORIES[category]["negative"] = TEST_CATEGORIES[category]["negative"][:1]
    
    tester = FinancialAgentTester()
    tester.run_tests(run_positive, run_negative, args.categories)
    success = tester.generate_report()
    
    exit(0 if success else 1)

if __name__ == "__main__":
    main()