#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Money Flow Agent 综合测试脚本 v2
基于新的理解和职责划分重新设计测试用例
"""

import sys
import os
import json
import logging
from typing import Dict, List, Tuple, Any
from datetime import datetime

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 导入被测试的模块
from agents.money_flow_agent_modular import MoneyFlowAgentModular
from database.mysql_connector import MySQLConnector

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class MoneyFlowAgentTester:
    """Money Flow Agent 测试器 v2"""
    
    def __init__(self):
        """初始化测试器"""
        self.mysql_conn = MySQLConnector()
        self.agent = MoneyFlowAgentModular(self.mysql_conn)
        self.results = []
        self.test_categories = {}
        
    def test_query(self, query: str, expected_success: bool = True, 
                   test_name: str = "", category: str = "",
                   should_route_to_sql: bool = False) -> Tuple[bool, Dict]:
        """
        执行单个测试查询
        
        Args:
            query: 查询语句
            expected_success: 期望是否成功
            test_name: 测试名称
            category: 测试类别
            should_route_to_sql: 是否应该路由到SQL Agent
            
        Returns:
            (是否通过, 结果详情)
        """
        print(f"\n{'='*60}")
        print(f"测试: {test_name or query}")
        print(f"类别: {category}")
        print(f"查询: {query}")
        print(f"期望: {'成功' if expected_success else '失败'}")
        if should_route_to_sql:
            print(f"特殊期望: 应该路由到SQL Agent")
        
        start_time = datetime.now()
        
        try:
            result = self.agent.query(query)
            elapsed_time = (datetime.now() - start_time).total_seconds()
            
            actual_success = result.get('success', False)
            
            # 特殊处理：如果应该路由到SQL Agent
            if should_route_to_sql:
                # 检查是否返回了路由错误
                if not actual_success and '应该由SQL Agent处理' in str(result.get('error', '')):
                    passed = True  # 正确识别了应该路由到SQL
                else:
                    passed = False
            else:
                passed = actual_success == expected_success
            
            # 记录结果
            test_result = {
                'category': category,
                'test_name': test_name,
                'query': query,
                'expected_success': expected_success,
                'actual_success': actual_success,
                'should_route_to_sql': should_route_to_sql,
                'passed': passed,
                'elapsed_time': elapsed_time,
                'error': result.get('error'),
                'result_preview': str(result.get('result', ''))[:300] if result.get('result') else None
            }
            
            self.results.append(test_result)
            
            # 更新分类统计
            if category not in self.test_categories:
                self.test_categories[category] = {'total': 0, 'passed': 0}
            self.test_categories[category]['total'] += 1
            if passed:
                self.test_categories[category]['passed'] += 1
            
            # 打印结果
            print(f"结果: {'✓ 通过' if passed else '✗ 失败'}")
            print(f"实际: {'成功' if actual_success else '失败'}")
            if result.get('error'):
                print(f"错误: {result['error']}")
            if actual_success and result.get('result'):
                print(f"响应预览: {str(result['result'])[:200]}...")
            print(f"耗时: {elapsed_time:.2f}秒")
            
            return passed, test_result
            
        except Exception as e:
            logger.error(f"测试异常: {str(e)}")
            test_result = {
                'category': category,
                'test_name': test_name,
                'query': query,
                'expected_success': expected_success,
                'actual_success': False,
                'passed': False,
                'elapsed_time': 0,
                'error': str(e),
                'exception': True
            }
            self.results.append(test_result)
            
            if category not in self.test_categories:
                self.test_categories[category] = {'total': 0, 'passed': 0}
            self.test_categories[category]['total'] += 1
            
            print(f"结果: ✗ 异常")
            print(f"异常: {str(e)}")
            
            return False, test_result
    
    def run_all_tests(self):
        """运行所有测试"""
        print("开始Money Flow Agent综合测试 v2...")
        print("="*80)
        
        # 1. 深度分析查询（Money Flow Agent的核心功能）
        self._test_deep_analysis()
        
        # 2. SQL路由识别测试（应该路由到SQL Agent的查询）
        self._test_sql_routing()
        
        # 3. 术语标准化测试
        self._test_term_standardization()
        
        # 4. 边界测试
        self._test_boundary_cases()
        
        # 5. 错误处理测试
        self._test_error_handling()
        
        # 生成测试报告
        self._generate_report()
    
    def _test_deep_analysis(self):
        """测试深度分析功能"""
        category = "1. 深度分析查询"
        
        # 1.1 个股深度分析
        test_cases = [
            ("分析贵州茅台的资金流向", True, "分析关键词开头"),
            ("评估平安银行的主力资金", True, "评估关键词"),
            ("研究宁德时代的资金趋势", True, "研究关键词"),
            ("贵州茅台主力是否在建仓", True, "行为模式-建仓"),
            ("平安银行有洗盘迹象吗", True, "行为模式-洗盘"),
            ("万科A主力在出货吗", True, "行为模式-出货"),
            ("如何看待茅台的资金流出", True, "深度分析需求"),
            ("贵州茅台资金流向趋势如何", True, "趋势分析"),
            ("预测平安银行未来资金走势", True, "预测分析"),
        ]
        
        for query, expected, name in test_cases:
            self.test_query(query, expected, name, category)
    
    def _test_sql_routing(self):
        """测试应该路由到SQL Agent的查询"""
        category = "2. SQL路由识别"
        
        test_cases = [
            # 排名查询
            ("主力净流入排名前10", True, "排名查询"),
            ("超大单净流出TOP20", True, "TOP查询"),
            ("主力资金排行", True, "排行查询"),
            
            # 简单数据查询
            ("贵州茅台的主力资金", True, "个股简单查询"),
            ("平安银行今天的超大单", True, "指定日期查询"),
            ("万科A的大单资金", True, "大单查询"),
            
            # 板块简单查询
            ("银行板块的主力资金", True, "板块简单查询"),
            ("新能源板块主力资金", True, "板块查询-无的"),
            ("白酒板块资金", True, "板块资金查询"),
        ]
        
        for query, expected, name in test_cases:
            # 这些查询应该被识别为SQL_ONLY类型
            self.test_query(query, False, name, category, should_route_to_sql=True)
    
    def _test_term_standardization(self):
        """测试术语标准化功能"""
        category = "3. 术语标准化"
        
        test_cases = [
            # 非标准术语应该被接受并转换
            ("分析贵州茅台的机构资金", True, "机构→超大单"),
            ("评估平安银行的游资行为", True, "游资→主力"),
            ("研究万科A的散户资金", True, "散户→小单"),
            ("分析茅台的大资金流向", True, "大资金→主力"),
            ("宁德时代的热钱动向分析", True, "热钱→主力"),
        ]
        
        for query, expected, name in test_cases:
            self.test_query(query, expected, name, category)
    
    def _test_boundary_cases(self):
        """测试边界情况"""
        category = "4. 边界测试"
        
        test_cases = [
            # 板块深度分析（当前不支持）
            ("分析银行板块的资金流向", False, "板块深度分析-暂不支持"),
            ("评估新能源板块的资金趋势", False, "板块趋势分析-暂不支持"),
            
            # 多股票对比（需要特殊处理）
            ("分析贵州茅台和五粮液的资金对比", True, "双股对比"),
            
            # 时间周期
            ("分析贵州茅台最近5天的资金流向", True, "指定天数"),
            ("评估平安银行本月的主力行为", True, "月度分析"),
        ]
        
        for query, expected, name in test_cases:
            self.test_query(query, expected, name, category)
    
    def _test_error_handling(self):
        """测试错误处理"""
        category = "5. 错误处理"
        
        test_cases = [
            # 空查询
            ("", False, "空查询"),
            ("   ", False, "空白查询"),
            
            # 无效查询
            ("分析天气如何", False, "非资金查询"),
            ("研究经济形势", False, "无股票查询"),
            
            # 无效股票
            ("分析茅台的资金流向", False, "股票简称"),
            ("评估中国平安的主力资金", False, "非标准名称"),
            ("分析123456的资金流向", False, "无效代码"),
        ]
        
        for query, expected, name in test_cases:
            self.test_query(query, expected, name, category)
    
    def _generate_report(self):
        """生成测试报告"""
        total_tests = len(self.results)
        passed_tests = sum(1 for r in self.results if r['passed'])
        failed_tests = total_tests - passed_tests
        
        print("\n" + "="*80)
        print("测试报告汇总")
        print("="*80)
        print(f"总测试数: {total_tests}")
        print(f"通过: {passed_tests}")
        print(f"失败: {failed_tests}")
        print(f"通过率: {passed_tests/total_tests*100:.1f}%")
        
        print("\n分类统计:")
        for category, stats in sorted(self.test_categories.items()):
            total = stats['total']
            passed = stats['passed']
            print(f"{category}: {passed}/{total} ({passed/total*100:.1f}%)")
        
        # 输出失败的测试
        failed_results = [r for r in self.results if not r['passed']]
        if failed_results:
            print("\n失败的测试:")
            for r in failed_results:
                print(f"- [{r['category']}] {r['test_name']}: {r['query']}")
                if r.get('error'):
                    print(f"  错误: {r['error']}")
                print(f"  期望: {'成功' if r['expected_success'] else '失败'}, "
                      f"实际: {'成功' if r.get('actual_success') else '失败'}")
                if r.get('should_route_to_sql'):
                    print(f"  特殊: 应该路由到SQL Agent")
        
        # 保存详细报告
        report_file = f"money_flow_test_report_v2_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump({
                'summary': {
                    'total': total_tests,
                    'passed': passed_tests,
                    'failed': failed_tests,
                    'pass_rate': passed_tests/total_tests*100
                },
                'categories': self.test_categories,
                'details': self.results
            }, f, ensure_ascii=False, indent=2)
        
        print(f"\n详细报告已保存到: {report_file}")


def main():
    """主函数"""
    tester = MoneyFlowAgentTester()
    
    try:
        tester.run_all_tests()
    except KeyboardInterrupt:
        print("\n测试被用户中断")
    except Exception as e:
        logger.error(f"测试过程发生错误: {str(e)}", exc_info=True)
    finally:
        # 确保数据库连接关闭
        if hasattr(tester, 'mysql_conn'):
            tester.mysql_conn.close()


if __name__ == "__main__":
    main()