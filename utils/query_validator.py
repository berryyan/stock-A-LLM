#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
查询验证器模块
统一处理所有查询的参数验证逻辑
"""

import sys
import os
import re
from typing import Tuple, Dict, Any, List, Optional
from dataclasses import dataclass, field
from datetime import datetime, timedelta

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.parameter_extractor import ExtractedParams
from utils.query_templates import QueryTemplate
from utils.logger import setup_logger

logger = setup_logger("query_validator")


@dataclass
class ValidationResult:
    """验证结果"""
    is_valid: bool
    error_code: Optional[str] = None
    error_detail: Dict[str, Any] = field(default_factory=dict)
    warnings: List[str] = field(default_factory=list)
    
    def add_warning(self, warning: str):
        """添加警告信息"""
        self.warnings.append(warning)


class QueryValidator:
    """统一的查询验证器"""
    
    def __init__(self):
        """初始化验证器"""
        self.logger = logger
        
        # 定义验证规则
        self.MAX_LIMIT = 999  # 用户要求：排名数量限制为999
        self.MIN_LIMIT = 1
        self.MAX_DATE_RANGE_DAYS = 3650  # 10年
        self.MAX_STOCKS_PER_QUERY = 10
        
    def validate_params(self, params: ExtractedParams, template: Optional[QueryTemplate] = None) -> ValidationResult:
        """
        验证提取的参数
        
        Args:
            params: 提取的参数对象
            template: 查询模板（可选）
            
        Returns:
            ValidationResult: 验证结果
        """
        result = ValidationResult(is_valid=True)
        
        try:
            # 如果参数提取时已有错误，直接返回
            if params.error:
                result.is_valid = False
                result.error_code = "PARAM_EXTRACTION_ERROR"
                result.error_detail = {"message": params.error}
                return result
            
            # 根据模板验证必需参数
            if template:
                result = self._validate_required_fields(params, template, result)
                if not result.is_valid:
                    return result
            
            # 验证股票
            if params.stocks:
                result = self._validate_stocks(params.stocks, result)
                if not result.is_valid:
                    return result
            
            # 验证日期
            if params.date:
                result = self._validate_date(params.date, result)
                if not result.is_valid:
                    return result
            
            # 验证日期范围
            if params.date_range:
                result = self._validate_date_range(params.date_range, result)
                if not result.is_valid:
                    return result
            
            # 验证数量限制
            result = self._validate_limit(params.limit, result)
            if not result.is_valid:
                return result
            
            # 验证报告期
            if params.period:
                result = self._validate_period(params.period, result)
                if not result.is_valid:
                    return result
            
            # 验证指标列表
            if params.metrics:
                result = self._validate_metrics(params.metrics, template, result)
                if not result.is_valid:
                    return result
            
            # 验证板块/行业
            if params.sector or params.industry:
                result = self._validate_sector_or_industry(params, result)
                
        except Exception as e:
            self.logger.error(f"参数验证失败: {e}")
            result.is_valid = False
            result.error_code = "VALIDATION_ERROR"
            result.error_detail = {"message": str(e)}
            
        return result
    
    def _validate_required_fields(self, params: ExtractedParams, template: QueryTemplate, result: ValidationResult) -> ValidationResult:
        """验证必需参数"""
        # 检查模板要求的必需字段
        if template.requires_stock and not params.stocks:
            result.is_valid = False
            result.error_code = "MISSING_REQUIRED_STOCK"
            result.error_detail = {"message": "此查询需要指定股票"}
            return result
        
        if template.requires_date and not params.date and not params.date_range:
            # 某些模板允许使用默认最新交易日
            allow_default_date_templates = [
                '股价查询', '估值指标查询', '个股主力资金', 
                '板块主力资金', '涨跌幅排名', '成交额排名',
                '成交量排名', '成交量查询', '市值排名', '流通市值排名',
                '主力净流入排行', '主力净流出排行'
            ]
            
            if template.name not in allow_default_date_templates:
                result.is_valid = False
                result.error_code = "MISSING_REQUIRED_DATE"
                result.error_detail = {"message": "此查询需要指定日期"}
                return result
            # 允许使用默认日期的模板，跳过此验证
        
        if template.requires_date_range and not params.date_range:
            # K线查询特殊处理：允许无日期范围（会使用默认90天）
            if template.name in ['K线查询', '历史K线查询', '走势查询']:
                # K线查询允许无日期范围，执行方法会设置默认值
                self.logger.info(f"{template.name}未指定日期范围，将使用默认90天")
            else:
                result.is_valid = False
                result.error_code = "MISSING_REQUIRED_DATE_RANGE"
                result.error_detail = {"message": "此查询需要指定日期范围"}
                return result
        
        return result
    
    def _validate_stocks(self, stocks: List[str], result: ValidationResult) -> ValidationResult:
        """验证股票列表"""
        # 检查股票数量
        if len(stocks) > self.MAX_STOCKS_PER_QUERY:
            result.is_valid = False
            result.error_code = "TOO_MANY_STOCKS"
            result.error_detail = {
                "count": len(stocks),
                "max": self.MAX_STOCKS_PER_QUERY,
                "message": f"一次查询最多支持{self.MAX_STOCKS_PER_QUERY}只股票"
            }
            return result
        
        # 验证股票代码格式（应该已经在提取阶段验证过）
        invalid_stocks = []
        for stock in stocks:
            if not re.match(r'^\d{6}\.[A-Z]{2}$', stock):
                invalid_stocks.append(stock)
        
        if invalid_stocks:
            result.is_valid = False
            result.error_code = "INVALID_STOCK_FORMAT"
            result.error_detail = {
                "invalid_stocks": invalid_stocks,
                "message": f"股票代码格式错误: {', '.join(invalid_stocks)}"
            }
            return result
        
        return result
    
    def _validate_date(self, date: str, result: ValidationResult) -> ValidationResult:
        """验证单个日期"""
        try:
            # 验证日期格式（支持多种格式）
            if len(date) == 8 and date.isdigit():
                # YYYYMMDD格式
                date_obj = datetime.strptime(date, '%Y%m%d')
            elif '-' in date:
                # YYYY-MM-DD格式
                date_obj = datetime.strptime(date, '%Y-%m-%d')
            else:
                raise ValueError(f"不支持的日期格式: {date}")
            
            # 检查日期是否在合理范围内
            if date_obj > datetime.now():
                result.is_valid = False
                result.error_code = "FUTURE_DATE"
                result.error_detail = {
                    "date": date,
                    "message": f"日期{date}是未来日期，股票数据不存在"
                }
                return result
            
            if date_obj < datetime(1990, 1, 1):
                result.is_valid = False
                result.error_code = "DATE_TOO_EARLY"
                result.error_detail = {
                    "date": date,
                    "message": "日期早于1990年，没有相关数据"
                }
                return result
                
        except ValueError:
            result.is_valid = False
            result.error_code = "INVALID_DATE_FORMAT"
            result.error_detail = {
                "date": date,
                "message": "日期格式错误，应为YYYY-MM-DD"
            }
            
        return result
    
    def _validate_date_range(self, date_range: Tuple[str, str], result: ValidationResult) -> ValidationResult:
        """验证日期范围"""
        start_date, end_date = date_range
        
        # 验证日期格式但不验证是否未来（因为日期范围的结束日期可以是未来）
        # 先验证开始日期
        try:
            if len(start_date) == 8 and start_date.isdigit():
                start_obj = datetime.strptime(start_date, '%Y%m%d')
            elif '-' in start_date:
                start_obj = datetime.strptime(start_date, '%Y-%m-%d')
            else:
                raise ValueError(f"不支持的日期格式: {start_date}")
                
            # 开始日期不能是未来日期
            if start_obj > datetime.now():
                result.is_valid = False
                result.error_code = "FUTURE_START_DATE"
                result.error_detail = {
                    "date": start_date,
                    "message": f"开始日期{start_date}不能是未来日期"
                }
                return result
                
            # 开始日期不能早于1990年
            if start_obj < datetime(1990, 1, 1):
                result.is_valid = False
                result.error_code = "DATE_TOO_EARLY"
                result.error_detail = {
                    "date": start_date,
                    "message": "日期早于1990年，没有相关数据"
                }
                return result
                
        except ValueError as e:
            result.is_valid = False
            result.error_code = "INVALID_DATE_FORMAT"
            result.error_detail = {
                "date": start_date,
                "message": f"开始日期格式错误: {str(e)}"
            }
            return result
        
        # 验证结束日期格式（但允许是未来日期）
        try:
            if len(end_date) == 8 and end_date.isdigit():
                end_obj = datetime.strptime(end_date, '%Y%m%d')
            elif '-' in end_date:
                end_obj = datetime.strptime(end_date, '%Y-%m-%d')
            else:
                raise ValueError(f"不支持的日期格式: {end_date}")
                
            # 结束日期可以是未来日期（查询时会自动截止到今天）
            # 但也不能太离谱（比如超过10年后）
            if end_obj > datetime.now() + timedelta(days=3650):
                result.is_valid = False
                result.error_code = "DATE_TOO_FAR"
                result.error_detail = {
                    "date": end_date,
                    "message": "结束日期太远，请使用合理的日期范围"
                }
                return result
                
        except ValueError as e:
            result.is_valid = False
            result.error_code = "INVALID_DATE_FORMAT"
            result.error_detail = {
                "date": end_date,
                "message": f"结束日期格式错误: {str(e)}"
            }
            return result
        
        try:
            # 检查日期顺序（支持多种格式）
            if len(start_date) == 8 and start_date.isdigit():
                start_obj = datetime.strptime(start_date, '%Y%m%d')
            else:
                start_obj = datetime.strptime(start_date, '%Y-%m-%d')
                
            if len(end_date) == 8 and end_date.isdigit():
                end_obj = datetime.strptime(end_date, '%Y%m%d')
            else:
                end_obj = datetime.strptime(end_date, '%Y-%m-%d')
            
            if start_obj > end_obj:
                result.is_valid = False
                result.error_code = "INVALID_DATE_RANGE"
                result.error_detail = {
                    "start_date": start_date,
                    "end_date": end_date,
                    "message": "开始日期不能晚于结束日期"
                }
                return result
            
            # 检查日期范围
            days_diff = (end_obj - start_obj).days
            if days_diff > self.MAX_DATE_RANGE_DAYS:
                result.is_valid = False
                result.error_code = "DATE_RANGE_TOO_LARGE"
                result.error_detail = {
                    "days": days_diff,
                    "max_days": self.MAX_DATE_RANGE_DAYS,
                    "message": f"日期范围不能超过{self.MAX_DATE_RANGE_DAYS}天"
                }
                return result
                
        except Exception as e:
            result.is_valid = False
            result.error_code = "DATE_RANGE_ERROR"
            result.error_detail = {"message": str(e)}
            
        return result
    
    def _validate_limit(self, limit: int, result: ValidationResult) -> ValidationResult:
        """验证数量限制"""
        if limit < self.MIN_LIMIT:
            result.is_valid = False
            result.error_code = "LIMIT_TOO_SMALL"
            result.error_detail = {
                "limit": limit,
                "min": self.MIN_LIMIT,
                "message": f"数量限制不能小于{self.MIN_LIMIT}"
            }
        elif limit > self.MAX_LIMIT:
            result.is_valid = False
            result.error_code = "LIMIT_TOO_LARGE"
            result.error_detail = {
                "limit": limit,
                "max": self.MAX_LIMIT,
                "message": f"数量限制不能大于{self.MAX_LIMIT}"
            }
            
        return result
    
    def _validate_period(self, period: str, result: ValidationResult) -> ValidationResult:
        """验证报告期"""
        # 验证报告期格式（YYYYMMDD）
        if not re.match(r'^\d{8}$', period):
            result.is_valid = False
            result.error_code = "INVALID_PERIOD_FORMAT"
            result.error_detail = {
                "period": period,
                "message": "报告期格式错误，应为YYYYMMDD"
            }
            return result
        
        # 检查是否是有效的报告期（季度末）
        valid_endings = ['0331', '0630', '0930', '1231']
        if period[4:] not in valid_endings:
            result.add_warning(f"报告期{period}可能不是标准的季度报告日期")
            
        return result
    
    def _validate_metrics(self, metrics: List[str], template: Optional[QueryTemplate], result: ValidationResult) -> ValidationResult:
        """验证指标列表"""
        # 如果有模板，检查指标是否在允许范围内
        if template and hasattr(template, 'required_fields') and hasattr(template, 'optional_fields'):
            allowed_metrics = template.required_fields + template.optional_fields
            invalid_metrics = [m for m in metrics if m not in allowed_metrics]
            
            if invalid_metrics:
                result.add_warning(f"以下指标可能不可用: {', '.join(invalid_metrics)}")
                
        return result
    
    def _validate_sector_or_industry(self, params: ExtractedParams, result: ValidationResult) -> ValidationResult:
        """验证板块或行业"""
        # 这里可以添加板块/行业的有效性检查
        # 例如检查是否在预定义的板块列表中
        
        # 暂时只做基本检查
        if params.sector and len(params.sector) > 20:
            result.add_warning(f"板块名称'{params.sector}'可能过长")
            
        if params.industry and len(params.industry) > 20:
            result.add_warning(f"行业名称'{params.industry}'可能过长")
            
        return result
    
    def get_user_friendly_message(self, result: ValidationResult) -> str:
        """
        获取用户友好的错误消息
        
        Args:
            result: 验证结果
            
        Returns:
            str: 用户友好的消息
        """
        if result.is_valid:
            return "参数验证通过"
        
        # 错误消息映射
        error_messages = {
            "PARAM_EXTRACTION_ERROR": "参数提取失败",
            "MISSING_REQUIRED_STOCK": "请指定要查询的股票",
            "MISSING_REQUIRED_DATE": "请指定查询日期",
            "MISSING_REQUIRED_DATE_RANGE": "请指定查询的日期范围",
            "TOO_MANY_STOCKS": "一次查询的股票数量过多",
            "INVALID_STOCK_FORMAT": "股票代码格式错误",
            "INVALID_DATE_FORMAT": "日期格式错误",
            "DATE_TOO_EARLY": "查询日期过早",
            "INVALID_DATE_RANGE": "日期范围无效",
            "DATE_RANGE_TOO_LARGE": "日期范围过大",
            "LIMIT_TOO_SMALL": "查询数量过少",
            "LIMIT_TOO_LARGE": "查询数量过多",
            "INVALID_PERIOD_FORMAT": "报告期格式错误",
            "VALIDATION_ERROR": "参数验证失败"
        }
        
        # 获取基础错误消息
        base_message = error_messages.get(result.error_code, "参数验证失败")
        
        # 如果有详细信息，添加到消息中
        if result.error_detail.get("message"):
            return f"{base_message}: {result.error_detail['message']}"
        
        return base_message
    
    def validate_enhanced(self, params: Any, template: Any) -> 'ValidationResult':
        """增强的验证方法"""
        self.logger.info(f"执行增强验证 - 查询: {params.raw_query}")
        
        # 先执行原有验证
        result = self.validate_params(params, template)
        if not result.is_valid:
            self.logger.info(f"基础验证失败: {result.error_code}")
            return result
        
        # 导入必要的类型
        from utils.query_templates import TemplateType
        
        # 额外的验证规则
        
        # 1. 排名查询的数量必须大于0
        if hasattr(template, 'type') and template.type == TemplateType.RANKING and params.limit <= 0:
            self.logger.info(f"拒绝查询 - 排名数量无效: {params.limit}")
            return ValidationResult(
                is_valid=False,
                error_code="INVALID_LIMIT",
                error_detail={
                    'message': f'排名查询的数量必须大于0，当前值：{params.limit}',
                    'field': 'limit',
                    'value': params.limit
                }
            )
        
        # 2. 个股不能有排名
        if any(keyword in params.raw_query for keyword in ['涨幅排名', '成交量排名', '市值排名', '排名', '排行']):
            # 检查是否指定了具体股票
            if params.stocks and len(params.stocks) == 1:
                # 排除"XX板块"的情况
                if '板块' not in params.raw_query:
                    return ValidationResult(
                        is_valid=False,
                        error_code="INVALID_QUERY",
                        error_detail={
                            'message': '个股不能进行排名查询，请查询该股票的具体数据',
                            'suggestion': f'您可以查询"{params.stock_names[0] if params.stock_names else params.stocks[0]}的涨幅"或"涨幅排名前10"'
                        }
                    )
        
        # 3. 未来日期验证
        if params.date:
            try:
                query_date = datetime.strptime(params.date, '%Y-%m-%d')
                if query_date > datetime.now():
                    return ValidationResult(
                        is_valid=False,
                        error_code="FUTURE_DATE",
                        error_detail={
                            'message': f'不能查询未来日期的数据：{params.date}',
                            'field': 'date',
                            'value': params.date
                        }
                    )
            except:
                pass  # 日期格式错误会在其他地方处理
        
        # 4. 板块查询必须包含"板块"后缀
        # 但需要排除个股名称（如"平安银行"）
        sector_keywords = ['银行', '房地产', '新能源', '白酒', '汽车', '医药', '科技']
        for sector in sector_keywords:
            if sector in params.raw_query and '板块' not in params.raw_query:
                # 检查是否已经识别出具体股票（如果有股票，就不是板块查询）
                if not params.stocks:  # 只有在没有识别出股票时才检查板块
                    # 检查是否是在查询板块数据
                    if any(kw in params.raw_query for kw in ['主力资金', '资金流向', '涨幅', '市值']):
                        return ValidationResult(
                            is_valid=False,
                            error_code="MISSING_SECTOR_SUFFIX",
                            error_detail={
                                'message': f'板块查询必须使用完整名称，如"{sector}板块"',
                                'suggestion': f'请使用"{sector}板块"进行查询'
                            }
                        )
        
        # 5. 非标准术语检查
        non_standard_terms = {
            '机构资金': '主力资金',
            '大资金': '主力资金',
            '游资': '主力资金',  # 游资属于主力资金范畴
            '散户资金': '小单资金',
            '散户': '小单资金',
            '庄家': '主力资金',
            '热钱': '主力资金',
            '大户': '大单资金',
            '中户': '中单资金',
            '小户': '小单资金'
        }
        
        for term, standard_term in non_standard_terms.items():
            if term in params.raw_query:
                self.logger.info(f"拒绝查询 - 非标准术语: {term}")
                return ValidationResult(
                    is_valid=False,
                    error_code="NON_STANDARD_TERM",
                    error_detail={
                        'message': f'请使用标准术语"{standard_term}"替代"{term}"',
                        'term': term,
                        'standard_term': standard_term
                    }
                )
        
        # 6. 数量范围验证（针对排名查询）
        if hasattr(template, 'type') and template.type == TemplateType.RANKING:
            if params.limit > 999:
                self.logger.info(f"拒绝查询 - 排名数量过大: {params.limit}")
                return ValidationResult(
                    is_valid=False,
                    error_code="LIMIT_TOO_LARGE",
                    error_detail={
                        'message': f'排名查询数量不能超过999，当前值：{params.limit}',
                        'field': 'limit',
                        'value': params.limit
                    }
                )
        
        self.logger.info("增强验证通过")
        return ValidationResult(is_valid=True)


# 测试代码
if __name__ == "__main__":
    from utils.parameter_extractor import ParameterExtractor
    
    # 创建提取器和验证器
    extractor = ParameterExtractor()
    validator = QueryValidator()
    
    # 测试用例
    test_cases = [
        {
            "query": "贵州茅台最新股价",
            "template_config": {"requires_stock": True}
        },
        {
            "query": "涨幅前1500的股票",  # 超过限制
            "template_config": {}
        },
        {
            "query": "茅台从1980-01-01到2025-12-31的数据",  # 日期范围问题
            "template_config": {"requires_date_range": True}
        },
        {
            "query": "市值最大的股票",  # 缺少必需的股票
            "template_config": {"requires_stock": True}
        },
        {
            "query": "贵州茅台2024年13月的数据",  # 无效日期
            "template_config": {}
        }
    ]
    
    print("查询验证测试")
    print("=" * 80)
    
    for test in test_cases:
        query = test["query"]
        print(f"\n查询: {query}")
        
        # 创建模拟模板
        template = type('MockTemplate', (), test["template_config"])() if test["template_config"] else None
        
        # 提取参数
        params = extractor.extract_all_params(query, template)
        
        # 验证参数
        result = validator.validate_params(params, template)
        
        print(f"验证结果: {'通过' if result.is_valid else '失败'}")
        if not result.is_valid:
            print(f"错误码: {result.error_code}")
            print(f"错误详情: {result.error_detail}")
            print(f"用户消息: {validator.get_user_friendly_message(result)}")
        
        if result.warnings:
            print(f"警告: {', '.join(result.warnings)}")
