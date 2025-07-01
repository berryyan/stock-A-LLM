#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试K线查询统一日期模块修复
验证用户指定的天数能正确返回对应天数的数据
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.query_templates import QueryTemplateLibrary
from agents.sql_agent import SQLAgent

def test_unified_kline_fix():
    """测试统一日期模块修复"""
    print("测试K线查询统一日期模块修复")
    print("=" * 60)
    
    # 初始化组件
    query_templates = QueryTemplateLibrary()
    sql_agent = SQLAgent()
    
    test_cases = [
        ("中国平安最近10天的K线", 10),
        ("万科A最近5天的K线", 5),
        ("比亚迪过去20天的K线", 20),
        ("贵州茅台最近30天的K线", 30),
        ("平安银行的K线", 90),  # 默认值
    ]
    
    print("\n1. 测试参数提取修复")
    print("-" * 40)
    
    for query, expected_days in test_cases:
        print(f"\n查询: {query}")
        print(f"期望天数: {expected_days}")
        
        # 测试模板匹配和参数提取
        template = query_templates.match_template(query)
        if template:
            print(f"✅ 匹配模板: {template.name}")
            
            params = query_templates.extract_params(query, template)
            extracted_days = params.get('days', 90)
            print(f"提取天数: {extracted_days}")
            
            if extracted_days == expected_days:
                print("✅ 天数提取正确")
            else:
                print("❌ 天数提取错误")
        else:
            print("❌ 模板匹配失败")
        
        print("-" * 20)
    
    print("\n2. 测试快速路由完整流程")
    print("-" * 40)
    
    for query, expected_days in test_cases[:3]:  # 只测试前3个，避免长时间运行
        print(f"\n查询: {query}")
        
        result = sql_agent._try_quick_query(query)
        if result and result.get('success'):
            print("✅ 快速路由成功")
            content = result['result']
            
            # 检查输出中的天数描述
            if f"最近{expected_days}天" in content:
                print("✅ 输出天数描述正确")
            elif "从" in content and "到" in content:
                print("✅ 使用日期范围格式")
            else:
                print("⚠️ 输出格式需要检查")
                print(f"输出预览: {content[:200]}...")
        else:
            print("❌ 快速路由失败")
        
        print("-" * 20)
    
    print("\n3. 测试日期智能模块直接调用")
    print("-" * 40)
    
    from utils.date_intelligence import date_intelligence
    
    for days in [5, 10, 20, 30]:
        print(f"\n测试获取最近{days}天交易日范围")
        date_range = date_intelligence.calculator.get_trading_days_range(days)
        if date_range:
            start_date, end_date = date_range
            print(f"✅ 范围: {start_date} 至 {end_date}")
        else:
            print("❌ 获取日期范围失败")
    
    print("\n测试完成！")

if __name__ == "__main__":
    test_unified_kline_fix()