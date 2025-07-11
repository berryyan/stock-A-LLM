#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Financial Agent 错误处理测试
专注于测试错误处理和参数验证，不等待LLM完成
"""
import sys
import os
import time
import json
from datetime import datetime

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.financial_agent_modular import FinancialAgentModular


def test_error_handling():
    """测试错误处理功能"""
    agent = FinancialAgentModular()
    
    print("="*80)
    print("Financial Agent 错误处理测试")
    print("="*80)
    
    total = 0
    passed = 0
    failed = 0
    
    # 错误处理测试用例
    error_test_cases = [
        {
            'query': '',
            'expected_error': '查询内容不能为空',
            'test_name': '空查询'
        },
        {
            'query': '   ',
            'expected_error': '查询内容不能为空',
            'test_name': '空白查询'
        },
        {
            'query': '茅台的财务健康度',
            'expected_error': '股票简称',
            'test_name': '股票简称错误'
        },
        {
            'query': '平安的财务分析',
            'expected_error': '股票简称',
            'test_name': '歧义股票名'
        },
        {
            'query': '123456的财务分析',
            'expected_error': '股票代码',
            'test_name': '错误代码格式'
        },
        {
            'query': '12345的财务健康度',
            'expected_error': '股票代码应为6位数字',
            'test_name': '5位代码'
        },
        {
            'query': '分析财务健康度',
            'expected_error': '股票',
            'test_name': '缺少股票'
        },
        {
            'query': '财务健康度',
            'expected_error': '股票',
            'test_name': '不完整查询'
        },
        {
            'query': '不存在公司的财务分析',
            'expected_error': '找不到',
            'test_name': '不存在的公司'
        },
        {
            'query': '600519.sh的财务健康度',
            'expected_error': '应为.SH',
            'test_name': '小写后缀'
        }
    ]
    
    # 参数识别测试用例（快速测试，仅检查参数提取）
    param_test_cases = [
        {
            'query': '贵州茅台2025年一季度与去年同期对比',
            'check_type': 'comparison',
            'test_name': '多期对比识别'
        },
        {
            'query': '万科A的杜邦分析',
            'check_type': 'dupont',
            'test_name': '杜邦分析识别'
        },
        {
            'query': '分析中国平安的现金流质量',
            'check_type': 'cash_flow',
            'test_name': '现金流分析识别'
        },
        {
            'query': '比亚迪的盈利能力',
            'check_type': 'profitability',
            'test_name': '盈利能力识别'
        },
        {
            'query': '宁德时代的偿债能力分析',
            'check_type': 'solvency',
            'test_name': '偿债能力识别'
        }
    ]
    
    # 1. 测试错误处理
    print("\n【错误处理测试】")
    for test_case in error_test_cases:
        total += 1
        query = test_case['query']
        expected_error = test_case['expected_error']
        test_name = test_case['test_name']
        
        print(f"\n测试: {test_name}")
        print(f"查询: '{query}'")
        
        try:
            result = agent.analyze(query)
            success = result.get('success', False)
            
            if not success:
                error_msg = result.get('error', '')
                if expected_error in error_msg:
                    passed += 1
                    print(f"✅ 通过 - 正确识别错误: {error_msg}")
                else:
                    failed += 1
                    print(f"❌ 失败 - 错误信息不符")
                    print(f"  预期包含: {expected_error}")
                    print(f"  实际错误: {error_msg}")
            else:
                failed += 1
                print(f"❌ 失败 - 应该返回错误但成功了")
                
        except Exception as e:
            failed += 1
            print(f"❌ 异常: {str(e)}")
    
    # 2. 测试分析类型识别（仅测试参数提取，不执行完整分析）
    print("\n\n【分析类型识别测试】")
    for test_case in param_test_cases:
        total += 1
        query = test_case['query']
        expected_type = test_case['check_type']
        test_name = test_case['test_name']
        
        print(f"\n测试: {test_name}")
        print(f"查询: '{query}'")
        
        try:
            # 仅测试分析类型识别
            analysis_type = agent._identify_analysis_type(query)
            
            if analysis_type == expected_type:
                passed += 1
                print(f"✅ 通过 - 正确识别为: {analysis_type}")
            else:
                failed += 1
                print(f"❌ 失败 - 识别错误")
                print(f"  预期: {expected_type}")
                print(f"  实际: {analysis_type}")
                
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
        'test_type': 'error_handling_and_params',
        'total': total,
        'passed': passed,
        'failed': failed,
        'pass_rate': f"{passed/total*100:.1f}%"
    }
    
    with open('test_financial_agent_errors_report.json', 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    print(f"\n测试报告已保存到: test_financial_agent_errors_report.json")


if __name__ == "__main__":
    test_error_handling()