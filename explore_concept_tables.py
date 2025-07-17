#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
探索概念相关数据表结构
"""

from database.mysql_connector import MySQLConnector
from sqlalchemy import text
import pandas as pd


def explore_concept_tables():
    """探索概念相关的数据表"""
    db = MySQLConnector()
    
    try:
        # 1. 查找概念相关的表
        print("=== 查找概念相关数据表 ===\n")
        
        # 查询所有表名
        all_tables_query = text("""
            SELECT TABLE_NAME, TABLE_COMMENT 
            FROM information_schema.TABLES 
            WHERE TABLE_SCHEMA = 'Tushare' 
            ORDER BY TABLE_NAME
        """)
        
        all_tables = pd.read_sql(all_tables_query, db.engine)
        
        # 筛选概念相关的表
        concept_tables = all_tables[
            all_tables['TABLE_NAME'].str.contains('concept', case=False) |
            all_tables['TABLE_NAME'].str.contains('板块', case=False) |
            all_tables['TABLE_NAME'].str.contains('block', case=False)
        ]
        
        print(f"找到 {len(concept_tables)} 个可能的概念相关表：")
        for _, table in concept_tables.iterrows():
            print(f"- {table['TABLE_NAME']}: {table['TABLE_COMMENT']}")
        
        # 2. 探索每个表的结构
        print("\n=== 详细表结构分析 ===\n")
        
        for table_name in concept_tables['TABLE_NAME']:
            print(f"\n{'='*60}")
            print(f"表名: {table_name}")
            print(f"{'='*60}")
            
            # 获取表结构
            columns_query = text(f"""
                SELECT 
                    COLUMN_NAME as '字段名',
                    DATA_TYPE as '数据类型',
                    IS_NULLABLE as '是否可空',
                    COLUMN_KEY as '键类型',
                    COLUMN_DEFAULT as '默认值',
                    COLUMN_COMMENT as '注释'
                FROM information_schema.COLUMNS 
                WHERE TABLE_SCHEMA = 'Tushare' 
                AND TABLE_NAME = :table_name
                ORDER BY ORDINAL_POSITION
            """)
            
            columns_df = pd.read_sql(columns_query, db.engine, params={'table_name': table_name})
            print("\n表结构：")
            print(columns_df.to_string(index=False))
            
            # 获取数据样例和统计
            try:
                # 数据行数
                count_query = text(f"SELECT COUNT(*) as cnt FROM {table_name}")
                count_result = pd.read_sql(count_query, db.engine)
                row_count = count_result['cnt'][0]
                print(f"\n数据量: {row_count:,} 行")
                
                # 数据样例
                if row_count > 0:
                    sample_query = text(f"SELECT * FROM {table_name} LIMIT 5")
                    sample_df = pd.read_sql(sample_query, db.engine)
                    print(f"\n数据样例（前5行）：")
                    print(sample_df.to_string(index=False))
                    
                    # 特殊字段统计
                    if 'ts_code' in columns_df['字段名'].values:
                        unique_stocks = pd.read_sql(
                            text(f"SELECT COUNT(DISTINCT ts_code) as cnt FROM {table_name}"),
                            db.engine
                        )['cnt'][0]
                        print(f"\n涉及股票数: {unique_stocks:,}")
                    
                    if 'concept_name' in columns_df['字段名'].values:
                        unique_concepts = pd.read_sql(
                            text(f"SELECT COUNT(DISTINCT concept_name) as cnt FROM {table_name}"),
                            db.engine
                        )['cnt'][0]
                        print(f"概念数量: {unique_concepts:,}")
                        
                        # 列出前10个概念
                        concepts_sample = pd.read_sql(
                            text(f"""
                                SELECT concept_name, COUNT(*) as stock_count 
                                FROM {table_name} 
                                GROUP BY concept_name 
                                ORDER BY stock_count DESC 
                                LIMIT 10
                            """),
                            db.engine
                        )
                        print("\n热门概念TOP10：")
                        print(concepts_sample.to_string(index=False))
                        
            except Exception as e:
                print(f"\n探索数据时出错: {str(e)}")
        
        # 3. 检查是否有我们设计的表
        print("\n\n=== 检查预期的概念表 ===\n")
        expected_tables = [
            'tu_concept_blocks',
            'tu_concept_stocks', 
            'tu_concept_evidence',
            'tu_concept_technical_cache'
        ]
        
        for expected in expected_tables:
            if expected in all_tables['TABLE_NAME'].values:
                print(f"✅ {expected} - 已创建")
            else:
                print(f"❌ {expected} - 未找到")
                
    except Exception as e:
        print(f"探索过程出错: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()


if __name__ == "__main__":
    explore_concept_tables()