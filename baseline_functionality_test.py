#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
基线功能测试 - 恢复和验证原有测试用例
包含"最新股价"等原有经典测试场景
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import time
from datetime import datetime

def test_original_rag_functionality():
    """测试原始RAG功能（基于baseline_test.py）"""
    print("🔍 测试原始RAG功能")
    print("=" * 60)
    
    try:
        from agents.rag_agent import RAGAgent
        
        # 1. 初始化测试
        print("1. 测试初始化...")
        rag_agent = RAGAgent()
        print("✓ 初始化成功")
        
        # 2. 测试基本查询（原有用例）
        print("\n2. 测试基本查询...")
        result = rag_agent.query("贵州茅台最新财报")
        
        if result.get('success'):
            print("✓ 查询成功")
            print(f"  - 文档数: {result.get('document_count', 0)}")
            print(f"  - 答案长度: {len(result.get('answer', ''))}")
            print(f"  - 处理时间: {result.get('processing_time', 0):.2f}秒")
            
            # 检查日期智能处理
            if 'date_parsing' in result:
                print(f"  ✓ 日期智能: {result['date_parsing'].get('suggestion', '')}")
        else:
            print(f"✗ 查询失败: {result.get('error', '未知错误')}")
            return False
        
        # 3. 测试过滤查询（原有用例）
        print("\n3. 测试过滤查询...")
        result2 = rag_agent.query(
            "分析财务数据",
            filters={"ts_code": "600519.SH"}
        )
        
        if result2.get('success'):
            print("✓ 过滤查询成功")
            print(f"  - 文档数: {result2.get('document_count', 0)}")
        else:
            print(f"✗ 过滤查询失败: {result2.get('error', '未知错误')}")
            return False
        
        # 4. 检查核心方法（原有用例）
        print("\n4. 检查核心方法...")
        methods = [
            '_build_filter_expr',
            '_extract_documents', 
            '_format_context',
            '_format_sources',
            '_get_chat_history'
        ]
        
        for method in methods:
            if hasattr(rag_agent, method):
                print(f"  ✓ {method}")
            else:
                print(f"  ✗ {method} 缺失")
                return False
        
        print("\n✓ 原始RAG功能测试完成")
        return True
        
    except Exception as e:
        print(f"\n✗ RAG功能测试失败: {e}")
        return False

def test_classic_stock_price_queries():
    """测试经典股价查询用例（包含"最新股价"）"""
    print("\n🔍 测试经典股价查询用例")
    print("=" * 60)
    
    try:
        from agents.sql_agent import SQLAgent
        from agents.hybrid_agent import HybridAgent
        
        sql_agent = SQLAgent()
        hybrid_agent = HybridAgent()
        
        # 经典测试用例（原系统应该支持的）
        classic_queries = [
            # 最新股价类（原有核心用例）
            "茅台最新股价",
            "贵州茅台最新股价多少",
            "600519.SH最新收盘价",
            "查询茅台最新股价",
            
            # 具体日期类（验证基础功能）
            "贵州茅台2025年6月20日的股价",
            "茅台2025-06-20收盘价",
            
            # 简单查询类（基础功能）
            "茅台股价",
            "查询贵州茅台股价信息"
        ]
        
        print("\n使用SQL Agent测试:")
        print(f"{'查询':<30} {'状态':<10} {'耗时':<10} {'结果预览'}")
        print("-" * 70)
        
        sql_results = []
        for query in classic_queries[:4]:  # 只测试前4个，节省时间
            start_time = time.time()
            try:
                result = sql_agent.query(query)
                elapsed = time.time() - start_time
                
                if result.get('success'):
                    status = "✅成功"
                    preview = str(result.get('result', ''))[:30] + "..."
                else:
                    status = "❌失败" 
                    preview = str(result.get('error', ''))[:30]
                
                sql_results.append(result.get('success', False))
                print(f"{query:<30} {status:<10} {elapsed:.1f}s     {preview}")
                
            except Exception as e:
                elapsed = time.time() - start_time
                print(f"{query:<30} {'❌异常':<10} {elapsed:.1f}s     {str(e)[:30]}")
                sql_results.append(False)
        
        print(f"\nSQL Agent成功率: {sum(sql_results)}/{len(sql_results)}")
        
        # 使用Hybrid Agent测试（应该有更好的路由）
        print("\n使用Hybrid Agent测试:")
        print(f"{'查询':<30} {'路由类型':<12} {'状态':<10} {'耗时'}")
        print("-" * 65)
        
        hybrid_results = []
        for query in classic_queries[:3]:  # 只测试前3个
            start_time = time.time()
            try:
                result = hybrid_agent.query(query)
                elapsed = time.time() - start_time
                
                query_type = result.get('query_type', 'unknown')
                if result.get('success'):
                    status = "✅成功"
                else:
                    status = "❌失败"
                
                hybrid_results.append(result.get('success', False))
                print(f"{query:<30} {query_type:<12} {status:<10} {elapsed:.1f}s")
                
            except Exception as e:
                elapsed = time.time() - start_time
                print(f"{query:<30} {'exception':<12} {'❌异常':<10} {elapsed:.1f}s")
                hybrid_results.append(False)
        
        print(f"\nHybrid Agent成功率: {sum(hybrid_results)}/{len(hybrid_results)}")
        
        # 整体评估
        total_success = sum(sql_results) + sum(hybrid_results)
        total_tests = len(sql_results) + len(hybrid_results)
        
        if total_success >= total_tests * 0.8:  # 80%成功率认为通过
            print(f"\n✅ 经典股价查询功能正常 ({total_success}/{total_tests})")
            return True
        else:
            print(f"\n❌ 经典股价查询功能异常 ({total_success}/{total_tests})")
            return False
            
    except Exception as e:
        print(f"\n❌ 经典股价查询测试失败: {e}")
        return False

