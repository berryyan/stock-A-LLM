#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
技术指标数据采集器
使用Tushare Pro API获取复权后的技术指标
"""

import tushare as ts
import pandas as pd
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import json
import os
import time
import logging
from utils.date_intelligence import DateIntelligenceModule as DateIntelligence

logger = logging.getLogger(__name__)

class TechnicalCollector:
    """技术指标采集器 - 使用Tushare API"""
    
    def __init__(self):
        """初始化"""
        # 初始化Tushare
        self.token = os.getenv('TUSHARE_TOKEN')
        if not self.token:
            # 尝试从配置文件读取
            try:
                from config.settings import TUSHARE_TOKEN
                self.token = TUSHARE_TOKEN
            except:
                raise ValueError("请设置TUSHARE_TOKEN环境变量或在config/settings.py中配置")
        
        ts.set_token(self.token)
        self.pro = ts.pro_api()
        
        # 初始化日期智能模块
        self.date_intelligence = DateIntelligence()
        
        # 缓存配置
        self.cache_dir = "data/technical_cache"
        os.makedirs(self.cache_dir, exist_ok=True)
        
        # API限流配置
        self.api_calls_per_minute = 200
        self.last_call_time = None
        
        logger.info("技术指标采集器初始化完成（使用Tushare API）")
    
    def get_latest_technical_indicators(self, ts_codes: List[str], days: int = 21) -> Dict[str, Dict]:
        """
        获取最新技术指标数据（Concept Agent专用版本）
        
        Args:
            ts_codes: 股票代码列表
            days: 获取最近N天的数据（用于计算）
            
        Returns:
            {ts_code: {指标数据}}，包含MACD和MA指标
        """
        results = {}
        
        # 获取日期范围
        end_date = self.date_intelligence.calculator.get_latest_trading_day()
        start_date = self.date_intelligence.calculator.get_nth_trading_day_before(days, end_date)
        
        logger.info(f"准备获取{len(ts_codes)}只股票的技术指标，日期范围：{start_date} - {end_date}")
        
        for ts_code in ts_codes:
            try:
                # 先检查缓存
                cached_data = self._get_from_cache(ts_code, end_date)
                if cached_data:
                    results[ts_code] = cached_data
                    continue
                
                # 调用API获取数据
                indicator_data = self._fetch_from_api(ts_code, start_date, end_date)
                if indicator_data:
                    results[ts_code] = indicator_data
                    # 保存到缓存
                    self._save_to_cache(ts_code, end_date, indicator_data)
                else:
                    results[ts_code] = self._get_empty_indicators()
                    
            except Exception as e:
                logger.error(f"获取{ts_code}技术指标失败: {str(e)}")
                results[ts_code] = self._get_empty_indicators()
        
        return results
    
    def _fetch_from_api(self, ts_code: str, start_date: str, end_date: str) -> Optional[Dict]:
        """
        从Tushare API获取技术指标
        
        使用stk_factor_pro接口获取复权后的技术指标
        """
        try:
            # API限流控制
            self._rate_limit()
            
            # 调用stk_factor_pro接口
            # 注意：该接口需要Tushare积分权限
            df = self.pro.stk_factor_pro(
                ts_code=ts_code,
                start_date=start_date.replace('-', ''),
                end_date=end_date.replace('-', ''),
                fields='ts_code,trade_date,close_qfq,macd_qfq,macd_dif_qfq,macd_dea_qfq,ma_qfq_5,ma_qfq_10'
            )
            
            if df.empty:
                logger.warning(f"{ts_code}无技术指标数据")
                return None
            
            # 按日期排序，获取最新数据
            df = df.sort_values('trade_date', ascending=False)
            latest = df.iloc[0]
            
            # 构建返回数据（专为Concept Agent设计）
            return {
                'trade_date': latest['trade_date'],
                'close': float(latest['close_qfq']) if pd.notna(latest['close_qfq']) else 0,
                # MACD相关数据
                'macd': float(latest['macd_qfq']) if pd.notna(latest['macd_qfq']) else 0,
                'macd_dif': float(latest['macd_dif_qfq']) if pd.notna(latest['macd_dif_qfq']) else 0,
                'macd_dea': float(latest['macd_dea_qfq']) if pd.notna(latest['macd_dea_qfq']) else 0,
                # 均线数据
                'ma5': float(latest['ma_qfq_5']) if pd.notna(latest['ma_qfq_5']) else 0,
                'ma10': float(latest['ma_qfq_10']) if pd.notna(latest['ma_qfq_10']) else 0,
                # 计算技术形态（用于评分）
                'macd_above_water': self._check_macd_above_water(latest),
                'ma_bullish': self._check_ma_bullish(latest)
            }
            
        except Exception as e:
            logger.error(f"API调用失败 {ts_code}: {str(e)}")
            # 如果是积分不足或接口权限问题，尝试使用基础数据计算
            if "积分" in str(e) or "权限" in str(e):
                logger.info(f"尝试使用基础数据计算{ts_code}的技术指标")
                return self._calculate_from_daily(ts_code, start_date, end_date)
            return None
    
    def _calculate_from_daily(self, ts_code: str, start_date: str, end_date: str) -> Optional[Dict]:
        """
        从日线数据计算技术指标（降级方案）
        """
        try:
            # 获取更多天数的数据用于计算
            extended_start = self.date_intelligence.calculator.get_nth_trading_day_before(60, end_date)
            
            # 获取日线数据
            df = self.pro.daily(
                ts_code=ts_code,
                start_date=extended_start.replace('-', ''),
                end_date=end_date.replace('-', '')
            )
            
            if df.empty or len(df) < 20:
                logger.warning(f"{ts_code}历史数据不足，无法计算技术指标")
                return None
            
            # 按日期排序
            df = df.sort_values('trade_date', ascending=True)
            
            # 计算复权因子
            df = self._calculate_adjust_factor(df, ts_code)
            
            # 计算复权收盘价
            df['close_qfq'] = df['close'] * df['adj_factor']
            
            # 计算MA
            df['ma5'] = df['close_qfq'].rolling(window=5).mean()
            df['ma10'] = df['close_qfq'].rolling(window=10).mean()
            
            # 简化的MACD计算
            df['ema12'] = df['close_qfq'].ewm(span=12, adjust=False).mean()
            df['ema26'] = df['close_qfq'].ewm(span=26, adjust=False).mean()
            df['dif'] = df['ema12'] - df['ema26']
            df['dea'] = df['dif'].ewm(span=9, adjust=False).mean()
            df['macd'] = (df['dif'] - df['dea']) * 2
            
            # 获取最新数据
            df = df.sort_values('trade_date', ascending=False)
            latest = df.iloc[0]
            
            return {
                'trade_date': latest['trade_date'],
                'close': float(latest['close_qfq']),
                'macd': float(latest['macd']) if pd.notna(latest['macd']) else 0,
                'macd_dif': float(latest['dif']) if pd.notna(latest['dif']) else 0,
                'macd_dea': float(latest['dea']) if pd.notna(latest['dea']) else 0,
                'ma5': float(latest['ma5']) if pd.notna(latest['ma5']) else 0,
                'ma10': float(latest['ma10']) if pd.notna(latest['ma10']) else 0,
                'macd_above_water': latest['macd'] > 0 and latest['dif'] > 0,
                'ma_bullish': latest['ma5'] > latest['ma10'] if pd.notna(latest['ma5']) and pd.notna(latest['ma10']) else False
            }
            
        except Exception as e:
            logger.error(f"从日线计算技术指标失败 {ts_code}: {str(e)}")
            return None
    
    def _calculate_adjust_factor(self, df: pd.DataFrame, ts_code: str) -> pd.DataFrame:
        """计算复权因子"""
        try:
            # 获取复权因子
            adj_df = self.pro.adj_factor(
                ts_code=ts_code,
                start_date=df['trade_date'].min(),
                end_date=df['trade_date'].max()
            )
            
            if not adj_df.empty:
                # 合并复权因子
                df = df.merge(adj_df[['trade_date', 'adj_factor']], on='trade_date', how='left')
                # 填充缺失值
                df['adj_factor'] = df['adj_factor'].fillna(1.0)
            else:
                df['adj_factor'] = 1.0
                
        except Exception as e:
            logger.warning(f"获取复权因子失败，使用不复权数据: {e}")
            df['adj_factor'] = 1.0
            
        return df
    
    def _check_macd_above_water(self, row) -> bool:
        """检查MACD是否在水上（MACD>0且DIF>0）"""
        try:
            macd = float(row.get('macd_qfq', row.get('macd', 0)))
            dif = float(row.get('macd_dif_qfq', row.get('dif', 0)))
            return macd > 0 and dif > 0
        except:
            return False
    
    def _check_ma_bullish(self, row) -> bool:
        """检查均线是否多头排列（MA5>MA10）"""
        try:
            ma5 = float(row.get('ma_qfq_5', row.get('ma5', 0)))
            ma10 = float(row.get('ma_qfq_10', row.get('ma10', 0)))
            return ma5 > ma10 and ma5 > 0 and ma10 > 0
        except:
            return False
    
    def _rate_limit(self):
        """API限流控制"""
        if self.last_call_time:
            elapsed = time.time() - self.last_call_time
            if elapsed < 60 / self.api_calls_per_minute:
                sleep_time = 60 / self.api_calls_per_minute - elapsed
                time.sleep(sleep_time)
        
        self.last_call_time = time.time()
    
    def _get_from_cache(self, ts_code: str, date: str) -> Optional[Dict]:
        """从缓存获取数据"""
        cache_file = os.path.join(self.cache_dir, f"{ts_code}_{date}.json")
        
        if os.path.exists(cache_file):
            try:
                # 检查文件修改时间，超过5小时则过期
                file_time = os.path.getmtime(cache_file)
                if time.time() - file_time > 5 * 3600:
                    return None
                    
                with open(cache_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                logger.debug(f"从缓存获取{ts_code}的技术指标")
                return data
            except:
                pass
        
        return None
    
    def _save_to_cache(self, ts_code: str, date: str, data: Dict):
        """保存到缓存"""
        cache_file = os.path.join(self.cache_dir, f"{ts_code}_{date}.json")
        
        try:
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False)
            logger.debug(f"缓存{ts_code}的技术指标")
        except Exception as e:
            logger.error(f"缓存保存失败: {str(e)}")
    
    def _get_empty_indicators(self) -> Dict:
        """返回空指标数据"""
        return {
            'trade_date': '',
            'close': 0,
            'macd': 0,
            'macd_dif': 0,
            'macd_dea': 0,
            'ma5': 0,
            'ma10': 0,
            'macd_above_water': False,
            'ma_bullish': False
        }
    
    def batch_update_cache(self, ts_codes: List[str]):
        """
        批量更新缓存（盘后运行）
        
        Args:
            ts_codes: 需要更新的股票列表
        """
        logger.info(f"开始批量更新{len(ts_codes)}只股票的技术指标缓存")
        
        success_count = 0
        for i, ts_code in enumerate(ts_codes):
            if i % 50 == 0:
                logger.info(f"进度: {i}/{len(ts_codes)}")
            
            try:
                end_date = self.date_intelligence.calculator.get_latest_trading_day()
                start_date = self.date_intelligence.calculator.get_nth_trading_day_before(30, end_date)
                
                data = self._fetch_from_api(ts_code, start_date, end_date)
                if data:
                    self._save_to_cache(ts_code, end_date, data)
                    success_count += 1
                    
            except Exception as e:
                logger.error(f"更新{ts_code}失败: {str(e)}")
        
        logger.info(f"批量更新完成，成功: {success_count}/{len(ts_codes)}")


# 测试代码
if __name__ == "__main__":
    collector = TechnicalCollector()
    
    # 测试单个股票
    test_codes = ["600519.SH", "000858.SZ"]
    results = collector.get_latest_technical_indicators(test_codes, days=21)
    
    for ts_code, data in results.items():
        print(f"\n{ts_code} 技术指标:")
        print(f"  交易日期: {data['trade_date']}")
        print(f"  收盘价: {data['close']:.2f}")
        print(f"  MACD: {data['macd']:.3f}")
        print(f"  DIF: {data['macd_dif']:.3f}")
        print(f"  DEA: {data['macd_dea']:.3f}")
        print(f"  MA5: {data['ma5']:.2f}")
        print(f"  MA10: {data['ma10']:.2f}")
        print(f"  MACD水上: {'是' if data['macd_above_water'] else '否'}")
        print(f"  均线多头: {'是' if data['ma_bullish'] else '否'}")