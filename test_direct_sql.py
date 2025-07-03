"""
直接测试SQL执行
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database.mysql_connector import MySQLConnector
from utils.sql_templates import SQLTemplates

def test_direct_sql():
    mysql = MySQLConnector()
    
    # 1. 获取最新交易日
    result = mysql.execute_query('SELECT DISTINCT trade_date FROM tu_daily_basic ORDER BY trade_date DESC LIMIT 1')
    last_trading_date = str(result[0]['trade_date'])
    print(f"最新交易日: {last_trading_date}")
    
    # 2. 准备参数
    params = {
        'trade_date': last_trading_date.replace('-', ''),  # 转换为YYYYMMDD格式
        'limit': 10
    }
    print(f"查询参数: {params}")
    
    # 3. 执行涨幅排名查询
    sql = SQLTemplates.PCT_CHG_RANKING
    print(f"\n执行SQL:\n{sql}")
    
    try:
        result = mysql.execute_query(sql, params)
        print(f"\n查询结果: {len(result)} 条记录")
        
        if result:
            print("\n前3条记录:")
            for i, row in enumerate(result[:3], 1):
                print(f"{i}. {row['name']} ({row['ts_code']}) - 涨幅: {row['pct_chg']:.2f}%")
    except Exception as e:
        print(f"查询失败: {e}")

if __name__ == "__main__":
    test_direct_sql()