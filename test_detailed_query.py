#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
详细的查询测试，显示完整响应
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import requests
import json
import time
from datetime import datetime


def test_query_detailed(question):
    """详细测试单个查询"""
    print(f"\n{'='*80}")
    print(f"查询: {question}")
    print('='*80)
    
    try:
        start_time = time.time()
        
        # 发送查询请求
        response = requests.post(
            "http://localhost:8000/query",
            json={"question": question},
            timeout=60
        )
        
        elapsed_time = time.time() - start_time
        
        print(f"\n响应状态码: {response.status_code}")
        print(f"响应时间: {elapsed_time:.2f}秒")
        
        if response.status_code == 200:
            data = response.json()
            
            print(f"\n完整响应数据:")
            print(json.dumps(data, indent=2, ensure_ascii=False))
            
            # 特别检查result字段
            result = data.get('result')
            print(f"\nResult类型: {type(result)}")
            print(f"Result内容: {result}")
            
            # 如果是字符串，检查是否为空
            if isinstance(result, str):
                print(f"Result长度: {len(result)}")
                print(f"Result是否为空: {not result or result.isspace()}")
                
        else:
            print(f"\n错误响应: {response.text}")
            
    except Exception as e:
        print(f"\n❌ 异常: {str(e)}")
        import traceback
        traceback.print_exc()


def test_hybrid_agent_directly():
    """直接测试HybridAgent"""
    print(f"\n{'='*80}")
    print("直接测试HybridAgent")
    print('='*80)
    
    try:
        from agents.hybrid_agent import HybridAgent
        
        print("\n初始化HybridAgent...")
        agent = HybridAgent()
        
        # 测试一个简单查询
        question = "贵州茅台的最新股价"
        print(f"\n执行查询: {question}")
        
        result = agent.query(question)
        
        print(f"\n查询结果:")
        print(json.dumps(result, indent=2, ensure_ascii=False))
        
    except Exception as e:
        print(f"\n❌ 异常: {str(e)}")
        import traceback
        traceback.print_exc()


def main():
    print("="*80)
    print("详细查询测试")
    print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80)
    
    # 1. 通过API测试
    print("\n### 通过API测试 ###")
    test_queries = [
        "贵州茅台的最新股价",
        "涨幅排名前5"
    ]
    
    for query in test_queries:
        test_query_detailed(query)
        time.sleep(1)
    
    # 2. 直接测试HybridAgent（可选）
    print("\n### 直接测试HybridAgent ###")
    test_hybrid_agent_directly()
    
    print("\n" + "="*80)
    print("测试完成")
    print("="*80)


if __name__ == "__main__":
    main()