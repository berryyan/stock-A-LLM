#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
SQL快速路由修复验证测试
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.sql_agent import SQLAgent
from utils.query_templates import match_query_template
from utils.date_intelligence import date_intelligence
import json

def test_specific_queries():
    """测试特定的5个问题查询"""
    sql_agent = SQLAgent()
    
    test_cases = [
        ("中国平安最近10天的K线", "K线查询"),
        ("平安银行的市盈率", "估值指标查询"), 
        ("市值最大的前10只股票", "总市值排名"),
        ("主力净流入排行前10", "主力净流入排行"),
        ("成交额最大的前10只股票", "成交额排名"),
    ]
    
    print("快速路由修复验证测试")
    print("=" * 60)
    
    for query, expected_template in test_cases:
        print(f"\n查询: {query}")
        print(f"期望模板: {expected_template}")
        
        # 1. 测试模板匹配
        processed_query, date_info = date_intelligence.preprocess_question(query)
        print(f"日期处理后: {processed_query}")
        
        match_result = match_query_template(processed_query)
        if match_result:
            template, params = match_result
            print(f"✅ 模板匹配: {template.name}")
            print(f"参数: {json.dumps(params, ensure_ascii=False)}")
            
            # 2. 测试快速路由
            quick_result = sql_agent._try_quick_query(query)
            if quick_result and quick_result.get('success'):
                print(f"✅ 快速路由成功")
                print(f"结果预览: {quick_result['result'][:100]}...")
            else:
                print(f"❌ 快速路由失败: {quick_result}")
                
                # 尝试调试原因
                print("调试信息:")
                print(f"  - 模板名称: {template.name}")
                print(f"  - 路由类型: {template.route_type}")
                print(f"  - 参数提取: {params}")
        else:
            print("❌ 模板匹配失败")
        
        print("-" * 40)

if __name__ == "__main__":
    test_specific_queries()