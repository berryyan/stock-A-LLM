#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
资金流向数据采集器
用于采集个股和板块的资金流向数据
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import pandas as pd
from functools import lru_cache
import asyncio
from concurrent.futures import ThreadPoolExecutor, as_completed

from database.mysql_connector import MySQLConnector
from utils.date_intelligence import DateIntelligenceModule as DateIntelligence

logger = logging.getLogger(__name__)


class MoneyFlowCollector:
    """资金流向数据采集器"""
    
    def __init__(self):
        """初始化采集器"""
        self.db = MySQLConnector()
        self.date_parser = DateIntelligence()
        self._cache = {}  # 内存缓存
        self._cache_ttl = 3600  # 缓存1小时
        self.max_workers = 5  # 最大并发数
        logger.info("MoneyFlowCollector初始化完成")
    
    def get_stock_money_flow(self, ts_code: str, days: int = 5) -> Dict[str, Any]:
        """
        获取个股资金流向数据
        
        Args:
            ts_code: 股票代码
            days: 获取天数（默认5天）
            
        Returns:
            包含资金流向数据的字典
        """
        cache_key = f"stock_flow_{ts_code}_{days}"
        
        # 检查缓存
        if cache_key in self._cache:
            cached_data, cache_time = self._cache[cache_key]
            if (datetime.now() - cache_time).seconds < self._cache_ttl:
                return cached_data
        
        try:
            # 获取最新交易日
            latest_date = self.date_parser.calculator.get_latest_trading_day()
            start_date = self.date_parser.calculator.get_nth_trading_day_before(days - 1, latest_date)
            
            # 查询资金流向数据（注意：为安全起见，仅对已验证的参数使用字符串格式化）
            query = f"""
            SELECT 
                trade_date,
                ts_code,
                name,
                close,
                pct_change,
                net_amount,
                net_amount_rate,
                buy_elg_amount,
                buy_lg_amount,
                buy_md_amount,
                buy_sm_amount,
                buy_elg_amount + buy_lg_amount as main_net_amount,
                buy_elg_amount_rate + buy_lg_amount_rate as main_net_rate
            FROM tu_moneyflow_dc
            WHERE ts_code = '{ts_code}' 
                AND trade_date >= '{start_date}' 
                AND trade_date <= '{latest_date}'
            ORDER BY trade_date DESC
            """
            
            df = pd.read_sql(query, self.db.engine)
            
            if df.empty:
                logger.warning(f"未找到{ts_code}的资金流向数据")
                return self._empty_money_flow_data()
            
            # 计算统计指标
            result = self._calculate_money_flow_stats(df)
            
            # 缓存结果
            self._cache[cache_key] = (result, datetime.now())
            
            return result
            
        except Exception as e:
            logger.error(f"获取{ts_code}资金流向数据失败: {str(e)}")
            return self._empty_money_flow_data()
    
    def get_batch_money_flow(self, ts_codes: List[str], days: int = 5) -> Dict[str, Dict]:
        """
        批量获取多只股票的资金流向数据
        
        Args:
            ts_codes: 股票代码列表
            days: 获取天数
            
        Returns:
            {ts_code: money_flow_data}
        """
        results = {}
        
        # 使用线程池并发获取
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_code = {
                executor.submit(self.get_stock_money_flow, code, days): code 
                for code in ts_codes
            }
            
            for future in as_completed(future_to_code):
                ts_code = future_to_code[future]
                try:
                    results[ts_code] = future.result()
                except Exception as e:
                    logger.error(f"获取{ts_code}资金流向失败: {str(e)}")
                    results[ts_code] = self._empty_money_flow_data()
        
        return results
    
    def get_sector_money_flow(self, sector_code: str) -> Dict[str, Any]:
        """
        获取板块资金流向数据
        
        Args:
            sector_code: 板块代码（如BK0459.DC）
            
        Returns:
            板块资金流向数据
        """
        try:
            latest_date = self.date_parser.calculator.get_latest_trading_day()
            
            query = f"""
            SELECT 
                trade_date,
                ts_code,
                name,
                content_type,
                net_amount,
                net_amount_rate,
                buy_elg_amount,
                buy_lg_amount,
                buy_elg_amount + buy_lg_amount as main_net_amount,
                `rank`
            FROM tu_moneyflow_ind_dc
            WHERE ts_code = '{sector_code}' 
                AND trade_date = '{latest_date}'
            """
            
            df = pd.read_sql(query, self.db.engine)
            
            if df.empty:
                logger.warning(f"未找到板块{sector_code}的资金流向数据")
                return {}
            
            row = df.iloc[0]
            return {
                'sector_code': sector_code,
                'sector_name': row['name'],
                'content_type': row['content_type'],
                'net_amount': float(row['net_amount']),
                'main_net_amount': float(row['main_net_amount']),
                'net_amount_rate': float(row['net_amount_rate']),
                'rank': int(row['rank']) if pd.notna(row['rank']) else None,
                'trade_date': row['trade_date']
            }
            
        except Exception as e:
            logger.error(f"获取板块{sector_code}资金流向失败: {str(e)}")
            return {}
    
    def get_money_flow_rank(self, limit: int = 50, order: str = 'desc') -> List[Dict]:
        """
        获取资金流向排名
        
        Args:
            limit: 返回数量
            order: 排序方式 'desc'降序, 'asc'升序
            
        Returns:
            排名列表
        """
        try:
            latest_date = self.date_parser.calculator.get_latest_trading_day()
            order_by = "DESC" if order == 'desc' else "ASC"
            
            query = f"""
            SELECT 
                ts_code,
                name,
                close,
                pct_change,
                net_amount,
                net_amount_rate,
                buy_elg_amount + buy_lg_amount as main_net_amount,
                buy_elg_amount_rate + buy_lg_amount_rate as main_net_rate
            FROM tu_moneyflow_dc
            WHERE trade_date = '{latest_date}'
            ORDER BY net_amount {order_by}
            LIMIT {limit}
            """
            
            df = pd.read_sql(query, self.db.engine)
            
            results = []
            for idx, row in df.iterrows():
                results.append({
                    'rank': idx + 1,
                    'ts_code': row['ts_code'],
                    'name': row['name'],
                    'close': float(row['close']),
                    'pct_change': float(row['pct_change']),
                    'net_amount': float(row['net_amount']),
                    'net_amount_rate': float(row['net_amount_rate']),
                    'main_net_amount': float(row['main_net_amount']),
                    'main_net_rate': float(row['main_net_rate'])
                })
            
            return results
            
        except Exception as e:
            logger.error(f"获取资金流向排名失败: {str(e)}")
            return []
    
    def _calculate_money_flow_stats(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        计算资金流向统计指标
        
        Args:
            df: 资金流向数据DataFrame
            
        Returns:
            统计结果字典
        """
        latest = df.iloc[0] if not df.empty else None
        
        # 计算连续净流入天数
        continuous_days = 0
        for _, row in df.iterrows():
            if row['net_amount'] > 0:
                continuous_days += 1
            else:
                break
        
        # 计算平均值
        avg_net_amount = df['net_amount'].mean()
        avg_main_net_amount = df['main_net_amount'].mean()
        
        # 计算总和
        total_net_amount = df['net_amount'].sum()
        total_main_net_amount = df['main_net_amount'].sum()
        
        return {
            'latest_data': {
                'trade_date': latest['trade_date'] if latest is not None else None,
                'ts_code': latest['ts_code'] if latest is not None else None,
                'name': latest['name'] if latest is not None else None,
                'close': float(latest['close']) if latest is not None else 0,
                'pct_change': float(latest['pct_change']) if latest is not None else 0,
                'net_amount': float(latest['net_amount']) if latest is not None else 0,
                'main_net_amount': float(latest['main_net_amount']) if latest is not None else 0,
                'net_amount_rate': float(latest['net_amount_rate']) if latest is not None else 0,
                'main_net_rate': float(latest['main_net_rate']) if latest is not None else 0
            },
            'statistics': {
                'continuous_inflow_days': continuous_days,
                'avg_net_amount': float(avg_net_amount),
                'avg_main_net_amount': float(avg_main_net_amount),
                'total_net_amount': float(total_net_amount),
                'total_main_net_amount': float(total_main_net_amount),
                'positive_days': len(df[df['net_amount'] > 0]),
                'negative_days': len(df[df['net_amount'] < 0]),
                'total_days': len(df)
            },
            'detail_data': df.to_dict('records')
        }
    
    def _empty_money_flow_data(self) -> Dict[str, Any]:
        """返回空的资金流向数据结构"""
        return {
            'latest_data': {
                'trade_date': None,
                'ts_code': None,
                'name': None,
                'close': 0,
                'pct_change': 0,
                'net_amount': 0,
                'main_net_amount': 0,
                'net_amount_rate': 0,
                'main_net_rate': 0
            },
            'statistics': {
                'continuous_inflow_days': 0,
                'avg_net_amount': 0,
                'avg_main_net_amount': 0,
                'total_net_amount': 0,
                'total_main_net_amount': 0,
                'positive_days': 0,
                'negative_days': 0,
                'total_days': 0
            },
            'detail_data': []
        }
    
    def __del__(self):
        """清理资源"""
        if hasattr(self, 'db'):
            self.db.close()


# 测试代码
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    print("=== 测试MoneyFlowCollector ===")
    
    collector = MoneyFlowCollector()
    
    # 测试个股资金流向
    print("\n1. 测试个股资金流向（贵州茅台）:")
    result = collector.get_stock_money_flow('600519.SH', days=5)
    if result['latest_data']['trade_date']:
        latest = result['latest_data']
        stats = result['statistics']
        print(f"   最新交易日: {latest['trade_date']}")
        print(f"   股票名称: {latest['name']}")
        print(f"   收盘价: {latest['close']:.2f}")
        print(f"   涨跌幅: {latest['pct_change']:.2f}%")
        print(f"   净流入: {latest['net_amount']:.2f}万元")
        print(f"   主力净流入: {latest['main_net_amount']:.2f}万元")
        print(f"   连续净流入天数: {stats['continuous_inflow_days']}天")
        print(f"   5日平均净流入: {stats['avg_net_amount']:.2f}万元")
    
    # 测试批量获取
    print("\n2. 测试批量获取资金流向:")
    stocks = ['000002.SZ', '000858.SZ', '002594.SZ']
    batch_results = collector.get_batch_money_flow(stocks, days=3)
    for ts_code, data in batch_results.items():
        if data['latest_data']['trade_date']:
            print(f"   {ts_code} - {data['latest_data']['name']}: "
                  f"净流入{data['latest_data']['net_amount']:.2f}万元")
    
    # 测试板块资金流向
    print("\n3. 测试板块资金流向（人工智能）:")
    sector_result = collector.get_sector_money_flow('BK0800.DC')
    if sector_result:
        print(f"   板块名称: {sector_result['sector_name']}")
        print(f"   净流入: {sector_result['net_amount']:.2f}万元")
        print(f"   主力净流入: {sector_result['main_net_amount']:.2f}万元")
        print(f"   排名: {sector_result['rank']}")
    
    # 测试资金流向排名
    print("\n4. 测试资金流向排名TOP5:")
    rank_results = collector.get_money_flow_rank(limit=5)
    for item in rank_results:
        print(f"   {item['rank']}. {item['name']}({item['ts_code']}): "
              f"净流入{item['net_amount']:.2f}万元")
    
    print("\n测试完成！")