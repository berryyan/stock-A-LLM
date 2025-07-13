#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
分析v2.3.0回归测试结果
从测试报告文件中提取关键信息
"""

import os
import re
from datetime import datetime


def extract_test_summary(file_path):
    """从测试文件中提取测试摘要信息"""
    if not os.path.exists(file_path):
        return None
    
    # 尝试多种编码
    encodings = ['utf-8', 'gbk', 'gb2312', 'cp936', 'latin-1']
    content = None
    
    for encoding in encodings:
        try:
            with open(file_path, 'r', encoding=encoding) as f:
                content = f.read()
                break
        except UnicodeDecodeError:
            continue
    
    if content is None:
        print(f"无法读取文件 {file_path}，尝试了所有编码")
        return None
    
    # 提取测试总结信息
    summary = {
        'total': 0,
        'passed': 0,
        'failed': 0,
        'pass_rate': 0.0,
        'error_types': [],
        'key_findings': []
    }
    
    # 查找测试统计
    # 模式1: "通过: X/Y"
    pattern1 = r'通过[：:]\s*(\d+)/(\d+)'
    match1 = re.search(pattern1, content)
    if match1:
        summary['passed'] = int(match1.group(1))
        summary['total'] = int(match1.group(2))
        summary['failed'] = summary['total'] - summary['passed']
    
    # 模式2: "总测试数: X, 通过: Y, 失败: Z"
    pattern2 = r'总测试数[：:]\s*(\d+).*?通过[：:]\s*(\d+).*?失败[：:]\s*(\d+)'
    match2 = re.search(pattern2, content, re.DOTALL)
    if match2:
        summary['total'] = int(match2.group(1))
        summary['passed'] = int(match2.group(2))
        summary['failed'] = int(match2.group(3))
    
    # 计算通过率
    if summary['total'] > 0:
        summary['pass_rate'] = (summary['passed'] / summary['total']) * 100
    
    # 提取错误类型
    error_patterns = [
        r'❌.*?失败[：:]\s*(.+)',
        r'错误[：:]\s*(.+)',
        r'异常[：:]\s*(.+)'
    ]
    
    for pattern in error_patterns:
        matches = re.findall(pattern, content)
        for match in matches[:5]:  # 只取前5个错误
            error_msg = match.strip()
            if error_msg and error_msg not in summary['error_types']:
                summary['error_types'].append(error_msg)
    
    # 提取关键发现
    if '超时' in content:
        summary['key_findings'].append('存在超时问题')
    if '数据' in content and ('缺失' in content or '不足' in content):
        summary['key_findings'].append('数据缺失或不足')
    if '路由' in content and '错误' in content:
        summary['key_findings'].append('路由判断问题')
    if 'LLM' in content and ('慢' in content or '超时' in content):
        summary['key_findings'].append('LLM响应慢')
    
    return summary


def generate_regression_report():
    """生成回归测试报告"""
    print("="*80)
    print("v2.3.0 回归测试结果分析")
    print(f"分析时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80)
    print()
    
    # 定义要分析的文件
    test_files = {
        'SQL Agent': 'test_results/sql_agent_regression_20250712.txt',
        'Money Flow Agent': 'test_results/money_flow_regression_20250712.txt',
        'Financial Agent': 'test_results/financial_regression_20250712.txt',
        'RAG Agent': 'test_results/rag_agent_regression_20250712.txt',
        'Hybrid Agent': 'test_results/hybrid_agent_regression_20250712.txt'
    }
    
    results = {}
    total_stats = {
        'total': 0,
        'passed': 0,
        'failed': 0
    }
    
    # 分析每个Agent的测试结果
    for agent_name, file_path in test_files.items():
        summary = extract_test_summary(file_path)
        if summary:
            results[agent_name] = summary
            total_stats['total'] += summary['total']
            total_stats['passed'] += summary['passed']
            total_stats['failed'] += summary['failed']
        else:
            print(f"⚠️  未找到 {agent_name} 的测试结果文件: {file_path}")
    
    # 打印总体统计
    print("## 总体测试统计")
    print("-"*60)
    print(f"总测试用例数: {total_stats['total']}")
    print(f"总通过数: {total_stats['passed']}")
    print(f"总失败数: {total_stats['failed']}")
    if total_stats['total'] > 0:
        overall_pass_rate = (total_stats['passed'] / total_stats['total']) * 100
        print(f"总体通过率: {overall_pass_rate:.1f}%")
    print()
    
    # 打印各Agent详细结果
    print("## 各Agent测试结果")
    print("-"*60)
    print(f"{'Agent':<20} {'测试数':<10} {'通过':<10} {'失败':<10} {'通过率':<10}")
    print("-"*60)
    
    for agent_name, summary in results.items():
        print(f"{agent_name:<20} {summary['total']:<10} {summary['passed']:<10} "
              f"{summary['failed']:<10} {summary['pass_rate']:.1f}%")
    print()
    
    # 打印主要问题汇总
    print("## 主要问题汇总")
    print("-"*60)
    
    for agent_name, summary in results.items():
        if summary['error_types'] or summary['key_findings']:
            print(f"\n### {agent_name}:")
            
            if summary['key_findings']:
                print("关键发现:")
                for finding in summary['key_findings']:
                    print(f"  - {finding}")
            
            if summary['error_types']:
                print("主要错误:")
                for i, error in enumerate(summary['error_types'][:3], 1):
                    print(f"  {i}. {error}")
    
    # 生成结论和建议
    print("\n## 结论与建议")
    print("-"*60)
    
    # 判断是否可以发布
    high_quality_agents = 0
    for agent_name, summary in results.items():
        if summary['pass_rate'] >= 90:
            high_quality_agents += 1
    
    if overall_pass_rate >= 85 and high_quality_agents >= 3:
        print("✅ 建议: 可以发布v2.3.0")
        print(f"   - 总体通过率 {overall_pass_rate:.1f}% 达到标准")
        print(f"   - {high_quality_agents}个Agent达到90%以上通过率")
    elif overall_pass_rate >= 70:
        print("⚠️  建议: 可以发布v2.3.0，但需要在发布说明中明确已知问题")
        print(f"   - 总体通过率 {overall_pass_rate:.1f}%")
        print(f"   - 部分Agent存在问题需要后续优化")
    else:
        print("❌ 建议: 暂缓发布，需要修复关键问题")
        print(f"   - 总体通过率仅 {overall_pass_rate:.1f}%")
        print("   - 建议先修复主要问题再发布")
    
    # 保存分析报告
    report_content = f"""# v2.3.0 回归测试分析报告

