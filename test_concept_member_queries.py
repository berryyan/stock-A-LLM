#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试概念与成分股的查询方式
尝试不同的方法找到东财和开盘啦的成分股关联
"""

from database.mysql_connector import MySQLConnector
from sqlalchemy import text
import pandas as pd


def test_concept_member_queries():
    """测试不同的查询方式"""
    db = MySQLConnector()
    
    try:
        print("=== 测试概念与成分股的查询方式 ===\n")
        
        # 1. 测试东财的成分股获取方式
        print(">>> 1. 东财概念成分股测试")
        
        # 方法1: 通过资金流向表反推
        print("\n方法1: 通过 tu_moneyflow_dc 获取某概念的所有股票")
        print("（假设：如果一个股票在某天有资金流数据，且该概念也有数据，可能存在关联）")
        
        # 先获取固态电池概念的交易日期
        dc_concept_dates = text("""
            SELECT DISTINCT trade_date 
            FROM tu_dc_index 
            WHERE name = '固态电池'
            ORDER BY trade_date DESC
            LIMIT 5
        """)
        
        dates_df = pd.read_sql(dc_concept_dates, db.engine)
        if not dates_df.empty:
            latest_date = dates_df.iloc[0]['trade_date']
            print(f"最新交易日: {latest_date}")
            
            # 获取该日涨幅前10的股票（可能是成分股）
            dc_top_stocks = text("""
                SELECT 
                    ts_code,
                    name,
                    pct_chg,
                    net_mf_amount
                FROM tu_moneyflow_dc
                WHERE trade_date = :trade_date
                AND ts_code IN (
                    SELECT ts_code 
                    FROM tu_stock_basic 
                    WHERE name LIKE '%电池%' 
                    OR name LIKE '%锂%'
                    OR name LIKE '%储能%'
                )
                ORDER BY pct_chg DESC
                LIMIT 10
            """)
            
            top_stocks = pd.read_sql(dc_top_stocks, db.engine, params={'trade_date': latest_date})
            print("\n可能的固态电池概念股（基于名称匹配）：")
            print(top_stocks.to_string(index=False))
        
        # 方法2: 检查是否有隐藏的映射表
        print("\n\n方法2: 查找所有可能的映射表")
        mapping_search = text("""
            SELECT 
                t1.TABLE_NAME,
                t1.TABLE_ROWS,
                GROUP_CONCAT(t2.COLUMN_NAME) as columns
            FROM information_schema.TABLES t1
            JOIN information_schema.COLUMNS t2 
                ON t1.TABLE_NAME = t2.TABLE_NAME 
                AND t1.TABLE_SCHEMA = t2.TABLE_SCHEMA
            WHERE t1.TABLE_SCHEMA = 'Tushare'
            AND t1.TABLE_NAME LIKE '%map%'
            OR t1.TABLE_NAME LIKE '%rel%'
            OR t1.TABLE_NAME LIKE '%link%'
            GROUP BY t1.TABLE_NAME, t1.TABLE_ROWS
        """)
        
        mapping_tables = pd.read_sql(mapping_search, db.engine)
        if not mapping_tables.empty:
            print("可能的映射表：")
            print(mapping_tables.to_string(index=False))
        
        # 2. 测试开盘啦的成分股获取方式
        print("\n\n>>> 2. 开盘啦概念成分股测试")
        
        # 通过 theme 字段分析
        print("\n分析 tu_kpl_list.theme 字段格式：")
        theme_analysis = text("""
            SELECT 
                theme,
                COUNT(*) as stock_count,
                GROUP_CONCAT(DISTINCT name LIMIT 5) as sample_stocks
            FROM tu_kpl_list
            WHERE theme LIKE '%固态电池%'
            GROUP BY theme
            LIMIT 10
        """)
        
        theme_result = pd.read_sql(theme_analysis, db.engine)
        if not theme_result.empty:
            print(theme_result.to_string(index=False))
        else:
            print("未找到包含'固态电池'的theme")
            
            # 看看theme的格式
            print("\n查看theme字段的典型格式：")
            theme_sample = text("""
                SELECT DISTINCT theme
                FROM tu_kpl_list
                WHERE theme IS NOT NULL 
                AND theme != ''
                AND trade_date = (SELECT MAX(trade_date) FROM tu_kpl_list)
                LIMIT 10
            """)
            
            theme_samples = pd.read_sql(theme_sample, db.engine)
            print(theme_samples.to_string(index=False))
        
        # 3. 综合测试：同一天的数据对比
        print("\n\n>>> 3. 同一天三个数据源的对比")
        
        test_date = '20250715'
        
        # 同花顺
        print(f"\n{test_date} 同花顺固态电池概念成分股数量：")
        ths_count = text("""
            SELECT COUNT(DISTINCT b.con_code) as stock_count
            FROM tu_ths_index a
            JOIN tu_ths_member b ON a.ts_code = b.ts_code
            WHERE a.name = '固态电池'
        """)
        
        ths_result = pd.read_sql(ths_count, db.engine)
        print(f"同花顺: {ths_result.iloc[0]['stock_count']} 只")
        
        # 东财
        dc_info = text("""
            SELECT up_num + down_num as total_stocks
            FROM tu_dc_index
            WHERE name = '固态电池'
            AND trade_date = :trade_date
        """)
        
        dc_result = pd.read_sql(dc_info, db.engine, params={'trade_date': test_date})
        if not dc_result.empty:
            print(f"东财: {dc_result.iloc[0]['total_stocks']} 只（up_num + down_num）")
        
        # 开盘啦
        kpl_info = text("""
            SELECT z_t_num
            FROM tu_kpl_concept
            WHERE name LIKE '%固态电池%'
            AND trade_date = :trade_date
        """)
        
        kpl_result = pd.read_sql(kpl_info, db.engine, params={'trade_date': test_date})
        if not kpl_result.empty:
            print(f"开盘啦: {kpl_result.iloc[0]['z_t_num']} 只涨停")
        
        # 4. 最终尝试：是否有我遗漏的表
        print("\n\n>>> 4. 最后的搜索")
        
        # 搜索所有包含 member 或 constituent 的列
        member_columns = text("""
            SELECT 
                TABLE_NAME,
                COLUMN_NAME,
                COLUMN_COMMENT
            FROM information_schema.COLUMNS 
            WHERE TABLE_SCHEMA = 'Tushare'
            AND (
                COLUMN_NAME LIKE '%member%'
                OR COLUMN_NAME LIKE '%constituent%'
                OR COLUMN_COMMENT LIKE '%成分%'
                OR COLUMN_COMMENT LIKE '%成员%'
            )
            ORDER BY TABLE_NAME
        """)
        
        member_cols = pd.read_sql(member_columns, db.engine)
        print("包含成分相关的列：")
        print(member_cols.to_string(index=False))
        
    except Exception as e:
        print(f"测试过程出错: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()


if __name__ == "__main__":
    test_concept_member_queries()