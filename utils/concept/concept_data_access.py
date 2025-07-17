#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
概念数据访问层
提供对三大数据源（同花顺、东财、开盘啦）的统一访问接口
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import logging
from typing import List, Dict, Optional, Set, Any
from datetime import datetime
from database.mysql_connector import MySQLConnector
from sqlalchemy import text
import pandas as pd

logger = logging.getLogger(__name__)


class ConceptDataAccess:
    """概念数据访问层"""
    
    def __init__(self):
        """初始化"""
        self.db = MySQLConnector()
        self._concept_cache = {}  # 概念缓存
        self._member_cache = {}   # 成分股缓存
        
        # 获取各数据源的最新日期
        self._source_latest_dates = self._get_source_latest_dates()
        
        logger.info("ConceptDataAccess初始化完成")
    
    def get_all_concepts(self, source: str = 'all') -> List[Dict[str, str]]:
        """
        获取所有概念列表
        
        Args:
            source: 数据源，可选 'ths'(同花顺), 'dc'(东财), 'kpl'(开盘啦), 'all'(全部)
            
        Returns:
            概念列表 [{"ts_code": "xxx", "name": "xxx", "source": "xxx"}, ...]
        """
        cache_key = f"concepts_{source}"
        if cache_key in self._concept_cache:
            return self._concept_cache[cache_key]
        
        concepts = []
        
        try:
            if source in ['ths', 'all']:
                # 同花顺概念
                ths_query = text("""
                    SELECT DISTINCT 
                        ts_code,
                        name,
                        'ths' as source
                    FROM tu_ths_index
                    WHERE exchange = 'A'
                    ORDER BY ts_code
                """)
                ths_result = pd.read_sql(ths_query, self.db.engine)
                concepts.extend(ths_result.to_dict('records'))
                logger.info(f"获取同花顺概念 {len(ths_result)} 个")
            
            if source in ['dc', 'all']:
                # 东财板块
                dc_query = text("""
                    SELECT DISTINCT 
                        ts_code,
                        name,
                        'dc' as source
                    FROM tu_dc_index
                    ORDER BY ts_code
                """)
                dc_result = pd.read_sql(dc_query, self.db.engine)
                concepts.extend(dc_result.to_dict('records'))
                logger.info(f"获取东财板块 {len(dc_result)} 个")
            
            if source in ['kpl', 'all']:
                # 开盘啦题材
                kpl_query = text("""
                    SELECT DISTINCT 
                        ts_code,
                        name,
                        'kpl' as source
                    FROM tu_kpl_concept
                    ORDER BY ts_code
                """)
                kpl_result = pd.read_sql(kpl_query, self.db.engine)
                concepts.extend(kpl_result.to_dict('records'))
                logger.info(f"获取开盘啦题材 {len(kpl_result)} 个")
            
            # 缓存结果
            self._concept_cache[cache_key] = concepts
            
            return concepts
            
        except Exception as e:
            logger.error(f"获取概念列表失败: {str(e)}")
            return []
    
    def get_concept_members(
        self, 
        concept_code: str, 
        date: Optional[str] = None
    ) -> List[Dict[str, str]]:
        """
        获取概念成分股
        
        Args:
            concept_code: 概念代码，如 "881157.TI"
            date: 日期，格式 YYYYMMDD，默认最新
            
        Returns:
            成分股列表 [{"ts_code": "xxx", "name": "xxx"}, ...]
        """
        # 确定数据源
        if concept_code.endswith('.TI'):
            source = 'ths'
        elif concept_code.endswith('.DC'):
            source = 'dc'
        elif concept_code.endswith('.KP'):
            source = 'kpl'
        else:
            logger.error(f"未知的概念代码格式: {concept_code}")
            return []
        
        cache_key = f"members_{concept_code}_{date or 'latest'}"
        if cache_key in self._member_cache:
            return self._member_cache[cache_key]
        
        members = []
        
        try:
            if source == 'ths':
                # 同花顺成分股（静态数据，不需要日期）
                query = text("""
                    SELECT DISTINCT
                        con_code as ts_code,
                        con_name as name
                    FROM tu_ths_member
                    WHERE ts_code = :concept_code
                    ORDER BY con_code
                """)
                result = pd.read_sql(query, self.db.engine, params={'concept_code': concept_code})
                
            elif source == 'dc':
                # 东财成分股
                if date:
                    query = text("""
                        SELECT DISTINCT
                            con_code as ts_code,
                            name
                        FROM tu_dc_member
                        WHERE ts_code = :concept_code
                        AND trade_date = :date
                        ORDER BY con_code
                    """)
                    result = pd.read_sql(query, self.db.engine, params={
                        'concept_code': concept_code,
                        'date': date
                    })
                else:
                    # 获取最新日期的数据
                    query = text("""
                        SELECT DISTINCT
                            con_code as ts_code,
                            name
                        FROM tu_dc_member
                        WHERE ts_code = :concept_code
                        AND trade_date = (
                            SELECT MAX(trade_date) 
                            FROM tu_dc_member 
                            WHERE ts_code = :concept_code
                        )
                        ORDER BY con_code
                    """)
                    result = pd.read_sql(query, self.db.engine, params={'concept_code': concept_code})
                    
            else:  # kpl
                # 开盘啦成分股
                if date:
                    query = text("""
                        SELECT DISTINCT
                            con_code as ts_code,
                            con_name as name
                        FROM tu_kpl_concept_cons
                        WHERE ts_code = :concept_code
                        AND trade_date = :date
                        ORDER BY con_code
                    """)
                    result = pd.read_sql(query, self.db.engine, params={
                        'concept_code': concept_code,
                        'date': date
                    })
                else:
                    # 获取最新日期的数据
                    query = text("""
                        SELECT DISTINCT
                            con_code as ts_code,
                            con_name as name
                        FROM tu_kpl_concept_cons
                        WHERE ts_code = :concept_code
                        AND trade_date = (
                            SELECT MAX(trade_date) 
                            FROM tu_kpl_concept_cons 
                            WHERE ts_code = :concept_code
                        )
                        ORDER BY con_code
                    """)
                    result = pd.read_sql(query, self.db.engine, params={'concept_code': concept_code})
            
            members = result.to_dict('records')
            logger.info(f"获取概念 {concept_code} 成分股 {len(members)} 只")
            
            # 缓存结果
            self._member_cache[cache_key] = members
            
            return members
            
        except Exception as e:
            logger.error(f"获取概念成分股失败: {str(e)}")
            return []
    
    def search_concepts(self, keyword: str, source: str = 'all') -> List[Dict[str, str]]:
        """
        搜索概念
        
        Args:
            keyword: 搜索关键词
            source: 数据源
            
        Returns:
            匹配的概念列表
        """
        all_concepts = self.get_all_concepts(source)
        
        matched = []
        keyword_lower = keyword.lower()
        
        for concept in all_concepts:
            name = concept['name']
            name_lower = name.lower()
            
            # 包含匹配
            if keyword in name or keyword_lower in name_lower:
                matched.append(concept)
                continue
            
            # 去掉"概念"后匹配
            if name.endswith('概念'):
                name_clean = name[:-2]
                if keyword in name_clean or keyword_lower in name_clean.lower():
                    matched.append(concept)
        
        logger.info(f"搜索 '{keyword}' 找到 {len(matched)} 个概念")
        return matched
    
    def get_stock_concepts(self, ts_code: str) -> List[Dict[str, str]]:
        """
        获取股票所属的所有概念
        
        Args:
            ts_code: 股票代码，如 "600519.SH"
            
        Returns:
            概念列表
        """
        concepts = []
        
        try:
            # 查询同花顺
            ths_query = text("""
                SELECT DISTINCT
                    a.ts_code,
                    b.name,
                    'ths' as source
                FROM tu_ths_member a
                JOIN tu_ths_index b ON a.ts_code = b.ts_code
                WHERE a.con_code = :ts_code
            """)
            ths_result = pd.read_sql(ths_query, self.db.engine, params={'ts_code': ts_code})
            concepts.extend(ths_result.to_dict('records'))
            
            # 查询东财（最新日期）
            dc_query = text("""
                SELECT DISTINCT
                    a.ts_code,
                    b.name,
                    'dc' as source
                FROM tu_dc_member a
                JOIN tu_dc_index b ON a.ts_code = b.ts_code
                WHERE a.con_code = :ts_code
                AND a.trade_date = (SELECT MAX(trade_date) FROM tu_dc_member)
            """)
            dc_result = pd.read_sql(dc_query, self.db.engine, params={'ts_code': ts_code})
            concepts.extend(dc_result.to_dict('records'))
            
            # 查询开盘啦（最新日期）
            kpl_query = text("""
                SELECT DISTINCT
                    a.ts_code,
                    a.name,
                    'kpl' as source
                FROM tu_kpl_concept_cons a
                WHERE a.con_code = :ts_code
                AND a.trade_date = (SELECT MAX(trade_date) FROM tu_kpl_concept_cons)
            """)
            kpl_result = pd.read_sql(kpl_query, self.db.engine, params={'ts_code': ts_code})
            concepts.extend(kpl_result.to_dict('records'))
            
            logger.info(f"股票 {ts_code} 属于 {len(concepts)} 个概念")
            return concepts
            
        except Exception as e:
            logger.error(f"获取股票概念失败: {str(e)}")
            return []
    
    def get_concept_stats(self) -> Dict[str, int]:
        """
        获取概念统计信息
        
        Returns:
            统计信息字典
        """
        stats = {}
        
        try:
            # 统计各数据源概念数量
            for source in ['ths', 'dc', 'kpl']:
                concepts = self.get_all_concepts(source)
                stats[f'{source}_concepts'] = len(concepts)
            
            # 统计股票总数
            stock_query = text("""
                SELECT COUNT(DISTINCT ts_code) as count
                FROM (
                    SELECT con_code as ts_code FROM tu_ths_member
                    UNION
                    SELECT con_code as ts_code FROM tu_dc_member
                    UNION
                    SELECT con_code as ts_code FROM tu_kpl_concept_cons
                ) t
            """)
            result = pd.read_sql(stock_query, self.db.engine)
            stats['total_stocks'] = int(result['count'].iloc[0])
            
            return stats
            
        except Exception as e:
            logger.error(f"获取统计信息失败: {str(e)}")
            return {}
    
    def _get_source_latest_dates(self) -> Dict[str, Optional[str]]:
        """获取各数据源的最新日期"""
        latest_dates = {
            'ths': None,  # 同花顺是静态数据，不需要日期
            'dc': None,
            'kpl': None
        }
        
        try:
            # 东财最新日期
            dc_query = text("SELECT MAX(trade_date) as latest FROM tu_dc_member")
            dc_result = pd.read_sql(dc_query, self.db.engine)
            if not dc_result.empty and dc_result.iloc[0]['latest']:
                latest_dates['dc'] = dc_result.iloc[0]['latest']
                
            # 开盘啦最新日期
            kpl_query = text("SELECT MAX(trade_date) as latest FROM tu_kpl_concept_cons")
            kpl_result = pd.read_sql(kpl_query, self.db.engine)
            if not kpl_result.empty and kpl_result.iloc[0]['latest']:
                latest_dates['kpl'] = kpl_result.iloc[0]['latest']
                
            logger.info(f"各数据源最新日期: {latest_dates}")
            
        except Exception as e:
            logger.error(f"获取数据源最新日期失败: {str(e)}")
            
        return latest_dates
    
    def get_source_data_status(self, concept_code: str) -> Dict[str, Any]:
        """获取指定概念在各数据源的数据状态"""
        status = {
            'concept_code': concept_code,
            'data_status': {}
        }
        
        try:
            # 判断数据源
            if concept_code.endswith('.TI'):
                source = 'ths'
            elif concept_code.endswith('.DC'):
                source = 'dc'
            elif concept_code.endswith('.KP'):
                source = 'kpl'
            else:
                return status
                
            if source == 'ths':
                # 同花顺数据状态
                query = text("SELECT COUNT(*) as cnt FROM tu_ths_member WHERE ts_code = :code")
                result = pd.read_sql(query, self.db.engine, params={'code': concept_code})
                status['data_status']['ths'] = {
                    'has_data': result.iloc[0]['cnt'] > 0,
                    'record_count': result.iloc[0]['cnt'],
                    'latest_date': 'N/A (静态数据)'
                }
            
            elif source == 'dc':
                # 东财数据状态
                query = text("""
                    SELECT 
                        COUNT(*) as total_count,
                        COUNT(DISTINCT trade_date) as date_count,
                        MAX(trade_date) as latest_date
                    FROM tu_dc_member 
                    WHERE ts_code = :code
                """)
                result = pd.read_sql(query, self.db.engine, params={'code': concept_code})
                row = result.iloc[0]
                status['data_status']['dc'] = {
                    'has_data': row['total_count'] > 0,
                    'record_count': row['total_count'],
                    'date_count': row['date_count'],
                    'latest_date': row['latest_date'] or 'N/A'
                }
                
            elif source == 'kpl':
                # 开盘啦数据状态
                query = text("""
                    SELECT 
                        COUNT(*) as total_count,
                        COUNT(DISTINCT trade_date) as date_count,
                        MAX(trade_date) as latest_date
                    FROM tu_kpl_concept_cons 
                    WHERE ts_code = :code
                """)
                result = pd.read_sql(query, self.db.engine, params={'code': concept_code})
                row = result.iloc[0]
                status['data_status']['kpl'] = {
                    'has_data': row['total_count'] > 0,
                    'record_count': row['total_count'],
                    'date_count': row['date_count'],
                    'latest_date': row['latest_date'] or 'N/A'
                }
                
        except Exception as e:
            logger.error(f"获取概念数据状态失败: {str(e)}")
            
        return status
    
    def clear_cache(self):
        """清空缓存"""
        self._concept_cache.clear()
        self._member_cache.clear()
        logger.info("数据访问层缓存已清空")
    
    def close(self):
        """关闭连接"""
        self.db.close()


