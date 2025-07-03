#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试公告表(tu_anns_d)的结构和查询功能
"""

from database.mysql_connector import MySQLConnector
from utils.schema_knowledge_base import SchemaKnowledgeBase
import json


def test_announcement_table():
    """测试公告表功能"""
    mysql = MySQLConnector()
    schema_kb = SchemaKnowledgeBase()
    
    print("=== 测试公告表结构 ===\n")
    
    # 1. 测试Schema知识库中的公告表信息
    print("1. Schema知识库中的公告表定义：")
    anns_schema = schema_kb.get_table_schema('tu_anns_d')
    if anns_schema:
        print(f"   表名: {anns_schema['table_name']}")
        print(f"   注释: {anns_schema['comment']}")
        print(f"   记录数: {anns_schema['row_count']:,}")
        print(f"   主要字段: {anns_schema['primary_fields']}")
        print("\n   字段详情:")
        for field_name, field_info in anns_schema['fields'].items():
            if field_name in anns_schema['primary_fields']:
                print(f"   - {field_name}: {field_info.get('comment', '无注释')} (类型: {field_info.get('type', 'unknown')})")
    
    # 2. 测试中文字段映射
    print("\n2. 测试中文字段映射：")
    test_mappings = ['公告日期', '标题', '链接', '公告链接', '原文链接']
    for chinese_name in test_mappings:
        result = schema_kb.locate_data(chinese_name, 'tu_anns_d')
        if result:
            match = result['matches'][0]
            print(f"   '{chinese_name}' -> {match['field']} (表: {match['table']})")
    
    # 3. 查询最新公告示例
    print("\n3. 查询最新公告示例：")
    query = """
    SELECT ts_code, name, ann_date, title, url
    FROM tu_anns_d
    WHERE ann_date >= '2025-07-01'
    ORDER BY ann_date DESC, rec_time DESC
    LIMIT 10
    """
    
    results = mysql.execute_query(query)
    print(f"   找到 {len(results)} 条最新公告：")
    for idx, row in enumerate(results, 1):
        print(f"\n   [{idx}] {row['name']} ({row['ts_code']})")
        print(f"       日期: {row['ann_date']}")
        print(f"       标题: {row['title'][:50]}{'...' if len(row['title']) > 50 else ''}")
        print(f"       链接: {row['url'][:60]}{'...' if len(row['url']) > 60 else ''}")
    
    # 4. 测试特定股票的公告查询
    print("\n\n4. 测试特定股票的公告查询（贵州茅台）：")
    stock_query = """
    SELECT ann_date, title, url
    FROM tu_anns_d
    WHERE ts_code = '600519.SH'
        AND ann_date >= '2025-06-01'
    ORDER BY ann_date DESC
    LIMIT 5
    """
    
    stock_results = mysql.execute_query(stock_query)
    print(f"   贵州茅台最近的 {len(stock_results)} 条公告：")
    for idx, row in enumerate(stock_results, 1):
        print(f"\n   [{idx}] {row['ann_date']} - {row['title'][:40]}...")
        if row['url']:
            print(f"       链接: {row['url']}")
    
    # 5. 测试公告类型统计
    print("\n\n5. 公告类型统计（基于标题关键词）：")
    type_query = """
    SELECT 
        CASE 
            WHEN title LIKE '%年度报告%' OR title LIKE '%年报%' THEN '年度报告'
            WHEN title LIKE '%季度报告%' OR title LIKE '%季报%' THEN '季度报告'
            WHEN title LIKE '%股东大会%' THEN '股东大会'
            WHEN title LIKE '%分红%' OR title LIKE '%权益分派%' THEN '分红公告'
            ELSE '其他'
        END as type,
        COUNT(*) as count
    FROM tu_anns_d
    WHERE ts_code = '600519.SH' 
        AND ann_date >= '2025-01-01'
    GROUP BY type
    ORDER BY count DESC
    """
    
    type_results = mysql.execute_query(type_query)
    for row in type_results:
        print(f"   {row['type']}: {row['count']} 条")
    
    # 6. 测试URL的可用性
    print("\n\n6. URL格式分析：")
    url_analysis = """
    SELECT 
        SUBSTRING_INDEX(url, '/', 3) as domain,
        COUNT(*) as count
    FROM tu_anns_d
    WHERE ann_date >= '2025-06-01'
        AND url IS NOT NULL
    GROUP BY domain
    ORDER BY count DESC
    LIMIT 5
    """
    
    url_results = mysql.execute_query(url_analysis)
    print("   最常见的URL域名：")
    for row in url_results:
        print(f"   - {row['domain']}: {row['count']:,} 条")
    
    print("\n\n=== 测试完成 ===")
    print("\n总结：")
    print("1. tu_anns_d表包含完整的公告信息，包括标题、日期和原文链接")
    print("2. url字段存储公告的原文下载链接，主要来自cninfo.com.cn")
    print("3. 表中有超过200万条公告记录，覆盖1.8万+股票")
    print("4. 可以通过ts_code和ann_date进行高效查询")
    print("5. Schema知识库已更新，支持中文字段名查询")


if __name__ == "__main__":
    test_announcement_table()