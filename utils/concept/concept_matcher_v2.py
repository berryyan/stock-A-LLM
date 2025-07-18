#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
概念匹配器 V2
在数据库中实际存在的概念名称中进行智能匹配
"""

import logging
from typing import List, Dict, Set, Optional
import json
from datetime import datetime, timedelta

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from sqlalchemy import text
import pandas as pd

# 添加配置导入
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from config.settings import settings
from database.mysql_connector import MySQLConnector

logger = logging.getLogger(__name__)


class ConceptMatcherV2:
    """概念匹配器V2 - 基于数据库实际概念的匹配"""
    
    def __init__(self):
        """初始化"""
        # 初始化数据库连接
        self.db = MySQLConnector()
        
        # 初始化LLM
        self.llm = ChatOpenAI(
            model="deepseek-chat",
            temperature=0.3,
            max_tokens=1000,
            api_key=settings.DEEPSEEK_API_KEY,
            base_url=settings.DEEPSEEK_BASE_URL
        )
        
        # 概念列表缓存
        self._concept_list_cache = None
        self._cache_time = None
        self._cache_ttl = timedelta(hours=1)
        
        # 匹配结果缓存
        self._match_cache = {}
        
        logger.info("ConceptMatcherV2初始化完成")
    
    def _load_all_concepts(self) -> Dict[str, List[Dict]]:
        """加载所有数据源的概念列表"""
        # 检查缓存
        if self._concept_list_cache and self._cache_time:
            if datetime.now() - self._cache_time < self._cache_ttl:
                return self._concept_list_cache
        
        concepts = {
            "THS": [],
            "DC": [],
            "KPL": []
        }
        
        try:
            # 1. 加载同花顺概念
            ths_query = """
            SELECT DISTINCT name, ts_code
            FROM tu_ths_index
            WHERE exchange = 'A' AND type = 'N'
            ORDER BY name
            """
            ths_result = self.db.execute_query(ths_query)
            concepts["THS"] = [{"name": r["name"], "code": r["ts_code"]} for r in ths_result]
            
            # 2. 加载东财板块
            dc_query = """
            SELECT DISTINCT name, ts_code
            FROM tu_dc_index
            GROUP BY name, ts_code
            ORDER BY name
            """
            dc_result = self.db.execute_query(dc_query)
            concepts["DC"] = [{"name": r["name"], "code": r["ts_code"]} for r in dc_result]
            
            # 3. 加载开盘啦概念（包含描述信息）
            kpl_query = """
            SELECT DISTINCT name, ts_code, `desc`
            FROM tu_kpl_concept_cons
            WHERE trade_date = (SELECT MAX(trade_date) FROM tu_kpl_concept_cons)
            GROUP BY name, ts_code, `desc`
            ORDER BY name
            """
            kpl_result = self.db.execute_query(kpl_query)
            concepts["KPL"] = [
                {
                    "name": r["name"], 
                    "code": r["ts_code"],
                    "desc": r.get("desc", "")
                } 
                for r in kpl_result
            ]
            
            # 更新缓存
            self._concept_list_cache = concepts
            self._cache_time = datetime.now()
            
            logger.info(f"加载概念完成 - 同花顺: {len(concepts['THS'])}个, "
                       f"东财: {len(concepts['DC'])}个, 开盘啦: {len(concepts['KPL'])}个")
            
        except Exception as e:
            logger.error(f"加载概念列表失败: {str(e)}")
            # 返回空结果，避免程序崩溃
            return {"THS": [], "DC": [], "KPL": []}
        
        return concepts
    
    def match_concepts(self, user_concepts: List[str]) -> Dict[str, List[str]]:
        """
        在实际存在的概念中匹配用户输入
        
        Args:
            user_concepts: 用户输入的概念列表
            
        Returns:
            按数据源分组的匹配结果
        """
        # 检查缓存
        cache_key = ','.join(sorted(user_concepts))
        if cache_key in self._match_cache:
            logger.info(f"从缓存返回匹配结果: {cache_key}")
            return self._match_cache[cache_key]
        
        # 加载所有概念
        all_concepts = self._load_all_concepts()
        
        # 如果概念列表为空，降级到简单匹配
        if not any(all_concepts.values()):
            logger.warning("概念列表为空，降级到简单匹配")
            return self._simple_match(user_concepts)
        
        try:
            # 使用LLM进行智能匹配
            matched = self._llm_match_concepts(user_concepts, all_concepts)
            
            # 缓存结果
            self._match_cache[cache_key] = matched
            
            return matched
            
        except Exception as e:
            logger.error(f"LLM匹配失败: {str(e)}, 降级到规则匹配")
            return self._rule_based_match(user_concepts, all_concepts)
    
    def _llm_match_concepts(self, user_concepts: List[str], all_concepts: Dict[str, List[Dict]]) -> Dict[str, List[str]]:
        """使用LLM进行概念匹配"""
        # 准备概念列表字符串
        concept_info = {
            "同花顺概念": [c["name"] for c in all_concepts["THS"]],
            "东财板块": [c["name"] for c in all_concepts["DC"]],
            "开盘啦概念": [
                f"{c['name']}（{c['desc'][:50]}...）" if c.get('desc') else c['name']
                for c in all_concepts["KPL"][:100]  # 限制数量避免token过多
            ]
        }
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", """你是一个A股市场概念匹配专家。
请在给定的概念列表中，找出与用户输入最相关的概念。

