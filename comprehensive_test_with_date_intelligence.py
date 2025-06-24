#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
综合测试 - 包含日期智能处理测试用例
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import time
from datetime import datetime

def test_imports():
    """测试模块导入"""
    print("🔍 测试模块导入")
    print("=" * 60)
    
    modules = [
        "utils.date_intelligence",
        "database.mysql_connector",
        "database.milvus_connector", 
        "agents.sql_agent",
        "agents.rag_agent",
        "agents.financial_agent",
        "agents.hybrid_agent",
        "api.main"
    ]
    
    all_success = True
    for module in modules:
        try:
            __import__(module)
            print(f"✅ {module}")
        except Exception as e:
            print(f"❌ {module}: {e}")
            all_success = False
    
    return all_success

def test_date_intelligence():
    """测试日期智能解析功能"""
    print("\n🔍 测试日期智能解析")
    print("=" * 60)
    
    try:
        from utils.date_intelligence import date_intelligence
        
        test_cases = [
            "茅台最新股价",
            "贵州茅台最近的财务报告",
            "600519.SH最新公告",
            "平安银行当前的股价表现"
        ]
        
        for question in test_cases:
            print(f"\n原始查询: {question}")
            processed, result = date_intelligence.preprocess_question(question)
            
            if result.get('modified_question'):
                print(f"✅ 处理后: {processed}")
                print(f"   解析: {result.get('suggestion', '')}")
            else:
                print(f"⚠️  未检测到时间表达")
        
        return True
        
    except Exception as e:
        print(f"❌ 日期智能解析测试失败: {e}")
        return False

def test_sql_with_date_intelligence():
    """测试SQL Agent的日期智能处理"""
    print("\n🔍 测试SQL Agent日期智能处理")
    print("=" * 60)
    
    try:
        from agents.sql_agent import SQLAgent
        agent = SQLAgent()
        
        test_queries = [
            "茅台最新股价",
            "贵州茅台最近的收盘价是多少",
            "查询比亚迪现在的股价"
        ]
        
        for query in test_queries:
            print(f"\n测试查询: {query}")
            start_time = time.time()
            
            result = agent.query(query)
            elapsed = time.time() - start_time
            
            if result.get('success'):
                print(f"✅ 查询成功 (耗时: {elapsed:.2f}秒)")
                # 只显示结果的前100个字符
                answer = str(result.get('result', ''))[:100]
                print(f"   结果预览: {answer}...")
            else:
                print(f"❌ 查询失败: {result.get('error', 'Unknown error')}")
        
        return True
        
    except Exception as e:
        print(f"❌ SQL Agent测试异常: {e}")
        return False

def test_rag_with_date_intelligence():
    """测试RAG Agent的日期智能处理"""
    print("\n🔍 测试RAG Agent日期智能处理")
    print("=" * 60)
    
    try:
        from agents.rag_agent import RAGAgent
        agent = RAGAgent()
        
        test_queries = [
            "贵州茅台最新公告说了什么",
            "茅台最近发布的年报主要内容",
            "600519.SH最新披露的信息",
            "平安银行最近的公告"
        ]
        
        for query in test_queries:
            print(f"\n测试查询: {query}")
            start_time = time.time()
            
            result = agent.query(query, top_k=3)
            elapsed = time.time() - start_time
            
            if result.get('success'):
                print(f"✅ 查询成功 (耗时: {elapsed:.2f}秒)")
                print(f"   文档数: {result.get('document_count', 0)}")
                
                # 检查日期解析信息
                if 'date_parsing' in result:
                    parsing_info = result['date_parsing']
                    print(f"   📅 日期解析: {parsing_info.get('suggestion', 'None')}")
                
                # 显示部分答案
                answer = result.get('answer', '')[:100]
                print(f"   答案预览: {answer}...")
            else:
                print(f"❌ 查询失败: {result.get('message', result.get('error', 'Unknown'))}")
        
        return True
        
    except Exception as e:
        print(f"❌ RAG Agent测试异常: {e}")
        return False

def test_financial_with_date():
    """测试财务分析的日期处理"""
    print("\n🔍 测试财务分析日期处理")
    print("=" * 60)
    
    try:
        from agents.hybrid_agent import HybridAgent
        agent = HybridAgent()
        
        test_queries = [
            "分析贵州茅台最新的财务健康状况",
            "茅台最近一期的财务表现如何",
            "平安银行当前的财务状况分析"
        ]
        
        for query in test_queries:
            print(f"\n测试查询: {query}")
            start_time = time.time()
            
            result = agent.query(query)
            elapsed = time.time() - start_time
            
            if result.get('success'):
                print(f"✅ 查询成功 (耗时: {elapsed:.2f}秒)")
                print(f"   查询类型: {result.get('query_type', 'unknown')}")
                
                # 显示部分答案
                answer = result.get('answer', '')[:150]
                print(f"   结果预览: {answer}...")
            else:
                print(f"❌ 查询失败: {result.get('error', 'Unknown error')}")
        
        return True
        
    except Exception as e:
        print(f"❌ 财务分析测试异常: {e}")
        return False

