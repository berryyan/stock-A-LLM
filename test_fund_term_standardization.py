#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试资金类型术语标准化功能
"""

from agents.money_flow_agent import MoneyFlowAgent
import time


def test_fund_term_standardization():
    """测试资金术语标准化"""
    
    print("=" * 80)
    print("资金类型术语标准化测试")
    print("=" * 80)
    
    # 测试用例设计
    test_cases = {
        "正向测试 - 非标准术语转换": [
            # (输入查询, 期望包含的标准术语, 期望的提示信息)
            ("贵州茅台的游资流入情况", "主力资金", "游资"),
            ("平安银行的庄家资金", "主力资金", "庄家"),
            ("比亚迪的散户资金流向", "小单", "散户"),
            ("大户资金买入万科", "大单", "大户"),
            ("招商银行的热钱流入", "主力资金", "热钱"),
            ("中国平安的机构资金", "超大单", "机构"),
        ],
        
        "边界测试 - 混合术语": [
            ("分析茅台的游资和散户资金", ["主力资金", "小单"], ["游资", "散户"]),
            ("庄家和大户同时买入平安银行", ["主力资金", "大单"], ["庄家", "大户"]),
        ],
        
        "错误测试 - 无法识别的术语": [
            # (输入查询, 期望失败, 期望错误信息包含)
            ("贵州茅台的外星人资金", False, "无法识别"),
            ("平安银行的神秘资金流向", False, "请使用以下标准术语"),
            ("比亚迪的不知道什么资金", False, "标准术语"),
        ],
        
        "兼容测试 - 标准术语直接使用": [
            # 使用标准术语应该正常工作，无需转换
            ("贵州茅台的主力资金流向", True, None),
            ("平安银行的超大单资金", True, None),
            ("比亚迪的小单资金流出", True, None),
        ]
    }
    
    # 初始化agent
    agent = MoneyFlowAgent()
    
    # 执行测试
    results = {
        "passed": 0,
        "failed": 0,
        "details": []
    }
    
    for category, cases in test_cases.items():
        print(f"\n### {category}")
        print("-" * 60)
        
        for test_case in cases:
            if category == "正向测试 - 非标准术语转换":
                query, expected_term, expected_hint = test_case
                print(f"\n测试: {query}")
                print(f"期望: 转换为'{expected_term}'，提示包含'{expected_hint}'")
                
                # 测试标准化功能（如果已实现）
                try:
                    # 这里需要调用实际的标准化函数
                    # standardized_query, hint = agent.standardize_fund_terms(query)
                    # 目前先模拟
                    print("⚠️ 标准化功能尚未实现")
                    results["failed"] += 1
                except Exception as e:
                    print(f"❌ 异常: {e}")
                    results["failed"] += 1
                    
            elif category == "错误测试 - 无法识别的术语":
                query, should_fail, error_keyword = test_case
                print(f"\n测试: {query}")
                print(f"期望: 应该失败并提示'{error_keyword}'")
                
                try:
                    result = agent.query(query)
                    if not result['success']:
                        if error_keyword in result.get('error', ''):
                            print(f"✅ 正确处理无法识别的术语")
                            results["passed"] += 1
                        else:
                            print(f"❌ 错误信息不符合预期")
                            results["failed"] += 1
                    else:
                        print(f"❌ 应该失败但成功了")
                        results["failed"] += 1
                except Exception as e:
                    print(f"❌ 异常: {e}")
                    results["failed"] += 1
    
    # 测试报告
    print("\n" + "=" * 80)
    print("测试结果汇总")
    print("=" * 80)
    print(f"通过: {results['passed']}")
    print(f"失败: {results['failed']}")
    print(f"总计: {results['passed'] + results['failed']}")
    
    # 实现建议
    print("\n" + "=" * 80)
    print("实现建议")
    print("=" * 80)
    print("""
1. 在MoneyFlowAgent中添加standardize_fund_terms方法
2. 创建FUND_TYPE_MAPPING字典进行术语映射
3. 在query方法开始处调用标准化函数
4. 对无法识别的术语提供清晰的错误提示
5. 在返回结果中包含术语转换的提示信息

示例实现：
```python
FUND_TYPE_MAPPING = {
    "游资": "主力资金",
    "庄家": "主力资金",
    "散户": "小单",
    "大户": "大单",
    "机构": "超大单",
    "热钱": "主力资金",
}

def standardize_fund_terms(self, query: str) -> tuple[str, list[str]]:
    standardized = query
    hints = []
    
    for non_standard, standard in FUND_TYPE_MAPPING.items():
        if non_standard in query:
            standardized = standardized.replace(non_standard, standard)
            hints.append(f"'{non_standard}'已转换为标准术语'{standard}'")
    
    return standardized, hints
```
    """)


if __name__ == "__main__":
    test_fund_term_standardization()