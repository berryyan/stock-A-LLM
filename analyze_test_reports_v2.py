#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
分析v2.3.0回归测试结果
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Any

def analyze_test_report(file_path: str, agent_name: str) -> Dict[str, Any]:
    """分析单个测试报告"""
    result = {
        'agent': agent_name,
        'file': file_path,
        'exists': False,
        'total_tests': 0,
        'passed': 0,
        'failed': 0,
        'pass_rate': 0.0,
        'test_categories': {},
        'error_patterns': {}
    }
    
    if not os.path.exists(file_path):
        return result
    
    result['exists'] = True
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # 提取基本统计信息 - 处理不同的报告格式
        if 'summary' in data:
            result['total_tests'] = data['summary'].get('total_tests', 0)
            result['passed'] = data['summary'].get('passed', 0)
            result['failed'] = data['summary'].get('failed', 0)
            result['pass_rate'] = data['summary'].get('pass_rate', 0.0)
            result['execution_time'] = data['summary'].get('execution_time', 0.0)
        elif 'total_tests' in data:
            # 直接在根级别的格式
            result['total_tests'] = data.get('total_tests', 0)
            result['passed'] = data.get('passed', 0)
            result['failed'] = data.get('failed', 0)
            result['pass_rate'] = data.get('pass_rate', 0.0)
            result['execution_time'] = data.get('test_duration', 0.0)
        else:
            # 尝试从测试列表计算
            tests = data.get('tests', data.get('test_results', []))
            if tests:
                result['total_tests'] = len(tests)
                result['passed'] = sum(1 for t in tests if t.get('passed', t.get('status') == 'passed'))
                result['failed'] = result['total_tests'] - result['passed']
                result['pass_rate'] = (result['passed'] / result['total_tests'] * 100) if result['total_tests'] > 0 else 0
        
        # 分析测试类别
        test_categories = {}
        tests = data.get('tests', data.get('test_results', []))
        for test in tests:
            category = test.get('category', test.get('test_category', 'Unknown'))
            if category not in test_categories:
                test_categories[category] = {'passed': 0, 'failed': 0}
            
            if test.get('passed', test.get('status') == 'passed'):
                test_categories[category]['passed'] += 1
            else:
                test_categories[category]['failed'] += 1
        
        result['test_categories'] = test_categories
        
        # 分析错误模式
        error_patterns = {}
        for test in data.get('tests', []):
            if not test.get('passed') and test.get('error'):
                error = test['error']
                # 提取错误关键词
                if '股票简称' in error:
                    error_key = '股票简称错误'
                elif '股票不存在' in error:
                    error_key = '股票不存在'
                elif '参数' in error:
                    error_key = '参数错误'
                elif '连接' in error or 'Connection' in error:
                    error_key = '连接错误'
                elif '超时' in error or 'timeout' in error:
                    error_key = '超时错误'
                else:
                    error_key = '其他错误'
                
                if error_key not in error_patterns:
                    error_patterns[error_key] = 0
                error_patterns[error_key] += 1
        
        result['error_patterns'] = error_patterns
        
    except Exception as e:
        result['parse_error'] = str(e)
    
    return result

def print_report_summary(analysis: Dict[str, Any]):
    """打印单个报告摘要"""
    print(f"\n{'='*60}")
    print(f"{analysis['agent']} 测试报告分析")
    print(f"{'='*60}")
    
    if not analysis['exists']:
        print("❌ 报告文件不存在")
        return
    
    if 'parse_error' in analysis:
        print(f"❌ 解析错误: {analysis['parse_error']}")
        return
    
    # 基本统计
    print(f"总测试数: {analysis['total_tests']}")
    pass_rate = float(analysis['pass_rate']) if isinstance(analysis['pass_rate'], (int, float, str)) else 0.0
    print(f"通过: {analysis['passed']} ({pass_rate:.1f}%)")
    print(f"失败: {analysis['failed']}")
    exec_time = float(analysis.get('execution_time', 0)) if analysis.get('execution_time') else 0.0
    print(f"执行时间: {exec_time:.1f}秒")
    
    # 按类别统计
    if analysis['test_categories']:
        print(f"\n测试类别分布:")
        for category, stats in analysis['test_categories'].items():
            total = stats['passed'] + stats['failed']
            pass_rate = (stats['passed'] / total * 100) if total > 0 else 0
            print(f"  {category}: {stats['passed']}/{total} ({pass_rate:.1f}%)")
    
    # 错误模式
    if analysis['error_patterns']:
        print(f"\n错误模式分析:")
        for error_type, count in sorted(analysis['error_patterns'].items(), 
                                      key=lambda x: x[1], reverse=True):
            print(f"  {error_type}: {count}次")

