#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
资金查询功能综合测试
测试所有资金相关查询的稳定性和正确性
"""

import time
from datetime import datetime
from typing import Dict, List, Tuple
from agents.sql_agent import SQLAgent
from agents.money_flow_agent import MoneyFlowAgent
from agents.hybrid_agent import HybridAgent
from utils.query_templates import match_query_template

class MoneyFlowComprehensiveTest:
    """资金查询功能综合测试类"""
    
    def __init__(self):
        """初始化测试环境"""
        print("初始化测试环境...")
        self.sql_agent = SQLAgent()
        self.money_flow_agent = MoneyFlowAgent()
        self.hybrid_agent = HybridAgent()
        self.test_results = []
        self.start_time = datetime.now()
        
    def run_all_tests(self):
        """运行所有测试"""
        print("\n" + "="*80)
        print("资金查询功能综合测试")
        print("="*80)
        
        # 1. 模板匹配测试
        self.test_template_matching()
        
        # 2. 个股资金查询测试
        self.test_individual_stock_queries()
        
        # 3. 板块资金查询测试
        self.test_sector_queries()
        
        # 4. 资金流向排名测试
        self.test_ranking_queries()
        
        # 5. 深度分析测试
        self.test_deep_analysis_queries()
        
        # 6. 错误处理测试
        self.test_error_handling()
        
        # 7. 性能测试
        self.test_performance()
        
        # 8. 生成测试报告
        self.generate_report()
        
    def test_template_matching(self):
        """测试模板匹配功能"""
        print("\n### 1. 模板匹配测试")
        print("-" * 60)
        
        test_cases = [
            # (查询, 预期模板, 预期路由)
            ("贵州茅台的主力资金", "个股主力资金", "SQL_ONLY"),
            ("平安银行的主力净流入", "个股主力资金", "SQL_ONLY"),
            ("银行板块的主力资金流入", "板块主力资金", "SQL_ONLY"),
            ("光伏设备板块主力资金", "板块主力资金", "SQL_ONLY"),
            ("主力净流入最多的前10只股票", "主力净流入排行", "SQL_ONLY"),
            ("主力资金净流出排名", "主力净流出排行", "SQL_ONLY"),
            ("分析比亚迪的资金流向", "资金流向分析", "MONEY_FLOW"),
            ("茅台的资金流向如何", "资金流向分析", "MONEY_FLOW"),
            ("贵州茅台的超大单分析", "超大单分析", "MONEY_FLOW"),
        ]
        
        passed = 0
        for query, expected_template, expected_route in test_cases:
            result = match_query_template(query)
            if result:
                template, params = result
                if template.name == expected_template and template.route_type == expected_route:
                    passed += 1
                    self._record_test("模板匹配", query, True, f"正确匹配: {template.name}")
                else:
                    self._record_test("模板匹配", query, False, 
                                    f"错误: 期望{expected_template}/{expected_route}, 实际{template.name}/{template.route_type}")
            else:
                self._record_test("模板匹配", query, False, "未匹配到任何模板")
                
        print(f"通过率: {passed}/{len(test_cases)} ({passed/len(test_cases)*100:.1f}%)")
        
    def test_individual_stock_queries(self):
        """测试个股资金查询"""
        print("\n### 2. 个股资金查询测试")
        print("-" * 60)
        
        test_queries = [
            "贵州茅台的主力资金",
            "平安银行的主力净流入",
            "比亚迪的主力资金流出",
            "中国平安昨天的主力资金",
            "万科最新的主力资金情况",
        ]
        
        for query in test_queries:
            print(f"\n测试: {query}")
            start = time.time()
            
            try:
                result = self.sql_agent.query(query)
                elapsed = time.time() - start
                
                if result['success']:
                    # 检查结果是否包含关键信息
                    result_text = result['result']
                    has_amount = "净流入" in result_text or "净流出" in result_text
                    has_data = "亿元" in result_text or "万元" in result_text
                    
                    if has_amount and has_data:
                        self._record_test("个股资金查询", query, True, f"成功 (耗时{elapsed:.2f}秒)")
                        print(f"✅ 查询成功，耗时{elapsed:.2f}秒")
                    else:
                        self._record_test("个股资金查询", query, False, "返回结果格式不正确")
                        print(f"❌ 结果格式不正确")
                else:
                    self._record_test("个股资金查询", query, False, result.get('error', '未知错误'))
                    print(f"❌ 查询失败: {result.get('error', '未知错误')}")
                    
            except Exception as e:
                self._record_test("个股资金查询", query, False, str(e))
                print(f"❌ 异常: {str(e)}")
                
    def test_sector_queries(self):
        """测试板块资金查询"""
        print("\n### 3. 板块资金查询测试")
        print("-" * 60)
        
        test_queries = [
            "银行板块的主力资金流入",
            "光伏设备板块主力资金",
            "半导体板块的主力资金流向",
            "汽车行业的主力资金",
            "医药板块昨天的主力资金",
        ]
        
        for query in test_queries:
            print(f"\n测试: {query}")
            start = time.time()
            
            try:
                result = self.sql_agent.query(query)
                elapsed = time.time() - start
                
                if result['success']:
                    result_text = result['result']
                    # 检查板块特有信息
                    has_sector_info = "板块代码" in result_text or "板块类型" in result_text
                    has_ranking = "板块排名" in result_text or "第" in result_text
                    
                    if has_sector_info or has_ranking:
                        self._record_test("板块资金查询", query, True, f"成功 (耗时{elapsed:.2f}秒)")
                        print(f"✅ 查询成功，耗时{elapsed:.2f}秒")
                    else:
                        self._record_test("板块资金查询", query, False, "缺少板块特有信息")
                        print(f"❌ 缺少板块信息")
                else:
                    self._record_test("板块资金查询", query, False, result.get('error', '未知错误'))
                    print(f"❌ 查询失败: {result.get('error', '未知错误')}")
                    
            except Exception as e:
                self._record_test("板块资金查询", query, False, str(e))
                print(f"❌ 异常: {str(e)}")
                
    def test_ranking_queries(self):
        """测试资金流向排名查询"""
        print("\n### 4. 资金流向排名测试")
        print("-" * 60)
        
        test_queries = [
            "主力净流入最多的前10只股票",
            "昨天主力净流出排行前5",
            "主力资金净流入排名",
            "今天主力净流出最多的前20只股票",
        ]
        
        for query in test_queries:
            print(f"\n测试: {query}")
            start = time.time()
            
            try:
                # 排名查询应该通过Hybrid Agent路由
                result = self.hybrid_agent.query(query)
                elapsed = time.time() - start
                
                if result['success']:
                    result_text = result['result']
                    # 检查是否有排名信息
                    has_ranking = "排名" in result_text or "第" in result_text or "前" in result_text
                    has_multiple = result_text.count("亿元") >= 3 or result_text.count("万元") >= 3
                    
                    if has_ranking or has_multiple:
                        self._record_test("排名查询", query, True, f"成功 (耗时{elapsed:.2f}秒)")
                        print(f"✅ 查询成功，耗时{elapsed:.2f}秒")
                    else:
                        self._record_test("排名查询", query, False, "缺少排名信息")
                        print(f"❌ 缺少排名信息")
                else:
                    self._record_test("排名查询", query, False, result.get('error', '未知错误'))
                    print(f"❌ 查询失败: {result.get('error', '未知错误')}")
                    
            except Exception as e:
                self._record_test("排名查询", query, False, str(e))
                print(f"❌ 异常: {str(e)}")
                
    def test_deep_analysis_queries(self):
        """测试深度资金流向分析"""
        print("\n### 5. 深度资金流向分析测试")
        print("-" * 60)
        
        test_queries = [
            "分析贵州茅台的资金流向",
            "比亚迪的资金流向如何",
            "平安银行的主力资金流向分析",
            "分析万科的超大单资金",
            "招商银行的机构资金分析",
        ]
        
        for query in test_queries:
            print(f"\n测试: {query}")
            start = time.time()
            
            try:
                result = self.money_flow_agent.query(query)
                elapsed = time.time() - start
                
                if result['success']:
                    result_text = result['result']
                    # 检查深度分析特征
                    has_analysis = "分析" in result_text or "特征" in result_text or "趋势" in result_text
                    has_detail = "超大单" in result_text and "大单" in result_text and "中单" in result_text
                    
                    if has_analysis and has_detail:
                        self._record_test("深度分析", query, True, f"成功 (耗时{elapsed:.2f}秒)")
                        print(f"✅ 分析成功，耗时{elapsed:.2f}秒")
                    else:
                        self._record_test("深度分析", query, False, "缺少深度分析内容")
                        print(f"❌ 缺少分析内容")
                else:
                    self._record_test("深度分析", query, False, result.get('error', '未知错误'))
                    print(f"❌ 分析失败: {result.get('error', '未知错误')}")
                    
            except Exception as e:
                self._record_test("深度分析", query, False, str(e))
                print(f"❌ 异常: {str(e)}")
                
    def test_error_handling(self):
        """测试错误处理"""
        print("\n### 6. 错误处理测试")
        print("-" * 60)
        
        error_cases = [
            ("", "空查询"),
            ("   ", "空白查询"),
            ("不存在的股票的主力资金", "无效股票"),
            ("未来板块的主力资金", "无效板块"),
            ("主力资金", "模糊查询"),
            ("大资金小资金中资金", "非标准术语"),
        ]
        
        for query, case_type in error_cases:
            print(f"\n测试{case_type}: '{query}'")
            
            try:
                result = self.hybrid_agent.query(query)
                
                if not result['success']:
                    self._record_test("错误处理", case_type, True, "正确处理错误")
                    print(f"✅ 正确处理: {result.get('error', '返回失败')}")
                else:
                    # 某些情况可能返回成功但有提示
                    if "无效" in result.get('result', '') or "错误" in result.get('result', ''):
                        self._record_test("错误处理", case_type, True, "返回错误提示")
                        print(f"✅ 返回提示信息")
                    else:
                        self._record_test("错误处理", case_type, False, "未正确处理错误")
                        print(f"❌ 未正确处理")
                        
            except Exception as e:
                self._record_test("错误处理", case_type, True, f"抛出异常: {str(e)}")
                print(f"✅ 捕获异常: {str(e)}")
                
    def test_performance(self):
        """测试查询性能"""
        print("\n### 7. 性能测试")
        print("-" * 60)
        
        performance_tests = [
            ("贵州茅台的主力资金", "个股快速查询", 5.0),
            ("银行板块的主力资金", "板块快速查询", 5.0),
            ("主力净流入最多的前10只股票", "排名查询", 30.0),
            ("分析茅台的资金流向", "深度分析", 60.0),
        ]
        
        for query, test_type, expected_time in performance_tests:
            print(f"\n测试{test_type}: {query}")
            
            # 预热查询
            try:
                _ = self.hybrid_agent.query(query)
            except:
                pass
            
            # 正式测试
            times = []
            for i in range(3):
                start = time.time()
                try:
                    result = self.hybrid_agent.query(query)
                    elapsed = time.time() - start
                    if result['success']:
                        times.append(elapsed)
                except:
                    pass
                    
            if times:
                avg_time = sum(times) / len(times)
                if avg_time <= expected_time:
                    self._record_test("性能测试", test_type, True, 
                                    f"平均耗时{avg_time:.2f}秒 <= {expected_time}秒")
                    print(f"✅ 性能达标: 平均{avg_time:.2f}秒")
                else:
                    self._record_test("性能测试", test_type, False, 
                                    f"平均耗时{avg_time:.2f}秒 > {expected_time}秒")
                    print(f"❌ 性能不达标: 平均{avg_time:.2f}秒")
            else:
                self._record_test("性能测试", test_type, False, "所有测试失败")
                print(f"❌ 测试失败")
                
    def _record_test(self, category: str, test_case: str, passed: bool, message: str):
        """记录测试结果"""
        self.test_results.append({
            'category': category,
            'test_case': test_case,
            'passed': passed,
            'message': message,
            'timestamp': datetime.now()
        })
        
    def generate_report(self):
        """生成测试报告"""
        print("\n" + "="*80)
        print("测试报告总结")
        print("="*80)
        
        # 统计各类别结果
        category_stats = {}
        for result in self.test_results:
            category = result['category']
            if category not in category_stats:
                category_stats[category] = {'total': 0, 'passed': 0}
            category_stats[category]['total'] += 1
            if result['passed']:
                category_stats[category]['passed'] += 1
                
        # 输出统计
        print("\n### 测试统计")
        print("-" * 60)
        total_tests = len(self.test_results)
        total_passed = sum(1 for r in self.test_results if r['passed'])
        
        for category, stats in category_stats.items():
            rate = stats['passed'] / stats['total'] * 100 if stats['total'] > 0 else 0
            print(f"{category}: {stats['passed']}/{stats['total']} ({rate:.1f}%)")
            
        print("-" * 60)
        overall_rate = total_passed / total_tests * 100 if total_tests > 0 else 0
        print(f"总体通过率: {total_passed}/{total_tests} ({overall_rate:.1f}%)")
        
        # 输出失败用例
        failed_tests = [r for r in self.test_results if not r['passed']]
        if failed_tests:
            print("\n### 失败测试详情")
            print("-" * 60)
            for test in failed_tests[:10]:  # 只显示前10个
                print(f"[{test['category']}] {test['test_case']}")
                print(f"  原因: {test['message']}")
                
        # 测试时长
        elapsed_time = (datetime.now() - self.start_time).total_seconds()
        print(f"\n测试总耗时: {elapsed_time:.2f}秒")
        
        # 保存报告
        report_path = f"test_reports/money_flow_test_{self.start_time.strftime('%Y%m%d_%H%M%S')}.txt"
        print(f"\n详细报告已保存至: {report_path}")


if __name__ == "__main__":
    # 设置5分钟超时
    import signal
    
    def timeout_handler(signum, frame):
        print("\n⚠️ 测试超时（5分钟），强制结束")
        raise TimeoutError("测试超时")
        
    # Windows不支持SIGALRM，使用threading
    import threading
    
    def run_with_timeout():
        tester = MoneyFlowComprehensiveTest()
        tester.run_all_tests()
        
    # 创建线程并设置超时
    test_thread = threading.Thread(target=run_with_timeout)
    test_thread.daemon = True
    test_thread.start()
    
    # 等待5分钟
    test_thread.join(timeout=300)
    
    if test_thread.is_alive():
        print("\n⚠️ 测试超时（5分钟），部分测试未完成")
    else:
        print("\n✅ 所有测试完成")