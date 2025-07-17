#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
深入分析开盘啦（KPL）相关数据表
"""

from database.mysql_connector import MySQLConnector
from sqlalchemy import text
import pandas as pd


def analyze_kpl_tables():
    """深入分析KPL相关表"""
    db = MySQLConnector()
    
    try:
        print("=== KPL数据表深度分析 ===\n")
        
        # 1. 分析 tu_kpl_list 表结构
        print("1. tu_kpl_list 表结构分析")
        print("="*60)
        
        columns_query = text("""
            SELECT 
                COLUMN_NAME as '字段名',
                DATA_TYPE as '数据类型',
                COLUMN_COMMENT as '注释'
            FROM information_schema.COLUMNS 
            WHERE TABLE_SCHEMA = 'Tushare' 
            AND TABLE_NAME = 'tu_kpl_list'
            ORDER BY ORDINAL_POSITION
        """)
        
        columns_df = pd.read_sql(columns_query, db.engine)
        print(columns_df.to_string(index=False))
        
        # 2. 统计数据概况
        print("\n\n2. 数据统计概况")
        print("="*60)
        
        # 数据总量
        count_query = text("SELECT COUNT(*) as cnt FROM tu_kpl_list")
        total_count = pd.read_sql(count_query, db.engine)['cnt'][0]
        print(f"总数据量: {total_count:,} 条")
        
        # 涉及的股票数
        stock_count_query = text("SELECT COUNT(DISTINCT ts_code) as cnt FROM tu_kpl_list")
        stock_count = pd.read_sql(stock_count_query, db.engine)['cnt'][0]
        print(f"涉及股票数: {stock_count:,} 只")
        
        # 日期范围
        date_range_query = text("""
            SELECT MIN(trade_date) as min_date, MAX(trade_date) as max_date 
            FROM tu_kpl_list
        """)
        date_range = pd.read_sql(date_range_query, db.engine)
        print(f"日期范围: {date_range['min_date'][0]} ~ {date_range['max_date'][0]}")
        
        # 3. 分析theme字段（概念/题材）
        print("\n\n3. 概念/题材分析")
        print("="*60)
        
        # 最新日期的热门概念
        latest_themes_query = text("""
            SELECT 
                theme,
                COUNT(*) as stock_count,
                GROUP_CONCAT(name ORDER BY name SEPARATOR ', ') as stocks
            FROM tu_kpl_list
            WHERE trade_date = (SELECT MAX(trade_date) FROM tu_kpl_list)
            AND theme IS NOT NULL AND theme != ''
            GROUP BY theme
            ORDER BY stock_count DESC
            LIMIT 20
        """)
        
        latest_themes = pd.read_sql(latest_themes_query, db.engine)
        print("\n最新交易日热门概念TOP20：")
        for idx, row in latest_themes.iterrows():
            print(f"\n{idx+1}. {row['theme']} ({row['stock_count']}只股票)")
            # 只显示前5只股票
            stocks = row['stocks'].split(', ')[:5]
            if len(stocks) < row['stock_count']:
                stocks.append('...')
            print(f"   股票: {', '.join(stocks)}")
        
        # 4. 分析概念包含的关键词
        print("\n\n4. 概念关键词分析")
        print("="*60)
        
        # 获取所有独特的概念
        all_themes_query = text("""
            SELECT DISTINCT theme 
            FROM tu_kpl_list 
            WHERE theme IS NOT NULL AND theme != ''
        """)
        
        all_themes = pd.read_sql(all_themes_query, db.engine)
        
        # 统计概念中的常见词
        word_count = {}
        for theme in all_themes['theme']:
            # 分割概念（按顿号、逗号等）
            words = theme.replace('、', ',').replace('，', ',').split(',')
            for word in words:
                word = word.strip()
                if word:
                    word_count[word] = word_count.get(word, 0) + 1
        
        # 显示最常见的概念词
        sorted_words = sorted(word_count.items(), key=lambda x: x[1], reverse=True)[:30]
        print("\n最常见的概念关键词TOP30：")
        for i, (word, count) in enumerate(sorted_words):
            if i % 3 == 0:
                print()
            print(f"{word}({count})", end="  ")
        print()
        
        # 5. 查看具体的股票-概念映射示例
        print("\n\n5. 股票-概念映射示例")
        print("="*60)
        
        # 查看贵州茅台的概念
        maotai_query = text("""
            SELECT DISTINCT trade_date, theme, tag, pct_chg
            FROM tu_kpl_list
            WHERE ts_code = '600519.SH'
            ORDER BY trade_date DESC
            LIMIT 10
        """)
        
        maotai_df = pd.read_sql(maotai_query, db.engine)
        if not maotai_df.empty:
            print("\n贵州茅台(600519.SH)最近的概念标签：")
            print(maotai_df.to_string(index=False))
        
        # 6. 分析 tu_kpl_concept 与 tu_kpl_list 的关系
        print("\n\n6. 概念表与股票表的关联分析")
        print("="*60)
        
        # 查看某个概念在两个表中的数据
        concept_name = 'AI智能体'
        
        # 在concept表中查找
        concept_info_query = text("""
            SELECT ts_code, name, z_t_num, trade_date
            FROM tu_kpl_concept
            WHERE name LIKE :concept_name
            ORDER BY trade_date DESC
            LIMIT 5
        """)
        
        concept_info = pd.read_sql(concept_info_query, db.engine, 
                                  params={'concept_name': f'%{concept_name}%'})
        
        if not concept_info.empty:
            print(f"\n'{concept_name}'在tu_kpl_concept表中的记录：")
            print(concept_info.to_string(index=False))
        
        # 在list表中查找包含该概念的股票
        stocks_with_concept_query = text("""
            SELECT ts_code, name, theme, trade_date
            FROM tu_kpl_list
            WHERE theme LIKE :concept_name
            ORDER BY trade_date DESC
            LIMIT 10
        """)
        
        stocks_with_concept = pd.read_sql(stocks_with_concept_query, db.engine,
                                        params={'concept_name': f'%{concept_name}%'})
        
        if not stocks_with_concept.empty:
            print(f"\n包含'{concept_name}'概念的股票：")
            print(stocks_with_concept.to_string(index=False))
            
    except Exception as e:
        print(f"分析过程出错: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()


if __name__ == "__main__":
    analyze_kpl_tables()