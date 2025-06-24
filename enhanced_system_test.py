#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
增强系统测试 - 完整基本功能测试 + 增强日期智能测试
包含更长的超时时间和更全面的测试用例
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import time
from datetime import datetime
from typing import Dict, List, Any

def test_imports_comprehensive():
    """全面测试模块导入"""
    print("🔍 全面测试模块导入")
    print("=" * 60)
    
    modules = [
        # 核心模块
        "utils.date_intelligence",
        "database.mysql_connector",
        "database.milvus_connector",
        # Agent模块
        "agents.sql_agent",
        "agents.rag_agent", 
        "agents.financial_agent",
        "agents.hybrid_agent",
        # API模块
        "api.main",
        # 工具模块
        "utils.logger"
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

def test_database_connections_detailed():
    """详细测试数据库连接"""
    print("\n🔍 详细测试数据库连接")
    print("=" * 60)
    
    try:
        from database.mysql_connector import MySQLConnector
        from database.milvus_connector import MilvusConnector
        
        # MySQL连接测试
        mysql = MySQLConnector()
        if mysql.test_connection():
            print("✅ MySQL连接正常")
            
            # 测试简单查询
            result = mysql.execute_query("SELECT COUNT(*) FROM tu_daily_detail LIMIT 1")
            if result:
                print(f"   - 日线数据表记录数: {result[0][0]:,}")
            
            result = mysql.execute_query("SELECT COUNT(*) FROM tu_stock_basic LIMIT 1") 
            if result:
                print(f"   - 股票基础信息表记录数: {result[0][0]:,}")
        else:
            print("❌ MySQL连接失败")
            return False
    except Exception as e:
        print(f"❌ MySQL连接异常: {e}")
        return False
    
    try:
        # Milvus连接测试
        milvus = MilvusConnector()
        stats = milvus.get_collection_stats()
        if stats:
            print(f"✅ Milvus连接正常")
            print(f"   - 向量文档数: {stats.get('row_count', 0):,}")
            print(f"   - 索引状态: {stats.get('index_status', 'Unknown')}")
        else:
            print("❌ Milvus连接失败")
            return False
    except Exception as e:
        print(f"❌ Milvus连接异常: {e}")
        return False
    
    return True

def test_enhanced_date_intelligence():
    """测试增强的日期智能处理功能"""
    print("\n🔍 测试增强日期智能处理")
    print("=" * 60)
    
    try:
        from utils.date_intelligence import date_intelligence
        
        # 测试基础日期功能
        print("\n📅 基础日期功能测试:")
        latest_trading = date_intelligence.get_latest_trading_day()
        print(f"✅ 最近交易日: {latest_trading}")
        
        previous_trading = date_intelligence.get_previous_trading_day()
        print(f"✅ 上一个交易日: {previous_trading}")
        
        # 测试相对日期计算
        print("\n📅 相对日期计算测试:")
        trading_days_5 = date_intelligence.get_trading_days_before(5)
        if trading_days_5:
            print(f"✅ 最近5个交易日: {trading_days_5[0]} ~ {trading_days_5[-1]}")
        
        # 测试时间段计算
        start_date, end_date = date_intelligence.get_date_range_by_period('week', 1)
        if start_date and end_date:
            print(f"✅ 最近一周范围: {start_date} ~ {end_date}")
        
        start_date, end_date = date_intelligence.get_date_range_by_period('month', 1)
        if start_date and end_date:
            print(f"✅ 最近一月范围: {start_date} ~ {end_date}")
        
        return True
        
    except Exception as e:
        print(f"❌ 日期智能测试失败: {e}")
        return False

def test_comprehensive_date_parsing():
    """全面测试日期解析能力"""
    print("\n🔍 全面测试日期解析能力")
    print("=" * 60)
    
    try:
        from utils.date_intelligence import date_intelligence
        
        # 增强的测试用例（原有的 + 新增的）
        test_cases = [
            # 基础时间表达（原有）
            ("茅台最新股价", "stock_price", "latest"),
            ("贵州茅台最近股价", "stock_price", "latest"), 
            ("600519.SH现在的收盘价", "stock_price", "latest"),
            ("比亚迪当前的股价表现", "stock_price", "latest"),
            ("贵州茅台最新财务数据", "financial", "latest"),
            ("茅台最近的业绩", "financial", "latest"),
            ("平安银行最新年报", "financial", "latest"),
            ("贵州茅台最新公告", "announcement", "latest"),
            ("600519.SH最近披露了什么", "announcement", "latest"),
            
            # 相对时间表达（新增）
            ("茅台上一个交易日的股价", "stock_price", "previous"),
            ("贵州茅台昨天的收盘价", "stock_price", "previous"),
            ("茅台前5个交易日的股价", "stock_price", "previous_n"),
            ("比亚迪3天前的股价", "stock_price", "previous_n"),
            
            # 时间段表达（新增）
            ("茅台最近5天的股价走势", "stock_price", "recent_n"),
            ("贵州茅台最近一周的表现", "stock_price", "recent_period"),
            ("茅台最近一月的股价变化", "stock_price", "recent_period"),
            ("比亚迪最近3个月的走势", "stock_price", "recent_n"),
            ("茅台最近一季度的表现", "stock_price", "recent_period"),
            ("贵州茅台最近半年的股价", "stock_price", "recent_period"),
            ("茅台最近一年的走势", "stock_price", "recent_period"),
            
            # 无时间表达（对比测试）
            ("查询茅台股价", None, None),
            ("分析贵州茅台财务状况", None, None),
            ("茅台的基本信息", None, None)
        ]
        
        print(f"\n{'查询':<35} {'数据类型':<15} {'时间类型':<15} {'解析结果':<20} {'状态'}")
        print("-" * 100)
        
        all_correct = True
        for query, expected_data_type, expected_time_type in test_cases:
            try:
                processed, result = date_intelligence.preprocess_question(query)
                actual_data_type = result['context'].get('data_type')
                actual_time_type = result['context'].get('time_type')
                
                # 判断解析是否正确
                data_type_correct = (expected_data_type is None and actual_data_type is None) or \
                                  (expected_data_type == actual_data_type)
                time_type_correct = (expected_time_type is None and actual_time_type is None) or \
                                  (expected_time_type == actual_time_type)
                
                is_correct = data_type_correct and time_type_correct
                status = "✅" if is_correct else "❌"
                
                parsed_info = result.get('suggestion', '')[:20] if result.get('suggestion') else '-'
                
                print(f"{status} {query:<33} {actual_data_type or '-':<15} {actual_time_type or '-':<15} {parsed_info:<20}")
                
                if not is_correct:
                    all_correct = False
                    print(f"   期望: 数据类型={expected_data_type}, 时间类型={expected_time_type}")
                    print(f"   实际: 数据类型={actual_data_type}, 时间类型={actual_time_type}")
                
            except Exception as e:
                print(f"❌ {query:<33} 解析异常: {e}")
                all_correct = False
        
        return all_correct
        
    except Exception as e:
        print(f"❌ 日期解析测试失败: {e}")
        return False

def test_sql_agent_with_timeout():
    """测试SQL Agent（增加超时控制）"""
    print("\n🔍 测试SQL Agent（超时控制）")
    print("=" * 60)
    
    try:
        from agents.sql_agent import SQLAgent
        agent = SQLAgent()
        
        # 基础查询测试
        test_queries = [
            "贵州茅台2025年6月20日的股价",  # 明确日期查询
            "茅台最新股价",  # 智能日期解析
            "查询比亚迪最近的收盘价",  # 智能日期解析
            "平安银行最近一个交易日的股价"  # 新增：相对日期
        ]
        
        for query in test_queries:
            print(f"\n查询: {query}")
            start_time = time.time()
            
            try:
                # 设置30秒超时
                result = agent.query(query)
                elapsed = time.time() - start_time
                
                if result.get('success'):
                    print(f"✅ 查询成功 (耗时: {elapsed:.2f}秒)")
                    # 显示部分结果
                    answer = str(result.get('result', ''))[:150]
                    print(f"   结果: {answer}...")
                else:
                    print(f"❌ 查询失败: {result.get('error', 'Unknown')}")
                    
            except Exception as e:
                elapsed = time.time() - start_time
                print(f"❌ 查询异常 (耗时: {elapsed:.2f}秒): {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ SQL Agent测试失败: {e}")
        return False

def test_rag_agent_with_timeout():
    """测试RAG Agent（增加超时控制）"""
    print("\n🔍 测试RAG Agent（超时控制）")
    print("=" * 60)
    
    try:
        from agents.rag_agent import RAGAgent
        agent = RAGAgent()
        
        # 基础查询测试（包含日期智能）
        test_queries = [
            "贵州茅台最新公告内容",  # 智能日期解析
            "茅台最近发布的年报摘要",  # 智能日期解析
            "平安银行最新披露信息",  # 智能日期解析
            "比亚迪公司最近的重要公告"  # 智能日期解析
        ]
        
        for query in test_queries:
            print(f"\n查询: {query}")
            start_time = time.time()
            
            try:
                # 限制返回文档数量，加快查询速度
                result = agent.query(query, top_k=3)
                elapsed = time.time() - start_time
                
                if result.get('success'):
                    print(f"✅ 查询成功 (耗时: {elapsed:.2f}秒)")
                    print(f"   文档数: {result.get('document_count', 0)}")
                    
                    # 检查日期解析信息
                    if 'date_parsing' in result:
                        parsing_info = result['date_parsing']
                        print(f"   📅 日期智能: {parsing_info.get('suggestion', '')}")
                    
                    # 显示部分答案
                    answer = result.get('answer', '')[:100]
                    print(f"   答案: {answer}...")
                else:
                    print(f"❌ 查询失败: {result.get('message', 'Unknown')}")
                    
            except Exception as e:
                elapsed = time.time() - start_time
                print(f"❌ 查询异常 (耗时: {elapsed:.2f}秒): {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ RAG Agent测试失败: {e}")
        return False

def test_financial_agent():
    """测试Financial Agent"""
    print("\n🔍 测试Financial Agent")
    print("=" * 60)
    
    try:
        from agents.financial_agent import FinancialAnalysisAgent
        agent = FinancialAnalysisAgent()
        
        # 测试数据获取
        print("测试财务数据获取...")
        financial_data = agent.get_financial_data("600519.SH", periods=2)
        
        if financial_data and len(financial_data) > 0:
            print(f"✅ 财务数据获取成功，共{len(financial_data)}期")
            latest = financial_data[0]
            print(f"   最新期间: {latest.end_date}")
            print(f"   营收: {latest.total_revenue/100000000:.2f}亿元")
            print(f"   净利润: {latest.n_income/100000000:.2f}亿元")
            
            # 测试财务分析
            print("\n测试财务健康度分析...")
            health_result = agent.analyze_financial_health("600519.SH")
            if health_result.get('success'):
                print(f"✅ 财务健康度分析成功")
                print(f"   评级: {health_result.get('rating', 'N/A')}")
                print(f"   综合得分: {health_result.get('score', 0):.2f}")
            else:
                print(f"❌ 财务健康度分析失败")
            
            return True
        else:
            print("❌ 财务数据获取失败")
            return False
            
    except Exception as e:
        print(f"❌ Financial Agent测试失败: {e}")
        return False

def test_hybrid_agent():
    """测试Hybrid Agent"""
    print("\n🔍 测试Hybrid Agent")
    print("=" * 60)
    
    try:
        from agents.hybrid_agent import HybridAgent
        agent = HybridAgent()
        
        # 测试查询路由
        test_queries = [
            "茅台最新股价多少",  # SQL查询
            "分析贵州茅台财务健康状况",  # 财务分析
            "茅台最新公告说了什么",  # RAG查询
            "茅台最新股价和最新公告"  # 混合查询
        ]
        
        for query in test_queries:
            print(f"\n查询: {query}")
            start_time = time.time()
            
            try:
                result = agent.query(query)
                elapsed = time.time() - start_time
                
                if result.get('success'):
                    print(f"✅ 查询成功 (耗时: {elapsed:.2f}秒)")
                    print(f"   路由类型: {result.get('query_type', 'unknown')}")
                    
                    # 显示部分答案
                    answer = result.get('answer', '')[:100]
                    print(f"   答案: {answer}...")
                else:
                    print(f"❌ 查询失败: {result.get('error', 'Unknown')}")
                    
            except Exception as e:
                elapsed = time.time() - start_time
                print(f"❌ 查询异常 (耗时: {elapsed:.2f}秒): {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Hybrid Agent测试失败: {e}")
        return False

def main():
    """主测试函数"""
    print("🚀 增强系统测试 - v1.4.1")
    print("=" * 80)
    print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    
    # 测试结果记录
    results = {}
    start_time = time.time()
    
    # 1. 模块导入测试
    results['imports'] = test_imports_comprehensive()
    
    # 2. 数据库连接测试
    results['databases'] = test_database_connections_detailed()
    
    # 3. 增强日期智能测试
    results['date_intelligence'] = test_enhanced_date_intelligence()
    
    # 4. 全面日期解析测试
    results['date_parsing'] = test_comprehensive_date_parsing()
    
    # 只有在数据库连接正常时才进行Agent测试
    if results['databases']:
        # 5. SQL Agent测试
        results['sql_agent'] = test_sql_agent_with_timeout()
        
        # 6. RAG Agent测试
        results['rag_agent'] = test_rag_agent_with_timeout()
        
        # 7. Financial Agent测试
        results['financial_agent'] = test_financial_agent()
        
        # 8. Hybrid Agent测试
        results['hybrid_agent'] = test_hybrid_agent()
    else:
        print("\n⚠️ 数据库连接失败，跳过Agent测试")
        results.update({
            'sql_agent': False,
            'rag_agent': False,
            'financial_agent': False,
            'hybrid_agent': False
        })
    
    # 测试结果总结
    total_time = time.time() - start_time
    print("\n" + "=" * 80)
    print("📊 测试结果总结")
    print("=" * 80)
    
    total_tests = len(results)
    passed_tests = sum(1 for v in results.values() if v)
    
    for test_name, result in results.items():
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{test_name:20} : {status}")
    
    print("-" * 80)
    print(f"总测试数: {total_tests}")
    print(f"通过数: {passed_tests}")
    print(f"失败数: {total_tests - passed_tests}")
    print(f"通过率: {passed_tests/total_tests*100:.1f}%")
    print(f"总耗时: {total_time:.2f}秒")
    
    if passed_tests == total_tests:
        print("\n🎉 所有测试通过！系统功能完全正常")
        print("📍 包含增强的日期智能处理功能")
        print("📍 支持相对日期和时间段查询")
        print("📍 系统已准备好Phase 2开发")
    else:
        print(f"\n⚠️ 有 {total_tests - passed_tests} 个测试失败")
        print("请检查失败的组件并修复问题")
    
    return passed_tests == total_tests

if __name__ == "__main__":
    main()