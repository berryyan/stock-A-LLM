#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试模块化API是否正常工作
"""
import requests
import json
from datetime import datetime

API_BASE_URL = "http://localhost:8001"

def test_health():
    """测试健康检查端点"""
    print("\n=== 测试健康检查 ===")
    try:
        response = requests.get(f"{API_BASE_URL}/health")
        if response.status_code == 200:
            data = response.json()
            print("✓ 健康检查成功")
            print(f"  - 状态: {data.get('status')}")
            print(f"  - MySQL连接: {data.get('mysql_connected')}")
            print(f"  - Milvus连接: {data.get('milvus_connected')}")
            print(f"  - Agent就绪: {data.get('agent_ready')}")
            print(f"  - 版本: {data.get('version')}")
            return True
        else:
            print(f"✗ 健康检查失败: HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ 连接失败: {str(e)}")
        print("  提示: 请确保模块化API正在运行（端口8001）")
        return False

def test_query(question):
    """测试查询端点"""
    print(f"\n=== 测试查询: {question} ===")
    try:
        response = requests.post(
            f"{API_BASE_URL}/query",
            json={"question": question},
            timeout=120
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                print("✓ 查询成功")
                print(f"  - 查询类型: {data.get('query_type')}")
                print(f"  - 答案预览: {data.get('answer', '')[:100]}...")
                return True
            else:
                print(f"✗ 查询失败: {data.get('error')}")
                return False
        else:
            print(f"✗ HTTP错误: {response.status_code}")
            return False
            
    except requests.exceptions.Timeout:
        print("✗ 查询超时（超过120秒）")
        return False
    except Exception as e:
        print(f"✗ 请求失败: {str(e)}")
        return False

def main():
    """主测试函数"""
    print("=== 模块化API测试 ===")
    print(f"API地址: {API_BASE_URL}")
    print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 测试健康检查
    health_ok = test_health()
    if not health_ok:
        print("\n⚠️ API未就绪，请先启动模块化API服务器")
        print("运行: python -m uvicorn api.main_modular:app --reload --host 0.0.0.0 --port 8001")
        return
    
    # 测试各种查询
    test_queries = [
        "贵州茅台最新股价",  # SQL查询
    ]
    
    for query in test_queries:
        test_query(query)
    
    print("\n=== 测试完成 ===")
    print("\n如果所有测试通过，说明模块化API工作正常！")
    print("可以使用 start_modular_system.bat 启动完整的前后端系统")

if __name__ == "__main__":
    main()