# 文件路径: E:\PycharmProjects\stock_analysis_system\agents\hybrid_agent.py

"""
Hybrid Agent - 智能路由混合查询
自动判断问题类型并路由到合适的Agent处理
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


class QueryType(str, Enum):
    """查询类型枚举"""
    SQL_ONLY = "sql"          # 仅需SQL查询
    RAG_ONLY = "rag"          # 仅需RAG查询
    FINANCIAL = "financial"   # 财务分析查询
    MONEY_FLOW = "money_flow" # 资金流向分析查询
    RANK = "rank"             # 排名分析查询（新增）
    ANNS = "anns"             # 公告查询（新增）
    QA = "qa"                 # 董秘互动查询（新增）
    SQL_FIRST = "sql_first"   # 先SQL后RAG
    RAG_FIRST = "rag_first"   # 先RAG后SQL
    PARALLEL = "parallel"     # 并行查询
    COMPLEX = "complex"       # 复杂查询需要多步骤
    
    # 添加小写别名以便兼容
    sql = "sql"
    rag = "rag"
    financial = "financial"
    money_flow = "money_flow"
    rank = "rank"
    anns = "anns"
    qa = "qa"
    hybrid = "hybrid"
    
    @classmethod
    def _missing_(cls, value):
        """处理未定义的值"""
        if not value:
            return cls.hybrid
            
        # 转换为小写
        value_lower = str(value).lower()
        
        # 映射表
        mappings = {
            'sql_only': cls.SQL_ONLY,
            'rag_only': cls.RAG_ONLY,
            'financial': cls.FINANCIAL,
            'money_flow': cls.MONEY_FLOW,
            'rank': cls.RANK,
            'anns': cls.ANNS,
            'qa': cls.QA,
            'sql': cls.sql,
            'rag': cls.rag,
            'complex': cls.COMPLEX,
            'sql_first': cls.SQL_FIRST,
            'rag_first': cls.RAG_FIRST,
            'parallel': cls.PARALLEL,
            # 保持向后兼容
            'hybrid': cls.COMPLEX,
        }
        
        return mappings.get(value_lower, cls.COMPLEX)


class HybridAgent:
    """混合查询代理 - 智能路由和结果整合"""
    
    def __init__(self):
        self.logger = setup_logger("hybrid_agent")
        
        # 根据配置选择使用哪种Agent
        if USE_MODULAR_AGENTS:
            self.logger.info("使用模块化Agent")
            # 初始化模块化子代理
            self.sql_agent = SQLAgentModular()  # 使用真正的模块化版本
            self.rag_agent = RAGAgentModular()
            self.financial_agent = FinancialAgentModular()
            self.money_flow_agent = MoneyFlowAgentModular()
        else:
            self.logger.info("使用传统Agent")
            # 初始化传统子代理
            self.sql_agent = SQLAgent()
            self.rag_agent = RAGAgent()
            self.financial_agent = FinancialAnalysisAgent()
            self.money_flow_agent = MoneyFlowAgent()
        
        # 初始化路由LLM
        self.router_llm = ChatOpenAI(
            model="deepseek-chat",
            temperature=0,
            api_key=settings.DEEPSEEK_API_KEY,
            base_url=settings.DEEPSEEK_BASE_URL
        )
        
        # 创建路由链
        self.router_chain = self._create_router_chain()
        
        # 创建整合链
        self.integration_chain = self._create_integration_chain()
        
        # 查询模式配置
        self.query_patterns = self._init_query_patterns()
        
        self.logger.info("Hybrid Agent初始化完成")
    
    def _init_query_patterns(self) -> Dict[str, Dict]:
        """初始化查询模式配置"""
        return {
            'sql_patterns': {
                'keywords': ['股价', '市值', '涨跌', '成交量', '市盈率', '总资产', '营收', '净利润', '排名', '统计'],
                'patterns': [
                    r'最新.*价格',
                    r'.*排名前\d+',
                    r'.*最高.*最低',
                    r'比较.*市值'
                ]
            },
            'rag_patterns': {
                'keywords': ['公告', '报告', '说明', '解释', '原因', '计划', '战略', '风险', '优势'],
                'patterns': [
                    r'.*报告.*内容',
                    r'.*公告.*说',
                    r'.*未来.*计划'
                ]
            },
            'financial_patterns': {
                'keywords': ['财务健康', '财务状况', '经营状况', '财务评级', '健康度', '盈利能力', 'ROE', 'ROA', '杜邦分析', '现金流质量', '偿债能力', '多期对比', '增长率', '财务分析', 
                            '投资价值', '投资机会', '投资潜力', '值得投资', '值得买', '财务风险', '风险状况', '经营风险', '风险评估'],
                'patterns': [
                    r'.*财务.*分析',
                    r'.*杜邦.*分析',
                    r'.*现金流.*质量',
                    r'.*财务.*健康',
                    r'.*财务.*评级',
                    r'.*盈利.*能力',
                    r'.*偿债.*能力',
                    r'.*多期.*对比',
                    r'ROE.*分解',
                    r'.*投资价值.*',
                    r'.*投资机会.*',
                    r'.*投资潜力.*',
                    r'.*值得.*投资.*',
                    r'.*值得.*买.*',
                    r'.*财务风险.*',
                    r'.*风险状况.*',
                    r'.*经营风险.*',
                    r'评估.*风险'
                ]
            },
            'money_flow_patterns': {
                'keywords': ['资金流向', '资金流入', '资金流出', '主力资金', '机构资金', '大资金', '超大单', '大单', '中单', '小单', '主力净流入', '主力净流出', '机构行为', '主力行为', '散户', '个人投资者'],
                'patterns': [
                    r'.*资金.*流向',
                    r'.*资金.*流入',
                    r'.*资金.*流出',
                    r'.*主力.*资金',
                    r'.*机构.*资金',
                    r'.*超大单',
                    r'.*大单.*中单.*小单',
                    r'.*主力.*净流入',
                    r'.*主力.*净流出',
                    r'.*机构.*行为',
                    r'.*主力.*行为',
                    r'.*买入.*卖出',
                    r'.*散户.*机构'
                ]
            },
            'rank_patterns': {
                'keywords': ['排行', '排名', '前十', 'TOP', '涨幅榜', '跌幅榜', '龙虎榜', '排行榜'],
                'patterns': [
                    r'.*排行.*',
                    r'.*排名.*',
                    r'.*前\d+.*',
                    r'.*涨跌幅.*排.*',
                    r'.*TOP\d+.*',
                    r'.*榜单.*'
                ]
            },
            'anns_patterns': {
                'keywords': ['公告', '年报', '季报', '半年报', '业绩快报', '业绩预告', '问询函', '回复函'],
                'patterns': [
                    r'.*公告.*列表',
                    r'.*最新.*公告',
                    r'.*年报.*季报',
                    r'.*业绩.*公告',
                    r'.*公告.*时间'
                ]
            },
            'qa_patterns': {
                'keywords': ['董秘', '互动', '问答', '投资者关系', '投资者提问', '公司回复'],
                'patterns': [
                    r'.*董秘.*问.*',
                    r'.*投资者.*问.*',
                    r'.*互动.*平台',
                    r'.*公司.*回复.*'
                ]
            },
            'hybrid_patterns': {
                'keywords': ['综合分析', '全面评估', '详细了解', '深入研究', '综合实力', '各方面表现', '全面对比', '多角度', '多维度'],
                'patterns': [
                    r'.*业绩.*原因',
                    r'.*比较.*分析',
                    r'.*对比.*综合实力',
                    r'.*比较.*各方面',
                    r'.*vs.*全面',
                    r'.*多角度.*对比',
                    r'.*多维度.*比较',
                    r'从.*角度.*对比'
                ]
            }
        }
    
    def _create_router_chain(self):
        """创建路由决策链"""
        router_prompt = PromptTemplate(
            input_variables=["question", "patterns"],
            template="""你是一个查询路由专家，需要分析用户问题并决定使用哪种查询方式。

