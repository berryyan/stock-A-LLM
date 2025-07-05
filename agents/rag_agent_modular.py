# 文件路径: E:\PycharmProjects\stock_analysis_system\agents\rag_agent_modular.py

"""
RAG Agent 模块化版本
逐步将现有功能迁移到模块化架构
"""
import sys
import os
from typing import List, Dict, Any, Optional, Tuple
import time
import json
from datetime import datetime

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 导入原始RAG Agent的基础类
from agents.rag_agent import RAGAgent as RAGAgentBase

# 导入新的模块化组件
from utils.parameter_extractor import ParameterExtractor, ExtractedParams
from utils.query_validator import QueryValidator
from utils.result_formatter import ResultFormatter, FormattedResult, ResultType
from utils.error_handler import ErrorHandler, ErrorCategory
from utils.logger import setup_logger
from utils.unified_stock_validator import UnifiedStockValidator
from utils import date_intelligence


class RAGAgentModular(RAGAgentBase):
    """RAG Agent 模块化版本 - 继承并逐步重构"""
    
    def __init__(self, llm_model_name: str = "deepseek-chat"):
        # 初始化父类
        super().__init__(llm_model_name)
        
        # 初始化模块化组件
        self.param_extractor = ParameterExtractor()
        self.query_validator = QueryValidator()
        self.result_formatter = ResultFormatter()
        self.error_handler = ErrorHandler()
        self.stock_validator = UnifiedStockValidator()
        
        self.logger = setup_logger("rag_agent_modular")
        self.logger.info("RAG Agent模块化版本初始化完成")
    
    def query(self, question: str, **kwargs) -> Dict[str, Any]:
        """
        执行RAG查询 - 使用模块化组件增强
        
        Args:
            question: 用户问题
            **kwargs: 其他参数
                - filter: 过滤条件字典
                - top_k: 返回结果数量
                - rerank: 是否重排序
                - return_source: 是否返回原文
                
        Returns:
            查询结果字典
        """
        self.query_count += 1
        start_time = time.time()
        
        try:
            # 1. 输入验证
            if not question or not question.strip():
                return self._handle_error(
                    ValueError("查询内容不能为空"),
                    "EMPTY_INPUT"
                )
            
            question = question.strip()
            self.logger.info(f"收到RAG查询: {question}")
            
            # 2. 使用参数提取器提取参数
            extracted_params = self.param_extractor.extract_all_params(question)
            
            # 3. 日期智能处理
            processed_question = self._apply_date_intelligence(question, extracted_params)
            
            # 4. 构建过滤条件
            filter_dict = self._build_filter(extracted_params, kwargs.get('filter', {}))
            
            # 5. 执行向量搜索
            search_results = self._vector_search_with_fallback(
                processed_question,
                filter_dict,
                kwargs.get('top_k', 5)
            )
            
            if not search_results:
                return self._handle_error(
                    ValueError("未找到相关文档"),
                    "NO_DATA_FOUND"
                )
            
            # 6. 构建上下文
            context = self._build_context(search_results)
            
            # 7. 执行LLM问答
            answer = self._execute_qa(processed_question, context)
            
            # 8. 格式化结果
            formatted_result = self._format_result(
                answer, 
                search_results,
                kwargs.get('return_source', True)
            )
            
            elapsed_time = time.time() - start_time
            self.success_count += 1
            
            return {
                'success': True,
                'result': formatted_result.formatted_text,
                'data': formatted_result.raw_data,
                'metadata': {
                    'doc_count': len(search_results),
                    'query_time': elapsed_time,
                    'filters_applied': bool(filter_dict)
                }
            }
            
        except Exception as e:
            self.logger.error(f"RAG查询失败: {str(e)}")
            return self._handle_error(e, "INTERNAL_ERROR")
    
    def _apply_date_intelligence(self, question: str, params: ExtractedParams) -> str:
        """应用日期智能解析"""
        try:
            # 如果已经提取到日期参数，不需要再次解析
            if params.date or params.date_range:
                return question
            
            # 使用日期智能处理
            processed = date_intelligence.process_query(question)
            if processed != question:
                self.logger.info(f"日期智能解析: {question} -> {processed}")
            
            return processed
            
        except Exception as e:
            self.logger.warning(f"日期智能解析失败: {str(e)}")
            return question
    
    def _build_filter(self, params: ExtractedParams, custom_filter: Dict) -> Dict[str, Any]:
        """构建向量搜索的过滤条件"""
        filter_dict = custom_filter.copy()
        
        # 添加股票过滤
        if params.stocks:
            # 将股票代码转换为多种可能的格式
            stock_filters = []
            for ts_code in params.stocks:
                code = ts_code.split('.')[0]
                stock_filters.extend([ts_code, code])
                
                # 添加股票名称
                if params.stock_names:
                    idx = params.stocks.index(ts_code)
                    if idx < len(params.stock_names):
                        stock_filters.append(params.stock_names[idx])
            
            filter_dict['stock_filter'] = stock_filters
        
        # 添加日期过滤
        if params.date:
            filter_dict['date'] = params.date
        elif params.date_range:
            filter_dict['date_range'] = params.date_range
        
        return filter_dict
    
    def _vector_search_with_fallback(self, query: str, filter_dict: Dict, top_k: int) -> List[Dict]:
        """执行向量搜索，带降级策略"""
        try:
            # 首次尝试：带过滤条件
            if filter_dict:
                self.logger.info(f"使用过滤条件搜索: {filter_dict}")
                results = self._search_documents(query, filter_dict, top_k)
                
                # 如果没有结果，尝试放松过滤条件
                if not results and 'stock_filter' in filter_dict:
                    self.logger.info("放松过滤条件重试...")
                    relaxed_filter = filter_dict.copy()
                    del relaxed_filter['stock_filter']
                    results = self._search_documents(query, relaxed_filter, top_k)
            else:
                # 无过滤条件直接搜索
                results = self._search_documents(query, {}, top_k)
            
            return results
            
        except Exception as e:
            self.logger.error(f"向量搜索失败: {str(e)}")
            return []
    
    def _search_documents(self, query: str, filter_dict: Dict, top_k: int) -> List[Dict]:
        """执行实际的文档搜索"""
        try:
            # 生成查询向量
            query_vector = self.embedding_model.encode([query])[0].tolist()
            
            # 执行向量搜索
            results = self.milvus.search(
                query_vectors=[query_vector],
                top_k=top_k,
                filter_expr=self._build_milvus_expr(filter_dict) if filter_dict else None
            )
            
            if results and results[0]:
                # 使用父类的_extract_documents方法处理搜索结果
                return self._extract_documents(results[0])
            
            return []
            
        except Exception as e:
            self.logger.error(f"文档搜索失败: {str(e)}")
            return []
    
    def _build_milvus_expr(self, filter_dict: Dict) -> str:
        """构建Milvus过滤表达式"""
        expressions = []
        
        # 股票过滤 - 修正字段名
        if 'stock_filter' in filter_dict:
            stock_conditions = []
            for stock in filter_dict['stock_filter']:
                # 只使用实际存在的字段 ts_code
                stock_conditions.append(f'ts_code == "{stock}"')
            if stock_conditions:
                expressions.append(f"({' or '.join(stock_conditions)})")
        
        # 日期过滤 - 修正字段名
        if 'date' in filter_dict:
            expressions.append(f'ann_date == "{filter_dict["date"]}"')
        elif 'date_range' in filter_dict:
            start, end = filter_dict['date_range']
            expressions.append(f'ann_date >= "{start}" and ann_date <= "{end}"')
        
        return ' and '.join(expressions) if expressions else ""
    
    def _execute_qa(self, question: str, context: str) -> str:
        """执行问答"""
        try:
            # 使用现有的qa_chain
            result = self.qa_chain.invoke({
                "context": context,
                "question": question,
                "chat_history": ""  # 暂时不使用历史记录
            })
            
            return result
            
        except Exception as e:
            self.logger.error(f"QA执行失败: {str(e)}")
            return "抱歉，处理您的问题时出现错误。"
    
    def _format_result(self, answer: str, documents: List[Dict], return_source: bool) -> FormattedResult:
        """格式化查询结果"""
        try:
            # 构建结果数据
            result_data = {
                "answer": answer,
                "document_count": len(documents)
            }
            
            # 如果需要返回原文
            if return_source and documents:
                sources = []
                for i, doc in enumerate(documents[:3]):  # 只显示前3个
                    # 文档已经被_extract_documents处理成字典格式
                    source = {
                        "title": doc.get('title', '未知标题'),
                        "date": doc.get('ann_date', '未知日期'),
                        "stock": doc.get('ts_code', ''),
                        "excerpt": doc.get('text', '')[:200] + "..." if doc.get('text') else "..."
                    }
                    sources.append(source)
                
                result_data["sources"] = sources
            
            # 使用结果格式化器
            return self.result_formatter.format_rag_result(answer, result_data)
            
        except Exception as e:
            self.logger.error(f"结果格式化失败: {str(e)}")
            # 降级返回
            return FormattedResult(
                result_type=ResultType.TEXT,
                formatted_text=answer,
                raw_data={"answer": answer}
            )
    
    def _handle_error(self, error: Exception, error_code: str) -> Dict[str, Any]:
        """处理错误"""
        error_info = self.error_handler.handle_error(error, error_code)
        
        return {
            'success': False,
            'error': error_info.user_message,
            'suggestion': error_info.suggestion,
            'details': error_info.details if self.error_handler.debug_mode else None
        }
    
    def _build_context(self, documents: List[Dict]) -> str:
        """构建上下文 - 调用父类的_format_context方法"""
        # 文档已经被_extract_documents处理过，直接使用
        return super()._format_context(documents)