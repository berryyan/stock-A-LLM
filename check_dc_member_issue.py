#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
检查东财成分股数据问题
"""

from database.mysql_connector import MySQLConnector
import pandas as pd
from sqlalchemy import text

db = MySQLConnector()

print("=== 检查东财成分股数据问题 ===\n")

# 1. 检查有问题的概念代码
problem_codes = ['BK0989.DC', 'BK0968.DC', 'BK0988.DC', 'BK1103.DC', 'BK1034.DC', 'BK0960.DC', 'BK1052.DC', 'BK1144.DC']

print("1. 检查问题概念代码的数据情况：")
for code in problem_codes:
    # 检查是否有任何数据
    query = text("""
        SELECT 
            COUNT(*) as total_count,
            COUNT(DISTINCT trade_date) as date_count,
            MAX(trade_date) as latest_date,
            MIN(trade_date) as earliest_date
        FROM tu_dc_member 
        WHERE ts_code = :code
    """)
    result = pd.read_sql(query, db.engine, params={'code': code})
    row = result.iloc[0]
    
    # 检查概念是否存在
    concept_query = text("SELECT name FROM tu_dc_index WHERE ts_code = :code")
    concept_result = pd.read_sql(concept_query, db.engine, params={'code': code})
    
    if not concept_result.empty:
        concept_name = concept_result.iloc[0]['name']
        print(f"\n{code} ({concept_name}):")
        print(f"  - 总记录数: {row['total_count']}")
        print(f"  - 日期数量: {row['date_count']}")
        print(f"  - 最新日期: {row['latest_date']}")
        print(f"  - 最早日期: {row['earliest_date']}")
    else:
        print(f"\n{code}: 概念不存在于tu_dc_index表中")

# 2. 检查整体数据更新情况
print("\n\n2. 东财成分股数据整体更新情况：")
update_query = text("""
    SELECT 
        trade_date,
        COUNT(DISTINCT ts_code) as concept_count,
        COUNT(*) as total_records
    FROM tu_dc_member
    WHERE trade_date >= '20250601'
    GROUP BY trade_date
    ORDER BY trade_date DESC
    LIMIT 10
""")
update_result = pd.read_sql(update_query, db.engine)
print(update_result.to_string(index=False))

# 3. 检查有数据的概念最新日期分布
print("\n\n3. 有数据的概念最新日期分布：")
latest_query = text("""
    SELECT 
        latest_date,
        COUNT(*) as concept_count
    FROM (
        SELECT 
            ts_code,
            MAX(trade_date) as latest_date
        FROM tu_dc_member
        GROUP BY ts_code
    ) t
    GROUP BY latest_date
    ORDER BY latest_date DESC
    LIMIT 10
""")
latest_result = pd.read_sql(latest_query, db.engine)
print(latest_result.to_string(index=False))

# 4. 对比一个有数据的概念
print("\n\n4. 对比BK0574.DC（锂电池）的数据情况：")
test_query = text("""
    SELECT 
        trade_date,
        COUNT(*) as member_count
    FROM tu_dc_member
    WHERE ts_code = 'BK0574.DC'
    GROUP BY trade_date
    ORDER BY trade_date DESC
    LIMIT 5
""")
test_result = pd.read_sql(test_query, db.engine)
print(test_result.to_string(index=False))

db.close()

print("\n\n=== 分析结论 ===")
print("1. 部分东财概念代码确实没有成分股数据")
print("2. 东财成分股数据更新不及时，最新数据停留在6月份")
print("3. 需要修改ConceptDataAccess以更好地处理这种情况")