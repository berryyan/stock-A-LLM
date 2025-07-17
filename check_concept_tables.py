#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
检查概念板块相关表的结构
包括同花顺、东财、开盘啦三个数据源
"""

from database.mysql_connector import MySQLConnector
from sqlalchemy import text
import pandas as pd


def check_concept_tables():
    """检查概念板块相关表的结构"""
    db = MySQLConnector()
    
    try:
        # 概念板块相关表
        concept_tables = {
            "同花顺": {
                "指数表": "tu_ths_index",
                "成分股表": "tu_ths_member",
                "日线表": "tu_ths_daily"
            },
            "东财": {
                "指数表": "tu_dc_index",
                "日线表": "tu_dc_daily"
            },
            "开盘啦": {
                "概念表": "tu_kpl_concept",
                "列表": "tu_kpl_list"
            }
        }
        
        print("=== 概念板块表结构检查 ===\n")
        
        for source, tables in concept_tables.items():
            print(f"\n{'='*80}")
            print(f"{source}数据源")
            print(f"{'='*80}")
            
            for desc, table_name in tables.items():
                print(f"\n>>> {desc}: {table_name}")
                
                # 检查表是否存在
                check_query = text("""
                    SELECT COUNT(*) as cnt
                    FROM information_schema.TABLES 
                    WHERE TABLE_SCHEMA = 'Tushare' 
                    AND TABLE_NAME = :table_name
                """)
                
                exists = pd.read_sql(check_query, db.engine, params={'table_name': table_name})
                
                if exists['cnt'][0] == 0:
                    print(f"   表 {table_name} 不存在!")
                    continue
                
                # 获取表结构
                columns_query = text("""
                    SELECT 
                        COLUMN_NAME as '字段名',
                        DATA_TYPE as '类型',
                        COLUMN_COMMENT as '注释'
                    FROM information_schema.COLUMNS 
                    WHERE TABLE_SCHEMA = 'Tushare' 
                    AND TABLE_NAME = :table_name
                    ORDER BY ORDINAL_POSITION
                    LIMIT 10
                """)
                
                columns_df = pd.read_sql(columns_query, db.engine, params={'table_name': table_name})
                print("\n主要字段：")
                print(columns_df.to_string(index=False))
                
                # 获取数据样例
                try:
                    # 特别处理不同类型的表
                    if "index" in desc.lower() or "概念" in desc:
                        # 概念/指数表
                        sample_query = text(f"""
                            SELECT * FROM {table_name} 
                            WHERE name LIKE '%电池%' OR name LIKE '%新能源%'
                            LIMIT 3
                        """)
                    else:
                        # 成分股表
                        sample_query = text(f"SELECT * FROM {table_name} LIMIT 3")
                    
                    sample_df = pd.read_sql(sample_query, db.engine)
                    
                    if not sample_df.empty:
                        print(f"\n数据样例：")
                        # 只显示重要列
                        important_cols = ['ts_code', 'code', 'name', 'index_code', 'index_name', 'con_code', 'con_name']
                        show_cols = [col for col in important_cols if col in sample_df.columns]
                        if show_cols:
                            print(sample_df[show_cols].to_string(index=False))
                        else:
                            print(sample_df.iloc[:, :5].to_string(index=False))
                    
                    # 统计信息
                    count_query = text(f"SELECT COUNT(*) as cnt FROM {table_name}")
                    count_result = pd.read_sql(count_query, db.engine)
                    print(f"\n总记录数: {count_result['cnt'][0]:,}")
                    
                except Exception as e:
                    print(f"\n读取数据失败: {str(e)}")
        
        # 检查成分股表的具体结构（用于确认如何关联）
        print(f"\n\n{'='*80}")
        print("成分股表详细结构分析")
        print(f"{'='*80}")
        
        # 同花顺成分股表
        print("\n>>> tu_ths_member 详细字段")
        member_query = text("""
            SELECT 
                COLUMN_NAME as '字段名',
                DATA_TYPE as '类型',
                COLUMN_KEY as '键',
                COLUMN_COMMENT as '注释'
            FROM information_schema.COLUMNS 
            WHERE TABLE_SCHEMA = 'Tushare' 
            AND TABLE_NAME = 'tu_ths_member'
            ORDER BY ORDINAL_POSITION
        """)
        
        member_df = pd.read_sql(member_query, db.engine)
        print(member_df.to_string(index=False))
        
        # 查询一些具体的概念及其成分股
        print("\n>>> 概念成分股查询示例")
        test_query = text("""
            SELECT 
                a.code as concept_code,
                a.name as concept_name,
                COUNT(DISTINCT b.code) as stock_count
            FROM tu_ths_index a
            LEFT JOIN tu_ths_member b ON a.ts_code = b.index_code
            WHERE a.name LIKE '%电池%'
            GROUP BY a.code, a.name
            LIMIT 5
        """)
        
        try:
            test_result = pd.read_sql(test_query, db.engine)
            print("\n电池相关概念：")
            print(test_result.to_string(index=False))
        except Exception as e:
            print(f"查询失败: {str(e)}")
        
    except Exception as e:
        print(f"检查过程出错: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()


if __name__ == "__main__":
    check_concept_tables()