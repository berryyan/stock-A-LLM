#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
深入探索概念与成分股的关联方式
"""

from database.mysql_connector import MySQLConnector
from sqlalchemy import text
import pandas as pd


def deep_explore_member_relations():
    """深入探索成分股关联"""
    db = MySQLConnector()
    
    try:
        print("=== 深入探索概念与成分股的关联方式 ===\n")
        
        # 1. 检查东财是否通过其他方式关联
        print(">>> 1. 东财板块与个股关联探索")
        
        # 检查 tu_moneyflow_dc 是否可以作为关联
        print("\n检查 tu_moneyflow_dc（个股资金流）是否有板块信息：")
        dc_flow_check = text("""
            SELECT 
                COLUMN_NAME,
                COLUMN_COMMENT
            FROM information_schema.COLUMNS 
            WHERE TABLE_SCHEMA = 'Tushare' 
            AND TABLE_NAME = 'tu_moneyflow_dc'
            AND (
                COLUMN_NAME LIKE '%板块%' 
                OR COLUMN_NAME LIKE '%concept%' 
                OR COLUMN_NAME LIKE '%industry%'
                OR COLUMN_NAME LIKE '%sector%'
                OR COLUMN_COMMENT LIKE '%板块%'
                OR COLUMN_COMMENT LIKE '%概念%'
            )
        """)
        
        dc_flow_cols = pd.read_sql(dc_flow_check, db.engine)
        if not dc_flow_cols.empty:
            print(dc_flow_cols.to_string(index=False))
        else:
            print("未找到板块相关字段")
        
        # 检查是否有单独的东财成分股表
        print("\n\n搜索东财成分股表（可能的表名）：")
        dc_member_search = text("""
            SELECT 
                TABLE_NAME,
                TABLE_COMMENT,
                TABLE_ROWS
            FROM information_schema.TABLES 
            WHERE TABLE_SCHEMA = 'Tushare' 
            AND (
                TABLE_NAME LIKE '%dc%member%'
                OR TABLE_NAME LIKE '%dc%stock%'
                OR TABLE_NAME LIKE '%dc%constituent%'
                OR TABLE_NAME LIKE '%bk%'  -- 东财板块代码前缀
            )
        """)
        
        dc_member_tables = pd.read_sql(dc_member_search, db.engine)
        print(dc_member_tables.to_string(index=False))
        
        # 2. 检查开盘啦的关联方式
        print("\n\n>>> 2. 开盘啦板块与个股关联探索")
        
        # 检查 tu_kpl_list 的 theme 字段
        print("\n检查 tu_kpl_list.theme 字段内容（可能包含概念信息）：")
        kpl_theme_sample = text("""
            SELECT 
                ts_code,
                name,
                theme,
                trade_date
            FROM tu_kpl_list
            WHERE theme IS NOT NULL AND theme != ''
            LIMIT 5
        """)
        
        try:
            kpl_theme_data = pd.read_sql(kpl_theme_sample, db.engine)
            print(kpl_theme_data.to_string(index=False))
        except Exception as e:
            print(f"查询失败: {e}")
        
        # 3. 检查是否有关联表
        print("\n\n>>> 3. 搜索可能的关联表")
        relation_search = text("""
            SELECT 
                TABLE_NAME,
                TABLE_COMMENT,
                TABLE_ROWS
            FROM information_schema.TABLES 
            WHERE TABLE_SCHEMA = 'Tushare' 
            AND (
                TABLE_NAME LIKE '%relation%'
                OR TABLE_NAME LIKE '%mapping%'
                OR TABLE_NAME LIKE '%link%'
                OR TABLE_NAME LIKE '%ref%'
            )
        """)
        
        relation_tables = pd.read_sql(relation_search, db.engine)
        if not relation_tables.empty:
            print(relation_tables.to_string(index=False))
        else:
            print("未找到明显的关联表")
        
        # 4. 分析 tu_limit_cpt_list 是否能作为关联
        print("\n\n>>> 4. 分析 tu_limit_cpt_list 表")
        print("\n检查该表是否包含个股列表：")
        
        # 查看具体数据
        cpt_detail = text("""
            SELECT *
            FROM tu_limit_cpt_list
            WHERE name LIKE '%固态电池%'
            ORDER BY trade_date DESC
            LIMIT 3
        """)
        
        try:
            cpt_data = pd.read_sql(cpt_detail, db.engine)
            print(cpt_data.to_string(index=False))
            
            # 检查 cons_nums 字段是否包含具体股票
            print("\n\ncons_nums 字段内容检查：")
            print("（注：cons_nums 看起来是'连板家数'，不是成分股列表）")
            
        except Exception as e:
            print(f"查询失败: {e}")
        
        # 5. 最后的尝试：检查是否有未被发现的表
        print("\n\n>>> 5. 检查所有包含股票代码和概念代码的表")
        final_search = text("""
            SELECT 
                t1.TABLE_NAME,
                t1.TABLE_COMMENT,
                t1.TABLE_ROWS,
                GROUP_CONCAT(t2.COLUMN_NAME) as key_columns
            FROM information_schema.TABLES t1
            JOIN information_schema.COLUMNS t2 
                ON t1.TABLE_NAME = t2.TABLE_NAME 
                AND t1.TABLE_SCHEMA = t2.TABLE_SCHEMA
            WHERE t1.TABLE_SCHEMA = 'Tushare'
            AND t2.COLUMN_NAME IN ('ts_code', 'stock_code', 'con_code', 'code')
            AND t1.TABLE_NAME NOT IN (
                'tu_ths_member',  -- 已知的
                'tu_stock_basic', -- 基础信息表
                'tu_daily',       -- 日线表
                'tu_money_flow'   -- 资金流表
            )
            GROUP BY t1.TABLE_NAME, t1.TABLE_COMMENT, t1.TABLE_ROWS
            HAVING COUNT(DISTINCT t2.COLUMN_NAME) >= 2  -- 至少有两个代码字段
            ORDER BY t1.TABLE_NAME
            LIMIT 20
        """)
        
        final_result = pd.read_sql(final_search, db.engine)
        if not final_result.empty:
            print("\n可能包含关联信息的表：")
            print(final_result.to_string(index=False))
        
        # 6. 确认：是否真的只有同花顺有成分股表？
        print("\n\n>>> 6. 最终确认")
        print("\n已确认的成分股表：")
        print("- 同花顺: tu_ths_member ✓ (已确认)")
        print("- 东财: ？")
        print("- 开盘啦: ？")
        
        # 再次搜索是否遗漏
        final_check = text("""
            SELECT 
                TABLE_NAME,
                TABLE_COMMENT
            FROM information_schema.TABLES 
            WHERE TABLE_SCHEMA = 'Tushare' 
            AND (
                TABLE_COMMENT LIKE '%成分%'
                OR TABLE_COMMENT LIKE '%成员%'
                OR TABLE_COMMENT LIKE '%constituent%'
                OR TABLE_NAME LIKE '%const%'
            )
        """)
        
        final_tables = pd.read_sql(final_check, db.engine)
        print("\n\n包含'成分'相关描述的表：")
        print(final_tables.to_string(index=False))
        
    except Exception as e:
        print(f"探索过程出错: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()


if __name__ == "__main__":
    deep_explore_member_relations()