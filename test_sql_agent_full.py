#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SQL Agent模块化版本全面测试脚本
基于test-guide-comprehensive.md v5.3和项目中的所有测试用例
"""

import sys
import os
import time
import json
from datetime import datetime
from typing import Dict, List, Tuple, Any

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.sql_agent_modular import SQLAgentModular


class SQLAgentFullTest:
    """SQL Agent全面测试类"""
    
    def __init__(self):
        self.agent = SQLAgentModular()
        self.test_results = {
            'total': 0,
            'passed': 0,
            'failed': 0,
            'errors': [],
            'details': [],
            'summary_by_category': {}
        }
        
    def test_query(self, query: str, expected_success: bool = True, 
                   test_name: str = "", category: str = "") -> Tuple[bool, Dict]:
        """测试单个查询"""
        self.test_results['total'] += 1
        
        print(f"\n{'='*60}")
        print(f"类别: {category}")
        print(f"测试: {test_name}")
        print(f"查询: {query}")
        print(f"期望: {'成功' if expected_success else '失败'}")
        print('-'*60)
        
        start_time = time.time()
        try:
            result = self.agent.query(query)
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
            
            if passed:
                self.test_results['passed'] += 1
                status = "✅ 通过"
            else:
                self.test_results['failed'] += 1
                status = "❌ 失败"
                self.test_results['errors'].append(test_result)
            
            self.test_results['details'].append(test_result)
            
            # 更新分类统计
            if category not in self.test_results['summary_by_category']:
                self.test_results['summary_by_category'][category] = {
                    'total': 0, 'passed': 0, 'failed': 0
                }
            self.test_results['summary_by_category'][category]['total'] += 1
            if passed:
                self.test_results['summary_by_category'][category]['passed'] += 1
            else:
                self.test_results['summary_by_category'][category]['failed'] += 1
            
            # 打印结果
            print(f"结果: {'成功' if success else '失败'}")
            print(f"状态: {status}")
            print(f"耗时: {elapsed_time:.2f}秒")
            
            if success and result.get('result'):
                print(f"预览: {str(result.get('result'))[:100]}...")
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
                'error': f"异常: {str(e)}",
                'result_preview': None
            }
            
            self.test_results['failed'] += 1
            self.test_results['errors'].append(test_result)
            self.test_results['details'].append(test_result)
            
            if category not in self.test_results['summary_by_category']:
                self.test_results['summary_by_category'][category] = {
                    'total': 0, 'passed': 0, 'failed': 0
                }
            self.test_results['summary_by_category'][category]['total'] += 1
            self.test_results['summary_by_category'][category]['failed'] += 1
            
            return False, {'success': False, 'error': str(e)}
    
    def run_all_tests(self):
        """运行所有测试用例"""
        print("="*80)
        print("SQL Agent模块化版本全面测试")
        print("基于test-guide-comprehensive.md v5.3")
        print(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*80)
        
        # 1. 股价查询测试
        self.test_stock_price_queries()
        
        # 2. 成交量/成交额查询测试
        self.test_volume_amount_queries()
        
        # 3. 估值指标查询测试
        self.test_valuation_queries()
        
        # 4. K线查询测试
        self.test_kline_queries()
        
        # 5. 涨跌幅排名测试
        self.test_pct_chg_ranking_queries()
        
        # 6. 市值排名测试
        self.test_market_cap_ranking_queries()
        
        # 7. 成交额排名测试
        self.test_amount_ranking_queries()
        
        # 8. 主力资金查询测试
        self.test_money_flow_queries()
        
        # 9. 利润查询测试
        self.test_profit_queries()
        
        # 10. 财务排名测试
        self.test_financial_ranking_queries()
        
        # 11. 特殊股票名称测试
        self.test_special_stock_names()
        
        # 12. 参数提取边界测试
        self.test_parameter_extraction_edge_cases()
        
        # 13. 错误处理测试
        self.test_error_handling()
        
        # 生成测试报告
        self.generate_report()
    
    def test_stock_price_queries(self):
        """1. 股价查询测试"""
        category = "股价查询"
        
        # 基础查询
        test_cases = [
            ("贵州茅台最新股价", True, "最新股价"),
            ("贵州茅台的最新股价", True, "最新股价-的"),
            ("600519.SH的股价", True, "股票代码"),
            ("600519最新股价", True, "无后缀代码"),
            ("中国平安昨天的股价", True, "昨天股价"),
            ("万科A前天的股价", True, "前天股价"),
            ("平安银行2025-07-04的股价", True, "指定日期"),
            ("贵州茅台2025年07月04日的股价", True, "中文日期"),
        ]
        
        for query, expected_success, test_name in test_cases:
            self.test_query(query, expected_success, test_name, category)
    
    def test_volume_amount_queries(self):
        """2. 成交量/成交额查询测试"""
        category = "成交量/成交额查询"
        
        test_cases = [
            # 成交量
            ("平安银行昨天的成交量", True, "成交量-昨天"),
            ("贵州茅台最新成交量", True, "成交量-最新"),
            ("万科A前天的成交量", True, "成交量-前天"),
            ("600519.SH今天的成交量", True, "成交量-代码"),
            
            # 成交额
            ("中国平安的成交额", True, "成交额-默认"),
            ("宁德时代昨天的成交额", True, "成交额-昨天"),
            ("比亚迪最新成交额", True, "成交额-最新"),
            ("000001.SZ的成交额", True, "成交额-代码"),
        ]
        
        for query, expected_success, test_name in test_cases:
            self.test_query(query, expected_success, test_name, category)
    
    def test_valuation_queries(self):
        """3. 估值指标查询测试"""
        category = "估值指标查询"
        
        test_cases = [
            ("中国平安的市盈率", True, "PE-中文"),
            ("贵州茅台的PE", True, "PE-英文"),
            ("平安银行的市净率", True, "PB-中文"),
            ("比亚迪的PB", True, "PB-英文"),
            ("万科A的PE是多少", True, "PE-问句"),
            ("宁德时代市盈率多少", True, "PE-简化"),
        ]
        
        for query, expected_success, test_name in test_cases:
            self.test_query(query, expected_success, test_name, category)
    
    def test_kline_queries(self):
        """4. K线查询测试"""
        category = "K线查询"
        
        test_cases = [
            # 基础K线查询
            ("贵州茅台最近10天的K线", True, "最近N天"),
            ("中国平安最近20天的走势", True, "走势-最近N天"),
            ("万科A从2025-06-01到2025-06-30的K线", True, "日期范围"),
            ("宁德时代2025-06-01至2025-06-30的K线", True, "至连接符"),
            ("比亚迪2025-06-01-2025-06-30的K线", True, "-连接符"),
            ("平安银行2025/06/01~2025/06/30的K线", True, "~连接符"),
            
            # 月份年份查询
            ("贵州茅台6月的K线", True, "单月"),
            ("中国平安2024年的K线", True, "年份"),
            ("万科A2025年第二季度的走势", True, "季度"),
            
            # 相对时间
            ("贵州茅台本月的K线", True, "本月"),
            ("平安银行上个月的K线", True, "上个月"),
            ("比亚迪去年的K线", True, "去年"),
        ]
        
        for query, expected_success, test_name in test_cases:
            self.test_query(query, expected_success, test_name, category)
    
    def test_pct_chg_ranking_queries(self):
        """5. 涨跌幅排名测试"""
        category = "涨跌幅排名"
        
        test_cases = [
            ("今天涨幅最大的前10只股票", True, "涨幅前10"),
            ("今日跌幅最大的前10只股票", True, "跌幅前10"),
            ("涨幅排名", True, "涨幅默认"),
            ("跌幅排行", True, "跌幅默认"),
            ("涨幅前20", True, "涨幅前20"),
            ("跌幅前5", True, "跌幅前5"),
            ("昨天涨幅排名", True, "昨天涨幅"),
            ("涨幅TOP10", True, "TOP格式"),
        ]
        
        for query, expected_success, test_name in test_cases:
            self.test_query(query, expected_success, test_name, category)
    
    def test_market_cap_ranking_queries(self):
        """6. 市值排名测试"""
        category = "市值排名"
        
        test_cases = [
            ("市值排名前10", True, "市值前10"),
            ("总市值排名", True, "总市值默认"),
            ("流通市值排名前20", True, "流通市值前20"),
            ("市值TOP10", True, "TOP格式"),
            ("总市值最大的前20只股票", True, "总市值前20"),
            ("流通市值最大的前10只股票", True, "流通市值前10"),
            ("今天的市值排名", True, "今天市值"),
            ("最新市值排名", True, "最新市值"),
        ]
        
        for query, expected_success, test_name in test_cases:
            self.test_query(query, expected_success, test_name, category)
    
    def test_amount_ranking_queries(self):
        """7. 成交额排名测试"""
        category = "成交额排名"
        
        test_cases = [
            ("成交额排名前10", True, "成交额前10"),
            ("成交额排名", True, "成交额默认"),
            ("成交额TOP20", True, "TOP格式"),
            ("成交额最大的前15只股票", True, "成交额前15"),
            ("昨天成交额排名", True, "昨天成交额"),
            ("成交额排行前5", True, "成交额前5"),
        ]
        
        for query, expected_success, test_name in test_cases:
            self.test_query(query, expected_success, test_name, category)
    
    def test_money_flow_queries(self):
        """8. 主力资金查询测试"""
        category = "主力资金查询"
        
        test_cases = [
            # 个股主力资金
            ("贵州茅台的主力资金", True, "个股主力"),
            ("平安银行的主力资金", True, "个股主力2"),
            ("600519.SH的主力资金", True, "代码主力"),
            ("贵州茅台昨天的主力资金", True, "昨天主力"),
            
            # 板块主力资金
            ("银行板块的主力资金", True, "板块主力"),
            ("新能源板块的主力资金", True, "板块主力2"),
            ("白酒板块的主力资金", True, "板块主力3"),
            
            # 主力资金排名
            ("主力净流入排名前10", True, "主力流入前10"),
            ("主力净流出排名前10", True, "主力流出前10"),
            ("主力净流入排名", True, "主力流入默认"),
        ]
        
        for query, expected_success, test_name in test_cases:
            self.test_query(query, expected_success, test_name, category)
    
    def test_profit_queries(self):
        """9. 利润查询测试"""
        category = "利润查询"
        
        test_cases = [
            ("贵州茅台的利润", True, "利润-默认"),
            ("贵州茅台的净利润", True, "净利润"),
            ("万科A的营收", True, "营收"),
            ("中国平安的营业收入", True, "营业收入"),
            ("贵州茅台2024年的净利润", True, "年度净利润"),
            ("万科A最新的营收", True, "最新营收"),
            ("平安银行2024Q3的利润", True, "季度利润"),
        ]
        
        for query, expected_success, test_name in test_cases:
            self.test_query(query, expected_success, test_name, category)
    
    def test_financial_ranking_queries(self):
        """10. 财务排名测试"""
        category = "财务排名"
        
        test_cases = [
            ("PE排名前10", True, "PE排名"),
            ("PB排名", True, "PB默认"),
            ("净利润排名前20", True, "净利润排名"),
            ("营收排名", True, "营收默认"),
            ("ROE排名前10", True, "ROE排名"),
            ("PE最高的前10", True, "PE最高"),
            ("PB最低的前10", True, "PB最低"),
        ]
        
        for query, expected_success, test_name in test_cases:
            self.test_query(query, expected_success, test_name, category)
    
    def test_special_stock_names(self):
        """11. 特殊股票名称测试"""
        category = "特殊股票名称"
        
        test_cases = [
            # 英文+中文
            ("GQY视讯的股价", True, "GQY视讯"),
            ("TCL科技的PE", True, "TCL科技"),
            ("TCL智家的市值", True, "TCL智家"),
            
            # 数字名称
            ("三六零的股价", True, "三六零"),
            ("七一二的市值", True, "七一二"),
            
            # 特殊后缀
            ("埃夫特-U的股价", True, "-U后缀"),
            ("思特威-W的市值", True, "-W后缀"),
            ("奥比中光-UW的PE", True, "-UW后缀"),
            
            # ST股票
            ("ST葫芦娃的股价", True, "ST股票"),
            ("*ST国华的市值", True, "*ST股票"),
            
            # A/B后缀
            ("万科A的股价", True, "A后缀"),
            ("南玻A的市值", True, "A后缀2"),
            
            # 多股票查询
            ("比较TCL科技和TCL智家", True, "多TCL股票"),
            ("GQY视讯、七一二和大北农的对比", True, "混合特殊股票"),
        ]
        
        for query, expected_success, test_name in test_cases:
            self.test_query(query, expected_success, test_name, category)
    
    def test_parameter_extraction_edge_cases(self):
        """12. 参数提取边界测试"""
        category = "参数提取边界"
        
        test_cases = [
            # 日期边界
            ("贵州茅台最后的股价", True, "最后的"),
            ("平安银行3年前的股价", True, "N年前"),
            ("万科A最近的公告", True, "最近的"),
            
            # 数量边界
            ("前五的股票", True, "中文数字-五"),
            ("前二十名", True, "中文数字-二十"),
            ("前一百只股票", True, "中文数字-一百"),
            
            # 复杂组合
            ("比较贵州茅台、五粮液和泸州老窖最近30天的走势", True, "多股票+日期范围"),
            ("银行板块2024年年报净利润排名前20", True, "板块+报告期+排名"),
            ("排除ST和北交所的市值排名前50", True, "排除条件+排名"),
        ]
        
        for query, expected_success, test_name in test_cases:
            self.test_query(query, expected_success, test_name, category)
    
    def test_error_handling(self):
        """13. 错误处理测试"""
        category = "错误处理"
        
        test_cases = [
            # 股票错误
            ("茅台最新股价", False, "股票简称"),
            ("平安最新股价", False, "歧义股票"),
            ("999999的股价", False, "不存在股票"),
            ("600519.sh的股价", False, "小写后缀"),
            
            # 日期错误
            ("贵州茅台2025-06-31的股价", False, "无效日期"),
            ("中国平安2099年的股价", False, "未来日期"),
            
            # 空查询
            ("", False, "空查询"),
            ("   ", False, "空白查询"),
            
            # 板块错误
            ("银行的主力资金", False, "缺少板块后缀"),
            ("新能源主力资金", False, "缺少板块后缀2"),
        ]
        
        for query, expected_success, test_name in test_cases:
            self.test_query(query, expected_success, test_name, category)
    
    def generate_report(self):
        """生成测试报告"""
        print("\n" + "="*80)
        print("测试报告汇总")
        print("="*80)
        print(f"总测试数: {self.test_results['total']}")
        print(f"通过数量: {self.test_results['passed']}")
        print(f"失败数量: {self.test_results['failed']}")
        print(f"通过率: {self.test_results['passed'] / self.test_results['total'] * 100:.1f}%")
        
        # 分类统计
        print("\n" + "="*80)
        print("分类统计")
        print("="*80)
        print(f"{'类别':<20} {'总数':>6} {'通过':>6} {'失败':>6} {'通过率':>8}")
        print("-"*52)
        
        for category, stats in sorted(self.test_results['summary_by_category'].items()):
            pass_rate = stats['passed'] / stats['total'] * 100 if stats['total'] > 0 else 0
            print(f"{category:<20} {stats['total']:>6} {stats['passed']:>6} "
                  f"{stats['failed']:>6} {pass_rate:>7.1f}%")
        
        # 失败详情
        if self.test_results['errors']:
            print("\n" + "="*80)
            print("失败测试详情 (前20个)")
            print("="*80)
            for i, error in enumerate(self.test_results['errors'][:20], 1):
                print(f"\n[{i}] 类别: {error['category']}")
                print(f"    测试: {error['test_name']}")
                print(f"    查询: {error['query']}")
                print(f"    错误: {error['error']}")
        
        # 性能统计
        print("\n" + "="*80)
        print("性能统计")
        print("="*80)
        
        elapsed_times = [d['elapsed_time'] for d in self.test_results['details']]
        if elapsed_times:
            print(f"平均耗时: {sum(elapsed_times) / len(elapsed_times):.2f}秒")
            print(f"最快耗时: {min(elapsed_times):.2f}秒")
            print(f"最慢耗时: {max(elapsed_times):.2f}秒")
            
            # 统计快速查询
            quick_count = sum(1 for t in elapsed_times if t < 0.5)
            print(f"快速查询(<0.5秒): {quick_count}/{len(elapsed_times)} "
                  f"({quick_count/len(elapsed_times)*100:.1f}%)")
        
        # 保存详细报告
        report_file = f"test_report_full_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(self.test_results, f, ensure_ascii=False, indent=2)
        print(f"\n详细报告已保存到: {report_file}")


if __name__ == "__main__":
    tester = SQLAgentFullTest()
    tester.run_all_tests()