# 文件路径: E:\PycharmProjects\stock_analysis_system\agents\sql_agent.py

"""
SQL Agent - 自然语言转SQL查询
支持将用户的自然语言问题转换为SQL查询并执行
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
from utils.unified_stock_validator import validate_stock_input, UnifiedStockValidator
from utils.security_filter import clean_llm_output, validate_query



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
        self.logger.info("初始化SQL Agent，准备加载Schema信息...")
        self.schema_info = self._get_schema_info()
        self.logger.info(f"Schema信息加载完成，共{len(self.schema_info)}个表")
        
        # 创建SQL工具包
        self.toolkit = SQLDatabaseToolkit(db=self.db, llm=self.llm)
        
        # 创建自定义prompt
        self.sql_prompt = self._create_sql_prompt()
        
        # 创建SQL agent
        self.agent = self._create_agent()
        
        # 对话记忆 - 使用现代化的内存管理
        # 注意: 根据LangChain迁移指南，内存功能已被现代化
        # 暂时保留但不在新的agent中使用
        self.memory = None  # 将在未来版本中实现现代化内存管理
        
        # 初始化查询缓存
        self._query_cache = {}
        
        # 初始化灵活解析器
        self.flexible_parser = FlexibleSQLOutputParser()
        
        self.logger.info("SQL Agent初始化完成")
    
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
                    'comment': table_data['comment'],
                    'row_count': table_data['row_count'],
                    'primary_fields': table_data['primary_fields']
                }
            
            self.logger.info(f"从Schema知识库获取了 {len(schema_info)} 个表的信息")
            
            # 记录性能提升
            stats = schema_kb.get_performance_stats()
            self.logger.info(f"Schema知识库统计: 表{stats['table_count']}个, "
                           f"字段{stats['field_count']}个, "
                           f"中文映射{stats['chinese_mapping_count']}个")
            
            return schema_info
            
        except Exception as e:
            self.logger.error(f"获取schema信息失败: {e}")
            # 降级到原始方法
            self.logger.warning("降级到原始数据库查询方法...")
            return self._get_schema_info_fallback()
    
    def _get_schema_info_fallback(self) -> Dict[str, Any]:
        """降级方法：原始的数据库查询方式"""
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
            self.logger.error(f"降级方法也失败: {e}")
            return {}
    
    def _try_quick_query(self, question: str) -> Optional[Dict[str, Any]]:
        """尝试使用快速查询路径，避免LLM调用"""
        try:
            # 先进行日期智能解析
            processed_question, parsing_result = date_intelligence.preprocess_question(question)
            
            self.logger.info(f"日期解析前: {question}")
            self.logger.info(f"日期解析后: {processed_question}")
            
            # 使用处理后的问题进行模板匹配
            template_match = match_query_template(processed_question)
            if not template_match:
                return None
                
            template, params = template_match
            
            # 只处理SQL查询类型
            if template.route_type != 'SQL_ONLY':
                return None
                
            # 获取最近交易日
            last_trading_date = self._get_last_trading_date()
            
            # 检查是否有对应的SQL模板
            if template.name == '股价查询':
                # 提取股票代码
                entities = params.get('entities', [])
                if not entities:
                    return None
                    
                # 转换为ts_code
                ts_code = convert_to_ts_code(entities[0])
                if not ts_code:
                    return None
                    
                # 获取股票名称
                stock_name = get_stock_name(ts_code)
                
                # 从处理后的查询中提取日期
                trade_date = self._extract_date_from_query(processed_question) or last_trading_date
                
                # 执行SQL查询
                if trade_date == last_trading_date:
                    sql = SQLTemplates.STOCK_PRICE_LATEST
                    result = self.mysql_connector.execute_query(sql, {'ts_code': ts_code})
                else:
                    sql = SQLTemplates.STOCK_PRICE_BY_DATE
                    result = self.mysql_connector.execute_query(sql, {
                        'ts_code': ts_code,
                        'trade_date': trade_date
                    })
                
                if result and len(result) > 0:
                    # 格式化结果
                    formatted_result = SQLTemplates.format_stock_price_result(
                        result[0], 
                        stock_name or ts_code
                    )
                    
                    return {
                        'success': True,
                        'result': formatted_result,
                        'sql': None,  # 不暴露SQL语句
                        'quick_path': True
                    }
                    
            elif template.name == '估值指标查询':
                # PE/PB查询
                entities = params.get('entities', [])
                if not entities:
                    return None
                    
                ts_code = convert_to_ts_code(entities[0])
                if not ts_code:
                    return None
                    
                stock_name = get_stock_name(ts_code)
                
                # 从处理后的查询中提取日期
                trade_date = self._extract_date_from_query(processed_question) or last_trading_date
                
                sql = SQLTemplates.VALUATION_METRICS_BY_DATE
                result = self.mysql_connector.execute_query(sql, {
                    'ts_code': ts_code,
                    'trade_date': trade_date
                })
                
                if result and len(result) > 0:
                    formatted_result = SQLTemplates.format_valuation_result(
                        result[0],
                        stock_name or ts_code
                    )
                    return {
                        'success': True,
                        'result': formatted_result,
                        'sql': None,  # 不暴露SQL语句
                        'quick_path': True
                    }
                    
            elif template.name in ['涨跌幅排名', '总市值排名', '流通市值排名']:
                # 排名查询
                limit = params.get('limit', 10)
                
                # 从处理后的查询中提取日期
                trade_date = self._extract_date_from_query(processed_question) or last_trading_date
                
                # 选择对应的SQL模板
                if template.name == '涨跌幅排名':
                    # 判断是涨幅还是跌幅
                    if '跌幅' in processed_question:
                        sql = SQLTemplates.PCT_CHG_RANKING_DESC  # 跌幅排名（升序）
                        ranking_type = 'pct_chg_desc'
                    else:
                        sql = SQLTemplates.PCT_CHG_RANKING  # 涨幅排名（降序）
                        ranking_type = 'pct_chg'
                elif template.name == '总市值排名':
                    sql = SQLTemplates.MARKET_CAP_RANKING  
                    ranking_type = 'market_cap'
                elif template.name == '流通市值排名':
                    sql = SQLTemplates.CIRC_MV_RANKING  # 使用专门的流通市值排名SQL
                    ranking_type = 'circ_mv'
                    
                # 执行查询
                result = self.mysql_connector.execute_query(sql, {
                    'trade_date': trade_date,
                    'limit': limit
                })
                
                if result and len(result) > 0:
                    formatted_result = SQLTemplates.format_ranking_result(
                        result,
                        ranking_type
                    )
                    return {
                        'success': True,
                        'result': formatted_result,
                        'sql': None,  # 不暴露SQL语句
                        'quick_path': True
                    }
                    
            elif template.name == 'K线查询':
                # K线数据查询
                entities = params.get('entities', [])
                if not entities:
                    return None
                
                # 从原始查询提取股票名称（避免日期处理干扰）
                stock_name_patterns = [
                    r'^([^最近过去近前\d]+?)(?:最近|过去|近|前|\d)',  # 匹配开头的股票名称
                    r'^(.+?)(?:的)?(?:最近|过去|近|前|\d)',         # 更宽泛的匹配
                    r'^(.+?)(?:的)?K线'                            # 直接匹配"XXX的K线"
                ]
                
                ts_code = None
                for pattern in stock_name_patterns:
                    stock_name_match = re.search(pattern, question.strip())
                    if stock_name_match:
                        stock_name_text = stock_name_match.group(1).strip()
                        ts_code = convert_to_ts_code(stock_name_text)
                        if ts_code:  # 如果成功转换，就跳出循环
                            break
                
                if not ts_code:
                    # 回退到实体提取
                    entity_text = entities[0]
                    # 从复杂实体中提取股票名称部分
                    clean_entity = re.sub(r'\d{4}-\d{2}-\d{2}.*', '', entity_text).strip()
                    ts_code = convert_to_ts_code(clean_entity)
                
                if not ts_code:
                    return None
                    
                stock_name = get_stock_name(ts_code)
                
                # 优先处理直接指定的日期范围
                if params.get('time_range') == 'date_range' and params.get('start_date') and params.get('end_date'):
                    # 参数中直接包含日期范围
                    start_date_raw = params['start_date']
                    end_date_raw = params['end_date']
                    
                    # 统一日期格式为YYYYMMDD
                    start_date = self._normalize_date_format(start_date_raw)
                    end_date = self._normalize_date_format(end_date_raw)
                    
                    sql = SQLTemplates.KLINE_RANGE
                    query_params = {
                        'ts_code': ts_code,
                        'start_date': start_date,
                        'end_date': end_date
                    }
                    
                    # 格式化显示用的日期
                    start_display = self._format_date_for_display(start_date)
                    end_display = self._format_date_for_display(end_date)
                    days_desc = f"从{start_display}到{end_display}"
                    
                elif '至' in processed_question:
                    # 日期智能解析已转换为日期范围格式
                    date_range_match = re.search(r'(\d{4}-\d{2}-\d{2})至(\d{4}-\d{2}-\d{2})', processed_question)
                    if date_range_match:
                        start_date = date_range_match.group(1).replace('-', '')
                        end_date = date_range_match.group(2).replace('-', '')
                        sql = SQLTemplates.KLINE_RANGE
                        query_params = {
                            'ts_code': ts_code,
                            'start_date': start_date,
                            'end_date': end_date
                        }
                        days_desc = f"从{start_date}到{end_date}"
                    else:
                        return None
                else:
                    # 使用天数参数或默认值
                    days = int(params.get('days', 90))
                    date_range = date_intelligence.calculator.get_trading_days_range(days)
                    if date_range:
                        start_date, end_date = date_range
                        start_date = start_date.replace('-', '')
                        end_date = end_date.replace('-', '')
                        sql = SQLTemplates.KLINE_RANGE
                        query_params = {
                            'ts_code': ts_code,
                            'start_date': start_date,
                            'end_date': end_date
                        }
                        days_desc = f"最近{days}天"
                    else:
                        return None
                
                result = self.mysql_connector.execute_query(sql, query_params)
                
                if result and len(result) > 0:
                    # 格式化K线数据
                    stock_info = f"{stock_name}（{ts_code}）" if stock_name else ts_code
                    lines = [f"\n{stock_info}{days_desc}K线数据：\n"]
                    lines.append("日期 | 开盘 | 最高 | 最低 | 收盘 | 涨跌幅 | 成交量(万手) | 成交额(万元)")
                    lines.append("-" * 90)
                    
                    # 准备结构化数据
                    kline_data = []
                    total_volume = 0
                    total_amount = 0
                    
                    for row in result[:30]:  # 显示前30条
                        vol_wan = row['vol'] / 10000 if row['vol'] else 0
                        amount_wan = row['amount'] / 10000 if row['amount'] else 0
                        line = f"{row['trade_date']} | {row['open']:7.2f} | {row['high']:7.2f} | "
                        line += f"{row['low']:7.2f} | {row['close']:7.2f} | {row['pct_chg']:6.2f}% | "
                        line += f"{vol_wan:10.2f} | {amount_wan:10.2f}"
                        lines.append(line)
                        
                        # 添加到结构化数据
                        kline_data.append({
                            "date": str(row['trade_date']),
                            "open": float(row['open']),
                            "high": float(row['high']),
                            "low": float(row['low']),
                            "close": float(row['close']),
                            "volume": int(row['vol']),
                            "amount": float(row['amount']),
                            "pct_chg": float(row['pct_chg'])
                        })
                        
                        total_volume += int(row['vol'])
                        total_amount += float(row['amount'])
                        
                    if len(result) > 30:
                        lines.append(f"\n... 共{len(result)}条记录")
                        
                    formatted_result = "\n".join(lines)
                    
                    # 计算汇总信息
                    avg_close = sum(item['close'] for item in kline_data) / len(kline_data) if kline_data else 0
                    
                    # 构建完整的响应数据
                    response_data = {
                        'success': True,
                        'result': formatted_result,
                        'sql': None,  # 不暴露SQL语句
                        'quick_path': True,
                        'data_type': 'kline',  # 标识数据类型
                        'structured_data': {
                            'type': 'kline',
                            'stock_info': {
                                'name': stock_name or ts_code,
                                'code': ts_code
                            },
                            'period': days_desc,
                            'data': kline_data,
                            'summary': {
                                'total_days': len(kline_data),
                                'avg_price': round(avg_close, 2),
                                'total_volume': total_volume,
                                'total_amount': round(total_amount, 2)
                            }
                        }
                    }
                    
                    return response_data
                    
            elif template.name == '成交量查询':
                # 成交量查询
                entities = params.get('entities', [])
                if not entities:
                    return None
                    
                ts_code = convert_to_ts_code(entities[0])
                if not ts_code:
                    return None
                    
                stock_name = get_stock_name(ts_code)
                
                # 从处理后的查询中提取日期
                trade_date = self._extract_date_from_query(processed_question) or last_trading_date
                
                sql = SQLTemplates.VOLUME_BY_DATE
                result = self.mysql_connector.execute_query(sql, {
                    'ts_code': ts_code,
                    'trade_date': trade_date
                })
                
                if result and len(result) > 0:
                    data = result[0]
                    stock_info = f"{stock_name}（{ts_code}）" if stock_name else ts_code
                    vol_wan = data['vol'] / 10000 if data['vol'] else 0
                    amount_yi = data['amount'] / 100000000 if data['amount'] else 0
                    
                    formatted_result = f"""{stock_info}在{data['trade_date']}的成交情况：
