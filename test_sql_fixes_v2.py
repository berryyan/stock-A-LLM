#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试SQL Agent字段修复效果 v2
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.sql_agent_modular import SQLAgentModular
from utils.logger import setup_logger

logger = setup_logger("test_sql_fixes_v2")

def test_fixes():
    """测试字段修复后的功能"""
    print("SQL Agent字段修复测试 v2")
    print("=" * 60)
    
    # 初始化Agent
    agent = SQLAgentModular()
    
    # 测试用例
    test_cases = [
        # 1. 测试利润查询（修复n_income/net_profit字段问题）
        {
            "query": "贵州茅台的利润",
            "description": "测试个股利润查询（PROFIT_LATEST模板）",
            "expected_fields": ["净利润", "营业收入"]
        },
        {
            "query": "中国平安最新净利润",
            "description": "测试净利润查询",
            "expected_fields": ["净利润"]
        },
        
        # 2. 测试资金流向排名（修复net_mf_amount/net_amount字段问题）
        {
            "query": "主力净流入排名前5",
            "description": "测试主力净流入排名（MONEY_FLOW_RANKING_IN）",
            "expected_fields": ["主力净流入"]
        },
        {
            "query": "主力净流出排名前5",
            "description": "测试主力净流出排名（MONEY_FLOW_RANKING_OUT）",
            "expected_fields": ["主力净流入"]  # 显示为负值
        },
        
        # 3. 额外测试其他功能
        {
            "query": "万科A6月的K线",
            "description": "测试无年份月份处理",
            "expected_fields": ["日期", "收盘"]
        },
        {
            "query": "PE最高的5只股票",
            "description": "测试PE排名（None值处理）",
            "expected_fields": ["PE"]
        },
    ]
    
    passed = 0
    failed = 0
    details = []
    
    for test_case in test_cases:
        query = test_case["query"]
        description = test_case["description"]
        expected_fields = test_case.get("expected_fields", [])
        
        print(f"\n测试: {description}")
        print(f"查询: {query}")
        print("-" * 40)
        
        try:
            result = agent.query(query)
            if result.get('success'):
                print("✅ 查询成功")
                result_str = str(result.get('result', ''))
                
                # 检查预期字段是否出现在结果中
                missing_fields = []
                for field in expected_fields:
                    if field not in result_str:
                        missing_fields.append(field)
                
                if missing_fields:
                    print(f"⚠️  缺少预期字段: {', '.join(missing_fields)}")
                    details.append(f"{query}: 缺少字段 {missing_fields}")
                
                # 显示结果预览
                if result_str:
                    lines = result_str.split('\n')
                    preview_lines = lines[:10]  # 显示前10行
                    if len(lines) > 10:
                        preview_lines.append(f"... (还有{len(lines)-10}行)")
                    print("结果预览:")
                    for line in preview_lines:
                        print(f"  {line}")
                
                passed += 1
            else:
                error = result.get('error', '未知错误')
                print(f"❌ 查询失败: {error}")
                details.append(f"{query}: {error}")
                failed += 1
        except Exception as e:
            print(f"❌ 异常: {str(e)}")
            details.append(f"{query}: 异常 - {str(e)}")
            failed += 1
    
    print("\n" + "=" * 60)
    print(f"测试完成: {passed}通过, {failed}失败")
    print(f"通过率: {passed/(passed+failed)*100:.1f}%")
    
    if details:
        print("\n详细问题:")
        for detail in details:
            print(f"  - {detail}")
    
    return passed, failed

if __name__ == "__main__":
    test_fixes()