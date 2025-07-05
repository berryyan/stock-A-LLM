#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
模块化Agent集成测试
测试所有4个Agent的模块化版本
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import time
import json
from datetime import datetime
from typing import Dict, List, Any

# 导入模块化Agent
from agents.sql_agent_modular import SQLAgentModular
from agents.rag_agent_modular import RAGAgentModular
from agents.financial_agent_modular import FinancialAgentModular
from agents.money_flow_agent_modular import MoneyFlowAgentModular
from utils.logger import setup_logger

logger = setup_logger("test_modular_integration")


class ModularAgentTester:
    """模块化Agent测试器"""
    
    def __init__(self):
        """初始化所有Agent"""
        print("初始化模块化Agent...")
        self.sql_agent = SQLAgentModular()
        self.rag_agent = RAGAgentModular()
        self.financial_agent = FinancialAgentModular()
        self.money_flow_agent = MoneyFlowAgentModular()
        
        # 测试结果统计
        self.results = {
            'sql': {'total': 0, 'success': 0, 'failures': []},
            'rag': {'total': 0, 'success': 0, 'failures': []},
            'financial': {'total': 0, 'success': 0, 'failures': []},
            'money_flow': {'total': 0, 'success': 0, 'failures': []}
        }
    
    def test_sql_agent(self):
        """测试SQL Agent"""
        print("\n" + "="*60)
        print("测试SQL Agent模块化版本")
        print("="*60)
        
        test_cases = [
            {
                'query': "贵州茅台的最新股价",
                'description': "股价查询"
            },
            {
                'query': "市值排名前5的股票",
                'description': "市值排名"
            },
            {
                'query': "比亚迪最近30天的K线",
                'description': "K线查询"
            },
            {
                'query': "今天涨幅最大的10只股票",
                'description': "涨幅排名"
            },
            {
                'query': "贵州茅台的财务数据",
                'description': "财务数据查询"
            }
        ]
        
        for case in test_cases:
            self._test_single_query(
                self.sql_agent, 
                case['query'], 
                case['description'],
                'sql'
            )
    
    def test_rag_agent(self):
        """测试RAG Agent"""
        print("\n" + "="*60)
        print("测试RAG Agent模块化版本")
        print("="*60)
        
        test_cases = [
            {
                'query': "贵州茅台最新的公告内容",
                'description': "公告查询"
            },
            {
                'query': "比亚迪的新能源汽车业务发展",
                'description': "业务分析"
            },
            {
                'query': "宁德时代的电池技术优势",
                'description': "技术分析"
            }
        ]
        
        for case in test_cases:
            self._test_single_query(
                self.rag_agent,
                case['query'],
                case['description'],
                'rag'
            )
    
    def test_financial_agent(self):
        """测试Financial Agent"""
        print("\n" + "="*60)
        print("测试Financial Agent模块化版本")
        print("="*60)
        
        test_cases = [
            {
                'query': "分析贵州茅台的财务健康度",
                'description': "财务健康度分析"
            },
            {
                'query': "比亚迪的盈利能力如何",
                'description': "盈利能力分析"
            },
            {
                'query': "宁德时代的现金流质量",
                'description': "现金流分析"
            }
        ]
        
        for case in test_cases:
            # Financial Agent使用analyze方法
            query = case['query']
            desc = case['description']
            
            print(f"\n测试: {desc}")
            print(f"查询: {query}")
            
            start_time = time.time()
            try:
                result = self.financial_agent.analyze(query)
                elapsed = time.time() - start_time
                
                self.results['financial']['total'] += 1
                
                if result.get('success'):
                    self.results['financial']['success'] += 1
                    print(f"✓ 成功 (耗时: {elapsed:.2f}秒)")
                    
                    # 只显示结果的前200个字符
                    result_preview = result.get('result', '')[:200]
                    if len(result.get('result', '')) > 200:
                        result_preview += "..."
                    print(f"结果预览: {result_preview}")
                else:
                    self.results['financial']['failures'].append({
                        'query': query,
                        'error': result.get('error', '未知错误')
                    })
                    print(f"✗ 失败: {result.get('error')}")
                    
            except Exception as e:
                self.results['financial']['total'] += 1
                self.results['financial']['failures'].append({
                    'query': query,
                    'error': str(e)
                })
                print(f"✗ 异常: {str(e)}")
    
    def test_money_flow_agent(self):
        """测试Money Flow Agent"""
        print("\n" + "="*60)
        print("测试Money Flow Agent模块化版本")
        print("="*60)
        
        test_cases = [
            {
                'query': "贵州茅台的主力资金",
                'description': "个股主力资金"
            },
            {
                'query': "分析比亚迪的资金流向",
                'description': "资金流向分析"
            },
            {
                'query': "银行板块的主力资金",
                'description': "板块资金流向"
            }
        ]
        
        for case in test_cases:
            # Money Flow Agent使用analyze方法
            query = case['query']
            desc = case['description']
            
            print(f"\n测试: {desc}")
            print(f"查询: {query}")
            
            start_time = time.time()
            try:
                result = self.money_flow_agent.analyze(query)
                elapsed = time.time() - start_time
                
                self.results['money_flow']['total'] += 1
                
                if result.get('success'):
                    self.results['money_flow']['success'] += 1
                    print(f"✓ 成功 (耗时: {elapsed:.2f}秒)")
                    
                    # 只显示结果的前200个字符
                    result_preview = result.get('result', '')[:200]
                    if len(result.get('result', '')) > 200:
                        result_preview += "..."
                    print(f"结果预览: {result_preview}")
                else:
                    self.results['money_flow']['failures'].append({
                        'query': query,
                        'error': result.get('error', '未知错误')
                    })
                    print(f"✗ 失败: {result.get('error')}")
                    
            except Exception as e:
                self.results['money_flow']['total'] += 1
                self.results['money_flow']['failures'].append({
                    'query': query,
                    'error': str(e)
                })
                print(f"✗ 异常: {str(e)}")
    
    def _test_single_query(self, agent, query: str, description: str, agent_type: str):
        """测试单个查询"""
        print(f"\n测试: {description}")
        print(f"查询: {query}")
        
        start_time = time.time()
        try:
            result = agent.query(query)
            elapsed = time.time() - start_time
            
            self.results[agent_type]['total'] += 1
            
            if result.get('success'):
                self.results[agent_type]['success'] += 1
                print(f"✓ 成功 (耗时: {elapsed:.2f}秒)")
                
                # 显示部分结果
                result_preview = result.get('result', '')[:200]
                if len(result.get('result', '')) > 200:
                    result_preview += "..."
                print(f"结果预览: {result_preview}")
                
                # 显示快速路径信息
                if result.get('quick_path'):
                    print("  使用了快速查询路径")
            else:
                self.results[agent_type]['failures'].append({
                    'query': query,
                    'error': result.get('error', '未知错误')
                })
                print(f"✗ 失败: {result.get('error')}")
                if result.get('suggestion'):
                    print(f"  建议: {result.get('suggestion')}")
                    
        except Exception as e:
            self.results[agent_type]['total'] += 1
            self.results[agent_type]['failures'].append({
                'query': query,
                'error': str(e)
            })
            print(f"✗ 异常: {str(e)}")
    
    def test_cross_agent_query(self):
        """测试跨Agent查询场景"""
        print("\n" + "="*60)
        print("测试跨Agent查询场景")
        print("="*60)
        
        # 测试同一只股票的不同维度分析
        stock = "贵州茅台"
        
        print(f"\n综合分析: {stock}")
        
        # 1. SQL查询基础数据
        print("\n1. 基础数据查询:")
        sql_result = self.sql_agent.query(f"{stock}的最新股价")
        if sql_result.get('success'):
            print("✓ 股价数据获取成功")
        
        # 2. 财务分析
        print("\n2. 财务分析:")
        financial_result = self.financial_agent.analyze(f"分析{stock}的财务健康度")
        if financial_result.get('success'):
            print("✓ 财务分析完成")
        
        # 3. 资金流向
        print("\n3. 资金流向分析:")
        money_flow_result = self.money_flow_agent.analyze(f"{stock}的主力资金")
        if money_flow_result.get('success'):
            print("✓ 资金流向分析完成")
        
        # 4. 公告信息
        print("\n4. 公告信息查询:")
        rag_result = self.rag_agent.query(f"{stock}最新的公告")
        if rag_result.get('success'):
            print("✓ 公告查询完成")
    
    def generate_report(self):
        """生成测试报告"""
        print("\n" + "="*80)
        print("模块化Agent集成测试报告")
        print("="*80)
        print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        # 总体统计
        total_tests = sum(r['total'] for r in self.results.values())
        total_success = sum(r['success'] for r in self.results.values())
        success_rate = (total_success / total_tests * 100) if total_tests > 0 else 0
        
        print(f"总测试数: {total_tests}")
        print(f"成功数: {total_success}")
        print(f"成功率: {success_rate:.1f}%")
        print()
        
        # 各Agent统计
        print("各Agent测试结果:")
        print("-" * 50)
        for agent_name, result in self.results.items():
            if result['total'] > 0:
                success_rate = result['success'] / result['total'] * 100
                print(f"{agent_name.upper():12} | 总数: {result['total']:3} | 成功: {result['success']:3} | 成功率: {success_rate:5.1f}%")
        
        # 失败详情
        print("\n失败的测试:")
        print("-" * 50)
        for agent_name, result in self.results.items():
            if result['failures']:
                print(f"\n{agent_name.upper()}:")
                for failure in result['failures']:
                    print(f"  - 查询: {failure['query']}")
                    print(f"    错误: {failure['error']}")
        
        # 保存报告
        report_file = f"test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, ensure_ascii=False, indent=2)
        print(f"\n详细报告已保存到: {report_file}")


def main():
    """主测试函数"""
    print("开始模块化Agent集成测试...")
    print("测试环境准备中...")
    
    tester = ModularAgentTester()
    
    try:
        # 测试各个Agent
        tester.test_sql_agent()
        tester.test_rag_agent()
        tester.test_financial_agent()
        tester.test_money_flow_agent()
        
        # 测试跨Agent场景
        tester.test_cross_agent_query()
        
    except KeyboardInterrupt:
        print("\n测试被用户中断")
    except Exception as e:
        print(f"\n测试过程中发生错误: {str(e)}")
        logger.error("测试异常", exc_info=True)
    finally:
        # 生成测试报告
        tester.generate_report()
        print("\n测试完成！")


if __name__ == "__main__":
    main()