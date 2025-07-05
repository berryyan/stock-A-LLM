#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
统一错误处理模块
负责处理所有查询过程中的错误和异常
"""

import sys
import traceback
from typing import Dict, Optional, Union, Any, Callable
from dataclasses import dataclass
from enum import Enum
from functools import wraps

from utils.logger import setup_logger
from utils.result_formatter import FormattedResult, ResultType, format_error

logger = setup_logger("error_handler")


class ErrorCategory(Enum):
    """错误类别枚举"""
    INPUT_ERROR = "input_error"          # 输入错误
    VALIDATION_ERROR = "validation_error" # 验证错误
    DATABASE_ERROR = "database_error"    # 数据库错误
    NETWORK_ERROR = "network_error"      # 网络错误
    PROCESSING_ERROR = "processing_error" # 处理错误
    SYSTEM_ERROR = "system_error"        # 系统错误
    UNKNOWN_ERROR = "unknown_error"      # 未知错误


class ErrorSeverity(Enum):
    """错误严重程度枚举"""
    LOW = "low"          # 低（可以继续处理）
    MEDIUM = "medium"    # 中（部分功能受影响）
    HIGH = "high"        # 高（查询失败）
    CRITICAL = "critical" # 严重（系统级错误）


@dataclass
class ErrorInfo:
    """错误信息数据类"""
    error_code: str                      # 错误代码
    error_message: str                   # 错误消息
    user_message: str                    # 用户友好的错误消息
    category: ErrorCategory              # 错误类别
    severity: ErrorSeverity              # 错误严重程度
    details: Optional[Dict[str, Any]] = None  # 详细信息
    suggestion: Optional[str] = None     # 修复建议
    traceback: Optional[str] = None      # 错误堆栈（仅在调试模式）


class ErrorHandler:
    """统一的错误处理器"""
    
    # 错误代码映射
    ERROR_MAPPINGS = {
        # 输入错误
        "EMPTY_QUERY": {
            "message": "查询内容为空",
            "user_message": "请输入查询内容",
            "category": ErrorCategory.INPUT_ERROR,
            "severity": ErrorSeverity.LOW,
            "suggestion": "请输入您想查询的股票信息或问题"
        },
        "INVALID_STOCK_FORMAT": {
            "message": "股票代码格式错误",
            "user_message": "股票代码格式不正确",
            "category": ErrorCategory.INPUT_ERROR,
            "severity": ErrorSeverity.LOW,
            "suggestion": "请输入正确的股票代码，如：600519或600519.SH"
        },
        "INVALID_STOCK": {
            "message": "无法识别输入内容",
            "user_message": "无法识别输入内容",
            "category": ErrorCategory.INPUT_ERROR,
            "severity": ErrorSeverity.LOW,
            "suggestion": "请输入：1) 6位股票代码（如002047）2) 证券代码（如600519.SH）3) 股票名称（如贵州茅台）"
        },
        "STOCK_NOT_EXISTS": {
            "message": "股票代码不存在",
            "user_message": "未找到该股票",
            "category": ErrorCategory.INPUT_ERROR,
            "severity": ErrorSeverity.LOW,
            "suggestion": "请检查股票代码是否正确，或使用完整的股票名称"
        },
        "USE_FULL_NAME": {
            "message": "需要使用完整公司名称",
            "user_message": "请使用完整的公司名称",
            "category": ErrorCategory.INPUT_ERROR,
            "severity": ErrorSeverity.LOW,
            "suggestion": "系统不支持股票简称，请使用完整的公司名称，如：贵州茅台、中国平安等"
        },
        
        # 验证错误
        "INVALID_DATE_FORMAT": {
            "message": "日期格式错误",
            "user_message": "日期格式不正确",
            "category": ErrorCategory.VALIDATION_ERROR,
            "severity": ErrorSeverity.LOW,
            "suggestion": "请使用YYYY-MM-DD格式的日期，如：2025-07-04"
        },
        "DATE_RANGE_INVALID": {
            "message": "日期范围无效",
            "user_message": "日期范围设置有误",
            "category": ErrorCategory.VALIDATION_ERROR,
            "severity": ErrorSeverity.LOW,
            "suggestion": "结束日期应该晚于开始日期"
        },
        "LIMIT_TOO_LARGE": {
            "message": "查询数量过多",
            "user_message": "一次查询的数据量过大",
            "category": ErrorCategory.VALIDATION_ERROR,
            "severity": ErrorSeverity.LOW,
            "suggestion": "建议减少查询数量，最多支持1000条"
        },
        
        # 数据库错误
        "DATABASE_CONNECTION_ERROR": {
            "message": "数据库连接失败",
            "user_message": "无法连接到数据库",
            "category": ErrorCategory.DATABASE_ERROR,
            "severity": ErrorSeverity.HIGH,
            "suggestion": "请稍后重试，如果问题持续，请联系技术支持"
        },
        "QUERY_TIMEOUT": {
            "message": "查询超时",
            "user_message": "查询时间过长",
            "category": ErrorCategory.DATABASE_ERROR,
            "severity": ErrorSeverity.MEDIUM,
            "suggestion": "请尝试缩小查询范围或稍后重试"
        },
        "NO_DATA_FOUND": {
            "message": "未找到数据",
            "user_message": "没有找到符合条件的数据",
            "category": ErrorCategory.DATABASE_ERROR,
            "severity": ErrorSeverity.LOW,
            "suggestion": "请检查查询条件或尝试其他查询"
        },
        
        # 处理错误
        "LLM_ERROR": {
            "message": "AI模型处理失败",
            "user_message": "AI处理您的请求时出现问题",
            "category": ErrorCategory.PROCESSING_ERROR,
            "severity": ErrorSeverity.HIGH,
            "suggestion": "请尝试简化您的问题或稍后重试"
        },
        "VECTOR_SEARCH_ERROR": {
            "message": "向量搜索失败",
            "user_message": "文档搜索出现问题",
            "category": ErrorCategory.PROCESSING_ERROR,
            "severity": ErrorSeverity.MEDIUM,
            "suggestion": "请尝试使用不同的关键词搜索"
        },
        
        # 系统错误
        "INTERNAL_ERROR": {
            "message": "内部错误",
            "user_message": "系统内部错误",
            "category": ErrorCategory.SYSTEM_ERROR,
            "severity": ErrorSeverity.CRITICAL,
            "suggestion": "请联系技术支持"
        }
    }
    
    def __init__(self, debug_mode: bool = False):
        """
        初始化错误处理器
        
        Args:
            debug_mode: 是否启用调试模式（显示详细错误信息）
        """
        self.debug_mode = debug_mode
        self.logger = logger
        
    def handle_error(self, error: Union[str, Exception], 
                    error_code: Optional[str] = None,
                    details: Optional[Dict[str, Any]] = None) -> ErrorInfo:
        """
        处理错误
        
        Args:
            error: 错误信息或异常对象
            error_code: 错误代码
            details: 额外的错误详情
            
        Returns:
            ErrorInfo: 错误信息对象
        """
        # 获取错误映射
        error_mapping = self.ERROR_MAPPINGS.get(error_code, {})
        
        # 构建错误信息
        if error_mapping:
            # 如果错误是字符串且包含详细信息，优先使用原始错误消息
            if isinstance(error, str) and error and error != error_mapping.get("message", ""):
                user_msg = error
            else:
                user_msg = error_mapping.get("user_message", "查询出现错误")
                
            error_info = ErrorInfo(
                error_code=error_code,
                error_message=error_mapping.get("message", str(error)),
                user_message=user_msg,
                category=error_mapping.get("category", ErrorCategory.UNKNOWN_ERROR),
                severity=error_mapping.get("severity", ErrorSeverity.MEDIUM),
                suggestion=error_mapping.get("suggestion"),
                details=details
            )
        else:
            # 未知错误
            # 如果错误是字符串且有内容，使用原始错误消息
            if isinstance(error, str) and error:
                user_msg = error
            else:
                user_msg = "查询过程中出现未知错误"
                
            error_info = ErrorInfo(
                error_code=error_code or "UNKNOWN_ERROR",
                error_message=str(error),
                user_message=user_msg,
                category=ErrorCategory.UNKNOWN_ERROR,
                severity=ErrorSeverity.HIGH,
                details=details
            )
        
        # 如果是异常对象，提取堆栈信息
        if isinstance(error, Exception) and self.debug_mode:
            error_info.traceback = traceback.format_exc()
            
        # 记录错误日志
        self._log_error(error_info)
        
        return error_info
    
    def get_user_friendly_message(self, error_info: ErrorInfo) -> str:
        """
        获取用户友好的错误消息
        
        Args:
            error_info: 错误信息对象
            
        Returns:
            str: 用户友好的错误消息
        """
        message = error_info.user_message
        
        # 添加详细信息（如果有）
        if error_info.details:
            detail_parts = []
            for key, value in error_info.details.items():
                if key in ["invalid_value", "expected_format"]:
                    detail_parts.append(f"{key}: {value}")
            if detail_parts:
                message += f" ({', '.join(detail_parts)})"
        
        # 添加建议（如果有）
        if error_info.suggestion:
            message += f"\n建议：{error_info.suggestion}"
            
        return message
    
    def format_error_response(self, error_info: ErrorInfo) -> FormattedResult:
        """
        格式化错误响应
        
        Args:
            error_info: 错误信息对象
            
        Returns:
            FormattedResult: 格式化的错误结果
        """
        user_message = self.get_user_friendly_message(error_info)
        
        metadata = {
            "error_code": error_info.error_code,
            "category": error_info.category.value,
            "severity": error_info.severity.value
        }
        
        if self.debug_mode:
            metadata["error_message"] = error_info.error_message
            if error_info.traceback:
                metadata["traceback"] = error_info.traceback
                
        return FormattedResult(
            success=False,
            result_type=ResultType.ERROR,
            data=user_message,
            message="查询失败",
            metadata=metadata
        )
    
    def _log_error(self, error_info: ErrorInfo):
        """记录错误日志"""
        log_message = f"[{error_info.error_code}] {error_info.error_message}"
        
        if error_info.details:
            log_message += f" | Details: {error_info.details}"
            
        # 根据严重程度选择日志级别
        if error_info.severity == ErrorSeverity.CRITICAL:
            self.logger.critical(log_message)
        elif error_info.severity == ErrorSeverity.HIGH:
            self.logger.error(log_message)
        elif error_info.severity == ErrorSeverity.MEDIUM:
            self.logger.warning(log_message)
        else:
            self.logger.info(log_message)


# 创建全局错误处理器实例
error_handler = ErrorHandler()


def handle_query_errors(func: Callable) -> Callable:
    """
    查询错误处理装饰器
    
    用于装饰查询函数，自动捕获和处理错误
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            # 尝试从异常中提取错误代码
            error_code = getattr(e, 'error_code', None)
            details = getattr(e, 'details', None)
            
            # 处理错误
            error_info = error_handler.handle_error(e, error_code, details)
            
            # 返回格式化的错误结果
            return error_handler.format_error_response(error_info)
            
    return wrapper


