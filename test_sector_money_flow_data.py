#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试板块资金流向数据结构
"""

import sys
sys.path.append('.')

from database.mysql_connector import MySQLConnector

def test_sector_data():
    """测试板块资金流向数据"""
    mysql = MySQLConnector()
    
    # 1. 查看板块资金流向表结构
    print("="*60)
    print("1. 板块资金流向表结构 (tu_moneyflow_ind_dc)")
    query = """
    SELECT COLUMN_NAME, DATA_TYPE, COLUMN_COMMENT 
    FROM INFORMATION_SCHEMA.COLUMNS 
    WHERE TABLE_SCHEMA = 'Tushare' 
    AND TABLE_NAME = 'tu_moneyflow_ind_dc'
    ORDER BY ORDINAL_POSITION
    """
    result = mysql.execute_query(query)
    for row in result[:20]:  # 只显示前20个字段
        print(f"{row['COLUMN_NAME']:20} {row['DATA_TYPE']:15} {row['COLUMN_COMMENT'] or ''}")
    
    # 2. 查看板块数据示例
    print("\n" + "="*60)
    print("2. 板块资金流向数据示例")
    query = """
    SELECT * FROM tu_moneyflow_ind_dc 
    WHERE trade_date = '20250709' 
    AND content_type = '行业'
    LIMIT 5
    """
    result = mysql.execute_query(query)
    if result:
        # 打印字段名
        print("字段名:", list(result[0].keys()))
        # 打印数据
        for i, row in enumerate(result):
            print(f"\n示例{i+1}:")
            for key, value in row.items():
                if value is not None:
                    print(f"  {key}: {value}")
    
    # 3. 查看可用的板块
    print("\n" + "="*60)
    print("3. 可用的板块列表")
    query = """
    SELECT DISTINCT name, ts_code 
    FROM tu_moneyflow_ind_dc 
    WHERE content_type = '行业' 
    AND trade_date = '20250709'
    ORDER BY name
    LIMIT 20
    """
    result = mysql.execute_query(query)
    for row in result:
        print(f"{row['name']:20} -> {row['ts_code']}")
    
    # 4. 查看板块内的股票（需要找到关联方式）
    print("\n" + "="*60)
    print("4. 测试查询银行板块的资金流向")
    query = """
    SELECT * FROM tu_moneyflow_ind_dc 
    WHERE name LIKE '%银行%' 
    AND trade_date = '20250709'
    AND content_type = '行业'
    """
    result = mysql.execute_query(query)
    if result:
        for row in result:
            print(f"板块: {row['name']} ({row['ts_code']})")
            print(f"主力净流入: {row['net_mf_amount']}万元")
            print(f"主力买入: {row['buy_mf_amount']}万元")
            print(f"主力卖出: {row['sell_mf_amount']}万元")

if __name__ == "__main__":
    test_sector_data()