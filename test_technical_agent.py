#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Technical Analysis Agent 测试脚本
测试技术指标查询和分析功能
"""

import asyncio
import json
import time
from datetime import datetime
from typing import List, Dict, Tuple

from agents.technical_agent_modular import TechnicalAgentModular
from utils.logger import setup_logger

# 设置日志
logger = setup_logger('test_technical_agent', 'logs/test_technical_agent.log')


class TechnicalAgentTester:
    """Technical Agent测试器"""
    
    def __init__(self):
        self.agent = TechnicalAgentModular()
        self.test_results = []
        self.passed = 0
        self.failed = 0
        self.total_time = 0
    
    async def run_all_tests(self):
        """运行所有测试"""
        print("=" * 80)
        print("Technical Analysis Agent 测试")
        print("=" * 80)
        
        start_time = time.time()
        
        # 运行各类测试
        await self.test_ma_queries()
        await self.test_macd_queries()
        await self.test_kdj_queries()
        await self.test_rsi_queries()
        await self.test_boll_queries()
        await self.test_cross_signals()
        await self.test_complex_analysis()
        await self.test_error_cases()
        
        self.total_time = time.time() - start_time
        
        # 显示测试报告
        self.show_test_report()
    
    async def test_ma_queries(self):
        """测试均线查询"""
        print("\n1. 测试均线查询")
        print("-" * 40)
        
        test_cases = [
            ("贵州茅台的5日均线", True, "MA5"),
            ("宁德时代的20日均线", True, "MA20"),
            ("比亚迪的60日均线", True, "MA60"),
            ("万科A的均线", True, "均线"),
            ("查看贵州茅台的250日均线", True, "MA250"),
        ]
        
        for query, expected_success, check_content in test_cases:
            await self._run_single_test(query, expected_success, check_content)
    
    async def test_macd_queries(self):
        """测试MACD查询"""
        print("\n2. 测试MACD查询")
        print("-" * 40)
        
        test_cases = [
            ("贵州茅台的MACD", True, "MACD"),
            ("宁德时代的MACD金叉", True, "MACD"),
            ("比亚迪最近有MACD死叉吗", True, "MACD"),
            ("查看茅台的MACD指标", True, "DIF"),
        ]
        
        for query, expected_success, check_content in test_cases:
            await self._run_single_test(query, expected_success, check_content)
    
    async def test_kdj_queries(self):
        """测试KDJ查询"""
        print("\n3. 测试KDJ查询")
        print("-" * 40)
        
        test_cases = [
            ("贵州茅台的KDJ", True, "KDJ"),
            ("宁德时代的KDJ指标", True, "K值"),
            ("比亚迪KDJ超买了吗", True, "J值"),
            ("万科A的KDJ是否超卖", True, "KDJ"),
        ]
        
        for query, expected_success, check_content in test_cases:
            await self._run_single_test(query, expected_success, check_content)
    
    async def test_rsi_queries(self):
        """测试RSI查询"""
        print("\n4. 测试RSI查询")
        print("-" * 40)
        
        test_cases = [
            ("贵州茅台的RSI", True, "RSI"),
            ("宁德时代RSI超买了吗", True, "RSI"),
            ("比亚迪的RSI指标", True, "RSI(6)"),
            ("查看茅台是否RSI超卖", True, "RSI"),
        ]
        
        for query, expected_success, check_content in test_cases:
            await self._run_single_test(query, expected_success, check_content)
    
    async def test_boll_queries(self):
        """测试布林带查询"""
        print("\n5. 测试布林带查询")
        print("-" * 40)
        
        test_cases = [
            ("贵州茅台的布林带", True, "布林带"),
            ("宁德时代的BOLL", True, "上轨"),
            ("比亚迪的布林线", True, "中轨"),
            ("茅台突破布林带上轨了吗", True, "布林带"),
        ]
        
        for query, expected_success, check_content in test_cases:
            await self._run_single_test(query, expected_success, check_content)
    
    async def test_cross_signals(self):
        """测试交叉信号查询"""
        print("\n6. 测试交叉信号查询")
        print("-" * 40)
        
        test_cases = [
            ("贵州茅台的金叉", True, "交叉信号"),
            ("宁德时代最近的死叉", True, "信号"),
            ("比亚迪的交叉信号", True, "MA信号"),
        ]
        
        for query, expected_success, check_content in test_cases:
            await self._run_single_test(query, expected_success, check_content)
    
    async def test_complex_analysis(self):
        """测试复杂技术分析"""
        print("\n7. 测试复杂技术分析")
        print("-" * 40)
        
        test_cases = [
            ("分析贵州茅台的技术趋势", True, "技术面"),
            ("判断宁德时代的技术形态", True, "技术指标"),
            ("贵州茅台的技术分析", True, "趋势"),
            ("比亚迪值得买入吗从技术面看", True, "技术"),
        ]
        
        for query, expected_success, check_content in test_cases:
            await self._run_single_test(query, expected_success, check_content)
    
    async def test_error_cases(self):
        """测试错误处理"""
        print("\n8. 测试错误处理")
        print("-" * 40)
        
        test_cases = [
            ("茅台的KDJ", False, "完整公司名称"),  # 股票简称
            ("不存在的股票的MACD", False, "股票"),
            ("", False, "查询"),  # 空查询
            ("600519.sh的RSI", False, "大写"),  # 小写后缀
        ]
        
        for query, expected_success, check_content in test_cases:
            await self._run_single_test(query, expected_success, check_content)
    
    async def _run_single_test(
        self, 
        query: str, 
        expected_success: bool,
        check_content: str
    ):
        """运行单个测试"""
        start_time = time.time()
        
        try:
            result = await self.agent.process_query(query)
            elapsed_time = time.time() - start_time
            
            # 判断测试结果
            if expected_success:
                if result.success and check_content in str(result.data):
                    self._record_success(query, elapsed_time, result.data)
                else:
                    self._record_failure(
                        query, 
                        f"期望成功但失败或未包含'{check_content}'",
                        result.error if not result.success else "内容不匹配"
                    )
            else:
                if not result.success:
                    self._record_success(query, elapsed_time, f"正确拒绝: {result.error}")
                else:
                    self._record_failure(query, "期望失败但成功", result.data)
                    
        except Exception as e:
            self._record_failure(query, "异常", str(e))
    
    def _record_success(self, query: str, time_taken: float, result: str):
        """记录成功的测试"""
        self.passed += 1
        self.test_results.append({
            'query': query,
            'status': 'PASS',
            'time': time_taken,
            'result': result[:100] + '...' if len(str(result)) > 100 else result
        })
        print(f"✓ {query} ({time_taken:.2f}s)")
    
    def _record_failure(self, query: str, reason: str, details: str):
        """记录失败的测试"""
        self.failed += 1
        self.test_results.append({
            'query': query,
            'status': 'FAIL',
            'reason': reason,
            'details': details
        })
        print(f"✗ {query} - {reason}")
    
    def show_test_report(self):
        """显示测试报告"""
        print("\n" + "=" * 80)
        print("测试报告")
        print("=" * 80)
        
        total_tests = self.passed + self.failed
        pass_rate = (self.passed / total_tests * 100) if total_tests > 0 else 0
        
        print(f"\n总测试数: {total_tests}")
        print(f"通过: {self.passed} ({pass_rate:.1f}%)")
        print(f"失败: {self.failed}")
        print(f"总耗时: {self.total_time:.2f}秒")
        print(f"平均响应时间: {self.total_time/total_tests:.2f}秒")
        
        # 显示失败的测试
        if self.failed > 0:
            print("\n失败的测试:")
            print("-" * 40)
            for result in self.test_results:
                if result['status'] == 'FAIL':
                    print(f"- {result['query']}")
                    print(f"  原因: {result['reason']}")
                    print(f"  详情: {result['details'][:100]}...")
        
        # 保存详细报告
        self._save_detailed_report()
    
    def _save_detailed_report(self):
        """保存详细测试报告"""
        report = {
            'test_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'summary': {
                'total': self.passed + self.failed,
                'passed': self.passed,
                'failed': self.failed,
                'pass_rate': f"{(self.passed/(self.passed+self.failed)*100):.1f}%",
                'total_time': f"{self.total_time:.2f}s"
            },
            'details': self.test_results
        }
        
        filename = f"test_results/technical_agent_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        print(f"\n详细报告已保存至: {filename}")


async def main():
    """主函数"""
    tester = TechnicalAgentTester()
    await tester.run_all_tests()


if __name__ == "__main__":
    # 注意：需要先创建tu_technical_indicators表并导入数据
    print("注意：运行此测试前，请确保：")
    print("1. 已创建tu_technical_indicators表")
    print("2. 已导入技术指标数据")
    print("3. 数据库连接正常")
    print()
    
    asyncio.run(main())