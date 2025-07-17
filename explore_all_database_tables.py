#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
全面探索数据库所有表，识别新增表
"""

from database.mysql_connector import MySQLConnector
from sqlalchemy import text
import pandas as pd
from datetime import datetime
import json


def explore_all_database_tables():
    """全面探索数据库所有表"""
    db = MySQLConnector()
    
    try:
        print("=== 数据库表全面探索 ===\n")
        print(f"探索时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*80)
        
        # 1. 获取所有表的列表
        all_tables_query = text("""
            SELECT 
                TABLE_NAME,
                TABLE_COMMENT,
                TABLE_ROWS,
                CREATE_TIME,
                UPDATE_TIME
            FROM information_schema.TABLES 
            WHERE TABLE_SCHEMA = 'Tushare' 
            ORDER BY CREATE_TIME DESC, TABLE_NAME
        """)
        
        all_tables = pd.read_sql(all_tables_query, db.engine)
        
        print(f"\n数据库中共有 {len(all_tables)} 个表\n")
        
        # 2. 已知的原有表列表（基于项目文档）
        known_tables = [
            # 基础数据表
            'tu_stock_basic',
            'tu_daily',
            'tu_daily_basic',
            'tu_weekly',
            'tu_monthly',
            'tu_trade_cal',
            'tu_name_change',
            'tu_hs_const',
            'tu_stock_company',
            'tu_stk_managers',
            'tu_new_share',
            
            # 财务数据表
            'tu_income',
            'tu_balance_sheet',
            'tu_cashflow',
            'tu_fina_indicator',
            'tu_express',
            'tu_forecast',
            'tu_dividend',
            
            # 行情数据表
            'tu_money_flow',
            'tu_adj_factor',
            'tu_suspend_d',
            'tu_daily_limit',
            'tu_moneyflow_hsgt',
            'tu_hsgt_top10',
            'tu_ggt_top10',
            
            # 指数数据表
            'tu_index_basic',
            'tu_index_daily',
            'tu_index_dailybasic',
            'tu_index_classify',
            'tu_index_member',
            'tu_index_weight',
            
            # 板块数据表
            'tu_sector',
            
            # 公告和新闻
            'tu_ann_date',
            'tu_ann_detail',
            'ann_detail',
            
            # 其他
            'tu_concept',
            'tu_top_list',
            'tu_top_inst',
            'tu_pledge_stat',
            'tu_pledge_detail',
            'tu_repurchase',
            'tu_share_float',
            'tu_margin',
            'tu_margin_detail',
            'tu_margin_target',
            'tu_settlement',
            'tu_broker_recommend'
        ]
        
        # 3. 识别新增表
        new_tables = []
        for _, table in all_tables.iterrows():
            if table['TABLE_NAME'] not in known_tables:
                new_tables.append(table)
        
        print(f"识别到 {len(new_tables)} 个可能的新增表：\n")
        
        # 4. 分类显示新增表
        concept_related = []
        technical_related = []
        kpl_related = []
        other_new = []
        
        for table in new_tables:
            table_name = table['TABLE_NAME'].lower()
            if 'concept' in table_name or 'block' in table_name or '板块' in str(table['TABLE_COMMENT']):
                concept_related.append(table)
            elif 'technical' in table_name or 'indicator' in table_name or '指标' in str(table['TABLE_COMMENT']):
                technical_related.append(table)
            elif 'kpl' in table_name:
                kpl_related.append(table)
            else:
                other_new.append(table)
        
        # 显示分类结果
        print("📊 概念/板块相关新表:")
        for table in concept_related:
            print(f"  - {table['TABLE_NAME']}: {table['TABLE_COMMENT']} (行数: {table['TABLE_ROWS']})")
        
        print("\n📈 技术指标相关新表:")
        for table in technical_related:
            print(f"  - {table['TABLE_NAME']}: {table['TABLE_COMMENT']} (行数: {table['TABLE_ROWS']})")
        
        print("\n🎯 开盘啦(KPL)相关表:")
        for table in kpl_related:
            print(f"  - {table['TABLE_NAME']}: {table['TABLE_COMMENT']} (行数: {table['TABLE_ROWS']})")
        
        print("\n🔧 其他新增表:")
        for table in other_new:
            print(f"  - {table['TABLE_NAME']}: {table['TABLE_COMMENT']} (行数: {table['TABLE_ROWS']})")
        
        # 5. 详细分析每个新增表
        print("\n\n=== 新增表详细分析 ===")
        
        # 优先分析概念相关表
        important_tables = concept_related + technical_related
        
        for table in important_tables[:10]:  # 限制详细分析的表数量
            table_name = table['TABLE_NAME']
            print(f"\n{'='*80}")
            print(f"表名: {table_name}")
            print(f"注释: {table['TABLE_COMMENT']}")
            print(f"数据行数: {table['TABLE_ROWS']:,}")
            print(f"创建时间: {table['CREATE_TIME']}")
            print(f"{'='*80}")
            
            # 获取表结构
            columns_query = text(f"""
                SELECT 
                    COLUMN_NAME as '字段名',
                    DATA_TYPE as '数据类型',
                    IS_NULLABLE as '可空',
                    COLUMN_KEY as '键',
                    COLUMN_COMMENT as '注释'
                FROM information_schema.COLUMNS 
                WHERE TABLE_SCHEMA = 'Tushare' 
                AND TABLE_NAME = :table_name
                ORDER BY ORDINAL_POSITION
            """)
            
            columns_df = pd.read_sql(columns_query, db.engine, params={'table_name': table_name})
            print("\n表结构：")
            print(columns_df.to_string(index=False))
            
            # 获取数据样例
            if table['TABLE_ROWS'] and table['TABLE_ROWS'] > 0:
                try:
                    sample_query = text(f"SELECT * FROM {table_name} LIMIT 5")
                    sample_df = pd.read_sql(sample_query, db.engine)
                    print(f"\n数据样例（前5行）：")
                    print(sample_df.to_string(index=False, max_cols=10))
                    
                    # 特殊分析
                    if 'ts_code' in columns_df['字段名'].values:
                        # 统计股票数
                        stock_count_query = text(f"SELECT COUNT(DISTINCT ts_code) as cnt FROM {table_name}")
                        stock_count = pd.read_sql(stock_count_query, db.engine)['cnt'][0]
                        print(f"\n涉及股票数: {stock_count:,}")
                    
                    if 'trade_date' in columns_df['字段名'].values:
                        # 日期范围
                        date_range_query = text(f"""
                            SELECT MIN(trade_date) as min_date, MAX(trade_date) as max_date 
                            FROM {table_name}
                        """)
                        date_range = pd.read_sql(date_range_query, db.engine)
                        print(f"日期范围: {date_range['min_date'][0]} ~ {date_range['max_date'][0]}")
                        
                except Exception as e:
                    print(f"\n读取数据样例失败: {str(e)}")
        
        # 6. 生成表格汇总报告
        print("\n\n=== 数据库表汇总报告 ===")
        print(f"总表数: {len(all_tables)}")
        print(f"已知表数: {len(known_tables)}")
        print(f"新增表数: {len(new_tables)}")
        print(f"  - 概念/板块相关: {len(concept_related)}")
        print(f"  - 技术指标相关: {len(technical_related)}")
        print(f"  - 开盘啦相关: {len(kpl_related)}")
        print(f"  - 其他: {len(other_new)}")
        
        # 7. 保存完整的表列表
        with open('database_tables_inventory.json', 'w', encoding='utf-8') as f:
            inventory = {
                'exploration_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'total_tables': len(all_tables),
                'known_tables': known_tables,
                'new_tables': [t['TABLE_NAME'] for t in new_tables],
                'concept_related': [t['TABLE_NAME'] for t in concept_related],
                'technical_related': [t['TABLE_NAME'] for t in technical_related],
                'kpl_related': [t['TABLE_NAME'] for t in kpl_related],
                'other_new': [t['TABLE_NAME'] for t in other_new]
            }
            json.dump(inventory, f, ensure_ascii=False, indent=2)
            print(f"\n完整表清单已保存至: database_tables_inventory.json")
        
    except Exception as e:
        print(f"探索过程出错: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()


if __name__ == "__main__":
    explore_all_database_tables()