# 文件路径: E:\PycharmProjects\stock_analysis_system\agents\sql_agent_modular.py

"""
SQL Agent 模块化版本 - 完全重构实现
使用统一的参数提取器、验证器、格式化器和错误处理器
"""
import re
import sys
import os
import time
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
import json
from functools import lru_cache

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from langchain_community.agent_toolkits.sql.base import create_sql_agent
from langchain.agents.agent_types import AgentType
from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits import SQLDatabaseToolkit
from langchain.memory import ConversationBufferMemory
from langchain.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from sqlalchemy import create_engine, inspect
import pandas as pd

from config.settings import settings
from database.mysql_connector import MySQLConnector
from utils.logger import setup_logger
from utils.date_intelligence import date_intelligence
from utils.schema_knowledge_base import schema_kb
from utils.flexible_parser import FlexibleSQLOutputParser, extract_result_from_error
from utils.sql_templates import SQLTemplates
from utils.query_templates import match_query_template
from utils.stock_code_mapper import convert_to_ts_code, get_stock_name
from utils.security_filter import clean_llm_output, validate_query

# 导入新的模块化组件
from utils.parameter_extractor import ParameterExtractor, ExtractedParams
from utils.query_validator import QueryValidator
from utils.result_formatter import ResultFormatter
from utils.error_handler import ErrorHandler, ErrorCategory, ErrorSeverity
from utils.agent_response import AgentResponse, success, error, ResponseType


