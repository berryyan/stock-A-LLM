#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
简单测试主力净流入排名单位
"""

from database.mysql_connector import MySQLConnector
from utils.sql_templates import SQLTemplates

def test_simple():
    """简单测试"""
    
    mysql_conn = MySQLConnector()
    
    # 查询数据
    query = """
        SELECT 
            m.ts_code,
            m.name,
            m.close,
            m.pct_change as pct_chg,
            m.net_amount,
            m.net_amount_rate,
            m.buy_elg_amount,
            m.buy_lg_amount,
            m.trade_date
        FROM tu_moneyflow_dc m
        WHERE m.trade_date = '20250702'
            AND m.name NOT LIKE '%ST%'
        ORDER BY m.net_amount DESC
        LIMIT 5
    """
    
    results = mysql_conn.execute_query(query)
    
    if results:
        # 测试格式化函数
        formatted = SQLTemplates.format_money_flow_ranking(results, is_outflow=False)
        
        print("格式化结果:")
        print(formatted)
        
        # 验证
        print("\n" + "="*60)
        print("验证:")
        print(f"第一条数据: {results[0]['name']}")
        print(f"原始net_amount: {results[0]['net_amount']} 万元")
        
        # 检查格式化后的值
        lines = formatted.split('\n')
        for line in lines:
            if results[0]['name'] in line:
                print(f"格式化后的行: {line}")
                # 提取数值
                parts = line.split('|')
                if len(parts) > 6:
                    value_str = parts[6].strip()
                    print(f"显示的数值: {value_str}")
                break


if __name__ == "__main__":
    test_simple()