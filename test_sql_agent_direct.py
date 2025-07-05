#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
直接测试SQL Agent模块化版本
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.sql_agent_modular import SQLAgentModular

def test_direct():
    """直接测试SQL Agent"""
    # 创建SQL Agent实例
    agent = SQLAgentModular()
    
    # 测试用例
    test_cases = [
        "600519.SH的股价",
        "平安银行昨天的成交量",
        "中国平安的市盈率",
        "贵州茅台的主力资金"
    ]
    
    for query in test_cases:
        print(f"\n{'='*60}")
        print(f"查询: {query}")
        print('='*60)
        
        try:
            result = agent.query(query)
            print(f"返回类型: {type(result)}")
            print(f"返回键: {list(result.keys()) if isinstance(result, dict) else 'Not a dict'}")
            print(f"成功: {result.get('success', 'N/A')}")
            
            if result.get('success'):
                print(f"结果: {result.get('result', '')[:200]}...")
            else:
                print(f"错误: {result.get('error', 'Unknown error')}")
                
        except Exception as e:
            print(f"异常: {str(e)}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    test_direct()