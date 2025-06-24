# 文件路径: E:\PycharmProjects\stock_analysis_system\agents\rag_agent.py

"""
RAG Agent - 增强的文档查询代理
基于向量数据库的智能文档问答系统
"""
import sys
import os
from typing import List, Dict, Any, Optional, Tuple
import time
import json
from datetime import datetime

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from langchain.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain.schema.runnable import RunnablePassthrough
from langchain_openai import ChatOpenAI
from langchain.memory import ConversationBufferWindowMemory

from database.milvus_connector import MilvusConnector
from models.embedding_model import EmbeddingModel
from config.settings import settings
from utils.logger import setup_logger
from utils.date_intelligence import date_intelligence


class RAGAgent:
    """RAG查询代理 - 处理基于文档的智能问答"""
    
    def __init__(self, llm_model_name: str = "deepseek-chat"):
        self.logger = setup_logger("rag_agent")
        
        # 初始化组件
        self.milvus = MilvusConnector()
        self.embedding_model = EmbeddingModel()
        
        # 初始化LLM
        self.llm = ChatOpenAI(
            model=llm_model_name,
            temperature=0.7,
            api_key=settings.DEEPSEEK_API_KEY,
            base_url=settings.DEEPSEEK_BASE_URL
        )
        
        # 对话记忆 - 使用现代化的内存管理
        # 注意: 根据LangChain迁移指南，内存功能已被现代化
        # 暂时保留但不在新的agent中使用
        self.memory = None  # 将在未来版本中实现现代化内存管理
        
        # 创建查询链
        self.qa_chain = self._create_qa_chain()
        
        # 创建分析链
        self.analysis_chain = self._create_analysis_chain()
        
        # 初始化统计信息
        self.query_count = 0
        self.success_count = 0
        
        self.logger.info("RAG Agent初始化完成")
    
    def _create_qa_chain(self):
        """创建问答链"""
        qa_prompt = PromptTemplate(
            input_variables=["context", "question", "chat_history"],
            template="""你是一位专业的股票分析师，请基于提供的公司公告内容回答用户的问题。

历史对话：
{chat_history}

相关文档内容：
{context}

用户问题：{question}

请注意：
1. 必须使用中文回答，不要使用英文
2. 回答必须基于提供的文档内容，不要编造信息
3. 如果文档中没有相关信息，请明确说明"根据现有文档，暂未找到相关信息"
4. 涉及财务数据时，请注明数据来源（如具体报告期）
5. 重要结论请用**加粗**标注
6. 数字请使用合适的单位（如亿元、万元）
7. 保持回答简洁明了，突出重点信息

中文回答："""
        )
        
        return qa_prompt | self.llm | StrOutputParser()
    
    def _create_analysis_chain(self):
        """创建分析链"""
        analysis_prompt = PromptTemplate(
            input_variables=["documents", "query", "analysis_type"],
            template="""你是一位专业的股票分析师，请对以下文档进行{analysis_type}分析。

文档内容：
{documents}

分析要求：{query}

请提供：
1. 核心发现（3-5个要点）
2. 详细分析
3. 潜在风险或机会
4. 结论与建议

分析报告："""
        )
        
        return analysis_prompt | self.llm | StrOutputParser()
    
    def query(self, 
             question: str, 
             filters: Optional[Dict[str, Any]] = None,
             top_k: int = 5) -> Dict[str, Any]:
        """
        执行RAG查询
        
        Args:
            question: 用户问题
            filters: 过滤条件 {'ts_code': '600519.SH', 'ann_date': '20250422'}
            top_k: 返回文档数量
            
        Returns:
            查询结果
        """
        # 更新查询统计（包括无效查询）
        self.query_count += 1
        
        # 输入验证
        if not question or not question.strip():
            return {
                'success': False,
                'error': '查询内容不能为空',
                'type': 'rag_query'
            }
        
        try:
            start_time = time.time()
            self.logger.info(f"RAG查询: {question}")
            
            # 0. 智能日期解析（RAG模式：仅提取股票代码，不强制时间过滤）
            self.logger.info("步骤1: 开始智能日期解析（RAG模式）")
            processed_question, parsing_result = date_intelligence.preprocess_question(question)
            
            # RAG查询模式：保持原问题不变，避免时间表达被过度处理
            if processed_question != question:
                self.logger.info(f"RAG模式：保持原问题不变，避免时间过滤干扰")
                processed_question = question  # 对RAG查询，保持原问题的语义完整性
            
            self.logger.info(f"使用问题: {processed_question}")
            
            # 仅提取股票代码用于过滤，不添加严格的时间限制
            if parsing_result.get('stock_code') and not filters:
                filters = {}
                filters['ts_code'] = parsing_result['stock_code']
                self.logger.info(f"从日期解析提取股票代码: {parsing_result['stock_code']}")
            
            # 1. 生成查询向量 (使用处理后的问题)
            self.logger.info("步骤2: 开始生成查询向量")
            try:
                query_vector = self.embedding_model.encode([processed_question])[0].tolist()
                self.logger.info(f"向量生成成功: 维度={len(query_vector)}")
            except Exception as e:
                self.logger.error(f"向量生成失败: {e}")
                raise
            
            # 2. 构建过滤表达式
            self.logger.info("步骤3: 构建过滤表达式")
            filter_expr = self._build_filter_expr(filters)
            self.logger.info(f"过滤表达式: {filter_expr}")
            
            # 3. 向量搜索
            self.logger.info("步骤4: 开始向量搜索")
            try:
                search_results = self.milvus.search(
                    query_vectors=[query_vector],
                    top_k=top_k,
                    filter_expr=filter_expr
                )
                self.logger.info(f"向量搜索完成: 找到{len(search_results[0]) if search_results else 0}个结果")
            except Exception as e:
                self.logger.error(f"向量搜索失败: {e}")
                raise
            
            if not search_results or len(search_results[0]) == 0:
                self.logger.warning("未找到相关文档")
                return {
                    'success': False,
                    'message': '未找到相关文档',
                    'question': question
                }
            
            # 4. 提取文档内容
            self.logger.info("步骤5: 提取文档内容")
            documents = self._extract_documents(search_results[0])
            self.logger.info(f"文档提取完成: {len(documents)}个文档")
            
            # 5. 生成答案
            self.logger.info("步骤6: 生成答案")
            context = self._format_context(documents)
            chat_history = self._get_chat_history()
            
            # 调用QA Chain并智能提取答案
            try:
                self.logger.info("开始调用QA Chain")
                answer = self.qa_chain.invoke({
                    "context": context,
                    "question": question,
                    "chat_history": chat_history
                })
                self.logger.info(f"QA Chain调用成功: 答案长度={len(answer) if answer else 0}")
                
                # 确保答案不为空
                if not answer or not isinstance(answer, str) or answer.strip() == '':
                    self.logger.warning("答案为空，使用默认回复")
                    answer = "抱歉，我无法从提供的文档中找到相关信息来回答您的问题。"
                    
            except Exception as e:
                self.logger.error(f"QA Chain调用失败: {e}", exc_info=True)
                answer = f"生成答案时出错: {str(e)}"
            
            # 6. 保存到记忆 (已现代化，暂时跳过内存保存)
            # TODO: 实现现代化的内存管理
            # if self.memory:
            #     self.memory.save_context(
            #         {"input": question},
            #         {"output": answer}
            #     )
            
            # 更新成功统计
            self.success_count += 1
            
            result = {
                'success': True,
                'question': question,
                'answer': answer,
                'sources': self._format_sources(documents),
                'document_count': len(documents),
                'type': 'rag_query',
                'processing_time': time.time() - start_time
            }
            
            # 如果有日期解析结果，添加到返回信息中
            if parsing_result.get('suggestion'):
                result['date_parsing'] = {
                    'suggestion': parsing_result['suggestion'],
                    'modified_question': parsing_result.get('modified_question'),
                    'parsed_date': parsing_result.get('parsed_date')
                }
            
            return result
            
        except Exception as e:
            self.logger.error(f"RAG查询失败: {e}")
            import traceback
            self.logger.error(f"异常详情: {traceback.format_exc()}")
            return {
                'success': False,
                'question': question,
                'error': str(e),
                'type': 'rag_query',
                'processing_time': time.time() - start_time
            }
    
    def analyze_documents(self,
                         query: str,
                         analysis_type: str = "综合",
                         filters: Optional[Dict[str, Any]] = None,
                         top_k: int = 10) -> Dict[str, Any]:
        """
        对文档进行深度分析
        
        Args:
            query: 分析要求
            analysis_type: 分析类型（综合/财务/风险/比较）
            filters: 过滤条件
            top_k: 文档数量
            
        Returns:
            分析结果
        """
        try:
            self.logger.info(f"文档分析: {query} (类型: {analysis_type})")
            
            # 1. 获取相关文档
            query_vector = self.embedding_model.encode([query])[0].tolist()
            filter_expr = self._build_filter_expr(filters)
            
            search_results = self.milvus.search(
                query_vectors=[query_vector],
                top_k=top_k,
                filter_expr=filter_expr
            )
            
            if not search_results or len(search_results[0]) == 0:
                return {
                    'success': False,
                    'message': '未找到相关文档进行分析'
                }
            
            # 2. 提取并格式化文档
            documents = self._extract_documents(search_results[0])
            formatted_docs = self._format_documents_for_analysis(documents)
            
            # 3. 执行分析
            analysis = self.analysis_chain.invoke({
                "documents": formatted_docs,
                "query": query,
                "analysis_type": analysis_type
            })
            
            return {
                'success': True,
                'query': query,
                'analysis_type': analysis_type,
                'analysis': analysis,
                'document_count': len(documents),
                'sources': self._format_sources(documents),
                'type': 'document_analysis'
            }
            
        except Exception as e:
            self.logger.error(f"文档分析失败: {e}")
            return {
                'success': False,
                'query': query,
                'error': str(e),
                'type': 'document_analysis'
            }
    
    def compare_companies(self,
                         companies: List[str],
                         aspect: str = "财务表现",
                         period: Optional[str] = None) -> Dict[str, Any]:
        """
        比较多家公司
        
        Args:
            companies: 公司代码列表 ['600519.SH', '000858.SZ']
            aspect: 比较维度
            period: 时间段
            
        Returns:
            比较结果
        """
        try:
            self.logger.info(f"比较公司: {companies}, 维度: {aspect}")
            
            # 为每个公司获取文档
            all_documents = []
            company_docs = {}
            
            for company in companies:
                filters = {'ts_code': company}
                if period:
                    filters['ann_date'] = period
                
                query_vector = self.embedding_model.encode([f"{aspect} {company}"])[0].tolist()
                filter_expr = self._build_filter_expr(filters)
                
                results = self.milvus.search(
                    query_vectors=[query_vector],
                    top_k=5,
                    filter_expr=filter_expr
                )
                
                if results and len(results[0]) > 0:
                    docs = self._extract_documents(results[0])
                    company_docs[company] = docs
                    all_documents.extend(docs)
            
            if not all_documents:
                return {
                    'success': False,
                    'message': '未找到相关文档进行比较'
                }
            
            # 执行比较分析
            comparison_prompt = f"比较以下公司的{aspect}：" + ", ".join(companies)
            
            analysis = self.analyze_documents(
                query=comparison_prompt,
                analysis_type="比较",
                top_k=20
            )
            
            return {
                'success': True,
                'companies': companies,
                'aspect': aspect,
                'comparison': analysis.get('analysis', ''),
                'company_documents': {
                    company: len(docs) for company, docs in company_docs.items()
                },
                'type': 'company_comparison'
            }
            
        except Exception as e:
            self.logger.error(f"公司比较失败: {e}")
            return {
                'success': False,
                'error': str(e),
                'type': 'company_comparison'
            }
    
    def _build_filter_expr(self, filters: Optional[Dict[str, Any]]) -> Optional[str]:
        """构建Milvus过滤表达式"""
        if not filters:
            return None
        
        conditions = []
        
        # 股票代码过滤
        if 'ts_code' in filters:
            if isinstance(filters['ts_code'], list):
                codes = ', '.join([f'"{code}"' for code in filters['ts_code']])
                conditions.append(f"ts_code in [{codes}]")
            else:
                conditions.append(f'ts_code == "{filters["ts_code"]}"')
        
        # 日期过滤
        if 'ann_date' in filters:
            date = filters['ann_date']
            if isinstance(date, dict):
                if 'start' in date:
                    conditions.append(f'ann_date >= "{date["start"]}"')
                if 'end' in date:
                    conditions.append(f'ann_date <= "{date["end"]}"')
            else:
                conditions.append(f'ann_date == "{date}"')
        
        # 标题关键词过滤
        if 'title_keywords' in filters:
            # 注意：Milvus的字符串匹配功能有限
            # 这里只是示例，实际可能需要在应用层过滤
            pass
        
        return ' and '.join(conditions) if conditions else None
    
    def _extract_documents(self, search_results) -> List[Dict[str, Any]]:
        """从搜索结果中提取文档"""
        documents = []
        
        for hit in search_results:
            # 使用属性访问而不是get方法
            doc = {
                'text': getattr(hit.entity, 'text', ''),
                'ts_code': getattr(hit.entity, 'ts_code', ''),
                'title': getattr(hit.entity, 'title', ''),
                'ann_date': getattr(hit.entity, 'ann_date', ''),
                'chunk_id': getattr(hit.entity, 'chunk_id', 0),
                'score': hit.distance,
                'metadata': getattr(hit.entity, 'metadata', {})
            }
            documents.append(doc)
        
        return documents
    def _format_context(self, documents: List[Dict[str, Any]]) -> str:
        """格式化文档内容作为上下文"""
        context_parts = []
        
        for i, doc in enumerate(documents):
            context_part = f"""
文档{i+1}:
公司: {doc['ts_code']}
标题: {doc['title']}
日期: {doc['ann_date']}
内容: {doc['text']}
---
"""
            context_parts.append(context_part)
        
        return "\n".join(context_parts)
    
    def _format_documents_for_analysis(self, documents: List[Dict[str, Any]]) -> str:
        """为分析格式化文档"""
        formatted_parts = []
        
        # 按公司分组
        from collections import defaultdict
        company_docs = defaultdict(list)
        
        for doc in documents:
            company_docs[doc['ts_code']].append(doc)
        
        for ts_code, docs in company_docs.items():
            company_part = f"\n【{ts_code}】\n"
            for doc in docs:
                company_part += f"- {doc['title']} ({doc['ann_date']}): {doc['text'][:200]}...\n"
            formatted_parts.append(company_part)
        
        return "\n".join(formatted_parts)
    
    def _format_sources(self, documents: List[Dict[str, Any]]) -> List[Dict[str, str]]:
        """格式化来源信息"""
        sources = []
        seen = set()
        
        for doc in documents:
            source_key = f"{doc['ts_code']}_{doc['title']}_{doc['ann_date']}"
            if source_key not in seen:
                seen.add(source_key)
                sources.append({
                    'ts_code': doc['ts_code'],
                    'title': doc['title'],
                    'ann_date': doc['ann_date']
                })
        
        return sources
    
    def _get_chat_history(self) -> str:
        """获取格式化的对话历史"""
        # 由于内存管理已现代化，暂时返回空字符串
        # TODO: 实现现代化的内存管理
        if self.memory and hasattr(self.memory, 'chat_memory'):
            messages = self.memory.chat_memory.messages
            history_parts = []
            
            for i in range(0, len(messages), 2):
                if i + 1 < len(messages):
                    user_msg = messages[i].content
                    assistant_msg = messages[i + 1].content
                    history_parts.append(f"用户: {user_msg}\n助手: {assistant_msg}")
            
            return "\n\n".join(history_parts) if history_parts else "无历史对话"
        else:
            return "无历史对话"
    
    def clear_memory(self):
        """清除对话记忆"""
        self.memory.clear()
        self.logger.info("对话记忆已清除")
    
    def get_stats(self) -> Dict[str, Any]:
        """获取查询统计信息"""
        return {
            'query_count': self.query_count,
            'success_count': self.success_count,
            'success_rate': self.success_count / self.query_count if self.query_count > 0 else 0.0
        }

    def get_similar_questions(self, question: str, top_k: int = 5) -> List[str]:
        """获取相似的问题建议"""
        # 这里可以基于历史查询或预定义的问题模板
        templates = [
            "{}的财务表现如何？",
            "{}最新的经营情况怎么样？",
            "{}的主要风险有哪些？",
            "{}的竞争优势是什么？",
            "{}的未来发展规划是什么？"
        ]
        
        # 简单的实现：提取关键公司名
        suggestions = []
        if "茅台" in question:
            company = "贵州茅台"
        elif "五粮液" in question:
            company = "五粮液"
        else:
            company = "该公司"
        
        for template in templates:
            suggestions.append(template.format(company))
        
        return suggestions[:top_k]


# 测试代码
if __name__ == "__main__":
    print("RAG Agent 模块创建成功!")
    print("可以通过以下方式使用：")
    print("from agents.rag_agent import RAGAgent")
    print("rag_agent = RAGAgent()")
    print("result = rag_agent.query('贵州茅台2024年第一季度的营收情况如何？')")
