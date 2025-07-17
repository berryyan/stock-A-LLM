#!/usr/bin/env python3
"""检查表的列结构"""

import pymysql

# 数据库连接配置
db_config = {
    'host': '10.0.0.77',
    'port': 3306,
    'user': 'readonly_user',
    'password': 'Tushare2024',
    'database': 'Tushare',
    'charset': 'utf8mb4'
}

def check_columns():
    """检查相关表的列结构"""
    connection = None
    try:
        # 建立数据库连接
        connection = pymysql.connect(**db_config)
        cursor = connection.cursor()
        
        tables = ['tu_kpl_concept_cons', 'tu_dc_member', 'tu_dc_index']
        
        for table in tables:
            print(f"\n{table}表的列结构:")
            print("-" * 60)
            cursor.execute(f"""
                SELECT column_name, data_type, column_comment
                FROM information_schema.columns
                WHERE table_schema = 'Tushare' AND table_name = '{table}'
                ORDER BY ordinal_position
            """)
            
            columns = cursor.fetchall()
            for col in columns:
                print(f"  {col[0]:<20} {col[1]:<15} {col[2]}")
                
    except Exception as e:
        print(f"查询出错: {str(e)}")
    finally:
        if connection:
            connection.close()

if __name__ == "__main__":
    check_columns()