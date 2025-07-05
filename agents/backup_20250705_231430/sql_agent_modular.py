# 文件路径: E:\PycharmProjects\stock_analysis_system\agents\sql_agent_v2.py

"""
SQL Agent V2 - 模块化架构版本
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


class SQLAgentModular:
    """SQL查询代理 V2 - 模块化架构版本"""
    
    def __init__(self, llm_model_name: str = "deepseek-chat"):
        self.logger = setup_logger("sql_agent_v2")
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
    
    def _get_schema_info(self) -> Dict[str, Any]:
        """获取数据库schema信息 - 使用Schema知识库优化性能"""
        schema_info = {}
        try:
            # 使用Schema知识库快速获取表信息（<10ms）
            self.logger.info("使用Schema知识库获取表结构信息...")
            
            # 获取所有表的基础信息
            for table_name, table_data in schema_kb.table_knowledge.items():
                schema_info[table_name] = {
                    'columns': table_data['fields'],
                    'description': table_data.get('cn_name', ''),
                    'type': table_data.get('type', 'table')
                }
                
            # 获取列的中文映射信息
            for key, value in schema_kb.column_mappings.items():
                table_name, column_name = key
                if table_name in schema_info:
                    # 找到对应的列并添加中文名
                    for col in schema_info[table_name]['columns']:
                        if col['name'] == column_name:
                            col['cn_name'] = value
                            break
                            
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
                        'cn_name': schema_kb.get_column_cn_name(table_name, col['name'])
                    })
                schema_info[table_name] = {
                    'columns': columns,
                    'description': schema_kb.get_table_cn_name(table_name),
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
    
    def _try_quick_query(self, question: str) -> Optional[Dict[str, Any]]:
        """尝试使用快速查询模板"""
        # 日期智能处理
        processed_question = date_intelligence.process_query(question)
        self.logger.info(f"日期智能处理后的查询: {processed_question}")
        
        # 匹配查询模板
        template, params = match_query_template(processed_question)
        if not template:
            return None
        
        self.logger.info(f"匹配到快速查询模板: {template.name}")
        
        try:
            # 使用统一的参数提取器
            extracted_params = self.param_extractor.extract_all_params(processed_question, template)
            
            # 如果有错误，返回错误信息
            if extracted_params.error:
                error_info = self.error_handler.handle_error(
                    extracted_params.error,
                    "INVALID_STOCK"
                )
                return {
                    'success': False,
                    'error': error_info.user_message,
                    'suggestion': error_info.suggestion
                }
            
            # 使用统一的查询验证器
            validation_errors = self.query_validator.validate_params(extracted_params, template)
            if validation_errors:
                return self.error_handler.format_error(
                    ErrorCode.VALIDATION_ERROR,
                    "; ".join(validation_errors)
                )
            
            # 获取最新交易日
            last_trading_date = date_intelligence.get_latest_trading_day()
            if not last_trading_date:
                last_trading_date = datetime.now().strftime('%Y%m%d')
            else:
                last_trading_date = last_trading_date.replace('-', '')
            
            # 执行特定模板的快速查询
            return self._execute_template_query(template, extracted_params, processed_question, last_trading_date)
            
        except Exception as e:
            self.logger.error(f"快速查询执行失败: {str(e)}")
            return self.error_handler.format_error(
                ErrorCode.EXECUTION_ERROR,
                f"查询执行失败: {str(e)}"
            )
    
    def _execute_template_query(self, template: Any, params: ExtractedParams, 
                              processed_question: str, last_trading_date: str) -> Optional[Dict[str, Any]]:
        """执行模板查询 - 使用模块化组件"""
        try:
            # 根据不同的模板执行相应的查询
            if template.name == '股价查询':
                return self._execute_stock_price_query(params, last_trading_date)
            elif template.name == '估值查询':
                return self._execute_valuation_query(params, last_trading_date)
            elif template.name == '市值排名':
                return self._execute_market_cap_ranking(params, last_trading_date)
            elif template.name == '涨幅排名':
                return self._execute_pct_chg_ranking(params, last_trading_date)
            elif template.name == '成交额排名':
                return self._execute_amount_ranking(params, last_trading_date)
            elif template.name == 'K线查询':
                return self._execute_kline_query(params, processed_question)
            elif template.name == '成交量查询':
                return self._execute_volume_query(params, last_trading_date)
            elif template.name == '主力净流入排行':
                return self._execute_money_flow_ranking(params, last_trading_date, is_outflow=False)
            elif template.name == '主力净流出排行':
                return self._execute_money_flow_ranking(params, last_trading_date, is_outflow=True)
            elif template.name == '个股主力资金':
                return self._execute_stock_money_flow(params, last_trading_date)
            elif template.name == '板块主力资金':
                return self._execute_sector_money_flow(params, last_trading_date)
            elif template.name == '财务数据查询':
                return self._execute_financial_query(params)
            elif template.name == '利润查询':
                return self._execute_profit_query(params)
            elif template.name == 'PE排名':
                return self._execute_pe_ranking(params, last_trading_date)
            elif template.name == 'PB排名':
                return self._execute_pb_ranking(params, last_trading_date)
            elif template.name == '净利润排名':
                return self._execute_profit_ranking(params)
            elif template.name == '营收排名':
                return self._execute_revenue_ranking(params)
            elif template.name == 'ROE排名':
                return self._execute_roe_ranking(params)
            elif template.name == '公告查询':
                return self._execute_announcement_query(params, processed_question)
            elif template.name == '板块成分股':
                return self._execute_sector_stocks_query(params)
            else:
                return None
                
        except Exception as e:
            self.logger.error(f"模板查询执行失败: {str(e)}")
            return self.error_handler.format_error(
                ErrorCode.EXECUTION_ERROR,
                f"查询执行失败: {str(e)}"
            )
    
    def _execute_stock_price_query(self, params: ExtractedParams, last_trading_date: str) -> Dict[str, Any]:
        """执行股价查询"""
        if not params.stocks:
            return self.error_handler.format_error(
                ErrorCode.MISSING_REQUIRED_PARAM,
                "未识别到股票信息"
            )
        
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
            
            return {
                'success': True,
                'result': formatted_result,
                'sql': None,  # 不暴露SQL
                'quick_path': True
            }
        else:
            return self.error_handler.format_error(
                ErrorCode.NO_DATA,
                f"未找到{stock_name or ts_code}在{trade_date}的股价数据"
            )
    
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
            return self.error_handler.format_error(
                ErrorCode.NO_DATA,
                f"未找到{trade_date}的市值数据"
            )
    
    def _execute_financial_query(self, params: ExtractedParams) -> Dict[str, Any]:
        """执行财务数据查询"""
        if not params.stocks:
            return self.error_handler.format_error(
                ErrorCode.MISSING_REQUIRED_PARAM,
                "未识别到股票信息"
            )
        
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
            return self.error_handler.format_error(
                ErrorCode.NO_DATA,
                f"未找到{stock_name or ts_code}的财务数据"
            )
    
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
        """执行查询"""
        try:
            # 输入验证
            if not question or not question.strip():
                return self.error_handler.format_error(
                    ErrorCode.INVALID_INPUT,
                    "查询内容不能为空"
                )
            
            question = question.strip()
            self.logger.info(f"收到查询请求: {question}")
            
            # 尝试快速查询路径
            quick_result = self._try_quick_query(question)
            if quick_result:
                self.logger.info("使用快速查询路径成功")
                return quick_result
            
            # 降级到传统LLM路径
            self.logger.info("使用传统LLM查询路径")
            return self._execute_llm_query(question)
            
        except Exception as e:
            self.logger.error(f"查询执行异常: {str(e)}")
            return self.error_handler.format_error(
                ErrorCode.SYSTEM_ERROR,
                f"系统错误: {str(e)}"
            )
    
    def _execute_llm_query(self, question: str) -> Dict[str, Any]:
        """执行传统的LLM查询"""
        try:
            # 日期智能处理
            processed_question = date_intelligence.process_query(question)
            
            # 使用参数提取器
            extracted_params = self.param_extractor.extract_all_params(processed_question)
            
            # 构建增强的查询
            enhanced_question = self._build_enhanced_question(processed_question, extracted_params)
            
            # 执行查询
            result = self.agent.invoke({"input": enhanced_question})
            
            # 解析结果
            if isinstance(result, dict) and 'output' in result:
                output = result['output']
                
                # 尝试从输出中提取SQL和结果
                sql_result = self.flexible_parser.parse(output)
                
                if sql_result['success']:
                    # 格式化结果
                    if isinstance(sql_result['result'], list) and sql_result['result']:
                        formatted_result = self.result_formatter.format_records(sql_result['result'])
                    else:
                        formatted_result = str(sql_result['result'])
                    
                    return {
                        'success': True,
                        'result': formatted_result,
                        'sql': sql_result.get('sql'),
                        'quick_path': False
                    }
                else:
                    return self.error_handler.format_error(
                        ErrorCode.PARSE_ERROR,
                        "无法解析查询结果"
                    )
            else:
                return self.error_handler.format_error(
                    ErrorCode.EXECUTION_ERROR,
                    "查询执行失败"
                )
                
        except Exception as e:
            self.logger.error(f"LLM查询执行失败: {str(e)}")
            return self.error_handler.format_error(
                ErrorCode.SYSTEM_ERROR,
                f"系统错误: {str(e)}"
            )
    
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
    
    # 其他查询方法的实现...
    def _execute_kline_query(self, params: ExtractedParams, processed_question: str) -> Dict[str, Any]:
        """执行K线查询"""
        if not params.stocks:
            return self.error_handler.format_error(
                ErrorCode.MISSING_REQUIRED_PARAM,
                "未识别到股票信息"
            )
        
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
                return self.error_handler.format_error(
                    ErrorCode.DATE_ERROR,
                    "无法确定日期范围"
                )
        
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
            return self.error_handler.format_error(
                ErrorCode.NO_DATA,
                f"未找到{stock_name or ts_code}的K线数据"
            )


# 导出主类
SQLAgent = SQLAgentModular