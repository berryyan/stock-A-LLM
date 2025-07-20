#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
概念股证据收集器
收集软件收录、财报、互动平台、公告等多维度证据
"""

import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import re

# 添加项目根目录到Python路径
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from database.mysql_connector import MySQLConnector
from agents.rag_agent_modular import RAGAgentModular
from utils.agent_response import AgentResponse

logger = logging.getLogger(__name__)


class EvidenceCollector:
    """概念股证据收集器"""
    
    def __init__(self):
        """初始化证据收集器"""
        self.db = MySQLConnector()
        self.rag_agent = None  # 延迟初始化，避免循环依赖
        
        # 缓存
        self._stock_name_cache = {}
        self._evidence_cache = {}
        
        logger.info("EvidenceCollector初始化完成")
    
    def collect_evidence(self, ts_code: str, concepts: List[str], 
                        data_sources: List[str] = None) -> Dict[str, List[Dict]]:
        """
        收集所有维度的证据
        
        Args:
            ts_code: 股票代码
            concepts: 概念列表
            data_sources: 数据源列表（用于软件收录证据）
            
        Returns:
            包含各维度证据的字典
        """
        # 生成缓存键
        cache_key = f"{ts_code}_{','.join(concepts)}"
        if cache_key in self._evidence_cache:
            return self._evidence_cache[cache_key]
        
        evidence = {
            'software': [],      # 软件收录证据
            'report': [],        # 财报证据
            'interaction': [],   # 互动平台证据
            'announcement': []   # 公告证据
        }
        
        try:
            # 1. 收集软件收录证据
            evidence['software'] = self._collect_software_evidence(
                ts_code, concepts, data_sources
            )
            
            # 2. 收集互动平台证据
            evidence['interaction'] = self._collect_interaction_evidence(
                ts_code, concepts
            )
            
            # 3. 收集年报证据（通过RAG）
            evidence['report'] = self._collect_report_evidence(
                ts_code, concepts
            )
            
            # 4. 收集公告证据（通过RAG）
            evidence['announcement'] = self._collect_announcement_evidence(
                ts_code, concepts
            )
            
            # 缓存结果
            self._evidence_cache[cache_key] = evidence
            
            logger.info(f"收集到 {ts_code} 的证据：软件{len(evidence['software'])}条，"
                       f"财报{len(evidence['report'])}条，"
                       f"互动{len(evidence['interaction'])}条，"
                       f"公告{len(evidence['announcement'])}条")
            
        except Exception as e:
            logger.error(f"收集证据时出错: {str(e)}")
        
        return evidence
    
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
            LIMIT 10
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
    
    def _collect_report_evidence(self, ts_code: str, concepts: List[str]) -> List[Dict]:
        """
        收集财报证据（通过RAG）
        
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
        
        # 对每个概念查询年报
        for concept in concepts:
            # 构造查询
            query = f"{stock_name} {concept} 年报 业务 收入"
            
            try:
                result = self.rag_agent.query(query)
                
                if isinstance(result, dict) and result.get('success') and result.get('result'):
                    content = result['result']
                    
                    # 检查是否包含年报相关内容
                    if '年报' in content and concept in content:
                        # 提取相关片段
                        excerpt = self._extract_relevant_excerpt(content, concept, 150)
                        
                        evidence_list.append({
                            'type': '财报',
                            'source': '年报',
                            'content': excerpt,
                            'score': 15,
                            'concept': concept
                        })
                    
                    # 检查季报
                    if '季报' in content and concept in content:
                        excerpt = self._extract_relevant_excerpt(content, concept, 150)
                        
                        evidence_list.append({
                            'type': '财报',
                            'source': '季报',
                            'content': excerpt,
                            'score': 15,
                            'concept': concept
                        })
                        
            except Exception as e:
                logger.error(f"查询财报证据失败: {str(e)}")
        
        return evidence_list
    
    def _collect_announcement_evidence(self, ts_code: str, concepts: List[str]) -> List[Dict]:
        """
        收集公告证据（通过RAG）
        
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
        
        # 对每个概念查询公告
        for concept in concepts:
            query = f"{stock_name} {concept} 公告"
            
            try:
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
    
    def flatten_evidence(self, evidence: Dict[str, List[Dict]]) -> List[Dict]:
        """将证据展平为列表"""
        flat_list = []
        
        for evidence_type, evidence_list in evidence.items():
            for ev in evidence_list:
                # 添加证据类型
                ev_copy = ev.copy()
                ev_copy['evidence_type'] = evidence_type
                flat_list.append(ev_copy)
        
        # 按分数降序排序
        flat_list.sort(key=lambda x: x.get('score', 0), reverse=True)
        
        return flat_list
    
    def __del__(self):
        """清理资源"""
        if hasattr(self, 'db'):
            self.db.close()


# 测试
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    collector = EvidenceCollector()
    
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