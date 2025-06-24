#!/usr/bin/env python
"""快速功能测试脚本"""
import time
from datetime import datetime

def test_sql_agent():
    """测试SQL Agent"""
    print("\n=== 测试SQL Agent ===")
    try:
        from agents.sql_agent import SQLAgent
        agent = SQLAgent()
        result = agent.query("贵州茅台最新股价")
        print(f"✓ SQL Agent: {result.get('success', False)}")
        if not result.get('success'):
            print(f"  错误: {result.get('error', '未知错误')}")
        return result.get('success', False)
    except Exception as e:
        print(f"✗ SQL Agent错误: {e}")
        return False

def test_rag_agent():
    """测试RAG Agent"""
    print("\n=== 测试RAG Agent ===")
    try:
        from agents.rag_agent import RAGAgent
        agent = RAGAgent()
        result = agent.query("茅台公告")
        print(f"✓ RAG Agent: {result.get('success', False)}")
        if not result.get('success'):
            print(f"  错误: {result.get('error', '未知错误')}")
        return result.get('success', False)
    except Exception as e:
        print(f"✗ RAG Agent错误: {e}")
        return False

def test_money_flow_agent():
    """测试Money Flow Agent"""
    print("\n=== 测试Money Flow Agent ===")
    try:
        from agents.money_flow_agent import MoneyFlowAgent
        agent = MoneyFlowAgent()
        result = agent.query("茅台资金流向")
        print(f"✓ Money Flow Agent: {result.get('success', False)}")
        if not result.get('success'):
            print(f"  错误: {result.get('error', '未知错误')}")
        return result.get('success', False)
    except Exception as e:
        print(f"✗ Money Flow Agent错误: {e}")
        return False

def test_financial_agent():
    """测试Financial Agent"""
    print("\n=== 测试Financial Agent ===")
    try:
        from agents.financial_agent import FinancialAnalysisAgent
        agent = FinancialAnalysisAgent()
        result = agent.query("分析茅台财务健康度")
        print(f"✓ Financial Agent: {result.get('success', False)}")
        if not result.get('success'):
            print(f"  错误: {result.get('error', '未知错误')}")
        return result.get('success', False)
    except Exception as e:
        print(f"✗ Financial Agent错误: {e}")
        return False

def main():
    """主测试函数"""
    print("=== 股票分析系统快速测试 ===")
    print(f"开始时间: {datetime.now()}")
    
    results = {
        'SQL Agent': test_sql_agent(),
        'RAG Agent': test_rag_agent(),
        'Money Flow Agent': test_money_flow_agent(),
        'Financial Agent': test_financial_agent()
    }
    
    print("\n=== 测试结果汇总 ===")
    passed = sum(results.values())
    total = len(results)
    
    for name, success in results.items():
        status = "✓ 通过" if success else "✗ 失败"
        print(f"{name}: {status}")
    
    print(f"\n总计: {passed}/{total} 通过")
    print(f"结束时间: {datetime.now()}")
    
    return passed == total

if __name__ == "__main__":
    main()