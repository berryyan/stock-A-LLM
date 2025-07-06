#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快速冒烟测试 - 每个Agent一个核心功能
"""
import sys
import os
import time

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.sql_agent_modular import SQLAgentModular
from agents.rag_agent_modular import RAGAgentModular
from agents.financial_agent_modular import FinancialAgentModular
from agents.money_flow_agent_modular import MoneyFlowAgentModular
from agents.hybrid_agent_modular import HybridAgentModular


def test_agent(agent_name: str, agent_class, query: str):
    """测试单个Agent"""
    print(f"\n{'='*60}")
    print(f"测试 {agent_name}")
    print(f"查询: {query}")
    print('-'*60)
    
    try:
        start = time.time()
        agent = agent_class()
        result = agent.query(query)
        elapsed = time.time() - start
        
        if result.get("success", False):
            print(f"✅ 成功 (耗时: {elapsed:.2f}秒)")
            # 打印部分结果
            if "answer" in result:
                answer = result["answer"][:200] + "..." if len(result.get("answer", "")) > 200 else result.get("answer", "")
                print(f"答案: {answer}")
            elif "result" in result:
                res = str(result["result"])[:200] + "..." if len(str(result.get("result", ""))) > 200 else str(result.get("result", ""))
                print(f"结果: {res}")
        else:
            print(f"❌ 失败 (耗时: {elapsed:.2f}秒)")
            print(f"错误: {result.get('error', '未知错误')}")
            
        return result.get("success", False)
        
    except Exception as e:
        print(f"❌ 异常: {str(e)}")
        return False


def main():
    """运行快速测试"""
    print("模块化Agent快速冒烟测试")
    print("="*60)
    
    tests = [
        ("SQL Agent", SQLAgentModular, "贵州茅台的最新股价"),
        ("RAG Agent", RAGAgentModular, "贵州茅台的发展战略"),
        ("Financial Agent", FinancialAgentModular, "分析贵州茅台的财务健康度"),
        ("Money Flow Agent", MoneyFlowAgentModular, "贵州茅台的主力资金"),
        ("Hybrid Agent", HybridAgentModular, "贵州茅台的股价和主要业务")
    ]
    
    results = []
    for name, agent_class, query in tests:
        success = test_agent(name, agent_class, query)
        results.append((name, success))
    
    # 打印摘要
    print(f"\n{'='*60}")
    print("测试摘要")
    print('-'*60)
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for name, success in results:
        status = "✅ 通过" if success else "❌ 失败"
        print(f"{name:<20} {status}")
    
    print('-'*60)
    print(f"总计: {passed}/{total} ({passed/total*100:.0f}%)")
    
    if passed == total:
        print("\n🎉 所有测试通过！模块化系统运行正常。")
    else:
        print(f"\n⚠️  有 {total-passed} 个测试失败，请检查相关Agent。")


if __name__ == "__main__":
    main()