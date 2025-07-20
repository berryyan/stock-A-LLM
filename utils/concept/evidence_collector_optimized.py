#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
优化版概念股证据收集器
集成缓存、并行执行和性能监控
"""

import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import re
import time

# 添加项目根目录到Python路径
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from database.mysql_connector import MySQLConnector
from agents.rag_agent_modular import RAGAgentModular
from utils.agent_response import AgentResponse
from utils.concept.performance_optimizer import (
    evidence_cache, 
    ParallelExecutor, 
    monitor_performance,
    performance_monitor,
    query_optimizer
)

logger = logging.getLogger(__name__)


class EvidenceCollectorOptimized:
    """优化版概念股证据收集器"""
    
    def __init__(self):
        """初始化证据收集器"""
        self.db = MySQLConnector()
        self.rag_agent = None  # 延迟初始化
        self.parallel_executor = ParallelExecutor(max_workers=4, timeout=10)
        
        # 缓存
        self._stock_name_cache = {}
        
        logger.info("优化版EvidenceCollector初始化完成")
    
    @monitor_performance("collect_evidence")
    def collect_evidence(self, ts_code: str, concepts: List[str], 
                        data_sources: List[str] = None) -> Dict[str, List[Dict]]:
        """
        收集所有维度的证据（带缓存和并行优化）
        
        Args:
            ts_code: 股票代码
            concepts: 概念列表
            data_sources: 数据源列表（用于软件收录证据）
            
        Returns:
            包含各维度证据的字典
        """
        start_time = time.time()
        
        # 尝试从缓存获取
        cached_evidence = evidence_cache.get(ts_code, concepts)
        if cached_evidence is not None:
            logger.info(f"从缓存获取证据: {ts_code}")
            performance_monitor.record('evidence_cache_hit', 1)
            return cached_evidence
        
        performance_monitor.record('evidence_cache_miss', 1)
        
        # 并行收集证据
        try:
            evidence = self._collect_evidence_parallel(ts_code, concepts, data_sources)
            
            # 缓存结果
            evidence_cache.set(ts_code, concepts, evidence)
            
            # 记录性能指标
            duration = time.time() - start_time
            performance_monitor.record('evidence_collection_time', duration)
            
            logger.info(f"收集到 {ts_code} 的证据：软件{len(evidence.get('software', []))}条，"
                       f"财报{len(evidence.get('report', []))}条，"
                       f"互动{len(evidence.get('interaction', []))}条，"
                       f"公告{len(evidence.get('announcement', []))}条，"
                       f"耗时{duration:.2f}秒")
            
            return evidence
            
        except Exception as e:
            logger.error(f"收集证据时出错: {str(e)}")
            # 返回空证据而不是抛出异常
            return {
                'software': [],
                'report': [],
                'interaction': [],
                'announcement': []
            }
    
    def _collect_evidence_parallel(self, ts_code: str, concepts: List[str], 
                                  data_sources: List[str] = None) -> Dict[str, List[Dict]]:
        """
        并行收集各类证据
        """
        # 准备并行任务
        tasks = {
            'software': lambda: self._collect_software_evidence(ts_code, concepts, data_sources),
            'interaction': lambda: self._collect_interaction_evidence(ts_code, concepts),
            'report': lambda: self._collect_report_evidence_optimized(ts_code, concepts),
            'announcement': lambda: self._collect_announcement_evidence_optimized(ts_code, concepts)
        }
        
        # 并行执行
        results = self.parallel_executor.execute(tasks)
        
        # 处理结果
        evidence = {}
        for evidence_type, result in results.items():
            if isinstance(result, dict) and 'error' in result:
                logger.warning(f"收集{evidence_type}证据失败: {result['error']}")
                evidence[evidence_type] = []
            else:
                evidence[evidence_type] = result or []
        
        return evidence
    
    @monitor_performance("collect_software_evidence")
    def _collect_software_evidence(self, ts_code: str, concepts: List[str], 
                                  data_sources: List[str] = None) -> List[Dict]:
        """
        收集软件收录证据
        
        根据原始设计：
        - 东财收录：15分
        - 同花顺收录：15分
        - 其他软件（开盘啦）：10分
        """
        evidence_list = []
        
        if not data_sources:
            # 查询股票在哪些数据源中
            data_sources = self._get_stock_data_sources(ts_code, concepts)
        
        # 数据源映射
        source_map = {
            'THS': ('同花顺', 15),
            'DC': ('东财', 15),
            'KPL': ('开盘啦', 10)
        }
        
        for source in data_sources:
            if source in source_map:
                name, score = source_map[source]
                evidence_list.append({
                    'type': '软件收录',
                    'source': name,
                    'content': f'{name}收录为相关概念成分股',
                    'score': score,
                    'date': datetime.now().strftime('%Y-%m-%d')
                })
        
        return evidence_list
    
    @monitor_performance("collect_interaction_evidence")
    def _collect_interaction_evidence(self, ts_code: str, concepts: List[str]) -> List[Dict]:
        """
        收集互动平台证据
        
        根据原始设计：
        - 董秘确认：20分
        """
        evidence_list = []
        
        # 确定交易所
        exchange = 'sh' if ts_code.endswith('.SH') else 'sz'
        table = f'tu_irm_qa_{exchange}'
        
        # 对每个概念进行查询
        for concept in concepts:
            query = f"""
            SELECT trade_date, q, a 
            FROM {table}
            WHERE ts_code = :ts_code 
            AND (q LIKE :concept_pattern OR a LIKE :concept_pattern)
            ORDER BY trade_date DESC
            LIMIT 5
            """
            
            try:
                results = self.db.execute_query(
                    query, 
                    {
                        'ts_code': ts_code,
                        'concept_pattern': f'%{concept}%'
                    }
                )
                
                # 分析回答内容
                for row in results:
                    answer = row['a']
                    question = row['q']
                    
                    # 检查是否在回答中确认了概念
                    if self._is_concept_confirmed(answer, concept):
                        evidence_list.append({
                            'type': '互动平台',
                            'source': '董秘回复',
                            'date': str(row['trade_date']),
                            'content': f"问：{question[:50]}... 答：{answer[:100]}...",
                            'score': 20,
                            'concept': concept
                        })
                        break  # 每个概念只需要一个确认
                    
                    # 检查是否明确否认
                    elif self._is_concept_denied(answer, concept):
                        evidence_list.append({
                            'type': '互动平台',
                            'source': '董秘回复',
                            'date': str(row['trade_date']),
                            'content': f"否认涉及{concept}业务",
                            'score': 0,
                            'concept': concept,
                            'negative': True
                        })
                        break
                        
            except Exception as e:
                logger.error(f"查询互动平台数据失败: {str(e)}")
        
        return evidence_list
    
    @monitor_performance("collect_report_evidence")
    def _collect_report_evidence_optimized(self, ts_code: str, concepts: List[str]) -> List[Dict]:
        """
        收集财报证据（优化版）
        
        根据原始设计：
        - 年报提及：15分
        - 季报提及：15分
        """
        evidence_list = []
        
        # 延迟初始化RAG Agent
        if self.rag_agent is None:
            try:
                self.rag_agent = RAGAgentModular()
            except Exception as e:
                logger.error(f"初始化RAG Agent失败: {str(e)}")
                return evidence_list
        
        # 获取股票名称
        stock_name = self._get_stock_name(ts_code)
        if not stock_name:
            return evidence_list
        
        # 优化查询
        optimized_queries = query_optimizer.optimize_rag_query(stock_name, concepts)
        
        # 限制查询数量
        for query in optimized_queries[:3]:  # 最多3个查询
            try:
                # 设置超时
                start = time.time()
                result = self.rag_agent.query(query)
                
                # 检查超时
                if time.time() - start > 8:  # 8秒超时
                    logger.warning(f"RAG查询接近超时: {query}")
                    break
                
                if isinstance(result, dict) and result.get('success') and result.get('result'):
                    content = result['result']
                    
                    # 分析内容
                    for concept in concepts:
                        if concept in content:
                            # 判断是年报还是季报
                            if '年报' in content:
                                excerpt = self._extract_relevant_excerpt(content, concept, 150)
                                evidence_list.append({
                                    'type': '财报',
                                    'source': '年报',
                                    'content': excerpt,
                                    'score': 15,
                                    'concept': concept
                                })
                            elif '季报' in content:
                                excerpt = self._extract_relevant_excerpt(content, concept, 150)
                                evidence_list.append({
                                    'type': '财报',
                                    'source': '季报',
                                    'content': excerpt,
                                    'score': 15,
                                    'concept': concept
                                })
                            
                            # 每个概念最多一个年报和一个季报证据
                            if len([e for e in evidence_list if e['concept'] == concept]) >= 2:
                                break
                        
            except Exception as e:
                logger.error(f"查询财报证据失败: {str(e)}")
                # 不要让一个失败影响整体
                continue
        
        return evidence_list
    
    @monitor_performance("collect_announcement_evidence")
    def _collect_announcement_evidence_optimized(self, ts_code: str, concepts: List[str]) -> List[Dict]:
        """
        收集公告证据（优化版）
        
        根据原始设计：
        - 临时公告：10分
        """
        evidence_list = []
        
        # 延迟初始化RAG Agent
        if self.rag_agent is None:
            try:
                self.rag_agent = RAGAgentModular()
            except Exception as e:
                logger.error(f"初始化RAG Agent失败: {str(e)}")
                return evidence_list
        
        # 获取股票名称
        stock_name = self._get_stock_name(ts_code)
        if not stock_name:
            return evidence_list
        
        # 只查询最重要的概念
        important_concepts = concepts[:2]  # 最多2个概念
        
        for concept in important_concepts:
            query = f"{stock_name} {concept} 公告"
            
            try:
                # 快速查询
                result = self.rag_agent.query(query)
                
                if isinstance(result, dict) and result.get('success') and result.get('result'):
                    content = result['result']
                    
                    # 检查是否包含公告相关内容
                    if '公告' in content and concept in content:
                        # 提取公告标题或摘要
                        excerpt = self._extract_announcement_title(content, concept)
                        
                        evidence_list.append({
                            'type': '公告',
                            'source': '临时公告',
                            'content': excerpt,
                            'score': 10,
                            'concept': concept
                        })
                        
            except Exception as e:
                logger.error(f"查询公告证据失败: {str(e)}")
                continue
        
        return evidence_list
    
    def _get_stock_data_sources(self, ts_code: str, concepts: List[str]) -> List[str]:
        """获取股票所在的数据源"""
        sources = []
        
        # 检查同花顺
        query = """
        SELECT DISTINCT 'THS' as source
        FROM tu_ths_member
        WHERE ts_code = :ts_code
        """
        result = self.db.execute_query(query, {'ts_code': ts_code})
        if result:
            sources.append('THS')
        
        # 检查东财
        query = """
        SELECT DISTINCT 'DC' as source
        FROM tu_dc_member
        WHERE ts_code = :ts_code
        """
        result = self.db.execute_query(query, {'ts_code': ts_code})
        if result:
            sources.append('DC')
        
        # 检查开盘啦
        query = """
        SELECT DISTINCT 'KPL' as source
        FROM tu_kpl_concept_cons
        WHERE ts_code = :ts_code
        """
        result = self.db.execute_query(query, {'ts_code': ts_code})
        if result:
            sources.append('KPL')
        
        return sources
    
    def _get_stock_name(self, ts_code: str) -> Optional[str]:
        """获取股票名称"""
        if ts_code in self._stock_name_cache:
            return self._stock_name_cache[ts_code]
        
        query = """
        SELECT name 
        FROM tu_stock_basic
        WHERE ts_code = :ts_code
        LIMIT 1
        """
        
        try:
            result = self.db.execute_query(query, {'ts_code': ts_code})
            if result:
                name = result[0]['name']
                self._stock_name_cache[ts_code] = name
                return name
        except:
            pass
        
        return None
    
    def _is_concept_confirmed(self, answer: str, concept: str) -> bool:
        """判断董秘回答是否确认了概念"""
        # 肯定词汇
        positive_words = ['是', '有', '涉及', '包含', '从事', '布局', '开展', '拥有']
        
        # 检查概念是否在回答中
        if concept not in answer:
            return False
        
        # 检查是否有肯定词汇
        for word in positive_words:
            if word in answer:
                # 检查是否是否定句
                if not self._is_concept_denied(answer, concept):
                    return True
        
        return False
    
    def _is_concept_denied(self, answer: str, concept: str) -> bool:
        """判断董秘回答是否否认了概念"""
        # 否定词汇
        negative_words = ['没有', '无', '不涉及', '不包含', '未从事', '暂无', '尚未']
        
        for word in negative_words:
            if word in answer and concept in answer:
                return True
        
        return False
    
    def _extract_relevant_excerpt(self, content: str, concept: str, max_length: int = 150) -> str:
        """提取相关片段"""
        # 找到概念出现的位置
        index = content.find(concept)
        if index == -1:
            return content[:max_length] + "..."
        
        # 提取前后文
        start = max(0, index - 50)
        end = min(len(content), index + max_length - 50)
        
        excerpt = content[start:end]
        
        # 添加省略号
        if start > 0:
            excerpt = "..." + excerpt
        if end < len(content):
            excerpt = excerpt + "..."
        
        return excerpt
    
    def _extract_announcement_title(self, content: str, concept: str) -> str:
        """提取公告标题"""
        # 尝试提取标题（通常在开头）
        lines = content.split('\n')
        for line in lines[:5]:  # 只看前5行
            if concept in line and len(line) < 100:
                return line.strip()
        
        # 如果没找到标题，返回摘要
        return self._extract_relevant_excerpt(content, concept, 100)
    
    def calculate_total_score(self, evidence: Dict[str, List[Dict]]) -> Dict[str, float]:
        """
        计算各维度总分
        
        Returns:
            各维度得分字典
        """
        scores = {
            'software': 0,      # 软件收录（满分40）
            'report': 0,        # 财报证据（满分30）
            'interaction': 0,   # 互动平台（满分20）
            'announcement': 0,  # 公告证据（满分10）
            'total': 0          # 总分（满分100）
        }
        
        # 计算各维度得分
        for evidence_type, evidence_list in evidence.items():
            for ev in evidence_list:
                if not ev.get('negative', False):  # 排除否定证据
                    scores[evidence_type] += ev.get('score', 0)
        
        # 限制各维度最高分
        scores['software'] = min(scores['software'], 40)
        scores['report'] = min(scores['report'], 30)
        scores['interaction'] = min(scores['interaction'], 20)
        scores['announcement'] = min(scores['announcement'], 10)
        
        # 计算总分
        scores['total'] = (scores['software'] + scores['report'] + 
                          scores['interaction'] + scores['announcement'])
        
        return scores
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """获取性能统计信息"""
        return {
            'cache_stats': evidence_cache.get_stats(),
            'performance_metrics': performance_monitor.get_all_stats()
        }
    
    def __del__(self):
        """清理资源"""
        if hasattr(self, 'db'):
            self.db.close()


# 测试
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    collector = EvidenceCollectorOptimized()
    
    # 测试证据收集
    evidence = collector.collect_evidence(
        ts_code='600519.SH',
        concepts=['白酒', '消费'],
        data_sources=['THS', 'DC']
    )
    
    print("\n收集到的证据:")
    for evidence_type, evidence_list in evidence.items():
        print(f"\n{evidence_type}:")
        for ev in evidence_list:
            print(f"  - {ev['source']}: {ev['content'][:50]}... (得分: {ev['score']})")
    
    # 计算总分
    scores = collector.calculate_total_score(evidence)
    print(f"\n各维度得分: {scores}")
    
    # 显示性能统计
    stats = collector.get_performance_stats()
    print(f"\n性能统计: {stats}")