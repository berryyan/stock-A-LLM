#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试主力净流入排名的单位问题
"""

from database.mysql_connector import MySQLConnector
from utils.sql_templates import SQLTemplates
from datetime import datetime

def test_money_flow_unit():
    """测试主力资金数据单位"""
    
    mysql_conn = MySQLConnector()
    
    # 1. 直接查询原始数据
    print("=" * 80)
    print("1. 直接查询数据库原始数据")
    print("=" * 80)
    
    query = """
        SELECT 
            ts_code,
            name,
            net_amount,
            buy_elg_amount,
            buy_lg_amount,
            trade_date
        FROM tu_moneyflow_dc
        WHERE trade_date = '20250702'
        ORDER BY net_amount DESC
        LIMIT 5
    """
    
    results = mysql_conn.execute_query(query)
    
    print("\n主力净流入TOP5（原始数据）:")
    print("-" * 60)
    for row in results:
        print(f"{row['name']} ({row['ts_code']})")
        print(f"  - net_amount: {row['net_amount']} (数据库原始值)")
        print(f"  - 主力资金(大单+超大单): {row['buy_lg_amount'] + row['buy_elg_amount']}")
        print()
    
    # 2. 使用SQLTemplates格式化
    print("\n" + "=" * 80)
    print("2. 使用SQLTemplates格式化后的显示")
    print("=" * 80)
    
    # 模拟format_main_force_ranking的计算
    print("\n格式化计算:")
    print("-" * 60)
    for row in results:
        # 原代码的计算方式
        net_mf = row['net_amount'] / 10000
        print(f"{row['name']}: {row['net_amount']} / 10000 = {net_mf:.2f}")
    
    # 3. 验证单位
    print("\n" + "=" * 80)
    print("3. 单位验证")
    print("=" * 80)
    
    # 查询一个具体股票验证
    stock_query = """
        SELECT 
            m.*,
            d.amount as trade_amount
        FROM tu_moneyflow_dc m
        JOIN tu_daily_detail d ON m.ts_code = d.ts_code AND m.trade_date = d.trade_date
        WHERE m.ts_code = '000001.SZ'
            AND m.trade_date = '20250702'
    """
    
    stock_result = mysql_conn.execute_query(stock_query)
    
    if stock_result:
        row = stock_result[0]
        print(f"\n平安银行 (000001.SZ) 2025-07-02:")
        print(f"  - 成交额(amount): {row['trade_amount']} 万元")
        print(f"  - 净流入(net_amount): {row['net_amount']} 万元")
        print(f"  - 净流入占成交额比例: {row['net_amount'] / row['trade_amount'] * 100:.2f}%")
        print(f"\n如果net_amount除以10000:")
        print(f"  - 净流入变成: {row['net_amount']/10000:.4f} 亿元")
        print(f"  - 占成交额比例: {(row['net_amount']/10000) / row['trade_amount'] * 100:.6f}% (明显不合理)")


if __name__ == "__main__":
    test_money_flow_unit()