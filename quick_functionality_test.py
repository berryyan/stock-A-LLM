#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快速功能测试 - 验证所有核心功能是否正常
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_database_connections():
    """测试数据库连接"""
    print("🔍 测试数据库连接")
    print("=" * 50)
    
    try:
        from database.mysql_connector import MySQLConnector
        mysql = MySQLConnector()
        if mysql.test_connection():
            print("✅ MySQL连接正常")
        else:
            print("❌ MySQL连接失败")
            return False
    except Exception as e:
        print(f"❌ MySQL连接异常: {e}")
        return False
    
    try:
        from database.milvus_connector import MilvusConnector
        milvus = MilvusConnector()
        stats = milvus.get_collection_stats()
        if stats:
            print(f"✅ Milvus连接正常，文档数: {stats.get('row_count', 0)}")
        else:
            print("❌ Milvus连接失败")
            return False
    except Exception as e:
        print(f"❌ Milvus连接异常: {e}")
        return False
    
    return True

def test_sql_agent():
    """测试SQL Agent"""
    print("\n🔍 测试SQL Agent")
    print("=" * 50)
    
    try:
        from agents.sql_agent import SQLAgent
        agent = SQLAgent()
        
        # 简单查询测试 - 使用确实存在的日期
        result = agent.query("贵州茅台2025年6月20日的股价")
        
        if isinstance(result, dict) and result.get('success'):
            print("✅ SQL Agent查询成功")
            return True
        else:
            print(f"❌ SQL Agent查询失败: {result}")
            return False
            
    except Exception as e:
        print(f"❌ SQL Agent异常: {e}")
        return False

def test_rag_agent():
    """测试RAG Agent - 快速版本"""
    print("\n🔍 测试RAG Agent")
    print("=" * 50)
    
    try:
        from agents.rag_agent import RAGAgent
        agent = RAGAgent()
        
        # 简单查询测试，限制返回数量
        result = agent.query("茅台", top_k=2)
        
        if isinstance(result, dict) and result.get('success'):
            print("✅ RAG Agent查询成功")
            return True
        else:
            print(f"❌ RAG Agent查询失败: {result}")
            return False
            
    except Exception as e:
        print(f"❌ RAG Agent异常: {e}")
        return False

def test_financial_agent():
    """测试Financial Agent"""
    print("\n🔍 测试Financial Agent")
    print("=" * 50)
    
    try:
        from agents.financial_agent import FinancialAnalysisAgent
        agent = FinancialAnalysisAgent()
        
        # 快速数据获取测试
        financial_data = agent.get_financial_data("600519.SH", periods=1)
        
        if financial_data and len(financial_data) > 0:
            print("✅ Financial Agent数据获取成功")
            latest = financial_data[0]
            print(f"   最新数据期: {latest.end_date}")
            print(f"   营收: {latest.total_revenue/100000000:.2f}亿元")
            return True
        else:
            print("❌ Financial Agent数据获取失败")
            return False
            
    except Exception as e:
        print(f"❌ Financial Agent异常: {e}")
        return False

def test_hybrid_agent():
    """测试Hybrid Agent"""
    print("\n🔍 测试Hybrid Agent")
    print("=" * 50)
    
    try:
        from agents.hybrid_agent import HybridAgent
        agent = HybridAgent()
        
        # 测试财务分析路由
        result = agent.query("茅台财务健康度")
        
        if isinstance(result, dict):
            print(f"✅ Hybrid Agent路由成功")
            print(f"   查询类型: {result.get('query_type', 'unknown')}")
            print(f"   成功状态: {result.get('success', False)}")
            return True
        else:
            print(f"❌ Hybrid Agent路由失败: {result}")
            return False
            
    except Exception as e:
        print(f"❌ Hybrid Agent异常: {e}")
        return False

def test_imports():
    """测试关键模块导入"""
    print("\n🔍 测试模块导入")
    print("=" * 50)
    
    modules = [
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

def main():
    """主测试函数"""
    print("🚀 快速功能测试")
    print("=" * 80)
    
    results = {}
    
    # 测试模块导入
    results['imports'] = test_imports()
    
    # 测试数据库连接
    results['databases'] = test_database_connections()
    
    # 测试各个Agent（仅在数据库连接正常时）
    if results['databases']:
        results['sql_agent'] = test_sql_agent()
        results['rag_agent'] = test_rag_agent()
        results['financial_agent'] = test_financial_agent()
        results['hybrid_agent'] = test_hybrid_agent()
    else:
        print("\n⚠️ 数据库连接失败，跳过Agent测试")
        results['sql_agent'] = False
        results['rag_agent'] = False
        results['financial_agent'] = False
        results['hybrid_agent'] = False
    
    # 总结
    print("\n" + "=" * 80)
    print("📊 测试结果总结")
    print("=" * 80)
    
    for test_name, result in results.items():
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{test_name:20} : {status}")
    
    all_passed = all(results.values())
    
    if all_passed:
        print("\n🎉 所有核心功能测试通过！")
        print("系统已准备就绪，可以进行进一步测试或部署")
    else:
        print("\n⚠️ 部分功能测试失败")
        print("请检查失败的组件并修复问题")
    
    return all_passed

if __name__ == "__main__":
    main()