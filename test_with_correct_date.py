#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Test with correct database date
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database.mysql_connector import MySQLConnector
from utils.sql_templates import SQLTemplates

def test_with_real_date():
    """使用真实数据库日期测试"""
    mysql = MySQLConnector()
    
    # 1. 获取真实的最新交易日
    result = mysql.execute_query('SELECT DISTINCT trade_date FROM tu_daily_basic ORDER BY trade_date DESC LIMIT 1')
    if result:
        latest_date = str(result[0]['trade_date'])
        print(f"数据库中的最新交易日: {latest_date}")
        
        # 2. 测试市值排名查询
        sql = SQLTemplates.MARKET_CAP_RANKING
        print(f"使用SQL模板查询...")
        
        try:
            ranking_result = mysql.execute_query(sql, {
                'trade_date': latest_date,
                'limit': 5
            })
            print(f"查询结果: {len(ranking_result) if ranking_result else 0} 条记录")
            if ranking_result:
                print("前5条记录:")
                for i, row in enumerate(ranking_result[:5], 1):
                    print(f"  {i}. {row['name']} ({row['ts_code']}) - 市值: {row['total_mv']:.2f}万")
        except Exception as e:
            print(f"查询失败: {e}")
    else:
        print("无法获取最新交易日")

if __name__ == "__main__":
    test_with_real_date()