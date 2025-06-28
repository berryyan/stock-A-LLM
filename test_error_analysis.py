#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
分析comprehensive_test中的错误类型
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_rag_queries():
    """测试RAG查询是否正常"""
    print("="*60)
    print("1. 测试RAG查询")
    print("="*60)
    
    try:
        from agents.rag_agent import RAGAgent
        agent = RAGAgent()
        
        # 测试查询
        test_queries = [
            "贵州茅台最新公告说了什么",
            "600519.SH最新披露的信息"
        ]
        
        for query in test_queries:
            print(f"\n查询: {query}")
            result = agent.query(query, top_k=3)
            
            if result.get('success'):
                print(f"✅ 成功，文档数: {result.get('document_count', 0)}")
                if result.get('document_count', 0) == 0:
                    print("   ⚠️ 没有找到相关文档（这可能是正常的）")
            else:
                print(f"❌ 失败: {result.get('message', result.get('error', 'Unknown'))}")
                
    except Exception as e:
        print(f"❌ RAG测试异常: {e}")
        import traceback
        traceback.print_exc()


def test_money_flow_queries():
    """测试资金流向查询"""
    print("\n\n" + "="*60)
    print("2. 测试资金流向查询")
    print("="*60)
    
    try:
        from agents.money_flow_agent import MoneyFlowAgent
        agent = MoneyFlowAgent()
        
        # 测试一个简单查询
        query = "茅台最近30天的资金流向"
        print(f"\n查询: {query}")
        
        result = agent.analyze(query)
        
        if result['success']:
            print("✅ 查询成功")
        else:
            print(f"❌ 查询失败: {result.get('error', 'Unknown')}")
            
    except Exception as e:
        print(f"❌ MoneyFlow测试异常: {e}")
        import traceback
        traceback.print_exc()


def test_financial_queries():
    """测试财务分析查询"""
    print("\n\n" + "="*60)
    print("3. 测试财务分析查询")
    print("="*60)
    
    try:
        from agents.financial_agent import FinancialAnalysisAgent
        agent = FinancialAnalysisAgent()
        
        query = "分析贵州茅台的财务健康度"
        print(f"\n查询: {query}")
        
        result = agent.analyze_financial_health("600519.SH")
        
        if result['success']:
            print("✅ 查询成功")
            print(f"   健康度评分: {result.get('health_score', 'N/A')}")
        else:
            print(f"❌ 查询失败: {result.get('error', 'Unknown')}")
            
    except Exception as e:
        print(f"❌ Financial测试异常: {e}")
        import traceback
        traceback.print_exc()


def test_hybrid_complex():
    """测试复杂查询"""
    print("\n\n" + "="*60)
    print("4. 测试复杂查询")
    print("="*60)
    
    try:
        from agents.hybrid_agent import HybridAgent
        agent = HybridAgent()
        
        # 测试一个可能需要多个agent的查询
        query = "茅台最新股价和最新公告"
        print(f"\n查询: {query}")
        
        result = agent.query(query)
        
        if result.get('success'):
            print(f"✅ 查询成功，查询类型: {result.get('query_type', 'unknown')}")
        else:
            print(f"❌ 查询失败: {result.get('error', 'Unknown')}")
            
    except Exception as e:
        print(f"❌ Hybrid测试异常: {e}")
        import traceback
        traceback.print_exc()


def check_configurations():
    """检查配置问题"""
    print("\n\n" + "="*60)
    print("5. 检查配置")
    print("="*60)
    
    # 检查MoneyFlowAgent的配置
    try:
        from agents.money_flow_agent import MoneyFlowAgent
        print("\n检查MoneyFlowAgent配置...")
        
        # 检查LLM配置
        agent = MoneyFlowAgent()
        print(f"LLM类型: {type(agent.llm)}")
        
        # 检查是否使用了正确的API配置
        if hasattr(agent.llm, 'openai_api_key'):
            print(f"API Key设置: {'已设置' if agent.llm.openai_api_key else '未设置'}")
        
    except Exception as e:
        print(f"配置检查失败: {e}")


def main():
    """主测试函数"""
    print("开始分析comprehensive_test中的错误...\n")
    
    # 逐个测试各个组件
    test_rag_queries()
    test_money_flow_queries()
    test_financial_queries()
    test_hybrid_complex()
    check_configurations()
    
    print("\n\n错误分析完成！")


if __name__ == "__main__":
    main()