# 测试
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    data_access = ConceptDataAccess()
    
    # 1. 获取所有概念
    print("\n=== 获取所有概念 ===")
    all_concepts = data_access.get_all_concepts()
    print(f"总共 {len(all_concepts)} 个概念")
    
    # 显示各数据源统计
    stats = data_access.get_concept_stats()
    print("\n数据源统计:")
    for key, value in stats.items():
        print(f"  {key}: {value}")
    
    # 2. 搜索概念
    print("\n=== 搜索概念 ===")
    search_keywords = ["固态电池", "新能源", "人工智能"]
    for keyword in search_keywords:
        results = data_access.search_concepts(keyword)
        print(f"\n搜索 '{keyword}':")
        for r in results[:5]:  # 显示前5个
            print(f"  - {r['name']} ({r['ts_code']}) [{r['source']}]")
        if len(results) > 5:
            print(f"  ... 还有 {len(results)-5} 个")
    
    # 3. 获取概念成分股
    print("\n=== 获取概念成分股 ===")
    # 测试每种数据源
    test_concepts = [
        ("881157.TI", "同花顺-固态电池"),
        ("BK0968.DC", "东财-固态电池"),
        ("000169.KP", "开盘啦-固态电池")
    ]
    
    for concept_code, desc in test_concepts:
        print(f"\n{desc} ({concept_code}):")
        members = data_access.get_concept_members(concept_code)
        if members:
            for m in members[:5]:  # 显示前5个
                print(f"  - {m['name']} ({m['ts_code']})")
            if len(members) > 5:
                print(f"  ... 还有 {len(members)-5} 只")
        else:
            print("  未找到成分股")
    
    # 4. 获取股票所属概念
    print("\n=== 获取股票所属概念 ===")
    test_stocks = ["002074.SZ", "600110.SH"]  # 国轩高科、诺德股份
    for stock in test_stocks:
        print(f"\n{stock} 所属概念:")
        concepts = data_access.get_stock_concepts(stock)
        for c in concepts[:10]:  # 显示前10个
            print(f"  - {c['name']} ({c['ts_code']}) [{c['source']}]")
        if len(concepts) > 10:
            print(f"  ... 还有 {len(concepts)-10} 个")
    
    data_access.close()