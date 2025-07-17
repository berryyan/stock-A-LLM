#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
概念数据采集器
负责从多个数据源采集概念股相关数据
"""

import logging
from typing import List, Dict, Any, Optional, Set
from datetime import datetime, timedelta
import pandas as pd
from sqlalchemy import text
import json

from database.mysql_connector import MySQLConnector
from utils.date_intelligence import DateIntelligenceModule as DateIntelligence

logger = logging.getLogger(__name__)


class ConceptDataCollector:
    """概念数据采集器"""
    
    def __init__(self):
        """初始化"""
        self.db = MySQLConnector()
        self.date_intelligence = DateIntelligence()
        
        # 获取最新交易日
        try:
            # 直接查询数据库
            from sqlalchemy import text
            query = text("SELECT MAX(trade_date) FROM tu_trade_cal WHERE is_open = 1")
            with self.db.engine.connect() as conn:
                result = conn.execute(query).scalar()
            self.latest_trading_day = result
        except:
            # 备用：使用今天的日期
            from datetime import datetime
            self.latest_trading_day = datetime.now().strftime('%Y%m%d')
        logger.info(f"最新交易日: {self.latest_trading_day}")
        
        # 缓存
        self._concept_cache = {}  # 概念列表缓存
        self._member_cache = {}   # 成分股缓存
        
    def get_concept_stocks(self, concepts: List[str]) -> List[Dict[str, Any]]:
        """
        获取概念相关股票
        
        Args:
            concepts: 概念名称列表
            
        Returns:
            股票列表，每个元素包含:
            {
                "ts_code": "000001.SZ",
                "name": "平安银行",
                "concepts": ["金融科技", "银行"],
                "data_source": ["THS", "DC"],
                "first_limit_date": "2025-07-10"  # 最近涨停日期
            }
        """
        all_stocks = {}  # ts_code -> stock_info
        
        # 1. 从三个数据源获取概念和成分股
        ths_stocks = self._get_ths_concept_stocks(concepts)
        dc_stocks = self._get_dc_concept_stocks(concepts)
        kpl_stocks = self._get_kpl_concept_stocks(concepts)
        
        # 2. 合并数据
        for source_name, source_stocks in [
            ("THS", ths_stocks),
            ("DC", dc_stocks),
            ("KPL", kpl_stocks)
        ]:
            for stock in source_stocks:
                ts_code = stock['ts_code']
                
                if ts_code not in all_stocks:
                    all_stocks[ts_code] = {
                        "ts_code": ts_code,
                        "name": stock['name'],
                        "concepts": set(),
                        "data_source": set(),
                        "first_limit_date": None,
                        "financial_report_mention": False,  # TODO: 从财报数据获取
                        "interaction_mention": False,        # TODO: 从互动平台数据获取
                        "announcement_mention": False,       # TODO: 从公告数据获取
                        "sector_rank_pct": 0.5              # TODO: 计算板块排名百分位
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
        
        # 3. 转换格式
        result = []
        for stock_info in all_stocks.values():
            stock_info['concepts'] = list(stock_info['concepts'])
            stock_info['data_source'] = list(stock_info['data_source'])
            result.append(stock_info)
        
        logger.info(f"共找到 {len(result)} 只概念相关股票")
        return result
    
    def _get_ths_concept_stocks(self, concepts: List[str]) -> List[Dict]:
        """从同花顺获取概念股"""
        stocks = []
        
        try:
            # 1. 获取匹配的概念
            concept_query = text("""
                SELECT DISTINCT ts_code, name
                FROM tu_ths_index
                WHERE type = 'N'  -- 概念类型
                AND (:concept_filter)
            """)
            
            # 构建概念过滤条件
            concept_conditions = []
            params = {}
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
                return stocks
            
            # 2. 获取成分股
            for _, concept_row in matched_concepts.iterrows():
                concept_code = concept_row['ts_code']
                concept_name = concept_row['name']
                
                member_query = text("""
                    SELECT DISTINCT 
                        m.con_code as ts_code,
                        m.con_name as name
                    FROM tu_ths_member m
                    WHERE m.ts_code = :concept_code
                """)
                
                members = pd.read_sql(
                    member_query, 
                    self.db.engine, 
                    params={'concept_code': concept_code}
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
        
        return stocks
    
    def _get_dc_concept_stocks(self, concepts: List[str]) -> List[Dict]:
        """从东财获取概念股"""
        stocks = []
        
        try:
            # 1. 获取匹配的概念
            concept_query = text("""
                SELECT DISTINCT 
                    ts_code,
                    name,
                    leading_code,
                    leading
                FROM tu_dc_index
                WHERE trade_date = :latest_date
                AND (:concept_filter)
            """)
            
            # 构建概念过滤条件
            concept_conditions = []
            params = {'latest_date': self.latest_trading_day}
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
                return stocks
            
            # 2. 东财目前没有成分股表，只能获取领涨股
            for _, concept_row in matched_concepts.iterrows():
                if concept_row['leading_code'] and concept_row['leading']:
                    stocks.append({
                        'ts_code': concept_row['leading_code'],
                        'name': concept_row['leading'],
                        'concept': concept_row['name'],
                        'is_leading': True  # 标记为领涨股
                    })
            
            # TODO: 等待DC成分股表补充后，这里需要更新查询逻辑
            logger.info(f"东财找到 {len(stocks)} 只领涨股（成分股表待补充）")
            
        except Exception as e:
            logger.error(f"获取东财概念股失败: {str(e)}")
        
        return stocks
    
    def _get_kpl_concept_stocks(self, concepts: List[str]) -> List[Dict]:
        """从开盘啦获取概念股"""
        stocks = []
        
        try:
            # 1. 通过theme字段查找相关股票
            theme_query = text("""
                SELECT DISTINCT
                    ts_code,
                    name,
                    theme
                FROM tu_kpl_list
                WHERE trade_date = :latest_date
                AND (:theme_filter)
            """)
            
            # 构建主题过滤条件
            theme_conditions = []
            params = {'latest_date': self.latest_trading_day}
            for i, concept in enumerate(concepts):
                param_name = f"theme_{i}"
                theme_conditions.append(f"theme LIKE :{param_name}")
                params[param_name] = f"%{concept}%"
            
            query_str = str(theme_query).replace(
                ":theme_filter", 
                " OR ".join(theme_conditions) if theme_conditions else "1=1"
            )
            
            theme_stocks = pd.read_sql(text(query_str), self.db.engine, params=params)
            
            if not theme_stocks.empty:
                for _, stock_row in theme_stocks.iterrows():
                    # 解析theme字段中的概念
                    themes = stock_row['theme'].split('、') if stock_row['theme'] else []
                    
                    # 找出匹配的概念
                    for theme in themes:
                        for concept in concepts:
                            if concept in theme:
                                stocks.append({
                                    'ts_code': stock_row['ts_code'],
                                    'name': stock_row['name'],
                                    'concept': theme
                                })
                                break
            
            # 2. 获取涨停信息
            limit_query = text("""
                SELECT DISTINCT
                    name as concept_name,
                    z_t_num
                FROM tu_kpl_concept
                WHERE trade_date = :latest_date
                AND (:concept_filter)
            """)
            
            # 复用概念过滤条件
            concept_conditions = []
            for i, concept in enumerate(concepts):
                param_name = f"concept_{i}"
                concept_conditions.append(f"name LIKE :{param_name}")
            
            query_str = str(limit_query).replace(
                ":concept_filter", 
                " OR ".join(concept_conditions) if concept_conditions else "1=1"
            )
            
            limit_info = pd.read_sql(text(query_str), self.db.engine, params=params)
            
            # TODO: 等待KPL题材成分表补充后，这里需要更新查询逻辑
            logger.info(f"开盘啦找到 {len(stocks)} 只股票（题材成分表待补充）")
            
        except Exception as e:
            logger.error(f"获取开盘啦概念股失败: {str(e)}")
        
        return stocks
    
    def get_technical_indicators(
        self, 
        stock_codes: List[str],
        days: int = 21
    ) -> Dict[str, Dict[str, Any]]:
        """
        获取技术指标数据
        
        Args:
            stock_codes: 股票代码列表
            days: 获取最近N天的数据
            
        Returns:
            {
                "000001.SZ": {
                    "latest_macd": 0.15,
                    "latest_dif": 0.20,
                    "latest_dea": 0.05,
                    "ma5": 12.5,
                    "ma10": 12.3,
                    "ma20": 12.1,
                    "macd_above_water_date": "2025-07-10",  # MACD上穿0轴日期
                    "ma_golden_cross_date": "2025-07-08"    # 均线金叉日期
                }
            }
        """
        result = {}
        
        if not stock_codes:
            return result
        
        try:
            # 计算起始日期
            # 简单计算：天数 * 1.5 （考虑周末）
            from datetime import datetime, timedelta
            end_date = datetime.strptime(self.latest_trading_day, '%Y%m%d')
            start_date = (end_date - timedelta(days=int(days * 1.5))).strftime('%Y%m%d')
            
            # 批量查询（使用 tu_pro_bar 或类似的技术指标表）
            # 注意：这里假设已经有技术指标数据表，实际可能需要调用Tushare API
            
            # 暂时使用模拟数据
            # TODO: 集成实际的技术指标数据源
            for ts_code in stock_codes:
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
            
            logger.info(f"获取了 {len(result)} 只股票的技术指标")
            
        except Exception as e:
            logger.error(f"获取技术指标失败: {str(e)}")
        
        return result
    
    def get_money_flow_data(
        self,
        stock_codes: List[str],
        days: int = 5
    ) -> Dict[str, Dict[str, Any]]:
        """
        获取资金流向数据
        
        Args:
            stock_codes: 股票代码列表
            days: 获取最近N天的数据
            
        Returns:
            {
                "000001.SZ": {
                    "daily_net_inflow": 1000000,      # 今日净流入
                    "weekly_net_inflow": 5000000,     # 本周净流入
                    "continuous_inflow_days": 3,       # 连续流入天数
                    "net_inflow_rank": 5,              # 净流入排名
                    "net_inflow_pct": 0.15            # 净流入占比
                }
            }
        """
        result = {}
        
        if not stock_codes:
            return result
        
        try:
            # 获取最近N天的资金流数据
            # 简单计算：天数 * 1.5 （考虑周末）
            from datetime import datetime, timedelta
            end_date = datetime.strptime(self.latest_trading_day, '%Y%m%d')
            start_date = (end_date - timedelta(days=int(days * 1.5))).strftime('%Y%m%d')
            
            # 批量查询资金流
            flow_query = text("""
                SELECT 
                    ts_code,
                    trade_date,
                    net_mf_amount,      -- 主力净流入
                    net_elg_amount,     -- 超大单净流入
                    net_lg_amount       -- 大单净流入
                FROM tu_money_flow
                WHERE ts_code IN :stock_codes
                AND trade_date >= :start_date
                ORDER BY ts_code, trade_date DESC
            """)
            
            flow_data = pd.read_sql(
                flow_query,
                self.db.engine,
                params={
                    'stock_codes': tuple(stock_codes),
                    'start_date': start_date
                }
            )
            
            if not flow_data.empty:
                # 按股票分组计算
                for ts_code in stock_codes:
                    stock_flows = flow_data[flow_data['ts_code'] == ts_code]
                    
                    if not stock_flows.empty:
                        # 最新一天数据
                        latest = stock_flows.iloc[0]
                        
                        # 本周数据（最近5天）
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
                            "net_inflow_rank": 0,  # 需要后续计算
                            "net_inflow_pct": 0    # 需要后续计算
                        }
            
            # 计算排名
            if result:
                # 按日净流入排序
                sorted_codes = sorted(
                    result.keys(), 
                    key=lambda x: result[x]['daily_net_inflow'],
                    reverse=True
                )
                
                for rank, ts_code in enumerate(sorted_codes, 1):
                    result[ts_code]['net_inflow_rank'] = rank
                    # 计算百分位
                    result[ts_code]['net_inflow_pct'] = (len(sorted_codes) - rank + 1) / len(sorted_codes)
            
            logger.info(f"获取了 {len(result)} 只股票的资金流向数据")
            
        except Exception as e:
            logger.error(f"获取资金流向数据失败: {str(e)}")
        
        return result
    
    def get_limit_up_info(
        self,
        concept_codes: List[str],
        days: int = 5
    ) -> Dict[str, List[Dict]]:
        """
        获取概念板块涨停信息
        
        Returns:
            {
                "concept_code": [
                    {
                        "ts_code": "000001.SZ",
                        "name": "平安银行",
                        "limit_date": "2025-07-10",
                        "limit_order": 1  # 板块内涨停顺序
                    }
                ]
            }
        """
        # TODO: 实现涨停数据查询
        return {}
    
    def get_financial_mentions(
        self,
        stock_codes: List[str]
    ) -> Dict[str, Dict[str, bool]]:
        """
        获取财报、公告、互动平台提及情况
        
        Returns:
            {
                "000001.SZ": {
                    "financial_report": True,
                    "announcement": False,
                    "interaction": True
                }
            }
        """
        # TODO: 实现文本提及检索
        return {}
    
    def __del__(self):
        """清理资源"""
        if hasattr(self, 'db'):
            self.db.close()


# 测试
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    collector = ConceptDataCollector()
    
    # 测试获取概念股
    concepts = ["固态电池", "锂电池"]
    stocks = collector.get_concept_stocks(concepts)
    
    print(f"\n找到 {len(stocks)} 只相关股票:")
    for stock in stocks[:5]:
        print(f"  {stock['name']}({stock['ts_code']}) - 概念: {stock['concepts']}")
    
    # 测试获取技术指标
    if stocks:
        stock_codes = [s['ts_code'] for s in stocks[:5]]
        tech_data = collector.get_technical_indicators(stock_codes)
        print(f"\n技术指标数据:")
        for ts_code, data in tech_data.items():
            print(f"  {ts_code}: MACD={data['latest_macd']}, MA5={data['ma5']}")
    
    # 测试获取资金流向
    if stocks:
        money_data = collector.get_money_flow_data(stock_codes)
        print(f"\n资金流向数据:")
        for ts_code, data in money_data.items():
            print(f"  {ts_code}: 日流入={data['daily_net_inflow']/10000:.2f}万")