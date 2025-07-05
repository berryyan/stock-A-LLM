#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
深度调试LangChain AgentFinish问题
专门用于分析多股票比较查询的返回值结构
"""

import sys
import os
import json
import time
from datetime import datetime

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.sql_agent_modular import SQLAgentModular


def debug_agent_result():
    """调试Agent返回结果"""
    agent = SQLAgentModular()
    
    # 测试查询
    query = "比较贵州茅台和五粮液"
    
    print("="*80)
    print("LangChain AgentFinish调试")
    print(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80)
    print(f"\n查询: {query}")
    print("-"*40)
    
    try:
        # 直接调用agent.invoke来观察返回值
        print("\n1. 准备调用agent.invoke()...")
        
        # 获取增强的问题
        processed_question, _ = agent.date_intelligence.preprocess_question(query)
        extracted_params = agent.param_extractor.extract_all_params(processed_question)
        enhanced_question = agent._build_enhanced_question(processed_question, extracted_params)
        
        print(f"增强查询: {enhanced_question}")
        
        # 执行查询
        result = agent.agent.invoke({"input": enhanced_question})
        
        print(f"\n2. agent.invoke()返回值类型: {type(result)}")
        print(f"   - 类型名称: {type(result).__name__}")
        print(f"   - 是否是dict: {isinstance(result, dict)}")
        print(f"   - 是否有return_values属性: {hasattr(result, 'return_values')}")
        
        # 详细分析返回结构
        if hasattr(result, 'return_values'):
            print("\n3. AgentFinish对象分析:")
            print(f"   - return_values类型: {type(result.return_values)}")
            print(f"   - return_values内容: {result.return_values}")
            
            if hasattr(result, 'log'):
                print(f"   - log: {result.log[:200]}..." if len(str(result.log)) > 200 else f"   - log: {result.log}")
                
        elif isinstance(result, dict):
            print("\n3. Dict结果分析:")
            print(f"   - keys: {list(result.keys())}")
            for key, value in result.items():
                print(f"   - {key}: {type(value)} = {str(value)[:100]}...")
                
        else:
            print(f"\n3. 其他类型结果: {result}")
            
        # 测试不同的访问方式
        print("\n4. 测试不同的访问方式:")
        
        # 方式1: 直接访问
        try:
            if hasattr(result, 'return_values'):
                print("   - result.return_values 访问成功")
                rv = result.return_values
                if isinstance(rv, dict):
                    print(f"     return_values是dict，keys: {list(rv.keys())}")
                    output = rv.get('output', None)
                    if output:
                        print(f"     output存在: {output[:100]}...")
                else:
                    print(f"     return_values不是dict: {type(rv)}")
        except Exception as e:
            print(f"   - result.return_values 访问失败: {e}")
            
        # 方式2: 使用getattr
        try:
            rv = getattr(result, 'return_values', None)
            if rv is not None:
                print("   - getattr(result, 'return_values') 访问成功")
        except Exception as e:
            print(f"   - getattr 访问失败: {e}")
            
        # 调用完整的查询方法看看错误
        print("\n5. 调用完整查询方法:")
        full_result = agent.query(query)
        print(f"   - 成功: {full_result.get('success')}")
        if not full_result.get('success'):
            print(f"   - 错误: {full_result.get('error')}")
            
    except Exception as e:
        print(f"\n异常: {str(e)}")
        import traceback
        traceback.print_exc()


def test_simple_llm_query():
    """测试简单的LLM查询"""
    agent = SQLAgentModular()
    
    queries = [
        "贵州茅台的总资产是多少",
        "查询平安银行的净利润",
        "分析万科A的财务状况"
    ]
    
    print("\n\n" + "="*80)
    print("测试其他LLM查询")
    print("="*80)
    
    for query in queries:
        print(f"\n查询: {query}")
        print("-"*40)
        
        try:
            result = agent.query(query)
            success = result.get('success', False)
            print(f"成功: {success}")
            if not success:
                print(f"错误: {result.get('error')}")
            else:
                print(f"结果预览: {str(result.get('result', ''))[:100]}...")
        except Exception as e:
            print(f"异常: {str(e)}")


if __name__ == "__main__":
    debug_agent_result()
    test_simple_llm_query()