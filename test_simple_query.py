#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简单的查询测试
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import requests
import json
import time


def test_single_query(question):
    """测试单个查询"""
    print(f"\n查询: {question}")
    print("-" * 60)
    
    try:
        start_time = time.time()
        
        # 发送查询请求
        response = requests.post(
            "http://localhost:8000/query",
            json={"question": question},
            timeout=60
        )
        
        elapsed_time = time.time() - start_time
        
        if response.status_code == 200:
            data = response.json()
            
            print(f"状态码: 200")
            print(f"成功: {data.get('success', False)}")
            print(f"查询类型: {data.get('query_type', 'unknown')}")
            print(f"响应时间: {elapsed_time:.2f}秒")
            
            if data.get('success'):
                result = data.get('result', '')
                # 只显示前300个字符
                if isinstance(result, str):
                    result_preview = result[:300]
                    if len(result) > 300:
                        result_preview += "..."
                else:
                    result_preview = str(result)[:300] + "..."
                    
                print(f"\n结果预览:")
                print(result_preview)
            else:
                print(f"\n错误: {data.get('error', '未知错误')}")
                
        else:
            print(f"状态码: {response.status_code}")
            print(f"错误响应: {response.text[:200]}")
            
    except requests.exceptions.Timeout:
        print("❌ 请求超时（60秒）")
    except requests.exceptions.ConnectionError:
        print("❌ 无法连接到API服务器")
        print("请确保API已启动: python -m uvicorn api.main:app --reload --host 0.0.0.0 --port 8000")
    except Exception as e:
        print(f"❌ 异常: {str(e)}")


def main():
    print("="*60)
    print("简单查询测试")
    print("="*60)
    
    # 测试几个基本查询
    test_queries = [
        "贵州茅台的最新股价",
        "银行板块的主力资金",
        "涨幅排名前5"
    ]
    
    for query in test_queries:
        test_single_query(query)
        time.sleep(1)  # 避免请求过快
    
    print("\n" + "="*60)
    print("测试完成")
    print("="*60)


if __name__ == "__main__":
    main()