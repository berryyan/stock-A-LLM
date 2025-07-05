#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试模块化Agent通过API
"""

import requests
import json
import time


def test_query(query: str, query_type: str = None):
    """测试单个查询"""
    print(f"\n{'='*60}")
    print(f"查询: {query}")
    if query_type:
        print(f"类型: {query_type}")
    print('='*60)
    
    url = "http://localhost:8000/query"
    payload = {
        "question": query,
        "query_type": query_type
    }
    
    try:
        start_time = time.time()
        response = requests.post(url, json=payload)
        elapsed_time = time.time() - start_time
        
        if response.status_code == 200:
            result = response.json()
            print(f"状态码: {response.status_code}")
            print(f"成功: {result.get('success')}")
            print(f"耗时: {elapsed_time:.2f}秒")
            
            if result.get('success'):
                # 检查是否有answer字段（API返回的格式）
                answer_text = result.get('answer', '')
                if answer_text:
                    # 只显示结果的前500个字符
                    if len(answer_text) > 500:
                        print(f"\n结果预览:\n{answer_text[:500]}...")
                    else:
                        print(f"\n结果:\n{answer_text}")
                else:
                    # 如果没有answer字段，可能是其他格式
                    print("\n警告：响应中没有answer字段")
                    print(f"响应键: {list(result.keys())}")
                
                # 显示元数据
                if 'query_type' in result:
                    print(f"\n查询类型: {result.get('query_type')}")
                if 'quick_path' in result:
                    print(f"快速路径: {result.get('quick_path')}")
            else:
                print(f"\n错误: {result.get('error')}")
                if 'suggestion' in result:
                    print(f"建议: {result.get('suggestion')}")
        else:
            print(f"HTTP错误: {response.status_code}")
            print(f"响应: {response.text}")
            
    except Exception as e:
        print(f"请求异常: {str(e)}")


def main():
    print("="*60)
    print("测试模块化Agent API")
    print("="*60)
    
    # 测试用例 - 基于 test-guide-comprehensive.md v5.3
    test_cases = [
        # 1.1 股价查询模板测试
        ("贵州茅台的最新股价", "sql"),
        ("中国平安昨天的股价", "sql"),
        ("600519.SH的股价", "sql"),
        
        # 1.2 成交量查询模板测试
        ("平安银行昨天的成交量", "sql"),
        ("万科A前天的成交量", "sql"),  # v2.1.17重点测试
        
        # 1.3 估值指标查询模板测试
        ("中国平安的市盈率", "sql"),
        
        # 1.5 涨跌幅排名模板测试
        ("今天涨幅最大的前10只股票", "sql"),
        
        # 1.6 市值排名模板测试
        ("市值排名前3", "sql"),
        ("总市值排名", "sql"),  # 无数字默认前10
        
        # 1.10 个股主力资金查询模板测试
        ("贵州茅台的主力资金", "sql"),
        
        # 1.11 板块主力资金查询模板测试
        ("银行板块的主力资金", "sql"),
    ]
    
    for query, query_type in test_cases:
        test_query(query, query_type)
        time.sleep(1)  # 避免请求过快


if __name__ == "__main__":
    main()