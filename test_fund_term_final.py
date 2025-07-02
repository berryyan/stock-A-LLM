#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试资金术语标准化功能 - 最终验证
"""

from agents.money_flow_agent import MoneyFlowAgent
import time


def test_standardization():
    """测试术语标准化功能"""
    
    print("=" * 80)
    print("资金术语标准化功能测试")
    print("=" * 80)
    
    agent = MoneyFlowAgent()
    
    # 1. 测试标准化方法
    print("\n### 1. 测试standardize_fund_terms方法")
    print("-" * 60)
    
    test_terms = [
        "贵州茅台的游资流入",
        "平安银行的散户资金",
        "比亚迪的庄家和大户资金",
        "招商银行的机构资金流向",
    ]
    
    for query in test_terms:
        standardized, hints = agent.standardize_fund_terms(query)
        print(f"\n原始查询: {query}")
        print(f"标准化后: {standardized}")
        print(f"转换提示: {hints}")
    
    # 2. 测试查询识别
    print("\n\n### 2. 测试is_money_flow_query识别")
    print("-" * 60)
    
    test_queries = [
        ("贵州茅台的游资流入", True),
        ("平安银行的散户资金", True),
        ("比亚迪的外星人资金", False),
        ("贵州茅台的主力资金", True),
    ]
    
    for query, expected in test_queries:
        is_money_flow = agent.is_money_flow_query(query)
        status = "✅" if is_money_flow == expected else "❌"
        print(f"{status} '{query}' -> {is_money_flow} (期望: {expected})")
    
    # 3. 测试完整查询流程
    print("\n\n### 3. 测试完整查询流程")
    print("-" * 60)
    
    # 3.1 正向测试 - 术语转换
    print("\n#### 3.1 正向测试 - 非标准术语")
    test_query = "贵州茅台的游资流入情况"
    print(f"查询: {test_query}")
    
    try:
        result = agent.query(test_query)
        if result['success']:
            print("✅ 查询成功")
            if 'term_hints' in result and result['term_hints']:
                print(f"术语提示: {result['term_hints']}")
            # 检查结果中是否包含提示
            if '术语提示' in result.get('answer', ''):
                print("✅ 结果中包含术语转换提示")
            else:
                print("⚠️ 结果中未包含术语转换提示")
        else:
            print(f"❌ 查询失败: {result.get('error')}")
    except Exception as e:
        print(f"❌ 异常: {e}")
    
    # 3.2 错误测试 - 无法识别的术语
    print("\n#### 3.2 错误测试 - 无法识别的术语")
    test_query = "平安银行的外星人资金流向"
    print(f"查询: {test_query}")
    
    try:
        result = agent.query(test_query)
        if not result['success']:
            print("✅ 正确拒绝无法识别的查询")
            error = result.get('error', '')
            if '标准资金类型术语' in error:
                print("✅ 提供了标准术语说明")
                print(f"错误信息预览: {error[:100]}...")
            else:
                print("⚠️ 错误信息未包含标准术语说明")
        else:
            print("❌ 不应该成功")
    except Exception as e:
        print(f"❌ 异常: {e}")
    
    # 3.3 兼容测试 - 标准术语
    print("\n#### 3.3 兼容测试 - 标准术语")
    test_query = "贵州茅台的主力资金流向"
    print(f"查询: {test_query}")
    
    try:
        result = agent.query(test_query)
        if result['success']:
            print("✅ 标准术语查询成功")
            if 'term_hints' in result and not result['term_hints']:
                print("✅ 无术语转换提示（符合预期）")
        else:
            print(f"❌ 查询失败: {result.get('error')}")
    except Exception as e:
        print(f"❌ 异常: {e}")


def test_mapping_coverage():
    """测试术语映射覆盖度"""
    
    print("\n\n" + "=" * 80)
    print("术语映射覆盖度测试")
    print("=" * 80)
    
    agent = MoneyFlowAgent()
    
    print(f"\n当前术语映射数量: {len(agent.FUND_TYPE_MAPPING)}")
    print("\n映射详情:")
    for non_standard, standard in sorted(agent.FUND_TYPE_MAPPING.items()):
        print(f"  {non_standard:12} -> {standard}")


if __name__ == "__main__":
    test_standardization()
    test_mapping_coverage()