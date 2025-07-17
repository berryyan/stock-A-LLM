#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
探索新增的成分股表结构
- tu_kpl_concept_cons (开盘啦题材成分)
- tu_dc_member (东财板块成分股)
"""

from database.mysql_connector import MySQLConnector
from sqlalchemy import text
import pandas as pd


def explore_new_tables():
    """探索新增表格"""
    db = MySQLConnector()
    
    try:
        print("=== 探索新增成分股表结构 ===\n")
        
        # 1. 探索 tu_dc_member 表
        print(">>> 1. 东财板块成分股表 (tu_dc_member)")
        
        # 获取表结构
        dc_structure = text("""
            SELECT 
                COLUMN_NAME as 字段名,
                DATA_TYPE as 数据类型,
                CHARACTER_MAXIMUM_LENGTH as 最大长度,
                IS_NULLABLE as 可为空,
                COLUMN_DEFAULT as 默认值,
                COLUMN_COMMENT as 字段说明
            FROM information_schema.COLUMNS 
            WHERE TABLE_SCHEMA = 'Tushare' 
            AND TABLE_NAME = 'tu_dc_member'
            ORDER BY ORDINAL_POSITION
        """)
        
        dc_cols = pd.read_sql(dc_structure, db.engine)
        print("\n表结构：")
        print(dc_cols.to_string(index=False))
        
        # 查看数据样例
        dc_sample = text("""
            SELECT * FROM tu_dc_member 
            LIMIT 5
        """)
        
        dc_data = pd.read_sql(dc_sample, db.engine)
        print("\n\n数据样例：")
        print(dc_data.to_string(index=False))
        
        # 统计信息
        dc_stats = text("""
            SELECT 
                COUNT(DISTINCT ts_code) as 板块数量,
                COUNT(DISTINCT con_code) as 股票数量,
                COUNT(*) as 总记录数
            FROM tu_dc_member
        """)
        
        stats = pd.read_sql(dc_stats, db.engine)
        print("\n\n统计信息：")
        print(stats.to_string(index=False))
        
        # 2. 探索 tu_kpl_concept_cons 表
        print("\n\n>>> 2. 开盘啦题材成分表 (tu_kpl_concept_cons)")
        
        # 获取表结构
        kpl_structure = text("""
            SELECT 
                COLUMN_NAME as 字段名,
                DATA_TYPE as 数据类型,
                CHARACTER_MAXIMUM_LENGTH as 最大长度,
                IS_NULLABLE as 可为空,
                COLUMN_DEFAULT as 默认值,
                COLUMN_COMMENT as 字段说明
            FROM information_schema.COLUMNS 
            WHERE TABLE_SCHEMA = 'Tushare' 
            AND TABLE_NAME = 'tu_kpl_concept_cons'
            ORDER BY ORDINAL_POSITION
        """)
        
        kpl_cols = pd.read_sql(kpl_structure, db.engine)
        print("\n表结构：")
        print(kpl_cols.to_string(index=False))
        
        # 查看数据样例
        kpl_sample = text("""
            SELECT * FROM tu_kpl_concept_cons 
            LIMIT 5
        """)
        
        kpl_data = pd.read_sql(kpl_sample, db.engine)
        print("\n\n数据样例：")
        print(kpl_data.to_string(index=False))
        
        # 统计信息
        kpl_stats = text("""
            SELECT 
                COUNT(DISTINCT ts_code) as 题材数量,
                COUNT(DISTINCT con_code) as 股票数量,
                COUNT(*) as 总记录数
            FROM tu_kpl_concept_cons
        """)
        
        stats = pd.read_sql(kpl_stats, db.engine)
        print("\n\n统计信息：")
        print(stats.to_string(index=False))
        
        # 3. 测试查询
        print("\n\n>>> 3. 测试查询")
        
        # 测试东财固态电池概念
        print("\n测试东财'固态电池'概念成分股：")
        dc_test = text("""
            SELECT 
                a.name as 板块名称,
                b.con_code as 股票代码,
                b.name as 股票名称
            FROM tu_dc_index a
            JOIN tu_dc_member b ON a.ts_code = b.ts_code
            WHERE a.name LIKE '%固态电池%'
            LIMIT 10
        """)
        
        dc_result = pd.read_sql(dc_test, db.engine)
        if not dc_result.empty:
            print(dc_result.to_string(index=False))
        else:
            print("未找到固态电池概念")
        
        # 测试开盘啦固态电池概念
        print("\n\n测试开盘啦'固态电池'概念成分股：")
        kpl_test = text("""
            SELECT 
                a.name as 题材名称,
                b.con_code as 股票代码,
                b.con_name as 股票名称
            FROM tu_kpl_concept a
            JOIN tu_kpl_concept_cons b ON a.ts_code = b.ts_code
            WHERE a.name LIKE '%固态电池%'
            LIMIT 10
        """)
        
        kpl_result = pd.read_sql(kpl_test, db.engine)
        if not kpl_result.empty:
            print(kpl_result.to_string(index=False))
        else:
            print("未找到固态电池概念")
        
        # 4. 字段含义总结
        print("\n\n>>> 4. 字段含义总结")
        
        print("\n东财板块成分股 (tu_dc_member):")
        print("- trade_date: 交易日期")
        print("- ts_code: 板块代码（如BK0145.DC）")
        print("- con_code: 股票代码（如603790.SH）")
        print("- name: 股票名称")
        
        print("\n开盘啦题材成分 (tu_kpl_concept_cons):")
        print("- trade_date: 交易日期")
        print("- ts_code: 题材代码（如000335.KP）")
        print("- name: 题材名称")
        print("- con_code: 股票代码（如300468.SZ）")
        print("- con_name: 股票名称")
        print("- is_new: 是否新增")
        print("- dis_date: 剔除日期")
        print("- desc: 成分股描述")
        print("- hot_num: 人气值")
        
        # 5. 数据完整性检查
        print("\n\n>>> 5. 数据完整性检查")
        
        # 检查三个数据源的覆盖度
        coverage_check = text("""
            SELECT 
                '同花顺' as 数据源,
                COUNT(DISTINCT ts_code) as 概念数量,
                COUNT(DISTINCT con_code) as 股票数量
            FROM tu_ths_member
            
            UNION ALL
            
            SELECT 
                '东财' as 数据源,
                COUNT(DISTINCT ts_code) as 概念数量,
                COUNT(DISTINCT con_code) as 股票数量
            FROM tu_dc_member
            
            UNION ALL
            
            SELECT 
                '开盘啦' as 数据源,
                COUNT(DISTINCT ts_code) as 概念数量,
                COUNT(DISTINCT con_code) as 股票数量
            FROM tu_kpl_concept_cons
        """)
        
        coverage = pd.read_sql(coverage_check, db.engine)
        print("\n数据源覆盖度对比：")
        print(coverage.to_string(index=False))
        
    except Exception as e:
        print(f"探索过程出错: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()


if __name__ == "__main__":
    explore_new_tables()