#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
分析v2.3.0最终测试结果
"""

import json
import os
from datetime import datetime

def analyze_report(file_path, agent_name):
    """分析单个测试报告"""
    if not os.path.exists(file_path):
        print(f"\n❌ {agent_name}: 报告文件不存在")
        return None
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # 处理不同的报告格式
        if 'summary' in data:
            # Money Flow Agent 格式
            total = data['summary'].get('total', 0)
            passed = data['summary'].get('passed', 0)
            failed = data['summary'].get('failed', 0)
            pass_rate = data['summary'].get('pass_rate', 0)
        elif 'total' in data and 'passed' in data:
            # SQL Agent 格式
            total = data.get('total', 0)
            passed = data.get('passed', 0)
            failed = data.get('failed', 0)
            pass_rate = (passed / total * 100) if total > 0 else 0
        elif 'total_tests' in data:
            # 其他Agent格式
            total = data.get('total_tests', 0)
            passed = data.get('passed', 0)
            failed = data.get('failed', 0)
            pass_rate = data.get('pass_rate', 0)
        else:
            # 未知格式
            print(f"\n⚠️ {agent_name}: 未知的报告格式")
            return None
        
        # 处理pass_rate可能是字符串的情况
        if isinstance(pass_rate, str):
            pass_rate = float(pass_rate.replace('%', ''))
        
        return {
            'total': total,
            'passed': passed,
            'failed': failed,
            'pass_rate': pass_rate
        }
        
    except Exception as e:
        print(f"\n❌ {agent_name}: 解析错误 - {str(e)}")
        return None

def main():
    print("="*80)
    print("v2.3.0 Agent Excellence - 最终测试结果分析")
    print(f"分析时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80)
    
    # 测试报告
    reports = [
        ('SQL Agent', 'test_report_20250713_003817.json'),
        ('Money Flow Agent', 'money_flow_test_report_final_20250713_004238.json'),
        ('Financial Agent', 'test_financial_agent_report_20250713_010842.json'),
        ('RAG Agent', 'rag_agent_comprehensive_results.json'),
    ]
    
    total_all = 0
    passed_all = 0
    failed_all = 0
    
    print("\n各Agent测试结果:")
    print("-"*80)
    
    for agent_name, report_file in reports:
        result = analyze_report(report_file, agent_name)
        if result:
            total_all += result['total']
            passed_all += result['passed']
            failed_all += result['failed']
            
            pass_rate = float(result['pass_rate']) if result['pass_rate'] else 0.0
            status = "✅" if pass_rate >= 95 else "⚠️" if pass_rate >= 80 else "❌"
            print(f"\n{agent_name}:")
            print(f"  总测试: {result['total']}")
            print(f"  通过: {result['passed']}")
            print(f"  失败: {result['failed']}")
            print(f"  通过率: {pass_rate:.1f}% {status}")
    
    print(f"\nHybrid Agent:")
    print(f"  状态: ❌ 无限递归问题（已修复，待重测）")
    
    # 总体统计
    print("\n" + "="*80)
    print("总体测试统计:")
    print("-"*80)
    print(f"总测试数: {total_all}")
    print(f"总通过数: {passed_all}")
    print(f"总失败数: {failed_all}")
    
    if total_all > 0:
        overall_rate = passed_all / total_all * 100
        print(f"整体通过率: {overall_rate:.1f}%")
    
    # 发布评估
    print("\n" + "="*80)
    print("v2.3.0 发布评估:")
    print("-"*80)
    
    print("\n✅ 已完成:")
    print("- SQL Agent: 100% 测试通过（41/41）")
    print("- Money Flow Agent: 100% 测试通过（64/64）") 
    print("- Financial Agent: 95.3% 测试通过（边界问题已解决）")
    print("- Hybrid Agent: 无限递归问题已修复")
    
    print("\n⚠️ 需要关注:")
    print("- RAG Agent: 数据格式待确认")
    print("- Hybrid Agent: 需要重新运行测试验证修复效果")
    
    print("\n📋 后续步骤:")
    print("1. 重新测试Hybrid Agent（验证无限递归修复）")
    print("2. 确认RAG Agent测试结果")
    print("3. 更新v2.3.0_release_notes.md")
    print("4. 准备发布")

if __name__ == "__main__":
    main()