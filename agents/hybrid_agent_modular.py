# 文件路径: E:\PycharmProjects\stock_analysis_system\agents\hybrid_agent_modular.py

"""
Hybrid Agent 模块化版本 - 智能路由混合查询
使用新的模块化Agent
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

# 导入模块化版本的Agent
from agents.sql_agent_modular import SQLAgentModular
from agents.rag_agent_modular import RAGAgentModular
from agents.financial_agent_modular import FinancialAgentModular
from agents.money_flow_agent_modular import MoneyFlowAgentModular

# 导入原有的枚举和工具
from agents.hybrid_agent import QueryType, HybridAgent

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


class HybridAgentModular(HybridAgent):
    """
    模块化版本的Hybrid Agent
    继承原有的HybridAgent，只替换Agent实例化部分
    """
    
    def __init__(self, llm_model_name: str = "deepseek-chat"):
        """初始化HybridAgent"""
        # 调用父类的初始化，但不让它创建Agent
        # 先设置基础属性
        self.logger = setup_logger("hybrid_agent_modular")
        self.logger.info("初始化模块化版本的HybridAgent...")
        
        # 初始化LLM
        self.llm = ChatOpenAI(
            model=llm_model_name,
            temperature=0,
            api_key=settings.api_key,
            base_url=settings.base_url
        )
        
        # 初始化模块化版本的各个Agent
        try:
            self.sql_agent = SQLAgentModular(llm_model_name)
            self.logger.info("✅ SQL Agent模块化版本初始化成功")
        except Exception as e:
            self.logger.error(f"SQL Agent初始化失败: {e}")
            raise
            
        try:
            self.rag_agent = RAGAgentModular(llm_model_name)
            self.logger.info("✅ RAG Agent模块化版本初始化成功")
        except Exception as e:
            self.logger.error(f"RAG Agent初始化失败: {e}")
            raise
            
        try:
            self.financial_agent = FinancialAgentModular(llm_model_name)
            self.logger.info("✅ Financial Agent模块化版本初始化成功")
        except Exception as e:
            self.logger.error(f"Financial Agent初始化失败: {e}")
            raise
            
        try:
            self.money_flow_agent = MoneyFlowAgentModular(llm_model_name)
            self.logger.info("✅ Money Flow Agent模块化版本初始化成功")
        except Exception as e:
            self.logger.error(f"Money Flow Agent初始化失败: {e}")
            raise
        
        # 初始化路由相关的属性
        self.routing_config = routing_config
        self.schema_router = schema_router
        
        # 路由监控器
        self.routing_monitor = routing_monitor
        
        # 创建路由提示模板
        self._create_routing_prompt()
        
        self.logger.info("✅ 模块化版本HybridAgent初始化完成")
    
    def query(self, question: str) -> Dict[str, Any]:
        """
        执行查询 - 使用父类的query方法
        所有路由逻辑保持不变，只是使用了新的模块化Agent
        """
        return super().query(question)