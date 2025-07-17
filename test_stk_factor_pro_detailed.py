#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
详细测试Tushare stk_factor_pro接口
了解所有可用字段和数据格式
"""

import tushare as ts
import pandas as pd
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 设置Tushare token
TUSHARE_TOKEN = os.getenv('TUSHARE_TOKEN', '')
ts.set_token(TUSHARE_TOKEN)
pro = ts.pro_api()


def test_stk_factor_pro_all_fields():
    """测试获取所有技术指标字段"""
    print("=== 测试 stk_factor_pro 所有字段 ===\n")
    
    try:
        # 1. 不指定fields，获取所有字段
        print("1. 获取所有可用字段（不指定fields参数）")
        df_all = pro.stk_factor_pro(
            ts_code='600519.SH',
            start_date='20250710',
            end_date='20250715'
        )
        
        if df_all is not None and not df_all.empty:
            print(f"获取到 {len(df_all)} 条数据")
            print(f"字段数量: {len(df_all.columns)}")
            print("\n所有字段列表:")
            for i, col in enumerate(df_all.columns):
                print(f"{i+1:3d}. {col}")
            
            # 显示前2行数据
            print("\n数据样例（前2行，部分字段）：")
            # 选择关键字段显示
            key_fields = ['ts_code', 'trade_date', 'close_bfq', 'macd_bfq', 'macd_dif_bfq', 
                         'macd_dea_bfq', 'kdj_bfq', 'kdj_k_bfq', 'kdj_d_bfq', 'rsi_6_bfq',
                         'ma_bfq_5', 'ma_bfq_10', 'ma_bfq_20']
            available_fields = [f for f in key_fields if f in df_all.columns]
            print(df_all[available_fields].head(2).to_string())
            
        else:
            print("未获取到数据")
            
    except Exception as e:
        print(f"获取所有字段失败: {str(e)}")
        print("可能的原因：")
        print("1. 积分不足（需要5000积分）")
        print("2. 接口调用频率限制")
        return
    
    print("\n" + "="*80 + "\n")
    
    # 2. 测试不同复权类型
    print("2. 测试不同复权类型的数据")
    
    # 测试前复权数据
    try:
        df_qfq = pro.stk_factor_pro(
            ts_code='600519.SH',
            trade_date='20250715',
            fields='ts_code,trade_date,close_qfq,macd_qfq,macd_dif_qfq,macd_dea_qfq,ma_qfq_5,ma_qfq_10'
        )
        
        if df_qfq is not None and not df_qfq.empty:
            print("\n前复权数据：")
            print(df_qfq.to_string())
    except Exception as e:
        print(f"获取前复权数据失败: {str(e)}")
    
    # 测试后复权数据
    try:
        df_hfq = pro.stk_factor_pro(
            ts_code='600519.SH',
            trade_date='20250715',
            fields='ts_code,trade_date,close_hfq,macd_hfq,macd_dif_hfq,macd_dea_hfq,ma_hfq_5,ma_hfq_10'
        )
        
        if df_hfq is not None and not df_hfq.empty:
            print("\n后复权数据：")
            print(df_hfq.to_string())
    except Exception as e:
        print(f"获取后复权数据失败: {str(e)}")


def test_batch_stocks():
    """测试批量获取多只股票的技术指标"""
    print("\n\n=== 测试批量获取多只股票技术指标 ===\n")
    
    # 测试股票列表（贵州茅台、五粮液、泸州老窖）
    stocks = ['600519.SH', '000858.SZ', '000568.SZ']
    
    results = []
    
    for stock in stocks:
        try:
            df = pro.stk_factor_pro(
                ts_code=stock,
                trade_date='20250715',
                fields='ts_code,trade_date,close_bfq,macd_bfq,macd_dif_bfq,macd_dea_bfq,kdj_k_bfq,kdj_d_bfq,kdj_bfq,rsi_6_bfq,ma_bfq_5,ma_bfq_10,ma_bfq_20'
            )
            
            if df is not None and not df.empty:
                results.append(df)
                
        except Exception as e:
            print(f"获取{stock}数据失败: {str(e)}")
    
    if results:
        # 合并结果
        df_all = pd.concat(results, ignore_index=True)
        print("批量获取结果：")
        print(df_all.to_string())
        
        # 分析技术指标
        print("\n技术分析结果：")
        for _, row in df_all.iterrows():
            stock = row['ts_code']
            print(f"\n{stock}:")
            
            # MACD分析
            if pd.notna(row.get('macd_bfq')):
                macd_status = "红柱" if row['macd_bfq'] > 0 else "绿柱"
                print(f"  MACD: {row['macd_bfq']:.4f} ({macd_status})")
            
            # KDJ分析
            if pd.notna(row.get('kdj_k_bfq')):
                kdj_k = row['kdj_k_bfq']
                kdj_status = "超买" if kdj_k > 80 else ("超卖" if kdj_k < 20 else "正常")
                print(f"  KDJ_K: {kdj_k:.2f} ({kdj_status})")
            
            # RSI分析
            if pd.notna(row.get('rsi_6_bfq')):
                rsi = row['rsi_6_bfq']
                rsi_status = "超买" if rsi > 70 else ("超卖" if rsi < 30 else "正常")
                print(f"  RSI(6): {rsi:.2f} ({rsi_status})")
            
            # 均线分析
            if all(pd.notna(row.get(f)) for f in ['ma_bfq_5', 'ma_bfq_10', 'ma_bfq_20']):
                ma5, ma10, ma20 = row['ma_bfq_5'], row['ma_bfq_10'], row['ma_bfq_20']
                if ma5 > ma10 > ma20:
                    print(f"  均线: 多头排列 (MA5:{ma5:.2f} > MA10:{ma10:.2f} > MA20:{ma20:.2f})")
                else:
                    print(f"  均线: 非多头排列 (MA5:{ma5:.2f}, MA10:{ma10:.2f}, MA20:{ma20:.2f})")


def test_date_range_query():
    """测试日期范围查询"""
    print("\n\n=== 测试日期范围查询 ===\n")
    
    try:
        # 获取最近20天的数据
        df = pro.stk_factor_pro(
            ts_code='600519.SH',
            start_date='20250620',
            end_date='20250715',
            fields='ts_code,trade_date,close_bfq,macd_bfq,macd_dif_bfq,macd_dea_bfq,ma_bfq_5,ma_bfq_10'
        )
        
        if df is not None and not df.empty:
            print(f"获取到 {len(df)} 天的数据")
            
            # 按日期排序
            df = df.sort_values('trade_date')
            
            # 分析MACD金叉死叉
            print("\nMACD交叉信号分析：")
            for i in range(1, len(df)):
                prev = df.iloc[i-1]
                curr = df.iloc[i]
                
                if pd.notna(prev['macd_dif_bfq']) and pd.notna(curr['macd_dif_bfq']):
                    # 金叉：DIF从下向上穿过DEA
                    if prev['macd_dif_bfq'] < prev['macd_dea_bfq'] and curr['macd_dif_bfq'] > curr['macd_dea_bfq']:
                        print(f"{curr['trade_date']}: MACD金叉")
                    # 死叉：DIF从上向下穿过DEA
                    elif prev['macd_dif_bfq'] > prev['macd_dea_bfq'] and curr['macd_dif_bfq'] < curr['macd_dea_bfq']:
                        print(f"{curr['trade_date']}: MACD死叉")
            
            # 显示最近5天数据
            print("\n最近5天技术指标：")
            print(df.tail(5).to_string())
            
    except Exception as e:
        print(f"日期范围查询失败: {str(e)}")


def test_api_limits():
    """测试API调用限制"""
    print("\n\n=== 测试API调用限制 ===\n")
    
    try:
        # 测试单次最大数据量
        df = pro.stk_factor_pro(
            ts_code='600519.SH',
            start_date='20240101',
            end_date='20250715',
            fields='ts_code,trade_date,close_bfq,macd_bfq'
        )
        
        if df is not None:
            print(f"单次查询获取数据量: {len(df)} 条")
            
    except Exception as e:
        print(f"大量数据查询失败: {str(e)}")
    
    # 获取用户信息
    try:
        user_info = pro.user()
        print("\n用户信息：")
        print(f"积分: {user_info.iloc[0]['point']}")
        print(f"等级: {user_info.iloc[0]['level']}")
    except Exception as e:
        print(f"获取用户信息失败: {str(e)}")


def design_cache_strategy():
    """设计缓存策略"""
    print("\n\n=== 技术指标缓存策略设计 ===\n")
    
    print("1. 缓存层级设计：")
    print("   - L1缓存（内存）: 5分钟，存储热门股票最新数据")
    print("   - L2缓存（Redis）: 1小时，存储当日所有查询过的数据")
    print("   - L3缓存（数据库）: 永久存储，每日批量更新")
    
    print("\n2. 缓存键设计：")
    print("   - 格式: tech_indicator:{ts_code}:{date}:{indicator_type}")
    print("   - 示例: tech_indicator:600519.SH:20250715:macd")
    
    print("\n3. 批量更新策略：")
    print("   - 每日收盘后批量计算所有活跃股票的技术指标")
    print("   - 优先更新概念热门股、涨停股等")
    print("   - 使用并发处理提高效率")
    
    print("\n4. 降级策略：")
    print("   - API调用失败时使用数据库缓存")
    print("   - 数据库无数据时使用手动计算")


if __name__ == "__main__":
    print("Tushare stk_factor_pro 接口详细测试")
    print("="*80)
    print(f"Token: {TUSHARE_TOKEN[:10]}...")
    print("="*80)
    
    # 运行测试
    test_stk_factor_pro_all_fields()
    test_batch_stocks()
    test_date_range_query()
    test_api_limits()
    design_cache_strategy()