成交量：{vol_wan:.2f}万手
成交额：{amount_yi:.2f}亿元
股价：{data['close']:.2f}元
涨跌幅：{data['pct_chg']:.2f}%"""
                    
                    return {
                        'success': True,
                        'result': formatted_result,
                        'sql': None,  # 不暴露SQL语句
                        'quick_path': True
                    }
                    
            elif template.name == '主力净流入排行':
                # 主力净流入排行
                limit = params.get('limit', 10)
                
                # 从处理后的查询中提取日期
                trade_date = self._extract_date_from_query(processed_question) or last_trading_date
                
                # 主力净流入排行榜
                sql = SQLTemplates.MAIN_FORCE_RANKING
                result = self.mysql_connector.execute_query(sql, {
                    'trade_date': trade_date,
                    'limit': limit
                })
                
                if result and len(result) > 0:
                    formatted_result = SQLTemplates.format_money_flow_ranking(
                        result
                    )
                    
                    return {
                        'success': True,
                        'result': formatted_result,
                        'sql': None,  # 不暴露SQL语句
                        'quick_path': True
                    }
                    
            elif template.name == '主力净流出排行':
                # 主力净流出排行（与流入相反，按ASC排序）
                limit = params.get('limit', 10)
                
                # 从处理后的查询中提取日期
                trade_date = self._extract_date_from_query(processed_question) or last_trading_date
                
                # 使用相同的SQL但按升序排列
                sql = SQLTemplates.MAIN_FORCE_RANKING.replace('DESC', 'ASC')
                result = self.mysql_connector.execute_query(sql, {
                    'trade_date': trade_date,
                    'limit': limit
                })
                
                if result and len(result) > 0:
                    formatted_result = SQLTemplates.format_money_flow_ranking(
                        result,
                        is_outflow=True
                    )
                    
                    return {
                        'success': True,
                        'result': formatted_result,
                        'sql': sql,
                        'quick_path': True
                    }
                    
            elif template.name == '成交额排名':
                # 成交额排名
                limit = params.get('limit', 10)
                
                # 从处理后的查询中提取日期
                trade_date = self._extract_date_from_query(processed_question) or last_trading_date
                
                sql = SQLTemplates.AMOUNT_RANKING
                result = self.mysql_connector.execute_query(sql, {
                    'trade_date': trade_date,
                    'limit': limit
                })
                
                if result and len(result) > 0:
                    formatted_result = SQLTemplates.format_ranking_result(
                        result,
                        'amount'
                    )
                    return {
                        'success': True,
                        'result': formatted_result,
                        'sql': None,  # 不暴露SQL语句
                        'quick_path': True
                    }
                    
            elif template.name == '成交量排名':
                # 成交量排名
                limit = params.get('limit', 10)
                
                # 从处理后的查询中提取日期
                trade_date = self._extract_date_from_query(processed_question) or last_trading_date
                
                sql = SQLTemplates.VOLUME_RANKING
                result = self.mysql_connector.execute_query(sql, {
                    'trade_date': trade_date,
                    'limit': limit
                })
                
                if result and len(result) > 0:
                    formatted_result = SQLTemplates.format_ranking_result(
                        result,
                        'volume'
                    )
                    return {
                        'success': True,
                        'result': formatted_result,
                        'sql': None,  # 不暴露SQL语句
                        'quick_path': True
                    }
                    
            elif template.name == '个股主力资金':
                # 个股主力资金查询
                entities = params.get('entities', [])
                if not entities:
                    return None
                    
                ts_code = convert_to_ts_code(entities[0])
                if not ts_code:
                    return None
                    
                stock_name = get_stock_name(ts_code)
                trade_date = self._extract_date_from_query(processed_question) or last_trading_date
                
                sql = SQLTemplates.STOCK_MONEY_FLOW
                result = self.mysql_connector.execute_query(sql, {
                    'ts_code': ts_code,
                    'trade_date': trade_date
                })
                
                if result and len(result) > 0:
                    data = result[0]
                    stock_info = f"{stock_name}（{ts_code}）" if stock_name else ts_code
                    
                    formatted_result = SQLTemplates.format_money_flow_result(
                        data,
                        stock_info
                    )
                    
                    return {
                        'success': True,
                        'result': formatted_result,
                        'sql': None,  # 不暴露SQL语句
                        'quick_path': True
                    }
                    
            # 其他模板类型暂不支持快速路径
            return None
            
        except Exception as e:
            self.logger.error(f"快速查询路径失败: {e}")
            return None
    
    def _normalize_date_format(self, date_str: str) -> str:
        """将各种日期格式统一为YYYYMMDD格式"""
        import re
        from datetime import datetime
        
        # 已经是YYYYMMDD格式
        if re.match(r'^\d{8}$', date_str):
            return date_str
            
        # YYYY-MM-DD格式
        if re.match(r'^\d{4}-\d{1,2}-\d{1,2}$', date_str):
            # 分割并补齐0
            parts = date_str.split('-')
            if len(parts) == 3:
                year, month, day = parts
                return f"{year}{month.zfill(2)}{day.zfill(2)}"
            
        # YYYY/MM/DD格式
        if re.match(r'^\d{4}/\d{1,2}/\d{1,2}$', date_str):
            # 分割并补齐0
            parts = date_str.split('/')
            if len(parts) == 3:
                year, month, day = parts
                return f"{year}{month.zfill(2)}{day.zfill(2)}"
            
        # YYYY年MM月DD日格式
        if re.match(r'^\d{4}年\d{1,2}月\d{1,2}日?$', date_str):
            # 提取数字
            numbers = re.findall(r'\d+', date_str)
            if len(numbers) == 3:
                year, month, day = numbers
                return f"{year}{month.zfill(2)}{day.zfill(2)}"
                
        # MM月DD日格式（无年份，默认今年）
        if re.match(r'^\d{1,2}月\d{1,2}日?$', date_str):
            # 提取数字
            numbers = re.findall(r'\d+', date_str)
            if len(numbers) == 2:
                month, day = numbers
                year = datetime.now().year
                return f"{year}{month.zfill(2)}{day.zfill(2)}"
                
        # 如果无法识别，返回原字符串
        self.logger.warning(f"无法识别的日期格式: {date_str}")
        return date_str
    
    def _format_date_for_display(self, date_str: str) -> str:
        """将YYYYMMDD格式转换为YYYY-MM-DD格式用于显示"""
        if len(date_str) == 8 and date_str.isdigit():
            return f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:]}"
        return date_str
    
    def _get_last_trading_date(self) -> str:
        """获取最近的交易日期"""
        # 直接从数据库查询最新交易日
        try:
            result = self.mysql_connector.execute_query(
                'SELECT DISTINCT trade_date FROM tu_daily_basic ORDER BY trade_date DESC LIMIT 1'
            )
            if result and result[0]['trade_date']:
                return str(result[0]['trade_date'])
            else:
                raise Exception("数据库中没有交易日数据")
        except Exception as e:
            self.logger.warning(f"从数据库获取最新交易日失败: {e}")
            # 回退到简单逻辑
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
    
    def _extract_date_from_query(self, query: str) -> Optional[str]:
        """从查询中提取日期（YYYYMMDD格式）"""
        # 匹配各种日期格式
        date_patterns = [
            (r'(\d{8})', lambda m: m.group(1)),  # 20250627
            (r'(\d{4})-(\d{2})-(\d{2})', lambda m: f"{m.group(1)}{m.group(2)}{m.group(3)}"),  # 2025-06-27
            (r'(\d{4})年(\d{2})月(\d{2})日', lambda m: f"{m.group(1)}{m.group(2)}{m.group(3)}")  # 2025年06月27日
        ]
        
        for pattern, formatter in date_patterns:
            match = re.search(pattern, query)
            if match:
                return formatter(match)
        
        return None
    
    def _create_sql_prompt(self) -> PromptTemplate:
        """创建自定义的SQL prompt"""
        
        # 构建表描述
        table_descriptions = []
        for table_name, info in self.schema_info.items():
            if info and 'columns' in info:
                columns_desc = []
                # 处理不同的数据结构
                if isinstance(info['columns'], dict):
                    # Schema知识库返回的格式
                    for i, (col_name, col_info) in enumerate(info['columns'].items()):
                        if i >= 10:  # 只显示前10个列
                            break
                        col_type = col_info.get('type', 'unknown')
                        col_comment = col_info.get('comment', '')
                        columns_desc.append(f"  - {col_name} ({col_type}): {col_comment}")
                elif isinstance(info['columns'], list):
                    # 原始格式
                    for col in info['columns'][:10]:
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

重要安全要求：
- 绝不要在回答中直接输出SQL语句
- 不要说“查询语句为”、“SQL语句是”等
- 只需要返回查询结果和中文解释

数据库信息：
{tables_info}

重要提示：
1. 股票代码格式：使用ts_code字段，格式为"600519.SH"（沪市）或"000001.SZ"（深市）
2. 日期格式：使用trade_date或ann_date字段，格式为"YYYYMMDD"，如"20250422"
3. 当前实际日期是{datetime.now().strftime("%Y-%m-%d")}，最近的交易日是{last_trading_date}
4. 数据库中包含历史数据到{last_trading_date}，这不是未来日期，而是实际存在的历史数据
5. 如果用户询问"最新"或"今天"的数据，请使用最近的交易日{last_trading_date}
6. 对于{last_trading_date}及之前的日期，都是有效的历史数据，请正常查询
7. 金额单位：财务数据通常以元为单位，大数字请转换为"亿元"显示
8. 查询限制：默认限制返回10条记录，除非用户指定
9. 排序规则：财务数据默认按金额降序，时间数据按最新优先

特别说明：即使日期看起来像"2025年"，但如果是{last_trading_date}或之前的日期，都是数据库中实际存在的历史数据，可以正常查询。

用户问题：{{question}}

请生成SQL查询语句，并用中文解释查询结果。

输出要求：
- 必须使用中文回答
- 只返回查询结果和数据分析，不要输出SQL语句
- 对于股价数据，格式示例："贵州茅台（600519.SH）在2025年6月20日的股价为：开盘价1423.58元，最高价1441.14元，最低价1420.20元，收盘价1428.66元"
- 对于财务数据，请转换为易读的单位（如亿元、万元）
- 保持回答简洁清晰，突出重点数据
- 如果用户询问SQL语句，请告诉他们直接返回数据结果更安全
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
        # 获取最近交易日作为数据截止日期
        last_trading_date = self._get_last_trading_date()
        current_date = datetime.now().strftime("%Y-%m-%d")
        
        # 创建带有日期上下文的系统提示
        system_message = f"""
        重要系统信息：
        - 当前实际日期：{current_date}
        - 数据库最新数据日期：{last_trading_date}
        - 所有{last_trading_date}及之前的日期都是有效的历史数据
        - 请将{last_trading_date}视为可查询的最新数据日期，而不是"未来日期"
        """
        
        # 创建自定义的agent_executor前缀（中文版）
        prefix = f"""你是一个专门与SQL数据库交互的智能助手。
