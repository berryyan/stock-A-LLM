#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试Financial Agent验证逻辑 - 建立基准预期
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.financial_agent import FinancialAnalysisAgent

def test_financial_agent_baseline():
    """测试Financial Agent建立验证基准"""
    print("=" * 80)
    print("测试Financial Agent验证逻辑 - 建立基准预期")
    print("=" * 80)
    
    # 初始化Financial Agent
    try:
        financial_agent = FinancialAnalysisAgent()
        print("✅ Financial Agent初始化成功")
    except Exception as e:
        print(f"❌ Financial Agent初始化失败: {e}")
        return
    
    # 全面的测试用例
    test_cases = [
        # 1. 正确案例
        ("贵州茅台财务健康度", "✅应该成功"),
        ("600519财务健康度", "✅应该成功"),
        ("600519.SH财务健康度", "✅应该成功"),
        ("中国平安财务健康度", "✅应该成功"),
        ("000001.SZ财务健康度", "✅应该成功"),
        
        # 2. 3字股票
        ("一品红财务健康度", "✅应该成功"),
        ("七匹狼财务健康度", "✅应该成功"),
        
        # 3. ST股票
        ("*ST国华财务健康度", "✅应该成功"),
        
        # 4. BJ市场股票
        ("831726.BJ财务健康度", "✅应该成功"),
        
        # 5. 简称（应该失败）
        ("茅台财务健康度", "❌应该失败-简称"),
        ("平安财务健康度", "❌应该失败-简称"),
        
        # 6. 不完整名称（应该失败）
        ("贵州茅财务健康度", "❌应该失败-不完整"),
        
        # 7. 错误位数代码
        ("60051财务健康度", "❌应该失败-位数不对"),
        ("1234567财务健康度", "❌应该失败-位数过多"),
        ("12345财务健康度", "❌应该失败-位数不足"),
        
        # 8. 错误后缀
        ("600519.XX财务健康度", "❌应该失败-错误后缀"),
        ("600519.AB财务健康度", "❌应该失败-错误后缀"),
        ("831726.BJJ财务健康度", "❌应该失败-BJ错拼"),
        ("831726.B财务健康度", "❌应该失败-BJ错拼"),
        ("831726.BK财务健康度", "❌应该失败-BJ错拼"),
        
        # 9. 数字位数正确但代码不存在
        ("123456.SH财务健康度", "❌应该失败-代码不存在"),
        ("999999.SZ财务健康度", "❌应该失败-代码不存在"),
        ("888888.BJ财务健康度", "❌应该失败-代码不存在"),
        
        # 10. 空输入
        ("", "❌应该失败-空输入"),
        ("   ", "❌应该失败-纯空格"),
        
        # 11. 无股票实体
        ("财务健康度分析", "❌应该失败-无股票实体"),
        ("最新的财务分析", "❌应该失败-无股票实体"),
    ]
    
    print(f"\n开始测试 {len(test_cases)} 个测试用例...\n")
    
    baseline_results = {}
    
    for i, (test_case, expectation) in enumerate(test_cases, 1):
        print(f"测试 {i:2d}: {test_case:<30} | 预期: {expectation}")
        
        try:
            result = financial_agent.query(test_case)
            success = result.get('success', False)
            error = result.get('error', 'No error message')
            
            # 记录到基准结果
            baseline_results[test_case] = {
                'success': success,
                'error': error,
                'expectation': expectation
            }
            
            # 显示结果
            if success:
                print(f"        结果: ✅ 成功")
            else:
                print(f"        结果: ❌ 失败 - {error}")
                
        except Exception as e:
            baseline_results[test_case] = {
                'success': False,
                'error': f"异常: {str(e)}",
                'expectation': expectation
            }
            print(f"        结果: ❌ 异常 - {str(e)[:50]}...")
        
        print()
    
    # 分析结果
    print("=" * 80)
    print("基准验证结果分析")
    print("=" * 80)
    
    should_succeed = [case for case, exp in test_cases if "✅应该成功" in exp]
    should_fail = [case for case, exp in test_cases if "❌应该失败" in exp]
    
    succeed_results = [(case, baseline_results[case]['success']) for case in should_succeed]
    fail_results = [(case, baseline_results[case]['success']) for case in should_fail]
    
    print(f"\n应该成功的用例 ({len(should_succeed)}个):")
    for case, actual_success in succeed_results:
        status = "✅ 正确" if actual_success else "❌ 错误"
        print(f"  {status} | {case}")
    
    print(f"\n应该失败的用例 ({len(should_fail)}个):")
    for case, actual_success in fail_results:
        status = "✅ 正确" if not actual_success else "❌ 错误"
        print(f"  {status} | {case}")
    
    # 统计
    correct_succeed = sum(1 for _, success in succeed_results if success)
    correct_fail = sum(1 for _, success in fail_results if not success)
    total_correct = correct_succeed + correct_fail
    
    print(f"\n📊 统计结果:")
    print(f"  应该成功且实际成功: {correct_succeed}/{len(should_succeed)}")
    print(f"  应该失败且实际失败: {correct_fail}/{len(should_fail)}")
    print(f"  总体正确率: {total_correct}/{len(test_cases)} ({total_correct/len(test_cases)*100:.1f}%)")
    
    # 保存基准结果
    import json
    with open('/tmp/financial_agent_baseline.json', 'w', encoding='utf-8') as f:
        json.dump(baseline_results, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ 基准结果已保存到 /tmp/financial_agent_baseline.json")
    print("这些结果将作为其他Agent的验证标准！")
    
    return baseline_results

if __name__ == "__main__":
    test_financial_agent_baseline()