重要原则：
1. 只能从提供的列表中选择，不能创造新概念
2. 要考虑语义相似性（如"储能"可能匹配"储能概念"、"储能设备"等）
3. 每个数据源最多返回5个最相关的匹配
4. 如果某个数据源没有相关概念，该数据源返回空列表

返回JSON格式：
{{
    "THS": ["概念1", "概念2", ...],
    "DC": ["板块1", "板块2", ...],
    "KPL": ["概念1", "概念2", ...]
}}"""),
            ("user", """用户输入的概念：{user_concepts}

可选择的概念列表：
同花顺：{ths_concepts}
东财：{dc_concepts}
开盘啦：{kpl_concepts}

请匹配最相关的概念。""")
        ])
        
        chain = prompt | self.llm | StrOutputParser()
        
        # 调用LLM
        result = chain.invoke({
            "user_concepts": ', '.join(user_concepts),
            "ths_concepts": ', '.join(concept_info["同花顺概念"][:50]),  # 限制数量
            "dc_concepts": ', '.join(concept_info["东财板块"][:50]),
            "kpl_concepts": ', '.join(concept_info["开盘啦概念"][:30])
        })
        
        try:
            # 解析JSON响应（处理可能的markdown包装）
            clean_result = result.strip()
            if clean_result.startswith('```'):
                # 移除markdown代码块标记
                lines = clean_result.split('\n')
                clean_result = '\n'.join(lines[1:-1])
            
            matched = json.loads(clean_result)
            
            # 验证返回的概念确实存在
            validated = {"THS": [], "DC": [], "KPL": []}
            
            ths_names = {c["name"] for c in all_concepts["THS"]}
            dc_names = {c["name"] for c in all_concepts["DC"]}
            kpl_names = {c["name"] for c in all_concepts["KPL"]}
            
            for name in matched.get("THS", []):
                if name in ths_names:
                    validated["THS"].append(name)
            
            for name in matched.get("DC", []):
                if name in dc_names:
                    validated["DC"].append(name)
            
            for name in matched.get("KPL", []):
                if name in kpl_names:
                    validated["KPL"].append(name)
            
            logger.info(f"LLM匹配结果 - 同花顺: {len(validated['THS'])}个, "
                       f"东财: {len(validated['DC'])}个, 开盘啦: {len(validated['KPL'])}个")
            
            return validated
            
        except json.JSONDecodeError:
            logger.error(f"解析LLM响应失败: {result}")
            raise
    
    def _rule_based_match(self, user_concepts: List[str], all_concepts: Dict[str, List[Dict]]) -> Dict[str, List[str]]:
        """基于规则的匹配（降级方案）"""
        matched = {"THS": [], "DC": [], "KPL": []}
        
        for user_concept in user_concepts:
            # 同花顺匹配
            for concept in all_concepts["THS"]:
                if user_concept in concept["name"] or concept["name"] in user_concept:
                    matched["THS"].append(concept["name"])
            
            # 东财匹配
            for concept in all_concepts["DC"]:
                if user_concept in concept["name"] or concept["name"] in user_concept:
                    matched["DC"].append(concept["name"])
            
            # 开盘啦匹配（包括描述）
            for concept in all_concepts["KPL"]:
                if (user_concept in concept["name"] or concept["name"] in user_concept or
                    (concept.get("desc") and user_concept in concept["desc"])):
                    matched["KPL"].append(concept["name"])
        
        # 去重
        for source in matched:
            matched[source] = list(set(matched[source]))[:5]  # 限制每个源最多5个
        
        logger.info(f"规则匹配结果 - 同花顺: {len(matched['THS'])}个, "
                   f"东财: {len(matched['DC'])}个, 开盘啦: {len(matched['KPL'])}个")
        
        return matched
    
    def _simple_match(self, user_concepts: List[str]) -> Dict[str, List[str]]:
        """简单匹配（当数据库不可用时）"""
        # 直接返回用户输入
        return {
            "THS": user_concepts,
            "DC": user_concepts,
            "KPL": user_concepts
        }
    
    def extract_concepts(self, query: str) -> List[str]:
        """
        从用户查询中提取概念关键词
        这是LLM第一次介入的地方
        
        Args:
            query: 用户输入的查询文本
            
        Returns:
            提取出的概念关键词列表
        """
        # 处理简单情况
        if len(query) < 10:
            # 短查询直接作为概念
            return [query.strip()]
        
        try:
            # 使用LLM提取概念
            prompt = ChatPromptTemplate.from_messages([
                ("system", """你是一个A股市场概念提取专家。
