#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
查找东财和开盘啦的成分股信息
"""

from database.mysql_connector import MySQLConnector
from sqlalchemy import text
import pandas as pd


def find_dc_kpl_members():
    """查找东财和开盘啦的成分股信息"""
    db = MySQLConnector()
    
    try:
        print("=== 查找东财和开盘啦成分股信息 ===\n")
        
        # 1. 搜索所有包含member或相关字段的表
        print(">>> 搜索可能包含成分股信息的表")
        search_query = text("""
            SELECT 
                TABLE_NAME,
                TABLE_COMMENT,
                TABLE_ROWS
            FROM information_schema.TABLES 
            WHERE TABLE_SCHEMA = 'Tushare' 
            AND (
                TABLE_NAME LIKE '%dc%' 
                OR TABLE_NAME LIKE '%kpl%'
                OR TABLE_NAME LIKE '%member%'
                OR TABLE_NAME LIKE '%list%'
                OR TABLE_NAME LIKE '%stock%'
            )
            ORDER BY TABLE_NAME
        """)
        
        tables = pd.read_sql(search_query, db.engine)
        print(tables.to_string(index=False))
        
        # 2. 检查tu_limit_list_d表（可能包含板块信息）
        print("\n\n>>> 检查tu_limit_list_d表结构")
        limit_structure = text("""
            SELECT 
                COLUMN_NAME as '字段名',
                DATA_TYPE as '类型',
                COLUMN_COMMENT as '注释'
            FROM information_schema.COLUMNS 
            WHERE TABLE_SCHEMA = 'Tushare' 
            AND TABLE_NAME = 'tu_limit_list_d'
            ORDER BY ORDINAL_POSITION
        """)
        
        limit_cols = pd.read_sql(limit_structure, db.engine)
        print(limit_cols.to_string(index=False))
        
        # 3. 检查tu_limit_cpt_list表
        print("\n\n>>> 检查tu_limit_cpt_list表（涨停概念表）")
        cpt_structure = text("""
            SELECT 
                COLUMN_NAME as '字段名',
                DATA_TYPE as '类型',
                COLUMN_COMMENT as '注释'
            FROM information_schema.COLUMNS 
            WHERE TABLE_SCHEMA = 'Tushare' 
            AND TABLE_NAME = 'tu_limit_cpt_list'
            ORDER BY ORDINAL_POSITION
        """)
        
        cpt_cols = pd.read_sql(cpt_structure, db.engine)
        print(cpt_cols.to_string(index=False))
        
        # 查看数据样例
        print("\n数据样例：")
        cpt_sample = text("""
            SELECT * FROM tu_limit_cpt_list 
            WHERE name LIKE '%电池%'
            LIMIT 5
        """)
        
        try:
            cpt_data = pd.read_sql(cpt_sample, db.engine)
            if not cpt_data.empty:
                print(cpt_data.to_string(index=False))
        except Exception as e:
            print(f"查询失败: {e}")
        
        # 4. 检查tu_moneyflow_ind_dc表（可能有板块成分股资金流）
        print("\n\n>>> 检查tu_moneyflow_ind_dc表")
        flow_structure = text("""
            SELECT 
                COLUMN_NAME as '字段名',
                DATA_TYPE as '类型',
                COLUMN_COMMENT as '注释'
            FROM information_schema.COLUMNS 
            WHERE TABLE_SCHEMA = 'Tushare' 
            AND TABLE_NAME = 'tu_moneyflow_ind_dc'
            ORDER BY ORDINAL_POSITION
            LIMIT 10
        """)
        
        flow_cols = pd.read_sql(flow_structure, db.engine)
        print(flow_cols.to_string(index=False))
        
        # 5. 看看是否有其他方式获取成分股
        print("\n\n>>> 检查东财概念表是否包含成分股数量")
        dc_count_query = text("""
            SELECT 
                COLUMN_NAME,
                COLUMN_COMMENT
            FROM information_schema.COLUMNS 
            WHERE TABLE_SCHEMA = 'Tushare' 
            AND TABLE_NAME = 'tu_dc_index'
            AND (COLUMN_NAME LIKE '%count%' OR COLUMN_NAME LIKE '%num%')
        """)
        
        dc_count_cols = pd.read_sql(dc_count_query, db.engine)
        print("东财概念表数量相关字段：")
        print(dc_count_cols.to_string(index=False))
        
        # 6. 查看tu_dc_index的完整字段
        print("\n\n>>> tu_dc_index完整字段列表")
        dc_all_cols = text("""
            SELECT 
                COLUMN_NAME as '字段',
                DATA_TYPE as '类型',
                COLUMN_COMMENT as '注释'
            FROM information_schema.COLUMNS 
            WHERE TABLE_SCHEMA = 'Tushare' 
            AND TABLE_NAME = 'tu_dc_index'
            ORDER BY ORDINAL_POSITION
        """)
        
        dc_all = pd.read_sql(dc_all_cols, db.engine)
        print(dc_all.to_string(index=False))
        
    except Exception as e:
        print(f"检查过程出错: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()


if __name__ == "__main__":
    find_dc_kpl_members()