#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Concept Agent - 概念股分析专家
基于多源数据融合的概念股智能发现和分析系统

主要功能：
1. 概念识别：支持关键词、概念查询、新闻文本等多种输入
2. 智能匹配：通过LLM扩展相关概念，提高查全率
3. 多维评分：概念关联度(40%) + 资金流向(30%) + 技术形态(30%)
4. 专业输出：生成包含详细评分和分析的投资报告
"""

import logging
import traceback
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta

# 添加项目根目录到Python路径
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# 复用公共模块
from utils.parameter_extractor import ParameterExtractor
from utils.unified_stock_validator import UnifiedStockValidator
from utils.date_intelligence import DateIntelligenceModule as DateIntelligence
from utils.agent_response import success as create_success_response, error as create_error_response
from utils.error_handler import ErrorHandler
from utils.result_formatter import ResultFormatter

# 概念专用模块
from utils.concept.concept_matcher_v2 import ConceptMatcherV2
from utils.concept.concept_data_collector import ConceptDataCollector
from utils.concept.concept_scorer_v2 import ConceptScorerV2  # 使用V2版本
from utils.concept.scoring_config import ScoringConfig
from utils.concept.technical_collector import TechnicalCollector
from utils.concept.money_flow_collector import MoneyFlowCollector

# LangChain
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

# 数据库连接
from database.mysql_connector import MySQLConnector

# 配置
from config.settings import settings

logger = logging.getLogger(__name__)


class ConceptAgent:
    """概念股分析Agent"""
    
    def __init__(self):
        """初始化Concept Agent"""
        # 初始化基础组件
        self.parameter_extractor = ParameterExtractor()
        self.stock_validator = UnifiedStockValidator()
        self.date_intelligence = DateIntelligence()
        self.error_handler = ErrorHandler()
        self.result_formatter = ResultFormatter()
        
        # 初始化概念专用组件
        self.concept_matcher = ConceptMatcherV2()
        self.data_collector = ConceptDataCollector()
        self.concept_scorer = ConceptScorerV2()  # 使用V2版本
        self.scoring_config = ScoringConfig()
        
        # 初始化数据采集器
        self.technical_collector = TechnicalCollector()
        self.money_flow_collector = MoneyFlowCollector()
        
        # 初始化LLM
        self._init_llm()
        
        # 初始化数据库连接
        self.db_connector = MySQLConnector()
        
        logger.info("Concept Agent初始化完成")
    
    def _init_llm(self):
        """初始化LLM"""
        try:
            self.llm = ChatOpenAI(
                model="deepseek-chat",
                temperature=0.3,  # 概念分析需要一定创造性
                max_tokens=4000,
                api_key=settings.DEEPSEEK_API_KEY,
                base_url=settings.DEEPSEEK_BASE_URL
            )
            logger.info("LLM初始化成功")
        except Exception as e:
            logger.error(f"LLM初始化失败: {str(e)}")
            raise
    
    def process_query(self, query: str) -> Dict[str, Any]:
        """
        处理概念股查询
        
        Args:
            query: 用户查询，支持三种输入类型：
                  1. 关键词输入："充电宝"
                  2. 概念查询："固态电池概念股有哪些？"
                  3. 新闻文本：长段落政策新闻分析
        
        Returns:
            标准化的响应结果
        """
        try:
            # 1. 参数提取和输入类型识别
            query_type, concepts = self._extract_query_info(query)
            
            if not concepts:
                return create_error_response(
                    error_msg="未能识别出有效的概念关键词",
                    error_code="INVALID_CONCEPT"
                )
            
            logger.info(f"识别到查询类型: {query_type}, 概念关键词: {concepts}")
            
            # 2. 概念扩展（通过LLM）
            # 这是LLM的另一次介入：扩展相关概念
            expanded_concepts = self.concept_matcher.expand_concepts(concepts)
            logger.info(f"扩展后的概念: {expanded_concepts}")
            
            # 3. 数据采集
            # 3.1 获取概念相关股票
            concept_stocks = self._get_concept_stocks(expanded_concepts)
            
            if not concept_stocks:
                return create_error_response(
                    error_msg=f"未找到与'{', '.join(concepts)}'相关的概念股",
                    error_code="NO_STOCKS_FOUND"
                )
            
            logger.info(f"找到 {len(concept_stocks)} 只相关概念股")
            
            # 3.2 获取技术指标和资金流向数据
            logger.info(f"开始采集 {len(concept_stocks)} 只股票的技术指标和资金流向数据")
            
            # 提取股票代码列表
            stock_codes = [stock['ts_code'] for stock in concept_stocks]
            
            # 获取技术指标数据
            try:
                technical_data = self.technical_collector.get_latest_technical_indicators(stock_codes)
                logger.info(f"成功获取 {len(technical_data)} 只股票的技术指标数据")
            except Exception as e:
                logger.error(f"获取技术指标数据失败: {str(e)}")
                technical_data = {}
            
            # 获取资金流向数据
            try:
                money_flow_data = self.money_flow_collector.get_batch_money_flow(stock_codes, days=5)
                logger.info(f"成功获取 {len(money_flow_data)} 只股票的资金流向数据")
            except Exception as e:
                logger.error(f"获取资金流向数据失败: {str(e)}")
                money_flow_data = {}
            
            # 4. 评分计算（使用新的证据系统）
            scored_stocks = self.concept_scorer.calculate_scores_with_evidence(
                concept_stocks,
                technical_data,
                money_flow_data,
                weights={'evidence': 1.0, 'technical': 0.0, 'money_flow': 0.0}  # 完全基于证据
            )
            
            # 5. 生成分析报告
            if query_type == 'news':
                # 新闻文本分析需要额外的LLM分析
                report = self._generate_news_analysis_report(
                    query, 
                    scored_stocks, 
                    expanded_concepts
                )
            else:
                # 普通概念查询
                report = self._generate_concept_report(
                    concepts,
                    scored_stocks,
                    expanded_concepts
                )
            
            # 6. 格式化输出
            formatted_result = self._format_result(scored_stocks, report)
            
            return create_success_response(
                data=formatted_result,
                metadata={
                    "query_type": query_type,
                    "original_concepts": concepts,
                    "expanded_concepts": expanded_concepts,
                    "stock_count": len(scored_stocks),
                    "data_sources": ["同花顺", "东财", "开盘啦"]
                }
            )
            
        except Exception as e:
            logger.error(f"处理查询时出错: {str(e)}")
            logger.error(traceback.format_exc())
            
            error_info = self.error_handler.handle_error(e)
            return create_error_response(
                error_msg=error_info.user_message,
                error_code=error_info.error_code,
                original_error=str(e)
            )
    
    def _extract_query_info(self, query: str) -> tuple[str, List[str]]:
        """
        提取查询信息和识别查询类型
        
        Returns:
            (query_type, concepts)
            query_type: 'keyword' | 'concept_query' | 'news'
            concepts: 提取出的概念关键词列表
        """
        # 去除触发词
        cleaned_query = query.replace("概念股分析：", "").strip()
        
        # 判断查询类型
        if len(cleaned_query) > 200:
            # 长文本视为新闻分析
            query_type = 'news'
        elif any(word in cleaned_query for word in ['有哪些', '相关', '概念股', '板块']):
            # 包含查询词的视为概念查询
            query_type = 'concept_query'
        else:
            # 简单关键词
            query_type = 'keyword'
        
        # 提取概念关键词 - 使用ConceptMatcherV2
        # 这是LLM第一次介入的地方
        concepts = self.concept_matcher.extract_concepts(cleaned_query)
        
        return query_type, concepts
    
    def _extract_concepts_from_news(self, news_text: str) -> List[str]:
        """从新闻文本中提取概念关键词"""
        prompt = ChatPromptTemplate.from_messages([
            ("system", """你是一个专业的金融概念提取专家。