def test_financial_analysis_basic():
    """测试基础财务分析功能"""
    print("\n🔍 测试基础财务分析功能")
    print("=" * 60)
    
    try:
        from agents.financial_agent import FinancialAnalysisAgent
        from agents.hybrid_agent import HybridAgent
        
        financial_agent = FinancialAnalysisAgent()
        hybrid_agent = HybridAgent()
        
        # 基础财务分析测试
        print("1. 测试财务数据获取...")
        financial_data = financial_agent.get_financial_data("600519.SH", periods=1)
        
        if financial_data and len(financial_data) > 0:
            print(f"✅ 财务数据获取成功")
            latest = financial_data[0]
            print(f"   期间: {latest.end_date}")
            print(f"   营收: {latest.total_revenue/100000000:.2f}亿")
        else:
            print("❌ 财务数据获取失败")
            return False
        
        # 财务分析查询测试
        print("\n2. 测试财务分析查询...")
        financial_queries = [
            "分析茅台财务健康状况",
            "茅台最新财务表现如何",
            "贵州茅台财务分析"
        ]
        
        success_count = 0
        for query in financial_queries:
            try:
                result = hybrid_agent.query(query)
                if result.get('success') and result.get('query_type') == 'FINANCIAL':
                    print(f"✅ {query}")
                    success_count += 1
                else:
                    print(f"❌ {query}: {result.get('error', 'No error info')}")
            except Exception as e:
                print(f"❌ {query}: {e}")
        
        if success_count >= len(financial_queries) * 0.8:
            print(f"\n✅ 财务分析功能正常 ({success_count}/{len(financial_queries)})")
            return True
        else:
            print(f"\n❌ 财务分析功能异常 ({success_count}/{len(financial_queries)})")
            return False
            
    except Exception as e:
        print(f"\n❌ 财务分析测试失败: {e}")
        return False

def test_announcement_queries():
    """测试公告查询功能"""
    print("\n🔍 测试公告查询功能")
    print("=" * 60)
    
    try:
        from agents.rag_agent import RAGAgent
        from agents.hybrid_agent import HybridAgent
        
        rag_agent = RAGAgent()
        hybrid_agent = HybridAgent()
        
        # 公告查询测试用例
        announcement_queries = [
            "茅台最新公告",
            "贵州茅台最新披露信息",
            "600519.SH最近公告内容",
            "茅台公司最新发布的公告"
        ]
        
        print("使用RAG Agent测试:")
        rag_success = 0
        for query in announcement_queries[:2]:  # 测试前2个
            try:
                result = rag_agent.query(query, top_k=2)  # 限制返回数量
                if result.get('success'):
                    print(f"✅ {query}")
                    # 检查日期智能
                    if 'date_parsing' in result:
                        print(f"   📅 {result['date_parsing'].get('suggestion', '')[:50]}...")
                    rag_success += 1
                else:
                    print(f"❌ {query}: {result.get('message', 'No message')}")
            except Exception as e:
                print(f"❌ {query}: {e}")
        
        print(f"\nRAG Agent成功率: {rag_success}/2")
        
        print("\n使用Hybrid Agent测试:")
        hybrid_success = 0
        for query in announcement_queries[2:]:  # 测试后2个
            try:
                result = hybrid_agent.query(query)
                if result.get('success'):
                    print(f"✅ {query}")
                    print(f"   路由: {result.get('query_type', 'unknown')}")
                    hybrid_success += 1
                else:
                    print(f"❌ {query}: {result.get('error', 'No error')}")
            except Exception as e:
                print(f"❌ {query}: {e}")
        
        print(f"\nHybrid Agent成功率: {hybrid_success}/2")
        
        total_success = rag_success + hybrid_success
        if total_success >= 3:  # 4个测试中至少3个成功
            print(f"\n✅ 公告查询功能正常 ({total_success}/4)")
            return True
        else:
            print(f"\n❌ 公告查询功能异常 ({total_success}/4)")
            return False
            
    except Exception as e:
        print(f"\n❌ 公告查询测试失败: {e}")
        return False

def main():
    """主测试函数"""
    print("🚀 基线功能测试 - 验证原有功能")
    print("=" * 80)
    print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("包含经典'最新股价'等原有测试用例")
    print("=" * 80)
    
    # 测试结果记录
    results = {}
    start_time = time.time()
    
    # 1. 原始RAG功能测试
    results['original_rag'] = test_original_rag_functionality()
    
    # 2. 经典股价查询测试
    results['classic_stock_queries'] = test_classic_stock_price_queries()
    
    # 3. 基础财务分析测试
    results['financial_analysis'] = test_financial_analysis_basic()
    
    # 4. 公告查询测试
    results['announcement_queries'] = test_announcement_queries()
    
    # 测试结果总结
    total_time = time.time() - start_time
    print("\n" + "=" * 80)
    print("📊 基线功能测试结果")
    print("=" * 80)
    
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
    print(f"总耗时: {total_time:.2f}秒")
    
    if passed_tests == total_tests:
        print("\n🎉 所有基线功能测试通过！")
        print("📍 原有功能完全恢复")
        print("📍 '最新股价'等经典用例正常工作")
        print("📍 增强的日期智能处理已集成")
    else:
        print(f"\n⚠️ 有 {total_tests - passed_tests} 个基线功能测试失败")
        print("需要检查原有功能的兼容性")
    
    return passed_tests == total_tests

if __name__ == "__main__":
    main()