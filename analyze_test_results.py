#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试结果分析工具
快速分析已有的测试结果文件，无需重新运行测试
"""
import os
import json
from datetime import datetime
from typing import Dict, List, Any


class TestResultsAnalyzer:
    """测试结果分析器"""
    
    def __init__(self):
        self.result_files = [
            {
                "name": "SQL Agent",
                "file": "sql_agent_comprehensive_results.json"
            },
            {
                "name": "RAG Agent",
                "file": "rag_agent_comprehensive_results.json"
            },
            {
                "name": "Financial Agent",
                "file": "financial_agent_comprehensive_results.json"
            },
            {
                "name": "Money Flow Agent",
                "file": "money_flow_agent_comprehensive_results.json"
            },
            {
                "name": "Hybrid Agent",
                "file": "hybrid_agent_comprehensive_results.json"
            }
        ]
        
    def load_results(self, file_path: str) -> Dict[str, Any]:
        """加载测试结果文件"""
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return None
        
    def analyze_agent_results(self, agent_name: str, results: Dict[str, Any]):
        """分析单个Agent的测试结果"""
        print(f"\n{'='*80}")
        print(f"{agent_name} 测试结果分析")
        print('='*80)
        
        # 基本统计
        total = results['total']
        passed = results['passed']
        failed = results['failed']
        pass_rate = passed / total * 100 if total > 0 else 0
        
        print(f"总测试数: {total}")
        print(f"通过: {passed} ({pass_rate:.1f}%)")
        print(f"失败: {failed}")
        
        # 功能详细分析
        print("\n功能测试详情:")
        print("-"*80)
        print(f"{'功能':<30} {'总数':<8} {'通过':<8} {'失败':<8} {'正向通过':<10} {'负向通过':<10}")
        print("-"*80)
        
        for func_name, stats in results['functions'].items():
            print(f"{func_name:<30} {stats['total']:<8} {stats['passed']:<8} {stats['failed']:<8} "
                  f"{stats['positive_passed']:<10} {stats['negative_passed']:<10}")
            
        # 失败测试详情
        if failed > 0:
            print(f"\n失败测试列表 ({failed}个):")
            print("-"*80)
            failed_count = 0
            for detail in results['details']:
                if detail['status'].startswith('❌'):
                    failed_count += 1
                    print(f"{failed_count}. [{detail['function']}] {detail['name']}")
                    if 'error' in detail:
                        print(f"   错误: {detail.get('error', 'N/A')}")
                        
    def generate_summary_report(self):
        """生成汇总报告"""
        print(f"\n{'='*80}")
        print("全部Agent测试结果汇总")
        print('='*80)
        print(f"分析时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        total_tests = 0
        total_passed = 0
        total_failed = 0
        agent_summaries = []
        
        # 收集所有Agent的结果
        for agent_info in self.result_files:
            results = self.load_results(agent_info['file'])
            if results:
                total_tests += results['total']
                total_passed += results['passed'] 
                total_failed += results['failed']
                
                agent_summaries.append({
                    "name": agent_info['name'],
                    "total": results['total'],
                    "passed": results['passed'],
                    "failed": results['failed'],
                    "pass_rate": results['passed'] / results['total'] * 100 if results['total'] > 0 else 0
                })
            else:
                agent_summaries.append({
                    "name": agent_info['name'],
                    "total": 0,
                    "passed": 0,
                    "failed": 0,
                    "pass_rate": 0,
                    "status": "未找到结果文件"
                })
                
        # 打印汇总表
        print("\n各Agent测试汇总:")
        print("-"*80)
        print(f"{'Agent':<20} {'总数':<10} {'通过':<10} {'失败':<10} {'通过率':<10} {'状态':<15}")
        print("-"*80)
        
        for summary in agent_summaries:
            status = summary.get('status', '✅ 已测试' if summary['failed'] == 0 else '⚠️ 有失败')
            print(f"{summary['name']:<20} {summary['total']:<10} {summary['passed']:<10} "
                  f"{summary['failed']:<10} {summary['pass_rate']:<10.1f}% {status:<15}")
                  
        # 总体统计
        print("\n" + "="*80)
        print("总体统计")
        print("="*80)
        print(f"测试Agent数: {len(self.result_files)}")
        print(f"总测试用例数: {total_tests}")
        print(f"总通过数: {total_passed}")
        print(f"总失败数: {total_failed}")
        if total_tests > 0:
            overall_pass_rate = total_passed / total_tests * 100
            print(f"总体通过率: {overall_pass_rate:.1f}%")
            
        # 生成建议
        print("\n" + "="*80)
        print("测试建议")
        print("="*80)
        
        if total_failed == 0:
            print("✅ 所有测试通过！系统稳定性良好。")
        else:
            print(f"⚠️ 有{total_failed}个测试失败，建议：")
            for summary in agent_summaries:
                if summary['failed'] > 0:
                    print(f"   - 修复{summary['name']}的{summary['failed']}个失败测试")
                    
    def analyze_specific_agent(self, agent_name: str):
        """分析特定Agent的测试结果"""
        for agent_info in self.result_files:
            if agent_info['name'] == agent_name:
                results = self.load_results(agent_info['file'])
                if results:
                    self.analyze_agent_results(agent_name, results)
                else:
                    print(f"未找到{agent_name}的测试结果文件: {agent_info['file']}")
                return
                
        print(f"未知的Agent名称: {agent_name}")
        
    def list_failed_tests(self):
        """列出所有失败的测试"""
        print(f"\n{'='*80}")
        print("所有失败测试汇总")
        print('='*80)
        
        total_failed = 0
        
        for agent_info in self.result_files:
            results = self.load_results(agent_info['file'])
            if results and results['failed'] > 0:
                print(f"\n{agent_info['name']} ({results['failed']}个失败):")
                print("-"*40)
                
                failed_count = 0
                for detail in results['details']:
                    if detail['status'].startswith('❌'):
                        failed_count += 1
                        total_failed += 1
                        print(f"{failed_count}. [{detail['function']}] {detail['name']}")
                        
        if total_failed == 0:
            print("✅ 没有失败的测试！")
        else:
            print(f"\n总计: {total_failed}个失败测试")


def main():
    """主函数"""
    analyzer = TestResultsAnalyzer()
    
    while True:
        print("\n" + "="*80)
        print("测试结果分析工具")
        print("="*80)
        print("1. 生成汇总报告")
        print("2. 分析特定Agent")
        print("3. 列出所有失败测试")
        print("4. 分析SQL Agent")
        print("5. 分析RAG Agent")
        print("6. 分析Financial Agent")
        print("7. 分析Money Flow Agent")
        print("8. 分析Hybrid Agent")
        print("0. 退出")
        
        choice = input("\n请选择操作 (0-8): ")
        
        if choice == '0':
            break
        elif choice == '1':
            analyzer.generate_summary_report()
        elif choice == '2':
            agent_name = input("请输入Agent名称: ")
            analyzer.analyze_specific_agent(agent_name)
        elif choice == '3':
            analyzer.list_failed_tests()
        elif choice == '4':
            analyzer.analyze_specific_agent("SQL Agent")
        elif choice == '5':
            analyzer.analyze_specific_agent("RAG Agent")
        elif choice == '6':
            analyzer.analyze_specific_agent("Financial Agent")
        elif choice == '7':
            analyzer.analyze_specific_agent("Money Flow Agent")
        elif choice == '8':
            analyzer.analyze_specific_agent("Hybrid Agent")
        else:
            print("无效选择，请重试")
            
        input("\n按Enter继续...")
        
    print("\n感谢使用测试结果分析工具！")


if __name__ == "__main__":
    main()