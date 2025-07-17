#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
全面探索三个数据源的成分股表
"""

from database.mysql_connector import MySQLConnector
from sqlalchemy import text
import pandas as pd


def explore_all_member_tables():
    """全面探索成分股表"""
    db = MySQLConnector()
    
    try:
        print("=== 全面探索概念板块和成分股表 ===\n")
        
        # 1. 查找所有可能相关的表
        print(">>> 1. 搜索所有可能的概念和成分股相关表")
        search_query = text("""
            SELECT 
                TABLE_NAME,
                TABLE_COMMENT,
                TABLE_ROWS
            FROM information_schema.TABLES 
            WHERE TABLE_SCHEMA = 'Tushare' 
            AND (
                TABLE_NAME LIKE '%ths%'      -- 同花顺
                OR TABLE_NAME LIKE '%dc%'    -- 东财
                OR TABLE_NAME LIKE '%kpl%'   -- 开盘啦
                OR TABLE_NAME LIKE '%member%'
                OR TABLE_NAME LIKE '%constituent%'
                OR TABLE_NAME LIKE '%stock%'
                OR TABLE_NAME LIKE '%ind%'
                OR TABLE_NAME LIKE '%concept%'
            )
            ORDER BY TABLE_NAME
        """)
        
        all_tables = pd.read_sql(search_query, db.engine)
        print(all_tables.to_string(index=False))
        
        # 2. 检查东财的可能成分股表
        print("\n\n>>> 2. 深入检查东财相关表")
        
        # 检查 tu_moneyflow_ind_dc 是否包含成分股信息
        print("\n检查 tu_moneyflow_ind_dc 表结构：")
        dc_flow_cols = text("""
            SELECT 
                COLUMN_NAME,
                DATA_TYPE,
                COLUMN_COMMENT
            FROM information_schema.COLUMNS 
            WHERE TABLE_SCHEMA = 'Tushare' 
            AND TABLE_NAME = 'tu_moneyflow_ind_dc'
            ORDER BY ORDINAL_POSITION
        """)
        
        dc_flow_structure = pd.read_sql(dc_flow_cols, db.engine)
        print(dc_flow_structure.to_string(index=False))
        
        # 查看数据样例
        print("\n数据样例：")
        dc_flow_sample = text("""
            SELECT * FROM tu_moneyflow_ind_dc 
            WHERE name LIKE '%固态电池%'
            LIMIT 5
        """)
        
        try:
            dc_sample_data = pd.read_sql(dc_flow_sample, db.engine)
            print(dc_sample_data.to_string(index=False))
        except Exception as e:
            print(f"查询失败: {e}")
        
        # 3. 仔细检查每个数据源
        print("\n\n>>> 3. 按数据源逐个检查")
        
        # 3.1 同花顺
        print("\n=== 同花顺（THS） ===")
        print("概念表: tu_ths_index")
        print("成分股表: tu_ths_member")
        
        # 验证关联
        ths_verify = text("""
            SELECT 
                'tu_ths_index' as table_name,
                COUNT(DISTINCT ts_code) as concept_count
            FROM tu_ths_index
            WHERE name LIKE '%电池%'
            
            UNION ALL
            
            SELECT 
                'tu_ths_member' as table_name,
                COUNT(DISTINCT ts_code) as concept_count
            FROM tu_ths_member
            WHERE ts_code IN (
                SELECT ts_code FROM tu_ths_index WHERE name LIKE '%电池%'
            )
        """)
        
        ths_result = pd.read_sql(ths_verify, db.engine)
        print(ths_result.to_string(index=False))
        
        # 3.2 东财
        print("\n\n=== 东财（DC） ===")
        
        # 查找所有dc相关表
        dc_tables = text("""
            SELECT 
                TABLE_NAME,
                TABLE_COMMENT,
                TABLE_ROWS
            FROM information_schema.TABLES 
            WHERE TABLE_SCHEMA = 'Tushare' 
            AND TABLE_NAME LIKE '%dc%'
            AND TABLE_NAME NOT LIKE '%moneyflow%'
            ORDER BY TABLE_NAME
        """)
        
        dc_all = pd.read_sql(dc_tables, db.engine)
        print("东财相关表：")
        print(dc_all.to_string(index=False))
        
        # 检查 tu_dc_daily 是否有成分股信息
        print("\n检查 tu_dc_daily 表结构：")
        dc_daily_cols = text("""
            SELECT 
                COLUMN_NAME,
                DATA_TYPE,
                COLUMN_COMMENT
            FROM information_schema.COLUMNS 
            WHERE TABLE_SCHEMA = 'Tushare' 
            AND TABLE_NAME = 'tu_dc_daily'
            ORDER BY ORDINAL_POSITION
            LIMIT 15
        """)
        
        dc_daily_structure = pd.read_sql(dc_daily_cols, db.engine)
        print(dc_daily_structure.to_string(index=False))
        
        # 3.3 开盘啦
        print("\n\n=== 开盘啦（KPL） ===")
        
        # 检查 tu_limit_cpt_list 是否是开盘啦数据
        print("\n检查 tu_limit_cpt_list 是否包含成分股：")
        cpt_check = text("""
            SELECT 
                COLUMN_NAME,
                COLUMN_COMMENT
            FROM information_schema.COLUMNS 
            WHERE TABLE_SCHEMA = 'Tushare' 
            AND TABLE_NAME = 'tu_limit_cpt_list'
            AND (COLUMN_NAME LIKE '%stock%' OR COLUMN_NAME LIKE '%code%' OR COLUMN_NAME LIKE '%cons%')
        """)
        
        cpt_cols = pd.read_sql(cpt_check, db.engine)
        print(cpt_cols.to_string(index=False))
        
        # 检查 tu_kpl_list 内容
        print("\n检查 tu_kpl_list 是否有概念关联：")
        kpl_list_cols = text("""
            SELECT 
                COLUMN_NAME,
                DATA_TYPE,
                COLUMN_COMMENT
            FROM information_schema.COLUMNS 
            WHERE TABLE_SCHEMA = 'Tushare' 
            AND TABLE_NAME = 'tu_kpl_list'
            ORDER BY ORDINAL_POSITION
        """)
        
        kpl_structure = pd.read_sql(kpl_list_cols, db.engine)
        print(kpl_structure.to_string(index=False))
        
        # 4. 搜索包含成分、个股等关键词的字段
        print("\n\n>>> 4. 搜索包含成分股相关字段的表")
        field_search = text("""
            SELECT 
                TABLE_NAME,
                COLUMN_NAME,
                COLUMN_COMMENT
            FROM information_schema.COLUMNS 
            WHERE TABLE_SCHEMA = 'Tushare' 
            AND (
                COLUMN_COMMENT LIKE '%成分%'
                OR COLUMN_COMMENT LIKE '%个股%'
                OR COLUMN_COMMENT LIKE '%成员%'
                OR COLUMN_NAME LIKE '%member%'
                OR COLUMN_NAME LIKE '%stock%code%'
                OR COLUMN_NAME LIKE '%cons%'
            )
            AND TABLE_NAME IN (
                SELECT TABLE_NAME 
                FROM information_schema.TABLES 
                WHERE TABLE_SCHEMA = 'Tushare' 
                AND (TABLE_NAME LIKE '%dc%' OR TABLE_NAME LIKE '%kpl%')
            )
            ORDER BY TABLE_NAME, COLUMN_NAME
        """)
        
        field_result = pd.read_sql(field_search, db.engine)
        print(field_result.to_string(index=False))
        
    except Exception as e:
        print(f"探索过程出错: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()


if __name__ == "__main__":
    explore_all_member_tables()