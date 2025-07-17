#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
最终确认概念成分股表结构
"""

from database.mysql_connector import MySQLConnector
from sqlalchemy import text
import pandas as pd


def final_concept_member_check():
    """最终确认各数据源的成分股表"""
    db = MySQLConnector()
    
    try:
        print("=== 最终确认概念成分股表结构 ===\n")
        
        # 1. 查看所有表名，特别注意可能遗漏的
        print(">>> 1. 数据库中所有表（按名称分组）")
        
        all_tables_grouped = text("""
            SELECT 
                CASE 
                    WHEN TABLE_NAME LIKE '%ths%' THEN '同花顺'
                    WHEN TABLE_NAME LIKE '%dc%' THEN '东财'
                    WHEN TABLE_NAME LIKE '%kpl%' THEN '开盘啦'
                    ELSE '其他'
                END as data_source,
                GROUP_CONCAT(TABLE_NAME ORDER BY TABLE_NAME SEPARATOR ', ') as tables
            FROM information_schema.TABLES 
            WHERE TABLE_SCHEMA = 'Tushare'
            GROUP BY data_source
            ORDER BY data_source
        """)
        
        grouped_tables = pd.read_sql(all_tables_grouped, db.engine)
        for _, row in grouped_tables.iterrows():
            print(f"\n{row['data_source']}相关表：")
            tables = row['tables'].split(', ')
            for table in tables:
                print(f"  - {table}")
        
        # 2. 专门查找成分股相关表
        print("\n\n>>> 2. 查找可能的成分股表（扩大搜索范围）")
        
        member_search = text("""
            SELECT 
                TABLE_NAME,
                TABLE_COMMENT,
                TABLE_ROWS
            FROM information_schema.TABLES 
            WHERE TABLE_SCHEMA = 'Tushare'
            AND (
                -- 直接包含member
                TABLE_NAME LIKE '%member%'
                -- 包含板块代码
                OR TABLE_NAME LIKE '%bk%'
                -- 包含constituent
                OR TABLE_NAME LIKE '%const%'
                -- 包含detail
                OR TABLE_NAME LIKE '%detail%'
                -- 包含list且有dc或kpl
                OR (TABLE_NAME LIKE '%list%' AND (TABLE_NAME LIKE '%dc%' OR TABLE_NAME LIKE '%kpl%'))
            )
            ORDER BY TABLE_NAME
        """)
        
        member_tables = pd.read_sql(member_search, db.engine)
        print(member_tables.to_string(index=False))
        
        # 3. 检查tu_dc_index是否直接存储成分股
        print("\n\n>>> 3. 检查tu_dc_index的所有字段")
        dc_index_cols = text("""
            SELECT 
                COLUMN_NAME,
                DATA_TYPE,
                CHARACTER_MAXIMUM_LENGTH,
                COLUMN_COMMENT
            FROM information_schema.COLUMNS 
            WHERE TABLE_SCHEMA = 'Tushare' 
            AND TABLE_NAME = 'tu_dc_index'
            ORDER BY ORDINAL_POSITION
        """)
        
        dc_cols = pd.read_sql(dc_index_cols, db.engine)
        print("tu_dc_index 完整字段：")
        print(dc_cols.to_string(index=False))
        
        # 4. 查看是否有JSON或TEXT字段存储成分股
        print("\n\n>>> 4. 查找可能包含成分股列表的TEXT/JSON字段")
        
        text_fields = text("""
            SELECT 
                TABLE_NAME,
                COLUMN_NAME,
                DATA_TYPE,
                COLUMN_COMMENT
            FROM information_schema.COLUMNS 
            WHERE TABLE_SCHEMA = 'Tushare'
            AND DATA_TYPE IN ('text', 'json', 'longtext', 'mediumtext')
            AND TABLE_NAME IN (
                SELECT TABLE_NAME 
                FROM information_schema.TABLES 
                WHERE TABLE_SCHEMA = 'Tushare'
                AND (TABLE_NAME LIKE '%dc%' OR TABLE_NAME LIKE '%kpl%')
            )
        """)
        
        text_cols = pd.read_sql(text_fields, db.engine)
        if not text_cols.empty:
            print("找到的TEXT/JSON字段：")
            print(text_cols.to_string(index=False))
            
            # 检查theme字段的内容格式
            print("\n\n检查 tu_kpl_list.theme 字段是否包含股票列表：")
            theme_check = text("""
                SELECT 
                    theme,
                    COUNT(*) as count
                FROM tu_kpl_list
                WHERE theme LIKE '%固态电池%'
                GROUP BY theme
                ORDER BY count DESC
                LIMIT 5
            """)
            
            theme_data = pd.read_sql(theme_check, db.engine)
            if not theme_data.empty:
                print(theme_data.to_string(index=False))
            else:
                # 查看theme的实际内容
                theme_sample = text("""
                    SELECT 
                        ts_code,
                        name,
                        theme
                    FROM tu_kpl_list
                    WHERE theme IS NOT NULL 
                    AND LENGTH(theme) > 10
                    LIMIT 5
                """)
                
                theme_samples = pd.read_sql(theme_sample, db.engine)
                print("\ntheme字段样例：")
                print(theme_samples.to_string(index=False))
        
        # 5. 最终总结
        print("\n\n>>> 5. 最终确认结果")
        
        # 确认同花顺
        ths_check = text("""
            SELECT 
                'tu_ths_index' as table_name,
                COUNT(*) as record_count,
                '概念指数表' as description
            FROM tu_ths_index
            UNION ALL
            SELECT 
                'tu_ths_member' as table_name,
                COUNT(*) as record_count,
                '概念成分股表' as description
            FROM tu_ths_member
        """)
        
        ths_result = pd.read_sql(ths_check, db.engine)
        print("\n同花顺：")
        print(ths_result.to_string(index=False))
        
        # 尝试找东财成分股的其他方式
        print("\n\n东财：")
        print("- 概念表：tu_dc_index")
        print("- 成分股表：？（需要确认）")
        print("- 可能通过其他方式关联？")
        
        print("\n\n开盘啦：")
        print("- 概念表：tu_kpl_concept")
        print("- 个股表：tu_kpl_list（包含theme字段）")
        print("- 关联方式：可能通过theme字段？")
        
        # 6. 搜索是否有隐藏的关系表
        print("\n\n>>> 6. 最后尝试：搜索可能的关系表")
        
        relation_search = text("""
            SELECT 
                TABLE_NAME,
                TABLE_COMMENT,
                TABLE_ROWS,
                CREATE_TIME
            FROM information_schema.TABLES 
            WHERE TABLE_SCHEMA = 'Tushare'
            AND TABLE_ROWS > 1000  -- 有一定数据量
            AND (
                -- 可能的关系表命名
                TABLE_NAME LIKE '%rel%'
                OR TABLE_NAME LIKE '%map%'
                OR TABLE_NAME LIKE '%link%'
                OR TABLE_NAME LIKE '%bind%'
                OR TABLE_NAME LIKE '%conn%'
                -- 或者包含两个关键词
                OR (TABLE_NAME LIKE '%concept%' AND TABLE_NAME LIKE '%stock%')
                OR (TABLE_NAME LIKE '%板块%' AND TABLE_NAME LIKE '%股票%')
            )
            ORDER BY CREATE_TIME DESC
        """)
        
        relation_tables = pd.read_sql(relation_search, db.engine)
        if not relation_tables.empty:
            print("可能的关系表：")
            print(relation_tables.to_string(index=False))
        else:
            print("未找到明显的关系表")
        
    except Exception as e:
        print(f"检查过程出错: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()


if __name__ == "__main__":
    final_concept_member_check()