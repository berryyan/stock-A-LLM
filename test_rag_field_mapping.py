#!/usr/bin/env python3
"""
快速测试RAG Agent字段映射修复
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.rag_agent_modular import RAGAgentModular

def test_filter_expression():
    """测试过滤表达式构建"""
    print("测试RAG Agent模块化版本 - 过滤表达式构建")
    print("=" * 60)
    
    # 初始化Agent
    rag_agent = RAGAgentModular()
    
    # 测试不同的过滤条件
    test_cases = [
        {
            "name": "股票过滤",
            "filter_dict": {
                "stock_filter": ["600519.SH", "000858.SZ", "002594.SZ"]
            },
            "expected": '(ts_code == "600519.SH" or ts_code == "000858.SZ" or ts_code == "002594.SZ")'
        },
        {
            "name": "日期过滤",
            "filter_dict": {
                "date": "2025-07-05"
            },
            "expected": 'ann_date == "2025-07-05"'
        },
        {
            "name": "日期范围过滤",
            "filter_dict": {
                "date_range": ("2025-07-01", "2025-07-05")
            },
            "expected": 'ann_date >= "2025-07-01" and ann_date <= "2025-07-05"'
        },
        {
            "name": "复合过滤",
            "filter_dict": {
                "stock_filter": ["600519.SH"],
                "date": "2025-07-05"
            },
            "expected": '(ts_code == "600519.SH") and ann_date == "2025-07-05"'
        }
    ]
    
    all_passed = True
    
    for test_case in test_cases:
        print(f"\n测试: {test_case['name']}")
        print(f"输入: {test_case['filter_dict']}")
        
        # 构建过滤表达式
        expr = rag_agent._build_milvus_expr(test_case['filter_dict'])
        
        print(f"输出: {expr}")
        print(f"期望: {test_case['expected']}")
        
        if expr == test_case['expected']:
            print("✓ 通过")
        else:
            print("✗ 失败")
            all_passed = False
    
    print("\n" + "=" * 60)
    if all_passed:
        print("✓ 所有测试通过！字段映射已正确修复。")
    else:
        print("✗ 部分测试失败，请检查实现。")
    
    return all_passed

if __name__ == "__main__":
    test_filter_expression()