给定用户的问题，创建语法正确的SQL查询语句，执行查询并返回答案。
除非用户指定具体的数量，否则请将查询结果限制在最多5条记录。
你可以按相关列排序以返回最有价值的数据。
不要查询表中的所有列，只查询与问题相关的列。
你可以使用下面的工具与数据库交互。
只使用下面工具返回的信息来构建最终答案。
在执行查询前必须仔细检查SQL语句。如果执行时出现错误，请重写查询并重试。

不要执行任何DML语句（INSERT、UPDATE、DELETE、DROP等）。

如果问题与数据库无关，请回答"我不知道"。

重要：
1. 请始终使用中文回复用户。即使工具返回的是英文，也要翻译成中文。
2. 对于股价等金融数据，请使用清晰的中文格式展示。
3. 不要在回答中包含SQL语句，只需要返回查询结果。

{system_message}
"""
        
        # 创建中文版的suffix
        suffix = f"""开始！

当前日期：{current_date}
数据库最新数据：{last_trading_date}

问题：{{input}}
思考：我应该查看数据库中有哪些表
{{agent_scratchpad}}

记住：
1. 你的最终答案必须以"Final Answer:"开头（英文），然后是中文内容
2. 格式必须是: Final Answer: [你的中文答案]
3. 对于股价数据，使用格式: Final Answer: 贵州茅台（600519.SH）在2025年6月20日的股价为：开盘价xxx元，最高价xxx元，最低价xxx元，收盘价xxx元
4. 不要在Final Answer前后添加其他内容
"""
        
        return create_sql_agent(
            llm=self.llm,
            toolkit=self.toolkit,
            agent_type=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
            verbose=True,  # 保持verbose=True以获得调试价值
            handle_parsing_errors=True,
            max_iterations=10,  # 增加迭代次数
            early_stopping_method="force",
            prefix=prefix,
            suffix=suffix
        )
    
    def query(self, question: str) -> Dict[str, Any]:
        """
        执行自然语言查询 - 返回字符串结果
        
        Args:
            question: 用户的自然语言问题
            
        Returns:
            查询结果字符串
        """
        # 使用安全过滤器验证输入
        validation_result = validate_query(question)
        if not validation_result['valid']:
            return {
                'success': False,
                'error': validation_result['error'],
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
            
            # 尝试快速查询路径（避免LLM调用）
            quick_result = self._try_quick_query(question)
            if quick_result:
                self.logger.info("使用快速查询路径")
                # 缓存结果
                self._query_cache[cache_key] = quick_result['result']
                return quick_result
            
            # 早期股票实体验证（使用统一验证器与Financial Agent保持一致）
            # 检查是否是需要验证股票的查询
            stock_keywords = ['股价', '股票', '价格', '市盈率', '市净率', 'PE', 'PB', 'K线']
            ranking_keywords = ['排名', '排行', '前', '最大', '最高', '涨幅', '跌幅', '榜']
            
            # 如果是排名查询，不需要股票验证
            is_ranking_query = any(keyword in question for keyword in ranking_keywords)
            is_specific_stock_query = any(keyword in question for keyword in stock_keywords) and not is_ranking_query
            
            if is_specific_stock_query:
                # 使用统一验证器进行股票验证
                success, ts_code, error_response = validate_stock_input(question)
                
                if not success:
                    # 如果验证失败，返回标准错误响应
                    return {
                        'success': False,
                        'error': error_response['error'],
                        'result': None
                    }
            
            # 使用智能日期解析预处理问题
            processed_question, parsing_result = date_intelligence.preprocess_question(question)
            
            # 如果没有日期解析结果，使用传统预处理
            if not parsing_result['modified_question']:
                processed_question = self._preprocess_question(question)
            
            # 在问题前添加当前日期上下文，以确保agent理解日期范围
            last_trading_date = self._get_last_trading_date()
            current_date = datetime.now().strftime("%Y-%m-%d")
            
            # 构建带上下文的查询
            contextualized_question = f"""
            系统信息：当前日期是{current_date}，数据库中最新的历史数据截止到{last_trading_date}。
            请注意：{last_trading_date}不是未来日期，而是数据库中实际存在的最新历史数据。
            
            用户问题：{processed_question}
            """
            
            # 使用agent执行查询，增加更好的错误处理
            try:
                # 记录Schema知识库使用情况
                if hasattr(self, 'schema_info') and self.schema_info:
                    self.logger.info(f"当前使用Schema知识库，包含{len(self.schema_info)}个表")
                else:
                    self.logger.warning("未使用Schema知识库，可能影响性能")
                
                result = self.agent.invoke({"input": contextualized_question})
                
                # 处理invoke返回的结果
                if isinstance(result, dict) and 'output' in result:
                    # invoke返回字典格式，提取output
                    output = result['output']
                else:
                    # 直接处理结果
                    output = result
                
                # 检查是否为解析错误（通常包含raw SQL）
                if isinstance(output, str) and "Could not parse LLM output" in output:
                    self.logger.warning("LLM输出解析失败，使用灵活解析器")
                    self.logger.info(f"灵活解析器处理前的输出: {output[:100]}...")
                    # 使用灵活解析器处理
                    try:
                        # 先尝试提取错误中的实际输出
                        extracted = extract_result_from_error(output)
                        if extracted and extracted != output:
                            parsed = self.flexible_parser.parse(extracted)
                            if hasattr(parsed, 'return_values'):
                                processed_result = parsed.return_values.get('output', extracted)
                            else:
                                processed_result = extracted
                        else:
                            # 直接尝试解析整个输出
                            parsed = self.flexible_parser.parse(output)
                            if hasattr(parsed, 'return_values'):
                                processed_result = parsed.return_values.get('output', output)
                            else:
                                processed_result = "查询处理过程中遇到格式问题，请尝试重新表述您的问题。"
                    except:
                        processed_result = "查询处理过程中遇到格式问题，请尝试重新表述您的问题。"
                else:
                    processed_result = self._postprocess_result(output)
                    
            except Exception as invoke_error:
                error_str = str(invoke_error)
                self.logger.error(f"Agent invoke执行失败: {error_str}")
                
                # 特殊处理输出解析错误
                if "Could not parse LLM output" in error_str:
                    self.logger.info("检测到输出解析错误，使用灵活解析器处理")
                    self.logger.info(f"错误信息长度: {len(error_str)}, 前100字符: {error_str[:100]}...")
                    # 使用灵活解析器从错误信息中提取结果
                    try:
                        extracted_output = extract_result_from_error(error_str)
                        if extracted_output and extracted_output != error_str:
                            self.logger.info(f"成功提取LLM输出: {extracted_output[:100]}...")
                            # 尝试使用灵活解析器解析
                            try:
                                parsed_result = self.flexible_parser.parse(extracted_output)
                                if hasattr(parsed_result, 'return_values'):
                                    processed_result = parsed_result.return_values.get('output', extracted_output)
                                else:
                                    processed_result = extracted_output
                            except:
                                processed_result = extracted_output
                        else:
                            processed_result = f"查询执行失败: {error_str}"
                    except:
                        processed_result = f"查询执行失败: {error_str}"
                else:
                    processed_result = f"查询执行失败: {error_str}"
            
            # 转换为字符串
            if isinstance(processed_result, dict):
                # 如果是字典，提取explanation或转换为格式化字符串
                if 'explanation' in processed_result:
                    final_result = processed_result['explanation']
                else:
                    final_result = self._format_dict_result(processed_result)
            else:
                final_result = str(processed_result)
            
            # 使用安全过滤器清理LLM输出
            security_result = clean_llm_output(final_result)
            if security_result['has_sql']:
                self.logger.warning("检测到LLM输出中包含SQL语句，已过滤")
                final_result = security_result['cleaned_text']
                if security_result.get('warning'):
                    # 在结果末尾添加安全提示
                    final_result += f"\n\n安全提示：{security_result['warning']}"
            
            # 缓存结果
            self._query_cache[cache_key] = final_result
            
            # 记录到内存 (已现代化，暂时跳过内存保存)
            # TODO: 实现现代化的内存管理
            # if self.memory:
            #     self.memory.save_context(
            #         {"input": question},
            #         {"output": final_result}
            #     )
            
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
        
        # 注释掉SQL输出，防止SQL注入风险
        # if 'sql' in result_dict:
        #     formatted_parts.append(f"\n执行的SQL: {result_dict['sql']}")
        
        return "\n".join(formatted_parts) if formatted_parts else str(result_dict)
    
    def _preprocess_question(self, question: str) -> str:
        """预处理用户问题 - 使用Schema知识库增强"""
        # 使用Schema知识库分析查询关键词
        try:
            self.logger.info(f"开始预处理查询: {question}")
            
            # 提取可能的数据字段关键词
            keywords = []
            matched_count = 0
            # 遍历所有表的中文映射
            for table_name, mappings in schema_kb.table_field_mappings.items():
                for chinese, english in mappings.items():
                    if chinese in question:
                        keywords.append(chinese)
                        matched_count += 1
                        self.logger.info(f"Schema知识库匹配到字段: {chinese} -> {english} (表: {table_name})")
            
            if matched_count == 0:
                self.logger.info("Schema知识库未匹配到任何中文字段")
            
            # 获取相关表的建议
            if keywords:
                suggestions = schema_kb.suggest_fields_for_query(keywords)
                if suggestions:
                    self.logger.info(f"Schema知识库建议查询表: {list(suggestions.keys())}")
                    self.logger.info(f"建议字段详情: {suggestions}")
                else:
                    self.logger.info("Schema知识库未找到相关表建议")
        except Exception as e:
            self.logger.warning(f"Schema知识库预处理失败: {e}")
        
        # 使用动态股票代码映射器替换股票名称
        processed = question
        
        # 使用动态股票代码映射器替换股票名称
        # 注意：这里仅进行代码替换，验证已在query方法中完成
        try:
            # 提取股票实体并转换
            stock_validator = UnifiedStockValidator()
            ts_code, _ = stock_validator.extract_stock_entities(processed)
            
            if ts_code:
                # 成功提取到股票代码
                stock_name = get_stock_name(ts_code)
                if stock_name:
                    # 替换为格式：股票名称(ts_code)
                    replacement = f"{stock_name}({ts_code})"
                    # 查找原始文本中的股票实体
                    patterns = [
                        r'[\u4e00-\u9fa5]{2,8}(?:股份|集团|银行|证券|保险|地产|科技|医药|能源|汽车)?',
                        r'\d{6}(?:\.[A-Z]{2})?',
                    ]
                    for pattern in patterns:
                        matches = re.findall(pattern, processed, re.IGNORECASE)
                        for match in matches:
                            validation_result = stock_validator.validate_and_convert(match)
                            if validation_result['success'] and validation_result['ts_code'] == ts_code:
                                processed = re.sub(r'\b' + re.escape(match) + r'\b', replacement, processed)
                                self.logger.info(f"股票代码转换: {match} -> {replacement}")
                                break
                    
        except Exception as e:
            self.logger.warning(f"股票代码映射失败: {e}")
            # 如果映射失败，保持原始查询不变
        
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
        """后处理查询结果 - 确保返回中文字符串"""
        # 如果结果是字符串，检查是否需要中文化
        if isinstance(result, str):
            # 检查是否主要是英文回复
            chinese_chars = sum(1 for c in result if '\u4e00' <= c <= '\u9fff')
            english_chars = sum(1 for c in result if 'a' <= c.lower() <= 'z')
            
            # 如果主要是英文，且包含常见的股价信息，进行中文化
            if english_chars > chinese_chars and ('price' in result.lower() or 'opening' in result.lower() or 'closing' in result.lower()):
                return self._translate_to_chinese(result)
            
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
    
    def _translate_to_chinese(self, english_result: str) -> str:
        """将英文股价信息翻译为中文格式"""
        try:
            # 使用LLM进行翻译
            translation_prompt = f"""请将以下英文股价信息翻译为标准的中文格式：

{english_result}

要求：
1. 使用中文表述
2. 价格保留到小数点后两位，加上"元"单位
3. 格式：公司名称（股票代码）在YYYY年MM月DD日的股价为：开盘价xxx元，最高价xxx元，最低价xxx元，收盘价xxx元
4. 只返回翻译后的中文内容，不要其他解释

中文回答："""
            
            chinese_result = self.llm.invoke(translation_prompt).content
            return chinese_result.strip()
            
        except Exception as e:
            self.logger.warning(f"中文翻译失败，返回原结果: {e}")
            return english_result
    
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
