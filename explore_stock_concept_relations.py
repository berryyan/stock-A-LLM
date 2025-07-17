#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
探索股票与概念的关联关系表
"""

from database.mysql_connector import MySQLConnector
from sqlalchemy import text
import pandas as pd


def explore_stock_concept_relations():
    """探索股票与概念的关联关系"""
    db = MySQLConnector()
    
    try:
        # 1. 查找可能包含股票-概念关系的表
        print("=== 查找股票-概念关联表 ===\n")
        
        # 扩大搜索范围
        keywords = ['concept', 'block', 'theme', '板块', '题材', '概念', 'sector', 'industry']
        
        all_tables_query = text("""
            SELECT TABLE_NAME, TABLE_COMMENT 
            FROM information_schema.TABLES 
            WHERE TABLE_SCHEMA = 'Tushare' 
            ORDER BY TABLE_NAME
        """)
        
        all_tables = pd.read_sql(all_tables_query, db.engine)
        
        # 查找相关表
        related_tables = []
        for _, table in all_tables.iterrows():
            table_name = table['TABLE_NAME'].lower()
            for keyword in keywords:
                if keyword in table_name:
                    related_tables.append(table)
                    break
        
        print(f"找到 {len(related_tables)} 个可能相关的表：")
        for table in related_tables:
            print(f"- {table['TABLE_NAME']}: {table['TABLE_COMMENT']}")
        
        # 2. 探索 tu_kpl_concept 表的详细内容
        print("\n=== tu_kpl_concept 表深度分析 ===\n")
        
        # 获取最新交易日的数据
        latest_date_query = text("""
            SELECT MAX(trade_date) as latest_date 
            FROM tu_kpl_concept
        """)
        latest_date = pd.read_sql(latest_date_query, db.engine)['latest_date'][0]
        print(f"最新数据日期: {latest_date}")
        
        # 获取该日期的所有概念
        concepts_query = text("""
            SELECT ts_code, name, z_t_num, up_num
            FROM tu_kpl_concept
            WHERE trade_date = :trade_date
            ORDER BY z_t_num DESC
            LIMIT 20
        """)
        
        concepts_df = pd.read_sql(concepts_query, db.engine, params={'trade_date': latest_date})
        print(f"\n{latest_date} 涨停数最多的概念TOP20：")
        print(concepts_df.to_string(index=False))
        
        # 3. 查找包含股票代码和概念关联的表
        print("\n\n=== 查找股票与概念的映射关系 ===\n")
        
        # 查找可能包含股票代码的表
        stock_concept_tables = []
        for table_name in all_tables['TABLE_NAME']:
            # 跳过已经分析过的表
            if table_name == 'tu_kpl_concept':
                continue
                
            # 检查表是否包含股票代码和概念相关字段
            columns_query = text(f"""
                SELECT COLUMN_NAME
                FROM information_schema.COLUMNS 
                WHERE TABLE_SCHEMA = 'Tushare' 
                AND TABLE_NAME = :table_name
            """)
            
            columns = pd.read_sql(columns_query, db.engine, params={'table_name': table_name})
            column_names = columns['COLUMN_NAME'].str.lower().tolist()
            
            # 检查是否同时包含股票代码和概念相关字段
            has_stock = any(col in column_names for col in ['ts_code', 'stock_code', 'code'])
            has_concept = any(col in column_names for col in ['concept', 'block', 'theme', 'sector'])
            
            if has_stock and has_concept:
                stock_concept_tables.append(table_name)
        
        if stock_concept_tables:
            print(f"找到 {len(stock_concept_tables)} 个可能包含股票-概念映射的表：")
            for table in stock_concept_tables:
                print(f"- {table}")
                
                # 查看表结构和样例
                try:
                    sample_query = text(f"SELECT * FROM {table} LIMIT 3")
                    sample_df = pd.read_sql(sample_query, db.engine)
                    print(f"  样例数据：")
                    print(sample_df.to_string(index=False))
                except Exception as e:
                    print(f"  读取样例失败: {str(e)}")
        else:
            print("未找到明确的股票-概念映射表")
            
        # 4. 分析 tu_sector 和相关表
        print("\n\n=== 分析板块相关表 ===\n")
        
        sector_tables = [t['TABLE_NAME'] for t in all_tables.to_dict('records') 
                        if 'sector' in t['TABLE_NAME'].lower()]
        
        for table_name in sector_tables:
            print(f"\n表名: {table_name}")
            
            # 获取表结构
            columns_query = text(f"""
                SELECT COLUMN_NAME, DATA_TYPE, COLUMN_COMMENT
                FROM information_schema.COLUMNS 
                WHERE TABLE_SCHEMA = 'Tushare' 
                AND TABLE_NAME = :table_name
                ORDER BY ORDINAL_POSITION
            """)
            
            columns_df = pd.read_sql(columns_query, db.engine, params={'table_name': table_name})
            print("表结构：")
            print(columns_df.to_string(index=False))
            
            # 查看数据样例
            try:
                count_query = text(f"SELECT COUNT(*) as cnt FROM {table_name}")
                count = pd.read_sql(count_query, db.engine)['cnt'][0]
                print(f"\n数据量: {count:,} 行")
                
                if count > 0:
                    sample_query = text(f"SELECT * FROM {table_name} LIMIT 5")
                    sample_df = pd.read_sql(sample_query, db.engine)
                    print("\n数据样例：")
                    print(sample_df.to_string(index=False))
            except Exception as e:
                print(f"读取数据失败: {str(e)}")
                
    except Exception as e:
        print(f"探索过程出错: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()


if __name__ == "__main__":
    explore_stock_concept_relations()