从给定的新闻文本中提取与股票投资相关的概念关键词。

要求：
1. 只提取与股票市场相关的概念
2. 优先提取行业、技术、政策相关概念
3. 返回格式：用逗号分隔的关键词列表
4. 最多返回5个最相关的概念"""),
            ("user", "{news_text}")
        ])
        
        chain = prompt | self.llm | StrOutputParser()
        
        try:
            result = chain.invoke({"news_text": news_text})
            concepts = [c.strip() for c in result.split(',') if c.strip()]
            return concepts[:5]  # 最多5个
        except Exception as e:
            logger.error(f"提取新闻概念失败: {str(e)}")
            # 降级到简单提取
            return self._simple_concept_extraction(news_text)
    
    def _simple_concept_extraction(self, text: str) -> List[str]:
        """简单的概念提取（基于规则）"""
        # 移除常见的查询词
        remove_words = ['概念股', '有哪些', '相关', '板块', '个股', '哪些', '？', '?']
        cleaned_text = text
        for word in remove_words:
            cleaned_text = cleaned_text.replace(word, '')
        
        # 简单分词（这里可以使用jieba等分词工具优化）
        concepts = [w.strip() for w in cleaned_text.split() if len(w.strip()) > 1]
        
        return concepts
    
    def _get_concept_stocks(self, concepts: List[str]) -> List[Dict[str, Any]]:
        """
        获取概念相关的股票
        使用ConceptMatcherV2进行智能概念匹配
        
        Args:
            concepts: 概念关键词列表
            
        Returns:
            股票列表
        """
        # 1. 使用ConceptMatcherV2进行概念匹配
        # 这是LLM第二次介入：将用户概念匹配到三大数据源的实际概念
        matched_concepts = self.concept_matcher.match_concepts(concepts)
        
        logger.info(f"概念匹配结果: 同花顺{len(matched_concepts['THS'])}个, "
                   f"东财{len(matched_concepts['DC'])}个, 开盘啦{len(matched_concepts['KPL'])}个")
        
        # 2. 收集所有匹配的概念名称
        all_matched_names = []
        all_matched_names.extend(matched_concepts['THS'])
        all_matched_names.extend(matched_concepts['DC'])
        all_matched_names.extend(matched_concepts['KPL'])
        
        if not all_matched_names:
            logger.warning(f"未找到匹配的概念: {concepts}")
            return []
        
        # 3. 使用DataCollector获取概念股
        # 这会自动从三大数据源获取数据并合并
        concept_stocks = self.data_collector.get_concept_stocks(all_matched_names)
        
        logger.info(f"获取到 {len(concept_stocks)} 只概念相关股票")
        
        # 4. 添加匹配来源信息
        for stock in concept_stocks:
            stock['matched_sources'] = {
                'THS': any(c in stock.get('concepts', []) for c in matched_concepts['THS']),
                'DC': any(c in stock.get('concepts', []) for c in matched_concepts['DC']),
                'KPL': any(c in stock.get('concepts', []) for c in matched_concepts['KPL'])
            }
        
        return concept_stocks
    
    def _generate_concept_report(
        self, 
        concepts: List[str], 
        scored_stocks: List[Dict],
        expanded_concepts: List[str]
    ) -> str:
        """生成概念股分析报告"""
        prompt = ChatPromptTemplate.from_messages([
            ("system", """你是一个专业的股票分析师，擅长概念股分析。
