#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
调试错误消息传递链
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.hybrid_agent_modular import HybridAgentModular


def test_error_chain():
    """测试错误消息传递链"""
    print("测试错误消息传递链")
    print("=" * 80)
    
    # 初始化HybridAgent
    hybrid_agent = HybridAgentModular()
    
    # 测试无效输入
    test_query = "abc"
    print(f"测试查询: {test_query}")
    
    # 执行查询
    result = hybrid_agent.query(test_query)
    
    print("\nHybridAgent返回的结果:")
    print(f"success: {result.get('success')}")
    print(f"error: {result.get('error')}")
    print(f"query_type: {result.get('query_type')}")
    print(f"answer: {result.get('answer')}")
    
    # 如果有sources，打印SQL Agent的返回
    if 'sources' in result and 'sql' in result['sources']:
        sql_result = result['sources']['sql']
        print("\nSQL Agent返回的结果:")
        print(f"success: {sql_result.get('success')}")
        print(f"error: {sql_result.get('error')}")
        print(f"result: {sql_result.get('result')}")


if __name__ == "__main__":
    test_error_chain()