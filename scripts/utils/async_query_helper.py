#!/usr/bin/env python3
"""
异步查询助手 - 绕过Bash超时限制
用于执行长时间运行的API查询
"""

import asyncio
import aiohttp
import json
import sys
import time
from datetime import datetime
import argparse

async def query_api(question, query_type="hybrid", api_url="http://10.0.0.66:8000", timeout=600):
    """
    异步查询API，支持自定义超时时间
    
    Args:
        question: 查询问题
        query_type: 查询类型 (sql, rag, financial_analysis, money_flow, hybrid)
        api_url: API地址
        timeout: 超时时间（秒）
    """
    url = f"{api_url}/query"
    
    print(f"🚀 开始查询: {question}")
    print(f"📡 API地址: {url}")
    print(f"⏱️  超时设置: {timeout}秒")
    print("-" * 50)
    
    start_time = time.time()
    
    try:
        timeout_config = aiohttp.ClientTimeout(total=timeout)
        async with aiohttp.ClientSession(timeout=timeout_config) as session:
            payload = {
                "question": question,
                "query_type": query_type,
                "top_k": 5
            }
            
            async with session.post(url, json=payload) as response:
                result = await response.json()
                
        end_time = time.time()
        elapsed = end_time - start_time
        
        print(f"\n✅ 查询成功！耗时: {elapsed:.2f}秒")
        print("-" * 50)
        
        return result
        
    except asyncio.TimeoutError:
        print(f"\n❌ 查询超时！已等待 {timeout} 秒")
        return {"success": False, "error": f"Query timeout after {timeout} seconds"}
    except Exception as e:
        print(f"\n❌ 查询失败: {str(e)}")
        return {"success": False, "error": str(e)}

def main():
    parser = argparse.ArgumentParser(description='异步查询助手')
    parser.add_argument('question', help='查询问题')
    parser.add_argument('--type', default='hybrid', help='查询类型')
    parser.add_argument('--timeout', type=int, default=600, help='超时时间（秒）')
    parser.add_argument('--api', default='http://10.0.0.66:8000', help='API地址')
    parser.add_argument('--output', help='输出文件路径')
    
    args = parser.parse_args()
    
    # 运行异步查询
    result = asyncio.run(query_api(
        args.question, 
        args.type, 
        args.api, 
        args.timeout
    ))
    
    # 输出结果
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        print(f"\n📄 结果已保存到: {args.output}")
    else:
        print("\n📋 查询结果:")
        print(json.dumps(result, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()