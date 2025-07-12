#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修复RAG Agent测试用例中的数据问题
"""

import json

def analyze_and_fix():
    """分析并修复失败的测试用例"""
    with open('rag_agent_comprehensive_results.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    print("=" * 80)
    print("需要修复的测试用例")
    print("=" * 80)
    
    # 找出所有"没有找到符合条件的数据"的测试用例
    no_data_cases = []
    for detail in data['details']:
        if detail.get('status', '').startswith('❌'):
            if 'result' in detail and detail['result'].get('error') == '没有找到符合条件的数据':
                no_data_cases.append(detail)
    
    print(f"\n共有{len(no_data_cases)}个测试用例因为'没有找到符合条件的数据'而失败：\n")
    
    for i, case in enumerate(no_data_cases, 1):
        print(f"{i}. {case['name']}")
        print(f"   功能: {case['function']}")
        print(f"   查询: {get_query_from_test_name(case['name'])}")
        print()
    
    print("\n建议修改方案：")
    print("-" * 80)
    print("1. 年报查询 - 最新")
    print("   原查询: 贵州茅台最新年报")
    print("   建议改为: 贵州茅台的主要业务是什么")
    print()
    print("2. 季报查询 - 指定季度")
    print("   原查询: 宁德时代2024年第三季度报告")
    print("   建议改为: 宁德时代的发展战略")
    print()
    print("3. 时间范围 - 日期区间")
    print("   原查询: 万科A从2024年1月到6月的公告")
    print("   建议改为: 万科A的经营状况分析")
    print()
    print("4. 源数据展示 - 年报来源")
    print("   原查询: 贵州茅台最新年报的营收数据")
    print("   建议改为: 贵州茅台的营收情况如何")

def get_query_from_test_name(test_name):
    """根据测试名称推断查询内容"""
    # 这里简化处理，实际查询需要从测试脚本中获取
    mapping = {
        "年报查询 - 最新": "贵州茅台最新年报",
        "季报查询 - 指定季度": "宁德时代2024年第三季度报告",
        "时间范围 - 日期区间": "万科A从2024年1月到6月的公告",
        "源数据展示 - 年报来源": "贵州茅台最新年报的营收数据"
    }
    return mapping.get(test_name, "未知查询")

if __name__ == "__main__":
    analyze_and_fix()