查询模式说明：
- SQL_ONLY: 查询结构化数据（股价、财务指标、简单排名等）
- RAG_ONLY: 查询文档内容（公告详情、管理层分析等）
- FINANCIAL: 专业财务分析（财务健康度、杜邦分析、现金流质量、投资价值、投资机会、投资潜力、风险评估、财务风险等）
- MONEY_FLOW: 资金流向分析（主力资金、超大单、资金分布等）
- RANK: 专业排名分析（涨跌幅排行、市值排名、板块排名等）
- ANNS: 公告查询（公告列表、年报季报、业绩快报等）
- QA: 董秘互动（投资者提问、公司回复等）
- SQL_FIRST: 先获取数据，再查找相关解释
- RAG_FIRST: 先查找文档，可能需要补充数据
- PARALLEL: 需要同时查询多个数据源（对比分析、综合评估、多股票比较等）
- COMPLEX: 复杂的多步骤查询（仅在无法直接分类时使用）

已知模式：
{patterns}

用户问题：{question}

重要路由规则：
1. 包含"投资价值"、"投资机会"、"投资潜力"、"值得投资"、"值得买"等词 → FINANCIAL
2. 包含"财务风险"、"风险状况"、"经营风险"、"风险评估"等词 → FINANCIAL
3. 包含"对比"、"比较"、"vs"且涉及多个股票 → PARALLEL
4. 包含"综合"、"全面"、"各方面"等词且涉及对比 → PARALLEL
5. 只有当无法明确分类且需要多步骤处理时，才选择 COMPLEX

请分析问题并返回JSON格式的决策：
{{
    "query_type": "选择一个查询类型",
    "reasoning": "决策理由",
    "sql_needed": true/false,
    "rag_needed": true/false,
    "entities": ["识别出的实体，如公司代码"],
    "time_range": "识别出的时间范围",
    "metrics": ["需要查询的指标"]
}}

决策："""
        )
        
        return router_prompt | self.router_llm | StrOutputParser()
    
    def _create_integration_chain(self):
        """创建结果整合链"""
        integration_prompt = PromptTemplate(
            input_variables=["question", "sql_result", "rag_result"],
            template="""你是一个专业的股票分析师，请整合以下查询结果，为用户提供完整的答案。

用户问题：{question}

数据查询结果：
{sql_result}

文档查询结果：
{rag_result}

请提供：
1. 直接回答用户问题
2. 整合数据和文档信息
3. 提供有价值的见解
4. 使用清晰的格式展示

