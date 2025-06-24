#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试API层面的RAG超时问题
"""

import requests
import json
import time
from datetime import datetime

def test_api_with_detailed_monitoring():
    """详细监控API调用过程"""
    print("=" * 60)
    print("API RAG查询超时诊断")
    print("=" * 60)
    print(f"测试时间: {datetime.now()}")
    print()
    
    api_url = "http://localhost:8000/query"
    
    # 测试查询
    request_data = {
        "question": "贵州茅台2024年的经营策略",
        "context": None
    }
    
    print(f"1. 发送API请求...")
    print(f"   URL: {api_url}")
    print(f"   查询: {request_data['question']}")
    print(f"   开始时间: {datetime.now()}")
    print()
    
    try:
        start_time = time.time()
        
        # 设置更长的超时时间
        response = requests.post(
            api_url,
            json=request_data,
            timeout=120  # 2分钟超时
        )
        
        end_time = time.time()
        duration = end_time - start_time
        
        print(f"2. API响应:")
        print(f"   响应时间: {duration:.2f}秒")
        print(f"   状态码: {response.status_code}")
        print(f"   结束时间: {datetime.now()}")
        print()
        
        if response.status_code == 200:
            result = response.json()
            print(f"3. 响应内容:")
            print(f"   success: {result.get('success', False)}")
            print(f"   query_type: {result.get('query_type', 'None')}")
            print(f"   error: {result.get('error', 'None')}")
            
            if result.get('success'):
                answer = result.get('answer', '')
                print(f"   answer_length: {len(answer)}")
                print(f"   answer_preview: {answer[:200]}...")
                return True
            else:
                print(f"   查询失败，但API响应正常")
                return False
                
        else:
            print(f"   HTTP错误: {response.status_code}")
            print(f"   错误内容: {response.text}")
            return False
            
    except requests.exceptions.Timeout:
        print(f"   ❌ API调用超时（120秒）")
        return False
    except requests.exceptions.ConnectionError:
        print(f"   ❌ 无法连接到API服务器")
        return False
    except Exception as e:
        print(f"   ❌ API调用异常: {e}")
        return False

def test_direct_hybrid_agent():
    """直接测试HybridAgent"""
    print("\n" + "=" * 60)
    print("直接测试HybridAgent")
    print("=" * 60)
    
    try:
        import sys
        import os
        sys.path.append(os.path.dirname(os.path.abspath(__file__)))
        
        from dotenv import load_dotenv
        load_dotenv()
        
        from agents.hybrid_agent import HybridAgent
        
        print("1. 创建HybridAgent...")
        start_time = time.time()
        hybrid_agent = HybridAgent()
        init_time = time.time() - start_time
        print(f"   ✅ HybridAgent创建成功，耗时: {init_time:.2f}秒")
        
        print("2. 执行HybridAgent查询...")
        query = "贵州茅台2024年的经营策略"
        print(f"   查询: {query}")
        print(f"   开始时间: {datetime.now()}")
        
        start_time = time.time()
        result = hybrid_agent.query(query)
        query_time = time.time() - start_time
        
        print(f"   查询耗时: {query_time:.2f}秒")
        print(f"   结束时间: {datetime.now()}")
        print()
        
        print("3. 查询结果:")
        print(f"   success: {result.get('success', False)}")
        print(f"   query_type: {result.get('query_type', 'None')}")
        print(f"   error: {result.get('error', 'None')}")
        
        if result.get('success'):
            answer = result.get('answer', '')
            print(f"   answer_length: {len(answer)}")
            print(f"   answer_preview: {answer[:200]}...")
            return True
        else:
            print(f"   查询失败")
            return False
            
    except Exception as e:
        print(f"   ❌ HybridAgent测试失败: {e}")
        import traceback
        print(f"   异常详情: {traceback.format_exc()}")
        return False

def main():
    """主测试函数"""
    print("API RAG超时问题诊断工具")
    print(f"测试开始时间: {datetime.now()}")
    print()
    
    # 测试1: API调用
    api_success = test_api_with_detailed_monitoring()
    
    # 测试2: 直接HybridAgent调用
    hybrid_success = test_direct_hybrid_agent()
    
    # 总结
    print("\n" + "=" * 60)
    print("诊断总结")
    print("=" * 60)
    print(f"1. API调用: {'✅ 成功' if api_success else '❌ 失败'}")
    print(f"2. HybridAgent直接调用: {'✅ 成功' if hybrid_success else '❌ 失败'}")
    
    if hybrid_success and not api_success:
        print("\n🔍 分析: HybridAgent正常，问题在API层面")
        print("可能原因:")
        print("  1. FastAPI的默认超时设置")
        print("  2. uvicorn服务器配置")
        print("  3. 请求处理中间件问题")
        print("  4. 异步处理问题")
    elif not hybrid_success:
        print("\n🔍 分析: HybridAgent本身有问题")
    else:
        print("\n🎉 所有测试都成功！")

if __name__ == "__main__":
    main()