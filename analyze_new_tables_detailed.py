#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
深入分析新增的重要数据表
"""

from database.mysql_connector import MySQLConnector
from sqlalchemy import text
import pandas as pd


def analyze_new_tables_detailed():
    """深入分析新增的重要数据表"""
    db = MySQLConnector()
    
    try:
        print("=== 新增重要数据表深度分析 ===\n")
        
        # 1. 分析董秘问答表
        print("1. 董秘互动问答数据分析")
        print("="*80)
        
        # 深证互动易
        print("\n📊 深证互动易 (tu_irm_qa_sz)")
        sz_qa_query = text("""
            SELECT 
                ts_code,
                q_date,
                question,
                answer,
                LENGTH(question) as q_len,
                LENGTH(answer) as a_len
            FROM tu_irm_qa_sz
            WHERE ts_code = '000002.SZ'
            ORDER BY q_date DESC
            LIMIT 5
        """)
        
        sz_qa = pd.read_sql(sz_qa_query, db.engine)
        print("\n万科A最新问答示例：")
        for _, row in sz_qa.iterrows():
            print(f"\n日期: {row['q_date']}")
            print(f"问题({row['q_len']}字): {row['question'][:100]}...")
            print(f"回答({row['a_len']}字): {row['answer'][:100]}...")
        
        # 统计
        sz_stats_query = text("""
            SELECT 
                COUNT(*) as total_qa,
                COUNT(DISTINCT ts_code) as stock_count,
                MIN(q_date) as min_date,
                MAX(q_date) as max_date
            FROM tu_irm_qa_sz
        """)
        sz_stats = pd.read_sql(sz_stats_query, db.engine)
        print(f"\n深证互动易统计：")
        print(f"- 总问答数: {sz_stats['total_qa'][0]:,}")
        print(f"- 涉及股票: {sz_stats['stock_count'][0]:,}")
        print(f"- 时间范围: {sz_stats['min_date'][0]} ~ {sz_stats['max_date'][0]}")
        
        # 2. 分析公告数据表
        print("\n\n2. 上市公司公告数据分析")
        print("="*80)
        
        # 查看公告表结构
        anns_columns_query = text("""
            SELECT COLUMN_NAME, DATA_TYPE, COLUMN_COMMENT
            FROM information_schema.COLUMNS 
            WHERE TABLE_SCHEMA = 'Tushare' 
            AND TABLE_NAME = 'tu_anns_d'
            ORDER BY ORDINAL_POSITION
        """)
        
        anns_columns = pd.read_sql(anns_columns_query, db.engine)
        print("\ntu_anns_d 表结构：")
        print(anns_columns.to_string(index=False))
        
        # 公告样例
        anns_sample_query = text("""
            SELECT 
                ts_code,
                ann_date,
                ann_type,
                title,
                ann_url
            FROM tu_anns_d
            WHERE ts_code = '600519.SH'
            ORDER BY ann_date DESC
            LIMIT 5
        """)
        
        anns_sample = pd.read_sql(anns_sample_query, db.engine)
        print("\n贵州茅台最新公告：")
        print(anns_sample.to_string(index=False))
        
        # 3. 分析连板天梯数据
        print("\n\n3. 连板天梯数据分析")
        print("="*80)
        
        limit_step_query = text("""
            SELECT *
            FROM tu_limit_step
            WHERE trade_date = (SELECT MAX(trade_date) FROM tu_limit_step)
            ORDER BY limit_times DESC
            LIMIT 10
        """)
        
        limit_step = pd.read_sql(limit_step_query, db.engine)
        print("\n最新交易日连板天梯TOP10：")
        print(limit_step.to_string(index=False))
        
        # 4. 分析东财个股资金流向表
        print("\n\n4. 东财个股资金流向数据分析")
        print("="*80)
        
        # 查看表结构
        moneyflow_dc_columns_query = text("""
            SELECT COLUMN_NAME, COLUMN_COMMENT
            FROM information_schema.COLUMNS 
            WHERE TABLE_SCHEMA = 'Tushare' 
            AND TABLE_NAME = 'tu_moneyflow_dc'
            ORDER BY ORDINAL_POSITION
        """)
        
        moneyflow_dc_columns = pd.read_sql(moneyflow_dc_columns_query, db.engine)
        print("\ntu_moneyflow_dc 表结构：")
        print(moneyflow_dc_columns.to_string(index=False))
        
        # 贵州茅台最新资金流向
        moneyflow_sample_query = text("""
            SELECT 
                trade_date,
                pct_change,
                close,
                net_amount,
                net_amount_rate,
                buy_elg_amount,
                buy_lg_amount,
                buy_md_amount,
                buy_sm_amount
            FROM tu_moneyflow_dc
            WHERE ts_code = '600519.SH'
            ORDER BY trade_date DESC
            LIMIT 5
        """)
        
        moneyflow_sample = pd.read_sql(moneyflow_sample_query, db.engine)
        print("\n贵州茅台最新5天资金流向：")
        print(moneyflow_sample.to_string(index=False))
        
        # 5. 分析同花顺指数数据
        print("\n\n5. 同花顺指数数据分析")
        print("="*80)
        
        # 查看同花顺指数列表
        ths_index_query = text("""
            SELECT 
                ts_code,
                name,
                type
            FROM tu_ths_index
            WHERE type IN ('N', 'I')
            ORDER BY ts_code
            LIMIT 20
        """)
        
        ths_index = pd.read_sql(ths_index_query, db.engine)
        print("\n同花顺概念指数示例：")
        for _, row in ths_index.iterrows():
            type_name = "概念" if row['type'] == 'N' else "行业"
            print(f"{row['ts_code']}: {row['name']} ({type_name})")
        
        # 6. 概念关联总结
        print("\n\n6. 概念股数据体系总结")
        print("="*80)
        
        print("\n📊 概念数据来源：")
        print("1) 同花顺体系:")
        print("   - tu_ths_index: 概念和行业指数定义")
        print("   - tu_ths_member: 概念成分股")
        print("   - tu_ths_daily: 概念指数行情")
        
        print("\n2) 东方财富体系:")
        print("   - tu_dc_index: 概念板块定义")
        print("   - tu_dc_daily: 概念板块行情")
        print("   - tu_moneyflow_ind_dc: 板块资金流向")
        print("   - tu_moneyflow_dc: 个股资金流向")
        
        print("\n3) 开盘啦体系:")
        print("   - tu_kpl_concept: 题材库统计")
        print("   - tu_kpl_list: 个股题材标签")
        
        print("\n4) 涨停板体系:")
        print("   - tu_limit_cpt_list: 最强板块统计")
        print("   - tu_limit_list_d: 涨跌停数据")
        print("   - tu_limit_step: 连板天梯")
        
        print("\n5) 董秘互动体系:")
        print("   - tu_irm_qa_sz: 深交所互动易")
        print("   - tu_irm_qa_sh: 上交所e互动")
        
        print("\n6) 公告体系:")
        print("   - tu_anns_d: 全量公告数据")
        
        # 7. 查看一个概念在多个体系中的表现
        print("\n\n7. 跨体系概念分析示例 - 人工智能")
        print("="*80)
        
        # 同花顺
        ai_ths_query = text("""
            SELECT ts_code, name 
            FROM tu_ths_index 
            WHERE name LIKE '%人工智能%' OR name LIKE '%AI%'
        """)
        ai_ths = pd.read_sql(ai_ths_query, db.engine)
        print("\n同花顺AI概念：")
        print(ai_ths.to_string(index=False))
        
        # 东财
        ai_dc_query = text("""
            SELECT DISTINCT ts_code, name 
            FROM tu_dc_index 
            WHERE name LIKE '%人工智能%' OR name LIKE '%AI%'
            LIMIT 5
        """)
        ai_dc = pd.read_sql(ai_dc_query, db.engine)
        print("\n东财AI概念：")
        print(ai_dc.to_string(index=False))
        
        # 开盘啦
        ai_kpl_query = text("""
            SELECT DISTINCT ts_code, name, MAX(z_t_num) as max_zt
            FROM tu_kpl_concept
            WHERE name LIKE '%AI%' OR name LIKE '%人工智能%'
            GROUP BY ts_code, name
            ORDER BY max_zt DESC
            LIMIT 5
        """)
        ai_kpl = pd.read_sql(ai_kpl_query, db.engine)
        print("\n开盘啦AI概念（按最大涨停数排序）：")
        print(ai_kpl.to_string(index=False))
        
    except Exception as e:
        print(f"分析过程出错: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()


if __name__ == "__main__":
    analyze_new_tables_detailed()