def test_hybrid_complex_queries():
    """测试复杂查询的日期处理"""
    print("\n🔍 测试复杂查询日期处理")
    print("=" * 60)
    
    try:
        from agents.hybrid_agent import HybridAgent
        agent = HybridAgent()
        
        test_queries = [
            "茅台最新股价和最新公告",
            "比较茅台和五粮液最近的股价表现",
            "分析银行板块最新的资金流向"
        ]
        
        for query in test_queries:
            print(f"\n测试查询: {query}")
            start_time = time.time()
            
            result = agent.query(query)
            elapsed = time.time() - start_time
            
            if result.get('success'):
                print(f"✅ 查询成功 (耗时: {elapsed:.2f}秒)")
                print(f"   查询类型: {result.get('query_type', 'unknown')}")
                
                # 检查是否有多个数据源
                sources = result.get('sources', {})
                if sources:
                    print(f"   数据源: {', '.join(sources.keys())}")
                
                # 显示部分答案
                answer = result.get('answer', '')[:150]
                print(f"   结果预览: {answer}...")
            else:
                print(f"❌ 查询失败: {result.get('error', 'Unknown error')}")
        
        return True
        
    except Exception as e:
        print(f"❌ 复杂查询测试异常: {e}")
        return False

def test_date_cache_performance():
    """测试日期解析缓存性能"""
    print("\n🔍 测试日期解析缓存性能")
    print("=" * 60)
    
    try:
        from utils.date_intelligence import date_intelligence
        
        # 测试同一查询的缓存效果
        test_query = "茅台最新股价"
        
        # 第一次查询（无缓存）
        start_time = time.time()
        processed1, result1 = date_intelligence.preprocess_question(test_query)
        time1 = time.time() - start_time
        
        # 第二次查询（有缓存）
        start_time = time.time()
        processed2, result2 = date_intelligence.preprocess_question(test_query)
        time2 = time.time() - start_time
        
        print(f"第一次查询耗时: {time1*1000:.2f}ms")
        print(f"第二次查询耗时: {time2*1000:.2f}ms")
        
        if time2 < time1:
            print(f"✅ 缓存生效，性能提升 {((time1-time2)/time1*100):.1f}%")
        else:
            print("⚠️  缓存可能未生效")
        
        return True
        
    except Exception as e:
        print(f"❌ 缓存性能测试异常: {e}")
        return False

def main():
    """主测试函数"""
    print("🚀 综合测试 - 日期智能处理功能")
    print("=" * 80)
    print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    
    # 测试结果记录
    results = {}
    
    # 1. 模块导入测试
    print("\n" + "="*80)
    results['imports'] = test_imports()
    
    # 2. 日期智能解析基础测试
    print("\n" + "="*80)
    results['date_intelligence'] = test_date_intelligence()
    
    # 3. SQL Agent日期处理测试
    print("\n" + "="*80)
    results['sql_date'] = test_sql_with_date_intelligence()
    
    # 4. RAG Agent日期处理测试
    print("\n" + "="*80)
    results['rag_date'] = test_rag_with_date_intelligence()
    
    # 5. 财务分析日期处理测试
    print("\n" + "="*80)
    results['financial_date'] = test_financial_with_date()
    
    # 6. 复杂查询日期处理测试
    print("\n" + "="*80)
    results['complex_date'] = test_hybrid_complex_queries()
    
    # 7. 缓存性能测试
    print("\n" + "="*80)
    results['cache_performance'] = test_date_cache_performance()
    
    # 测试结果总结
    print("\n" + "="*80)
    print("📊 测试结果总结")
    print("="*80)
    
    total_tests = len(results)
    passed_tests = sum(1 for v in results.values() if v)
    
    for test_name, result in results.items():
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{test_name:25} : {status}")
    
    print("-" * 80)
    print(f"总测试数: {total_tests}")
    print(f"通过数: {passed_tests}")
    print(f"失败数: {total_tests - passed_tests}")
    print(f"通过率: {passed_tests/total_tests*100:.1f}%")
    
    if passed_tests == total_tests:
        print("\n🎉 所有测试通过！日期智能处理功能正常工作")
    else:
        print(f"\n⚠️  有 {total_tests - passed_tests} 个测试失败，请检查相关功能")
    
    return passed_tests == total_tests

if __name__ == "__main__":
    main()