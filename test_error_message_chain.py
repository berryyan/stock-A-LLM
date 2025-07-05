#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试错误消息传递链
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.sql_agent_modular import SQLAgentModular
from agents.hybrid_agent_modular import HybridAgentModular
from utils.error_handler import error_handler


def test_error_message_propagation():
    """测试错误消息在各层的传递"""
    print("测试错误消息传递链")
    print("=" * 80)
    
    # 测试1: 直接测试error_handler
    print("\n1. 测试error_handler:")
    error_info = error_handler.handle_error("测试错误", "INVALID_STOCK")
    print(f"   错误码: {error_info.error_code}")
    print(f"   用户消息: {error_info.user_message}")
    print(f"   建议: {error_info.suggestion}")
    
    # 测试2: 测试SQL Agent
    print("\n2. 测试SQL Agent:")
    sql_agent = SQLAgentModular()
    sql_result = sql_agent.query("abc")
    print(f"   成功: {sql_result.get('success')}")
    print(f"   错误: {sql_result.get('error')}")
    print(f"   结果: {sql_result.get('result')}")
    
    # 测试3: 测试Hybrid Agent
    print("\n3. 测试Hybrid Agent:")
    hybrid_agent = HybridAgentModular()
    hybrid_result = hybrid_agent.query("abc")
    print(f"   成功: {hybrid_result.get('success')}")
    print(f"   错误: {hybrid_result.get('error')}")
    print(f"   查询类型: {hybrid_result.get('query_type')}")
    
    # 检查sources中的sql结果
    if 'sources' in hybrid_result and 'sql' in hybrid_result['sources']:
        print("\n   SQL源结果:")
        sql_source = hybrid_result['sources']['sql']
        print(f"   - 成功: {sql_source.get('success')}")
        print(f"   - 错误: {sql_source.get('error')}")
    
    print("\n" + "=" * 80)


if __name__ == "__main__":
    test_error_message_propagation()