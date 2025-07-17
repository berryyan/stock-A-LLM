#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
检查三个概念数据源的表结构差异
"""

from database.mysql_connector import MySQLConnector
import pandas as pd
from sqlalchemy import text

db = MySQLConnector()

print("=== 概念成分股表结构对比 ===\n")

# 1. 检查同花顺成分股表
print("1. 同花顺成分股表 (tu_ths_member):")
try:
    query = text("DESCRIBE tu_ths_member")
    result = pd.read_sql(query, db.engine)
    print(result.to_string(index=False))
    
    # 查看示例数据
    sample_query = text("SELECT * FROM tu_ths_member LIMIT 3")
    sample = pd.read_sql(sample_query, db.engine)
    print("\n示例数据:")
    print(sample.to_string(index=False))
except Exception as e:
    print(f"错误: {e}")

print("\n" + "="*80 + "\n")

# 2. 检查东财成分股表
print("2. 东财成分股表 (tu_dc_member):")
try:
    query = text("DESCRIBE tu_dc_member")
    result = pd.read_sql(query, db.engine)
    print(result.to_string(index=False))
    
    # 查看示例数据
    sample_query = text("SELECT * FROM tu_dc_member WHERE trade_date = '20250716' LIMIT 3")
    sample = pd.read_sql(sample_query, db.engine)
    print("\n示例数据:")
    print(sample.to_string(index=False))
except Exception as e:
    print(f"错误: {e}")

print("\n" + "="*80 + "\n")

# 3. 检查开盘啦成分股表
print("3. 开盘啦成分股表 (tu_kpl_concept_cons):")
try:
    query = text("DESCRIBE tu_kpl_concept_cons")
    result = pd.read_sql(query, db.engine)
    print(result.to_string(index=False))
    
    # 查看示例数据
    sample_query = text("SELECT * FROM tu_kpl_concept_cons LIMIT 3")
    sample = pd.read_sql(sample_query, db.engine)
    print("\n示例数据:")
    print(sample.to_string(index=False))
except Exception as e:
    print(f"错误: {e}")

print("\n" + "="*80 + "\n")

# 4. 分析差异
print("4. 表结构差异分析:")
print("- tu_ths_member: 没有trade_date字段，数据是静态的")
print("- tu_dc_member: 有trade_date字段，按交易日更新")
print("- tu_kpl_concept_cons: 有trade_date字段，按交易日更新")
print("\n这意味着：")
print("- 同花顺数据不需要指定日期查询")
print("- 东财和开盘啦需要处理日期，并且可能存在数据更新不及时的问题")

# 5. 检查各表的数据量
print("\n5. 各表数据量统计:")
tables = [
    ('tu_ths_member', None),
    ('tu_dc_member', "WHERE trade_date = '20250716'"),
    ('tu_kpl_concept_cons', "WHERE trade_date = '20250716'")
]

for table, where_clause in tables:
    if where_clause:
        count_query = text(f"SELECT COUNT(*) as cnt FROM {table} {where_clause}")
    else:
        count_query = text(f"SELECT COUNT(*) as cnt FROM {table}")
    
    result = pd.read_sql(count_query, db.engine)
    print(f"{table}: {result.iloc[0]['cnt']} 条记录" + (f" ({where_clause})" if where_clause else ""))

db.close()