#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SQL Agent模块化版本简单测试
只测试最基本的功能
"""

import sys
import os
import time

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.sql_agent_modular import SQLAgentModular

def test_simple():
    """测试简单用例"""
    agent = SQLAgentModular()
    
    # 简单测试用例
    test_cases = [
        # 股价查询
        ("贵州茅台的最新股价", "股价查询"),
        # 成交量查询
        ("平安银行昨天的成交量", "成交量查询"),
        # K线查询
        ("贵州茅台最近10天的K线", "K线查询"),
        # 成交额排名
        ("成交额排名前10", "成交额排名"),
    ]
    
    print("="*60)
    print("SQL Agent模块化版本简单测试")
    print("="*60)
    
    for query, test_name in test_cases:
        print(f"\n测试: {test_name}")
        print(f"查询: {query}")
        print("-"*40)
        
        start_time = time.time()
        try:
            result = agent.query(query)
            elapsed_time = time.time() - start_time
            
            if result.get('success'):
                print(f"✅ 成功 (耗时: {elapsed_time:.2f}秒)")
                result_text = str(result.get('result', ''))
                if len(result_text) > 100:
                    print(f"结果: {result_text[:100]}...")
                else:
                    print(f"结果: {result_text}")
            else:
                print(f"❌ 失败: {result.get('error', '未知错误')}")
                
        except Exception as e:
            print(f"❌ 异常: {str(e)}")


if __name__ == "__main__":
    test_simple()