#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查数据库中可用的历史数据日期
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database.mysql_connector import MySQLConnector

def check_available_dates():
    """检查数据库中可用的日期范围"""
    print("🔍 检查数据库中可用的历史数据日期")
    print("=" * 60)
    
    try:
        mysql = MySQLConnector()
        
        # 检查日线数据的日期范围
        print("\n📊 日线数据 (tu_daily_detail):")
        query = """
        SELECT 
            MIN(trade_date) as earliest_date,
            MAX(trade_date) as latest_date,
            COUNT(DISTINCT trade_date) as total_days,
            COUNT(DISTINCT ts_code) as total_stocks
        FROM tu_daily_detail
        """
        
        result = mysql.execute_query(query)
        if result:
            data = result[0]
            print(f"   最早日期: {data['earliest_date']}")
            print(f"   最新日期: {data['latest_date']}")
            print(f"   总交易日: {data['total_days']}")
            print(f"   股票数量: {data['total_stocks']}")
        
        # 检查贵州茅台的具体可用日期
        print("\n🍷 贵州茅台 (600519.SH) 最近数据:")
        query = """
        SELECT trade_date, close, pct_chg
        FROM tu_daily_detail 
        WHERE ts_code = '600519.SH'
        ORDER BY trade_date DESC
        LIMIT 10
        """
        
        result = mysql.execute_query(query)
        if result:
            for row in result:
                print(f"   {row['trade_date']}: 收盘价 {row['close']}, 涨跌幅 {row['pct_chg']}%")
        else:
            print("   ❌ 未找到贵州茅台数据")
        
        # 检查财务数据的日期范围
        print("\n💰 财务数据 (tu_income):")
        query = """
        SELECT 
            MIN(end_date) as earliest_date,
            MAX(end_date) as latest_date,
            COUNT(DISTINCT end_date) as total_periods,
            COUNT(DISTINCT ts_code) as total_stocks
        FROM tu_income
        WHERE report_type = '1'
        """
        
        result = mysql.execute_query(query)
        if result:
            data = result[0]
            print(f"   最早期间: {data['earliest_date']}")
            print(f"   最新期间: {data['latest_date']}")
            print(f"   总报告期: {data['total_periods']}")
            print(f"   股票数量: {data['total_stocks']}")
        
        # 推荐的测试日期
        print("\n📅 推荐的测试日期:")
        
        # 获取最近几个交易日
        query = """
        SELECT DISTINCT trade_date
        FROM tu_daily_detail 
        WHERE trade_date < CURDATE()
        ORDER BY trade_date DESC
        LIMIT 5
        """
        
        result = mysql.execute_query(query)
        if result:
            print("   最近交易日:")
            for row in result:
                print(f"     - {row['trade_date']}")
                
        # 获取最近几个财务报告期
        query = """
        SELECT DISTINCT end_date
        FROM tu_income
        WHERE report_type = '1' AND ts_code = '600519.SH'
        ORDER BY end_date DESC
        LIMIT 5
        """
        
        result = mysql.execute_query(query)
        if result:
            print("   最近财务报告期:")
            for row in result:
                print(f"     - {row['end_date']}")
        
        return True
        
    except Exception as e:
        print(f"❌ 检查失败: {e}")
        return False

if __name__ == "__main__":
    check_available_dates()