def main():
    """主函数"""
    print("="*80)
    print("v2.3.0 Agent Excellence 回归测试结果分析")
    print(f"分析时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80)
    
    # 测试报告文件映射
    test_reports = {
        'SQL Agent': 'test_report_20250713_003817.json',
        'Money Flow Agent': 'money_flow_test_report_final_20250713_004238.json',
        'Financial Agent': 'test_financial_agent_report_20250713_010842.json',
        'RAG Agent': 'rag_agent_comprehensive_results.json',
        # Hybrid Agent 测试失败，没有生成报告
    }
    
    # 分析每个报告
    all_results = []
    total_stats = {
        'total_tests': 0,
        'total_passed': 0,
        'total_failed': 0
    }
    
    for agent_name, report_file in test_reports.items():
        analysis = analyze_test_report(report_file, agent_name)
        all_results.append(analysis)
        print_report_summary(analysis)
        
        if analysis['exists'] and 'parse_error' not in analysis:
            total_stats['total_tests'] += analysis['total_tests']
            total_stats['total_passed'] += analysis['passed']
            total_stats['total_failed'] += analysis['failed']
    
    # 总体统计
    print(f"\n{'='*80}")
    print("总体测试统计")
    print(f"{'='*80}")
    print(f"总测试数: {total_stats['total_tests']}")
    print(f"总通过数: {total_stats['total_passed']}")
    print(f"总失败数: {total_stats['total_failed']}")
    
    overall_pass_rate = 0
    if total_stats['total_tests'] > 0:
        overall_pass_rate = total_stats['total_passed'] / total_stats['total_tests'] * 100
        print(f"整体通过率: {overall_pass_rate:.1f}%")
    else:
        print("整体通过率: 无法计算（总测试数为0）")
    
    # 关键发现
    print(f"\n{'='*80}")
    print("关键发现与建议")
    print(f"{'='*80}")
    
    # 检查各Agent状态
    print("\nAgent状态评估:")
    for result in all_results:
        if result['exists'] and 'parse_error' not in result and result['total_tests'] > 0:
            status = "✅ 优秀" if result['pass_rate'] >= 95 else \
                    "⚠️ 良好" if result['pass_rate'] >= 80 else \
                    "❌ 需改进"
            print(f"- {result['agent']}: {result['pass_rate']:.1f}% {status}")
        elif result['exists']:
            print(f"- {result['agent']}: 数据格式问题或无测试数据")
    
    print("\n❌ Hybrid Agent: 无限递归问题（已修复）")
    
    # 发布建议
    print(f"\n{'='*80}")
    print("v2.3.0 发布建议")
    print(f"{'='*80}")
    
    if total_stats['total_tests'] > 0 and overall_pass_rate >= 90:
        print("✅ 建议：测试通过率良好，修复Hybrid Agent后可以发布")
    else:
        print("⚠️ 建议：需要进一步优化，特别关注低通过率的Agent")
    
    print("\n后续步骤:")
    print("1. 重新测试已修复的Hybrid Agent")
    print("2. 针对性修复各Agent的主要错误模式")
    print("3. 更新发布说明文档")
    print("4. 执行最终的集成测试")

if __name__ == "__main__":
    main()