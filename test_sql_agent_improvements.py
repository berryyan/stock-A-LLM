#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
SQL Agent 快速模板改进测试脚本
测试日期智能解析集成和快速模板功能

注意事项：
1. 坚持中文思考和输出
2. 不因测试用例修改原本的程序设计
3. 测试用例坚持原设计初衷
4. 测试超时时间设置为5分钟
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import time
import json
from datetime import datetime
from typing import Dict, List, Any
from agents.sql_agent import SQLAgent
from utils.logger import setup_logger

# 设置日志
logger = setup_logger("test_sql_improvements")

class SQLAgentImprovementTester:
    """SQL Agent改进测试器"""
    
    def __init__(self):
        self.sql_agent = SQLAgent()
        self.test_results = []
        self.start_time = None
        
    def run_single_test(self, test_case: Dict[str, Any]) -> Dict[str, Any]:
        """运行单个测试用例"""
        query = test_case['query']
        expected_type = test_case.get('expected_type')
        should_prompt_full_name = test_case.get('should_prompt_full_name', False)
        
        logger.info(f"\n{'='*60}")
        logger.info(f"测试查询: {query}")
        logger.info(f"预期类型: {expected_type}")
        logger.info(f"预期提示完整名称: {should_prompt_full_name}")
        
        start_time = time.time()
        
        try:
            # 执行查询
            result = self.sql_agent.query(query)
            elapsed_time = time.time() - start_time
            
            # 分析结果
            test_result = {
                'query': query,
                'success': result.get('success', False),
                'elapsed_time': elapsed_time,
                'expected_type': expected_type,
                'actual_type': None,
                'result': result
            }
            
            # 检查是否使用了快速模板
            if result.get('success'):
                # 从结果中判断是否使用了快速模板
                if result.get('quick_path', False):
                    test_result['used_quick_template'] = True
                else:
                    test_result['used_quick_template'] = False
                    
                # 检查是否有SQL语句（快速模板会返回sql字段）
                if result.get('sql'):
                    test_result['has_sql'] = True
                    
            # 检查股票简称提示
            if should_prompt_full_name:
                if result.get('error') and ('请使用完整' in result['error'] or '股票名称' in result['error']):
                    test_result['prompted_full_name'] = True
                    test_result['success'] = True  # 这是预期的错误
                else:
                    test_result['prompted_full_name'] = False
                    
            logger.info(f"测试结果: {'成功' if test_result['success'] else '失败'}")
            logger.info(f"执行时间: {elapsed_time:.2f}秒")
            
            if result.get('result'):
                logger.info(f"返回结果示例: {str(result['result'])[:200]}...")
            elif result.get('error'):
                logger.info(f"错误信息: {result['error']}")
                
            return test_result
            
        except Exception as e:
            logger.error(f"测试出错: {str(e)}")
            return {
                'query': query,
                'success': False,
                'error': str(e),
                'elapsed_time': time.time() - start_time
            }
    
    def run_all_tests(self):
        """运行所有测试用例"""
        self.start_time = time.time()
        
        # 定义测试用例
        test_cases = [
            # === 股价查询测试（支持历史日期） ===
            {
                'query': '贵州茅台最新股价',
                'expected_type': 'price_query',
                'category': '股价查询'
            },
            {
                'query': '贵州茅台20250627的股价',
                'expected_type': 'price_query',
                'category': '股价查询'
            },
            {
                'query': '平安银行2025-06-27的股价',
                'expected_type': 'price_query',
                'category': '股价查询'
            },
            {
                'query': '中国平安2025年06月27日的股价',
                'expected_type': 'price_query',
                'category': '股价查询'
            },
            {
                'query': '格力电器昨天的股价',
                'expected_type': 'price_query',
                'category': '股价查询'
            },
            {
                'query': '万科A上个交易日的股价',
                'expected_type': 'price_query',
                'category': '股价查询'
            },
            
            # === K线查询测试（支持时间段） ===
            {
                'query': '贵州茅台最近30天K线',
                'expected_type': 'kline_query',
                'category': 'K线查询'
            },
            {
                'query': '平安银行从2025-06-01到2025-06-27的K线',
                'expected_type': 'kline_query',
                'category': 'K线查询'
            },
            {
                'query': '中国平安过去5天的走势',
                'expected_type': 'kline_query',
                'category': 'K线查询'
            },
            
            # === 成交量查询测试 ===
            {
                'query': '贵州茅台最新成交量',
                'expected_type': 'volume_query',
                'category': '成交量查询'
            },
            {
                'query': '平安银行昨天的成交量',
                'expected_type': 'volume_query',
                'category': '成交量查询'
            },
            {
                'query': '中国平安20250627的成交额',
                'expected_type': 'volume_query',
                'category': '成交量查询'
            },
            
            # === 利润查询测试 ===
            {
                'query': '贵州茅台的净利润',
                'expected_type': 'profit_query',
                'category': '利润查询'
            },
            {
                'query': '平安银行的营业收入',
                'expected_type': 'profit_query',
                'category': '利润查询'
            },
            
            # === 估值指标查询测试（支持历史日期） ===
            {
                'query': '中国平安最新PE',
                'expected_type': 'valuation_query',
                'category': '估值查询'
            },
            {
                'query': '贵州茅台昨天的市盈率',
                'expected_type': 'valuation_query',
                'category': '估值查询'
            },
            {
                'query': '平安银行20250627的市净率',
                'expected_type': 'valuation_query',
                'category': '估值查询'
            },
            
            # === 排名查询测试（支持历史日期） ===
            {
                'query': '今天涨幅前10',
                'expected_type': 'ranking_query',
                'category': '涨跌幅排名'
            },
            {
                'query': '20250627涨幅前10',
                'expected_type': 'ranking_query',
                'category': '涨跌幅排名'
            },
            {
                'query': '昨天跌幅最大的20只股票',
                'expected_type': 'ranking_query',
                'category': '涨跌幅排名'
            },
            {
                'query': '上个交易日总市值排名前10',
                'expected_type': 'ranking_query',
                'category': '市值排名'
            },
            {
                'query': '昨天流通市值前10',
                'expected_type': 'ranking_query',
                'category': '市值排名'
            },
            {
                'query': '20250627市值最大的前20只股票',
                'expected_type': 'ranking_query',
                'category': '市值排名'
            },
            
            # === 主力净流入排行测试 ===
            {
                'query': '今日主力净流入排行前10',
                'expected_type': 'money_flow_ranking',
                'category': '资金流向排名'
            },
            {
                'query': '昨天主力净流入前20',
                'expected_type': 'money_flow_ranking',
                'category': '资金流向排名'
            },
            {
                'query': '20250627主力净流入排名',
                'expected_type': 'money_flow_ranking',
                'category': '资金流向排名'
            },
            
            # === 股票简称测试（预期提示使用完整名称） ===
            {
                'query': '茅台最新股价',
                'expected_type': 'price_query',
                'should_prompt_full_name': True,
                'category': '股票简称验证'
            },
            {
                'query': '平安昨天的PE',
                'expected_type': 'valuation_query',
                'should_prompt_full_name': True,
                'category': '股票简称验证'
            },
            {
                'query': '万科的市值',
                'expected_type': 'market_cap_query',
                'should_prompt_full_name': True,
                'category': '股票简称验证'
            }
        ]
        
        # 按类别分组运行测试
        categories = {}
        for test_case in test_cases:
            category = test_case.get('category', '其他')
            if category not in categories:
                categories[category] = []
            categories[category].append(test_case)
        
        # 运行测试
        total_tests = len(test_cases)
        passed_tests = 0
        
        for category, cases in categories.items():
            logger.info(f"\n\n{'#'*60}")
            logger.info(f"# 测试类别: {category}")
            logger.info(f"# 测试数量: {len(cases)}")
            logger.info(f"{'#'*60}")
            
            for test_case in cases:
                result = self.run_single_test(test_case)
                self.test_results.append(result)
                
                if result['success']:
                    passed_tests += 1
                    
                # 避免请求过快
                time.sleep(1)
        
        # 生成测试报告
        self.generate_report(total_tests, passed_tests)
    
    def generate_report(self, total_tests: int, passed_tests: int):
        """生成测试报告"""
        total_time = time.time() - self.start_time
        
        logger.info(f"\n\n{'='*60}")
        logger.info("测试报告总结")
        logger.info(f"{'='*60}")
        logger.info(f"总测试数: {total_tests}")
        logger.info(f"通过数: {passed_tests}")
        logger.info(f"失败数: {total_tests - passed_tests}")
        logger.info(f"成功率: {passed_tests/total_tests*100:.1f}%")
        logger.info(f"总耗时: {total_time:.2f}秒")
        
        # 分析快速模板使用情况
        quick_template_count = sum(1 for r in self.test_results 
                                 if r.get('used_quick_template', False))
        logger.info(f"\n快速模板使用次数: {quick_template_count}")
        
        # 分析SQL使用情况
        has_sql_count = sum(1 for r in self.test_results 
                              if r.get('has_sql', False))
        logger.info(f"SQL查询执行次数: {has_sql_count}")
        
        # 股票简称提示情况
        name_prompt_count = sum(1 for r in self.test_results 
                              if r.get('prompted_full_name', False))
        logger.info(f"股票简称提示次数: {name_prompt_count}")
        
        # 性能分析
        if self.test_results:
            avg_time = sum(r['elapsed_time'] for r in self.test_results) / len(self.test_results)
            max_time = max(r['elapsed_time'] for r in self.test_results)
            min_time = min(r['elapsed_time'] for r in self.test_results)
            
            logger.info(f"\n性能统计:")
            logger.info(f"平均响应时间: {avg_time:.2f}秒")
            logger.info(f"最快响应时间: {min_time:.2f}秒")
            logger.info(f"最慢响应时间: {max_time:.2f}秒")
        
        # 失败用例分析
        failed_tests = [r for r in self.test_results if not r['success']]
        if failed_tests:
            logger.info(f"\n失败用例分析:")
            for i, failed in enumerate(failed_tests, 1):
                logger.info(f"{i}. {failed['query']}")
                if 'error' in failed:
                    logger.info(f"   错误: {failed['error']}")
        
        # 保存详细结果
        report_file = f"sql_agent_improvement_test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump({
                'summary': {
                    'total_tests': total_tests,
                    'passed_tests': passed_tests,
                    'success_rate': passed_tests/total_tests,
                    'total_time': total_time,
                    'quick_template_usage': quick_template_count,
                    'sql_usage': has_sql_count,
                    'name_prompt_count': name_prompt_count
                },
                'test_results': self.test_results
            }, f, ensure_ascii=False, indent=2)
        
        logger.info(f"\n详细测试报告已保存到: {report_file}")


def main():
    """主函数"""
    logger.info("开始SQL Agent快速模板改进测试")
    logger.info(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("测试超时时间: 5分钟")
    
    tester = SQLAgentImprovementTester()
    
    try:
        tester.run_all_tests()
    except KeyboardInterrupt:
        logger.info("\n测试被用户中断")
    except Exception as e:
        logger.error(f"测试过程出错: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()