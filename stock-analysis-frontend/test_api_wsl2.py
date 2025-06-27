#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试API服务器长时间运行任务
用于验证WSL2超时配置是否生效
"""

import requests
import json
import time
from datetime import datetime

# API基础URL - 使用localhost
BASE_URL = "http://localhost:8000"

def print_section(title):
    print(f"\n{'='*60}")
    print(f"{title}")
    print('='*60)

def test_health():
    """测试健康检查"""
    print_section("1. 测试健康检查")
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=10)
        print(f"状态码: {response.status_code}")
        print(f"响应: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
        return True
    except Exception as e:
        print(f"❌ 错误: {e}")
        return False

def test_financial_analysis():
    """测试财务分析 - 长时间运行任务"""
    print_section("2. 测试财务分析（预期25-45秒）")
    
    test_cases = [
        {
            "question": "分析贵州茅台的财务健康状况",
            "expected_time": "25-35秒"
        },
        {
            "question": "对比分析茅台和五粮液的财务状况",
            "expected_time": "35-45秒"
        }
    ]
    
    for i, test in enumerate(test_cases, 1):
        print(f"\n测试 {i}: {test['question']}")
        print(f"预期时间: {test['expected_time']}")
        
        start_time = time.time()
        try:
            response = requests.post(
                f"{BASE_URL}/query",
                json={"question": test["question"]},
                timeout=300  # 5分钟超时
            )
            
            elapsed_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ 成功 - 耗时: {elapsed_time:.2f}秒")
                print(f"查询类型: {data.get('type', 'unknown')}")
                
                # 打印部分响应内容
                if 'result' in data:
                    result_preview = str(data['result'])[:200] + "..."
                    print(f"结果预览: {result_preview}")
            else:
                print(f"❌ 失败 - 状态码: {response.status_code}")
                print(f"错误: {response.text}")
                
        except requests.exceptions.Timeout:
            elapsed_time = time.time() - start_time
            print(f"❌ 超时 - 在{elapsed_time:.2f}秒后超时")
        except Exception as e:
            print(f"❌ 错误: {e}")

def test_money_flow_analysis():
    """测试资金流向分析 - 长时间运行任务"""
    print_section("3. 测试资金流向分析（预期60-120秒）")
    
    test_cases = [
        {
            "question": "分析贵州茅台最近的资金流向",
            "expected_time": "60-80秒"
        },
        {
            "question": "对比茅台、五粮液、泸州老窖的资金流向",
            "expected_time": "90-120秒"
        }
    ]
    
    for i, test in enumerate(test_cases, 1):
        print(f"\n测试 {i}: {test['question']}")
        print(f"预期时间: {test['expected_time']}")
        
        start_time = time.time()
        try:
            response = requests.post(
                f"{BASE_URL}/query",
                json={"question": test["question"]},
                timeout=600  # 10分钟超时
            )
            
            elapsed_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ 成功 - 耗时: {elapsed_time:.2f}秒")
                print(f"查询类型: {data.get('type', 'unknown')}")
                
                # 打印部分响应内容
                if 'result' in data:
                    result_preview = str(data['result'])[:200] + "..."
                    print(f"结果预览: {result_preview}")
            else:
                print(f"❌ 失败 - 状态码: {response.status_code}")
                print(f"错误: {response.text}")
                
        except requests.exceptions.Timeout:
            elapsed_time = time.time() - start_time
            print(f"❌ 超时 - 在{elapsed_time:.2f}秒后超时")
        except Exception as e:
            print(f"❌ 错误: {e}")

def main():
    print("🚀 WSL2长时间运行API测试")
    print(f"开始时间: {datetime.now()}")
    print(f"API地址: {BASE_URL}")
    
    # 先测试健康检查
    if not test_health():
        print("\n❌ API服务器无法访问，请确保服务器已启动")
        return
    
    # 测试长时间运行任务
    test_financial_analysis()
    test_money_flow_analysis()
    
    print(f"\n测试完成时间: {datetime.now()}")
    print("\n✅ WSL2超时配置测试完成!")

if __name__ == "__main__":
    main()