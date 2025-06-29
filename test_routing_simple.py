#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
简单测试路由机制
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 只测试触发词检测，不需要初始化整个Agent
def test_trigger_detection():
    """测试触发词检测逻辑"""
    print("=== 测试触发词检测 ===\n")
    
    # 模拟触发词检测逻辑
    trigger_mapping = {
        "排行分析：": "rank",
        "查询公告：": "anns",
        "董秘互动：": "qa"
    }
    
    test_cases = [
        ("排行分析：今日涨幅前10的股票", "rank"),
        ("查询公告：贵州茅台最新年报", "anns"),
        ("董秘互动：平安银行分红计划", "qa"),
        ("贵州茅台最新股价", None),
        ("分析茅台财务健康度", None),
    ]
    
    for question, expected in test_cases:
        detected = None
        for trigger, query_type in trigger_mapping.items():
            if question.startswith(trigger):
                detected = query_type
                break
        
        print(f"问题: {question}")
        print(f"期望: {expected}")
        print(f"检测: {detected}")
        print(f"结果: {'✅ 正确' if detected == expected else '❌ 错误'}")
        print("-" * 50)

if __name__ == "__main__":
    test_trigger_detection()