#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""调试Money Flow Agent失败的测试用例"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.money_flow_agent_modular import MoneyFlowAgentModular
from database.mysql_connector import MySQLConnector
import logging

# 设置详细日志
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def test_specific_queries():
    """测试特定失败的查询"""
    mysql_conn = MySQLConnector()
    agent = MoneyFlowAgentModular(mysql_conn)
    
    test_queries = [
        # 失败的查询
        "解析比亚迪的资金动向",
        "研究万科A本月的资金趋势",
        "分析宁德时代近30天的资金动向",
        "评估光伏设备板块的资金趋势",
        "评估平安银行和招商银行的主力差异",
        "研究比亚迪与宁德时代的资金流向",
        
        # 对比成功的查询
        "分析比亚迪的资金动向",  # 使用"分析"而不是"解析"
        "研究万科A的资金趋势",    # 不带时间段
    ]
    
    for query in test_queries:
        print(f"\n{'='*60}")
        print(f"测试查询: {query}")
        print("="*60)
        
        try:
            result = agent.query(query)
            print(f"成功: {result.get('success')}")
            if result.get('error'):
                print(f"错误: {result['error']}")
            if result.get('result'):
                print(f"结果预览: {str(result['result'])[:200]}...")
        except Exception as e:
            print(f"异常: {str(e)}")
            import traceback
            traceback.print_exc()
    
    mysql_conn.close()

if __name__ == "__main__":
    test_specific_queries()