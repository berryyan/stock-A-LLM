#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试SQL Agent快速路由功能
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.sql_agent import SQLAgent

def test_sql_agent_quick_route():
    """测试SQL Agent的快速路由功能"""
    
    # 初始化SQL Agent
    sql_agent = SQLAgent()
    
    # 测试查询列表
    test_queries = [
        # 估值指标查询
        "中国平安的市盈率",
        "贵州茅台的PE", 
        "平安银行的市净率",
        "比亚迪的PB",
        
        # 市值排名
        "总市值最大的前20只股票",
        "市值排名前50",
        "流通市值最大的前10只股票",
        
        # 主力净流入
        "主力净流入最多的前10只股票",
        
        # 成交额排名
        "成交额最大的前10只股票",
        "成交额排名前20",
        
        # K线查询
        "中国平安最近10天的K线",
    ]
    
    print("SQL Agent快速路由测试")
    print("=" * 80)
    
    for query in test_queries:
        print(f"\n测试查询: {query}")
        print("-" * 40)
        
        # 直接测试快速查询路径
        try:
            quick_result = sql_agent._try_quick_query(query)
            
            if quick_result:
                print(f"✅ 快速路由成功!")
                print(f"   quick_path: {quick_result.get('quick_path', False)}")
                if quick_result.get('result'):
                    # 只显示结果的前200个字符
                    result_preview = quick_result['result'][:200]
                    if len(quick_result['result']) > 200:
                        result_preview += "..."
                    print(f"   结果预览: {result_preview}")
            else:
                print(f"❌ 快速路由失败 - 返回None")
                
        except Exception as e:
            print(f"❌ 出现错误: {e}")
            import traceback
            traceback.print_exc()
    
    # 清理
    sql_agent.mysql_connector.close()


if __name__ == "__main__":
    test_sql_agent_quick_route()