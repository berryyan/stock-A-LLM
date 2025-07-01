#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Debug quick routing issues
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.sql_agent import SQLAgent
from utils.query_templates import match_query_template
from utils.date_intelligence import date_intelligence

def debug_specific_query():
    """测试特定查询的快速路由失败原因"""
    sql_agent = SQLAgent()
    
    query = "市值最大的前10只股票"
    print(f"调试查询: {query}")
    print("=" * 50)
    
    # 1. 日期预处理
    processed_query, date_info = date_intelligence.preprocess_question(query)
    print(f"1. 日期处理后: {processed_query}")
    
    # 2. 模板匹配
    match_result = match_query_template(processed_query)
    if match_result:
        template, params = match_result
        print(f"2. 模板匹配: {template.name}")
        print(f"   参数: {params}")
        
        # 3. 检查最新交易日
        last_trading_date = sql_agent._get_last_trading_date()
        print(f"3. 最新交易日: {last_trading_date}")
        
        # 4. 检查日期提取
        extracted_date = sql_agent._extract_date_from_query(processed_query)
        print(f"4. 提取日期: {extracted_date}")
        
        trade_date = extracted_date or last_trading_date
        print(f"5. 最终日期: {trade_date}")
        
        # 6. 手动查询SQL
        from utils.sql_templates import SQLTemplates
        sql = SQLTemplates.MARKET_CAP_RANKING
        print(f"6. SQL模板: {sql[:200]}...")
        
        try:
            result = sql_agent.mysql_connector.execute_query(sql, {
                'trade_date': trade_date,
                'limit': 10
            })
            print(f"7. SQL查询结果: {len(result) if result else 0} 条记录")
            if result:
                print(f"   首条记录: {result[0]}")
        except Exception as e:
            print(f"7. SQL查询失败: {e}")
        
        # 8. 测试完整快速路由
        print("\n8. 完整快速路由测试:")
        quick_result = sql_agent._try_quick_query(query)
        print(f"   结果: {quick_result}")
    else:
        print("模板匹配失败")

if __name__ == "__main__":
    debug_specific_query()