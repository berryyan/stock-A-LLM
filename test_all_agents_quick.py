#!/usr/bin/env python3
"""快速测试所有模块化Agent的基本功能"""

import sys
sys.path.append('.')
import time

# 导入所有模块化Agent
from agents.sql_agent_modular import SQLAgentModular
from agents.rag_agent_modular import RAGAgentModular
from agents.financial_agent_modular import FinancialAgentModular
from agents.money_flow_agent_modular import MoneyFlowAgentModular
from agents.hybrid_agent_modular import HybridAgentModular


def test_agent(agent_name, agent_instance, test_queries):
    """测试单个Agent"""
    print(f"\n{'='*60}")
    print(f"测试 {agent_name}")
    print('='*60)
    
    passed = 0
    failed = 0
    
    for query, expected_type in test_queries:
        print(f"\n查询: {query}")
        print(f"期望: {expected_type}")
        
        try:
            start = time.time()
            result = agent_instance.query(query)
            elapsed = time.time() - start
            
            if result.get('success'):
                print(f"✅ 成功 ({elapsed:.2f}秒)")
                print(f"结果预览: {str(result.get('result', ''))[:100]}...")
                passed += 1
            else:
                print(f"❌ 失败: {result.get('error', '未知错误')}")
                failed += 1
                
        except Exception as e:
            print(f"❌ 异常: {str(e)}")
            failed += 1
    
    print(f"\n{agent_name} 测试结果: {passed}/{passed+failed} 通过")
    return passed, failed


def main():
    """运行所有Agent的快速测试"""
    print("模块化Agent快速功能测试")
    print("="*80)
    
    total_passed = 0
    total_failed = 0
    
    # 1. SQL Agent测试
    sql_agent = SQLAgentModular()
    sql_queries = [
        ("贵州茅台最新股价", "股价查询"),
        ("涨幅前10", "涨幅排名"),
        ("银行板块的主力资金", "板块资金"),
    ]
    p, f = test_agent("SQLAgentModular", sql_agent, sql_queries)
    total_passed += p
    total_failed += f
    
    # 2. RAG Agent测试
    rag_agent = RAGAgentModular()
    rag_queries = [
        ("贵州茅台的主营业务", "业务查询"),
        ("茅台最新公告", "公告查询"),
    ]
    p, f = test_agent("RAGAgentModular", rag_agent, rag_queries)
    total_passed += p
    total_failed += f
    
    # 3. Financial Agent测试
    financial_agent = FinancialAgentModular()
    financial_queries = [
        ("分析贵州茅台的财务健康度", "财务健康度"),
        ("贵州茅台的杜邦分析", "杜邦分析"),
    ]
    p, f = test_agent("FinancialAgentModular", financial_agent, financial_queries)
    total_passed += p
    total_failed += f
    
    # 4. Money Flow Agent测试
    money_flow_agent = MoneyFlowAgentModular()
    money_flow_queries = [
        ("分析贵州茅台的资金流向", "资金流向分析"),
        ("贵州茅台的超大单资金", "超大单分析"),
    ]
    p, f = test_agent("MoneyFlowAgentModular", money_flow_agent, money_flow_queries)
    total_passed += p
    total_failed += f
    
    # 5. Hybrid Agent测试
    hybrid_agent = HybridAgentModular()
    hybrid_queries = [
        ("贵州茅台的股价和主营业务", "混合查询"),
        ("分析平安银行", "智能路由"),
    ]
    p, f = test_agent("HybridAgentModular", hybrid_agent, hybrid_queries)
    total_passed += p
    total_failed += f
    
    # 总结
    print(f"\n{'='*80}")
    print(f"总体测试结果: {total_passed}/{total_passed+total_failed} 通过")
    print(f"通过率: {total_passed/(total_passed+total_failed)*100:.1f}%")
    
    if total_failed == 0:
        print("\n✅ 所有模块化Agent基本功能正常！")
    else:
        print(f"\n⚠️ 有 {total_failed} 个测试失败，需要进一步调试")


if __name__ == "__main__":
    main()