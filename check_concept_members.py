#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
检查概念成分股关联查询
"""

from database.mysql_connector import MySQLConnector
from sqlalchemy import text
import pandas as pd


def check_concept_members():
    """检查概念成分股关联"""
    db = MySQLConnector()
    
    try:
        print("=== 概念成分股关联查询 ===\n")
        
        # 1. 同花顺概念查询
        print(">>> 同花顺概念示例")
        ths_query = text("""
            SELECT 
                a.ts_code as concept_code,
                a.name as concept_name,
                COUNT(DISTINCT b.con_code) as stock_count
            FROM tu_ths_index a
            LEFT JOIN tu_ths_member b ON a.ts_code = b.ts_code
            WHERE a.name LIKE '%电池%'
            GROUP BY a.ts_code, a.name
            LIMIT 10
        """)
        
        ths_result = pd.read_sql(ths_query, db.engine)
        print(ths_result.to_string(index=False))
        
        # 2. 查询具体一个概念的成分股
        print("\n\n>>> 固态电池概念成分股（同花顺）")
        member_query = text("""
            SELECT 
                a.name as concept_name,
                b.con_code as stock_code,
                b.con_name as stock_name
            FROM tu_ths_index a
            JOIN tu_ths_member b ON a.ts_code = b.ts_code
            WHERE a.name LIKE '%固态%电池%'
            LIMIT 20
        """)
        
        try:
            member_result = pd.read_sql(member_query, db.engine)
            if not member_result.empty:
                print(member_result.to_string(index=False))
            else:
                print("未找到固态电池概念")
        except Exception as e:
            print(f"查询失败: {e}")
        
        # 3. 东财概念查询（看是否有成分股表）
        print("\n\n>>> 东财概念数据检查")
        dc_check = text("""
            SELECT 
                TABLE_NAME, 
                TABLE_COMMENT,
                TABLE_ROWS
            FROM information_schema.TABLES 
            WHERE TABLE_SCHEMA = 'Tushare' 
            AND TABLE_NAME LIKE '%dc%member%'
        """)
        
        dc_tables = pd.read_sql(dc_check, db.engine)
        if not dc_tables.empty:
            print("东财成分股表：")
            print(dc_tables.to_string(index=False))
        else:
            print("未找到东财成分股表")
            
            # 检查东财概念表是否包含成分股信息
            print("\n检查tu_dc_index表内容：")
            dc_sample = text("""
                SELECT * FROM tu_dc_index 
                WHERE name LIKE '%电池%'
                ORDER BY trade_date DESC
                LIMIT 5
            """)
            dc_result = pd.read_sql(dc_sample, db.engine)
            print(dc_result.to_string(index=False))
        
        # 4. 开盘啦概念查询
        print("\n\n>>> 开盘啦概念数据")
        kpl_query = text("""
            SELECT 
                ts_code,
                name,
                z_t_num,
                trade_date
            FROM tu_kpl_concept
            WHERE name LIKE '%电池%'
            ORDER BY trade_date DESC
            LIMIT 10
        """)
        
        kpl_result = pd.read_sql(kpl_query, db.engine)
        print(kpl_result.to_string(index=False))
        
        # 5. 查找所有可能的成分股关联表
        print("\n\n>>> 搜索所有可能的成分股关联表")
        member_tables = text("""
            SELECT 
                TABLE_NAME,
                TABLE_COMMENT,
                TABLE_ROWS
            FROM information_schema.TABLES 
            WHERE TABLE_SCHEMA = 'Tushare' 
            AND (TABLE_NAME LIKE '%member%' OR TABLE_NAME LIKE '%constituent%' OR TABLE_NAME LIKE '%stock%list%')
            ORDER BY TABLE_NAME
        """)
        
        all_member_tables = pd.read_sql(member_tables, db.engine)
        print(all_member_tables.to_string(index=False))
        
    except Exception as e:
        print(f"检查过程出错: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()


if __name__ == "__main__":
    check_concept_members()