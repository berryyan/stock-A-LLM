#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
验证数据表的最新更新日期
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database.mysql_connector import MySQLConnector

def verify_data_update_date():
    """验证各个数据表的最新更新日期"""
    
    mysql_connector = MySQLConnector()
    
    # 要检查的表列表
    tables_to_check = [
        ('tu_daily_basic', 'trade_date', '基础日数据'),
        ('tu_daily_detail', 'trade_date', '详细日数据'),
        ('tu_moneyflow_dc', 'trade_date', '资金流向数据'),
    ]
    
    print("数据表最新更新日期检查")
    print("=" * 80)
    
    for table_name, date_column, description in tables_to_check:
        try:
            # 查询最新日期
            sql = f"SELECT MAX({date_column}) as latest_date, COUNT(DISTINCT {date_column}) as date_count FROM {table_name}"
            result = mysql_connector.execute_query(sql)
            
            if result and result[0]['latest_date']:
                latest_date = result[0]['latest_date']
                date_count = result[0]['date_count']
                print(f"\n{description} ({table_name}):")
                print(f"  最新日期: {latest_date}")
                print(f"  日期数量: {date_count}")
                
                # 查询最新日期的记录数
                count_sql = f"SELECT COUNT(*) as record_count FROM {table_name} WHERE {date_column} = %s"
                count_result = mysql_connector.execute_query(count_sql, (latest_date,))
                if count_result:
                    print(f"  最新日期记录数: {count_result[0]['record_count']}")
            else:
                print(f"\n{description} ({table_name}): 无数据")
                
        except Exception as e:
            print(f"\n{description} ({table_name}): 查询失败 - {e}")
    
    # 清理
    mysql_connector.close()
    
    print("\n" + "=" * 80)
    print("检查完成")
    print("\n结论：")
    print("如果数据表的最新日期是2025-06-25或更早，那么查询返回2025-06-23的数据是正常的，")
    print("因为数据库中确实没有更新的数据。")


if __name__ == "__main__":
    verify_data_update_date()