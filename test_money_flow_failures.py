#!/usr/bin/env python3
"""测试Money Flow Agent失败用例的详细分析"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.money_flow_agent_modular import MoneyFlowAgentModular
from database.mysql_connector import MySQLConnector
import logging

# 设置日志级别为DEBUG
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

def test_money_flow_failures():
    """测试Money Flow Agent失败的用例"""
    
    # 初始化Agent
    mysql_conn = MySQLConnector()
    agent = MoneyFlowAgentModular(mysql_conn)
    
    # 失败的测试用例
    test_cases = [
        # 1. "解析"动词测试
        ("解析比亚迪的资金动向", "解析动词失败"),
        ("分析比亚迪的资金动向", "分析动词成功（对比）"),
        ("研究比亚迪的资金动向", "研究动词（对比）"),
        
        # 2. 时间段查询测试
        ("研究万科A本月的资金趋势", "时间段查询失败"),
        ("分析宁德时代近30天的资金动向", "时间段查询失败"),
        ("分析万科A的资金趋势", "无时间段（对比）"),
        
        # 3. 板块路由测试
        ("房地产开发板块的超大单", "板块SQL路由问题"),
        ("贵州茅台的超大单", "个股SQL路由（对比）"),
        
        # 4. 板块分析失败测试
        ("评估光伏设备板块的资金趋势", "板块分析失败"),
        ("分析银行板块的资金流向", "银行板块成功（对比）"),
        
        # 5. 多股票对比测试
        ("评估平安银行和招商银行的主力差异", "多股票对比失败"),
        ("研究比亚迪与宁德时代的资金流向", "多股票对比失败"),
        ("分析贵州茅台和五粮液的资金流向", "多股票对比成功（对比）"),
    ]
    
    print("Money Flow Agent失败用例详细分析")
    print("=" * 80)
    
    for query, description in test_cases:
        print(f"\n测试: {description}")
        print(f"查询: {query}")
        print("-" * 40)
        
        try:
            result = agent.analyze(query)
            
            if result['success']:
                print(f"✅ 成功")
                print(f"耗时: {result.get('query_time', 0):.2f}秒")
                # 打印结果的前200个字符
                result_text = result.get('result', '')
                if isinstance(result_text, str):
                    print(f"结果预览: {result_text[:200]}...")
            else:
                print(f"❌ 失败")
                print(f"错误: {result.get('error', '未知错误')}")
                if result.get('suggestion'):
                    print(f"建议: {result['suggestion']}")
                    
        except Exception as e:
            print(f"💥 异常: {str(e)}")
            import traceback
            traceback.print_exc()
        
        print("-" * 40)
        input("按Enter继续下一个测试...")

if __name__ == "__main__":
    test_money_flow_failures()