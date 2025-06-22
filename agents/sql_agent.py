# 文件路径: E:\PycharmProjects\stock_analysis_system\agents\sql_agent.py

"""
SQL Agent - 自然语言转SQL查询
支持将用户的自然语言问题转换为SQL查询并执行
"""
import re
import sys
import os
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


class SQLAgent:
    """SQL查询代理 - 处理自然语言到SQL的转换"""
    
    def __init__(self, llm_model_name: str = "deepseek-chat"):
        self.logger = setup_logger("sql_agent")
        self.mysql_connector = MySQLConnector()
        
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
        self.schema_info = self._get_schema_info()
        
        # 创建SQL工具包
        self.toolkit = SQLDatabaseToolkit(db=self.db, llm=self.llm)
        
        # 创建自定义prompt
        self.sql_prompt = self._create_sql_prompt()
        
        # 创建SQL agent
        self.agent = self._create_agent()
        
        # 对话记忆
        self.memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True
        )
        
        # 初始化查询缓存
        self._query_cache = {}
        
        self.logger.info("SQL Agent初始化完成")
    
    def _get_schema_info(self) -> Dict[str, Any]:
        """获取数据库schema信息"""
        schema_info = {}
        try:
            # 获取主要表的信息
            important_tables = ['tu_anns_d', 'tu_daily_detail', 'tu_moneyflow_dc', 
                              'tu_moneyflow_ind_dc', 'tu_irm_qa_sh', 'tu_irm_qa_sz']
            
            for table in important_tables:
                try:
                    info = self.mysql_connector.get_table_info(table)
                    schema_info[table] = info
                    self.logger.info(f"获取表 {table} 信息成功")
                except Exception as e:
                    self.logger.warning(f"获取表 {table} 信息失败: {e}")
            
            return schema_info
            
        except Exception as e:
            self.logger.error(f"获取schema信息失败: {e}")
            return {}
    
    def _get_last_trading_date(self) -> str:
        """获取最近的交易日期"""
        today = datetime.now()
        # 如果是周末，回退到周五
        if today.weekday() == 5:  # 周六
            last_trading = today - timedelta(days=1)
        elif today.weekday() == 6:  # 周日
            last_trading = today - timedelta(days=2)
        else:
            last_trading = today
        
        # 格式化为YYYYMMDD
        return last_trading.strftime("%Y%m%d")
    
    def _create_sql_prompt(self) -> PromptTemplate:
        """创建自定义的SQL prompt"""
        
        # 构建表描述
        table_descriptions = []
        for table_name, info in self.schema_info.items():
            if info and 'columns' in info:
                columns_desc = []
                for col in info['columns'][:10]:  # 只显示前10个重要列
                    columns_desc.append(f"  - {col['COLUMN_NAME']} ({col['DATA_TYPE']}): {col.get('COLUMN_COMMENT', '')}")
                
                table_desc = f"""
表名: {table_name}
描述: {self._get_table_description(table_name)}
主要列:
{chr(10).join(columns_desc)}
"""
                table_descriptions.append(table_desc)
        
        tables_info = "\n".join(table_descriptions)
        
        # 获取最近交易日
        last_trading_date = self._get_last_trading_date()
        
        prompt_template = f"""你是一个专业的股票数据分析师，精通SQL查询。
请根据用户的问题，生成准确的SQL查询语句。

数据库信息：
{tables_info}

重要提示：
1. 股票代码格式：使用ts_code字段，格式为"600519.SH"（沪市）或"000001.SZ"（深市）
2. 日期格式：使用trade_date或ann_date字段，格式为"YYYYMMDD"，如"20250422"
3. 今天是{datetime.now().strftime("%Y-%m-%d")}，最近的交易日是{last_trading_date}
4. 如果用户询问"最新"或"今天"的数据，请使用最近的交易日{last_trading_date}
5. 金额单位：财务数据通常以元为单位，大数字请转换为"亿元"显示
6. 查询限制：默认限制返回10条记录，除非用户指定
7. 排序规则：财务数据默认按金额降序，时间数据按最新优先

用户问题：{{question}}

请生成SQL查询语句，并用中文解释查询结果。
"""
        
        return PromptTemplate(
            input_variables=["question"],
            template=prompt_template
        )
    
    def _get_table_description(self, table_name: str) -> str:
        """获取表的中文描述"""
        descriptions = {
            'tu_anns_d': '上市公司公告信息表，包含公告标题、发布日期、PDF链接等',
            'tu_daily_detail': '股票日线行情数据，包含开高低收、成交量、市值等详细信息',
            'tu_moneyflow_dc': '个股资金流向数据，包含主力、散户等各类资金流向',
            'tu_moneyflow_ind_dc': '行业资金流向数据，包含各行业的资金流入流出情况',
            'tu_irm_qa_sh': '上交所投资者互动问答数据',
            'tu_irm_qa_sz': '深交所投资者互动问答数据',
            'stock_basic': '股票基本信息表，包含股票代码、名称、上市日期等',
            'daily': '股票日线行情数据，包含开高低收、成交量等',
            'income': '上市公司利润表数据，包含营业收入、净利润等',
            'balancesheet': '上市公司资产负债表数据，包含总资产、负债等'
        }
        return descriptions.get(table_name, '数据表')
    
    def _create_agent(self):
        """创建SQL agent"""
        return create_sql_agent(
            llm=self.llm,
            toolkit=self.toolkit,
            agent_type=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
            verbose=True,
            handle_parsing_errors=True,
            max_iterations=5,
            early_stopping_method="force"
        )
    
    def query(self, question: str) -> Dict[str, Any]:
        """
        执行自然语言查询 - 返回字符串结果
        
        Args:
            question: 用户的自然语言问题
            
        Returns:
            查询结果字符串
        """
        # 输入验证
        if not question or not question.strip():
            return {
                'success': False,
                'error': '查询内容不能为空',
                'result': None
            }
        
        try:
            self.logger.info(f"接收查询: {question}")
            
            # 检查缓存
            cache_key = self._get_cache_key(question)
            if cache_key in self._query_cache:
                self.logger.info("使用缓存结果")
                return {
                'success': True,
                'result': self._query_cache[cache_key],
                'sql': None,
                'cached': True
            }
            
            # 预处理问题
            processed_question = self._preprocess_question(question)
            
            # 使用agent执行查询
            result = self.agent.run(processed_question)
            
            # 后处理结果 - 确保返回字符串
            processed_result = self._postprocess_result(result)
            
            # 转换为字符串
            if isinstance(processed_result, dict):
                # 如果是字典，提取explanation或转换为格式化字符串
                if 'explanation' in processed_result:
                    final_result = processed_result['explanation']
                else:
                    final_result = self._format_dict_result(processed_result)
            else:
                final_result = str(processed_result)
            
            # 缓存结果
            self._query_cache[cache_key] = final_result
            
            # 记录到内存
            self.memory.save_context(
                {"input": question},
                {"output": final_result}
            )
            
            return {
                'success': True,
                'result': final_result,
                'sql': None,
                'cached': False
            }
            
        except Exception as e:
            self.logger.error(f"查询执行失败: {e}")
            error_msg = f"查询执行失败: {str(e)}"
            return {
                'success': False,
                'result': None,
                'error': error_msg,
                'cached': False
            }
    
    def _get_cache_key(self, question: str) -> str:
        """生成缓存键"""
        # 简单的缓存键生成，可以根据需要优化
        return f"{question.lower().strip()}_{self._get_last_trading_date()}"
    
    def _format_dict_result(self, result_dict: dict) -> str:
        """格式化字典结果为字符串"""
        formatted_parts = []
        
        if 'data' in result_dict:
            formatted_parts.append("查询结果：")
            data = result_dict['data']
            if isinstance(data, list) and data:
                # 格式化数据表格
                df = pd.DataFrame(data)
                formatted_parts.append(df.to_string(index=False))
        
        if 'row_count' in result_dict:
            formatted_parts.append(f"\n共找到 {result_dict['row_count']} 条记录")
        
        if 'sql' in result_dict:
            formatted_parts.append(f"\n执行的SQL: {result_dict['sql']}")
        
        return "\n".join(formatted_parts) if formatted_parts else str(result_dict)
    
    def _preprocess_question(self, question: str) -> str:
        """预处理用户问题"""
        # 识别并转换股票代码格式
        stock_name_mapping = {
            '茅台': '贵州茅台(600519.SH)',
            '五粮液': '五粮液(000858.SZ)',
            '平安': '中国平安(601318.SH)',
            '招行': '招商银行(600036.SH)',
            '宁德时代': '宁德时代(300750.SZ)',
            '比亚迪': '比亚迪(002594.SZ)',
            '中国移动': '中国移动(600941.SH)',
            '工商银行': '工商银行(601398.SH)',
            '建设银行': '建设银行(601939.SH)',
            '农业银行': '农业银行(601288.SH)'
        }
        
        processed = question
        for name, full_name in stock_name_mapping.items():
            if name in processed:
                processed = processed.replace(name, full_name)
        
        # 处理时间相关词汇
        time_mappings = {
            '今天': f'{self._get_last_trading_date()}',
            '最新': f'{self._get_last_trading_date()}',
            '昨天': f'{(datetime.now() - timedelta(days=1)).strftime("%Y%m%d")}',
            '本周': f'最近5个交易日',
            '本月': f'{datetime.now().strftime("%Y%m")}月'
        }
        
        for time_word, replacement in time_mappings.items():
            if time_word in processed:
                processed = processed.replace(time_word, replacement)
        
        # 识别并转换日期格式
        year_pattern = r'(\d{4})年'
        year_match = re.search(year_pattern, processed)
        if year_match:
            year = year_match.group(1)
            processed = processed.replace(f"{year}年", f"{year}0101到{year}1231期间")
        
        return processed
    
    def _postprocess_result(self, result: Any) -> str:
        """后处理查询结果 - 确保返回字符串"""
        # 如果结果是字符串，直接返回
        if isinstance(result, str):
            # 尝试美化格式
            if "```" in result:
                # 提取代码块中的内容
                code_blocks = re.findall(r'```(.*?)```', result, re.DOTALL)
                if code_blocks:
                    # 返回纯文本结果，不要包装成字典
                    return result
            return result
        
        # 如果是其他类型，转换为字符串
        return str(result)
    
    def execute_direct_sql(self, sql: str) -> Dict[str, Any]:
        """
        直接执行SQL查询（供高级用户使用）
        
        Args:
            sql: SQL查询语句
            
        Returns:
            查询结果
        """
        try:
            self.logger.info(f"执行SQL: {sql}")
            
            # 安全检查
            if not self._is_safe_query(sql):
                raise ValueError("不安全的SQL查询")
            
            # 执行查询
            df = self.mysql_connector.execute_query_df(sql)
            
            return {
                'success': True,
                'sql': sql,
                'data': df.to_dict('records'),
                'row_count': len(df),
                'columns': list(df.columns)
            }
            
        except Exception as e:
            self.logger.error(f"SQL执行失败: {e}")
            return {
                'success': False,
                'sql': sql,
                'error': str(e)
            }
    
    def _is_safe_query(self, sql: str) -> bool:
        """检查SQL查询是否安全"""
        # 转换为小写进行检查
        sql_lower = sql.lower()
        
        # 危险关键词
        dangerous_keywords = [
            'drop', 'delete', 'truncate', 'update', 'insert', 
            'alter', 'create', 'grant', 'revoke'
        ]
        
        for keyword in dangerous_keywords:
            if keyword in sql_lower:
                return False
        
        return True
    
    def get_query_suggestions(self) -> List[str]:
        """获取查询建议"""
        suggestions = [
            "查询贵州茅台最新股价",
            "比较银行股最新的市盈率",
            "查找最近发布年报的公司",
            "统计2024年第一季度业绩增长最快的公司",
            "查询总市值最大的10家公司",
            "分析白酒行业最近的资金流向",
            "查找最近有重要公告的公司",
            "查询今天涨幅最大的股票"
        ]
        return suggestions
    
    def analyze_query_complexity(self, question: str) -> Dict[str, Any]:
        """分析查询复杂度"""
        complexity_indicators = {
            'simple': ['查询', '查找', '显示', '列出'],
            'medium': ['比较', '统计', '计算', '排序'],
            'complex': ['分析', '预测', '关联', '趋势', '相关性']
        }
        
        complexity = 'simple'
        for level, keywords in complexity_indicators.items():
            if any(keyword in question for keyword in keywords):
                complexity = level
        
        # 估计涉及的表
        involved_tables = []
        table_keywords = {
            'tu_anns_d': ['公告', '年报', '季报', '报告'],
            'tu_daily_detail': ['股价', '价格', '行情', '涨跌', '成交量', '市值'],
            'tu_moneyflow_dc': ['资金', '主力', '散户', '流入', '流出'],
            'tu_moneyflow_ind_dc': ['行业资金', '板块资金'],
            'tu_irm_qa_sh': ['互动', '问答', '上交所'],
            'tu_irm_qa_sz': ['互动', '问答', '深交所']
        }
        
        for table, keywords in table_keywords.items():
            if any(keyword in question for keyword in keywords):
                involved_tables.append(table)
        
        return {
            'complexity': complexity,
            'involved_tables': involved_tables,
            'estimated_time': {
                'simple': '1-2秒',
                'medium': '2-5秒',
                'complex': '5-10秒'
            }.get(complexity, '未知')
        }
    
    def clear_cache(self):
        """清空查询缓存"""
        self._query_cache.clear()
        self.logger.info("查询缓存已清空")


# 测试代码
if __name__ == "__main__":
    print("SQL Agent 模块优化完成!")
    print("主要改进：")
    print("1. 修复了返回格式问题 - 现在总是返回字符串")
    print("2. 添加了查询缓存机制")
    print("3. 改进了非交易日处理")
    print("4. 优化了时间相关查询")
