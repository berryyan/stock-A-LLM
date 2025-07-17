#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
概念匹配器
通过LLM扩展概念关键词，提高查全率
"""

import logging
from typing import List, Dict, Set
import json

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

# 添加配置导入
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from config.settings import settings

logger = logging.getLogger(__name__)


class ConceptMatcher:
    """概念匹配器"""
    
    def __init__(self):
        """初始化"""
        # 初始化LLM
        self.llm = ChatOpenAI(
            model="deepseek-chat",
            temperature=0.3,  # 适中的创造性
            max_tokens=1000,
            api_key=settings.DEEPSEEK_API_KEY,
            base_url=settings.DEEPSEEK_BASE_URL
        )
        
        # 概念映射缓存（避免重复调用LLM）
        self._concept_cache = {}
        
        logger.info("ConceptMatcher初始化完成")
    
    def expand_concepts(self, concepts: List[str]) -> List[str]:
        """
        扩展概念关键词
        
        Args:
            concepts: 原始概念列表，如 ["固态电池"]
            
        Returns:
            扩展后的概念列表，如 ["固态电池", "全固态电池", "固态锂电池", "半固态电池"]
        """
        # 检查缓存
        cache_key = ','.join(sorted(concepts))
        if cache_key in self._concept_cache:
            logger.info(f"从缓存返回概念扩展: {cache_key}")
            return self._concept_cache[cache_key]
        
        try:
            # 使用LLM扩展概念
            expanded = self._llm_expand_concepts(concepts)
            
            # 合并原始概念和扩展概念
            all_concepts = list(set(concepts + expanded))
            
            # 缓存结果
            self._concept_cache[cache_key] = all_concepts
            
            return all_concepts
            
        except Exception as e:
            logger.error(f"LLM概念扩展失败: {str(e)}, 降级到规则扩展")
            # 降级到基于规则的扩展
            return self._rule_based_expand(concepts)
    
    def _llm_expand_concepts(self, concepts: List[str]) -> List[str]:
        """使用LLM扩展概念"""
        prompt = ChatPromptTemplate.from_messages([
            ("system", """你是一个A股市场概念专家。
根据给定的概念关键词，扩展出相关的概念名称。

要求：
1. 扩展的概念必须是A股市场实际存在的概念板块
2. 包括同义词、近义词、上下位概念
3. 优先扩展同花顺、东财等主流平台的概念名称
4. 返回JSON格式：{{"expanded": ["概念1", "概念2", ...]}}
5. 最多返回10个最相关的概念

