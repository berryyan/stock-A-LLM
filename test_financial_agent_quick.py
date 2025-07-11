#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Financial Agent 快速测试脚本
仅测试关键功能和错误处理，跳过耗时的LLM分析
"""
import sys
import os
import time
import json
from datetime import datetime

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.financial_agent_modular import FinancialAgentModular


def test_financial_agent():
    """运行快速测试"""
    agent = FinancialAgentModular()
    
    print("="*80)
    print("Financial Agent 快速功能测试")
    print("="*80)
    
    total = 0
    passed = 0
    failed = 0
    
    # 测试用例 - 只测试基本功能
    test_cases = [
        # 正常用例
        {
            'query': '分析贵州茅台的财务健康度',
            'expected_success': True,
            'check_contains': ['财务健康度', '贵州茅台'],
            'category': '财务健康度分析'
        },
        {
            'query': '分析601318.SH的财务健康度',
            'expected_success': True,
            'check_contains': ['财务健康度', '601318.SH'],
            'category': '财务健康度分析'
        },
        {
            'query': '贵州茅台的杜邦分析',
            'expected_success': True,
            'check_contains': ['杜邦分析', 'ROE'],
            'category': '杜邦分析'
        },
        {
            'query': '分析万科A的现金流质量',
            'expected_success': True,
            'check_contains': ['现金流', '质量'],
            'category': '现金流分析'
        },
        {
            'query': '贵州茅台2025年一季度与去年同期对比',
            'expected_success': True,
            'check_contains': ['对比', '2025'],
            'category': '多期对比'
        },
        
        # 错误用例
        {
            'query': '茅台的财务健康度',
            'expected_success': False,
            'check_error': '股票简称',
            'category': '错误处理'
        },
        {
            'query': '',
            'expected_success': False,
            'check_error': '查询内容不能为空',
            'category': '错误处理'
        },
        {
            'query': '分析财务健康度',
            'expected_success': False,
            'check_error': '股票',
            'category': '错误处理'
        },
        {
            'query': '123456的财务分析',
            'expected_success': False,
            'check_error': '股票代码',
            'category': '错误处理'
        },
        {
            'query': '分析不存在公司的财务',
            'expected_success': False,
            'check_error': '找不到',
            'category': '错误处理'
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        total += 1
        query = test_case['query']
        expected_success = test_case['expected_success']
        category = test_case['category']
        
        print(f"\n测试 {i}/{len(test_cases)}: {category}")
        print(f"查询: {query}")
        print(f"预期: {'成功' if expected_success else '失败'}")
        
        start_time = time.time()
        try:
            # 设置超时，避免等待LLM太久
            result = agent.query(query)
            elapsed_time = time.time() - start_time
            
            success = result.get('success', False)
            
            # 如果成功但耗时超过5秒，可能在等待LLM，我们认为基本功能已通过
            if success and elapsed_time > 5:
                print("(注意：查询耗时较长，可能在等待LLM)")
            
            # 验证结果
            test_passed = success == expected_success
            
            # 额外检查
            if test_passed and expected_success:
                # 检查是否包含预期内容
                if 'check_contains' in test_case:
                    result_str = str(result.get('result', ''))
                    for keyword in test_case['check_contains']:
                        if keyword not in result_str:
                            test_passed = False
                            print(f"❌ 结果中未找到关键词: {keyword}")
                            break
            
            elif test_passed and not expected_success:
                # 检查错误信息
                if 'check_error' in test_case:
                    error_msg = str(result.get('error', ''))
                    if test_case['check_error'] not in error_msg:
                        test_passed = False
                        print(f"❌ 错误信息不符合预期: {error_msg}")
            
            if test_passed:
                passed += 1
                print(f"✅ 通过 (耗时: {elapsed_time:.2f}秒)")
            else:
                failed += 1
                print(f"❌ 失败")
                if success:
                    print(f"结果预览: {str(result.get('result', ''))[:100]}...")
                else:
                    print(f"错误: {result.get('error', '未知错误')}")
                    
        except Exception as e:
            failed += 1
            print(f"❌ 异常: {str(e)}")
    
    # 打印总结
    print("\n" + "="*80)
    print("测试总结")
    print(f"总测试数: {total}")
    print(f"通过: {passed}")
    print(f"失败: {failed}")
    print(f"通过率: {passed/total*100:.1f}%")
    
    # 保存测试报告
    report = {
        'test_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'total': total,
        'passed': passed,
        'failed': failed,
        'pass_rate': f"{passed/total*100:.1f}%"
    }
    
    with open('test_financial_agent_quick_report.json', 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    print(f"\n测试报告已保存到: test_financial_agent_quick_report.json")


if __name__ == "__main__":
    test_financial_agent()