基于提供的概念股评分数据，生成一份专业的分析报告。

报告要求：
1. 概述：简要说明查询的概念和找到的相关股票数量
2. 核心推荐：基于评分推荐TOP5股票，说明推荐理由
3. 风险提示：说明概念投资的风险
4. 投资建议：给出具体的操作建议

注意：
- 使用专业但易懂的语言
- 重点关注高分股票的投资价值
- 必须包含风险提示"""),
            ("user", """查询概念：{concepts}
扩展概念：{expanded_concepts}
评分结果（前20）：
{scored_stocks}

请生成分析报告。""")
        ])
        
        chain = prompt | self.llm | StrOutputParser()
        
        # 准备数据
        top_stocks = scored_stocks[:20]
        stocks_str = self._format_stocks_for_llm(top_stocks)
        
        report = chain.invoke({
            "concepts": ', '.join(concepts),
            "expanded_concepts": ', '.join(expanded_concepts),
            "scored_stocks": stocks_str
        })
        
        return report
    
    def _generate_news_analysis_report(
        self,
        news_text: str,
        scored_stocks: List[Dict],
        expanded_concepts: List[str]
    ) -> str:
        """生成新闻相关的概念股分析报告"""
        prompt = ChatPromptTemplate.from_messages([
            ("system", """你是一个专业的股票分析师，擅长解读政策和新闻对股市的影响。
