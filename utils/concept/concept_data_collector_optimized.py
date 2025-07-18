#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
概念数据采集器 - 性能优化版本
增加查询限制、批量处理、进度显示等优化
"""

import logging
from typing import List, Dict, Any, Optional, Set
from datetime import datetime, timedelta
import pandas as pd
from sqlalchemy import text
import json
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm

from database.mysql_connector import MySQLConnector
from utils.date_intelligence import DateIntelligenceModule as DateIntelligence

logger = logging.getLogger(__name__)


class ConceptDataCollectorOptimized:
    """概念数据采集器 - 优化版"""
    
    # 性能优化参数
    MAX_STOCKS_PER_CONCEPT = 100  # 每个概念最多返回股票数
    BATCH_SIZE = 50              # 批量查询大小
    MAX_WORKERS = 3              # 并发线程数
    
    def __init__(self):
        """初始化"""
        self.db = MySQLConnector()
        self.date_intelligence = DateIntelligence()
        
        # 获取各数据源的最新交易日
        self.latest_dates = {}
        try:
            with self.db.engine.connect() as conn:
                # 同花顺没有trade_date字段，使用默认值
                self.latest_dates['THS'] = '20250717'
                
                # 东财最新日期
                dc_date = conn.execute(text("SELECT MAX(trade_date) FROM tu_dc_member")).scalar()
                self.latest_dates['DC'] = dc_date or '20250717'
                
                # 开盘啦最新日期
                kpl_date = conn.execute(text("SELECT MAX(trade_date) FROM tu_kpl_concept_cons")).scalar()
                self.latest_dates['KPL'] = kpl_date or '20250716'
                
                # 使用最新的日期作为默认
                self.latest_trading_day = max(self.latest_dates.values())
        except Exception as e:
            logger.error(f"获取最新交易日失败: {e}")
            # 备用：使用今天的日期
            from datetime import datetime
            self.latest_trading_day = datetime.now().strftime('%Y%m%d')
            self.latest_dates = {
                'THS': self.latest_trading_day,
                'DC': self.latest_trading_day,
                'KPL': self.latest_trading_day
            }
        
        logger.info(f"各数据源最新交易日: {self.latest_dates}")
        
        # 缓存
        self._concept_cache = {}  # 概念列表缓存
        self._member_cache = {}   # 成分股缓存
        
    def get_concept_stocks(self, concepts: List[str], show_progress: bool = True) -> List[Dict[str, Any]]:
        """
        获取概念相关股票 - 优化版
        
        Args:
            concepts: 概念名称列表
            show_progress: 是否显示进度条
            
        Returns:
            股票列表
        """
        all_stocks = {}  # ts_code -> stock_info
        
        # 使用进度条
        if show_progress:
            pbar = tqdm(total=len(concepts) * 3, desc="获取概念股数据")
        
        # 并发获取三个数据源的数据
        with ThreadPoolExecutor(max_workers=self.MAX_WORKERS) as executor:
            futures = []
            
            # 提交任务
            for concept in concepts:
                futures.append(executor.submit(self._get_ths_concept_stocks_optimized, [concept]))
                futures.append(executor.submit(self._get_dc_concept_stocks_optimized, [concept]))
                futures.append(executor.submit(self._get_kpl_concept_stocks_optimized, [concept]))
            
            # 收集结果
            for future in as_completed(futures):
                try:
                    source_name, source_stocks = future.result()
                    
                    # 合并数据
                    for stock in source_stocks:
                        ts_code = stock['ts_code']
                        
                        if ts_code not in all_stocks:
                            all_stocks[ts_code] = {
                                "ts_code": ts_code,
                                "name": stock['name'],
                                "concepts": set(),
                                "data_source": set(),
                                "first_limit_date": None,
                                "financial_report_mention": False,
                                "interaction_mention": False,
                                "announcement_mention": False,
                                "sector_rank_pct": 0.5
                            }
                        
                        # 添加概念和数据源
                        if 'concept' in stock:
                            all_stocks[ts_code]['concepts'].add(stock['concept'])
                        all_stocks[ts_code]['data_source'].add(source_name)
                        
                        # 更新涨停日期
                        if stock.get('first_limit_date'):
                            current_date = all_stocks[ts_code]['first_limit_date']
                            new_date = stock['first_limit_date']
                            if not current_date or new_date > current_date:
                                all_stocks[ts_code]['first_limit_date'] = new_date
                    
                    if show_progress:
                        pbar.update(1)
                        
                except Exception as e:
                    logger.error(f"获取数据失败: {e}")
                    if show_progress:
                        pbar.update(1)
        
        if show_progress:
            pbar.close()
        
        # 转换格式
        result = []
        for stock_info in all_stocks.values():
            stock_info['concepts'] = list(stock_info['concepts'])
            stock_info['data_source'] = list(stock_info['data_source'])
            result.append(stock_info)
        
        logger.info(f"共找到 {len(result)} 只概念相关股票")
        return result
    
    def _get_ths_concept_stocks_optimized(self, concepts: List[str]) -> tuple:
        """从同花顺获取概念股 - 优化版"""
        stocks = []
        
        try:
            # 1. 获取匹配的概念（限制数量）
            concept_query = text("""
                SELECT DISTINCT ts_code, name
                FROM tu_ths_index
                WHERE type = 'N'  -- 概念类型
                AND (:concept_filter)
                LIMIT :limit
            """)
            
            # 构建概念过滤条件
            concept_conditions = []
            params = {'limit': 10}  # 限制概念数量
            for i, concept in enumerate(concepts):
                param_name = f"concept_{i}"
                concept_conditions.append(f"name LIKE :{param_name}")
                params[param_name] = f"%{concept}%"
            
            query_str = str(concept_query).replace(
                ":concept_filter", 
                " OR ".join(concept_conditions) if concept_conditions else "1=1"
            )
            
            matched_concepts = pd.read_sql(text(query_str), self.db.engine, params=params)
            
            if matched_concepts.empty:
                logger.info(f"同花顺未找到匹配概念: {concepts}")
                return ("THS", stocks)
            
            # 2. 获取成分股（限制每个概念的股票数量）
            for _, concept_row in matched_concepts.iterrows():
                concept_code = concept_row['ts_code']
                concept_name = concept_row['name']
                
                member_query = text("""
                    SELECT DISTINCT 
                        m.con_code as ts_code,
                        m.con_name as name
                    FROM tu_ths_member m
                    WHERE m.ts_code = :concept_code
                    LIMIT :limit
                """)
                
                members = pd.read_sql(
                    member_query, 
                    self.db.engine, 
                    params={'concept_code': concept_code, 'limit': self.MAX_STOCKS_PER_CONCEPT}
                )
                
                for _, member in members.iterrows():
                    stocks.append({
                        'ts_code': member['ts_code'],
                        'name': member['name'],
                        'concept': concept_name,
                        'concept_code': concept_code
                    })
            
            logger.info(f"同花顺找到 {len(stocks)} 只股票")
            
        except Exception as e:
            logger.error(f"获取同花顺概念股失败: {str(e)}")
        
        return ("THS", stocks)
    
    def _get_dc_concept_stocks_optimized(self, concepts: List[str]) -> tuple:
        """从东财获取概念股 - 优化版"""
        stocks = []
        
        try:
            # 1. 获取匹配的概念（限制数量）
            concept_query = text("""
                SELECT DISTINCT 
                    ts_code,
                    name,
                    leading_code,
                    `leading`
                FROM tu_dc_index
                WHERE trade_date = :latest_date
                AND (:concept_filter)
                LIMIT :limit
            """)
            
            # 构建概念过滤条件
            concept_conditions = []
            params = {'latest_date': self.latest_dates['DC'], 'limit': 10}
            for i, concept in enumerate(concepts):
                param_name = f"concept_{i}"
                concept_conditions.append(f"name LIKE :{param_name}")
                params[param_name] = f"%{concept}%"
            
            query_str = str(concept_query).replace(
                ":concept_filter", 
                " OR ".join(concept_conditions) if concept_conditions else "1=1"
            )
            
            matched_concepts = pd.read_sql(text(query_str), self.db.engine, params=params)
            
            if matched_concepts.empty:
                logger.info(f"东财未找到匹配概念: {concepts}")
                return ("DC", stocks)
            
            # 2. 获取成分股（限制数量）
            for _, concept_row in matched_concepts.iterrows():
                # 先添加领涨股
                if concept_row['leading_code'] and concept_row['leading']:
                    stocks.append({
                        'ts_code': concept_row['leading_code'],
                        'name': concept_row['leading'],
                        'concept': concept_row['name'],
                        'is_leading': True
                    })
                
                # 查询该板块的成分股
                member_query = text("""
                    SELECT DISTINCT 
                        con_code as ts_code,
                        name
                    FROM tu_dc_member
                    WHERE trade_date = :trade_date
                    AND ts_code = :concept_code
                    LIMIT :limit
                """)
                
                member_params = {
                    'trade_date': self.latest_dates['DC'],
                    'concept_code': concept_row['ts_code'],
                    'limit': self.MAX_STOCKS_PER_CONCEPT
                }
                
                members = pd.read_sql(member_query, self.db.engine, params=member_params)
                
                # 添加成分股
                for _, member in members.iterrows():
                    stocks.append({
                        'ts_code': member['ts_code'],
                        'name': member['name'],
                        'concept': concept_row['name']
                    })
            
            logger.info(f"东财找到 {len(stocks)} 只股票")
            
        except Exception as e:
            logger.error(f"获取东财概念股失败: {str(e)}")
        
        return ("DC", stocks)
    
    def _get_kpl_concept_stocks_optimized(self, concepts: List[str]) -> tuple:
        """从开盘啦获取概念股 - 优化版"""
        stocks = []
        
        try:
            # 直接从成分股表查询（限制数量）
            cons_query = text("""
                SELECT DISTINCT
                    c.ts_code as concept_code,
                    c.name as concept_name,
                    c.con_code as ts_code,
                    c.con_name as name
                FROM (
                    SELECT DISTINCT name, ts_code
                    FROM tu_kpl_concept_cons
                    WHERE trade_date = :latest_date
                    AND (:concept_filter)
                    LIMIT 10
                ) concept_list
                JOIN tu_kpl_concept_cons c ON c.name = concept_list.name 
                    AND c.ts_code = concept_list.ts_code
                    AND c.trade_date = :latest_date
                LIMIT :total_limit
            """)
            
            # 构建概念过滤条件
            concept_conditions = []
            params = {
                'latest_date': self.latest_dates['KPL'],
                'total_limit': self.MAX_STOCKS_PER_CONCEPT * len(concepts)
            }
            for i, concept in enumerate(concepts):
                param_name = f"concept_{i}"
                concept_conditions.append(f"name LIKE :{param_name}")
                params[param_name] = f"%{concept}%"
            
            query_str = str(cons_query).replace(
                ":concept_filter", 
                " OR ".join(concept_conditions) if concept_conditions else "1=1"
            )
            
            concept_stocks = pd.read_sql(text(query_str), self.db.engine, params=params)
            
            if not concept_stocks.empty:
                # 获取所有成分股
                for _, row in concept_stocks.iterrows():
                    stocks.append({
                        'ts_code': row['ts_code'],
                        'name': row['name'],
                        'concept': row['concept_name']
                    })
                
                logger.info(f"开盘啦找到 {len(stocks)} 只股票")
            else:
                logger.info(f"开盘啦未找到匹配概念: {concepts}")
            
        except Exception as e:
            logger.error(f"获取开盘啦概念股失败: {str(e)}")
        
        return ("KPL", stocks)
    
    def get_technical_indicators_batch(
        self, 
        stock_codes: List[str],
        days: int = 21,
        batch_size: int = None
    ) -> Dict[str, Dict[str, Any]]:
        """
        批量获取技术指标数据
        
        Args:
            stock_codes: 股票代码列表
            days: 获取最近N天的数据
            batch_size: 批次大小
            
        Returns:
            技术指标数据
        """
        if batch_size is None:
            batch_size = self.BATCH_SIZE
            
        result = {}
        
        if not stock_codes:
            return result
        
        try:
            # 分批处理
            total_batches = (len(stock_codes) + batch_size - 1) // batch_size
            
            with tqdm(total=len(stock_codes), desc="获取技术指标") as pbar:
                for i in range(0, len(stock_codes), batch_size):
                    batch = stock_codes[i:i + batch_size]
                    
                    # 这里应该调用实际的技术指标API
                    # 暂时使用模拟数据
                    for ts_code in batch:
                        result[ts_code] = {
                            "latest_macd": 0.1,
                            "latest_dif": 0.15,
                            "latest_dea": 0.05,
                            "ma5": 10.5,
                            "ma10": 10.3,
                            "ma20": 10.1,
                            "macd_above_water_date": None,
                            "ma_golden_cross_date": None
                        }
                    
                    pbar.update(len(batch))
            
            logger.info(f"获取了 {len(result)} 只股票的技术指标")
            
        except Exception as e:
            logger.error(f"获取技术指标失败: {str(e)}")
        
        return result
    
    def get_money_flow_data_batch(
        self,
        stock_codes: List[str],
        days: int = 5,
        batch_size: int = None
    ) -> Dict[str, Dict[str, Any]]:
        """
        批量获取资金流向数据
        
        Args:
            stock_codes: 股票代码列表
            days: 获取最近N天的数据
            batch_size: 批次大小
            
        Returns:
            资金流向数据
        """
        if batch_size is None:
            batch_size = self.BATCH_SIZE
            
        result = {}
        
        if not stock_codes:
            return result
        
        try:
            # 计算日期范围
            from datetime import datetime, timedelta
            end_date = datetime.strptime(self.latest_trading_day, '%Y%m%d')
            start_date = (end_date - timedelta(days=int(days * 1.5))).strftime('%Y%m%d')
            
            # 分批查询
            with tqdm(total=len(stock_codes), desc="获取资金流向") as pbar:
                for i in range(0, len(stock_codes), batch_size):
                    batch = stock_codes[i:i + batch_size]
                    
                    # 批量查询资金流
                    flow_query = text("""
                        SELECT 
                            ts_code,
                            trade_date,
                            net_mf_amount,
                            net_elg_amount,
                            net_lg_amount
                        FROM tu_stk_moneyflow_em
                        WHERE ts_code IN :stock_codes
                        AND trade_date >= :start_date
                        ORDER BY ts_code, trade_date DESC
                    """)
                    
                    flow_data = pd.read_sql(
                        flow_query,
                        self.db.engine,
                        params={
                            'stock_codes': tuple(batch),
                            'start_date': start_date
                        }
                    )
                    
                    if not flow_data.empty:
                        # 按股票分组计算
                        for ts_code in batch:
                            stock_flows = flow_data[flow_data['ts_code'] == ts_code]
                            
                            if not stock_flows.empty:
                                # 最新一天数据
                                latest = stock_flows.iloc[0]
                                
                                # 本周数据
                                weekly_sum = stock_flows['net_mf_amount'].sum()
                                
                                # 连续流入天数
                                continuous_days = 0
                                for _, row in stock_flows.iterrows():
                                    if row['net_mf_amount'] > 0:
                                        continuous_days += 1
                                    else:
                                        break
                                
                                result[ts_code] = {
                                    "daily_net_inflow": float(latest['net_mf_amount']),
                                    "weekly_net_inflow": float(weekly_sum),
                                    "continuous_inflow_days": continuous_days,
                                    "net_inflow_rank": 0,
                                    "net_inflow_pct": 0
                                }
                    
                    pbar.update(len(batch))
            
            # 计算排名
            if result:
                sorted_codes = sorted(
                    result.keys(), 
                    key=lambda x: result[x]['daily_net_inflow'],
                    reverse=True
                )
                
                for rank, ts_code in enumerate(sorted_codes, 1):
                    result[ts_code]['net_inflow_rank'] = rank
                    result[ts_code]['net_inflow_pct'] = (len(sorted_codes) - rank + 1) / len(sorted_codes)
            
            logger.info(f"获取了 {len(result)} 只股票的资金流向数据")
            
        except Exception as e:
            logger.error(f"获取资金流向数据失败: {str(e)}")
        
        return result
    
    def __del__(self):
        """清理资源"""
        if hasattr(self, 'db'):
            self.db.close()


# 测试
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    collector = ConceptDataCollectorOptimized()
    
    # 测试获取概念股
    concepts = ["储能", "固态电池"]
    stocks = collector.get_concept_stocks(concepts, show_progress=True)
    
    print(f"\n找到 {len(stocks)} 只相关股票:")
    for stock in stocks[:5]:
        print(f"  {stock['name']}({stock['ts_code']}) - 概念: {stock['concepts']}")
    
    # 测试批量获取技术指标
    if stocks:
        stock_codes = [s['ts_code'] for s in stocks[:20]]
        tech_data = collector.get_technical_indicators_batch(stock_codes)
        print(f"\n技术指标数据: {len(tech_data)} 只股票")
    
    # 测试批量获取资金流向
    if stocks:
        money_data = collector.get_money_flow_data_batch(stock_codes)
        print(f"\n资金流向数据: {len(money_data)} 只股票")