从用户输入中提取股票投资相关的概念关键词。

重要原则：
1. 提取明确的概念名称（如"储能"、"人工智能"、"新能源"等）
2. 如果提到板块，提取板块名称
3. 如果是新闻文本，提取最核心的2-3个概念
4. 去除无关的修饰词和语气词
5. 概念词应该是名词或名词短语

返回格式：
直接返回概念列表，用逗号分隔，如：储能,固态电池,新能源"""),
                ("user", "请从以下文本中提取概念关键词：{query}")
            ])
            
            chain = prompt | self.llm | StrOutputParser()
            result = chain.invoke({"query": query})
            
            # 解析结果
            concepts = [c.strip() for c in result.split(',') if c.strip()]
            
            # 限制数量
            concepts = concepts[:5]
            
            logger.info(f"LLM提取概念: {concepts}")
            return concepts
            
        except Exception as e:
            logger.error(f"LLM提取概念失败: {str(e)}, 降级到简单提取")
            return self._simple_extract(query)
    
    def _simple_extract(self, query: str) -> List[str]:
        """简单的概念提取（降级方案）"""
        # 移除常见的查询词
        remove_words = ['概念股', '有哪些', '相关', '股票', '板块', '分析', '？', '?', '的']
        
        cleaned = query
        for word in remove_words:
            cleaned = cleaned.replace(word, ' ')
        
        # 分词并过滤
        concepts = []
        for word in cleaned.split():
            if len(word) >= 2:  # 至少2个字符
                concepts.append(word)
        
        return concepts[:3]  # 最多返回3个
    
    def expand_concepts(self, concepts: List[str]) -> List[str]:
        """
        扩展概念（通过LLM生成相关概念）
        
        Args:
            concepts: 原始概念列表
            
        Returns:
            扩展后的概念列表
        """
        if not concepts:
            return []
        
        try:
            prompt = ChatPromptTemplate.from_messages([
                ("system", """你是一个A股市场概念扩展专家。
给定一个或多个概念，扩展出相关的概念。

扩展原则：
1. 添加同义词和近义词（如"储能"→"储能设备"、"储能技术"）
2. 添加上下位概念（如"固态电池"→"电池"、"新能源电池"）
3. 添加相关产业链概念（如"新能源车"→"锂电池"、"充电桩"）
4. 最多扩展到8个概念

返回格式：
直接返回所有概念（包括原始概念），用逗号分隔"""),
                ("user", "请扩展以下概念：{concepts}")
            ])
            
            chain = prompt | self.llm | StrOutputParser()
            result = chain.invoke({"concepts": ', '.join(concepts)})
            
            # 解析结果
            expanded = [c.strip() for c in result.split(',') if c.strip()]
            
            # 确保原始概念包含在内
            for concept in concepts:
                if concept not in expanded:
                    expanded.insert(0, concept)
            
            # 限制数量
            expanded = expanded[:8]
            
            logger.info(f"概念扩展: {concepts} -> {expanded}")
            return expanded
            
        except Exception as e:
            logger.error(f"概念扩展失败: {str(e)}")
            return concepts  # 返回原始概念
    
    def __del__(self):
        """清理资源"""
        if hasattr(self, 'db'):
            self.db.close()


# 测试
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    matcher = ConceptMatcherV2()
    
    # 测试匹配
    test_concepts = ["储能", "新能源", "人工智能"]
    result = matcher.match_concepts(test_concepts)
    
    print("\n匹配结果:")
    for source, concepts in result.items():
        print(f"{source}: {concepts}")