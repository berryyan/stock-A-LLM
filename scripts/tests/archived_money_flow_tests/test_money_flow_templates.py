#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试资金流向相关模板的匹配情况
验证个股查询与分析查询的正确区分
"""

from utils.query_templates import match_query_template

def test_money_flow_templates():
    """测试资金流向相关模板"""
    
    print("=" * 60)
    print("资金流向模板匹配测试")
    print("=" * 60)
    
    # 测试用例
    test_cases = [
        # 个股主力资金查询（应该匹配"个股主力资金"模板，路由到SQL_ONLY）
        ("贵州茅台的主力净流入", "个股主力资金", "SQL_ONLY"),
        ("平安银行的主力资金", "个股主力资金", "SQL_ONLY"),
        ("比亚迪的主力资金流入", "个股主力资金", "SQL_ONLY"),
        ("中国平安的主力资金流出", "个股主力资金", "SQL_ONLY"),
        ("万科的机构资金", "个股主力资金", "SQL_ONLY"),
        ("招商银行的大资金流向", "个股主力资金", "SQL_ONLY"),
        
        # 资金流向分析（应该匹配"资金流向分析"模板，路由到MONEY_FLOW）
        ("分析比亚迪的资金流向", "资金流向分析", "MONEY_FLOW"),
        ("茅台的资金流向如何", "资金流向分析", "MONEY_FLOW"),
        ("平安银行的主力资金流向分析", "资金流向分析", "MONEY_FLOW"),
        ("贵州茅台的主力资金分析", "资金流向分析", "MONEY_FLOW"),
        ("万科的资金流向怎么样", "资金流向分析", "MONEY_FLOW"),
        
        # 超大单分析（应该匹配"超大单分析"模板，路由到MONEY_FLOW）
        ("贵州茅台的超大单资金流入情况", "超大单分析", "MONEY_FLOW"),
        ("分析平安银行的超大单", "超大单分析", "MONEY_FLOW"),
        ("比亚迪的机构资金分析", "超大单分析", "MONEY_FLOW"),
        ("万科的超大单如何", "超大单分析", "MONEY_FLOW"),
        
        # 排名查询（不应该匹配资金流向模板）
        ("主力净流入最多的前10只股票", None, None),
        ("主力资金净流入排名", None, None),
        ("主力净流出前20", None, None),
    ]
    
    passed = 0
    failed = 0
    
    for query, expected_template, expected_route in test_cases:
        print(f"\n测试查询: {query}")
        result = match_query_template(query)
        
        if result:
            template, params = result
            print(f"  匹配模板: {template.name}")
            print(f"  路由类型: {template.route_type}")
            
            # 检查是否符合预期
            if expected_template:
                if template.name == expected_template and template.route_type == expected_route:
                    print("  ✅ 匹配正确")
                    passed += 1
                else:
                    print(f"  ❌ 匹配错误！预期: {expected_template}/{expected_route}")
                    failed += 1
            else:
                print("  ❌ 不应该匹配任何资金流向模板")
                failed += 1
        else:
            if expected_template is None:
                print("  ✅ 正确：未匹配任何模板")
                passed += 1
            else:
                print(f"  ❌ 未匹配到模板！预期: {expected_template}")
                failed += 1
    
    print(f"\n\n测试结果汇总:")
    print(f"通过: {passed}/{len(test_cases)}")
    print(f"失败: {failed}/{len(test_cases)}")
    print(f"成功率: {passed/len(test_cases)*100:.1f}%")
    
    return passed, failed


if __name__ == "__main__":
    test_money_flow_templates()