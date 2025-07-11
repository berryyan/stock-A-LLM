# 文件路径: E:\PycharmProjects\stock_analysis_system\agents\financial_agent_modular.py

"""
Financial Agent 模块化版本
逐步将现有功能迁移到模块化架构
"""
import sys
import os
from typing import List, Dict, Any, Optional, Tuple
import time
import numpy as np
from datetime import datetime, timedelta
from dataclasses import dataclass

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 导入原始Financial Agent的基础类
from agents.financial_agent import FinancialAnalysisAgent as FinancialAgentBase, FinancialData

# 导入新的模块化组件
from utils.parameter_extractor import ParameterExtractor, ExtractedParams
from utils.query_validator import QueryValidator
from utils.result_formatter import ResultFormatter, FormattedResult, ResultType, TableData
from utils.error_handler import ErrorHandler, ErrorCategory
from utils.logger import setup_logger
from utils.stock_validation_helper import validate_and_convert_stock


class FinancialAgentModular(FinancialAgentBase):
    """Financial Agent 模块化版本 - 继承并逐步重构"""
    
    def __init__(self, llm_model_name: str = "deepseek-chat"):
        # 初始化父类
        super().__init__(llm_model_name)
        
        # 初始化模块化组件
        self.param_extractor = ParameterExtractor()
        self.query_validator = QueryValidator()
        self.result_formatter = ResultFormatter()
        self.error_handler = ErrorHandler()
        
        self.logger = setup_logger("financial_agent_modular")
        self.logger.info("Financial Agent模块化版本初始化完成")
    
    def analyze(self, query: str) -> Dict[str, Any]:
        """
        执行财务分析 - 使用模块化组件增强
        
        Args:
            query: 用户查询
            
        Returns:
            分析结果
        """
        start_time = time.time()
        
        try:
            # 1. 输入验证
            if not query or not query.strip():
                return self._handle_error(
                    ValueError("查询内容不能为空"),
                    "EMPTY_INPUT"
                )
            
            query = query.strip()
            self.logger.info(f"收到财务分析查询: {query}")
            
            # 2. 使用参数提取器
            extracted_params = self.param_extractor.extract_all_params(query)
            
            # 3. 识别分析类型
            analysis_type = self._identify_analysis_type(query)
            if not analysis_type:
                return self._handle_error(
                    ValueError("无法识别财务分析类型"),
                    "INVALID_QUERY"
                )
            
            self.logger.info(f"识别到分析类型: {analysis_type}")
            
            # 4. 验证股票参数
            if not extracted_params.stocks:
                # 尝试从查询中提取股票
                stocks, error = self._extract_stock_from_query(query)
                if error:
                    return self._handle_error(
                        ValueError(error),
                        "INVALID_STOCK"
                    )
                extracted_params.stocks = stocks
            
            # 5. 执行相应的分析
            result = self._execute_analysis(analysis_type, extracted_params, query)
            
            elapsed_time = time.time() - start_time
            
            if result.get('success'):
                result['query_time'] = elapsed_time
                
                # 尝试使用新的格式化器优化结果展示
                if 'raw_data' in result and result['raw_data']:
                    try:
                        formatted_result = self._format_with_new_formatter(
                            result['raw_data'], 
                            analysis_type
                        )
                        if formatted_result:
                            result['result'] = formatted_result.formatted_text
                    except Exception as e:
                        self.logger.warning(f"新格式化器处理失败: {str(e)}")
            
            return result
            
        except Exception as e:
            self.logger.error(f"财务分析执行异常: {str(e)}")
            return self._handle_error(e, "INTERNAL_ERROR")
    
    def _extract_stock_from_query(self, query: str) -> Tuple[List[str], Optional[str]]:
        """从查询中提取股票代码"""
        try:
            # 使用参数提取器的股票提取功能
            params = self.param_extractor.extract_all_params(query)
            
            if params.stocks:
                return params.stocks, None
            elif params.error:
                return [], params.error
            else:
                return [], "未识别到股票信息"
                
        except Exception as e:
            self.logger.error(f"股票提取失败: {str(e)}")
            return [], f"股票提取失败: {str(e)}"
    
    def _identify_analysis_type(self, query: str) -> str:
        """识别财务分析类型"""
        # 使用父类的query_patterns
        for pattern_type, patterns in self.query_patterns.items():
            if any(pattern in query for pattern in patterns):
                return pattern_type
        
        # 默认返回综合分析
        return 'financial_health'
    
    def _execute_analysis(self, analysis_type: str, params: ExtractedParams, query: str) -> Dict[str, Any]:
        """执行具体的分析 - 调用父类方法并增强"""
        try:
            # 获取第一个股票代码
            ts_code = params.stocks[0] if params.stocks else None
            if not ts_code:
                return {
                    'success': False,
                    'error': "未找到有效的股票代码"
                }
            
            # 调用父类的相应分析方法
            if analysis_type in ['financial_health', 'profitability', 'solvency', 'growth']:
                # 这些都使用财务健康度分析
                return self.analyze_financial_health(ts_code)
            elif analysis_type == 'cash_flow':
                return self.cash_flow_quality_analysis(ts_code)
            elif analysis_type == 'dupont':
                return self.dupont_analysis(ts_code)
            elif analysis_type == 'comparison':
                # 暂时返回财务健康度分析，因为父类没有comparison方法
                return self.analyze_financial_health(ts_code)
            else:
                return {
                    'success': False,
                    'error': f"不支持的分析类型: {analysis_type}"
                }
                
        except Exception as e:
            self.logger.error(f"分析执行失败: {str(e)}")
            return {
                'success': False,
                'error': f"分析执行失败: {str(e)}"
            }
    
    def _extract_periods_from_params(self, params: ExtractedParams) -> Optional[int]:
        """从参数中提取报告期数量"""
        # 如果有明确的数量限制，使用它作为期数
        if params.limit and params.limit != 10:  # 10是默认值
            return params.limit
        
        # 如果有日期范围，尝试计算期数
        if params.date_range:
            # 简单估算：每3个月一期
            start_date = datetime.strptime(params.date_range[0], '%Y%m%d')
            end_date = datetime.strptime(params.date_range[1], '%Y%m%d')
            months = (end_date.year - start_date.year) * 12 + end_date.month - start_date.month
            return max(1, months // 3)
        
        # 默认返回None，让父类使用默认值
        return None
    
    def _format_with_new_formatter(self, raw_data: Any, analysis_type: str) -> Optional[FormattedResult]:
        """使用新的格式化器格式化结果"""
        try:
            if analysis_type == 'financial_health':
                # 财务健康度分析结果格式化
                if isinstance(raw_data, dict) and 'score' in raw_data:
                    formatted_data = {
                        "财务健康度评分": f"{raw_data['score']}分",
                        "评级": raw_data.get('rating', 'N/A'),
                        "盈利能力": f"{raw_data.get('profitability_score', 0)}/25分",
                        "偿债能力": f"{raw_data.get('solvency_score', 0)}/25分",
                        "运营能力": f"{raw_data.get('operation_score', 0)}/25分",
                        "成长能力": f"{raw_data.get('growth_score', 0)}/25分"
                    }
                    
                    # 使用格式化器
                    result = self.result_formatter.format_financial_health(raw_data)
                    return result
            
            elif analysis_type == 'comparison' and isinstance(raw_data, list):
                # 多期对比结果格式化
                if raw_data and all('end_date' in item for item in raw_data):
                    # 构建表格数据
                    headers = ["报告期", "营收(亿)", "净利润(亿)", "ROE(%)", "负债率(%)"]
                    rows = []
                    
                    for item in raw_data:
                        rows.append([
                            self._format_period(item['end_date']),
                            f"{item.get('total_revenue', 0) / 100000000:.2f}",
                            f"{item.get('n_income_attr_p', 0) / 100000000:.2f}",
                            f"{item.get('roe', 0):.2f}",
                            f"{item.get('debt_to_assets', 0):.2f}"
                        ])
                    
                    table_data = TableData(
                        headers=headers,
                        rows=rows,
                        column_types={
                            "营收(亿)": "number",
                            "净利润(亿)": "number",
                            "ROE(%)": "number",
                            "负债率(%)": "number"
                        }
                    )
                    
                    return FormattedResult(
                        result_type=ResultType.TABLE,
                        formatted_text=table_data.to_markdown(),
                        raw_data=raw_data
                    )
            
            return None
            
        except Exception as e:
            self.logger.error(f"格式化失败: {str(e)}")
            return None
    
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
    
    def _handle_error(self, error: Exception, error_code: str) -> Dict[str, Any]:
        """处理错误"""
        # 直接使用原始错误消息
        error_message = str(error)
        
        return {
            'success': False,
            'error': error_message,
            'suggestion': None,
            'details': None
        }
    
