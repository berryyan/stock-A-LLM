#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
统一结果格式化模块
负责将各种查询结果转换为统一的格式
"""

import json
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass, field, asdict
from enum import Enum
from datetime import datetime
import pandas as pd

from utils.logger import setup_logger

logger = setup_logger("result_formatter")


class ResultType(Enum):
    """结果类型枚举"""
    TABLE = "table"          # 表格数据
    TEXT = "text"            # 文本数据
    CHART = "chart"          # 图表数据（预留）
    MIXED = "mixed"          # 混合类型
    ERROR = "error"          # 错误结果


@dataclass
class TableData:
    """表格数据结构"""
    headers: List[str]                    # 表头
    rows: List[List[Any]]                # 数据行
    column_types: Optional[Dict[str, str]] = None  # 列类型信息
    total_count: Optional[int] = None    # 总记录数
    
    def to_markdown(self) -> str:
        """转换为Markdown表格"""
        if not self.rows:
            return "无数据"
            
        # 构建表头
        header_line = " | ".join(self.headers)
        separator_line = " | ".join(["---"] * len(self.headers))
        
        # 构建数据行
        data_lines = []
        for row in self.rows:
            # 格式化每个单元格
            formatted_cells = []
            for i, cell in enumerate(row):
                formatted_cell = self._format_cell(cell, i)
                formatted_cells.append(formatted_cell)
            data_lines.append(" | ".join(formatted_cells))
        
        # 组合成完整的Markdown表格
        markdown = f"| {header_line} |\n| {separator_line} |\n"
        for line in data_lines:
            markdown += f"| {line} |\n"
            
        return markdown
    
    def _format_cell(self, value: Any, col_index: int) -> str:
        """格式化单元格值"""
        if value is None:
            return "-"
            
        # 根据列类型格式化
        if self.column_types and col_index < len(self.headers):
            col_name = self.headers[col_index]
            col_type = self.column_types.get(col_name, "")
            
            if col_type == "number":
                if isinstance(value, (int, float)):
                    # 大数字添加千分符
                    if abs(value) >= 10000:
                        return f"{value:,.0f}"
                    elif abs(value) >= 1:
                        return f"{value:,.2f}"
                    else:
                        return f"{value:.4f}"
                        
            elif col_type == "percent":
                if isinstance(value, (int, float)):
                    return f"{value:.2f}%"
                    
            elif col_type == "date":
                if isinstance(value, datetime):
                    return value.strftime("%Y-%m-%d")
                    
            elif col_type == "money":
                if isinstance(value, (int, float)):
                    # 金额格式化
                    if abs(value) >= 100000000:  # 亿
                        return f"{value/100000000:.2f}亿"
                    elif abs(value) >= 10000:  # 万
                        return f"{value/10000:.2f}万"
                    else:
                        return f"{value:.2f}"
        
        # 默认格式化
        return str(value)


@dataclass
class FormattedResult:
    """格式化后的结果"""
    success: bool                        # 是否成功
    result_type: ResultType              # 结果类型
    data: Optional[Union[str, TableData, Dict]] = None  # 数据内容
    message: Optional[str] = None        # 消息（用于成功或错误）
    metadata: Dict[str, Any] = field(default_factory=dict)  # 元数据
    raw_data: Optional[Any] = None       # 原始数据（便于调试）
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        result = {
            "success": self.success,
            "result_type": self.result_type.value,
            "message": self.message,
            "metadata": self.metadata
        }
        
        # 处理数据字段
        if self.result_type == ResultType.TABLE and isinstance(self.data, TableData):
            result["data"] = {
                "headers": self.data.headers,
                "rows": self.data.rows,
                "column_types": self.data.column_types,
                "total_count": self.data.total_count
            }
            result["markdown"] = self.data.to_markdown()
        elif self.result_type == ResultType.TEXT:
            result["data"] = self.data
        elif self.result_type == ResultType.ERROR:
            result["error"] = self.data
        else:
            result["data"] = self.data
            
        return result
    
    def to_json(self) -> str:
        """转换为JSON字符串"""
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=2)


class ResultFormatter:
    """统一的结果格式化器"""
    
    def __init__(self):
        """初始化格式化器"""
        self.logger = logger
        
    def format_sql_result(self, result: Union[List[Dict], pd.DataFrame], 
                         query_type: str = "general") -> FormattedResult:
        """
        格式化SQL查询结果
        
        Args:
            result: SQL查询结果（字典列表或DataFrame）
            query_type: 查询类型（用于确定格式化方式）
            
        Returns:
            FormattedResult: 格式化后的结果
        """
        try:
            # 转换为DataFrame以便处理
            if isinstance(result, list):
                if not result:
                    return FormattedResult(
                        success=True,
                        result_type=ResultType.TEXT,
                        data="查询无结果",
                        message="查询成功但没有匹配的数据"
                    )
                df = pd.DataFrame(result)
            else:
                df = result
                
            # 根据查询类型确定列类型
            column_types = self._infer_column_types(df, query_type)
            
            # 创建表格数据
            table_data = TableData(
                headers=df.columns.tolist(),
                rows=df.values.tolist(),
                column_types=column_types,
                total_count=len(df)
            )
            
            # 添加统计信息到元数据
            metadata = {
                "row_count": len(df),
                "column_count": len(df.columns),
                "query_type": query_type
            }
            
            return FormattedResult(
                success=True,
                result_type=ResultType.TABLE,
                data=table_data,
                message=f"查询成功，返回{len(df)}条记录",
                metadata=metadata,
                raw_data=result
            )
            
        except Exception as e:
            self.logger.error(f"格式化SQL结果失败: {e}")
            return FormattedResult(
                success=False,
                result_type=ResultType.ERROR,
                data=str(e),
                message="格式化结果时出错"
            )
    
    def format_rag_result(self, documents: List[Dict], answer: str) -> FormattedResult:
        """
        格式化RAG查询结果
        
        Args:
            documents: 检索到的文档列表
            answer: 生成的答案
            
        Returns:
            FormattedResult: 格式化后的结果
        """
        try:
            # 构建格式化的文本结果
            formatted_text = f"**回答**：\n{answer}\n\n"
            
            if documents:
                formatted_text += f"**参考文档** (共{len(documents)}篇)：\n\n"
                for i, doc in enumerate(documents, 1):
                    formatted_text += f"{i}. **{doc.get('title', '未知标题')}**\n"
                    formatted_text += f"   - 股票：{doc.get('stock_name', '未知')} ({doc.get('ts_code', '')})\n"
                    formatted_text += f"   - 日期：{doc.get('date', '未知')}\n"
                    formatted_text += f"   - 相关度：{doc.get('score', 0):.2f}\n"
                    
                    # 添加摘要
                    content = doc.get('content', '')
                    if content:
                        # 截取前200个字符作为摘要
                        summary = content[:200] + "..." if len(content) > 200 else content
                        formatted_text += f"   - 摘要：{summary}\n"
                    formatted_text += "\n"
            
            metadata = {
                "document_count": len(documents),
                "has_answer": bool(answer)
            }
            
            return FormattedResult(
                success=True,
                result_type=ResultType.TEXT,
                data=formatted_text,
                message="RAG查询成功",
                metadata=metadata,
                raw_data={"documents": documents, "answer": answer}
            )
            
        except Exception as e:
            self.logger.error(f"格式化RAG结果失败: {e}")
            return FormattedResult(
                success=False,
                result_type=ResultType.ERROR,
                data=str(e),
                message="格式化结果时出错"
            )
    
    def format_financial_result(self, analysis: Dict) -> FormattedResult:
        """
        格式化财务分析结果
        
        Args:
            analysis: 财务分析结果
            
        Returns:
            FormattedResult: 格式化后的结果
        """
        try:
            # 提取分析类型
            analysis_type = analysis.get("analysis_type", "general")
            
            # 构建格式化文本
            formatted_text = f"## {analysis.get('title', '财务分析报告')}\n\n"
            
            # 添加股票信息
            if "stock_info" in analysis:
                info = analysis["stock_info"]
                formatted_text += f"**股票信息**：{info.get('name', '')} ({info.get('code', '')})\n"
                formatted_text += f"**分析期间**：{info.get('period', '')}\n\n"
            
            # 添加核心指标
            if "key_metrics" in analysis:
                formatted_text += "### 核心财务指标\n\n"
                metrics = analysis["key_metrics"]
                for key, value in metrics.items():
                    formatted_text += f"- **{key}**：{value}\n"
                formatted_text += "\n"
            
            # 添加分析内容
            if "analysis_content" in analysis:
                formatted_text += f"### 详细分析\n\n{analysis['analysis_content']}\n\n"
            
            # 添加结论和建议
            if "conclusion" in analysis:
                formatted_text += f"### 结论\n\n{analysis['conclusion']}\n\n"
                
            if "suggestions" in analysis:
                formatted_text += "### 投资建议\n\n"
                for suggestion in analysis["suggestions"]:
                    formatted_text += f"- {suggestion}\n"
            
            metadata = {
                "analysis_type": analysis_type,
                "has_metrics": "key_metrics" in analysis,
                "has_suggestions": "suggestions" in analysis
            }
            
            return FormattedResult(
                success=True,
                result_type=ResultType.TEXT,
                data=formatted_text,
                message="财务分析完成",
                metadata=metadata,
                raw_data=analysis
            )
            
        except Exception as e:
            self.logger.error(f"格式化财务分析结果失败: {e}")
            return FormattedResult(
                success=False,
                result_type=ResultType.ERROR,
                data=str(e),
                message="格式化结果时出错"
            )
    
    def format_error(self, error: Union[str, Exception], 
                    error_code: Optional[str] = None) -> FormattedResult:
        """
        格式化错误信息
        
        Args:
            error: 错误信息或异常对象
            error_code: 错误代码
            
        Returns:
            FormattedResult: 格式化后的错误结果
        """
        error_message = str(error)
        
        metadata = {}
        if error_code:
            metadata["error_code"] = error_code
            
        if isinstance(error, Exception):
            metadata["error_type"] = type(error).__name__
            
        return FormattedResult(
            success=False,
            result_type=ResultType.ERROR,
            data=error_message,
            message="查询失败",
            metadata=metadata
        )
    
    def _infer_column_types(self, df: pd.DataFrame, query_type: str) -> Dict[str, str]:
        """推断列类型"""
        column_types = {}
        
        # 常见的列名到类型的映射
        type_mappings = {
            # 数值类型
            "close": "number",
            "open": "number", 
            "high": "number",
            "low": "number",
            "vol": "number",
            "amount": "money",
            "market_cap": "money",
            "circ_market_cap": "money",
            
            # 百分比类型
            "pct_chg": "percent",
            "turnover_rate": "percent",
            "pe_ttm": "number",
            "pb": "number",
            "roe": "percent",
            
            # 日期类型
            "trade_date": "date",
            "ann_date": "date",
            "period": "date",
            
            # 金额类型
            "n_income": "money",
            "total_revenue": "money",
            "net_mf_amount": "money",
            "net_elg_amount": "money",
            "net_lg_amount": "money",
            "net_md_amount": "money",
            "net_sm_amount": "money"
        }
        
        for col in df.columns:
            col_lower = col.lower()
            # 先尝试直接匹配
            if col_lower in type_mappings:
                column_types[col] = type_mappings[col_lower]
            # 再尝试部分匹配
            elif any(key in col_lower for key in ["amount", "income", "revenue"]):
                column_types[col] = "money"
            elif any(key in col_lower for key in ["pct", "rate", "ratio"]):
                column_types[col] = "percent"
            elif any(key in col_lower for key in ["date", "time"]):
                column_types[col] = "date"
            elif df[col].dtype in ['int64', 'float64']:
                column_types[col] = "number"
                
        return column_types


# 创建全局格式化器实例
result_formatter = ResultFormatter()


# 便捷函数
def format_sql_result(result: Union[List[Dict], pd.DataFrame], 
                     query_type: str = "general") -> FormattedResult:
    """格式化SQL查询结果"""
    return result_formatter.format_sql_result(result, query_type)


def format_rag_result(documents: List[Dict], answer: str) -> FormattedResult:
    """格式化RAG查询结果"""
    return result_formatter.format_rag_result(documents, answer)


def format_financial_result(analysis: Dict) -> FormattedResult:
    """格式化财务分析结果"""
    return result_formatter.format_financial_result(analysis)


def format_error(error: Union[str, Exception], 
                error_code: Optional[str] = None) -> FormattedResult:
    """格式化错误信息"""
    return result_formatter.format_error(error, error_code)


# 测试代码
if __name__ == "__main__":
    # 测试SQL结果格式化
    sql_data = [
        {"ts_code": "600519.SH", "name": "贵州茅台", "close": 1800.5, 
         "pct_chg": 2.35, "amount": 5678900000},
        {"ts_code": "000858.SZ", "name": "五粮液", "close": 165.8, 
         "pct_chg": -1.23, "amount": 2345600000}
    ]
    
    formatted = format_sql_result(sql_data, "stock_price")
    print("SQL结果格式化:")
    print(formatted.to_json())
    print("\nMarkdown表格:")
    if isinstance(formatted.data, TableData):
        print(formatted.data.to_markdown())
    
    # 测试RAG结果格式化
    print("\n" + "="*80 + "\n")
    rag_docs = [
        {"title": "2024年年报", "stock_name": "贵州茅台", 
         "ts_code": "600519.SH", "date": "2024-03-15", 
         "score": 0.95, "content": "公司2024年实现营业收入..."}
    ]
    rag_answer = "根据年报显示，贵州茅台2024年业绩表现优异..."
    
    formatted_rag = format_rag_result(rag_docs, rag_answer)
    print("RAG结果格式化:")
    print(formatted_rag.data)
    
    # 测试错误格式化
    print("\n" + "="*80 + "\n")
    error_result = format_error("股票代码不存在", "STOCK_NOT_FOUND")
    print("错误结果格式化:")
    print(error_result.to_json())