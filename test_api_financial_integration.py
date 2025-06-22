#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
API财务分析集成测试
测试Phase 1财务分析功能是否成功集成到API
"""

import requests
import json
import time
from typing import Dict, Any

# API基础URL
BASE_URL = "http://localhost:8000"

def test_api_root():
    """测试API根路径"""
    print("🧪 测试API根路径")
    print("=" * 50)
    
    try:
        response = requests.get(f"{BASE_URL}/")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ API根路径访问成功")
            print(f"版本: {data.get('version')}")
            print(f"功能特性: {', '.join(data.get('features', []))}")
            return True
        else:
            print(f"❌ API根路径访问失败: {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ API服务器未启动，请先运行:")
        print("python -m uvicorn api.main:app --reload --host 0.0.0.0 --port 8000")
        return False
    except Exception as e:
        print(f"❌ 测试异常: {e}")
        return False

def test_health_check():
    """测试健康检查"""
    print("\n🧪 测试健康检查")
    print("=" * 50)
    
    try:
        response = requests.get(f"{BASE_URL}/health")
        data = response.json()
        
        print(f"状态: {data.get('status')}")
        print(f"MySQL连接: {'✅' if data.get('mysql') else '❌'}")
        print(f"Milvus连接: {'✅' if data.get('milvus') else '❌'}")
        
        return data.get('status') == 'healthy'
        
    except Exception as e:
        print(f"❌ 健康检查失败: {e}")
        return False

def test_general_query_routing():
    """测试通用查询的财务分析路由"""
    print("\n🧪 测试通用查询路由到财务分析")
    print("=" * 50)
    
    test_queries = [
        "分析贵州茅台的财务健康状况",
        "600519.SH的杜邦分析",
        "茅台的现金流质量如何",
        "平安银行的财务评级"
    ]
    
    for query in test_queries:
        print(f"\n🔍 测试查询: {query}")
        print("-" * 40)
        
        try:
            payload = {
                "question": query,
                "context": None,
                "filters": None,
                "top_k": 5
            }
            
            start_time = time.time()
            response = requests.post(f"{BASE_URL}/query", json=payload, timeout=120)
            processing_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                
                print(f"✅ 查询成功")
                print(f"查询类型: {data.get('query_type', 'unknown')}")
                print(f"处理时间: {processing_time:.2f}秒")
                
                if data.get('success'):
                    if data.get('query_type') == 'financial':
                        print("🎯 成功路由到财务分析!")
                        # 显示答案摘要
                        answer = data.get('answer', '')
                        if answer:
                            preview = answer[:150] + "..." if len(answer) > 150 else answer
                            print(f"分析摘要: {preview}")
                    else:
                        print(f"⚠️ 路由到: {data.get('query_type')}")
                else:
                    print(f"❌ 查询失败: {data.get('error')}")
            else:
                print(f"❌ HTTP错误: {response.status_code}")
                
        except requests.exceptions.Timeout:
            print("⏰ 查询超时 (120秒)")
        except Exception as e:
            print(f"❌ 查询异常: {e}")

def test_dedicated_financial_api():
    """测试专门的财务分析API端点"""
    print("\n🧪 测试专门的财务分析API端点")
    print("=" * 50)
    
    test_cases = [
        {"ts_code": "600519.SH", "analysis_type": "financial_health", "name": "贵州茅台财务健康度"},
        {"ts_code": "000001.SZ", "analysis_type": "dupont_analysis", "name": "平安银行杜邦分析"},
        {"ts_code": "000002.SZ", "analysis_type": "cash_flow_quality", "name": "万科A现金流质量"}
    ]
    
    for case in test_cases:
        print(f"\n📊 测试: {case['name']}")
        print("-" * 40)
        
        try:
            payload = {
                "ts_code": case["ts_code"],
                "analysis_type": case["analysis_type"]
            }
            
            start_time = time.time()
            response = requests.post(f"{BASE_URL}/financial-analysis", json=payload, timeout=120)
            processing_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                
                print(f"✅ API调用成功")
                print(f"处理时间: {processing_time:.2f}秒")
                print(f"分析成功: {'✅' if data.get('success') else '❌'}")
                
                if data.get('success'):
                    print(f"股票代码: {data.get('ts_code')}")
                    print(f"分析类型: {data.get('analysis_type')}")
                    
                    # 显示分析报告摘要
                    report = data.get('analysis_report', '')
                    if report:
                        preview = report[:200] + "..." if len(report) > 200 else report
                        print(f"分析报告摘要: {preview}")
                        
                    # 显示财务数据摘要
                    financial_data = data.get('financial_data')
                    if financial_data:
                        if financial_data.get('health_score'):
                            score = financial_data['health_score']
                            print(f"财务评级: {score.get('rating')} ({score.get('total_score')}/100)")
                        elif financial_data.get('dupont_metrics'):
                            dupont = financial_data['dupont_metrics']
                            if dupont.get('valid'):
                                print(f"净利率: {dupont.get('net_profit_margin', 'N/A')}%")
                                print(f"ROE: {dupont.get('reported_roe', 'N/A')}%")
                else:
                    print(f"❌ 分析失败: {data.get('error')}")
            else:
                print(f"❌ HTTP错误: {response.status_code}")
                print(f"响应: {response.text}")
                
        except requests.exceptions.Timeout:
            print("⏰ 请求超时 (120秒)")
        except Exception as e:
            print(f"❌ 请求异常: {e}")

def test_api_documentation():
    """测试API文档访问"""
    print("\n🧪 测试API文档")
    print("=" * 50)
    
    try:
        # 测试OpenAPI文档
        response = requests.get(f"{BASE_URL}/docs")
        
        if response.status_code == 200:
            print("✅ Swagger文档可访问: http://localhost:8000/docs")
        else:
            print("❌ Swagger文档访问失败")
        
        # 测试ReDoc文档
        response = requests.get(f"{BASE_URL}/redoc")
        
        if response.status_code == 200:
            print("✅ ReDoc文档可访问: http://localhost:8000/redoc")
        else:
            print("❌ ReDoc文档访问失败")
            
    except Exception as e:
        print(f"❌ 文档测试异常: {e}")

def main():
    """主测试函数"""
    print("🚀 API财务分析集成测试")
    print("=" * 80)
    
    # 基础连接测试
    if not test_api_root():
        print("\n⚠️ API服务器未启动，终止测试")
        return
    
    # 健康检查
    if not test_health_check():
        print("\n⚠️ 系统健康检查失败，但继续测试")
    
    # 通用查询路由测试
    test_general_query_routing()
    
    # 专门财务分析API测试
    test_dedicated_financial_api()
    
    # API文档测试
    test_api_documentation()
    
    print("\n" + "=" * 80)
    print("🎉 API财务分析集成测试完成!")
    print("\n📖 使用指南:")
    print("1. 通用查询: POST /query")
    print("   - 自动识别财务分析查询并路由")
    print("   - 支持自然语言: '分析茅台的财务健康度'")
    print("\n2. 专门财务分析: POST /financial-analysis")
    print("   - 直接调用财务分析功能")
    print("   - 支持四种分析类型: financial_health, dupont_analysis, cash_flow_quality, multi_period_comparison")
    print("\n3. API文档: http://localhost:8000/docs")

if __name__ == "__main__":
    main()