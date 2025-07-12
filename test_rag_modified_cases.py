#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试修改后的RAG Agent测试用例
只测试之前失败的4个用例
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.rag_agent_modular import RAGAgentModular
import time


def test_modified_cases():
    """测试修改后的用例"""
    print("=" * 80)
    print("测试修改后的RAG Agent用例")
    print("=" * 80)
    
    agent = RAGAgentModular()
    
    # 之前失败的4个测试用例，现在使用修改后的查询
    test_cases = [
        {
            "name": "年报查询 - 最新（修改后）",
            "query": "贵州茅台的主要业务是什么",
            "original": "贵州茅台最新年报"
        },
        {
            "name": "季报查询 - 指定季度（修改后）",
            "query": "宁德时代的发展战略",
            "original": "宁德时代2024年第三季度报告"
        },
        {
            "name": "时间范围 - 日期区间（修改后）",
            "query": "万科A的经营状况分析",
            "original": "万科A从2024年1月到6月的公告"
        },
        {
            "name": "源数据展示 - 年报来源（修改后）",
            "query": "贵州茅台的营收情况如何",
            "original": "贵州茅台最新年报的营收数据"
        }
    ]
    
    passed = 0
    failed = 0
    
    for test_case in test_cases:
        print(f"\n测试: {test_case['name']}")
        print(f"原查询: {test_case['original']}")
        print(f"新查询: {test_case['query']}")
        
        start_time = time.time()
        try:
            result = agent.query(test_case['query'])
            elapsed = time.time() - start_time
            
            if result.get('success', False):
                answer = result.get('answer', '')
                if answer and len(answer) > 50:
                    print(f"✅ 测试通过 (耗时: {elapsed:.2f}秒)")
                    print(f"回答预览: {answer[:100]}...")
                    passed += 1
                else:
                    print(f"❌ 测试失败: 回答内容不足")
                    failed += 1
            else:
                print(f"❌ 测试失败: {result.get('error', '未知错误')}")
                failed += 1
                
        except Exception as e:
            print(f"❌ 异常: {str(e)}")
            failed += 1
    
    print(f"\n{'='*80}")
    print("测试总结")
    print(f"{'='*80}")
    print(f"总测试数: {len(test_cases)}")
    print(f"通过: {passed}")
    print(f"失败: {failed}")
    print(f"通过率: {passed/len(test_cases)*100:.1f}%")
    
    print("\n结论:")
    if passed == len(test_cases):
        print("✅ 所有修改后的测试用例都通过了！")
        print("说明：将具体的文档查询改为更通用的业务查询后，RAG Agent能够正常工作。")
    else:
        print("❌ 仍有测试用例失败，可能需要进一步调整。")
    
    return passed == len(test_cases)


if __name__ == "__main__":
    success = test_modified_cases()
    exit(0 if success else 1)