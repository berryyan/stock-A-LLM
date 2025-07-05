# 文件路径: E:\PycharmProjects\stock_analysis_system\agents\money_flow_agent_modular.py

"""
Money Flow Agent 模块化版本
逐步将现有功能迁移到模块化架构
"""
import re
import json
from typing import Dict, Any, Optional, List
from datetime import datetime
import logging

# 添加项目根目录到Python路径
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 导入原始Money Flow Agent的基础类
from agents.money_flow_agent import MoneyFlowAgent as MoneyFlowAgentBase

# 导入新的模块化组件
from utils.parameter_extractor import ParameterExtractor, ExtractedParams
from utils.query_validator import QueryValidator
from utils.result_formatter import ResultFormatter, FormattedResult, ResultType
from utils.error_handler import ErrorHandler
from utils.logger import setup_logger
from database.mysql_connector import MySQLConnector


class MoneyFlowAgentModular(MoneyFlowAgentBase):
    """Money Flow Agent 模块化版本 - 继承并逐步重构"""
    
    def __init__(self, mysql_connector: MySQLConnector = None):
        # 初始化父类
        super().__init__(mysql_connector)
        
        # 初始化模块化组件
        self.param_extractor = ParameterExtractor()
        self.query_validator = QueryValidator()
        self.result_formatter = ResultFormatter()
        self.error_handler = ErrorHandler()
        
        self.logger = setup_logger("money_flow_agent_modular")
        self.logger.info("Money Flow Agent模块化版本初始化完成")
    
    def analyze(self, query: str) -> Dict[str, Any]:
        """
        分析查询并执行资金流向分析 - 使用模块化组件增强
        
        Args:
            query: 用户查询字符串
            
        Returns:
            包含分析结果的字典
        """
        start_time = datetime.now()
        
        try:
            # 1. 输入验证
            if not query or not query.strip():
                return self._handle_error(
                    ValueError("查询内容不能为空"),
                    "EMPTY_INPUT"
                )
            
            query = query.strip()
            self.logger.info(f"收到资金流向查询: {query}")
            
            # 2. 使用参数提取器
            extracted_params = self.param_extractor.extract_all_params(query)
            
            # 3. 识别查询类型
            query_type = self._identify_query_type(query)
            self.logger.info(f"识别到查询类型: {query_type}")
            
            # 4. 标准化资金类型术语
            standardized_query, fund_type_msg = self._standardize_fund_type(query)
            if fund_type_msg:
                self.logger.info(f"资金类型标准化: {fund_type_msg}")
            
            # 5. 根据查询类型执行相应分析
            if query_type == "SQL_ONLY":
                # 快速数据查询
                result = self._execute_sql_query(extracted_params, standardized_query)
            else:
                # 深度分析
                result = self._execute_deep_analysis(extracted_params, standardized_query)
            
            # 6. 添加术语转换提示
            if fund_type_msg and result.get('success'):
                if isinstance(result.get('result'), str):
                    result['result'] = f"{fund_type_msg}\n\n{result['result']}"
            
            # 记录执行时间
            result['query_time'] = (datetime.now() - start_time).total_seconds()
            
            return result
            
        except Exception as e:
            self.logger.error(f"资金流向分析异常: {str(e)}", exc_info=True)
            return self._handle_error(e, "INTERNAL_ERROR")
    
    def _execute_sql_query(self, params: ExtractedParams, query: str) -> Dict[str, Any]:
        """执行SQL查询 - 使用模块化参数"""
        try:
            # 验证参数
            if not params.stocks and not params.sector:
                return {
                    'success': False,
                    'error': "请指定股票或板块名称"
                }
            
            # 获取交易日期
            trade_date = self._get_trade_date(params)
            
            if params.stocks:
                # 个股资金流向查询
                ts_code = params.stocks[0]
                stock_name = params.stock_names[0] if params.stock_names else ""
                
                # 调用父类方法获取数据
                result = self._get_stock_money_flow(ts_code, trade_date)
                
                if result:
                    # 使用新的格式化器
                    formatted_result = self._format_stock_money_flow(result, stock_name)
                    return {
                        'success': True,
                        'result': formatted_result,
                        'data_type': 'money_flow',
                        'raw_data': result
                    }
                else:
                    return {
                        'success': False,
                        'error': f"未找到{stock_name or ts_code}在{trade_date}的资金流向数据"
                    }
            
            elif params.sector:
                # 板块资金流向查询
                # 调用父类的板块查询方法
                return self._handle_sector_money_flow(params.sector, trade_date)
            
        except Exception as e:
            self.logger.error(f"SQL查询执行失败: {str(e)}")
            return {
                'success': False,
                'error': f"查询执行失败: {str(e)}"
            }
    
    def _execute_deep_analysis(self, params: ExtractedParams, query: str) -> Dict[str, Any]:
        """执行深度资金流向分析"""
        try:
            # 验证股票参数
            if not params.stocks:
                return {
                    'success': False,
                    'error': "深度分析需要指定具体股票"
                }
            
            ts_code = params.stocks[0]
            stock_name = params.stock_names[0] if params.stock_names else ""
            
            # 调用父类的深度分析方法
            analysis_result = self.analyze_money_flow(ts_code)
            
            if analysis_result['success']:
                # 增强格式化
                if 'formatted_report' in analysis_result:
                    # 在报告开头添加股票信息
                    stock_info = f"### {stock_name}（{ts_code}）资金流向深度分析\n\n"
                    analysis_result['result'] = stock_info + analysis_result['formatted_report']
                
                return analysis_result
            else:
                return analysis_result
                
        except Exception as e:
            self.logger.error(f"深度分析执行失败: {str(e)}")
            return {
                'success': False,
                'error': f"深度分析失败: {str(e)}"
            }
    
    def _get_trade_date(self, params: ExtractedParams) -> str:
        """获取交易日期"""
        if params.date:
            return params.date
        
        # 获取最新交易日
        from utils.date_intelligence import date_intelligence
        latest_date = date_intelligence.get_latest_trading_day()
        if latest_date:
            return latest_date.replace('-', '')
        
        # 默认返回今天
        return datetime.now().strftime('%Y%m%d')
    
    def _format_stock_money_flow(self, data: Dict, stock_name: str) -> str:
        """格式化个股资金流向数据"""
        try:
            # 构建格式化数据
            formatted_data = {
                "股票": f"{stock_name}（{data.get('ts_code', '')}）" if stock_name else data.get('ts_code', ''),
                "日期": data.get('trade_date', ''),
                "主力净流入": f"{data.get('net_mf_amount', 0):.2f}万元",
                "超大单净流入": f"{data.get('net_elg_amount', 0):.2f}万元",
                "大单净流入": f"{data.get('net_lg_amount', 0):.2f}万元",
                "中单净流入": f"{data.get('net_md_amount', 0):.2f}万元",
                "小单净流入": f"{data.get('net_sm_amount', 0):.2f}万元"
            }
            
            # 使用结果格式化器
            result = FormattedResult(
                result_type=ResultType.TEXT,
                formatted_text=self._dict_to_text(formatted_data),
                raw_data=data
            )
            
            return result.formatted_text
            
        except Exception as e:
            self.logger.error(f"格式化失败: {str(e)}")
            # 降级到简单格式
            return str(data)
    
    def _dict_to_text(self, data: Dict) -> str:
        """将字典转换为文本格式"""
        lines = []
        for key, value in data.items():
            lines.append(f"{key}: {value}")
        return "\n".join(lines)
    
    def _handle_error(self, error: Exception, error_code: str) -> Dict[str, Any]:
        """处理错误"""
        error_info = self.error_handler.handle_error(error, error_code)
        
        return {
            'success': False,
            'error': error_info.user_message,
            'suggestion': error_info.suggestion,
            'details': error_info.details if self.error_handler.debug_mode else None
        }
    
    def _standardize_fund_type(self, query: str) -> tuple:
        """标准化资金类型术语 - 使用父类方法"""
        return super()._standardize_fund_type(query)
    
    def _identify_query_type(self, query: str) -> str:
        """识别查询类型 - 使用父类方法"""
        return super()._identify_query_type(query)