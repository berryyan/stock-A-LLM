#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
基于Schema知识库的增强路由器
利用数据库结构知识优化查询路由决策
"""

import re
from typing import Dict, List, Any, Optional, Tuple, Set
from collections import defaultdict

from utils.schema_knowledge_base import schema_kb
from utils.logger import setup_logger


class SchemaEnhancedRouter:
    """Schema增强的路由器"""
    
    def __init__(self):
        """初始化路由器"""
        self.logger = setup_logger("schema_enhanced_router")
        
        # 构建字段到表的反向映射
        self._build_field_to_table_mapping()
        
        # 定义表类型到查询类型的映射
        self.table_type_mapping = {
            'financial': {
                'tables': ['tu_income', 'tu_balancesheet', 'tu_cashflow', 'tu_fina_indicator'],
                'query_type': 'FINANCIAL',
                'priority': 90
            },
            'money_flow': {
                'tables': ['tu_moneyflow_dc', 'tu_moneyflow_ind_dc'],
                'query_type': 'MONEY_FLOW',
                'priority': 85
            },
            'daily_data': {
                'tables': ['tu_daily_detail', 'tu_daily_basic'],
                'query_type': 'SQL_ONLY',
                'priority': 80
            },
            'announcement': {
                'tables': ['tu_anns_d'],
                'query_type': 'RAG_ONLY',
                'priority': 75
            },
            'interaction': {
                'tables': ['tu_irm_qa_sh', 'tu_irm_qa_sz'],
                'query_type': 'RAG_ONLY',
                'priority': 70
            }
        }
        
        # 构建关键词权重映射
        self._build_keyword_weights()
        
        self.logger.info("Schema增强路由器初始化完成")
    
    def _build_field_to_table_mapping(self):
        """构建字段到表的反向映射"""
        self.field_to_tables = defaultdict(set)
        
        for table_name, table_data in schema_kb.table_knowledge.items():
            for field_name in table_data['fields']:
                self.field_to_tables[field_name].add(table_name)
        
        # 构建中文字段到表的映射
        self.chinese_to_tables = defaultdict(set)
        for chinese, english in schema_kb.chinese_mapping.items():
            # 查找包含该英文字段的表
            for table_name, table_data in schema_kb.table_knowledge.items():
                if english in table_data['fields']:
                    self.chinese_to_tables[chinese].add(table_name)
    
    def _build_keyword_weights(self):
        """构建关键词权重映射"""
        self.keyword_weights = {
            # 财务分析关键词（高权重）
            '财务': {'weight': 10, 'types': ['FINANCIAL']},
            '健康度': {'weight': 10, 'types': ['FINANCIAL']},
            '杜邦分析': {'weight': 10, 'types': ['FINANCIAL']},
            'ROE': {'weight': 9, 'types': ['FINANCIAL']},
            'ROA': {'weight': 9, 'types': ['FINANCIAL']},
            '现金流': {'weight': 8, 'types': ['FINANCIAL']},
            '负债': {'weight': 7, 'types': ['FINANCIAL']},
            '利润': {'weight': 7, 'types': ['FINANCIAL', 'SQL_ONLY']},
            '营收': {'weight': 7, 'types': ['FINANCIAL', 'SQL_ONLY']},
            
            # 资金流向关键词
            '资金流向': {'weight': 10, 'types': ['MONEY_FLOW']},
            '主力资金': {'weight': 10, 'types': ['MONEY_FLOW']},
            '超大单': {'weight': 9, 'types': ['MONEY_FLOW']},
            '大单': {'weight': 8, 'types': ['MONEY_FLOW']},
            '流入': {'weight': 7, 'types': ['MONEY_FLOW']},
            '流出': {'weight': 7, 'types': ['MONEY_FLOW']},
            
            # 股价数据关键词
            '股价': {'weight': 8, 'types': ['SQL_ONLY']},
            '价格': {'weight': 7, 'types': ['SQL_ONLY']},
            '涨跌': {'weight': 7, 'types': ['SQL_ONLY']},
            '成交量': {'weight': 6, 'types': ['SQL_ONLY']},
            '市值': {'weight': 6, 'types': ['SQL_ONLY']},
            '开盘': {'weight': 5, 'types': ['SQL_ONLY']},
            '收盘': {'weight': 5, 'types': ['SQL_ONLY']},
            
            # 文档相关关键词
            '公告': {'weight': 9, 'types': ['RAG_ONLY']},
            '年报': {'weight': 8, 'types': ['RAG_ONLY']},
            '季报': {'weight': 8, 'types': ['RAG_ONLY']},
            '披露': {'weight': 7, 'types': ['RAG_ONLY']},
            '说明': {'weight': 6, 'types': ['RAG_ONLY']},
            '解释': {'weight': 6, 'types': ['RAG_ONLY']},
            
            # 复合查询关键词
            '比较': {'weight': 5, 'types': ['PARALLEL', 'COMPLEX']},
            '对比': {'weight': 5, 'types': ['PARALLEL', 'COMPLEX']},
            '分析': {'weight': 4, 'types': ['FINANCIAL', 'COMPLEX']},
            '和': {'weight': 3, 'types': ['PARALLEL']},
            '以及': {'weight': 3, 'types': ['PARALLEL']},
            '同时': {'weight': 3, 'types': ['PARALLEL']}
        }
    
    def analyze_query_fields(self, query: str) -> Dict[str, Any]:
        """分析查询中涉及的字段和表"""
        result = {
            'detected_fields': [],
            'detected_tables': set(),
            'chinese_fields': [],
            'suggested_tables': defaultdict(list),
            'field_matches': defaultdict(int)
        }
        
        # 检测中文字段
        for chinese, tables in self.chinese_to_tables.items():
            if chinese in query:
                result['chinese_fields'].append(chinese)
                result['detected_tables'].update(tables)
                for table in tables:
                    result['suggested_tables'][table].append(chinese)
                    result['field_matches'][table] += 1
        
        # 检测英文字段
        for field, tables in self.field_to_tables.items():
            if field.lower() in query.lower():
                result['detected_fields'].append(field)
                result['detected_tables'].update(tables)
                for table in tables:
                    result['suggested_tables'][table].append(field)
                    result['field_matches'][table] += 1
        
        return result
    
    def calculate_route_scores(self, query: str) -> Dict[str, float]:
        """计算各路由类型的得分"""
        scores = defaultdict(float)
        
        # 1. 基于关键词权重计算
        for keyword, info in self.keyword_weights.items():
            if keyword in query:
                weight = info['weight']
                for query_type in info['types']:
                    scores[query_type] += weight
        
        # 2. 基于Schema字段分析
        field_analysis = self.analyze_query_fields(query)
        
        # 根据检测到的表类型调整分数
        for table in field_analysis['detected_tables']:
            for type_name, type_info in self.table_type_mapping.items():
                if table in type_info['tables']:
                    query_type = type_info['query_type']
                    priority = type_info['priority']
                    # 基于匹配字段数量和优先级计算加分
                    field_count = field_analysis['field_matches'][table]
                    scores[query_type] += (priority / 10) * field_count
        
        # 3. 特殊模式检测
        # 检测是否需要多源数据
        multi_source_patterns = [
            (r'.*股价.*公告.*', ['PARALLEL']),
            (r'.*财务.*资金.*', ['COMPLEX']),
            (r'.*比较.*和.*', ['PARALLEL']),
            (r'.*分析.*整体.*', ['COMPLEX'])
        ]
        
        for pattern, types in multi_source_patterns:
            if re.search(pattern, query):
                for query_type in types:
                    scores[query_type] += 5
        
        # 4. 长度和复杂度因素
        query_length = len(query)
        if query_length > 20:  # 较长的查询可能更复杂
            scores['COMPLEX'] += 2
            scores['PARALLEL'] += 1
        
        return dict(scores)
    
    def enhance_routing_decision(self, query: str, llm_decision: Dict[str, Any]) -> Dict[str, Any]:
        """增强LLM的路由决策"""
        # 获取Schema分析结果
        field_analysis = self.analyze_query_fields(query)
        route_scores = self.calculate_route_scores(query)
        
        # 获取LLM的原始决策
        original_type = llm_decision.get('query_type', 'UNKNOWN')
        
        # 找出得分最高的类型
        if route_scores:
            best_type = max(route_scores.items(), key=lambda x: x[1])
            suggested_type = best_type[0]
            confidence = best_type[1]
        else:
            suggested_type = original_type
            confidence = 0
        
        # 构建增强决策
        enhanced_decision = {
            'query_type': original_type,  # 保留原始决策
            'original_decision': llm_decision,
            'schema_analysis': {
                'detected_fields': field_analysis['detected_fields'],
                'chinese_fields': field_analysis['chinese_fields'],
                'detected_tables': list(field_analysis['detected_tables']),
                'suggested_tables': dict(field_analysis['suggested_tables']),
                'route_scores': route_scores,
                'suggested_type': suggested_type,
                'confidence': confidence
            }
        }
        
        # 如果Schema建议与LLM决策不同，且置信度高，考虑覆盖
        if suggested_type != original_type and confidence > 15:
            self.logger.info(f"Schema建议覆盖LLM决策: {original_type} -> {suggested_type} (置信度: {confidence})")
            enhanced_decision['query_type'] = suggested_type
            enhanced_decision['override_reason'] = f"Schema分析置信度高 ({confidence:.1f})"
        
        # 添加额外的元数据
        enhanced_decision['entities'] = llm_decision.get('entities', [])
        enhanced_decision['reasoning'] = llm_decision.get('reasoning', '')
        
        # 如果检测到特定表，添加表建议
        if field_analysis['detected_tables']:
            enhanced_decision['recommended_tables'] = list(field_analysis['detected_tables'])
        
        return enhanced_decision
    
    def get_quick_route(self, query: str) -> Optional[str]:
        """快速路由判断（用于常见模式）"""
        # 定义快速路由模式
        quick_patterns = [
            # 财务分析模式
            (r'.*财务健康.*|.*财务状况.*|.*杜邦分析.*', 'FINANCIAL'),
            (r'.*ROE.*|.*ROA.*|.*净资产收益率.*', 'FINANCIAL'),
            
            # 资金流向模式
            (r'.*资金流向.*|.*主力资金.*|.*超大单.*', 'MONEY_FLOW'),
            (r'.*资金流入.*|.*资金流出.*', 'MONEY_FLOW'),
            
            # 简单查询模式
            (r'^.*最新股价.*$|^.*今天.*价格.*$', 'SQL_ONLY'),
            (r'^.*最新公告.*$|^.*年报.*$|^.*季报.*$', 'RAG_ONLY'),
            
            # 并行查询模式
            (r'.*股价.*公告.*|.*公告.*股价.*', 'PARALLEL'),
            (r'.*比较.*和.*|.*对比.*与.*', 'PARALLEL')
        ]
        
        for pattern, route_type in quick_patterns:
            if re.search(pattern, query, re.IGNORECASE):
                self.logger.info(f"快速路由匹配: {query[:30]}... -> {route_type}")
                return route_type
        
        return None
    
    def validate_routing(self, query: str, route_type: str) -> Tuple[bool, Optional[str]]:
        """验证路由决策的合理性"""
        field_analysis = self.analyze_query_fields(query)
        
        # 验证规则
        validations = []
        
        # 1. 财务查询应该涉及财务表
        if route_type == 'FINANCIAL':
            financial_tables = set(self.table_type_mapping['financial']['tables'])
            if not field_analysis['detected_tables'].intersection(financial_tables):
                validations.append("财务查询但未检测到财务相关字段")
        
        # 2. 资金流向查询应该涉及资金流表
        if route_type == 'MONEY_FLOW':
            money_flow_tables = set(self.table_type_mapping['money_flow']['tables'])
            if not field_analysis['detected_tables'].intersection(money_flow_tables):
                validations.append("资金流向查询但未检测到相关字段")
        
        # 3. RAG查询不应该包含太多数值字段
        if route_type == 'RAG_ONLY':
            if len(field_analysis['detected_fields']) > 3:
                validations.append("RAG查询包含过多数据字段，可能需要SQL")
        
        # 返回验证结果
        is_valid = len(validations) == 0
        warning = "; ".join(validations) if validations else None
        
        return is_valid, warning


# 创建全局实例
schema_router = SchemaEnhancedRouter()


# 便捷函数
def enhance_routing(query: str, llm_decision: Dict[str, Any]) -> Dict[str, Any]:
    """增强路由决策"""
    return schema_router.enhance_routing_decision(query, llm_decision)


def quick_route(query: str) -> Optional[str]:
    """快速路由"""
    return schema_router.get_quick_route(query)


def validate_route(query: str, route_type: str) -> Tuple[bool, Optional[str]]:
    """验证路由"""
    return schema_router.validate_routing(query, route_type)


# 测试代码
if __name__ == "__main__":
    # 测试查询
    test_queries = [
        "分析贵州茅台的财务健康度",
        "茅台最新股价是多少",
        "茅台的资金流向如何",
        "贵州茅台最新公告内容",
        "比较茅台和五粮液的营业收入",
        "分析银行板块的整体表现"
    ]
    
    router = SchemaEnhancedRouter()
    
    for query in test_queries:
        print(f"\n查询: {query}")
        print("-" * 50)
        
        # 分析字段
        field_analysis = router.analyze_query_fields(query)
        print(f"检测到的中文字段: {field_analysis['chinese_fields']}")
        print(f"建议的表: {list(field_analysis['detected_tables'])}")
        
        # 计算路由得分
        scores = router.calculate_route_scores(query)
        print(f"路由得分: {scores}")
        
        # 快速路由
        quick = router.get_quick_route(query)
        if quick:
            print(f"快速路由: {quick}")
        
        # 模拟LLM决策
        mock_llm_decision = {
            'query_type': 'SQL_ONLY',
            'entities': ['600519.SH'],
            'reasoning': '测试'
        }
        
        # 增强决策
        enhanced = router.enhance_routing_decision(query, mock_llm_decision)
        print(f"最终决策: {enhanced['query_type']}")
        
        # 验证
        is_valid, warning = router.validate_routing(query, enhanced['query_type'])
        if not is_valid:
            print(f"验证警告: {warning}")