生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 测试环境
- 操作系统: Windows
- Python环境: Anaconda (stock-frontend)
- 测试类型: 完整综合测试

## 总体统计
- 总测试用例: {total_stats['total']}
- 通过: {total_stats['passed']}
- 失败: {total_stats['failed']}
- 总体通过率: {overall_pass_rate:.1f}%

## 各Agent测试结果

| Agent | 测试数 | 通过 | 失败 | 通过率 |
|-------|--------|------|------|--------|
"""
    
    for agent_name, summary in results.items():
        report_content += f"| {agent_name} | {summary['total']} | {summary['passed']} | {summary['failed']} | {summary['pass_rate']:.1f}% |\n"
    
    report_content += "\n## 详细问题分析\n\n"
    
    for agent_name, summary in results.items():
        if summary['error_types'] or summary['key_findings']:
            report_content += f"### {agent_name}\n\n"
            
            if summary['key_findings']:
                report_content += "**关键发现:**\n"
                for finding in summary['key_findings']:
                    report_content += f"- {finding}\n"
                report_content += "\n"
            
            if summary['error_types']:
                report_content += "**主要错误:**\n"
                for i, error in enumerate(summary['error_types'][:5], 1):
                    report_content += f"{i}. {error}\n"
                report_content += "\n"
    
    # 保存报告（使用utf-8-sig避免BOM问题）
    with open('test_results/regression_analysis_20250712.md', 'w', encoding='utf-8-sig') as f:
        f.write(report_content)
    
    print(f"\n分析报告已保存到: test_results/regression_analysis_20250712.md")
    print("="*80)


if __name__ == "__main__":
    generate_regression_report()