# 自定义异常类
class QueryError(Exception):
    """查询错误基类"""
    def __init__(self, message: str, error_code: str, details: Optional[Dict] = None):
        super().__init__(message)
        self.error_code = error_code
        self.details = details


class InputError(QueryError):
    """输入错误"""
    pass


class ValidationError(QueryError):
    """验证错误"""
    pass


class DatabaseError(QueryError):
    """数据库错误"""
    pass


class ProcessingError(QueryError):
    """处理错误"""
    pass


# 便捷函数
def handle_error(error: Union[str, Exception], 
                error_code: Optional[str] = None,
                details: Optional[Dict[str, Any]] = None) -> ErrorInfo:
    """处理错误"""
    return error_handler.handle_error(error, error_code, details)


def get_user_friendly_message(error_info: ErrorInfo) -> str:
    """获取用户友好的错误消息"""
    return error_handler.get_user_friendly_message(error_info)


def format_error_response(error_info: ErrorInfo) -> FormattedResult:
    """格式化错误响应"""
    return error_handler.format_error_response(error_info)


# 测试代码
if __name__ == "__main__":
    # 测试错误处理
    print("测试错误处理")
    print("=" * 80)
    
    # 测试已知错误
    error1 = handle_error("股票代码格式不正确", "INVALID_STOCK_FORMAT", 
                         {"invalid_value": "600519.sh"})
    print(f"错误1: {get_user_friendly_message(error1)}")
    print(f"格式化响应: {format_error_response(error1).to_json()}")
    
    print("\n" + "-" * 80 + "\n")
    
    # 测试异常处理
    try:
        raise ValueError("测试异常")
    except Exception as e:
        error2 = handle_error(e, "INTERNAL_ERROR")
        print(f"错误2: {get_user_friendly_message(error2)}")
    
    print("\n" + "-" * 80 + "\n")
    
    # 测试装饰器
    @handle_query_errors
    def test_query():
        raise InputError("股票简称不支持", "USE_FULL_NAME", 
                        {"input": "茅台", "suggestion": "贵州茅台"})
    
    result = test_query()
    print(f"装饰器测试结果: {result.to_json()}")