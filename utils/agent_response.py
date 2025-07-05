#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
统一的Agent响应格式
所有模块化Agent都应该使用这个响应格式
"""

from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass, field, asdict
from enum import Enum
import json

from utils.error_handler import ErrorInfo


class ResponseType(Enum):
    """响应类型枚举"""
    DATA = "data"              # 数据查询响应
    ANALYSIS = "analysis"      # 分析类响应
    ERROR = "error"            # 错误响应
    INFO = "info"              # 信息提示


@dataclass
class AgentResponse:
    """
    统一的Agent响应格式
    所有模块化Agent都应该返回这个格式
    """
    success: bool                              # 是否成功
    response_type: ResponseType                # 响应类型
    data: Optional[Any] = None                # 主要数据
    error: Optional[ErrorInfo] = None         # 错误信息（如果有）
    message: Optional[str] = None             # 用户友好的消息
    metadata: Dict[str, Any] = field(default_factory=dict)  # 元数据
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        result = {
            "success": self.success,
            "response_type": self.response_type.value,
            "message": self.message
        }
        
        # 添加数据
        if self.data is not None:
            result["data"] = self.data
            
        # 添加错误信息
        if self.error:
            result["error"] = {
                "code": self.error.error_code,
                "message": self.error.user_message,
                "category": self.error.category.value,
                "severity": self.error.severity.value
            }
            if self.error.suggestion:
                result["error"]["suggestion"] = self.error.suggestion
                
        # 添加元数据
        if self.metadata:
            result["metadata"] = self.metadata
            
        return result
    
    def to_json(self) -> str:
        """转换为JSON字符串"""
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=2)
    
    def to_legacy_format(self, agent_type: str) -> Dict[str, Any]:
        """
        转换为旧格式，保持向后兼容
        注意：这个方法仅用于过渡期，最终应该废弃
        """
        if agent_type == "sql":
            return {
                'success': self.success,
                'result': self.data if self.success else None,
                'error': self.error.user_message if self.error else self.message,
                'sql': self.metadata.get('sql'),
                'quick_path': self.metadata.get('quick_path', False)
            }
        elif agent_type == "rag":
            return {
                'success': self.success,
                'error': self.error.error_code if self.error else None,
                'message': self.message or (self.error.user_message if self.error else ""),
                'type': 'rag_query',
                'question': self.metadata.get('question', ''),
                'result': self.data
            }
        elif agent_type == "financial":
            return {
                'success': self.success,
                'result': self.data,
                'error': self.error.user_message if self.error else None,
                'analysis_type': self.metadata.get('analysis_type')
            }
        elif agent_type == "money_flow":
            return {
                'success': self.success,
                'result': self.data,
                'error': self.error.user_message if self.error else None,
                'flow_type': self.metadata.get('flow_type')
            }
        else:
            # 默认格式
            return self.to_dict()
    
    @classmethod
    def success_response(cls, data: Any, message: str = None, 
                        response_type: ResponseType = ResponseType.DATA,
                        **metadata) -> 'AgentResponse':
        """创建成功响应"""
        return cls(
            success=True,
            response_type=response_type,
            data=data,
            message=message,
            metadata=metadata
        )
    
    @classmethod
    def error_response(cls, error: Union[str, ErrorInfo, Exception], 
                      error_code: str = None, **metadata) -> 'AgentResponse':
        """创建错误响应"""
        # 处理不同类型的错误输入
        if isinstance(error, ErrorInfo):
            error_info = error
        elif isinstance(error, str):
            from utils.error_handler import error_handler
            error_info = error_handler.handle_error(error, error_code)
        else:  # Exception
            from utils.error_handler import error_handler
            error_info = error_handler.handle_error(error, error_code)
            
        return cls(
            success=False,
            response_type=ResponseType.ERROR,
            error=error_info,
            message=error_info.user_message,
            metadata=metadata
        )


# 便捷函数
def success(data: Any, message: str = None, **metadata) -> AgentResponse:
    """创建成功响应的快捷方式"""
    return AgentResponse.success_response(data, message, **metadata)


def error(error_msg: str, error_code: str = None, **metadata) -> AgentResponse:
    """创建错误响应的快捷方式"""
    return AgentResponse.error_response(error_msg, error_code, **metadata)


def analysis(data: Any, message: str = None, **metadata) -> AgentResponse:
    """创建分析类响应的快捷方式"""
    return AgentResponse.success_response(
        data, message, 
        response_type=ResponseType.ANALYSIS, 
        **metadata
    )


# 测试代码
if __name__ == "__main__":
    print("测试统一响应格式")
    print("=" * 80)
    
    # 测试成功响应
    resp1 = success(
        data={"price": 1580.5, "change": 2.3},
        message="查询成功",
        sql="SELECT * FROM stock_price",
        quick_path=True
    )
    print("成功响应：")
    print(resp1.to_json())
    print("\n转换为SQL Agent格式：")
    print(json.dumps(resp1.to_legacy_format("sql"), ensure_ascii=False, indent=2))
    
    print("\n" + "-" * 80 + "\n")
    
    # 测试错误响应
    resp2 = error(
        "未找到股票代码",
        error_code="STOCK_NOT_FOUND",
        query="查询茅台股价"
    )
    print("错误响应：")
    print(resp2.to_json())
    print("\n转换为SQL Agent格式：")
    print(json.dumps(resp2.to_legacy_format("sql"), ensure_ascii=False, indent=2))