整合答案："""
        )
        
        return integration_prompt | self.router_llm | StrOutputParser()
    
    def query(self, question: str, context: Optional[Dict] = None) -> Dict[str, Any]:
        """
        执行混合查询
        
        Args:
            question: 用户问题
            context: 上下文信息（如已知的公司代码等）
            
        Returns:
            查询结果
        """
        # 输入验证
        if not question or not question.strip():
            return {
                'success': False,
                'error': '查询内容不能为空',
                'type': 'hybrid_query'
            }
        
        # 检查无效输入（纯特殊字符）
        stripped = question.strip()
        if self._is_invalid_input(stripped):
            return {
                'success': False,
                'error': '查询内容无效，请输入有意义的问题',
                'type': 'hybrid_query'
            }
        
        try:
            self.logger.info(f"接收查询: {question}")
            start_time = datetime.now()
            
            # 路由决策
            routing_decision = self._route_query(question)
            self.logger.info(f"路由决策: {routing_decision['query_type']}")
            
            # 记录路由决策到监控器
            query_id = routing_monitor.record_routing_decision(question, routing_decision)
            
            # 2. 根据决策执行查询
            query_type = QueryType(routing_decision['query_type'])
            self.logger.info(f"解析后的查询类型: {query_type}, 原始决策: {routing_decision['query_type']}")
            
            # 执行查询并记录结果
            result = None
            error_msg = None
            
            try:
                if query_type == QueryType.SQL_ONLY:
                    result = self._handle_sql_only(question, routing_decision)
            
                elif query_type == QueryType.RAG_ONLY:
                    result = self._handle_rag_only(question, routing_decision)
                
                elif query_type == QueryType.FINANCIAL:
                    result = self._handle_financial_analysis(question, routing_decision)
                
                elif query_type == QueryType.MONEY_FLOW:
                    result = self._handle_money_flow_analysis(question, routing_decision)
                
                elif query_type == QueryType.RANK:
                    result = self._handle_rank(question, routing_decision)
                
                elif query_type == QueryType.ANNS:
                    result = self._handle_anns(question, routing_decision)
                
                elif query_type == QueryType.QA:
                    result = self._handle_qa(question, routing_decision)
                
                elif query_type == QueryType.SQL_FIRST:
                    result = self._handle_sql_first(question, routing_decision)
                
                elif query_type == QueryType.RAG_FIRST:
                    result = self._handle_rag_first(question, routing_decision)
                
                elif query_type == QueryType.PARALLEL:
                    result = self._handle_parallel(question, routing_decision)
                
                elif query_type == QueryType.COMPLEX:
                    result = self._handle_complex(question, routing_decision)
                
                else:
                    raise ValueError(f"未知的查询类型: {query_type}")
                
                # 记录成功结果到监控器
                response_time = (datetime.now() - start_time).total_seconds()
                routing_monitor.record_query_result(query_id, True, response_time)
                
                return result
                
            except Exception as e:
                # 记录查询执行错误
                error_msg = str(e)
                response_time = (datetime.now() - start_time).total_seconds()
                routing_monitor.record_query_result(query_id, False, response_time, error_msg)
                raise
                
        except Exception as e:
            self.logger.error(f"混合查询失败: {e}")
            error_msg = str(e)
            
            # 记录失败结果到监控器
            if 'query_id' in locals():
                response_time = (datetime.now() - start_time).total_seconds()
                routing_monitor.record_query_result(query_id, False, response_time, error_msg)
            
            return {
                'success': False,
                'question': question,
                'error': error_msg,
                'type': 'hybrid_query'
            }
    
    def _is_invalid_input(self, question: str) -> bool:
        """检查输入是否无效（纯特殊字符或无意义内容）"""
        # 移除所有空白字符
        cleaned = ''.join(question.split())
        
        # 检查是否只包含特殊字符
        if not cleaned:
            return True
            
        # 检查是否只包含标点符号和特殊字符
        import string
        special_chars = string.punctuation + '！？。，、；：""''（）【】《》「」『』〈〉〔〕｛｝［］'
        if all(c in special_chars for c in cleaned):
            return True
            
        # 检查是否包含至少一个中文字符或字母数字
        has_valid_char = any(
            '\u4e00' <= c <= '\u9fff' or  # 中文字符
            c.isalnum()  # 字母或数字
            for c in cleaned
        )
        
        return not has_valid_char
    
    def _check_trigger_words(self, question: str) -> Optional[str]:
        """检测触发词并返回对应的查询类型"""
        # 从配置文件获取触发词映射
        trigger_mapping = routing_config.TRIGGER_WORDS
        
        for trigger, query_type_str in trigger_mapping.items():
            if question.startswith(trigger):
                self.logger.info(f"检测到触发词: {trigger} -> {query_type_str}")
                return query_type_str
        
        return None
    
    def _route_query(self, question: str) -> Dict[str, Any]:
        """路由查询到合适的处理器"""
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
                    
                    if len(query_types) > 1:
                        self.logger.info(f"检测到复合查询，需要并行处理: {query_types}")
                        return {
                            'query_type': 'PARALLEL',
                            'reasoning': '复合查询需要并行处理',
                            'entities': self._extract_entities(question),
                            'time_range': self._extract_time_range(question),
                            'metrics': self._extract_metrics(question),
                            'composite_parts': composite_parts,
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
            
            # 其次尝试Schema快速路由
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
            
            # 使用LLM进行智能路由
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
    
    def _rule_based_routing(self, question: str) -> Dict[str, Any]:
        """基于规则的路由（降级方案）"""
        sql_score = 0
        rag_score = 0
        financial_score = 0
        money_flow_score = 0
        rank_score = 0
        anns_score = 0
        qa_score = 0
        
        # 关键词匹配
        for keyword in self.query_patterns['sql_patterns']['keywords']:
            if keyword in question:
                sql_score += 1
        
        for keyword in self.query_patterns['rag_patterns']['keywords']:
            if keyword in question:
                rag_score += 1
        
        for keyword in self.query_patterns['financial_patterns']['keywords']:
            if keyword in question:
                financial_score += 2  # 财务分析关键词权重更高
        
        for keyword in self.query_patterns['money_flow_patterns']['keywords']:
            if keyword in question:
                money_flow_score += 2  # 资金流向关键词权重更高
        
        for keyword in self.query_patterns['rank_patterns']['keywords']:
            if keyword in question:
                rank_score += 2  # 排名分析关键词权重更高
        
        for keyword in self.query_patterns['anns_patterns']['keywords']:
            if keyword in question:
                anns_score += 1
        
        for keyword in self.query_patterns['qa_patterns']['keywords']:
            if keyword in question:
                qa_score += 2  # 董秘互动关键词权重更高
        
        # 模式匹配
        for pattern in self.query_patterns['financial_patterns']['patterns']:
            if re.search(pattern, question):
                financial_score += 3
        
        for pattern in self.query_patterns['money_flow_patterns']['patterns']:
            if re.search(pattern, question):
                money_flow_score += 3
        
        for pattern in self.query_patterns['rank_patterns']['patterns']:
            if re.search(pattern, question):
                rank_score += 3
        
        for pattern in self.query_patterns['anns_patterns']['patterns']:
            if re.search(pattern, question):
                anns_score += 3
        
        for pattern in self.query_patterns['qa_patterns']['patterns']:
            if re.search(pattern, question):
                qa_score += 3
        
        # 决定查询类型（按优先级排序）
        if rank_score > 0:
            query_type = QueryType.RANK.value
        elif qa_score > 0:
            query_type = QueryType.QA.value
        elif anns_score > 0:
            query_type = QueryType.ANNS.value
        elif money_flow_score > 0:
            query_type = QueryType.MONEY_FLOW.value
        elif financial_score > 0:
            query_type = QueryType.FINANCIAL.value
        elif sql_score > 0 and rag_score == 0:
            query_type = QueryType.SQL_ONLY.value
        elif rag_score > 0 and sql_score == 0:
            query_type = QueryType.RAG_ONLY.value
        elif sql_score > rag_score:
            query_type = QueryType.SQL_FIRST.value
        elif rag_score > sql_score:
            query_type = QueryType.RAG_FIRST.value
        else:
            query_type = QueryType.PARALLEL.value
        
        return {
            'query_type': query_type,
            'reasoning': '基于规则匹配',
            'sql_needed': sql_score > 0,
            'rag_needed': rag_score > 0,
            'entities': self._extract_entities(question),
            'time_range': self._extract_time_range(question),
            'metrics': self._extract_metrics(question)
        }
    
    def _handle_sql_only(self, question: str, routing: Dict) -> Dict[str, Any]:
        """处理仅需SQL的查询，增加类型安全检查"""
        try:
            # 调用SQL Agent处理查询
            sql_result = self.sql_agent.query(question)
            
            # 类型安全检查和转换
            if isinstance(sql_result, str):
                # 如果SQL Agent返回字符串，转换为标准格式
                self.logger.warning("SQL Agent返回了字符串，进行格式转换")
                sql_result = {
                    'success': True,
                    'result': sql_result,
                    'sql': None,
                    'error': None
                }
            elif not isinstance(sql_result, dict):
                # 其他非预期类型
                self.logger.error(f"SQL Agent返回了非预期类型: {type(sql_result)}")
                sql_result = {
                    'success': False,
                    'result': None,
                    'error': f"SQL Agent返回了非预期类型: {type(sql_result)}"
                }
            
            # 确保字典包含必要的键
            if 'success' not in sql_result:
                sql_result['success'] = bool(sql_result.get('result'))
            
            # 记录SQL Agent返回的数据结构
            self.logger.debug(f"SQL Agent返回的键: {list(sql_result.keys())}")
            
            # 检查是否成功
            if sql_result.get('success', False):
                # 获取结果内容 - 注意SQL Agent返回的是'result'而不是'answer'
                result_content = sql_result.get('result', '')
                
                # 如果结果为空，记录警告
                if not result_content:
                    self.logger.warning("SQL Agent返回成功但结果为空")
                    
                return {
                    'success': True,
                    'question': question,
                    'answer': result_content,  # 将'result'映射到'answer'
                    'query_type': QueryType.SQL_ONLY.value,
                    'routing': routing,
                    'sources': {'sql': sql_result}
                }
            else:
                return {
                    'success': False,
                    'question': question,
                    'error': sql_result.get('error', 'SQL查询失败'),
                    'query_type': QueryType.SQL_ONLY.value,
                    'routing': routing
                }
                
        except Exception as e:
            self.logger.error(f"处理SQL查询时出错: {e}")
            return {
                'success': False,
                'question': question,
                'error': str(e),
                'query_type': QueryType.SQL_ONLY.value,
                'routing': routing
            }
    def _handle_rag_only(self, question: str, routing: Dict) -> Dict[str, Any]:
        """处理仅需RAG的查询"""
        try:
            # 构建过滤条件
            filters = self._build_rag_filters(routing)
            
            # 直接调用RAG Agent（依赖其内部超时机制）
            self.logger.info(f"开始RAG查询: {question}")
            rag_result = self.rag_agent.query(question, filter=filters)
            self.logger.info(f"RAG查询完成: success={rag_result.get('success', False)}")
            
            if rag_result.get('success', False):
                return {
                    'success': True,
                    'question': question,
                    'answer': rag_result.get('answer', ''),
                    'query_type': QueryType.RAG_ONLY.value,
                    'routing': routing,
                    'sources': {'rag': rag_result}
                }
            else:
                self.logger.warning(f"RAG查询失败: {rag_result.get('error', '未知错误')}")
                return {
                    'success': False,
                    'question': question,
                    'error': rag_result.get('error', 'RAG查询失败'),
                    'query_type': QueryType.RAG_ONLY.value,
                    'routing': routing
                }
                
        except Exception as e:
            self.logger.error(f"RAG查询异常: {e}")
            import traceback
            self.logger.error(f"异常详情: {traceback.format_exc()}")
            return {
                'success': False,
                'question': question,
                'error': str(e),
                'query_type': QueryType.RAG_ONLY.value,
                'routing': routing
            }
    
    def _handle_financial_analysis(self, question: str, routing: Dict) -> Dict[str, Any]:
        """处理财务分析查询"""
        try:
            self.logger.info(f"执行财务分析查询: {question}")
            
            # 直接调用财务分析代理
            financial_result = self.financial_agent.query(question)
            
            if financial_result.get('success', False):
                return {
                    'success': True,
                    'question': question,
                    'answer': financial_result.get('analysis_report', '财务分析完成'),
                    'query_type': QueryType.FINANCIAL.value,
                    'routing': routing,
                    'sources': {
                        'financial': financial_result
                    },
                    'financial_data': financial_result  # 保留完整的财务分析数据
                }
            else:
                return {
                    'success': False,
                    'question': question,
                    'error': financial_result.get('error', '财务分析失败'),
                    'query_type': QueryType.FINANCIAL.value,
                    'routing': routing
                }
                
        except Exception as e:
            self.logger.error(f"财务分析处理失败: {e}")
            return {
                'success': False,
                'question': question,
                'error': str(e),
                'query_type': QueryType.FINANCIAL.value,
                'routing': routing
            }
    
    def _handle_money_flow_analysis(self, question: str, routing: Dict) -> Dict[str, Any]:
        """处理资金流向分析查询"""
        try:
            self.logger.info(f"执行资金流向分析查询: {question}")
            
            # 直接调用资金流向分析代理
            money_flow_result = self.money_flow_agent.query(question)
            
            if money_flow_result.get('success', False):
                return {
                    'success': True,
                    'question': question,
                    'answer': money_flow_result.get('answer', '资金流向分析完成'),
                    'query_type': QueryType.MONEY_FLOW.value,
                    'routing': routing,
                    'sources': {
                        'money_flow': money_flow_result
                    },
                    'money_flow_data': money_flow_result.get('money_flow_data')  # 保留完整的资金流向数据
                }
            else:
                return {
                    'success': False,
                    'question': question,
                    'error': money_flow_result.get('error', '资金流向分析失败'),
                    'query_type': QueryType.MONEY_FLOW.value,
                    'routing': routing
                }
                
        except Exception as e:
            self.logger.error(f"资金流向分析处理失败: {e}")
            return {
                'success': False,
                'question': question,
                'error': str(e),
                'query_type': QueryType.MONEY_FLOW.value,
                'routing': routing
            }
    
    def _handle_sql_first(self, question: str, routing: Dict) -> Dict[str, Any]:
        """先SQL后RAG的查询"""
        # 1. 执行SQL查询
        sql_result = self.sql_agent.query(question)
        
        if not sql_result.get('success', False):
            return sql_result
        
        # 2. 基于SQL结果构建RAG查询
        # 从SQL结果中提取关键信息
        enhanced_question = self._enhance_question_with_sql_result(
            question, sql_result
        )
        
        filters = self._build_rag_filters(routing)
        rag_result = self.rag_agent.query(enhanced_question, filter=filters)
        
        # 3. 整合结果
        if rag_result.get('success', False):
            integrated_answer = self.integration_chain.invoke({
                "question": question,
                "sql_result": json.dumps(sql_result.get('result', sql_result) if isinstance(sql_result, dict) else sql_result, ensure_ascii=False),
                "rag_result": rag_result.get('answer', '')
            })
            
            return {
                'success': True,
                'question': question,
                'answer': integrated_answer,
                'query_type': QueryType.SQL_FIRST.value,
                'routing': routing,
                'sources': {
                    'sql': sql_result,
                    'rag': rag_result
                }
            }
        else:
            # RAG失败，至少返回SQL结果
            return {
                'success': True,
                'question': question,
                'answer': f"基于数据查询结果：\n{sql_result.get('result', sql_result) if isinstance(sql_result, dict) else sql_result}",
                'query_type': QueryType.SQL_FIRST.value,
                'routing': routing,
                'sources': {'sql': sql_result}
            }
    
    def _handle_rag_first(self, question: str, routing: Dict) -> Dict[str, Any]:
        """先RAG后SQL的查询"""
        # 1. 执行RAG查询
        filters = self._build_rag_filters(routing)
        rag_result = self.rag_agent.query(question, filter=filters)
        
        if not rag_result.get('success', False):
            return rag_result
        
        # 2. 分析是否需要补充SQL查询
        if self._needs_sql_supplement(rag_result):
            # 构建补充查询
            sql_question = self._build_supplementary_sql_question(
                question, rag_result
            )
            sql_result = self.sql_agent.query(sql_question)
            
            # 3. 整合结果
            if sql_result.get('success', False):
                integrated_answer = self.integration_chain.invoke({
                    "question": question,
                    "sql_result": json.dumps(sql_result.get('result', sql_result) if isinstance(sql_result, dict) else sql_result, ensure_ascii=False),
                    "rag_result": rag_result.get('answer', '')
                })
                
                return {
                    'success': True,
                    'question': question,
                    'answer': integrated_answer,
                    'query_type': QueryType.RAG_FIRST.value,
                    'routing': routing,
                    'sources': {
                        'rag': rag_result,
                        'sql': sql_result
                    }
                }
        
        # 不需要SQL补充，直接返回RAG结果
        return {
            'success': True,
            'question': question,
            'answer': rag_result.get('answer', ''),
            'query_type': QueryType.RAG_FIRST.value,
            'routing': routing,
            'sources': {'rag': rag_result}
        }
    
    def _handle_parallel(self, question: str, routing: Dict) -> Dict[str, Any]:
        """并行处理SQL和RAG查询"""
        import concurrent.futures
        
        # 并行执行两种查询
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
            # 提交任务
            sql_future = executor.submit(self.sql_agent.query, question)
            
            filters = self._build_rag_filters(routing)
            rag_future = executor.submit(self.rag_agent.query, question, filter=filters)
            
            # 获取结果
            sql_result = sql_future.result()
            rag_result = rag_future.result()
        
        # 整合结果
        sources = {}
        if sql_result.get('success', False):
            sources['sql'] = sql_result
        if rag_result.get('success', False):
            sources['rag'] = rag_result
        
        if sources:
            # 使用LLM整合两个结果
            # 准备整合数据
            sql_data = sql_result.get('result', '无数据') if isinstance(sql_result, dict) else str(sql_result)
            rag_data = rag_result.get('answer', '无文档') if isinstance(rag_result, dict) else str(rag_result)
            
            integrated_answer = self.integration_chain.invoke({
                "question": question,
                "sql_result": json.dumps(sql_data, ensure_ascii=False),
                "rag_result": rag_data
            })
            
            return {
                'success': True,
                'question': question,
                'answer': integrated_answer,
                'query_type': QueryType.PARALLEL.value,
                'routing': routing,
                'sources': sources
            }
        else:
            return {
                'success': False,
                'question': question,
                'error': '并行查询均失败',
                'query_type': QueryType.PARALLEL.value
            }
    
    def _handle_complex(self, question: str, routing: Dict) -> Dict[str, Any]:
        """处理复杂的多步骤查询"""
        # 获取或初始化递归深度
        context = routing.get('context', {})
        recursion_depth = context.get('recursion_depth', 0)
        
        # 检查递归深度限制
        if recursion_depth >= 3:
            self.logger.warning(f"达到最大递归深度限制: {recursion_depth}")
            return {
                'success': False,
                'question': question,
                'error': '查询过于复杂，无法处理',
                'query_type': QueryType.COMPLEX.value
            }
        
        # 复杂查询需要分解为多个子任务
        subtasks = self._decompose_complex_query(question, routing)
        
        # 如果没有有效的子任务或只有一个与原查询相同的子任务，返回错误
        if not subtasks or (len(subtasks) == 1 and subtasks[0]['question'] == question):
            self.logger.warning("无法有效分解复杂查询")
            return {
                'success': False,
                'question': question,
                'error': '无法理解查询内容，请重新描述您的问题',
                'query_type': QueryType.COMPLEX.value
            }
        
        results = []
        for subtask in subtasks:
            # 增加递归深度
            subtask_context = subtask.get('context', {})
            subtask_context['recursion_depth'] = recursion_depth + 1
            subtask['context'] = subtask_context
            
            # 递归调用query处理子任务
            sub_result = self.query(subtask['question'], subtask['context'])
            results.append(sub_result)
        
        # 整合所有子任务结果
        final_answer = self._integrate_complex_results(question, results)
        
        return {
            'success': True,
            'question': question,
            'answer': final_answer,
            'query_type': QueryType.COMPLEX.value,
            'routing': routing,
            'subtasks': results
        }
    
    def _extract_entities(self, question: str) -> List[str]:
        """提取问题中的实体（公司代码等）"""
        entities = []
        
        # 股票代码模式 - 直接识别股票代码
        code_pattern = r'\b\d{6}\.[SH|SZ]{2}\b'
        codes = re.findall(code_pattern, question)
        entities.extend(codes)
        
        # 公司名称映射 - 使用统一的转换函数
        company_mapping = {
            '茅台': '600519.SH',
            '贵州茅台': '600519.SH',
            '五粮液': '000858.SZ',
            '宁德时代': '300750.SZ',
            '比亚迪': '002594.SZ',
            '招商银行': '600036.SH',
            '平安银行': '000001.SZ',
            '万科A': '000002.SZ',
            '万科': '000002.SZ',
            '中国平安': '601318.SH',
            '工商银行': '601398.SH',
            '建设银行': '601939.SH',
            '农业银行': '601288.SH',
            '中国银行': '601988.SH',
            '中石油': '601857.SH',
            '中石化': '600028.SH'
        }
        
        # 精确和模糊匹配公司名称，转换为股票代码
        for name, code in company_mapping.items():
            if name in question and code not in entities:
                entities.append(code)
        
        # 额外的模糊匹配，使用转换函数
        found_any = False
        for name in company_mapping.keys():
            if name in question:
                found_any = True
                break
        
        # 如果没有找到任何匹配的公司名称，尝试提取其他可能的实体并转换
        if not found_any:
            # 查找可能的公司名称（中文字符+可能的公司后缀）
            company_pattern = r'[\u4e00-\u9fff]+(?:股份|有限|集团|银行|科技|电子|医药|能源|地产|保险|证券|基金|投资|控股|实业|发展|建设|工业|贸易|服务|传媒|文化|教育|环保|新能源|生物|化工|机械|汽车|房地产|金融|通信|软件|网络|互联网|电商|物流|交通|航空|海运|港口|钢铁|有色|煤炭|石油|天然气|电力|水务|燃气|食品|饮料|服装|家电|家具|建材|装饰|酒店|旅游|餐饮|零售|超市|百货|药店|医院|养老|地产|物业|园区)?(?:股份有限公司|有限责任公司|有限公司|集团|公司|股份|有限)?'
            potential_companies = re.findall(company_pattern, question)
            
            for company in potential_companies:
                converted_code = self._convert_entity_to_stock_code(company)
                if converted_code and converted_code != company and converted_code not in entities:
                    entities.append(converted_code)
        
        return entities
    
    def _convert_entity_to_stock_code(self, entity: str) -> Optional[str]:
        """将实体（公司名称或代码）转换为标准股票代码"""
        # 使用新的股票代码映射器
        result = convert_to_ts_code(entity)
        
        # 如果映射失败，记录日志并返回原始实体
        if not result:
            self.logger.warning(f"无法转换实体到ts_code: {entity}，保留原始值")
            return entity
            
        return result
    
    def _extract_time_range(self, question: str) -> Optional[str]:
        """提取时间范围"""
        # 年份模式
        year_pattern = r'(\d{4})年'
        year_match = re.search(year_pattern, question)
        
        # 季度模式
        quarter_patterns = {
            '第一季度': 'Q1',
            '第二季度': 'Q2',
            '第三季度': 'Q3',
            '第四季度': 'Q4',
            '一季度': 'Q1',
            '二季度': 'Q2',
            '三季度': 'Q3',
            '四季度': 'Q4'
        }
        
        time_range = None
        if year_match:
            year = year_match.group(1)
            time_range = year
            
            for quarter_text, quarter_code in quarter_patterns.items():
                if quarter_text in question:
                    time_range = f"{year}{quarter_code}"
                    break
        
        # 最近N天
        recent_pattern = r'最近(\d+)天'
        recent_match = re.search(recent_pattern, question)
        if recent_match:
            days = int(recent_match.group(1))
            time_range = f"recent_{days}d"
        
        return time_range
    
    def _extract_metrics(self, question: str) -> List[str]:
        """提取查询指标"""
        metrics = []
        
        metric_keywords = {
            '营收': 'revenue',
            '营业收入': 'revenue',
            '净利润': 'net_profit',
            '总资产': 'total_assets',
            '净资产': 'net_assets',
            '市盈率': 'pe_ratio',
            '市净率': 'pb_ratio',
            '股价': 'price',
            '涨跌幅': 'change_pct'
        }
        
        for keyword, metric in metric_keywords.items():
            if keyword in question:
                metrics.append(metric)
        
        return metrics
    
    def _build_rag_filters(self, routing: Dict) -> Dict[str, Any]:
        """构建RAG查询过滤器"""
        filters = {}
        
        # 添加实体过滤
        if routing.get('entities'):
            # 确保转换为股票代码而不是公司名称
            entities = routing['entities']
            if isinstance(entities, list):
                # 转换所有实体为股票代码
                converted_entities = []
                for entity in entities:
                    converted_entity = self._convert_entity_to_stock_code(entity)
                    if converted_entity:
                        converted_entities.append(converted_entity)
                if converted_entities:
                    if len(converted_entities) == 1:
                        filters['ts_code'] = converted_entities[0]
                    else:
                        filters['ts_code'] = converted_entities
            else:
                # 单个实体
                converted_entity = self._convert_entity_to_stock_code(entities)
                if converted_entity:
                    filters['ts_code'] = converted_entity
        
        # RAG查询的时间过滤策略：宽松模式，避免过度限制
        # 对于描述性时间表达（如"2024年的经营策略"），不添加严格时间过滤
        if routing.get('time_range'):
            time_range = routing['time_range']
            
            # 判断是否为明确的时间查询需求
            if time_range.startswith('recent_'):
                # "最近N天" - 这是明确的时间需求，保留过滤
                days = int(time_range.split('_')[1].replace('d', ''))
                end_date = datetime.now().strftime('%Y%m%d')
                start_date = (datetime.now() - timedelta(days=days)).strftime('%Y%m%d')
                filters['ann_date'] = {'start': start_date, 'end': end_date}
                self.logger.info(f"添加时间过滤: 最近{days}天")
            elif 'Q' in time_range:
                # 季度查询 - 这是明确的时间需求，保留过滤
                year = time_range[:4]
                quarter = time_range[-1]
                filters['ann_date'] = self._get_quarter_date_range(year, quarter)
                self.logger.info(f"添加时间过滤: {year}年第{quarter}季度")
            else:
                # 年度表达 - 对RAG查询采用宽松策略
                clean_time_range = time_range.replace('年', '').replace('月', '').replace('日', '')
                if clean_time_range.isdigit() and len(clean_time_range) == 4:
                    # 对于RAG查询，年度时间表达通常是描述性的，不应该成为严格限制
                    # 因此跳过时间过滤，让语义搜索自然匹配相关时间的内容
                    self.logger.info(f"RAG模式：跳过年度时间过滤 ({clean_time_range}年)，保持语义搜索灵活性")
                    # 注释掉严格的时间过滤
                    # filters['ann_date'] = {'start': f"{clean_time_range}0101", 'end': f"{clean_time_range}1231"}
        else:
            self.logger.info("无时间范围，使用纯语义搜索")
        
        return filters
    
    def _get_quarter_date_range(self, year: str, quarter: str) -> Dict[str, str]:
        """获取季度日期范围"""
        quarter_ranges = {
            '1': {'start': f"{year}0101", 'end': f"{year}0331"},
            '2': {'start': f"{year}0401", 'end': f"{year}0630"},
            '3': {'start': f"{year}0701", 'end': f"{year}0930"},
            '4': {'start': f"{year}1001", 'end': f"{year}1231"}
        }
        return quarter_ranges.get(quarter, {})
    
    def _enhance_question_with_sql_result(self, question: str, sql_result: Dict) -> str:
        """使用SQL结果增强问题"""
        # 简单实现：将SQL结果的关键信息添加到问题中
        result_summary = str(sql_result.get('result', ''))[:200]
        enhanced = f"{question}\n基于以下数据：{result_summary}"
        return enhanced
    
    def _needs_sql_supplement(self, rag_result: Dict) -> bool:
        """判断是否需要SQL补充"""
        # 检查RAG回答中是否提到需要具体数据
        answer = rag_result.get('answer', '')
        need_data_keywords = ['具体数据', '详细数字', '准确数值', '最新价格']
        
        return any(keyword in answer for keyword in need_data_keywords)
    
    def _build_supplementary_sql_question(self, original_question: str, rag_result: Dict) -> str:
        """构建补充的SQL查询问题"""
        # 基于RAG结果构建针对性的SQL查询
        return f"请提供{original_question}相关的具体数据"
    
    def _decompose_complex_query(self, question: str, routing: Dict) -> List[Dict]:
        """分解复杂查询为子任务"""
        # 检查是否已经是子任务（避免递归分解）
        if question.startswith(('获取相关财务数据：', '查找相关分析报告：', '查询')):
            # 已经是子任务，直接返回失败，避免无限递归
            return []
        
        subtasks = []
        
        # 如果问题包含"比较"，分解为多个单独查询
        if '比较' in question:
            entities = routing.get('entities', [])
            for entity in entities:
                subtasks.append({
                    'question': f"查询{entity}的相关信息",
                    'context': {'entity': entity}
                })
        
        # 如果问题包含"分析"，判断具体分析类型
        elif '分析' in question:
            # 检查是否是特定类型的分析，这些应该直接失败，让路由重新判断
            special_analysis_keywords = ['投资价值', '投资潜力', '投资机会', '财务风险', '风险状况', '经营风险']
            if any(keyword in question for keyword in special_analysis_keywords):
                # 这些应该路由到 Financial Agent，不应该在 COMPLEX 处理
                return []
            
            # 其他分析查询，尝试分解
            entities = routing.get('entities', [])
            if entities and len(entities) > 0:
                entity = entities[0]
                # 生成更具体的子任务
                subtasks.extend([
                    {'question': f"{entity}的最新财务数据"},
                    {'question': f"{entity}的年报摘要"}
                ])
            else:
                # 没有实体信息，无法有效分解
                return []
        
        # 处理"对比"、"比较"查询
        elif '对比' in question or '比较' in question or ' vs ' in question.lower():
            # 这类查询应该路由到 PARALLEL，不应该在 COMPLEX 处理
            return []
        
        # 处理"评估"查询
        elif '评估' in question:
            # 评估类查询通常需要专业分析
            return []
        
        # 如果没有生成有效的子任务，返回空列表
        return subtasks if subtasks else []
    
    def _integrate_complex_results(self, question: str, results: List[Dict]) -> str:
        """整合复杂查询的多个结果"""
        # 收集所有成功的结果
        successful_results = [r for r in results if r.get('success')]
        
        if not successful_results:
            return "无法获取相关信息"
        
        # 构建整合提示
        results_text = []
        for i, result in enumerate(successful_results):
            results_text.append(f"子任务{i+1}结果：\n{result.get('answer', '')}")
        
        # 使用LLM整合
        integration_prompt = f"""