基于提供的新闻内容和相关概念股数据，生成投资分析报告。

报告要求：
1. 新闻解读：简要总结新闻要点和对市场的影响
2. 受益板块：分析哪些概念板块将受益
3. 核心标的：推荐最受益的个股（基于评分）
4. 投资策略：短期和中长期的操作建议
5. 风险提示：相关风险和注意事项"""),
            ("user", """新闻内容（摘要）：
{news_summary}

相关概念：{concepts}
评分前20股票：
{scored_stocks}

请生成分析报告。""")
        ])
        
        chain = prompt | self.llm | StrOutputParser()
        
        # 新闻摘要（如果太长）
        news_summary = news_text[:500] + "..." if len(news_text) > 500 else news_text
        
        report = chain.invoke({
            "news_summary": news_summary,
            "concepts": ', '.join(expanded_concepts),
            "scored_stocks": self._format_stocks_for_llm(scored_stocks[:20])
        })
        
        return report
    
    def _format_stocks_for_llm(self, stocks: List[Dict]) -> str:
        """格式化股票数据供LLM使用"""
        lines = []
        for i, stock in enumerate(stocks, 1):
            line = (f"{i}. {stock['name']}({stock['ts_code']}) "
                   f"总分:{stock['total_score']:.1f} "
                   f"概念关联:{stock['concept_score']:.1f} "
                   f"资金流向:{stock['money_score']:.1f} "
                   f"技术形态:{stock['technical_score']:.1f}")
            lines.append(line)
        
        return '\n'.join(lines)
    
    def _format_result(self, scored_stocks: List[Dict], report: str) -> str:
        """格式化最终输出结果（包含证据）"""
        # 生成股票评分表格
        headers = ["股票代码", "股票名称", "关联强度", "总分", "软件收录", "财报证据", "互动平台", "公告证据"]
        rows = []
        
        for stock in scored_stocks[:30]:  # 显示前30只
            evidence_scores = stock.get('evidence_scores', {})
            rows.append([
                stock['ts_code'],
                stock['name'],
                stock.get('relevance_level', ''),
                f"{stock['total_score']:.0f}/100",
                f"{evidence_scores.get('software', 0):.0f}/40",
                f"{evidence_scores.get('report', 0):.0f}/30",
                f"{evidence_scores.get('interaction', 0):.0f}/20",
                f"{evidence_scores.get('announcement', 0):.0f}/10"
            ])
        
        # 使用result_formatter生成表格
        if rows:
            table = self.result_formatter.format_table(
                headers,
                rows,
                title="概念股关联度评分（基于事实证据）"
            )
        else:
            table = "暂无数据"
        
        # 添加前5只股票的详细证据
        evidence_details = []
        for stock in scored_stocks[:5]:
            if stock.get('evidence_list'):
                evidence_report = self.concept_scorer.format_evidence_report(stock)
                evidence_details.append(evidence_report)
        
        # 组合最终结果
        if evidence_details:
            evidence_section = "\n\n## 详细证据分析（前5只）\n\n" + "\n\n---\n\n".join(evidence_details)
            result = f"{report}\n\n{table}\n{evidence_section}"
        else:
            result = f"{report}\n\n{table}"
        
        return result
    
    def __del__(self):
        """清理资源"""
        if hasattr(self, 'db_connector'):
            self.db_connector.close()


# 测试入口
if __name__ == "__main__":
    # 配置日志
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # 创建Agent实例
    agent = ConceptAgent()
    
    # 测试查询
    test_queries = [
        "概念股分析：充电宝概念股有哪些？",
        "概念股分析：固态电池概念相关板块有哪些个股现在可以重点关注？"
    ]
    
    for query in test_queries:
        print(f"\n{'='*80}")
        print(f"测试查询: {query}")
        print(f"{'='*80}")
        
        result = agent.process_query(query)
        
        if result.success:
            print(result.data)
        else:
            print(f"错误: {result.error}")