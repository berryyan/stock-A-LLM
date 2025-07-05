#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试模块化系统集成
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import requests
import json
import time
from datetime import datetime


def test_api_health():
    """测试API健康状态"""
    print("\n" + "="*60)
    print("测试API健康状态")
    print("="*60)
    
    try:
        response = requests.get("http://localhost:8000/health")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ API健康检查成功")
            print(f"状态: {data['status']}")
            if 'version' in data:
                print(f"版本: {data['version']}")
            if 'services' in data:
                print(f"服务状态: {json.dumps(data['services'], indent=2, ensure_ascii=False)}")
            return True
        else:
            print(f"❌ 健康检查失败，状态码: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 连接失败: {str(e)}")
        print("\n请确保:")
        print("1. 后端API已启动: python -m uvicorn api.main:app --reload --host 0.0.0.0 --port 8000")
        print("2. 前端已启动: cd frontend && npm run dev")
        return False


def test_web_interface():
    """测试Web界面"""
    print("\n" + "="*60)
    print("测试Web界面")
    print("="*60)
    
    try:
        # 检查前端是否运行
        response = requests.get("http://localhost:5173", timeout=5)
        if response.status_code == 200:
            print("✅ 前端界面运行正常 (http://localhost:5173)")
            return True
    except:
        pass
    
    try:
        # 检查后端的Web界面
        response = requests.get("http://localhost:8000", timeout=5)
        if response.status_code == 200:
            print("✅ 后端Web界面运行正常 (http://localhost:8000)")
            return True
    except:
        pass
    
    print("❌ Web界面未运行")
    return False


def test_query_functionality():
    """测试查询功能"""
    print("\n" + "="*60)
    print("测试查询功能（使用模块化Agent）")
    print("="*60)
    
    test_queries = [
        {
            "question": "贵州茅台的最新股价",
            "expected_type": "sql"
        },
        {
            "question": "银行板块的主力资金",
            "expected_type": "sql"
        },
        {
            "question": "贵州茅台最新的公告",
            "expected_type": "rag"
        }
    ]
    
    success_count = 0
    
    for test in test_queries:
        print(f"\n测试查询: {test['question']}")
        print("-" * 40)
        
        try:
            start_time = time.time()
            response = requests.post(
                "http://localhost:8000/query",
                json={"question": test['question']},
                timeout=60
            )
            elapsed_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                if data['success']:
                    print(f"✅ 查询成功")
                    print(f"查询类型: {data.get('query_type', 'unknown')}")
                    print(f"响应时间: {elapsed_time:.2f}秒")
                    
                    # 检查是否使用了模块化Agent（通过日志或其他方式判断）
                    result_preview = str(data.get('result', ''))[:200]
                    print(f"结果预览: {result_preview}...")
                    
                    success_count += 1
                else:
                    print(f"❌ 查询失败: {data.get('error', '未知错误')}")
            else:
                print(f"❌ 请求失败，状态码: {response.status_code}")
                
        except Exception as e:
            print(f"❌ 请求异常: {str(e)}")
    
    print(f"\n总结: {success_count}/{len(test_queries)} 个查询成功")
    return success_count == len(test_queries)


def check_modular_agent_status():
    """检查是否在使用模块化Agent"""
    print("\n" + "="*60)
    print("检查模块化Agent状态")
    print("="*60)
    
    try:
        from config.modular_settings import USE_MODULAR_AGENTS
        if USE_MODULAR_AGENTS:
            print("✅ 系统配置为使用模块化Agent")
        else:
            print("❌ 系统配置为使用传统Agent")
            print("提示：修改 config/modular_settings.py 中的 USE_MODULAR_AGENTS = True")
        return USE_MODULAR_AGENTS
    except ImportError:
        print("❌ 无法导入模块化配置")
        return False


def main():
    """主测试函数"""
    print("="*60)
    print("股票分析系统模块化测试")
    print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)
    
    # 1. 检查模块化配置
    modular_enabled = check_modular_agent_status()
    
    # 2. 测试API健康状态
    if not test_api_health():
        return
    
    # 3. 测试Web界面
    test_web_interface()
    
    # 4. 测试查询功能
    if modular_enabled:
        test_query_functionality()
    else:
        print("\n⚠️ 跳过查询测试，因为未启用模块化Agent")
    
    print("\n" + "="*60)
    print("测试完成")
    print("\n下一步:")
    print("1. 如果测试失败，检查日志文件: logs/hybrid_agent.log")
    print("2. 确保数据库服务正常运行")
    print("3. 在Web界面进行更多测试: http://localhost:5173 或 http://localhost:8000")
    print("="*60)


if __name__ == "__main__":
    main()