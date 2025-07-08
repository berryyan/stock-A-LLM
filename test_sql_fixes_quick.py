#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
快速测试SQL Agent修复效果
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.sql_agent_modular import SQLAgentModular
from utils.logger import setup_logger

logger = setup_logger("test_sql_fixes")

def test_fixes():
    """测试主要修复功能"""
    print("SQL Agent修复测试")
    print("=" * 60)
    
    # 初始化Agent
    agent = SQLAgentModular()
    
    # 测试用例
    test_cases = [
        # 1. 测试PROFIT_LATEST模板
        ("贵州茅台的利润", "测试个股利润查询（PROFIT_LATEST模板）"),
        ("中国平安最新净利润", "测试净利润查询"),
        
        # 2. 测试MONEY_FLOW_RANKING_IN/OUT模板
        ("主力净流入排名前10", "测试主力净流入排名（MONEY_FLOW_RANKING_IN）"),
        ("主力净流出排名前10", "测试主力净流出排名（MONEY_FLOW_RANKING_OUT）"),
        
        # 3. 测试日期处理增强
        ("万科A6月的K线", "测试无年份月份处理"),
        ("宁德时代2025年第二季度的走势", "测试季度转日期范围"),
        
        # 4. 测试成交量默认日期
        ("万科A的成交量", "测试成交量查询使用默认日期"),
        
        # 5. 测试PE排名（None值处理）
        ("PE最高的10只股票", "测试PE排名格式化"),
    ]
    
    passed = 0
    failed = 0
    
    for query, description in test_cases:
        print(f"\n测试: {description}")
        print(f"查询: {query}")
        print("-" * 40)
        
        try:
            result = agent.query(query)
            if result.get('success'):
                print("✅ 成功")
                if result.get('result'):
                    # 只显示结果的前200个字符
                    preview = str(result['result'])[:200]
                    if len(str(result['result'])) > 200:
                        preview += "..."
                    print(f"结果预览: {preview}")
                passed += 1
            else:
                print(f"❌ 失败: {result.get('error', '未知错误')}")
                failed += 1
        except Exception as e:
            print(f"❌ 异常: {str(e)}")
            failed += 1
    
    print("\n" + "=" * 60)
    print(f"测试完成: {passed}通过, {failed}失败")
    print(f"通过率: {passed/(passed+failed)*100:.1f}%")
    
    return passed, failed

if __name__ == "__main__":
    test_fixes()