#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
检查重要表的结构
"""

from database.mysql_connector import MySQLConnector
from sqlalchemy import text
import pandas as pd


def check_table_structures():
    """检查重要表的结构"""
    db = MySQLConnector()
    
    try:
        # 需要检查的表
        tables_to_check = [
            'tu_irm_qa_sz',
            'tu_irm_qa_sh',
            'tu_anns_d',
            'tu_moneyflow_dc',
            'tu_ths_member',
            'tu_dc_index'
        ]
        
        for table_name in tables_to_check:
            print(f"\n{'='*80}")
            print(f"表名: {table_name}")
            print(f"{'='*80}")
            
            # 获取表结构
            columns_query = text(f"""
                SELECT 
                    COLUMN_NAME,
                    DATA_TYPE,
                    IS_NULLABLE,
                    COLUMN_KEY,
                    COLUMN_COMMENT
                FROM information_schema.COLUMNS 
                WHERE TABLE_SCHEMA = 'Tushare' 
                AND TABLE_NAME = :table_name
                ORDER BY ORDINAL_POSITION
            """)
            
            columns_df = pd.read_sql(columns_query, db.engine, params={'table_name': table_name})
            print("\n表结构：")
            print(columns_df.to_string(index=False))
            
            # 获取前3行数据
            try:
                sample_query = text(f"SELECT * FROM {table_name} LIMIT 3")
                sample_df = pd.read_sql(sample_query, db.engine)
                
                # 只显示前5列避免输出太长
                cols_to_show = min(5, len(sample_df.columns))
                print(f"\n数据样例（前3行，显示前{cols_to_show}列）：")
                print(sample_df.iloc[:, :cols_to_show].to_string(index=False))
                
                if len(sample_df.columns) > cols_to_show:
                    print(f"... 还有 {len(sample_df.columns) - cols_to_show} 列")
                    
            except Exception as e:
                print(f"\n读取样例数据失败: {str(e)}")
        
    except Exception as e:
        print(f"检查过程出错: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()


if __name__ == "__main__":
    check_table_structures()