#!/usr/bin/env python3
"""列出数据库中所有概念相关的表"""

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

def list_concept_tables():
    """列出所有概念相关的表"""
    connection = None
    try:
        # 建立数据库连接
        connection = pymysql.connect(**db_config)
        cursor = connection.cursor()
        
        print("数据库中包含'concept'或'member'的表:")
        print("-" * 60)
        
        # 查询所有表名
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'Tushare' 
            AND (table_name LIKE '%concept%' OR table_name LIKE '%member%' OR table_name LIKE '%dc%' OR table_name LIKE '%kpl%')
            ORDER BY table_name
        """)
        
        tables = cursor.fetchall()
        for table in tables:
            table_name = table[0]
            # 获取表的行数
            try:
                cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                count = cursor.fetchone()[0]
                print(f"{table_name}: {count:,} 行")
            except:
                print(f"{table_name}: 无法获取行数")
        
        print("\n" + "-" * 60)
        print("查找东财(DC)相关表:")
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'Tushare' 
            AND (table_name LIKE 'stk_dc%' OR table_name LIKE '%dc_%')
            ORDER BY table_name
        """)
        
        tables = cursor.fetchall()
        for table in tables:
            table_name = table[0]
            try:
                cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                count = cursor.fetchone()[0]
                print(f"{table_name}: {count:,} 行")
            except:
                print(f"{table_name}: 无法获取行数")
                
    except Exception as e:
        print(f"查询出错: {str(e)}")
    finally:
        if connection:
            connection.close()

if __name__ == "__main__":
    list_concept_tables()