基于以下子任务结果，回答用户问题：{question}

{chr(10).join(results_text)}

请提供整合的完整答案：
"""
        
        integrated = self.router_llm.invoke(integration_prompt).content
        return integrated

    def _handle_rank(self, question: str, routing: Dict) -> Dict[str, Any]:
        """处理排名分析查询"""
        try:
            # TODO: 实现Rank Agent后，这里调用rank_agent.query(question)
            # 暂时使用SQL Agent处理排名查询
            self.logger.info("Rank Agent尚未实现，暂时使用SQL Agent处理")
            return self.sql_agent.query(question)
        except Exception as e:
            self.logger.error(f"排名分析失败: {e}")
            return {
                'success': False,
                'error': f"排名分析失败: {str(e)}",
                'type': 'rank_analysis'
            }
    
    def _handle_anns(self, question: str, routing: Dict) -> Dict[str, Any]:
        """处理公告查询"""
        try:
            # TODO: 实现ANNS Agent后，这里调用anns_agent.query(question)
            # 暂时使用SQL Agent查询公告元数据
            self.logger.info("ANNS Agent尚未实现，暂时使用SQL Agent处理")
            return self.sql_agent.query(question)
        except Exception as e:
            self.logger.error(f"公告查询失败: {e}")
            return {
                'success': False,
                'error': f"公告查询失败: {str(e)}",
                'type': 'anns_query'
            }
    
    def _handle_qa(self, question: str, routing: Dict) -> Dict[str, Any]:
        """处理董秘互动查询"""
        try:
            # TODO: 实现QA Agent后，这里调用qa_agent.query(question)
            # 暂时返回未实现提示
            self.logger.info("QA Agent尚未实现")
            return {
                'success': False,
                'error': 'QA Agent功能尚未实现，请等待后续更新',
                'type': 'qa_query'
            }
        except Exception as e:
            self.logger.error(f"董秘互动查询失败: {e}")
            return {
                'success': False,
                'error': f"董秘互动查询失败: {str(e)}",
                'type': 'qa_query'
            }
    
    def _safe_extract_result(self, result: Any, source_type: str) -> str:
        """安全地提取结果内容"""
        try:
            if isinstance(result, dict):
                # 优先级：result > data > answer > 其他
                for key in ['result', 'data', 'answer', 'content']:
                    if key in result and result[key]:
                        return str(result[key])
                # 如果没有找到，返回整个字典的字符串表示
                return json.dumps(result, ensure_ascii=False, indent=2)
            elif isinstance(result, str):
                return result
            elif result is None:
                return f"无{source_type}数据"
            else:
                return str(result)
        except Exception as e:
            self.logger.error(f"提取{source_type}结果时出错: {e}")
            return f"{source_type}数据提取失败"


# 测试代码
    def _is_composite_query(self, question: str) -> bool:
        """判断是否为复合查询"""
        # 复合查询的连接词
        composite_keywords = ['和', '以及', '还有', '同时', '并且', '另外', '以及其', '及其', '及']
        
        # 检查是否包含连接词
        for keyword in composite_keywords:
            if keyword in question:
                # 进一步检查连接词前后是否有实质性内容
                parts = question.split(keyword)
                if len(parts) >= 2 and all(len(p.strip()) > 2 for p in parts):
                    return True
        
        return False
    
    def _analyze_composite_query(self, question: str) -> List[str]:
        """分析复合查询的组成部分"""
        # 复合查询的连接词
        composite_keywords = ['和', '以及', '还有', '同时', '并且', '另外', '以及其', '及其', '及']
        
        # 找到所有连接词的位置
        parts = [question]
        for keyword in composite_keywords:
            new_parts = []
            for part in parts:
                if keyword in part:
                    sub_parts = part.split(keyword)
                    new_parts.extend(sub_parts)
                else:
                    new_parts.append(part)
            parts = new_parts
        
        # 清理和过滤
        cleaned_parts = []
        for part in parts:
            cleaned = part.strip()
            if len(cleaned) > 2:  # 过滤掉太短的片段
                cleaned_parts.append(cleaned)
        
        return cleaned_parts


if __name__ == "__main__":
    print("Hybrid Agent 模块创建成功!")
    print("可以通过以下方式使用：")
    print("from agents.hybrid_agent import HybridAgent")
    print("hybrid_agent = HybridAgent()")
    print("result = hybrid_agent.query('分析贵州茅台2024年的财务表现')")