示例：
输入：固态电池
输出：{{"expanded": ["固态电池", "全固态电池", "固态锂电池", "半固态电池", "固态电解质", "锂电池", "新能源电池", "储能"]}}"""),
            ("user", "请扩展以下概念：{concepts}")
        ])
        
        chain = prompt | self.llm | StrOutputParser()
        
        # 调用LLM
        result = chain.invoke({"concepts": ', '.join(concepts)})
        
        # 解析结果
        try:
            data = json.loads(result)
            expanded = data.get('expanded', [])
            
            # 过滤和清理
            expanded = [c.strip() for c in expanded if c.strip() and len(c.strip()) > 1]
            
            return expanded[:10]  # 最多10个
            
        except json.JSONDecodeError:
            logger.error(f"LLM返回格式错误: {result}")
            # 尝试简单解析
            return self._simple_parse_llm_result(result)
    
    def _simple_parse_llm_result(self, result: str) -> List[str]:
        """简单解析LLM结果（降级方案）"""
        # 先尝试移除markdown代码块标记
        cleaned_result = result.strip()
        if cleaned_result.startswith('```'):
            # 移除开头的```json或```
            cleaned_result = cleaned_result.split('\n', 1)[1] if '\n' in cleaned_result else cleaned_result[3:]
        if cleaned_result.endswith('```'):
            # 移除结尾的```
            cleaned_result = cleaned_result.rsplit('```', 1)[0]
        
        # 再次尝试JSON解析
        try:
            data = json.loads(cleaned_result.strip())
            expanded = data.get('expanded', [])
            return [c.strip() for c in expanded if c.strip() and len(c.strip()) > 1][:10]
        except:
            # 如果还是失败，使用正则提取
            import re
            pattern = r'[\u4e00-\u9fa5]+'
            matches = re.findall(pattern, result)
            
            # 过滤太短的词
            concepts = [m for m in matches if len(m) > 1]
            
            return concepts[:10]
    
    def _rule_based_expand(self, concepts: List[str]) -> List[str]:
        """基于规则的概念扩展（降级方案）"""
        expanded = set(concepts)
        
        # 定义一些常见的概念扩展规则
        expansion_rules = {
            "电池": ["锂电池", "新能源电池", "储能", "动力电池"],
            "固态电池": ["全固态电池", "半固态电池", "固态锂电池", "固态电解质"],
            "充电": ["充电桩", "充电站", "快充", "无线充电"],
            "光伏": ["太阳能", "光伏发电", "光伏组件", "分布式光伏"],
            "芯片": ["半导体", "集成电路", "晶圆", "芯片设计"],
            "新能源": ["新能源车", "清洁能源", "绿色能源", "可再生能源"],
            "人工智能": ["AI", "机器学习", "深度学习", "智能算法"],
            "医药": ["创新药", "医疗", "生物医药", "中药"],
            "汽车": ["新能源车", "智能汽车", "汽车零部件", "整车"],
            "5G": ["通信", "5G基站", "5G应用", "物联网"]
        }
        
        # 应用规则
        for concept in concepts:
            # 直接匹配
            if concept in expansion_rules:
                expanded.update(expansion_rules[concept])
            
            # 部分匹配
            for key, values in expansion_rules.items():
                if key in concept or concept in key:
                    expanded.update(values)
        
        # 生成变体
        for concept in concepts:
            # 如果包含"概念"，去掉试试
            if concept.endswith("概念"):
                expanded.add(concept[:-2])
            # 如果不包含"概念"，加上试试
            elif "概念" not in concept:
                expanded.add(concept + "概念")
        
        return list(expanded)
    
    def match_concepts_in_database(
        self, 
        concepts: List[str], 
        available_concepts: List[Dict[str, str]]
    ) -> List[Dict[str, str]]:
        """
        在数据库中匹配概念
        
        Args:
            concepts: 要匹配的概念列表
            available_concepts: 数据库中的概念列表
                               [{"ts_code": "xxx", "name": "xxx"}, ...]
        
        Returns:
            匹配到的概念列表
        """
        matched = []
        
        # 转换为集合以提高查找效率
        concept_set = set(concepts)
        
        for db_concept in available_concepts:
            concept_name = db_concept['name']
            
            # 精确匹配
            if concept_name in concept_set:
                matched.append(db_concept)
                continue
            
            # 模糊匹配
            for concept in concepts:
                if self._fuzzy_match(concept, concept_name):
                    matched.append(db_concept)
                    break
        
        # 去重
        seen = set()
        unique_matched = []
        for item in matched:
            if item['ts_code'] not in seen:
                seen.add(item['ts_code'])
                unique_matched.append(item)
        
        return unique_matched
    
    def _fuzzy_match(self, query: str, target: str) -> bool:
        """模糊匹配"""
        # 1. 包含关系
        if query in target or target in query:
            return True
        
        # 2. 去掉"概念"后匹配
        query_clean = query.replace("概念", "").replace("板块", "")
        target_clean = target.replace("概念", "").replace("板块", "")
        
        if query_clean and target_clean:
            if query_clean in target_clean or target_clean in query_clean:
                return True
        
        # 3. 同义词匹配（可以扩展）
        synonyms = {
            "电池": ["电源", "储能"],
            "汽车": ["整车", "车"],
            "医药": ["制药", "药"],
            "半导体": ["芯片"],
            "人工智能": ["AI"]
        }
        
        for key, values in synonyms.items():
            if key in query:
                for value in values:
                    if value in target:
                        return True
            if key in target:
                for value in values:
                    if value in query:
                        return True
        
        return False
    
    def clear_cache(self):
        """清空缓存"""
        self._concept_cache.clear()
        logger.info("概念缓存已清空")


# 测试
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    matcher = ConceptMatcher()
    
    # 测试概念扩展
    test_concepts = [
        ["固态电池"],
        ["充电宝"],
        ["人工智能"],
        ["新能源汽车"]
    ]
    
    for concepts in test_concepts:
        print(f"\n原始概念: {concepts}")
        expanded = matcher.expand_concepts(concepts)
        print(f"扩展后: {expanded}")
    
    # 测试数据库匹配
    db_concepts = [
        {"ts_code": "881157.TI", "name": "固态电池"},
        {"ts_code": "881158.TI", "name": "锂电池"},
        {"ts_code": "881159.TI", "name": "充电桩"},
        {"ts_code": "881160.TI", "name": "人工智能"},
        {"ts_code": "881161.TI", "name": "新能源车"}
    ]
    
    print("\n\n数据库概念匹配测试:")
    matched = matcher.match_concepts_in_database(["固态电池", "充电"], db_concepts)
    for m in matched:
        print(f"  匹配到: {m['name']} ({m['ts_code']})")