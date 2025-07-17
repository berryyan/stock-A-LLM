#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试Tushare技术指标API
了解其功能和限制
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
if not TUSHARE_TOKEN:
    print("请在.env文件中设置TUSHARE_TOKEN")
    exit(1)

ts.set_token(TUSHARE_TOKEN)
pro = ts.pro_api()


def test_stk_factor_pro():
    """测试股票技术面因子接口"""
    print("=== 测试 stk_factor_pro 接口 ===\n")
    
    try:
        # 测试获取贵州茅台最近10天的技术指标
        df = pro.stk_factor_pro(
            ts_code='600519.SH',
            start_date='20250701',
            end_date='20250715',
            fields='ts_code,trade_date,macd_dif,macd_dea,macd,kdj_k,kdj_d,kdj,rsi_6,rsi_12,ma_5,ma_10,ma_20'
        )
        
        if df is not None and not df.empty:
            print("成功获取技术指标数据：")
            print(df.head())
            print(f"\n数据行数: {len(df)}")
            print(f"字段列表: {df.columns.tolist()}")
        else:
            print("未获取到数据")
            
    except Exception as e:
        print(f"调用stk_factor_pro失败: {str(e)}")
        print("可能原因：")
        print("1. 积分不足（需要5000积分）")
        print("2. 接口限制")
        print("3. 参数错误")


def test_daily_basic():
    """测试每日指标接口"""
    print("\n\n=== 测试 daily_basic 接口 ===\n")
    
    try:
        # 获取基础行情数据
        df = pro.daily_basic(
            ts_code='600519.SH',
            start_date='20250710',
            end_date='20250715'
        )
        
        if df is not None and not df.empty:
            print("成功获取每日指标数据：")
            print(df[['ts_code', 'trade_date', 'close', 'turnover_rate', 'volume_ratio', 'pe', 'pb']])
        else:
            print("未获取到数据")
            
    except Exception as e:
        print(f"调用daily_basic失败: {str(e)}")


def test_manual_calculation():
    """测试手动计算技术指标"""
    print("\n\n=== 测试手动计算技术指标 ===\n")
    
    try:
        # 获取日线数据
        df = pro.daily(
            ts_code='600519.SH',
            start_date='20250601',
            end_date='20250715'
        )
        
        if df is not None and not df.empty:
            # 按日期排序
            df = df.sort_values('trade_date')
            
            # 计算5日、10日、20日均线
            df['ma5'] = df['close'].rolling(window=5).mean()
            df['ma10'] = df['close'].rolling(window=10).mean()
            df['ma20'] = df['close'].rolling(window=20).mean()
            
            # 判断均线多头排列（MA5 > MA10 > MA20）
            df['ma_bullish'] = (df['ma5'] > df['ma10']) & (df['ma10'] > df['ma20'])
            
            print("计算均线结果（最近5天）：")
            print(df[['trade_date', 'close', 'ma5', 'ma10', 'ma20', 'ma_bullish']].tail())
            
            # 使用talib计算MACD（如果安装了）
            try:
                import talib
                
                # 计算MACD
                df['dif'], df['dea'], df['macd'] = talib.MACD(
                    df['close'].values,
                    fastperiod=12,
                    slowperiod=26,
                    signalperiod=9
                )
                
                # 判断MACD红柱（MACD > 0）
                df['macd_red'] = df['macd'] > 0
                
                print("\n\nMACD计算结果（最近5天）：")
                print(df[['trade_date', 'close', 'dif', 'dea', 'macd', 'macd_red']].tail())
                
            except ImportError:
                print("\n未安装talib，跳过MACD计算")
                print("安装方法: pip install TA-Lib")
                
        else:
            print("未获取到日线数据")
            
    except Exception as e:
        print(f"手动计算失败: {str(e)}")


def test_concept_stock_technical():
    """测试概念股技术筛选场景"""
    print("\n\n=== 模拟概念股技术筛选 ===\n")
    
    # 假设这是某个概念的成分股
    concept_stocks = ['600519.SH', '000858.SZ', '002304.SZ']
    
    results = []
    
    for stock in concept_stocks:
        try:
            # 获取最近30天数据用于计算
            df = pro.daily(
                ts_code=stock,
                start_date='20250615',
                end_date='20250715'
            )
            
            if df is not None and not df.empty:
                df = df.sort_values('trade_date')
                
                # 计算技术指标
                df['ma5'] = df['close'].rolling(window=5).mean()
                df['ma10'] = df['close'].rolling(window=10).mean()
                
                # 获取最新数据
                latest = df.iloc[-1]
                
                # 判断条件
                ma_bullish = latest['ma5'] > latest['ma10']
                
                results.append({
                    'ts_code': stock,
                    'close': latest['close'],
                    'ma5': latest['ma5'],
                    'ma10': latest['ma10'],
                    'ma_bullish': ma_bullish,
                    'pct_chg': latest['pct_chg']
                })
                
        except Exception as e:
            print(f"处理{stock}失败: {str(e)}")
    
    # 显示结果
    result_df = pd.DataFrame(results)
    print("概念股技术筛选结果：")
    print(result_df)
    
    # 筛选符合条件的股票
    filtered = result_df[result_df['ma_bullish'] == True]
    print(f"\n符合MA5>MA10条件的股票：")
    print(filtered[['ts_code', 'close', 'ma5', 'ma10']])


def check_api_limits():
    """检查API限制和积分情况"""
    print("\n\n=== API限制说明 ===\n")
    
    print("1. daily接口（日线行情）：")
    print("   - 免费使用")
    print("   - 限制：单次最多5000条数据")
    print("   - 频率：120积分每分钟最多200次")
    
    print("\n2. daily_basic接口（每日指标）：")
    print("   - 需要120积分")
    print("   - 包含PE、PB、市值等")
    
    print("\n3. stk_factor_pro接口（技术因子）：")
    print("   - 需要5000积分")
    print("   - 包含MACD、KDJ、RSI等技术指标")
    print("   - 提供不复权、前复权、后复权数据")
    
    print("\n4. 手动计算方案：")
    print("   - 使用daily获取原始数据")
    print("   - 使用pandas计算MA均线")
    print("   - 使用talib计算MACD、KDJ等复杂指标")


if __name__ == "__main__":
    # 测试各种方法
    test_daily_basic()
    test_manual_calculation()
    test_concept_stock_technical()
    test_stk_factor_pro()  # 可能失败，需要5000积分
    check_api_limits()