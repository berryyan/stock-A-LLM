# 文件路径: E:\PycharmProjects\stock_analysis_system\agents\sql_agent_modular.py

"""
SQL Agent 模块化版本
逐步将现有功能迁移到模块化架构
"""
import re
import sys
import os
import time
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
import json

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 导入原始SQL Agent的基础类
from agents.sql_agent import SQLAgent as SQLAgentBase

# 导入新的模块化组件
from utils.parameter_extractor import ParameterExtractor, ExtractedParams
from utils.query_validator import QueryValidator
from utils.result_formatter import ResultFormatter
from utils.error_handler import ErrorHandler
from utils.logger import setup_logger


class SQLAgentModular(SQLAgentBase):
    """SQL Agent 模块化版本 - 继承并逐步重构"""
    
    def __init__(self, llm_model_name: str = "deepseek-chat"):
        # 初始化父类
        super().__init__(llm_model_name)
        
        # 初始化模块化组件
        self.param_extractor = ParameterExtractor()
        self.query_validator = QueryValidator()
        self.result_formatter = ResultFormatter()
        self.error_handler = ErrorHandler()
        
        self.logger = setup_logger("sql_agent_modular")
        self.logger.info("SQL Agent模块化版本初始化完成")
    
    def _extract_query_params(self, query: str, template: Any, params: Dict,
                             processed_question: str, last_trading_date: str) -> Tuple[bool, Optional[str], Dict, Optional[str]]:
        """
        重写参数提取方法，使用新的参数提取器
        """
        try:
            # 使用新的参数提取器
            extracted_params = self.param_extractor.extract_all_params(processed_question, template)
            
            # 如果有错误，返回错误信息
            if extracted_params.error:
                return False, None, {}, extracted_params.error
            
            # 构建返回的参数字典
            query_params = {}
            error_message = None
            
            # 处理股票参数
            if template.requires_stock and extracted_params.stocks:
                ts_code = extracted_params.stocks[0]
                stock_name = extracted_params.stock_names[0] if extracted_params.stock_names else None
                query_params['ts_code'] = ts_code
                query_params['stock_name'] = stock_name
            elif template.requires_stock:
                # 尝试从原始params中获取
                entities = params.get('entities', [])
                if entities:
                    # 使用原有的股票验证逻辑
                    from utils.stock_validation_helper import extract_and_validate_stock_from_entities
                    success, ts_code, stock_name, error_msg = extract_and_validate_stock_from_entities(entities)
                    if success:
                        query_params['ts_code'] = ts_code
                        query_params['stock_name'] = stock_name
                    else:
                        return False, None, {}, error_msg
                else:
                    return False, None, {}, "未识别到股票信息"
            
            # 处理日期参数
            if template.requires_date:
                if extracted_params.date:
                    query_params['trade_date'] = extracted_params.date
                elif extracted_params.date_range:
                    query_params['start_date'] = extracted_params.date_range[0]
                    query_params['end_date'] = extracted_params.date_range[1]
                else:
                    # 使用最新交易日
                    query_params['trade_date'] = last_trading_date
            
            # 处理限制参数
            query_params['limit'] = extracted_params.limit
            
            # 处理板块参数
            if extracted_params.sector:
                query_params['sector'] = extracted_params.sector
                query_params['sector_code'] = extracted_params.sector_code
            
            # 处理报告期参数
            if extracted_params.period:
                query_params['period'] = extracted_params.period
            
            return True, ts_code if 'ts_code' in query_params else None, query_params, error_message
            
        except Exception as e:
            self.logger.error(f"参数提取失败: {str(e)}")
            return False, None, {}, f"参数提取失败: {str(e)}"
    
    def _format_result_with_formatter(self, result: Any, template_name: str, **kwargs) -> str:
        """
        使用新的结果格式化器格式化结果
        """
        try:
            if isinstance(result, list) and result:
                # 根据模板类型选择合适的格式化方法
                if "排名" in template_name or "排行" in template_name:
                    # 构建表格数据
                    headers, rows = self._build_table_data(result, template_name)
                    return self.result_formatter.format_table(headers, rows, title=kwargs.get('title', template_name))
                else:
                    # 使用记录格式化
                    return self.result_formatter.format_records(result)
            elif isinstance(result, dict):
                return self.result_formatter.format_dict_data(result)
            else:
                return str(result)
                
        except Exception as e:
            self.logger.error(f"结果格式化失败: {str(e)}")
            # 降级到原始格式
            return str(result)
    
    def _build_table_data(self, result: List[Dict], template_name: str) -> Tuple[List[str], List[List]]:
        """
        根据模板类型构建表格数据
        """
        if "市值排名" in template_name:
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
            return headers, rows
            
        elif "涨幅排名" in template_name or "涨跌幅" in template_name:
            headers = ["排名", "股票代码", "股票名称", "涨跌幅(%)", "最新价", "成交额(亿元)"]
            rows = []
            for i, row in enumerate(result, 1):
                rows.append([
                    i,
                    row['ts_code'],
                    row['name'],
                    f"{row['pct_chg']:.2f}",
                    f"{row['close']:.2f}",
                    f"{row['amount'] / 100000:.2f}"
                ])
            return headers, rows
            
        elif "成交额排名" in template_name:
            headers = ["排名", "股票代码", "股票名称", "成交额(亿元)", "成交量(万手)", "涨跌幅(%)"]
            rows = []
            for i, row in enumerate(result, 1):
                rows.append([
                    i,
                    row['ts_code'],
                    row['name'],
                    f"{row['amount'] / 100000:.2f}",
                    f"{row['vol'] / 10000:.2f}",
                    f"{row['pct_chg']:.2f}"
                ])
            return headers, rows
            
        elif "主力" in template_name and ("流入" in template_name or "流出" in template_name):
            headers = ["排名", "股票代码", "股票名称", "主力净流入(万元)", "主力流入占比(%)", "涨跌幅(%)"]
            rows = []
            for i, row in enumerate(result, 1):
                rows.append([
                    i,
                    row['ts_code'],
                    row['name'],
                    f"{row['net_mf_amount']:.2f}",
                    f"{row['net_mf_amount'] / row['amount'] * 10000:.2f}" if row['amount'] else "0.00",
                    f"{row['pct_chg']:.2f}"
                ])
            return headers, rows
            
        else:
            # 默认格式
            if result:
                headers = list(result[0].keys())
                rows = [[str(row[h]) for h in headers] for row in result]
                return headers, rows
            else:
                return [], []
    
    def _handle_error_with_handler(self, error: Exception, error_code: str = None) -> Dict[str, Any]:
        """
        使用新的错误处理器处理错误
        """
        error_info = self.error_handler.handle_error(error, error_code)
        
        return {
            'success': False,
            'error': error_info.user_message,
            'suggestion': error_info.suggestion,
            'details': error_info.details if self.error_handler.debug_mode else None
        }
    
    def query(self, question: str) -> Dict[str, Any]:
        """
        重写查询方法，逐步集成模块化组件
        """
        try:
            # 输入验证
            if not question or not question.strip():
                return self._handle_error_with_handler(
                    ValueError("查询内容不能为空"),
                    "EMPTY_INPUT"
                )
            
            # 调用父类的查询方法
            result = super().query(question)
            
            # 如果是快速路径成功的结果，尝试使用新的格式化器重新格式化
            if result.get('success') and result.get('quick_path'):
                original_result = result.get('result', '')
                try:
                    # 这里可以根据需要重新格式化结果
                    # 暂时保持原样
                    pass
                except Exception as e:
                    self.logger.warning(f"重新格式化失败: {str(e)}")
            
            return result
            
        except Exception as e:
            self.logger.error(f"查询执行异常: {str(e)}")
            return self._handle_error_with_handler(e, "INTERNAL_ERROR")