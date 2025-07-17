#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
新闻文本处理器
用于从新闻文本中提取概念和关键信息
"""

import re
import logging
from typing import List, Dict, Tuple, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class NewsProcessor:
    """新闻文本处理器"""
    
    def __init__(self):
        """初始化"""
        # 政策相关关键词
        self.policy_keywords = [
            '发改委', '工信部', '国务院', '证监会', '央行', '银保监会',
            '政策', '规划', '意见', '通知', '措施', '方案', '指导'
        ]
        
        # 技术概念关键词
        self.tech_keywords = {
            '新能源': ['新能源', '清洁能源', '绿色能源', '可再生能源'],
            '电池': ['电池', '锂电', '钠电', '固态电池', '储能'],
            '汽车': ['汽车', '新能源车', '智能驾驶', '自动驾驶', '车联网'],
            '半导体': ['芯片', '半导体', '集成电路', '晶圆'],
            '人工智能': ['人工智能', 'AI', '机器学习', '深度学习'],
            '5G': ['5G', '通信', '基站', '物联网'],
            '医药': ['医药', '创新药', '疫苗', '医疗器械']
        }
        
        # 时间表达提取正则
        self.time_patterns = [
            (r'(\d{4})年', 'year'),
            (r'到(\d{4})年', 'target_year'),
            (r'(\d+)月', 'month'),
            (r'近日|最近|日前', 'recent'),
            (r'今年|本年', 'this_year'),
            (r'明年', 'next_year')
        ]
        
        # 数量表达提取正则
        self.quantity_patterns = [
            (r'(\d+(?:\.\d+)?)\s*万?千瓦', 'power_capacity'),
            (r'(\d+(?:\.\d+)?)\s*[万亿]元', 'money'),
            (r'(\d+(?:\.\d+)?)\s*%', 'percentage'),
            (r'(\d+(?:\.\d+)?)\s*倍', 'times')
        ]
        
        logger.info("NewsProcessor初始化完成")
    
    def process_news(self, news_text: str) -> Dict[str, Any]:
        """
        处理新闻文本
        
        Args:
            news_text: 新闻文本
            
        Returns:
            处理结果，包含：
            - concepts: 提取的概念列表
            - entities: 提取的实体（政策部门、公司等）
            - time_info: 时间信息
            - quantities: 数量信息
            - summary: 关键信息摘要
        """
        result = {
            'concepts': [],
            'entities': {
                'policy_makers': [],
                'companies': [],
                'industries': []
            },
            'time_info': {},
            'quantities': {},
            'key_points': [],
            'sentiment': 'neutral'
        }
        
        # 1. 提取概念
        result['concepts'] = self.extract_concepts(news_text)
        
        # 2. 提取政策制定者
        result['entities']['policy_makers'] = self.extract_policy_makers(news_text)
        
        # 3. 提取时间信息
        result['time_info'] = self.extract_time_info(news_text)
        
        # 4. 提取数量信息
        result['quantities'] = self.extract_quantities(news_text)
        
        # 5. 提取关键要点
        result['key_points'] = self.extract_key_points(news_text)
        
        # 6. 分析情感倾向
        result['sentiment'] = self.analyze_sentiment(news_text)
        
        logger.info(f"新闻处理完成，提取概念: {result['concepts']}")
        
        return result
    
    def extract_concepts(self, text: str) -> List[str]:
        """提取概念关键词"""
        concepts = []
        
        # 1. 基于技术关键词提取
        for category, keywords in self.tech_keywords.items():
            for keyword in keywords:
                if keyword in text:
                    concepts.append(keyword)
        
        # 2. 提取"XXX概念"、"XXX板块"、"XXX行业"
        pattern = r'([^\s，。、]{2,6})(概念|板块|行业|领域|产业)'
        matches = re.findall(pattern, text)
        for match in matches:
            concept = match[0] + match[1]
            if concept not in concepts and len(match[0]) >= 2:
                concepts.append(match[0])  # 只保留核心词
        
        # 3. 去重和清理
        concepts = list(set(concepts))
        
        # 4. 过滤太短或太长的概念
        concepts = [c for c in concepts if 2 <= len(c) <= 10]
        
        return concepts[:10]  # 最多返回10个概念
    
    def extract_policy_makers(self, text: str) -> List[str]:
        """提取政策制定部门"""
        makers = []
        
        for keyword in self.policy_keywords:
            if keyword in text:
                makers.append(keyword)
        
        # 提取"XXX部"格式
        pattern = r'([^\s]{2,6}部)(?:门|委)?'
        matches = re.findall(pattern, text)
        for match in matches:
            if match not in makers and not match.startswith('全'):
                makers.append(match)
        
        return list(set(makers))
    
    def extract_time_info(self, text: str) -> Dict[str, str]:
        """提取时间信息"""
        time_info = {}
        
        for pattern, time_type in self.time_patterns:
            matches = re.findall(pattern, text)
            if matches:
                if time_type in ['year', 'target_year', 'month']:
                    time_info[time_type] = matches[0]
                else:
                    time_info[time_type] = True
        
        # 处理相对时间
        current_year = datetime.now().year
        if time_info.get('this_year'):
            time_info['year'] = str(current_year)
        elif time_info.get('next_year'):
            time_info['year'] = str(current_year + 1)
        
        return time_info
    
    def extract_quantities(self, text: str) -> Dict[str, List[str]]:
        """提取数量信息"""
        quantities = {}
        
        for pattern, q_type in self.quantity_patterns:
            matches = re.findall(pattern, text)
            if matches:
                quantities[q_type] = matches
        
        return quantities
    
    def extract_key_points(self, text: str) -> List[str]:
        """提取关键要点"""
        key_points = []
        
        # 1. 提取带有关键动词的句子
        key_verbs = ['支持', '鼓励', '推动', '发展', '提出', '明确', '重点', '加快', '推广', '部署']
        
        sentences = re.split(r'[。！？]', text)
        for sentence in sentences:
            if any(verb in sentence for verb in key_verbs) and 10 < len(sentence) < 100:
                # 清理句子
                sentence = sentence.strip()
                if sentence and sentence not in key_points:
                    key_points.append(sentence)
        
        # 2. 提取数字相关的目标
        for sentence in sentences:
            if re.search(r'\d+', sentence) and ('达到' in sentence or '目标' in sentence):
                sentence = sentence.strip()
                if sentence and sentence not in key_points:
                    key_points.append(sentence)
        
        return key_points[:5]  # 最多返回5个要点
    
    def analyze_sentiment(self, text: str) -> str:
        """分析情感倾向"""
        positive_words = [
            '利好', '支持', '鼓励', '推动', '发展', '增长', '提升', '加快',
            '创新', '突破', '领先', '优势', '机遇', '红利'
        ]
        
        negative_words = [
            '下降', '减少', '困难', '挑战', '风险', '压力', '下滑', '萎缩',
            '限制', '约束', '不利', '担忧'
        ]
        
        positive_count = sum(1 for word in positive_words if word in text)
        negative_count = sum(1 for word in negative_words if word in text)
        
        if positive_count > negative_count * 2:
            return 'positive'
        elif negative_count > positive_count * 2:
            return 'negative'
        else:
            return 'neutral'
    
    def get_concept_suggestions(self, processed_result: Dict[str, Any]) -> List[str]:
        """
        基于处理结果给出概念建议
        
        Args:
            processed_result: process_news的返回结果
            
        Returns:
            建议关注的概念列表
        """
        suggestions = []
        
        # 1. 直接提取的概念
        suggestions.extend(processed_result['concepts'])
        
        # 2. 根据政策制定者推断
        if '工信部' in processed_result['entities']['policy_makers']:
            suggestions.extend(['工业互联网', '智能制造', '新材料'])
        if '发改委' in processed_result['entities']['policy_makers']:
            suggestions.extend(['基建', '新基建', '碳中和'])
        
        # 3. 根据情感倾向调整
        if processed_result['sentiment'] == 'positive':
            # 积极情绪下，可以关注相关的上游产业
            if '新能源' in suggestions:
                suggestions.extend(['锂矿', '稀土', '新能源设备'])
        
        # 去重并限制数量
        suggestions = list(set(suggestions))
        
        return suggestions[:8]


# 测试
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    processor = NewsProcessor()
    
    # 测试新闻
    test_news = """
    据悉，国家发改委、工信部等多部门近日联合发布《关于推动新型储能高质量发展的指导意见》。
    文件指出，到2025年，新型储能装机规模达到3000万千瓦以上，到2030年，新型储能全面市场化发展。
    文件特别强调，要重点发展锂离子电池、钠离子电池、液流电池、压缩空气储能、飞轮储能等多元化技术路线。
    同时，支持固态电池、锂金属电池、钠离子电池等新一代高能量密度储能技术研发和产业化。
    """
    
    result = processor.process_news(test_news)
    
    print("处理结果:")
    print(f"概念: {result['concepts']}")
    print(f"政策制定者: {result['entities']['policy_makers']}")
    print(f"时间信息: {result['time_info']}")
    print(f"数量信息: {result['quantities']}")
    print(f"情感倾向: {result['sentiment']}")
    print(f"\n关键要点:")
    for point in result['key_points']:
        print(f"  - {point}")
    
    suggestions = processor.get_concept_suggestions(result)
    print(f"\n建议关注的概念: {suggestions}")