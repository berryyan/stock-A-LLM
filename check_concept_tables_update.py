#!/usr/bin/env python3
"""检查概念板块相关表格的数据更新情况"""

import pymysql
import pandas as pd
from datetime import datetime

# 数据库连接配置
db_config = {
    'host': '10.0.0.77',
    'port': 3306,
    'user': 'readonly_user',
    'password': 'Tushare2024',
    'database': 'Tushare',
    'charset': 'utf8mb4'
}

def check_tables():
    """检查各个表的数据情况"""
    connection = None
    try:
        # 建立数据库连接
        connection = pymysql.connect(**db_config)
        cursor = connection.cursor()
        
        print("=" * 80)
        print("概念板块相关表格数据更新检查")
        print("=" * 80)
        
        # 1. 检查tu_kpl_concept_cons表（开平类概念成分股）
        print("\n1. tu_kpl_concept_cons表统计:")
        cursor.execute("""
            SELECT COUNT(*) as total_records 
            FROM tu_kpl_concept_cons
        """)
        result = cursor.fetchone()
        print(f"   总记录数: {result[0]:,}")
        
        # 2. 检查tu_dc_member表（东财概念成分股）
        print("\n2. tu_dc_member表统计:")
        cursor.execute("""
            SELECT COUNT(*) as total_records 
            FROM tu_dc_member
        """)
        result = cursor.fetchone()
        print(f"   总记录数: {result[0]:,}")
        
        # 3. 检查tu_kpl_concept表（开平类概念列表）
        print("\n3. tu_kpl_concept表统计:")
        cursor.execute("""
            SELECT COUNT(*) as total_records 
            FROM tu_kpl_concept
        """)
        result = cursor.fetchone()
        print(f"   总记录数: {result[0]:,}")
        
        # 4. 检查tu_dc_index表（东财指数/概念列表）
        print("\n4. tu_dc_index表统计:")
        cursor.execute("""
            SELECT COUNT(*) as total_records 
            FROM tu_dc_index
        """)
        result = cursor.fetchone()
        print(f"   总记录数: {result[0]:,}")
        
        # 5. 检查BK0989.DC储能概念的数据
        print("\n5. BK0989.DC储能概念数据检查:")
        
        # 在tu_kpl_concept_cons表中
        cursor.execute("""
            SELECT COUNT(*) as member_count 
            FROM tu_kpl_concept_cons 
            WHERE ts_code = 'BK0989.DC'
        """)
        result = cursor.fetchone()
        print(f"   tu_kpl_concept_cons表中的成员数: {result[0]}")
        
        # 在tu_dc_member表中
        cursor.execute("""
            SELECT COUNT(*) as member_count 
            FROM tu_dc_member 
            WHERE ts_code = 'BK0989.DC'
        """)
        result = cursor.fetchone()
        print(f"   tu_dc_member表中的成员数: {result[0]}")
        
        # 6. 检查其他之前发现缺失数据的概念
        print("\n6. 其他重要概念数据检查:")
        important_concepts = [
            ('BK0456.DC', '特斯拉'),
            ('BK0481.DC', '充电桩'),
            ('BK0487.DC', '虚拟现实'),
            ('BK0493.DC', '新能源汽车'),
            ('BK0545.DC', '锂电池'),
            ('BK0574.DC', '锂矿'),
            ('BK0606.DC', '智能电网'),
            ('BK0731.DC', '固态电池'),
            ('BK0989.DC', '储能')
        ]
        
        for concept_code, concept_name in important_concepts:
            cursor.execute(f"""
                SELECT 
                    (SELECT COUNT(*) FROM tu_kpl_concept_cons WHERE ts_code = '{concept_code}') as kpl_count,
                    (SELECT COUNT(*) FROM tu_dc_member WHERE ts_code = '{concept_code}') as dc_count
            """)
            result = cursor.fetchone()
            print(f"   {concept_code} ({concept_name}): "
                  f"kpl_concept_cons表: {result[0]}条, dc_member表: {result[1]}条")
        
        # 7. 检查东财概念列表中的概念数量
        print("\n7. 东财概念统计:")
        cursor.execute("""
            SELECT COUNT(DISTINCT ts_code) as concept_count
            FROM tu_dc_index
            WHERE ts_code LIKE 'BK%'
        """)
        result = cursor.fetchone()
        print(f"   东财概念总数: {result[0]}")
        
        # 8. 查看一些示例数据
        print("\n8. 查看BK0989.DC储能概念的部分成员股票:")
        cursor.execute("""
            SELECT con_code, name
            FROM tu_dc_member
            WHERE ts_code = 'BK0989.DC'
            LIMIT 10
        """)
        results = cursor.fetchall()
        if results:
            for row in results:
                print(f"   {row[0]} - {row[1]}")
        else:
            print("   没有找到该概念的成员股票数据")
            
        # 9. 检查最新的交易日期
        print("\n9. 检查数据的最新交易日期:")
        cursor.execute("""
            SELECT MAX(trade_date) as latest_date
            FROM tu_dc_member
        """)
        result = cursor.fetchone()
        print(f"   tu_dc_member表最新交易日期: {result[0]}")
        
        cursor.execute("""
            SELECT MAX(trade_date) as latest_date
            FROM tu_kpl_concept_cons
        """)
        result = cursor.fetchone()
        print(f"   tu_kpl_concept_cons表最新交易日期: {result[0]}")
        
        print("\n" + "=" * 80)
        
    except Exception as e:
        print(f"查询出错: {str(e)}")
    finally:
        if connection:
            connection.close()

if __name__ == "__main__":
    check_tables()