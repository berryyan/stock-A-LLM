#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Hybrid Agent 快速验证脚本
专注于核心路由功能验证
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.hybrid_agent_modular import HybridAgentModular
import time
import json

def quick_verify():
    """快速验证核心路由功能"""
    print("=" * 80)
    print("Hybrid Agent 快速验证")
    print("=" * 80)
    
    agent = HybridAgentModular()
    
    # 测试用例：每种路由类型2-3个
    test_cases = [
        # SQL路由测试
        ("贵州茅台的股价是多少", "SQL", "股价查询"),
        ("今天涨幅前10的股票", "SQL", "排名查询"),
        ("万科A的成交量", "SQL", "成交量查询"),
        
        # RAG路由测试
        ("贵州茅台的主要业务是什么", "RAG", "业务查询"),
        ("万科A最新的公告内容", "RAG", "公告查询"),
        
        # Financial路由测试
        ("分析贵州茅台的财务健康度", "Financial", "财务分析"),
        ("万科A的杜邦分析", "Financial", "杜邦分析"),
        
        # Money Flow路由测试
        ("贵州茅台的主力资金流向", "MoneyFlow", "资金流向"),
        ("主力资金净流入前10", "MoneyFlow", "资金排名"),
        
        # 复合查询测试
        ("贵州茅台的股价和主要业务", "Composite", "SQL+RAG"),
        ("万科A的财务状况和最新公告", "Composite", "Financial+RAG"),
        
        # 错误处理测试
        ("", "Error", "空查询"),
        ("茅台", "Error", "股票简称"),
    ]
    
    results = {
        "total": len(test_cases),
        "passed": 0,
        "failed": 0,
        "details": []
    }
    
    for query, expected_type, test_name in test_cases:
        print(f"\n测试: {test_name}")
        print(f"查询: {query}")
        print(f"期望路由: {expected_type}")
        
        start_time = time.time()
        try:
            result = agent.query(query)
            elapsed_time = time.time() - start_time
            
            # 判断路由是否正确
            # 这里需要分析结果来判断实际路由
            actual_type = detect_actual_route(result, query)
            
            # 对于错误测试，期望失败
            if expected_type == "Error":
                test_passed = not result.get('success', True)
            # 对于复合查询，检查是否有多个结果
            elif expected_type == "Composite":
                test_passed = result.get('success', False) and is_composite_result(result)
            # 对于单一路由，检查是否路由正确
            else:
                test_passed = result.get('success', False) and actual_type == expected_type
            
            if test_passed:
                print(f"✅ 测试通过")
                results["passed"] += 1
            else:
                print(f"❌ 测试失败")
                print(f"实际路由: {actual_type}")
                results["failed"] += 1
                
            print(f"耗时: {elapsed_time:.2f}秒")
            
            if not result.get('success', True):
                print(f"错误: {result.get('error', '未知错误')}")
            
            results["details"].append({
                "test_name": test_name,
                "query": query,
                "expected": expected_type,
                "actual": actual_type,
                "passed": test_passed,
                "elapsed": elapsed_time,
                "error": result.get('error') if not result.get('success', True) else None
            })
            
        except Exception as e:
            print(f"❌ 异常: {str(e)}")
            results["failed"] += 1
            results["details"].append({
                "test_name": test_name,
                "query": query,
                "expected": expected_type,
                "actual": "Exception",
                "passed": False,
                "error": str(e)
            })
    
    # 打印总结
    print(f"\n{'='*80}")
    print("测试总结")
    print(f"{'='*80}")
    print(f"总测试数: {results['total']}")
    print(f"通过: {results['passed']} ({results['passed']/results['total']*100:.1f}%)")
    print(f"失败: {results['failed']} ({results['failed']/results['total']*100:.1f}%)")
    
    # 保存结果
    with open('hybrid_agent_quick_verify_results.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print(f"\n详细结果已保存到: hybrid_agent_quick_verify_results.json")
    
    return results["failed"] == 0

def detect_actual_route(result, query):
    """检测实际使用的路由"""
    if not result.get('success', False):
        return "Error"
    
    # 检查结果中的线索
    # Hybrid Agent返回'answer'字段，其他Agent返回'result'字段
    result_text = str(result.get('answer', result.get('result', '')))
    
    # 检查是否是复合查询结果
    if '查询结果' in result_text and ('业务' in result_text or '公告' in result_text) and ('股价' in result_text or '财务' in result_text):
        return "Composite"
    
    # 根据结果特征判断路由
    if any(word in result_text for word in ['元/股', '涨跌幅', '成交量', '市值', 'K线']):
        return "SQL"
    elif any(word in result_text for word in ['主营业务', '公告', '战略', '竞争优势', '发展']):
        return "RAG"
    elif any(word in result_text for word in ['财务健康度', '杜邦分析', 'ROE', '财务状况', '现金流质量']):
        return "Financial"
    elif any(word in result_text for word in ['主力资金', '资金流向', '净流入', '超大单']):
        return "MoneyFlow"
    
    # 如果无法判断，看查询内容
    if '资金' in query or '主力' in query:
        return "MoneyFlow"
    elif '财务' in query or '杜邦' in query or '健康度' in query:
        return "Financial"
    elif '业务' in query or '公告' in query or '战略' in query:
        return "RAG"
    else:
        return "SQL"

def is_composite_result(result):
    """判断是否是复合查询结果"""
    # Hybrid Agent返回'answer'字段
    result_text = str(result.get('answer', result.get('result', '')))
    
    # 检查是否包含多种类型的信息
    has_sql = any(word in result_text for word in ['股价', '市值', '成交量'])
    has_rag = any(word in result_text for word in ['业务', '公告', '战略'])
    has_financial = any(word in result_text for word in ['财务', 'ROE', '健康度'])
    has_money = any(word in result_text for word in ['资金', '主力'])
    
    # 如果包含2种或以上类型的信息，认为是复合查询
    type_count = sum([has_sql, has_rag, has_financial, has_money])
    return type_count >= 2

if __name__ == "__main__":
    success = quick_verify()
    exit(0 if success else 1)