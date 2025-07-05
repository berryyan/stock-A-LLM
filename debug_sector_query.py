#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
调试板块主力资金查询
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.parameter_extractor import ParameterExtractor
from utils.query_templates import match_query_template
from agents.sql_agent_modular import SQLAgentModular
import json


def test_template_matching():
    """测试模板匹配"""
    query = "银行板块的主力资金"
    print(f"测试查询: {query}")
    print("="*60)
    
    # 测试模板匹配
    template_match = match_query_template(query)
    if template_match:
        template, params = template_match
        print(f"\n匹配到模板: {template.name}")
        print(f"模板参数: {params}")
        print(f"路由类型: {template.route_type}")
    else:
        print("未匹配到模板")
        
    return template_match


def test_parameter_extraction():
    """测试参数提取"""
    print("\n\n测试参数提取")
    print("="*60)
    
    extractor = ParameterExtractor()
    query = "银行板块的主力资金"
    
    params = extractor.extract_all_params(query)
    
    print(f"提取结果:")
    print(f"  板块: {params.sector}")
    print(f"  板块代码: {getattr(params, 'sector_code', 'None')}")
    print(f"  股票: {params.stocks}")
    print(f"  日期: {params.date}")
    print(f"  错误: {params.error}")
    
    return params


def test_sql_query():
    """测试SQL查询"""
    print("\n\n测试SQL Agent处理")
    print("="*60)
    
    agent = SQLAgentModular()
    
    # 测试快速查询路径
    query = "银行板块的主力资金"
    
    # 获取处理后的查询
    from utils import date_intelligence
    processed_query, _ = date_intelligence.preprocess_question(query) if hasattr(date_intelligence, 'preprocess_question') else (query, None)
    print(f"处理后的查询: {processed_query}")
    
    # 调用_try_quick_query方法
    quick_result = agent._try_quick_query(query)
    
    print(f"\n快速查询结果:")
    if quick_result:
        print(f"  成功: {quick_result.get('success')}")
        if quick_result.get('success'):
            print(f"  结果预览: {str(quick_result.get('result', ''))[:200]}...")
        else:
            print(f"  错误: {quick_result.get('error')}")
    else:
        print("  快速查询未返回结果")
        
    # 测试完整查询
    print("\n\n测试完整查询:")
    full_result = agent.query(query)
    print(f"  成功: {full_result.get('success')}")
    if full_result.get('success'):
        print(f"  结果: {full_result.get('result')}")
    else:
        print(f"  错误: {full_result.get('error')}")


def main():
    print("板块主力资金查询调试")
    print("="*80)
    
    # 1. 测试模板匹配
    test_template_matching()
    
    # 2. 测试参数提取
    test_parameter_extraction()
    
    # 3. 测试SQL查询
    test_sql_query()


if __name__ == "__main__":
    main()