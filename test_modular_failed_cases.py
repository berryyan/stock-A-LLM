#!/usr/bin/env python3
"""测试模块化版本的3个失败用例"""

import sys
sys.path.append('.')

from agents.sql_agent_modular import SQLAgentModular
from agents.hybrid_agent_modular import HybridAgentModular

def test_failed_cases():
    """测试失败的3个用例"""
    # 使用模块化SQL Agent
    sql_agent = SQLAgentModular()
    hybrid_agent = HybridAgentModular()
    
    test_cases = [
        # 测试板块查询日期解析
        {
            "query": "银行板块昨天的主力资金",
            "agent": sql_agent,
            "expected": "板块查询成功",
            "category": "板块主力资金-时间指定"
        },
        {
            "query": "白酒板块今天的主力资金",
            "agent": sql_agent,
            "expected": "板块查询成功",
            "category": "板块主力资金-时间指定"
        },
        # 测试非标准术语
        {
            "query": "万科A的游资",
            "agent": hybrid_agent,  # 测试报告显示这是通过Hybrid Agent的
            "expected": "错误：非标准术语",
            "category": "个股主力资金-错误用例"
        }
    ]
    
    print("测试模块化版本失败用例")
    print("=" * 80)
    
    passed = 0
    failed = 0
    
    for i, test in enumerate(test_cases, 1):
        print(f"\n测试 {i}/{len(test_cases)}")
        print(f"类别: {test['category']}")
        print(f"查询: {test['query']}")
        print(f"期望: {test['expected']}")
        
        try:
            result = test['agent'].query(test['query'])
            
            if result['success']:
                print(f"结果: 成功")
                
                # 检查具体期望
                if test['expected'] == "板块查询成功":
                    # 检查结果中是否包含板块相关内容
                    result_text = str(result.get('result', ''))
                    if '板块' in result_text or '净流入' in result_text:
                        print("✅ 通过 - 包含板块资金数据")
                        passed += 1
                    else:
                        print("❌ 失败 - 未包含板块数据")
                        print(f"实际结果: {result_text[:200]}...")
                        failed += 1
                        
                elif test['expected'] == "错误：非标准术语":
                    print("❌ 失败 - 应该返回错误但成功了")
                    print(f"实际结果: {str(result.get('result', ''))[:200]}...")
                    failed += 1
                    
            else:
                error_msg = result.get('error', '')
                print(f"结果: 失败 - {error_msg}")
                
                if test['expected'] == "错误：非标准术语":
                    if '标准术语' in error_msg or '游资' in error_msg:
                        print("✅ 通过 - 正确识别非标准术语")
                        passed += 1
                    else:
                        print("❌ 失败 - 错误消息不匹配")
                        failed += 1
                        
                elif test['expected'] == "板块查询成功":
                    print("❌ 失败 - 板块查询应该成功")
                    failed += 1
                    
        except Exception as e:
            print(f"异常: {str(e)}")
            print("❌ 失败")
            failed += 1
    
    print(f"\n{'='*80}")
    print(f"测试完成: 通过 {passed}/{len(test_cases)}, 失败 {failed}/{len(test_cases)}")
    
    # 如果全部通过，说明问题可能在老版本API
    if passed == len(test_cases):
        print("\n⚠️ 注意：模块化版本全部测试通过！")
        print("测试报告中的失败可能来自老版本API（端口8000）")
        print("建议：")
        print("1. 确认测试报告是使用哪个API版本生成的")
        print("2. 如果是老版本，考虑是否需要修复老版本或只关注模块化版本")

if __name__ == "__main__":
    test_failed_cases()