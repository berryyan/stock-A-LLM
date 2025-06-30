#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
安全过滤器模块
用于过滤和清理LLM输出，防止SQL注入等安全风险
"""

import re
from typing import Dict, Any, List, Optional
from utils.logger import setup_logger


class SecurityFilter:
    """LLM输出安全过滤器"""
    
    def __init__(self):
        self.logger = setup_logger("security_filter")
        
        # SQL关键字列表（不区分大小写）
        self.sql_keywords = [
            'SELECT', 'INSERT', 'UPDATE', 'DELETE', 'DROP', 'CREATE', 'ALTER',
            'TRUNCATE', 'EXEC', 'EXECUTE', 'FROM', 'WHERE', 'JOIN', 'UNION',
            'GROUP BY', 'ORDER BY', 'HAVING', 'LIMIT', 'OFFSET', 'INTO',
            'VALUES', 'SET', 'TABLE', 'DATABASE', 'SCHEMA', 'INDEX', 'VIEW',
            'PROCEDURE', 'FUNCTION', 'TRIGGER', 'GRANT', 'REVOKE'
        ]
        
        # SQL语句模式（更严格的检测）
        self.sql_patterns = [
            # 基本SQL语句模式
            r'\b(SELECT|INSERT|UPDATE|DELETE|DROP|CREATE|ALTER)\s+.*\b(FROM|INTO|TABLE|DATABASE)\b',
            # SELECT语句模式
            r'\bSELECT\s+.+\s+FROM\s+\w+',
            # INSERT语句模式
            r'\bINSERT\s+INTO\s+\w+\s*\(',
            # UPDATE语句模式
            r'\bUPDATE\s+\w+\s+SET\s+',
            # DELETE语句模式
            r'\bDELETE\s+FROM\s+\w+',
            # 查询语句建议模式
            r'(查询语句|SQL语句|执行|运行)[为是：:\s]*[`\'"]?.*?(SELECT|INSERT|UPDATE|DELETE)',
            # 建议查询模式
            r'建议.*?查询.*?(SELECT|FROM|WHERE)',
        ]
        
        # 编译正则表达式
        self.sql_regex = [re.compile(pattern, re.IGNORECASE | re.DOTALL) for pattern in self.sql_patterns]
        
        # 敏感信息模式
        self.sensitive_patterns = [
            r'\b(password|pwd|passwd|api_key|secret|token)\s*[=:]\s*[\'"]?[\w\-]+',
            r'\b(mysql|postgres|oracle|sqlserver)://[\w:@\.\-/]+',
        ]
        
        self.sensitive_regex = [re.compile(pattern, re.IGNORECASE) for pattern in self.sensitive_patterns]
    
    def contains_sql_statement(self, text: str) -> bool:
        """检测文本是否包含SQL语句"""
        if not text:
            return False
            
        # 检查SQL模式
        for pattern in self.sql_regex:
            if pattern.search(text):
                self.logger.warning(f"检测到SQL语句模式: {pattern.pattern}")
                return True
        
        # 检查连续的SQL关键字
        upper_text = text.upper()
        sql_keyword_count = 0
        for keyword in self.sql_keywords:
            if f' {keyword} ' in f' {upper_text} ':
                sql_keyword_count += 1
                if sql_keyword_count >= 3:  # 如果包含3个或更多SQL关键字
                    self.logger.warning(f"检测到多个SQL关键字: {sql_keyword_count}个")
                    return True
        
        return False
    
    def contains_sensitive_info(self, text: str) -> bool:
        """检测文本是否包含敏感信息"""
        if not text:
            return False
            
        for pattern in self.sensitive_regex:
            if pattern.search(text):
                self.logger.warning(f"检测到敏感信息模式: {pattern.pattern}")
                return True
        
        return False
    
    def filter_sql_statements(self, text: str) -> str:
        """过滤掉SQL语句，返回清理后的文本"""
        if not text:
            return text
        
        filtered_text = text
        
        # 移除SQL语句块
        for pattern in self.sql_regex:
            filtered_text = pattern.sub('[SQL语句已被过滤]', filtered_text)
        
        # 移除包含SQL建议的句子
        lines = filtered_text.split('\n')
        filtered_lines = []
        for line in lines:
            if not any(keyword in line.upper() for keyword in ['查询语句为', 'SQL语句', '执行以下查询']):
                filtered_lines.append(line)
            else:
                self.logger.info(f"过滤掉包含SQL建议的行: {line[:50]}...")
        
        return '\n'.join(filtered_lines)
    
    def filter_sensitive_info(self, text: str) -> str:
        """过滤敏感信息"""
        if not text:
            return text
            
        filtered_text = text
        for pattern in self.sensitive_regex:
            filtered_text = pattern.sub('[敏感信息已被过滤]', filtered_text)
        
        return filtered_text
    
    def clean_llm_output(self, text: str, allow_sql: bool = False) -> Dict[str, Any]:
        """
        清理LLM输出
        
        Args:
            text: LLM的原始输出
            allow_sql: 是否允许SQL语句（默认False）
            
        Returns:
            {
                "success": bool,
                "cleaned_text": str,
                "has_sql": bool,
                "has_sensitive": bool,
                "warning": str (optional)
            }
        """
        result = {
            "success": True,
            "cleaned_text": text,
            "has_sql": False,
            "has_sensitive": False
        }
        
        # 检测SQL语句
        if self.contains_sql_statement(text):
            result["has_sql"] = True
            if not allow_sql:
                result["cleaned_text"] = self.filter_sql_statements(text)
                result["warning"] = "检测到SQL语句并已过滤。为了安全起见，系统不会直接返回SQL查询语句。"
                self.logger.warning("LLM输出包含SQL语句，已过滤")
        
        # 检测敏感信息
        if self.contains_sensitive_info(result["cleaned_text"]):
            result["has_sensitive"] = True
            result["cleaned_text"] = self.filter_sensitive_info(result["cleaned_text"])
            if "warning" in result:
                result["warning"] += " 同时检测到敏感信息并已过滤。"
            else:
                result["warning"] = "检测到敏感信息并已过滤。"
            self.logger.warning("LLM输出包含敏感信息，已过滤")
        
        return result
    
    def validate_query_input(self, query: str) -> Dict[str, Any]:
        """
        验证用户查询输入
        
        Returns:
            {
                "valid": bool,
                "query": str (cleaned),
                "error": str (if invalid)
            }
        """
        if not query or not query.strip():
            return {
                "valid": False,
                "query": "",
                "error": "查询内容不能为空"
            }
        
        # 检查是否包含恶意SQL注入尝试
        suspicious_patterns = [
            r';\s*(DROP|DELETE|TRUNCATE|UPDATE)\s+',
            r'--\s*$',
            r'/\*.*\*/',
            r'(OR|AND)\s+\d+\s*=\s*\d+',
            r'UNION\s+SELECT',
        ]
        
        for pattern in suspicious_patterns:
            if re.search(pattern, query, re.IGNORECASE):
                self.logger.error(f"检测到可疑的SQL注入尝试: {query}")
                return {
                    "valid": False,
                    "query": query,
                    "error": "检测到可疑的查询模式，请使用正常的自然语言提问"
                }
        
        return {
            "valid": True,
            "query": query.strip(),
            "error": None
        }


# 创建全局实例
security_filter = SecurityFilter()


# 便捷函数
def clean_llm_output(text: str, allow_sql: bool = False) -> Dict[str, Any]:
    """清理LLM输出的便捷函数"""
    return security_filter.clean_llm_output(text, allow_sql)


def validate_query(query: str) -> Dict[str, Any]:
    """验证查询输入的便捷函数"""
    return security_filter.validate_query_input(query)


# 测试代码
if __name__ == "__main__":
    # 测试SQL语句检测
    test_cases = [
        "贵州茅台的净利润是100亿元。",
        "建议查询最近5个报告期的数据，查询语句为：SELECT end_date, profit_dedt FROM tu_fina_indicator WHERE ts_code='601318.SH' ORDER BY end_date DESC LIMIT 5",
        "你可以执行 SELECT * FROM stocks WHERE code = '600519'",
        "营业收入增长了20%，净利润增长了15%。",
        "数据库连接字符串是 mysql://user:password@localhost/db",
        "API密钥是: api_key=sk-1234567890",
    ]
    
    print("安全过滤器测试")
    print("=" * 60)
    
    for i, text in enumerate(test_cases, 1):
        print(f"\n测试用例 {i}:")
        print(f"原文: {text[:100]}...")
        result = clean_llm_output(text)
        print(f"包含SQL: {result['has_sql']}")
        print(f"包含敏感信息: {result['has_sensitive']}")
        if result.get('warning'):
            print(f"警告: {result['warning']}")
        if result['cleaned_text'] != text:
            print(f"清理后: {result['cleaned_text'][:100]}...")