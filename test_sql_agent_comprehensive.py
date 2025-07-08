#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SQL Agent模块化版本综合测试脚本
基于test-guide-comprehensive.md v5.3的所有SQL Agent测试用例
"""

import sys
import os
import time
import json
from datetime import datetime
from typing import Dict, List, Tuple, Any

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.sql_agent_modular import SQLAgentModular

class ComprehensiveTest:
    """综合测试类"""
    
    def __init__(self):
        self.agent = SQLAgentModular()
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
        print("SQL Agent 模块化版本综合测试")
        print("基于 test-guide-comprehensive.md v5.3")
        print(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*80)
        
        # 1.1 股价查询模板测试
        self.test_stock_price_queries()
        
        # 1.2 成交量查询模板测试
        self.test_volume_queries()
        
        # 1.3 估值指标查询模板测试
        self.test_valuation_queries()
        
        # 1.4 K线查询模板测试
        self.test_kline_queries()
        
        # 1.5 涨跌幅排名模板测试
        self.test_pct_chg_ranking_queries()
        
        # 1.6 市值排名模板测试
        self.test_market_cap_ranking_queries()
        
        # 1.7 成交额排名模板测试
        self.test_amount_ranking_queries()
        
        # 1.8 成交量排名模板测试
        self.test_volume_ranking_queries()
        
        # 1.9 主力净流入/流出排名模板测试
        self.test_money_flow_ranking_queries()
        
        # 1.10 个股主力资金查询模板测试
        self.test_stock_money_flow_queries()
        
        # 1.11 板块主力资金查询模板测试
        self.test_sector_money_flow_queries()
        
        # 1.12 利润查询模板测试
        self.test_profit_queries()
        
        # 1.13 PE排名模板测试
        self.test_pe_ranking_queries()
        
        # 生成测试报告
        self.generate_report()
    
    def test_stock_price_queries(self):
        """1.1 股价查询模板测试"""
        category = "1.1 股价查询"
        
        # 正常用例
        normal_cases = [
            ("贵州茅台最新股价", "基础查询-最新"),
            ("贵州茅台20250627的股价", "指定日期"),
            ("平安银行昨天的股价", "相对日期-昨天"),
            ("600519.SH最新股价", "股票代码查询"),
            ("贵州茅台2025-06-27的股价", "日期格式变体"),
            ("000001.SZ的股价", "深市股票代码"),
        ]
        
        for query, test_name in normal_cases:
            self.test_query(query, True, test_name, category)
        
        # 边界测试
        boundary_cases = [
            ("贵州茅台2025年06月27日的股价", "中文日期格式"),
            ("600519最新股价", "无后缀股票代码"),
            ("贵州茅台前天的股价", "相对日期-前天"),
            ("贵州茅台上个交易日的股价", "相对日期-上个交易日"),
        ]
        
        for query, test_name in boundary_cases:
            self.test_query(query, True, test_name, f"{category}-边界测试")
        
        # 错误用例
        error_cases = [
            ("茅台最新股价", "股票简称错误"),
            ("平安最新股价", "歧义股票名称"),
            ("123456最新股价", "不存在的股票代码"),
            ("贵州茅台2025-06-31的股价", "无效日期"),
            ("600519.sh最新股价", "小写后缀错误"),
            ("", "空字符串查询"),
        ]
        
        for query, test_name in error_cases:
            self.test_query(query, False, test_name, f"{category}-错误用例")
    
    def test_volume_queries(self):
        """1.2 成交量查询模板测试"""
        category = "1.2 成交量查询"
        
        # 成交量正常用例
        volume_cases = [
            ("平安银行昨天的成交量", "成交量-昨天"),
            ("贵州茅台最新成交量", "成交量-最新"),
            ("万科A的成交量", "成交量-默认"),
            ("600519.SH今天的成交量", "成交量-今天"),
        ]
        
        for query, test_name in volume_cases:
            self.test_query(query, True, test_name, category)
        
        # 成交额正常用例
        amount_cases = [
            ("中国平安的成交额", "成交额-默认"),
            ("宁德时代昨天的成交额", "成交额-昨天"),
            ("比亚迪最新成交额", "成交额-最新"),
            ("000001.SZ的成交额", "成交额-股票代码"),
        ]
        
        for query, test_name in amount_cases:
            self.test_query(query, True, test_name, category)
        
        # 边界测试（v2.1.17重点）
        boundary_cases = [
            ("万科A前天的成交量", "股票名称清理测试"),
            ("中国平安昨天的成交额", "日期替换不影响股票提取"),
            ("贵州茅台最近5天的成交量", "日期替换后的股票提取"),
            ("宁德时代今天的成交额", "今天替换测试"),
            ("比亚迪上个交易日的成交量", "上个交易日"),
        ]
        
        for query, test_name in boundary_cases:
            self.test_query(query, True, test_name, f"{category}-边界测试")
        
        # 错误用例
        error_cases = [
            ("茅台的成交量", "股票简称错误"),
            ("不存在股票的成交量", "不存在的股票"),
            ("贵州茅台2099年的成交量", "未来日期"),
        ]
        
        for query, test_name in error_cases:
            self.test_query(query, False, test_name, f"{category}-错误用例")
    
    def test_valuation_queries(self):
        """1.3 估值指标查询模板测试"""
        category = "1.3 估值指标查询"
        
        cases = [
            ("中国平安的市盈率", "市盈率查询"),
            ("贵州茅台的PE", "PE查询"),
            ("平安银行的市净率", "市净率查询"),
            ("比亚迪的PB", "PB查询"),
        ]
        
        for query, test_name in cases:
            self.test_query(query, True, test_name, category)
    
    def test_kline_queries(self):
        """1.4 K线查询模板测试"""
        category = "1.4 K线查询"
        
        # 正常用例
        normal_cases = [
            ("中国平安最近10天的K线", "最近N天"),
            ("宁德时代从2025/06/01到2025/06/30的K线", "日期范围"),
            ("宁德时代从6月1日到6月30日的K线", "中文日期"),
            ("贵州茅台最近30天的走势", "走势查询"),
            ("贵州茅台的K线", "无时间范围-默认90天"),
        ]
        
        for query, test_name in normal_cases:
            self.test_query(query, True, test_name, category)
        
        # 边界测试（v2.1.17新增）
        boundary_cases = [
            ("贵州茅台2025-06-01至2025-06-30的K线", "至连接符"),
            ("万科A2025-06-01到2025-06-30的K线", "到连接符"),
            ("中国平安2025-06-01-2025-06-30的K线", "-连接符"),
            ("比亚迪2025/6/1~2025/6/30的K线", "~连接符"),
            ("万科A6月的K线", "月份转换"),
            ("中国平安2024年的K线", "年份转换"),
            ("宁德时代2025年第二季度的走势", "季度转换"),
            ("贵州茅台本月的K线", "相对月份"),
            ("平安银行上个月的K线", "上个月"),
            ("比亚迪去年的K线", "去年"),
            ("贵州茅台最近二十天的K线", "中文数字-二十"),
            ("中国平安前十天的走势", "中文数字-十"),
            ("万科A最近一百天的K线", "中文数字-一百"),
        ]
        
        for query, test_name in boundary_cases:
            self.test_query(query, True, test_name, f"{category}-边界测试")
        
        # 错误用例
        error_cases = [
            ("K线", "无股票名称"),
            ("茅台的K线", "股票简称"),
            ("不存在股票的K线", "不存在的股票"),
            ("贵州茅台13月的K线", "无效月份"),
            ("中国平安2025年第五季度的K线", "无效季度"),
        ]
        
        for query, test_name in error_cases:
            self.test_query(query, False, test_name, f"{category}-错误用例")
    
    def test_pct_chg_ranking_queries(self):
        """1.5 涨跌幅排名模板测试"""
        category = "1.5 涨跌幅排名"
        
        # 正常用例
        normal_cases = [
            ("今天涨幅最大的前10只股票", "涨幅前10"),
            ("今日跌幅最大的前10只股票", "跌幅前10"),
            ("20250627涨幅前10", "指定日期涨幅"),
            ("涨幅排名", "默认涨幅排名"),
            ("跌幅最大的股票", "跌幅最大"),
        ]
        
        for query, test_name in normal_cases:
            self.test_query(query, True, test_name, category)
        
        # 边界测试
        boundary_cases = [
            ("涨幅前二十", "中文数字-二十"),
            ("跌幅最大的前五只股票", "中文数字-五"),
            ("涨幅前一百名", "中文数字-一百"),
            ("昨天涨幅排名", "昨天涨幅"),
            ("2025-06-27跌幅排名", "指定日期跌幅"),
            ("上个交易日涨幅前10", "上个交易日"),
        ]
        
        for query, test_name in boundary_cases:
            self.test_query(query, True, test_name, f"{category}-边界测试")
        
        # 错误用例
        error_cases = [
            ("贵州茅台涨幅排名", "个股涨幅排名"),
            ("涨幅前0只股票", "无效数量-0"),
            ("涨幅前1000只股票", "数量过大"),
        ]
        
        for query, test_name in error_cases:
            self.test_query(query, False, test_name, f"{category}-错误用例")
    
    def test_market_cap_ranking_queries(self):
        """1.6 市值排名模板测试"""
        category = "1.6 市值排名"
        
        # 传统格式
        traditional_cases = [
            ("总市值最大的前20只股票", "总市值前20"),
            ("流通市值最大的前10只股票", "流通市值前10"),
            ("市值排名前50", "市值前50"),
            ("市值前20名", "市值前20名"),
        ]
        
        for query, test_name in traditional_cases:
            self.test_query(query, True, test_name, category)
        
        # 无数字默认前10
        default_cases = [
            ("总市值排名", "总市值默认"),
            ("市值排名", "市值默认"),
            ("流通市值排名", "流通市值默认"),
            ("市值排行", "市值排行默认"),
        ]
        
        for query, test_name in default_cases:
            self.test_query(query, True, test_name, f"{category}-默认前10")
        
        # TOP格式
        top_cases = [
            ("市值TOP10", "TOP10格式"),
            ("总市值TOP20", "总市值TOP20"),
            ("流通市值TOP5", "流通市值TOP5"),
            ("A股市值TOP15", "A股市值TOP15"),
        ]
        
        for query, test_name in top_cases:
            self.test_query(query, True, test_name, f"{category}-TOP格式")
        
        # 时间+排名
        time_cases = [
            ("今天的市值排名", "今天市值"),
            ("最新市值排名", "最新市值"),
            ("昨天流通市值排名", "昨天流通市值"),
            ("2025-07-01市值排名", "指定日期市值"),
        ]
        
        for query, test_name in time_cases:
            self.test_query(query, True, test_name, f"{category}-时间指定")
    
    def test_amount_ranking_queries(self):
        """1.7 成交额排名模板测试"""
        category = "1.7 成交额排名"
        
        # 传统格式
        traditional_cases = [
            ("成交额最大的前10只股票", "成交额前10"),
            ("成交额排名前20", "成交额前20"),
            ("成交额前15", "成交额前15"),
            ("昨天成交额最大的前15只股票", "昨天成交额前15"),
        ]
        
        for query, test_name in traditional_cases:
            self.test_query(query, True, test_name, category)
        
        # 无数字默认前10
        default_cases = [
            ("成交额排名", "成交额默认"),
            ("成交额排行", "成交额排行默认"),
            ("A股成交额排名", "A股成交额默认"),
        ]
        
        for query, test_name in default_cases:
            self.test_query(query, True, test_name, f"{category}-默认前10")
        
        # TOP格式
        top_cases = [
            ("成交额TOP10", "成交额TOP10"),
            ("成交额TOP20", "成交额TOP20"),
            ("成交额TOP5", "成交额TOP5"),
        ]
        
        for query, test_name in top_cases:
            self.test_query(query, True, test_name, f"{category}-TOP格式")
    
    def test_volume_ranking_queries(self):
        """1.8 成交量排名模板测试"""
        category = "1.8 成交量排名"
        
        # 传统格式
        traditional_cases = [
            ("成交量最大的前10只股票", "成交量前10"),
            ("成交量排名前20", "成交量前20"),
            ("成交量前15", "成交量前15"),
            ("昨天成交量最大的前15只股票", "昨天成交量前15"),
        ]
        
        for query, test_name in traditional_cases:
            self.test_query(query, True, test_name, category)
        
        # 与个股查询的区分
        distinction_cases = [
            ("贵州茅台的成交量", "个股成交量查询"),  # 应该成功
            ("成交量排名", "成交量排名查询"),
            ("平安银行成交量", "个股成交量"),  # 应该成功
            ("成交量TOP10", "成交量TOP排名"),
        ]
        
        for query, test_name in distinction_cases:
# 修正逻辑：排名查询和个股查询都应该成功
            if "排名" in query or "TOP" in query:
                expected_success = True  # 排名查询
            else:
                expected_success = True  # 个股查询也应该成功
            self.test_query(query, expected_success, test_name, f"{category}-区分测试")
    
    def test_money_flow_ranking_queries(self):
        """1.9 主力净流入/流出排名模板测试"""
        category = "1.9 主力资金排名"
        
        # 传统格式
        traditional_cases = [
            ("主力净流入最多的前10只股票", "主力流入前10"),
            ("主力净流出最多的前10只股票", "主力流出前10"),
            ("主力净流入排名前20", "主力流入前20"),
            ("主力净流出排名前15", "主力流出前15"),
        ]
        
        for query, test_name in traditional_cases:
            self.test_query(query, True, test_name, category)
        
        # 无数字默认前10
        default_cases = [
            ("主力净流入排名", "主力流入默认"),
            ("主力净流入排行", "主力流入排行默认"),
            ("主力净流出排名", "主力流出默认"),
            ("主力净流出排行", "主力流出排行默认"),
        ]
        
        for query, test_name in default_cases:
            self.test_query(query, True, test_name, f"{category}-默认前10")
        
        # 错误用例（非标准术语）
        error_cases = [
            ("机构资金流入排名", "非标准术语-机构"),
            ("大资金流入排行", "非标准术语-大资金"),
        ]
        
        for query, test_name in error_cases:
            self.test_query(query, False, test_name, f"{category}-错误用例")
    
    def test_stock_money_flow_queries(self):
        """1.10 个股主力资金查询模板测试"""
        category = "1.10 个股主力资金"
        
        # 标准表达
        standard_cases = [
            ("贵州茅台的主力资金", "贵州茅台主力"),
            ("平安银行的主力资金", "平安银行主力"),
            ("600519.SH的主力资金", "股票代码主力"),
            ("比亚迪的主力资金", "比亚迪主力"),
            ("万科A的主力资金", "万科A主力"),
        ]
        
        for query, test_name in standard_cases:
            self.test_query(query, True, test_name, category)
        
        # 时间指定
        time_cases = [
            ("贵州茅台昨天的主力资金", "昨天主力"),
            ("平安银行2025-07-01的主力资金", "指定日期主力"),
            ("万科A今天的主力资金", "今天主力"),
        ]
        
        for query, test_name in time_cases:
            self.test_query(query, True, test_name, f"{category}-时间指定")
        
        # 错误用例
        error_cases = [
            ("贵州茅台的机构资金", "非标准术语-机构"),
            ("平安银行的大资金流入", "非标准术语-大资金"),
            ("万科A的游资", "不支持的资金类型"),
            ("茅台的主力资金", "股票简称错误"),
            ("平安的主力资金", "歧义股票名称"),
        ]
        
        for query, test_name in error_cases:
            self.test_query(query, False, test_name, f"{category}-错误用例")
    
    def test_sector_money_flow_queries(self):
        """1.11 板块主力资金查询模板测试"""
        category = "1.11 板块主力资金"
        
        # 标准表达
        standard_cases = [
            ("银行板块的主力资金", "银行板块"),
            ("新能源板块的主力资金", "新能源板块"),
            ("白酒板块的主力资金", "白酒板块"),
            ("房地产板块的主力资金", "房地产板块"),
            ("证券板块的主力资金", "证券板块"),
        ]
        
        for query, test_name in standard_cases:
            self.test_query(query, True, test_name, category)
        
        # 时间指定
        time_cases = [
            ("银行板块昨天的主力资金", "银行板块昨天"),
            ("新能源板块2025-07-01的主力资金", "新能源板块指定日期"),
            ("白酒板块今天的主力资金", "白酒板块今天"),
        ]
        
        for query, test_name in time_cases:
            self.test_query(query, True, test_name, f"{category}-时间指定")
        
        # 错误用例
        error_cases = [
            ("银行的主力资金", "缺少板块后缀"),
            ("新能源主力资金", "缺少板块后缀"),
            ("白酒主力净流入", "缺少板块后缀"),
            ("银行板块的机构资金", "非标准术语"),
            ("新能源板块的大资金", "非标准术语"),
        ]
        
        for query, test_name in error_cases:
            self.test_query(query, False, test_name, f"{category}-错误用例")
    
    def test_profit_queries(self):
        """1.12 利润查询模板测试"""
        category = "1.12 利润查询"
        
        # 基础查询
        basic_cases = [
            ("贵州茅台的利润", "贵州茅台利润"),
            ("贵州茅台的净利润", "贵州茅台净利润"),
            ("万科A的营收", "万科A营收"),
            ("中国平安的营业收入", "中国平安营业收入"),
            ("宁德时代的净利润", "宁德时代净利润"),
        ]
        
        for query, test_name in basic_cases:
            self.test_query(query, True, test_name, category)
        
        # 带时间参数
        time_cases = [
            ("贵州茅台2024年的净利润", "2024年净利润"),
            ("万科A最新的营收", "最新营收"),
            ("平安银行2024Q3的利润", "2024Q3利润"),
            ("宁德时代2024年第三季度的营业收入", "2024第三季度营收"),
        ]
        
        for query, test_name in time_cases:
            self.test_query(query, True, test_name, f"{category}-时间指定")
        
        # 其他表达方式
        other_cases = [
            ("茅台赚了多少钱", False, "赚钱表达-简称错误"),
            ("万科盈利情况", False, "盈利情况-简称错误"),
            ("中国平安收入是多少", True, "收入表达-正常"),
        ]
        
        for query, expected, test_name in other_cases:
            self.test_query(query, expected, test_name, f"{category}-其他表达")
        
        # 错误用例
        error_cases = [
            ("茅台的利润", "股票简称错误"),
            ("平安的营收", "歧义股票名称"),
        ]
        
        for query, test_name in error_cases:
            self.test_query(query, False, test_name, f"{category}-错误用例")
    
    def test_pe_ranking_queries(self):
        """1.13 PE排名模板测试"""
        category = "1.13 PE排名"
        
        # 传统格式
        traditional_cases = [
            ("PE最高的前10", "PE最高前10"),
            ("市盈率排名前20", "市盈率前20"),
            ("PE最低的前10", "PE最低前10"),
            ("市盈率最高的前5", "市盈率最高前5"),
        ]
        
        for query, test_name in traditional_cases:
            self.test_query(query, True, test_name, category)
        
        # 无数字默认前10
        default_cases = [
            ("PE排名", "PE默认排名"),
            ("市盈率排名", "市盈率默认排名"),
            ("PE排行", "PE默认排行"),
        ]
        
        for query, test_name in default_cases:
            self.test_query(query, True, test_name, f"{category}-默认前10")
    
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
        report_file = f"test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
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