class SQLAgentModular:
    """SQL查询代理 - 模块化架构版本"""
    
    def __init__(self, llm_model_name: str = "deepseek-chat"):
        self.logger = setup_logger("sql_agent_modular")
        self.mysql_connector = MySQLConnector()
        
        # 初始化模块化组件
        self.param_extractor = ParameterExtractor()
        self.query_validator = QueryValidator()
        self.result_formatter = ResultFormatter()
        self.error_handler = ErrorHandler()
        
        # 初始化LLM（使用DeepSeek）
        self.llm = ChatOpenAI(
            model=llm_model_name,
            temperature=0,
            api_key=settings.DEEPSEEK_API_KEY,
            base_url=settings.DEEPSEEK_BASE_URL
        )
        
        # 初始化SQL数据库对象
        self.db = SQLDatabase.from_uri(settings.MYSQL_URL)
        
        # 获取数据库schema信息
        self.logger.info("初始化SQL Agent V2，准备加载Schema信息...")
        self.schema_info = self._get_schema_info()
        self.logger.info(f"Schema信息加载完成，共{len(self.schema_info)}个表")
        
        # 创建SQL工具包
        self.toolkit = SQLDatabaseToolkit(db=self.db, llm=self.llm)
        
        # 创建自定义prompt
        self.sql_prompt = self._create_sql_prompt()
        
        # 创建SQL agent
        self.agent = self._create_agent()
        
        # 对话记忆
        self.memory = None
        
        # 初始化查询缓存
        self._query_cache = {}
        
        # 初始化灵活解析器
        self.flexible_parser = FlexibleSQLOutputParser()
        
        self.logger.info("SQL Agent V2初始化完成")
    
    def _format_error_response(self, error_msg: str, error_code: str = "QUERY_ERROR", 
                             details: Optional[Dict] = None) -> Dict[str, Any]:
        """
        统一的错误响应格式化方法
        使用ErrorHandler记录错误，但返回系统期望的格式
        """
        # 使用ErrorHandler处理错误（用于日志记录和错误分类）
        error_info = self.error_handler.handle_error(
            Exception(error_msg), 
            error_code,
            details
        )
        
        # 记录错误日志
        self.logger.error(f"[{error_code}] {error_msg}")
        if details:
            self.logger.debug(f"错误详情: {details}")
        
        # 返回系统期望的格式
        return {
            'success': False,
            'error': error_msg,
            'result': None,
            'sql': None,
            'quick_path': False
        }
    
    def _get_schema_info(self) -> Dict[str, Any]:
        """获取数据库schema信息 - 使用Schema知识库优化性能"""
        schema_info = {}
        try:
            # 使用Schema知识库快速获取表信息（<10ms）
            self.logger.info("使用Schema知识库获取表结构信息...")
            
            # 获取所有表的基础信息
            for table_name, table_data in schema_kb.table_knowledge.items():
                # 将fields字典转换为列表格式
                columns = []
                fields = table_data.get('fields', {})
                if isinstance(fields, dict):
                    for field_name, field_info in fields.items():
                        columns.append({
                            'name': field_name,
                            'cn_name': field_info.get('chinese_name', ''),
                            'type': field_info.get('type', ''),
                            'comment': field_info.get('comment', '')
                        })
                else:
                    # 如果fields已经是列表，直接使用
                    columns = fields
                    
                schema_info[table_name] = {
                    'columns': columns,
                    'description': table_data.get('cn_name', ''),
                    'type': table_data.get('type', 'table')
                }
                
            # 获取列的中文映射信息（如果需要的话）
            # 注意：我们已经在上面的循环中设置了cn_name，这里可以跳过
                            
            return schema_info
            
        except Exception as e:
            self.logger.error(f"获取Schema信息失败: {str(e)}")
            # 降级到直接数据库查询
            return self._get_schema_info_from_db()
    
    def _get_schema_info_from_db(self) -> Dict[str, Any]:
        """从数据库直接获取schema信息（降级方案）"""
        schema_info = {}
        try:
            engine = create_engine(settings.MYSQL_URL)
            inspector = inspect(engine)
            
            for table_name in inspector.get_table_names():
                columns = []
                for col in inspector.get_columns(table_name):
                    columns.append({
                        'name': col['name'],
                        'type': str(col['type']),
                        'nullable': col['nullable'],
                        'default': col['default'],
                        'cn_name': ''  # Will be populated later if available
                    })
                schema_info[table_name] = {
                    'columns': columns,
                    'description': schema_kb.table_knowledge.get(table_name, {}).get('cn_name', ''),
                    'type': 'table'
                }
                
            return schema_info
            
        except Exception as e:
            self.logger.error(f"从数据库获取Schema信息失败: {str(e)}")
            return {}
    
    def _create_sql_prompt(self) -> PromptTemplate:
        """创建优化的SQL查询prompt"""
        template = """你是一个MySQL数据库专家，专门处理股票市场数据查询。

重要规则：
1. 股票代码必须使用.SH/.SZ/.BJ后缀的格式（如'600519.SH'）
2. 日期格式必须是YYYYMMDD（如'20250111'）
3. 不要在最终SQL语句中使用中文别名
4. 优先使用简单高效的SQL语句
5. 对于排名查询，默认返回前10条记录
6. 不要返回过多数据，适当使用LIMIT限制

可用的表和字段信息：
{schema_info}

问题：{question}

请生成一个准确、高效的SQL查询语句。
"""
        
        # 构建schema信息字符串
        schema_str = self._build_schema_string()
        
        return PromptTemplate(
            input_variables=["question"],
            template=template,
            partial_variables={"schema_info": schema_str}
        )
    
    def _build_schema_string(self) -> str:
        """构建schema信息字符串"""
        lines = []
        
        # 只包含主要的表信息
        main_tables = ['tu_stock_basic', 'tu_daily', 'tu_daily_basic', 
                      'tu_income', 'tu_balancesheet', 'tu_cashflow', 
                      'tu_fina_indicator', 'tu_moneyflow', 'juchao_announcement']
        
        for table_name in main_tables:
            if table_name in self.schema_info:
                info = self.schema_info[table_name]
                cn_name = info.get('description', '')
                if cn_name:
                    lines.append(f"\n表：{table_name} ({cn_name})")
                else:
                    lines.append(f"\n表：{table_name}")
                
                # 只列出关键字段
                key_fields = []
                for col in info['columns'][:20]:  # 限制显示字段数量
                    col_str = f"  - {col['name']}"
                    if col.get('cn_name'):
                        col_str += f" ({col['cn_name']})"
                    col_str += f": {col['type']}"
                    key_fields.append(col_str)
                
                lines.extend(key_fields)
                
                if len(info['columns']) > 20:
                    lines.append(f"  ... 还有{len(info['columns']) - 20}个字段")
        
        return "\n".join(lines)
    
    def _create_agent(self):
        """创建SQL Agent（使用现代LangChain API）"""
        return create_sql_agent(
            llm=self.llm,
            toolkit=self.toolkit,
            agent_type=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
            verbose=True,
            handle_parsing_errors=True,
            max_iterations=3,
            extra_tools=[]
        )
    
    def _try_quick_query(self, question: str) -> Optional[AgentResponse]:
        """尝试使用快速查询模板"""
        # 日期智能处理
        processed_question, date_info = date_intelligence.preprocess_question(question)
        self.logger.info(f"日期智能处理后的查询: {processed_question}")
        
        # 中文数字规范化（在日期处理后，模板匹配前）
        from utils.chinese_number_converter import normalize_quantity_expression
        processed_question = normalize_quantity_expression(processed_question)
        self.logger.info(f"中文数字规范化后: {processed_question}")
        
        # 匹配查询模板
        template_result = match_query_template(processed_question)
        if not template_result:
            # 检查是否包含需要股票的关键词但没有股票信息
            stock_required_keywords = ['K线', 'k线', '走势', '行情', '股价', '成交量', '市值', '涨跌', '涨幅排名']
            if any(keyword in processed_question for keyword in stock_required_keywords):
                # 尝试提取股票
                temp_params = self.param_extractor.extract_all_params(processed_question)
                if not temp_params.stocks:
                    return error(
                        "未识别到股票信息，请指定具体股票",
                        "MISSING_STOCK",
                        query=processed_question
                    )
            return None
        
        template, params = template_result
        
        self.logger.info(f"匹配到快速查询模板: {template.name}")
        
        try:
            # 使用统一的参数提取器
            extracted_params = self.param_extractor.extract_all_params(processed_question, template)
            
            # 如果有错误，返回错误信息
            if extracted_params.error:
                return error(
                    extracted_params.error,
                    "INVALID_STOCK",
                    template=template.name
                )
            
            # 对于某些查询，如果没有日期，使用最新交易日
            if template.requires_date and not extracted_params.date and not extracted_params.date_range:
                # 允许使用默认最新交易日的模板列表
                allow_default_date_templates = [
                    '股价查询', '估值指标查询', '个股主力资金', 
                    '板块主力资金', '涨跌幅排名', '成交额排名',
                    '成交量排名', '成交量查询', '市值排名', '主力净流入排行', '主力净流出排行'
                ]
                
                if template.name in allow_default_date_templates:
                    self.logger.info(f"查询 '{template.name}' 未指定日期，使用最新交易日")
                    # 即使使用默认日期，也要进行增强验证
                    validation_result = self.query_validator.validate_enhanced(extracted_params, template)
                    if not validation_result.is_valid:
                        error_msg = validation_result.error_detail.get('message', '参数验证失败')
                        return error(
                            error_msg,
                            validation_result.error_code or "VALIDATION_ERROR",
                            template=template.name
                        )
                    # 继续执行，后续会使用last_trading_date
                else:
                    # 其他需要日期的查询，返回错误
                    validation_result = self.query_validator.validate_enhanced(extracted_params, template)
                    if not validation_result.is_valid:
                        error_msg = validation_result.error_detail.get('message', '参数验证失败')
                        return error(
                            error_msg,
                            validation_result.error_code or "VALIDATION_ERROR",
                            template=template.name
                        )
            else:
                # 使用统一的查询验证器 - 先尝试增强验证
                validation_result = self.query_validator.validate_enhanced(extracted_params, template)
                if not validation_result.is_valid:
                    error_msg = validation_result.error_detail.get('message', '参数验证失败')
                    return error(
                        error_msg,
                        validation_result.error_code or "VALIDATION_ERROR",
                        template=template.name
                    )
            
            # 获取最新交易日
            last_trading_date = date_intelligence.calculator.get_latest_trading_day()
            if not last_trading_date:
                last_trading_date = datetime.now().strftime('%Y%m%d')
            else:
                last_trading_date = last_trading_date.replace('-', '')
            
            # 执行特定模板的快速查询
            return self._execute_template_query(template, extracted_params, processed_question, last_trading_date)
            
        except Exception as e:
            self.logger.error(f"快速查询执行失败: {str(e)}")
            return error(
                f"查询执行失败: {str(e)}",
                "EXECUTION_ERROR",
                template=template.name if template else None
            )
    
    def _execute_template_query(self, template: Any, params: ExtractedParams, 
                              processed_question: str, last_trading_date: str) -> AgentResponse:
        """执行模板查询 - 使用模块化组件"""
        try:
            # 根据不同的模板执行相应的查询
            result = None
            if template.name == '股价查询':
                result = self._execute_stock_price_query(params, last_trading_date)
            elif template.name == '估值查询' or template.name == '估值指标查询':
                result = self._execute_valuation_query(params, last_trading_date)
            elif template.name == '市值排名':
                result = self._execute_market_cap_ranking(params, last_trading_date)
            elif template.name == '涨幅排名' or template.name == '涨跌幅排名':
                result = self._execute_pct_chg_ranking(params, last_trading_date)
            elif template.name == '成交额排名':
                result = self._execute_amount_ranking(params, last_trading_date)
            elif template.name == '总市值排名' or template.name == '市值排名':
                result = self._execute_market_cap_ranking(params, last_trading_date)
            elif template.name == '流通市值排名':
                result = self._execute_circ_market_cap_ranking(params, last_trading_date)
            elif template.name == 'K线查询':
                result = self._execute_kline_query(params, processed_question)
            elif template.name == '成交量查询':
                result = self._execute_volume_query(params, last_trading_date)
            elif template.name == '成交量排名':
                result = self._execute_volume_ranking(params, last_trading_date)
            elif template.name == '主力净流入排行':
                result = self._execute_money_flow_ranking(params, last_trading_date, is_outflow=False)
            elif template.name == '主力净流出排行':
                result = self._execute_money_flow_ranking(params, last_trading_date, is_outflow=True)
            elif template.name == '个股主力资金':
                result = self._execute_stock_money_flow(params, last_trading_date)
            elif template.name == '板块主力资金':
                result = self._execute_sector_money_flow(params, last_trading_date)
            elif template.name == '财务数据查询':
                result = self._execute_financial_query(params)
            elif template.name == '利润查询':
                result = self._execute_profit_query(params)
            elif template.name == 'PE排名':
                result = self._execute_pe_ranking(params, last_trading_date)
            elif template.name == 'PB排名':
                result = self._execute_pb_ranking(params, last_trading_date)
            elif template.name == '净利润排名':
                result = self._execute_profit_ranking(params)
            elif template.name == '营收排名':
                result = self._execute_revenue_ranking(params)
            elif template.name == 'ROE排名':
                result = self._execute_roe_ranking(params)
            elif template.name == '公告查询':
                result = self._execute_announcement_query(params, processed_question)
            elif template.name == '板块成分股':
                result = self._execute_sector_stocks_query(params)
            else:
                return None
            
            # 如果执行方法返回的是字典，将其转换为AgentResponse
            if isinstance(result, dict):
                if result.get('success', False):
                    return success(
                        result.get('result', ''),
                        message=f"{template.name}查询成功",
                        sql=result.get('sql'),
                        quick_path=result.get('quick_path', True),
                        template=template.name
                    )
                else:
                    return error(
                        result.get('error', '查询失败'),
                        "QUERY_ERROR",
                        template=template.name
                    )
            elif isinstance(result, AgentResponse):
                # 如果已经是AgentResponse，直接返回
                return result
            else:
                # 如果返回了其他类型，记录错误
                self.logger.error(f"执行方法返回了意外的类型: {type(result)}")
                return error(
                    f"执行方法返回了意外的类型: {type(result)}",
                    "UNEXPECTED_RETURN_TYPE",
                    template=template.name
                )
                
        except Exception as e:
            self.logger.error(f"模板查询执行失败: {str(e)}")
            return error(
                f"查询执行失败: {str(e)}",
                "TEMPLATE_EXECUTION_ERROR",
                template=template.name if template else None
            )
    
    def _execute_stock_price_query(self, params: ExtractedParams, last_trading_date: str) -> AgentResponse:
        """执行股价查询"""
        if not params.stocks:
            return error("未识别到股票信息", "MISSING_STOCK")
        
        ts_code = params.stocks[0]
        stock_name = params.stock_names[0] if params.stock_names else ""
        trade_date = params.date or last_trading_date
        
        # 根据是否有日期选择不同的SQL模板
        if params.date:
            sql = SQLTemplates.STOCK_PRICE_BY_DATE
            query_params = {'ts_code': ts_code, 'trade_date': trade_date}
        else:
            sql = SQLTemplates.STOCK_PRICE_LATEST
            query_params = {'ts_code': ts_code}
        
        result = self.mysql_connector.execute_query(sql, query_params)
        
        if result and len(result) > 0:
            data = result[0]
            
            # 使用结果格式化器
            formatted_data = {
                "股票": f"{stock_name}（{ts_code}）" if stock_name else ts_code,
                "日期": data['trade_date'],
                "开盘价": f"{data['open']:.2f}",
                "最高价": f"{data['high']:.2f}",
                "最低价": f"{data['low']:.2f}",
                "收盘价": f"{data['close']:.2f}",
                "涨跌幅": f"{data['pct_chg']:.2f}%",
                "成交量": f"{data['vol'] / 10000:.2f}万手",
                "成交额": f"{data['amount'] / 10000:.2f}万元"
            }
            
            formatted_result = self.result_formatter.format_dict_data(formatted_data)
            
            return success(
                formatted_result,
                message=f"{stock_name or ts_code}股价查询成功",
                sql=None,  # 不暴露SQL
                quick_path=True,
                stock_code=ts_code,
                stock_name=stock_name,
                trade_date=trade_date
            )
        else:
            return error(
                f"未找到{stock_name or ts_code}在{trade_date}的股价数据",
                "NO_DATA",
                stock_code=ts_code,
                trade_date=trade_date
            )
    
    def _execute_valuation_query(self, params: ExtractedParams, last_trading_date: str) -> Dict[str, Any]:
        """执行估值指标查询"""
        if not params.stocks:
            return {
                'success': False,
                'error': "未识别到股票信息"
            }
        
        ts_code = params.stocks[0]
        stock_name = params.stock_names[0] if params.stock_names else ""
        trade_date = params.date or last_trading_date
        
        sql = SQLTemplates.VALUATION_METRICS_BY_DATE if params.date else SQLTemplates.VALUATION_METRICS
        result = self.mysql_connector.execute_query(sql, {
            'ts_code': ts_code,
            'trade_date': trade_date
        })
        
        if result and len(result) > 0:
            data = result[0]
            
            valuation_data = {
                "股票": f"{stock_name}（{ts_code}）" if stock_name else ts_code,
                "日期": trade_date,
                "市盈率(PE)": f"{data.get('pe', 0):.2f}",
                "市盈率(TTM)": f"{data.get('pe_ttm', 0):.2f}",
                "市净率(PB)": f"{data.get('pb', 0):.2f}",
                "市销率(PS)": f"{data.get('ps', 0):.2f}",
                "市销率(TTM)": f"{data.get('ps_ttm', 0):.2f}",
                "股息率": f"{data.get('dv_ratio', 0):.2f}%"
            }
            
            formatted_result = self.result_formatter.format_dict_data(valuation_data)
            
            return {
                'success': True,
                'result': formatted_result,
                'sql': None,
                'quick_path': True
            }
        else:
            return {
                'success': False,
                'error': f"未找到{stock_name or ts_code}的估值数据"
            }
    
    def _execute_pct_chg_ranking(self, params: ExtractedParams, last_trading_date: str) -> Dict[str, Any]:
        """执行涨跌幅排名查询"""
        trade_date = params.date or last_trading_date
        limit = params.limit
        order = params.order_by  # DESC for 涨幅, ASC for 跌幅
        
        sql = SQLTemplates.PCT_CHG_RANKING_DESC if order == "DESC" else SQLTemplates.PCT_CHG_RANKING
        result = self.mysql_connector.execute_query(sql, {
            'trade_date': trade_date,
            'limit': limit
        })
        
        if result and len(result) > 0:
            headers = ["排名", "股票代码", "股票名称", "收盘价", "涨跌幅(%)"]
            rows = []
            
            for i, row in enumerate(result, 1):
                rows.append([
                    i,
                    row['ts_code'],
                    row['name'],
                    f"{row['close']:.2f}",
                    f"{row['pct_chg']:.2f}"
                ])
            
            order_desc = "涨幅" if order == "DESC" else "跌幅"
            title = f"{trade_date} {order_desc}排名前{limit}"
            
            formatted_result = self.result_formatter.format_table(headers, rows, title=title)
            
            return {
                'success': True,
                'result': formatted_result,
                'sql': None,
                'quick_path': True
            }
        else:
            return {
                'success': False,
                'error': f"未找到{trade_date}的涨跌幅数据"
            }
    
    def _execute_amount_ranking(self, params: ExtractedParams, last_trading_date: str) -> Dict[str, Any]:
        """执行成交额排名查询"""
        trade_date = params.date or last_trading_date
        limit = params.limit
        
        sql = SQLTemplates.AMOUNT_RANKING
        result = self.mysql_connector.execute_query(sql, {
            'trade_date': trade_date,
            'limit': limit
        })
        
        if result and len(result) > 0:
            headers = ["排名", "股票代码", "股票名称", "收盘价", "涨跌幅(%)", "成交额(亿元)"]
            rows = []
            
            for i, row in enumerate(result, 1):
                rows.append([
                    i,
                    row['ts_code'],
                    row['name'],
                    f"{row['close']:.2f}",
                    f"{row['pct_chg']:.2f}",
                    f"{row['amount'] / 100000:.2f}"  # 转换为亿元
                ])
            
            title = f"{trade_date} 成交额排名前{limit}"
            
            formatted_result = self.result_formatter.format_table(headers, rows, title=title)
            
            return {
                'success': True,
                'result': formatted_result,
                'sql': None,
                'quick_path': True
            }
        else:
            return {
                'success': False,
                'error': f"未找到{trade_date}的成交额数据"
            }
    
    def _execute_profit_query(self, params: ExtractedParams) -> Dict[str, Any]:
        """执行利润查询"""
        if not params.stocks:
            return {
                'success': False,
                'error': "未识别到股票信息"
            }
        
        ts_code = params.stocks[0]
        stock_name = params.stock_names[0] if params.stock_names else ""
        
        # 如果指定了报告期，使用指定的；否则查询最新的
        if params.period:
            sql = """
                SELECT end_date, revenue, n_income, basic_eps
                FROM tu_income
                WHERE ts_code = :ts_code AND end_date = :period
                LIMIT 1
            """
            result = self.mysql_connector.execute_query(sql, {
                'ts_code': ts_code,
                'period': params.period
            })
        else:
            sql = SQLTemplates.PROFIT_LATEST
            result = self.mysql_connector.execute_query(sql, {'ts_code': ts_code})
        
        if result and len(result) > 0:
            # 准备表格数据
            headers = ["报告期", "营业收入(亿元)", "净利润(亿元)", "基本每股收益"]
            rows = []
            
            for row in result[:4]:  # 只显示最近4期
                # 处理可能存在的字段名问题
                revenue = row.get('revenue', 0) or 0
                net_profit = row.get('net_profit', row.get('n_income', 0)) or 0
                basic_eps = row.get('basic_eps', 0) or 0
                
                rows.append([
                    self._format_period(row['end_date']),
                    f"{revenue / 100000000:.2f}",
                    f"{net_profit / 100000000:.2f}",
                    f"{basic_eps:.3f}"
                ])
            
            stock_info = f"{stock_name}（{ts_code}）" if stock_name else ts_code
            title = f"{stock_info} 财务利润数据"
            
            formatted_result = self.result_formatter.format_table(headers, rows, title=title)
            
            return {
                'success': True,
                'result': formatted_result,
                'sql': None,
                'quick_path': True
            }
        else:
            return {
                'success': False,
                'error': f"未找到{stock_name or ts_code}的利润数据"
            }
    
    def _execute_market_cap_ranking(self, params: ExtractedParams, last_trading_date: str) -> Dict[str, Any]:
        """执行市值排名查询"""
        trade_date = params.date or last_trading_date
        limit = params.limit
        
        # 总市值排名
        sql = SQLTemplates.MARKET_CAP_RANKING
        result = self.mysql_connector.execute_query(sql, {
            'trade_date': trade_date,
            'limit': limit
        })
        
        if result and len(result) > 0:
            # 准备表格数据
            headers = ["排名", "股票代码", "股票名称", "总市值(亿元)", "流通市值(亿元)", "涨跌幅(%)"]
            rows = []
            
            for i, row in enumerate(result, 1):
                rows.append([
                    i,
                    row['ts_code'],
                    row['name'],
                    f"{row['total_mv'] / 10000:.2f}",
                    f"{row['circ_mv'] / 10000:.2f}",
                    f"{row['pct_chg']:.2f}"
                ])
            
            # 使用结果格式化器
            formatted_result = self.result_formatter.format_table(
                headers, 
                rows,
                title=f"{trade_date} A股市值排名前{limit}"
            )
            
            return {
                'success': True,
                'result': formatted_result,
                'sql': None,
                'quick_path': True
            }
        else:
            return {
                'success': False,
                'error': f"未找到{trade_date}的市值数据"
            }
    
    def _execute_circ_market_cap_ranking(self, params: ExtractedParams, last_trading_date: str) -> Dict[str, Any]:
        """执行流通市值排名查询"""
        trade_date = params.date or last_trading_date
        limit = params.limit
        
        # 流通市值排名
        sql = SQLTemplates.CIRC_MV_RANKING
        result = self.mysql_connector.execute_query(sql, {
            'trade_date': trade_date,
            'limit': limit
        })
        
        if result and len(result) > 0:
            # 准备表格数据
            headers = ["排名", "股票代码", "股票名称", "流通市值(亿元)", "总市值(亿元)", "涨跌幅(%)"]
            rows = []
            
            for i, row in enumerate(result, 1):
                rows.append([
                    i,
                    row['ts_code'],
                    row['name'],
                    f"{row['circ_mv'] / 10000:.2f}",
                    f"{row['total_mv'] / 10000:.2f}",
                    f"{row['pct_chg']:.2f}"
                ])
            
            # 使用结果格式化器
            formatted_result = self.result_formatter.format_table(
                headers, 
                rows,
                title=f"{trade_date} A股流通市值排名前{limit}"
            )
            
            return {
                'success': True,
                'result': formatted_result,
                'sql': None,
                'quick_path': True
            }
        else:
            return {
                'success': False,
                'error': f"未找到{trade_date}的流通市值数据"
            }
    
    def _execute_financial_query(self, params: ExtractedParams) -> Dict[str, Any]:
        """执行财务数据查询"""
        if not params.stocks:
            return {
                'success': False,
                'error': "未识别到股票信息"
            }
        
        ts_code = params.stocks[0]
        stock_name = params.stock_names[0] if params.stock_names else ""
        
        sql = SQLTemplates.FINANCIAL_LATEST
        result = self.mysql_connector.execute_query(sql, {'ts_code': ts_code})
        
        if result and len(result) > 0:
            data = result[0]
            
            # 构建财务数据字典
            financial_data = {
                "股票": f"{stock_name}（{ts_code}）" if stock_name else ts_code,
                "报告期": self._format_period(data['end_date']),
                "基本每股收益": f"{data['basic_eps']:.2f}元",
                "净资产收益率": f"{data['roe']:.2f}%",
                "营业总收入": f"{data['revenue'] / 100000000:.2f}亿元",
                "归母净利润": f"{data['n_income'] / 100000000:.2f}亿元",
                "总资产": f"{data['total_assets'] / 100000000:.2f}亿元",
                "净资产": f"{data['total_hldr_eqy_exc_min_int'] / 100000000:.2f}亿元"
            }
            
            formatted_result = self.result_formatter.format_dict_data(financial_data)
            
            return {
                'success': True,
                'result': formatted_result,
                'sql': None,
                'quick_path': True
            }
        else:
            return {
                'success': False,
                'error': f"未找到{stock_name or ts_code}的财务数据"
            }
    
    def _format_period(self, end_date: str) -> str:
        """格式化报告期"""
        if not end_date:
            return "未知"
        
        try:
            # 转换格式 20250331 -> 2025年一季度
            year = end_date[:4]
            month = end_date[4:6]
            
            if month == '03':
                return f"{year}年一季度"
            elif month == '06':
                return f"{year}年半年度"
            elif month == '09':
                return f"{year}年三季度"
            elif month == '12':
                return f"{year}年年度"
            else:
                return end_date
        except:
            return end_date
    
    def query(self, question: str) -> Dict[str, Any]:
        """
        执行查询
        
        注意：为了保持向后兼容，这个方法仍然返回Dict格式
        内部使用AgentResponse，最后转换为旧格式
        """
        try:
            # 输入验证
            if not question or not question.strip():
                resp = error("查询内容不能为空", "EMPTY_QUERY")
                return resp.to_legacy_format("sql")
            
            question = question.strip()
            self.logger.info(f"收到查询请求: {question}")
            
            # 尝试快速查询路径
            quick_result = self._try_quick_query(question)
            if quick_result:
                if quick_result.success:
                    self.logger.info("使用快速查询路径成功")
                else:
                    self.logger.info("快速查询路径返回错误，不降级到LLM")
                return quick_result.to_legacy_format("sql")
            
            # 降级到传统LLM路径
            self.logger.info("使用传统LLM查询路径")
            llm_result = self._execute_llm_query(question)
            # 如果LLM查询返回的是AgentResponse，转换它
            if isinstance(llm_result, AgentResponse):
                return llm_result.to_legacy_format("sql")
            else:
                return llm_result  # 兼容旧格式
            
        except Exception as e:
            self.logger.error(f"查询执行异常: {str(e)}")
            resp = error(f"系统错误: {str(e)}", "SYSTEM_ERROR", query=question)
            return resp.to_legacy_format("sql")
    
    def _execute_llm_query(self, question: str) -> Dict[str, Any]:
        """执行传统的LLM查询"""
        try:
            # 日期智能处理
            processed_question, date_info = date_intelligence.preprocess_question(question)
            
            # 使用参数提取器
            extracted_params = self.param_extractor.extract_all_params(processed_question)
            
            # 执行增强验证（检查非标准术语等）
            validation_result = self.query_validator.validate_enhanced(extracted_params, None)
            if not validation_result.is_valid:
                error_msg = validation_result.error_detail.get('message', '参数验证失败')
                return {
                    'success': False,
                    'error': error_msg,
                    'query_type': 'sql'
                }
            
            # 构建增强的查询
            enhanced_question = self._build_enhanced_question(processed_question, extracted_params)
            
            # 执行查询
            result = self.agent.invoke({"input": enhanced_question})
            
            # 处理不同类型的返回结果
            output = None
            
            # 检查是否是AgentFinish类型（通过类名字符串检查，避免导入问题）
            result_type_name = type(result).__name__
            
            if result_type_name == 'AgentFinish':
                # 这是一个AgentFinish对象
                if hasattr(result, 'return_values'):
                    if isinstance(result.return_values, dict):
                        output = result.return_values.get('output', '')
                    else:
                        output = str(result.return_values)
                else:
                    # 如果没有return_values属性，尝试直接转换
                    output = str(result)
                    self.logger.warning(f"AgentFinish对象没有return_values属性")
            elif hasattr(result, 'return_values'):
                # 有return_values属性的其他对象
                if isinstance(result.return_values, dict):
                    output = result.return_values.get('output', '')
                else:
                    output = str(result.return_values)
            elif isinstance(result, dict):
                # 字典格式
                if 'output' in result:
                    output = result['output']
                elif 'result' in result:
                    output = result['result']
                else:
                    # 尝试将整个字典转换为字符串
                    output = str(result)
            elif isinstance(result, str):
                # 字符串格式
                output = result
            else:
                # 尝试直接转换为字符串
                output = str(result)
                self.logger.warning(f"未知的返回类型: {type(result).__name__}, 已转换为字符串")
            
            if not output:
                self.logger.error(f"无法从结果中提取输出: {result}")
                return {
                    'success': False,
                    'error': "无法从查询结果中提取有效输出"
                }
            
            # 解析结果
            if output:
                # flexible_parser.parse返回的是AgentFinish对象，不是字典
                # 我们已经有了output，直接使用它
                try:
                    # 尝试使用flexible_parser从输出中提取SQL
                    from utils.flexible_parser import FlexibleSQLOutputParser, extract_result_from_error
                    
                    # 尝试提取SQL语句
                    sql_pattern = r'```sql\n(.*?)\n```'
                    import re
                    sql_match = re.search(sql_pattern, output, re.DOTALL)
                    extracted_sql = sql_match.group(1) if sql_match else None
                    
                    # 直接返回output作为结果
                    return {
                        'success': True,
                        'result': output,
                        'sql': extracted_sql,
                        'quick_path': False
                    }
                except Exception as parse_error:
                    self.logger.warning(f"解析输出时出错: {parse_error}, 但仍返回原始输出")
                    return {
                        'success': True,
                        'result': output,
                        'sql': None,
                        'quick_path': False
                    }
            else:
                return {
                'success': False,
                'error': "查询执行失败"
            }
                
        except Exception as e:
            self.logger.error(f"LLM查询执行失败: {str(e)}")
            import traceback
            self.logger.error(f"错误堆栈: {traceback.format_exc()}")
            return {
                'success': False,
                'error': f"系统错误: {str(e)}"
            }
    
    def _build_enhanced_question(self, question: str, params: ExtractedParams) -> str:
        """构建增强的查询问题"""
        enhanced = question
        
        # 如果提取到了股票，添加提示
        if params.stocks:
            stocks_hint = f"（股票代码：{', '.join(params.stocks)}）"
            enhanced += stocks_hint
        
        # 如果提取到了日期，添加提示
        if params.date:
            enhanced += f"（日期：{params.date}）"
        elif params.date_range:
            enhanced += f"（日期范围：{params.date_range[0]}至{params.date_range[1]}）"
        
        return enhanced
    
    def _execute_volume_query(self, params: ExtractedParams, last_trading_date: str) -> Dict[str, Any]:
        """执行成交量查询"""
        if not params.stocks:
            return {
                'success': False,
                'error': "未识别到股票信息"
            }
        
        ts_code = params.stocks[0]
        stock_name = params.stock_names[0] if params.stock_names else ""
        trade_date = params.date or last_trading_date
        
        sql = SQLTemplates.VOLUME_BY_DATE
        result = self.mysql_connector.execute_query(sql, {
            'ts_code': ts_code,
            'trade_date': trade_date
        })
        
        if result and len(result) > 0:
            data = result[0]
            volume_desc = f"{stock_name}（{ts_code}）" if stock_name else ts_code
            volume_desc += f"在{trade_date}的成交量为{data['vol'] / 10000:.2f}万手，成交额为{data['amount'] / 10000:.2f}万元"
            
            return {
                'success': True,
                'result': volume_desc,
                'sql': None,
                'quick_path': True
            }
        else:
            return {
                'success': False,
                'error': f"未找到{stock_name or ts_code}在{trade_date}的成交量数据"
            }
    
    def _execute_money_flow_ranking(self, params: ExtractedParams, last_trading_date: str, is_outflow: bool = False) -> Dict[str, Any]:
        """执行主力资金流向排名查询"""
        trade_date = params.date or last_trading_date
        limit = params.limit
        
        sql = SQLTemplates.MONEY_FLOW_RANKING_OUT if is_outflow else SQLTemplates.MONEY_FLOW_RANKING_IN
        result = self.mysql_connector.execute_query(sql, {
            'trade_date': trade_date,
            'limit': limit
        })
        
        if result and len(result) > 0:
            headers = ["排名", "股票代码", "股票名称", "主力净流入(万元)", "涨跌幅(%)"]
            rows = []
            
            for i, row in enumerate(result, 1):
                rows.append([
                    i,
                    row['ts_code'],
                    row['name'],
                    f"{row['net_amount'] / 10000:.2f}",
                    f"{row['pct_chg']:.2f}"
                ])
            
            flow_type = "净流出" if is_outflow else "净流入"
            title = f"{trade_date} 主力{flow_type}排名前{limit}"
            
            formatted_result = self.result_formatter.format_table(headers, rows, title=title)
            
            return {
                'success': True,
                'result': formatted_result,
                'sql': None,
                'quick_path': True
            }
        else:
            return {
                'success': False,
                'error': f"未找到{trade_date}的主力资金流向数据"
            }
    
    def _execute_stock_money_flow(self, params: ExtractedParams, last_trading_date: str) -> Dict[str, Any]:
        """执行个股主力资金查询"""
        if not params.stocks:
            return {
                'success': False,
                'error': "未识别到股票信息"
            }
        
        ts_code = params.stocks[0]
        stock_name = params.stock_names[0] if params.stock_names else ""
        trade_date = params.date or last_trading_date
        
        sql = SQLTemplates.STOCK_MONEY_FLOW
        result = self.mysql_connector.execute_query(sql, {
            'ts_code': ts_code,
            'trade_date': trade_date
        })
        
        if result and len(result) > 0:
            data = result[0]
            
            # 根据SQL模板返回的字段名构建数据
            flow_data = {
                "股票": f"{stock_name}（{ts_code}）" if stock_name else ts_code,
                "日期": trade_date,
                "净流入金额": f"{data.get('net_amount', 0) / 10000:.2f}万元",
                "净流入率": f"{data.get('net_amount_rate', 0):.2f}%",
                "超大单买入": f"{data.get('buy_elg_amount', 0) / 10000:.2f}万元",
                "大单买入": f"{data.get('buy_lg_amount', 0) / 10000:.2f}万元",
                "中单买入": f"{data.get('buy_md_amount', 0) / 10000:.2f}万元",
                "小单买入": f"{data.get('buy_sm_amount', 0) / 10000:.2f}万元",
                "涨跌幅": f"{data.get('pct_change', 0):.2f}%"
            }
            
            formatted_result = self.result_formatter.format_dict_data(flow_data)
            
            return {
                'success': True,
                'result': formatted_result,
                'sql': None,
                'quick_path': True
            }
        else:
            return {
                'success': False,
                'error': f"未找到{stock_name or ts_code}在{trade_date}的主力资金数据"
            }
    
    def _execute_sector_money_flow(self, params: ExtractedParams, last_trading_date: str) -> Dict[str, Any]:
        """执行板块主力资金查询"""
        # 提取板块名称和板块代码
        sector_name = params.sector or params.industry
        sector_code = params.sector_code
        
        if not sector_name and not sector_code:
            return {
                'success': False,
                'error': "未识别到板块信息"
            }
        
        # 如果有板块代码，优先使用板块代码查询
        if sector_code:
            # 如果板块代码是BKxxxx.DC格式，通过代码反查名称
            from utils.sector_code_mapper import get_sector_name
            resolved_name = get_sector_name(sector_code)
            if resolved_name:
                sector_name = resolved_name
                self.logger.info(f"通过板块代码 {sector_code} 获取板块名称: {sector_name}")
            else:
                # 如果没有找到对应的名称，使用代码作为名称
                sector_name = sector_code
                self.logger.warning(f"未找到板块代码 {sector_code} 对应的名称，使用代码查询")
        
        # 添加板块名称映射
        from utils.sector_name_mapper import map_sector_name
        mapped_name = map_sector_name(sector_name)
        if mapped_name:
            self.logger.info(f"板块名称映射: {sector_name} -> {mapped_name}")
            sector_name = mapped_name
        
        trade_date = params.date or last_trading_date
        
        # 查询板块主力资金数据（tu_moneyflow_ind_dc表存储的是板块级别数据）
        sql = SQLTemplates.SECTOR_MONEY_FLOW
        
        # 检查是否已经包含板块后缀
        if not sector_name.endswith('板块'):
            query_sector_name = sector_name + '板块'
        else:
            query_sector_name = sector_name
            
        result = self.mysql_connector.execute_query(sql, {
            'sector_name': query_sector_name,
            'trade_date': trade_date
        })
        
        # 如果没找到，尝试不带"板块"后缀
        if not result:
            result = self.mysql_connector.execute_query(sql, {
                'sector_name': sector_name,
                'trade_date': trade_date
            })
        
        if result and len(result) > 0:
            # 板块级别的数据只有一行
            row = result[0]
            
            # 格式化板块主力资金数据
            formatted_result = f"""## {sector_name}板块主力资金（{trade_date}）

**板块名称**: {row.get('name', sector_name)}
**交易日期**: {trade_date}
**主力净流入**: {row.get('net_amount', 0) / 10000:.2f}万元
**超大单净流入**: {row.get('buy_elg_amount', 0) / 10000:.2f}万元
**大单净流入**: {row.get('buy_lg_amount', 0) / 10000:.2f}万元
**中单净流入**: {row.get('buy_md_amount', 0) / 10000:.2f}万元
**小单净流入**: {row.get('buy_sm_amount', 0) / 10000:.2f}万元
**板块涨跌幅**: {row.get('pct_change', 0):.2f}%
**板块排名**: 第{row.get('rank', '-')}名"""
            
            return {
                'success': True,
                'result': formatted_result,
                'sql': None,
                'quick_path': True
            }
        else:
            return {
                'success': False,
                'error': f"未找到{sector_name}在{trade_date}的主力资金数据"
            }
    
    def _get_sector_stocks(self, sector_name: str) -> List[str]:
        """获取板块成分股"""
        # 简单的板块映射（实际应该从数据库查询）
        sector_map = {
            '银行': ['601398.SH', '601939.SH', '601288.SH', '601988.SH', '600016.SH'],
            '白酒': ['600519.SH', '000858.SZ', '000568.SZ', '002304.SZ', '603369.SH'],
            '新能源': ['300750.SZ', '002594.SZ', '300124.SZ', '300274.SZ', '002129.SZ']
        }
        
        # 去掉"板块"后缀
        clean_name = sector_name.replace('板块', '')
        return sector_map.get(clean_name, [])
    
    def _execute_pe_ranking(self, params: ExtractedParams, last_trading_date: str) -> Dict[str, Any]:
        """执行PE排名查询"""
        trade_date = params.date or last_trading_date
        limit = params.limit
        order = params.order_by
        
        sql = SQLTemplates.PE_RANKING
        result = self.mysql_connector.execute_query(sql, {
            'trade_date': trade_date,
            'order': order,
            'limit': limit
        })
        
        if result and len(result) > 0:
            headers = ["排名", "股票代码", "股票名称", "PE", "涨跌幅(%)"]
            rows = []
            
            for i, row in enumerate(result, 1):
                # 处理None值的情况
                pe_value = row.get('pe_ttm')
                if pe_value is None:
                    pe_str = "N/A"
                else:
                    pe_str = f"{pe_value:.2f}"
                    
                pct_chg = row.get('pct_chg', 0) or 0
                
                rows.append([
                    i,
                    row['ts_code'],
                    row['name'],
                    pe_str,
                    f"{pct_chg:.2f}"
                ])
            
            order_desc = "最高" if order == "DESC" else "最低"
            title = f"{trade_date} PE{order_desc}前{limit}"
            
            formatted_result = self.result_formatter.format_table(headers, rows, title=title)
            
            return {
                'success': True,
                'result': formatted_result,
                'sql': None,
                'quick_path': True
            }
        else:
            return {
                'success': False,
                'error': f"未找到{trade_date}的PE数据"
            }
    
    def _execute_pb_ranking(self, params: ExtractedParams, last_trading_date: str) -> Dict[str, Any]:
        """执行PB排名查询"""
        trade_date = params.date or last_trading_date
        limit = params.limit
        order = params.order_by
        
        sql = SQLTemplates.PB_RANKING
        result = self.mysql_connector.execute_query(sql, {
            'trade_date': trade_date,
            'order': order,
            'limit': limit
        })
        
        if result and len(result) > 0:
            headers = ["排名", "股票代码", "股票名称", "PB", "涨跌幅(%)"]
            rows = []
            
            for i, row in enumerate(result, 1):
                rows.append([
                    i,
                    row['ts_code'],
                    row['name'],
                    f"{row['pb']:.2f}",
                    f"{row['pct_chg']:.2f}"
                ])
            
            order_desc = "最高" if order == "DESC" else "最低"
            title = f"{trade_date} PB{order_desc}前{limit}"
            
            formatted_result = self.result_formatter.format_table(headers, rows, title=title)
            
            return {
                'success': True,
                'result': formatted_result,
                'sql': None,
                'quick_path': True
            }
        else:
            return {
                'success': False,
                'error': f"未找到{trade_date}的PB数据"
            }
    
    def _execute_profit_ranking(self, params: ExtractedParams) -> Dict[str, Any]:
        """执行净利润排名查询"""
        limit = params.limit
        order = params.order_by
        period = params.period or "20241231"  # 默认最新年报
        
        sql = SQLTemplates.PROFIT_RANKING
        result = self.mysql_connector.execute_query(sql, {
            'period': period,
            'order': order,
            'limit': limit
        })
        
        if result and len(result) > 0:
            headers = ["排名", "股票代码", "股票名称", "净利润(亿元)", "同比增长(%)"]
            rows = []
            
            for i, row in enumerate(result, 1):
                rows.append([
                    i,
                    row['ts_code'],
                    row['name'],
                    f"{row['n_income'] / 100000000:.2f}",
                    f"{row.get('n_income_yoy', 0):.2f}"
                ])
            
            order_desc = "最高" if order == "DESC" else "最低"
            period_desc = self._format_period(period)
            title = f"{period_desc} 净利润{order_desc}前{limit}"
            
            formatted_result = self.result_formatter.format_table(headers, rows, title=title)
            
            return {
                'success': True,
                'result': formatted_result,
                'sql': None,
                'quick_path': True
            }
        else:
            return {
                'success': False,
                'error': f"未找到{period}的净利润数据"
            }
    
    def _execute_revenue_ranking(self, params: ExtractedParams) -> Dict[str, Any]:
        """执行营收排名查询"""
        limit = params.limit
        order = params.order_by
        period = params.period or "20241231"
        
        sql = SQLTemplates.REVENUE_RANKING
        result = self.mysql_connector.execute_query(sql, {
            'period': period,
            'order': order,
            'limit': limit
        })
        
        if result and len(result) > 0:
            headers = ["排名", "股票代码", "股票名称", "营业收入(亿元)", "同比增长(%)"]
            rows = []
            
            for i, row in enumerate(result, 1):
                rows.append([
                    i,
                    row['ts_code'],
                    row['name'],
                    f"{row['revenue'] / 100000000:.2f}",
                    f"{row.get('revenue_yoy', 0):.2f}"
                ])
            
            order_desc = "最高" if order == "DESC" else "最低"
            period_desc = self._format_period(period)
            title = f"{period_desc} 营业收入{order_desc}前{limit}"
            
            formatted_result = self.result_formatter.format_table(headers, rows, title=title)
            
            return {
                'success': True,
                'result': formatted_result,
                'sql': None,
                'quick_path': True
            }
        else:
            return {
                'success': False,
                'error': f"未找到{period}的营收数据"
            }
    
    def _execute_roe_ranking(self, params: ExtractedParams) -> Dict[str, Any]:
        """执行ROE排名查询"""
        limit = params.limit
        order = params.order_by
        period = params.period or "20241231"
        
        sql = SQLTemplates.ROE_RANKING
        result = self.mysql_connector.execute_query(sql, {
            'period': period,
            'order': order,
            'limit': limit
        })
        
        if result and len(result) > 0:
            headers = ["排名", "股票代码", "股票名称", "ROE(%)", "净利润(亿元)"]
            rows = []
            
            for i, row in enumerate(result, 1):
                rows.append([
                    i,
                    row['ts_code'],
                    row['name'],
                    f"{row['roe']:.2f}",
                    f"{row['n_income'] / 100000000:.2f}"
                ])
            
            order_desc = "最高" if order == "DESC" else "最低"
            period_desc = self._format_period(period)
            title = f"{period_desc} ROE{order_desc}前{limit}"
            
            formatted_result = self.result_formatter.format_table(headers, rows, title=title)
            
            return {
                'success': True,
                'result': formatted_result,
                'sql': None,
                'quick_path': True
            }
        else:
            return {
                'success': False,
                'error': f"未找到{period}的ROE数据"
            }
    
    def _execute_announcement_query(self, params: ExtractedParams, processed_question: str) -> Dict[str, Any]:
        """执行公告查询"""
        if not params.stocks:
            return {
                'success': False,
                'error': "未识别到股票信息"
            }
        
        ts_code = params.stocks[0]
        stock_name = params.stock_names[0] if params.stock_names else ""
        
        # 根据参数选择合适的SQL
        if params.date:
            sql = SQLTemplates.ANNOUNCEMENT_BY_DATE
            query_params = {
                'ts_code': ts_code,
                'ann_date': params.date
            }
        elif params.date_range:
            sql = SQLTemplates.ANNOUNCEMENT_BY_RANGE
            query_params = {
                'ts_code': ts_code,
                'start_date': params.date_range[0],
                'end_date': params.date_range[1]
            }
        else:
            sql = SQLTemplates.ANNOUNCEMENT_LATEST
            query_params = {
                'ts_code': ts_code,
                'limit': 5
            }
        
        result = self.mysql_connector.execute_query(sql, query_params)
        
        if result and len(result) > 0:
            headers = ["公告日期", "公告标题", "链接"]
            rows = []
            
            for row in result:
                rows.append([
                    row['ann_date'],
                    row['title'],
                    row.get('pdf_url', '暂无链接')
                ])
            
            stock_info = f"{stock_name}（{ts_code}）" if stock_name else ts_code
            title = f"{stock_info}公告列表"
            
            formatted_result = self.result_formatter.format_table(headers, rows, title=title)
            
            return {
                'success': True,
                'result': formatted_result,
                'sql': None,
                'quick_path': True
            }
        else:
            return {
                'success': False,
                'error': f"未找到{stock_name or ts_code}的公告信息"
            }
    
    def _execute_sector_stocks_query(self, params: ExtractedParams) -> Dict[str, Any]:
        """执行板块成分股查询"""
        sector_name = params.sector or params.industry
        if not sector_name:
            return {
                'success': False,
                'error': "未识别到板块信息"
            }
        
        # 获取板块股票列表
        sector_stocks = self._get_sector_stocks(sector_name)
        if not sector_stocks:
            return {
                'success': False,
                'error': f"未找到{sector_name}的成分股"
            }
        
        # 查询股票基本信息
        sql = """
        SELECT ts_code, name, area, industry, market, list_date
        FROM tu_stock_basic
        WHERE ts_code IN :ts_codes
        """
        
        result = self.mysql_connector.execute_query(sql, {'ts_codes': sector_stocks})
        
        if result and len(result) > 0:
            headers = ["股票代码", "股票名称", "地区", "行业", "市场", "上市日期"]
            rows = []
            
            for row in result:
                rows.append([
                    row['ts_code'],
                    row['name'],
                    row['area'],
                    row['industry'],
                    row['market'],
                    row['list_date']
                ])
            
            title = f"{sector_name}成分股列表"
            formatted_result = self.result_formatter.format_table(headers, rows, title=title)
            
            return {
                'success': True,
                'result': formatted_result,
                'sql': None,
                'quick_path': True
            }
        else:
            return {
                'success': False,
                'error': f"未找到{sector_name}的成分股信息"
            }
    
    def _execute_kline_query(self, params: ExtractedParams, processed_question: str) -> Dict[str, Any]:
        """执行K线查询"""
        if not params.stocks:
            return {
                'success': False,
                'error': "未识别到股票信息"
            }
        
        ts_code = params.stocks[0]
        stock_name = params.stock_names[0] if params.stock_names else ""
        
        # 确定查询的日期范围
        if params.date_range:
            start_date, end_date = params.date_range
            days_desc = f"从{start_date}到{end_date}"
        else:
            # 默认最近90天
            days = 90
            date_range = date_intelligence.calculator.get_trading_days_range(days)
            if date_range:
                start_date, end_date = date_range
                start_date = start_date.replace('-', '')
                end_date = end_date.replace('-', '')
                days_desc = f"最近{days}天"
            else:
                return {
                'success': False,
                'error': "无法确定日期范围"
            }
        
        sql = SQLTemplates.KLINE_RANGE
        query_params = {
            'ts_code': ts_code,
            'start_date': start_date,
            'end_date': end_date
        }
        
        result = self.mysql_connector.execute_query(sql, query_params)
        
        if result and len(result) > 0:
            # 准备K线数据表格
            headers = ["日期", "开盘", "最高", "最低", "收盘", "涨跌幅", "成交量(万手)", "成交额(万元)"]
            rows = []
            
            for row in result[:30]:  # 只显示前30条
                rows.append([
                    row['trade_date'],
                    f"{row['open']:.2f}",
                    f"{row['high']:.2f}",
                    f"{row['low']:.2f}",
                    f"{row['close']:.2f}",
                    f"{row['pct_chg']:.2f}%",
                    f"{row['vol'] / 10000:.2f}",
                    f"{row['amount'] / 10000:.2f}"
                ])
            
            stock_info = f"{stock_name}（{ts_code}）" if stock_name else ts_code
            title = f"{stock_info}{days_desc}K线数据"
            
            formatted_result = self.result_formatter.format_table(headers, rows, title=title)
            
            if len(result) > 30:
                formatted_result += f"\n... 共{len(result)}条记录"
            
            return {
                'success': True,
                'result': formatted_result,
                'sql': None,
                'quick_path': True
            }
        else:
            return {
                'success': False,
                'error': f"未找到{stock_name or ts_code}的K线数据"
            }
    
    def _execute_volume_ranking(self, params: ExtractedParams, last_trading_date: str) -> Dict[str, Any]:
        """执行成交量排名查询 - 使用公共SQL模板"""
        trade_date = params.date or last_trading_date
        limit = params.limit
        
        # 使用公共的SQL模板
        sql = SQLTemplates.VOLUME_RANKING
        result = self.mysql_connector.execute_query(sql, {
            'trade_date': trade_date,
            'limit': limit
        })
        
        if result and len(result) > 0:
            headers = ["排名", "股票代码", "股票名称", "收盘价", "涨跌幅", "成交量(万手)", "成交额(万元)"]
            rows = []
            for i, row in enumerate(result, 1):
                rows.append([
                    str(i),
                    row['ts_code'],
                    row['name'],
                    f"{row['close']:.2f}",
                    f"{row['pct_chg']:.2f}%",
                    f"{row['vol'] / 10000:.2f}",
                    f"{row['amount'] / 10000:.2f}"
                ])
            
            formatted_result = self.result_formatter.format_table(
                headers, 
                rows, 
                title=f"成交量排名前{limit}（{trade_date}）"
            )
            
            return {
                'success': True,
                'result': formatted_result,
                'sql': sql,
                'quick_path': True
            }
        else:
            return {
                'success': False,
                'error': f"没有找到{trade_date}的成交量数据"
            }


# 导出主类
SQLAgent = SQLAgentModular