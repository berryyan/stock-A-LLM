#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
技术指标数据导入脚本
用于从tu_daily_detail表计算技术指标并导入tu_technical_indicators表

运行方式：
python scripts/data_import/import_technical_indicators.py

参数：
--start-date: 开始日期（默认：2年前）
--end-date: 结束日期（默认：今天）
--batch-size: 批量大小（默认：1000）
--stocks: 指定股票代码列表（默认：全部）
"""

import os
import sys
import argparse
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import pandas as pd
import numpy as np
from sqlalchemy import create_engine, text
from concurrent.futures import ThreadPoolExecutor, as_completed
import warnings
warnings.filterwarnings('ignore')

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from config.database import get_mysql_connection_string
from utils.logger import setup_logger

# 设置日志
logger = setup_logger('technical_import', 'logs/technical_import.log')


class TechnicalIndicatorImporter:
    """技术指标数据导入器"""
    
    def __init__(self, batch_size: int = 1000):
        """初始化导入器"""
        self.batch_size = batch_size
        self.engine = create_engine(get_mysql_connection_string())
        self.processed_count = 0
        self.error_count = 0
        
    def import_data(
        self, 
        start_date: str, 
        end_date: str, 
        stock_list: Optional[List[str]] = None
    ):
        """导入技术指标数据"""
        logger.info(f"开始导入技术指标数据: {start_date} 至 {end_date}")
        
        # 获取股票列表
        if stock_list:
            stocks = stock_list
        else:
            stocks = self._get_all_stocks()
        
        logger.info(f"共需处理 {len(stocks)} 只股票")
        
        # 多线程处理
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = []
            for stock in stocks:
                future = executor.submit(
                    self._process_stock, 
                    stock, 
                    start_date, 
                    end_date
                )
                futures.append(future)
            
            # 等待所有任务完成
            for future in as_completed(futures):
                try:
                    future.result()
                except Exception as e:
                    logger.error(f"处理股票时出错: {e}")
                    self.error_count += 1
        
        logger.info(f"导入完成！处理: {self.processed_count}, 错误: {self.error_count}")
    
    def _get_all_stocks(self) -> List[str]:
        """获取所有股票代码"""
        query = """
        SELECT DISTINCT ts_code 
        FROM tu_stock_basic 
        WHERE list_status = 'L'
        ORDER BY ts_code
        """
        
        with self.engine.connect() as conn:
            result = conn.execute(text(query))
            return [row[0] for row in result]
    
    def _process_stock(self, ts_code: str, start_date: str, end_date: str):
        """处理单只股票"""
        try:
            logger.info(f"处理股票: {ts_code}")
            
            # 获取股票数据
            df = self._get_stock_data(ts_code, start_date, end_date)
            if df.empty:
                logger.warning(f"股票 {ts_code} 无数据")
                return
            
            # 计算技术指标
            df = self._calculate_indicators(df)
            
            # 识别信号
            df = self._identify_signals(df)
            
            # 保存到数据库
            self._save_to_database(df, ts_code)
            
            self.processed_count += 1
            logger.info(f"股票 {ts_code} 处理完成")
            
        except Exception as e:
            logger.error(f"处理股票 {ts_code} 时出错: {e}")
            raise
    
    def _get_stock_data(self, ts_code: str, start_date: str, end_date: str) -> pd.DataFrame:
        """获取股票历史数据"""
        # 需要获取更早的数据用于计算（如250日均线需要250天前的数据）
        extended_start = (
            datetime.strptime(start_date, '%Y%m%d') - timedelta(days=300)
        ).strftime('%Y%m%d')
        
        query = f"""
        SELECT 
            trade_date,
            open_qfq as open,
            high_qfq as high,
            low_qfq as low,
            close_qfq as close,
            pre_close_qfq as pre_close,
            vol as volume,
            amount,
            turnover_rate
        FROM tu_daily_detail
        WHERE ts_code = '{ts_code}'
          AND trade_date BETWEEN '{extended_start}' AND '{end_date}'
        ORDER BY trade_date
        """
        
        df = pd.read_sql(query, self.engine)
        df['trade_date'] = pd.to_datetime(df['trade_date'])
        df.set_index('trade_date', inplace=True)
        
        return df
    
    def _calculate_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """计算技术指标"""
        # 计算涨跌幅
        df['change_rate'] = (df['close'] / df['pre_close'] - 1) * 100
        
        # 计算振幅
        df['amplitude'] = (df['high'] - df['low']) / df['pre_close'] * 100
        
        # 计算均线
        for period in [5, 10, 20, 30, 60, 120, 250]:
            df[f'ma_{period}'] = df['close'].rolling(window=period).mean()
        
        # 计算EMA
        df['ema_12'] = df['close'].ewm(span=12, adjust=False).mean()
        df['ema_26'] = df['close'].ewm(span=26, adjust=False).mean()
        
        # 计算MACD
        df['macd_dif'] = df['ema_12'] - df['ema_26']
        df['macd_dea'] = df['macd_dif'].ewm(span=9, adjust=False).mean()
        df['macd_histogram'] = df['macd_dif'] - df['macd_dea']
        
        # 计算KDJ
        df = self._calculate_kdj(df)
        
        # 计算RSI
        for period in [6, 12, 24]:
            df[f'rsi_{period}'] = self._calculate_rsi(df['close'], period)
        
        # 计算布林带
        df = self._calculate_bollinger_bands(df)
        
        # 计算成交量指标
        df['volume_ratio'] = df['volume'] / df['volume'].rolling(5).mean()
        df['volume_ma_5'] = df['volume'].rolling(5).mean()
        df['volume_ma_10'] = df['volume'].rolling(10).mean()
        
        return df
    
    def _calculate_kdj(self, df: pd.DataFrame, n: int = 9) -> pd.DataFrame:
        """计算KDJ指标"""
        low_n = df['low'].rolling(window=n).min()
        high_n = df['high'].rolling(window=n).max()
        
        rsv = (df['close'] - low_n) / (high_n - low_n) * 100
        
        df['kdj_k'] = rsv.ewm(alpha=1/3, adjust=False).mean()
        df['kdj_d'] = df['kdj_k'].ewm(alpha=1/3, adjust=False).mean()
        df['kdj_j'] = 3 * df['kdj_k'] - 2 * df['kdj_d']
        
        return df
    
    def _calculate_rsi(self, prices: pd.Series, period: int) -> pd.Series:
        """计算RSI指标"""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        
        return rsi
    
    def _calculate_bollinger_bands(self, df: pd.DataFrame, period: int = 20, std_dev: int = 2) -> pd.DataFrame:
        """计算布林带"""
        df['boll_middle'] = df['close'].rolling(window=period).mean()
        rolling_std = df['close'].rolling(window=period).std()
        
        df['boll_upper'] = df['boll_middle'] + (rolling_std * std_dev)
        df['boll_lower'] = df['boll_middle'] - (rolling_std * std_dev)
        df['boll_width'] = df['boll_upper'] - df['boll_lower']
        
        return df
    
    def _identify_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        """识别交易信号"""
        # MA交叉信号
        df['ma_cross_signal'] = None
        ma5_cross_ma20 = (df['ma_5'] > df['ma_20']) & (df['ma_5'].shift(1) <= df['ma_20'].shift(1))
        ma5_cross_ma20_down = (df['ma_5'] < df['ma_20']) & (df['ma_5'].shift(1) >= df['ma_20'].shift(1))
        df.loc[ma5_cross_ma20, 'ma_cross_signal'] = '金叉'
        df.loc[ma5_cross_ma20_down, 'ma_cross_signal'] = '死叉'
        
        # MACD交叉信号
        df['macd_cross_signal'] = None
        macd_golden = (df['macd_dif'] > df['macd_dea']) & (df['macd_dif'].shift(1) <= df['macd_dea'].shift(1))
        macd_death = (df['macd_dif'] < df['macd_dea']) & (df['macd_dif'].shift(1) >= df['macd_dea'].shift(1))
        df.loc[macd_golden, 'macd_cross_signal'] = '金叉'
        df.loc[macd_death, 'macd_cross_signal'] = '死叉'
        
        # KDJ信号
        df['kdj_signal'] = None
        df.loc[df['kdj_j'] > 100, 'kdj_signal'] = '超买'
        df.loc[df['kdj_j'] < 0, 'kdj_signal'] = '超卖'
        
        # RSI信号
        df['rsi_signal'] = None
        df.loc[df['rsi_6'] > 70, 'rsi_signal'] = '超买'
        df.loc[df['rsi_6'] < 30, 'rsi_signal'] = '超卖'
        
        # 布林带信号
        df['boll_signal'] = None
        df.loc[df['close'] > df['boll_upper'], 'boll_signal'] = '突破上轨'
        df.loc[df['close'] < df['boll_lower'], 'boll_signal'] = '突破下轨'
        
        return df
    
    def _save_to_database(self, df: pd.DataFrame, ts_code: str):
        """保存到数据库"""
        # 重置索引，trade_date变为列
        df = df.reset_index()
        
        # 只保留需要的日期范围
        df['ts_code'] = ts_code
        
        # 选择需要保存的列
        columns = [
            'ts_code', 'trade_date', 'close', 'high', 'low', 'open', 'pre_close',
            'ma_5', 'ma_10', 'ma_20', 'ma_30', 'ma_60', 'ma_120', 'ma_250',
            'ema_12', 'ema_26',
            'macd_dif', 'macd_dea', 'macd_histogram',
            'kdj_k', 'kdj_d', 'kdj_j',
            'rsi_6', 'rsi_12', 'rsi_24',
            'boll_upper', 'boll_middle', 'boll_lower', 'boll_width',
            'volume', 'volume_ratio', 'volume_ma_5', 'volume_ma_10',
            'turnover_rate', 'amplitude', 'change_rate',
            'ma_cross_signal', 'macd_cross_signal', 'kdj_signal', 'rsi_signal', 'boll_signal'
        ]
        
        # 重命名列以匹配数据库
        df = df.rename(columns={
            'close': 'close_price',
            'high': 'high_price',
            'low': 'low_price',
            'open': 'open_price'
        })
        
        # 转换日期格式
        df['trade_date'] = df['trade_date'].dt.strftime('%Y%m%d')
        
        # 选择存在的列
        save_columns = [col for col in columns if col in df.columns or col.replace('_price', '') in df.columns]
        df_save = df[save_columns].copy()
        
        # 批量插入
        for i in range(0, len(df_save), self.batch_size):
            batch = df_save.iloc[i:i+self.batch_size]
            
            try:
                # 使用replace避免重复数据
                batch.to_sql(
                    'tu_technical_indicators',
                    self.engine,
                    if_exists='append',
                    index=False,
                    method='multi'
                )
            except Exception as e:
                logger.error(f"批量插入失败: {e}")
                # 尝试逐条插入
                for _, row in batch.iterrows():
                    try:
                        row.to_frame().T.to_sql(
                            'tu_technical_indicators',
                            self.engine,
                            if_exists='append',
                            index=False
                        )
                    except Exception as e2:
                        logger.error(f"单条插入失败: {e2}")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='导入技术指标数据')
    parser.add_argument(
        '--start-date',
        type=str,
        default=(datetime.now() - timedelta(days=730)).strftime('%Y%m%d'),
        help='开始日期，格式：YYYYMMDD'
    )
    parser.add_argument(
        '--end-date',
        type=str,
        default=datetime.now().strftime('%Y%m%d'),
        help='结束日期，格式：YYYYMMDD'
    )
    parser.add_argument(
        '--batch-size',
        type=int,
        default=1000,
        help='批量大小'
    )
    parser.add_argument(
        '--stocks',
        type=str,
        nargs='+',
        help='指定股票代码列表，如：600519.SH 000002.SZ'
    )
    
    args = parser.parse_args()
    
    # 创建导入器
    importer = TechnicalIndicatorImporter(batch_size=args.batch_size)
    
    # 导入数据
    importer.import_data(
        start_date=args.start_date,
        end_date=args.end_date,
        stock_list=args.stocks
    )


if __name__ == '__main__':
    main()