# 文件路径: E:\PycharmProjects\stock_analysis_system\agents\hybrid_agent_fixed.py

"""
Hybrid Agent - 修复版
修复了复合查询路由被模板匹配覆盖的问题
"""
import sys
import os
from typing import Dict, List, Any, Optional, Tuple
import re
from enum import Enum
from datetime import datetime, timedelta
import json

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.sql_agent import SQLAgent
from agents.rag_agent import RAGAgent
from agents.financial_agent import FinancialAnalysisAgent
from agents.money_flow_agent import MoneyFlowAgent

# 导入模块化版本
try:
    from config.modular_settings import USE_MODULAR_AGENTS
    if USE_MODULAR_AGENTS:
        from agents.sql_agent_modular import SQLAgentModular
        from agents.rag_agent_modular import RAGAgentModular
        from agents.financial_agent_modular import FinancialAgentModular
        from agents.money_flow_agent_modular import MoneyFlowAgentModular
except ImportError:
    USE_MODULAR_AGENTS = False
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

from config.settings import settings
from config.routing_config import routing_config
from utils.logger import setup_logger
from utils.stock_code_mapper import convert_to_ts_code
from utils.routing_monitor import routing_monitor
from utils.schema_enhanced_router import schema_router
from utils.query_templates import match_query_template

# 从原版复制所有必要的类和方法
from agents.hybrid_agent import QueryType, HybridAgent


class HybridAgentFixed(HybridAgent):
    """
    修复版的Hybrid Agent
    主要修复：复合查询路由被模板匹配覆盖的问题
    """
    
    def _route_query(self, question: str) -> Dict[str, Any]:
        """
        修复版的路由查询方法
        确保复合查询检测到PARALLEL后直接返回，不被模板匹配覆盖
        """
        try:
            # 0. 首先检查触发词（最高优先级）
            trigger_type = self._check_trigger_words(question)
            if trigger_type:
                return {
                    'query_type': trigger_type,
                    'reasoning': '触发词匹配',
                    'entities': self._extract_entities(question),
                    'time_range': self._extract_time_range(question),
                    'metrics': self._extract_metrics(question),
                    'confidence': 1.0
                }
            
            # 1. 检查是否为复合查询（包含"和"、"以及"等连接词）
            if self._is_composite_query(question):
                # 分析复合查询的组成部分
                composite_parts = self._analyze_composite_query(question)
                if composite_parts and len(composite_parts) > 1:
                    # 检查是否需要不同类型的查询
                    query_types = set()
                    for part in composite_parts:
                        if any(kw in part for kw in ['股价', '价格', '成交量', '涨跌', '市值', 'K线']):
                            query_types.add('SQL')
                        if any(kw in part for kw in ['业务', '战略', '公告', '分析', '前景', '计划']):
                            query_types.add('RAG')
                        if any(kw in part for kw in ['财务', '健康度', 'ROE', '杜邦']):
                            query_types.add('Financial')
                        if any(kw in part for kw in ['资金', '主力', '流向']):
                            query_types.add('MoneyFlow')
                    
                    if len(query_types) > 1:
                        self.logger.info(f"检测到复合查询，需要并行处理: {query_types}")
                        # 🔥 关键修复：直接返回，不再继续执行模板匹配
                        return {
                            'query_type': 'PARALLEL',
                            'reasoning': '复合查询需要并行处理',
                            'entities': self._extract_entities(question),
                            'time_range': self._extract_time_range(question),
                            'metrics': self._extract_metrics(question),
                            'composite_parts': composite_parts,
                            'query_types_needed': list(query_types),
                            'confidence': 0.9
                        }
            
            # 2. 其次尝试模板匹配（次高优先级）
            template_result = match_query_template(question)
            if template_result:
                template, params = template_result
                
                # 检查是否需要覆盖路由目标
                route_type = template.route_type
                if template.name in routing_config.TEMPLATE_ROUTE_OVERRIDE:
                    route_type = routing_config.TEMPLATE_ROUTE_OVERRIDE[template.name]
                    self.logger.info(f"路由覆盖: {template.name} -> {template.route_type} 改为 {route_type}")
                else:
                    self.logger.info(f"使用模板路由: {template.name} -> {route_type}")
                
                # 从模板参数中提取实体
                entities = params.get('entities', [])
                if not entities:
                    entities = self._extract_entities(question)
                
                decision = {
                    'query_type': route_type,
                    'reasoning': f'基于查询模板: {template.name}',
                    'entities': entities,
                    'time_range': params.get('time_range', self._extract_time_range(question)),
                    'metrics': template.required_fields,
                    'template_params': params
                }
                
                return decision
            
            # 3. 尝试Schema快速路由
            quick_route_type = schema_router.get_quick_route(question)
            if quick_route_type:
                self.logger.info(f"使用快速路由: {quick_route_type}")
                decision = {
                    'query_type': quick_route_type,
                    'reasoning': '基于Schema快速路由',
                    'entities': self._extract_entities(question),
                    'time_range': self._extract_time_range(question),
                    'metrics': self._extract_metrics(question)
                }
                
                # 验证路由决策
                is_valid, warning = schema_router.validate_routing(question, quick_route_type)
                if not is_valid:
                    self.logger.warning(f"快速路由验证警告: {warning}")
                
                return decision
            
            # 4. 使用LLM进行智能路由
            patterns_str = json.dumps(self.query_patterns, ensure_ascii=False, indent=2)
            
            result = self.router_chain.invoke({
                "question": question,
                "patterns": patterns_str
            })
            
            # 解析JSON结果
            # 清理可能的markdown代码块标记
            result = result.strip()
            if result.startswith('```'):
                result = result.split('```')[1]
                if result.startswith('json'):
                    result = result[4:]
            
            decision = json.loads(result.strip())
            
            # 补充实体识别
            if 'entities' not in decision:
                decision['entities'] = self._extract_entities(question)
            
            # 使用Schema增强路由决策
            enhanced_decision = schema_router.enhance_routing_decision(question, decision)
            self.logger.info(f"Schema增强后的路由决策: {enhanced_decision['query_type']}")
            
            # 如果Schema建议覆盖了LLM决策，记录原因
            if enhanced_decision.get('override_reason'):
                self.logger.info(f"Schema覆盖原因: {enhanced_decision['override_reason']}")
            
            return enhanced_decision
            
        except Exception as e:
            self.logger.warning(f"路由决策失败，使用规则匹配: {e}")
            # 降级到规则匹配
            return self._rule_based_routing(question)