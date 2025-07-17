#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
技术指标数据采集器
负责采集股票的技术指标数据，主要使用Tushare的stk_factor_pro接口
"""

import logging
import pandas as pd
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed
import time

from database.mysql_connector import MySQLConnector
from utils.date_intelligence import DateIntelligence

logger = logging.getLogger(__name__)


class TechnicalCollector:
    """技术指标数据采集器"""
    
    def __init__(self, db: MySQLConnector = None):
        """初始化"""
        self.db = db or MySQLConnector()
        self.date_intelligence = DateIntelligence()
        
        # 缓存配置
        self._cache = {}
        self._cache_expiry = {}
        self._cache_ttl = 3600  # 缓存1小时
        
        # 并发控制
        self._max_workers = 5
        self._batch_size = 50
        
        logger.info("TechnicalCollector初始化完成")
    
    def collect_technical_data(
        self, 
        stock_codes: List[str],
        start_date: str = None,
        end_date: str = None,
        force_refresh: bool = False
    ) -> Dict[str, Dict[str, Any]]:
        """
        批量采集技术指标数据
        
        Args:
            stock_codes: 股票代码列表
            start_date: 开始日期
            end_date: 结束日期
            force_refresh: 是否强制刷新
            
        Returns:
            {ts_code: technical_data} 字典
        """
        if not stock_codes:
            return {}
        
        # 设置默认日期范围（最近21个交易日）
        if not end_date:
            end_date = self.date_intelligence.get_latest_trading_day()
        if not start_date:
            start_date = self.date_intelligence.get_n_trading_days_before(end_date, 21)
        
        logger.info(f"开始采集 {len(stock_codes)} 只股票的技术指标数据，日期范围：{start_date} 至 {end_date}")
        
        # 分批处理
        results = {}
        for i in range(0, len(stock_codes), self._batch_size):
            batch_codes = stock_codes[i:i + self._batch_size]
            batch_results = self._collect_batch(batch_codes, start_date, end_date, force_refresh)
            results.update(batch_results)
        
        logger.info(f"技术指标数据采集完成，成功 {len(results)} 只")
        
        return results
    
    def _collect_batch(
        self,
        batch_codes: List[str],
        start_date: str,
        end_date: str,
        force_refresh: bool
    ) -> Dict[str, Dict[str, Any]]:
        """批量采集一组股票的数据"""
        results = {}
        
        # 检查缓存
        if not force_refresh:
            cached_results = self._get_cached_data(batch_codes, start_date, end_date)
            results.update(cached_results)
            batch_codes = [code for code in batch_codes if code not in cached_results]
        
        if not batch_codes:
            return results
        
        # 从数据库查询
        db_results = self._query_technical_data(batch_codes, start_date, end_date)
        
        # 处理查询结果
        for ts_code in batch_codes:
            if ts_code in db_results:
                processed_data = self._process_technical_data(db_results[ts_code])
                results[ts_code] = processed_data
                
                # 更新缓存
                self._update_cache(ts_code, start_date, end_date, processed_data)
        
        return results
    
    def _query_technical_data(
        self,
        ts_codes: List[str],
        start_date: str,
        end_date: str
    ) -> Dict[str, pd.DataFrame]:
        """
        从数据库查询技术指标数据
        
        使用stk_factor_pro表，包含各种技术指标
        """
        # 构建SQL查询
        codes_str = ','.join([f"'{code}'" for code in ts_codes])
        
        query = f"""
        SELECT 
            ts_code,
            trade_date,
            close,
            turnover_rate,
            volume_ratio,
            pe,
            pb,
            ps,
            dv_ratio,
            total_share,
            float_share,
            free_share,
            total_mv,
            circ_mv,
            macd_dif,
            macd_dea,
            macd,
            kdj_k,
            kdj_d,
            kdj_j,
            rsi_6,
            rsi_12,
            rsi_24,
            boll_upper,
            boll_mid,
            boll_lower,
            cci
        FROM 
            tu_stk_factor_pro
        WHERE 
            ts_code IN ({codes_str})
            AND trade_date >= '{start_date.replace("-", "")}'
            AND trade_date <= '{end_date.replace("-", "")}'
        ORDER BY 
            ts_code, trade_date DESC
        """
        
        try:
            df = pd.read_sql(query, self.db.connection)
            
            if df.empty:
                logger.warning(f"未查询到技术指标数据，股票：{ts_codes[:3]}...")
                return {}
            
            # 按股票代码分组
            grouped = df.groupby('ts_code')
            results = {ts_code: group for ts_code, group in grouped}
            
            logger.info(f"查询到 {len(results)} 只股票的技术指标数据")
            
            return results
            
        except Exception as e:
            logger.error(f"查询技术指标数据失败：{e}")
            return {}
    
    def _process_technical_data(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        处理技术指标数据，提取关键指标
        """
        if df.empty:
            return {}
        
        # 确保按日期排序（最新的在前）
        df = df.sort_values('trade_date', ascending=False)
        
        # 获取最新数据
        latest = df.iloc[0]
        
        # 计算均线（如果有足够的数据）
        close_prices = df['close'].values
        ma5 = float(close_prices[:5].mean()) if len(close_prices) >= 5 else 0
        ma10 = float(close_prices[:10].mean()) if len(close_prices) >= 10 else 0
        ma20 = float(close_prices[:20].mean()) if len(close_prices) >= 20 else 0
        
        # 判断MACD金叉死叉
        macd_cross = self._check_macd_cross(df)
        
        # 判断KDJ状态
        kdj_status = self._check_kdj_status(latest)
        
        # 构建结果
        result = {
            # 最新价格和成交数据
            'latest_close': float(latest['close']) if pd.notna(latest['close']) else 0,
            'latest_trade_date': latest['trade_date'],
            'turnover_rate': float(latest['turnover_rate']) if pd.notna(latest['turnover_rate']) else 0,
            'volume_ratio': float(latest['volume_ratio']) if pd.notna(latest['volume_ratio']) else 0,
            
            # 估值指标
            'pe': float(latest['pe']) if pd.notna(latest['pe']) else 0,
            'pb': float(latest['pb']) if pd.notna(latest['pb']) else 0,
            'ps': float(latest['ps']) if pd.notna(latest['ps']) else 0,
            
            # 市值数据
            'total_mv': float(latest['total_mv']) if pd.notna(latest['total_mv']) else 0,
            'circ_mv': float(latest['circ_mv']) if pd.notna(latest['circ_mv']) else 0,
            
            # MACD指标
            'latest_macd': float(latest['macd']) if pd.notna(latest['macd']) else 0,
            'latest_dif': float(latest['macd_dif']) if pd.notna(latest['macd_dif']) else 0,
            'latest_dea': float(latest['macd_dea']) if pd.notna(latest['macd_dea']) else 0,
            'macd_cross': macd_cross,
            
            # KDJ指标
            'kdj_k': float(latest['kdj_k']) if pd.notna(latest['kdj_k']) else 0,
            'kdj_d': float(latest['kdj_d']) if pd.notna(latest['kdj_d']) else 0,
            'kdj_j': float(latest['kdj_j']) if pd.notna(latest['kdj_j']) else 0,
            'kdj_status': kdj_status,
            
            # RSI指标
            'rsi_6': float(latest['rsi_6']) if pd.notna(latest['rsi_6']) else 0,
            'rsi_12': float(latest['rsi_12']) if pd.notna(latest['rsi_12']) else 0,
            'rsi_24': float(latest['rsi_24']) if pd.notna(latest['rsi_24']) else 0,
            
            # 布林带
            'boll_upper': float(latest['boll_upper']) if pd.notna(latest['boll_upper']) else 0,
            'boll_mid': float(latest['boll_mid']) if pd.notna(latest['boll_mid']) else 0,
            'boll_lower': float(latest['boll_lower']) if pd.notna(latest['boll_lower']) else 0,
            
            # CCI指标
            'cci': float(latest['cci']) if pd.notna(latest['cci']) else 0,
            
            # 均线数据
            'ma5': ma5,
            'ma10': ma10,
            'ma20': ma20,
            
            # 技术形态判断
            'ma_trend': self._check_ma_trend(ma5, ma10, ma20),
            'price_position': self._check_price_position(float(latest['close']), ma5, ma10, ma20),
            
            # 原始数据行数（用于验证数据完整性）
            'data_count': len(df)
        }
        
        return result
    
    def _check_macd_cross(self, df: pd.DataFrame) -> str:
        """
        检查MACD金叉死叉状态
        
        Returns:
            'golden_cross': 金叉
            'dead_cross': 死叉
            'above_zero': 零轴上方
            'below_zero': 零轴下方
        """
        if len(df) < 2:
            return 'unknown'
        
        # 获取最新两天的数据
        today = df.iloc[0]
        yesterday = df.iloc[1]
        
        today_dif = float(today['macd_dif']) if pd.notna(today['macd_dif']) else 0
        today_dea = float(today['macd_dea']) if pd.notna(today['macd_dea']) else 0
        yesterday_dif = float(yesterday['macd_dif']) if pd.notna(yesterday['macd_dif']) else 0
        yesterday_dea = float(yesterday['macd_dea']) if pd.notna(yesterday['macd_dea']) else 0
        
        # 判断金叉死叉
        if yesterday_dif <= yesterday_dea and today_dif > today_dea:
            return 'golden_cross'
        elif yesterday_dif >= yesterday_dea and today_dif < today_dea:
            return 'dead_cross'
        elif today_dif > 0 and today_dea > 0:
            return 'above_zero'
        else:
            return 'below_zero'
    
    def _check_kdj_status(self, latest: pd.Series) -> str:
        """
        检查KDJ状态
        
        Returns:
            'oversold': 超卖
            'overbought': 超买
            'normal': 正常
        """
        k = float(latest['kdj_k']) if pd.notna(latest['kdj_k']) else 50
        d = float(latest['kdj_d']) if pd.notna(latest['kdj_d']) else 50
        j = float(latest['kdj_j']) if pd.notna(latest['kdj_j']) else 50
        
        if k < 20 and d < 20:
            return 'oversold'
        elif k > 80 and d > 80:
            return 'overbought'
        else:
            return 'normal'
    
    def _check_ma_trend(self, ma5: float, ma10: float, ma20: float) -> str:
        """
        检查均线趋势
        
        Returns:
            'bullish': 多头排列
            'bearish': 空头排列
            'mixed': 混合
        """
        if ma5 > ma10 > ma20 and ma5 > 0:
            return 'bullish'
        elif ma5 < ma10 < ma20 and ma5 > 0:
            return 'bearish'
        else:
            return 'mixed'
    
    def _check_price_position(
        self, 
        close: float, 
        ma5: float, 
        ma10: float, 
        ma20: float
    ) -> str:
        """
        检查价格相对均线的位置
        
        Returns:
            'strong': 价格在所有均线之上
            'normal': 价格在部分均线之上
            'weak': 价格在所有均线之下
        """
        if close > ma5 and close > ma10 and close > ma20:
            return 'strong'
        elif close < ma5 and close < ma10 and close < ma20:
            return 'weak'
        else:
            return 'normal'
    
    def _get_cached_data(
        self,
        ts_codes: List[str],
        start_date: str,
        end_date: str
    ) -> Dict[str, Dict[str, Any]]:
        """从缓存获取数据"""
        results = {}
        current_time = time.time()
        
        for ts_code in ts_codes:
            cache_key = f"{ts_code}_{start_date}_{end_date}"
            
            if cache_key in self._cache:
                # 检查是否过期
                if current_time < self._cache_expiry.get(cache_key, 0):
                    results[ts_code] = self._cache[cache_key]
                    logger.debug(f"从缓存获取 {ts_code} 的技术数据")
                else:
                    # 清理过期缓存
                    del self._cache[cache_key]
                    del self._cache_expiry[cache_key]
        
        return results
    
    def _update_cache(
        self,
        ts_code: str,
        start_date: str,
        end_date: str,
        data: Dict[str, Any]
    ):
        """更新缓存"""
        cache_key = f"{ts_code}_{start_date}_{end_date}"
        self._cache[cache_key] = data
        self._cache_expiry[cache_key] = time.time() + self._cache_ttl
    
    def get_latest_technical_indicators(
        self,
        ts_codes: List[str]
    ) -> Dict[str, Dict[str, Any]]:
        """
        获取最新的技术指标（简化版本，只获取最新一天）
        
        Args:
            ts_codes: 股票代码列表
            
        Returns:
            技术指标数据字典
        """
        end_date = self.date_intelligence.get_latest_trading_day()
        start_date = end_date  # 只获取最新一天
        
        return self.collect_technical_data(ts_codes, start_date, end_date)


# 测试
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    collector = TechnicalCollector()
    
    # 测试股票
    test_codes = ['600519.SH', '000001.SZ', '000002.SZ']
    
    # 采集数据
    results = collector.collect_technical_data(test_codes)
    
    # 打印结果
    for ts_code, data in results.items():
        print(f"\n{ts_code} 技术指标：")
        print(f"  最新收盘价: {data.get('latest_close', 0):.2f}")
        print(f"  MACD: {data.get('latest_macd', 0):.3f}")
        print(f"  MACD状态: {data.get('macd_cross')}")
        print(f"  均线趋势: {data.get('ma_trend')}")
        print(f"  KDJ状态: {data.get('kdj_status')}")
        print(f"  RSI(6): {data.get('rsi_6', 0):.2f}")