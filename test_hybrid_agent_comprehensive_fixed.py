#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Hybrid Agent 全面测试套件 - 修正版
基于test-guide-comprehensive.md的完整功能测试
覆盖所有混合查询和路由功能，参考SQL Agent的测试标准
"""
import sys
import os
import time
import json
from datetime import datetime
from typing import Dict, List, Tuple, Any

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.hybrid_agent_modular import HybridAgentModular


class ComprehensiveTest:
    """综合测试类"""
    
    def __init__(self):
        self.agent = HybridAgentModular()
        self.test_results = {
            'total': 0,
            'passed': 0,
            'failed': 0,
            'errors': [],
            'details': []
        }
        
    def test_query(self, query: str, expected_success: bool = True, 
                   test_name: str = "", category: str = "", 
                   expected_route: str = None) -> Tuple[bool, Dict]:
        """测试单个查询"""
        print(f"\n{'='*60}")
        print(f"测试类别: {category}")
        print(f"测试名称: {test_name}")
        print(f"查询: {query}")
        print(f"预期: {'成功' if expected_success else '失败'}")
        if expected_route:
            print(f"预期路由: {expected_route}")
        print('-'*60)
        
        start_time = time.time()
        try:
            result = self.agent.query(query)
            elapsed_time = time.time() - start_time
            
            # 检查结果
            success = result.get('success', False)
            passed = success == expected_success
            
            # 如果有路由预期，也要检查
            if expected_route and success:
                actual_route = result.get('query_type', '')
                if actual_route != expected_route:
                    passed = False
                    print(f"路由不匹配: 期望{expected_route}, 实际{actual_route}")
            
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
                'result_preview': str(result.get('result', ''))[:200] if success else None,
                'query_type': result.get('query_type') if success else None
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
            if success:
                print(f"路由: {result.get('query_type', 'Unknown')}")
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
                'result_preview': None,
                'query_type': None
            }
            
            self.test_results['total'] += 1
            self.test_results['failed'] += 1
            self.test_results['errors'].append(test_result)
            self.test_results['details'].append(test_result)
            
            return False, {'success': False, 'error': str(e)}
    
    def run_all_tests(self):
        """运行所有测试用例"""
        print("="*80)
        print("Hybrid Agent 模块化版本综合测试")
        print("基于 test-guide-comprehensive.md 和 SQL Agent 测试标准")
        print(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*80)
        
        # 4.1 智能路由功能
        self.test_intelligent_routing()
        
        # 4.2 复合查询功能
        self.test_composite_queries()
        
        # 4.3 投资价值分析
        self.test_investment_analysis()
        
        # 4.4 风险评估分析
        self.test_risk_assessment()
        
        # 4.5 综合对比分析
        self.test_comparison_analysis()
        
        # 4.6 错误传递功能
        self.test_error_propagation()
        
        # 4.7 特殊场景处理
        self.test_special_scenarios()
        
        # 4.8 并行查询功能
        self.test_parallel_queries()
        
        # 生成测试报告
        self.generate_report()
    
    def test_intelligent_routing(self):
        """4.1 智能路由功能测试"""
        category = "4.1 智能路由"
        
        # 正常用例
        normal_cases = [
            ("贵州茅台最新股价", "SQL路由-股价", "sql"),
            ("贵州茅台的公司战略是什么", "RAG路由-战略", "rag"),
            ("分析贵州茅台的财务状况", "Financial路由", "financial_analysis"),
            ("分析茅台的资金流向", "MoneyFlow路由", "money_flow"),
            ("万科A最近30天的K线", "SQL路由-K线", "sql"),
            ("分析茅台最新年报", "RAG路由-年报", "rag"),
            ("对平安银行进行杜邦分析", "Financial路由-杜邦", "financial_analysis"),
            ("贵州茅台的主力资金", "SQL路由-主力资金", "sql"),
        ]
        
        for query, test_name, expected_route in normal_cases:
            self.test_query(query, True, test_name, category, expected_route)
        
        # 边界测试
        boundary_cases = [
            ("茅台股价", "简化查询", "sql"),
            ("查询贵州茅台", "模糊查询", "sql"),
            ("分析一下贵州茅台", "通用分析", None),  # 可能多种路由
            ("600519.SH", "纯股票代码", "sql"),
            ("贵州茅台怎么样", "口语化查询", None),
        ]
        
        for item in boundary_cases:
            if len(item) == 3:
                query, test_name, expected_route = item
            else:
                query, test_name = item
                expected_route = None
            self.test_query(query, True, test_name, f"{category}-边界测试", expected_route)
        
        # 错误用例
        error_cases = [
            ("", "空查询"),
            ("!@#$%^&*()", "无效字符"),
            ("查询一下", "无具体内容"),
            ("分析", "不完整查询"),
            ("   ", "纯空格"),
        ]
        
        for query, test_name in error_cases:
            self.test_query(query, False, test_name, f"{category}-错误用例")
    
    def test_composite_queries(self):
        """4.2 复合查询功能测试"""
        category = "4.2 复合查询"
        
        # 正常用例
        normal_cases = [
            ("贵州茅台的股价和主要业务", "股价和业务"),
            ("比亚迪的财务状况以及发展战略", "财务以及战略"),
            ("宁德时代的市值还有技术优势", "市值还有技术"),
            ("中国平安的业绩同时分析其风险", "业绩同时风险"),
            ("万科A的股价及其财务状况和发展前景", "多连接词"),
            ("贵州茅台的营收并且分析其竞争优势", "营收并且优势"),
            ("分析平安银行的股价、主营业务和财务健康度", "三项内容"),
            ("贵州茅台股价走势和主力资金流向", "走势和资金"),
        ]
        
        for query, test_name in normal_cases:
            self.test_query(query, True, test_name, category)
        
        # 边界测试
        boundary_cases = [
            ("贵州茅台的股价，主要业务", "逗号分隔"),
            ("万科A股价/财务/前景", "斜杠分隔"),
            ("比较贵州茅台和五粮液", "对比查询"),
            ("分析茅台vs五粮液", "vs格式"),
            ("贵州茅台股价&业务", "&符号"),
        ]
        
        for query, test_name in boundary_cases:
            self.test_query(query, True, test_name, f"{category}-边界测试")
        
        # 错误用例
        error_cases = [
            ("贵州茅台和", "不完整连接"),
            ("股价和股价", "重复内容"),
            ("xyz和abc", "无效内容"),
            ("和以及还有", "纯连接词"),
            ("分析和查询", "动词连接"),
        ]
        
        for query, test_name in error_cases:
            self.test_query(query, False, test_name, f"{category}-错误用例")
    
    def test_investment_analysis(self):
        """4.3 投资价值分析测试"""
        category = "4.3 投资价值分析"
        
        # 正常用例
        normal_cases = [
            ("分析贵州茅台的投资价值", "基础分析"),
            ("评估宁德时代的投资机会", "评估机会"),
            ("比亚迪值得投资吗", "值得投资"),
            ("万科A的投资潜力如何", "投资潜力"),
            ("综合评估平安银行的投资价值", "综合评估"),
            ("分析贵州茅台的长期投资价值", "长期价值"),
            ("中国平安投资价值分析报告", "分析报告"),
            ("600519.SH是否值得买入", "买入建议"),
        ]
        
        for query, test_name in normal_cases:
            self.test_query(query, True, test_name, category)
        
        # 边界测试
        boundary_cases = [
            ("贵州茅台投资分析", "简化表达"),
            ("万科值不值得买", "口语化"),
            ("分析茅台的投资回报", "投资回报"),
            ("平安银行投资风险收益", "风险收益"),
            ("比亚迪短期投资价值", "短期价值"),
        ]
        
        for query, test_name in boundary_cases:
            self.test_query(query, True, test_name, f"{category}-边界测试")
        
        # 错误用例
        error_cases = [
            ("投资价值", "空泛查询"),
            ("分析投资价值", "无股票"),
            ("茅台值得买吗", "股票简称"),
            ("值得投资吗", "无主体"),
            ("投资分析", "不完整"),
        ]
        
        for query, test_name in error_cases:
            self.test_query(query, False, test_name, f"{category}-错误用例")
    
    def test_risk_assessment(self):
        """4.4 风险评估分析测试"""
        category = "4.4 风险评估分析"
        
        # 正常用例
        normal_cases = [
            ("评估万科A的财务风险和股价表现", "财务风险"),
            ("分析恒大的风险状况", "风险状况"),
            ("评估中国平安的经营风险", "经营风险"),
            ("分析银行股的系统性风险", "系统性风险"),
            ("评估宁德时代的股价波动风险", "股价波动"),
            ("贵州茅台的投资风险分析", "投资风险"),
            ("分析比亚迪的市场风险", "市场风险"),
            ("万科A风险评估报告", "评估报告"),
        ]
        
        for query, test_name in normal_cases:
            self.test_query(query, True, test_name, category)
        
        # 边界测试
        boundary_cases = [
            ("贵州茅台风险怎么样", "口语化"),
            ("600519风险评估", "股票代码"),
            ("分析万科的潜在风险", "潜在风险"),
            ("平安银行风险控制", "风险控制"),
            ("比亚迪有什么风险", "什么风险"),
        ]
        
        for query, test_name in boundary_cases:
            self.test_query(query, True, test_name, f"{category}-边界测试")
        
        # 错误用例
        error_cases = [
            ("风险", "单词查询"),
            ("贵州茅台的天气风险", "无关风险"),
            ("评估风险收益比", "无股票"),
            ("风险分析", "不完整"),
            ("茅台风险", "股票简称"),
        ]
        
        for query, test_name in error_cases:
            self.test_query(query, False, test_name, f"{category}-错误用例")
    
    def test_comparison_analysis(self):
        """4.5 综合对比分析测试"""
        category = "4.5 综合对比分析"
        
        # 正常用例
        normal_cases = [
            ("对比茅台和五粮液的综合实力", "两股对比"),
            ("比较宁德时代和比亚迪的各方面表现", "各方面表现"),
            ("平安银行 vs 招商银行全面对比", "vs格式"),
            ("从财务、技术、市场等角度对比茅台和五粮液", "多维度"),
            ("从投资角度对比万科A和保利地产", "投资角度"),
            ("贵州茅台与五粮液竞争力对比", "竞争力"),
            ("分析比较中国平安和中国人寿", "保险对比"),
            ("对比600519和000858", "代码对比"),
        ]
        
        for query, test_name in normal_cases:
            self.test_query(query, True, test_name, category)
        
        # 边界测试
        boundary_cases = [
            ("茅台五粮液对比", "简化表达"),
            ("比较万科保利", "省略A"),
            ("宁德时代>比亚迪", "大于号"),
            ("平安vs招商", "简称vs"),
            ("对比贵州茅台、五粮液", "顿号分隔"),
        ]
        
        for query, test_name in boundary_cases:
            self.test_query(query, True, test_name, f"{category}-边界测试")
        
        # 错误用例
        error_cases = [
            ("对比贵州茅台", "单一股票"),
            ("对比茅台、五粮液、泸州老窖、洋河、剑南春", "过多股票"),
            ("对比ABC和XYZ", "无效股票"),
            ("对比", "无内容"),
            ("比较分析", "无股票"),
        ]
        
        for query, test_name in error_cases:
            self.test_query(query, False, test_name, f"{category}-错误用例")
    
    def test_error_propagation(self):
        """4.6 错误传递功能测试"""
        category = "4.6 错误传递"
        
        # 正常的错误传递（应该返回具体错误）
        error_cases = [
            ("xyz123的股价", "不存在股票-SQL"),
            ("不存在公司的年报", "不存在公司-RAG"),
            ("分析xyz的财务健康度", "不存在股票-Financial"),
            ("茅台的股价", "股票简称错误"),
            ("贵州茅台2099年的股价", "未来日期"),
            ("600519.sh的股价", "小写后缀"),
            ("12345的股价", "5位代码"),
            ("平安的财务分析", "歧义名称"),
        ]
        
        for query, test_name in error_cases:
            result = self.agent.query(query)
            passed = not result.get('success', True) and 'error' in result
            
            print(f"\n{'='*60}")
            print(f"测试类别: {category}")
            print(f"测试名称: {test_name}")
            print(f"查询: {query}")
            print(f"预期: 失败并返回具体错误")
            print('-'*60)
            print(f"实际: {'失败' if not result.get('success', True) else '成功'}")
            if not result.get('success', True):
                print(f"错误: {result.get('error', '无错误信息')}")
            print(f"状态: {'✅ 通过' if passed else '❌ 失败'}")
            
            self.test_results['total'] += 1
            if passed:
                self.test_results['passed'] += 1
            else:
                self.test_results['failed'] += 1
                self.test_results['errors'].append({
                    'category': category,
                    'test_name': test_name,
                    'query': query,
                    'error': '未正确传递错误信息'
                })
        
        # 正常查询不应有错误
        success_cases = [
            ("贵州茅台的股价", "正常查询"),
            ("万科A的财务分析", "正常财务"),
            ("分析比亚迪", "正常分析"),
        ]
        
        for query, test_name in success_cases:
            self.test_query(query, True, test_name, f"{category}-成功用例")
    
    def test_special_scenarios(self):
        """4.7 特殊场景处理测试"""
        category = "4.7 特殊场景处理"
        
        # 正常用例
        normal_cases = [
            ("请详细分析贵州茅台的股价走势、财务健康状况、主力资金流向、发展战略以及投资价值", "长查询"),
            ("查询贵州茅台、五粮液、泸州老窖的股价", "多股票查询"),
            ("分析BYD比亚迪的PE ratio", "中英混合"),
            ("ST股票的风险如何？", "特殊字符"),
            ("茅台最近咋样", "口语化查询"),
            ("*ST康美的情况", "特殊前缀"),
            ("中国平安-H的分析", "特殊后缀"),
            ("300750.SZ宁德时代分析", "代码+名称"),
        ]
        
        for query, test_name in normal_cases:
            self.test_query(query, True, test_name, category)
        
        # 边界测试
        boundary_cases = [
            ("贵州茅台" * 10, "重复内容"),
            ("分析" + "贵州茅台" * 5 + "的各种情况", "中度长查询"),
            ("!!!贵州茅台???", "标点符号"),
            ("【贵州茅台】股价", "特殊括号"),
            ("贵州茅台$股价", "货币符号"),
        ]
        
        for query, test_name in boundary_cases:
            self.test_query(query, True, test_name, f"{category}-边界测试")
        
        # 错误用例
        error_cases = [
            ("贵州茅台" * 100, "超长查询"),
            ("，。！？", "纯标点"),
            ("'; DROP TABLE stocks; --", "SQL注入"),
            ("<script>alert('test')</script>", "脚本注入"),
            ("\\x00\\x01\\x02", "控制字符"),
        ]
        
        for query, test_name in error_cases:
            self.test_query(query, False, test_name, f"{category}-错误用例")
    
    def test_parallel_queries(self):
        """4.8 并行查询功能测试"""
        category = "4.8 并行查询"
        
        # 正常用例
        normal_cases = [
            ("贵州茅台的最新股价和发展战略", "SQL+RAG"),
            ("万科A的市值和财务健康度", "SQL+Financial"),
            ("分析宁德时代的技术优势和财务状况", "RAG+Financial"),
            ("比亚迪的股价、主要业务和财务健康度", "三种类型"),
            ("全面分析贵州茅台的投资价值", "全面分析"),
            ("中国平安的业绩表现和风险评估", "业绩+风险"),
            ("分析万科A的资金流向和财务状况", "Money+Financial"),
            ("贵州茅台的K线走势和主力资金", "K线+资金"),
        ]
        
        for query, test_name in normal_cases:
            self.test_query(query, True, test_name, category)
        
        # 边界测试
        boundary_cases = [
            ("贵州茅台股价&业务&财务&资金", "&连接"),
            ("分析茅台的所有情况", "所有情况"),
            ("600519全方位分析", "全方位"),
            ("贵州茅台360度评估", "360度"),
            ("综合研究万科A", "综合研究"),
        ]
        
        for query, test_name in boundary_cases:
            self.test_query(query, True, test_name, f"{category}-边界测试")
        
        # 错误用例（部分失败的并行查询）
        error_cases = [
            ("贵州茅台的股价和不存在公司的业务", "部分失败"),
            ("xyz123的股价和业务分析", "全部失败"),
            ("和以及还有", "无效组合"),
            ("分析贵州茅台和xyz的对比", "部分无效"),
            ("查询所有股票的所有信息", "范围过大"),
        ]
        
        for query, test_name in error_cases:
            # 这些查询可能部分成功，所以不一定完全失败
            result = self.agent.query(query)
            print(f"\n{'='*60}")
            print(f"测试类别: {category}-错误用例")
            print(f"测试名称: {test_name}")
            print(f"查询: {query}")
            print(f"结果: {'部分成功' if result.get('success') else '失败'}")
            if result.get('error'):
                print(f"错误: {result.get('error')}")
    
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
        report_file = f"hybrid_test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
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
        
        # 路由统计
        print("\n" + "="*80)
        print("路由统计")
        print("="*80)
        route_stats = {}
        for detail in self.test_results['details']:
            if detail.get('query_type'):
                route = detail['query_type']
                route_stats[route] = route_stats.get(route, 0) + 1
        
        for route, count in sorted(route_stats.items()):
            print(f"{route}: {count}次")


if __name__ == "__main__":
    tester = ComprehensiveTest()
    tester.run_all_tests()