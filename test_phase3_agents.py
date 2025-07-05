#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Phase 3 模块化Agent功能测试
测试所有模块化Agent的基本功能
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import asyncio
from datetime import datetime
import json


def test_rag_agent():
    """测试RAG Agent模块化版本"""
    print("\n=== 测试 RAG Agent ===")
    try:
        from agents.rag_agent_modular import RAGAgentModular
        
        agent = RAGAgentModular()
        
        # 测试用例
        test_cases = [
            "贵州茅台最新公告内容",
            "平安银行的年报提到了什么风险",
            "宁德时代的发展战略"
        ]
        
        for query in test_cases:
            print(f"\n查询: {query}")
            start_time = datetime.now()
            try:
                result = agent.query(query)
                end_time = datetime.now()
                elapsed = (end_time - start_time).total_seconds()
                
                if result.get("success"):
                    print(f"✓ 成功 (耗时: {elapsed:.2f}秒)")
                    # 显示部分结果
                    answer = result.get("answer", "")
                    if answer:
                        preview = answer[:200] + "..." if len(answer) > 200 else answer
                        print(f"  结果预览: {preview}")
                else:
                    print(f"✗ 失败: {result.get('error', '未知错误')}")
            except Exception as e:
                print(f"✗ 异常: {str(e)}")
                
    except Exception as e:
        print(f"✗ RAG Agent初始化失败: {str(e)}")


def test_financial_agent():
    """测试Financial Agent模块化版本"""
    print("\n=== 测试 Financial Agent ===")
    try:
        from agents.financial_agent_modular import FinancialAgentModular
        
        agent = FinancialAgentModular()
        
        # 测试用例
        test_cases = [
            "分析贵州茅台的财务健康度",
            "比亚迪的杜邦分析",
            "平安银行的现金流质量如何"
        ]
        
        for query in test_cases:
            print(f"\n查询: {query}")
            start_time = datetime.now()
            try:
                result = agent.analyze(query)
                end_time = datetime.now()
                elapsed = (end_time - start_time).total_seconds()
                
                if result.get("success"):
                    print(f"✓ 成功 (耗时: {elapsed:.2f}秒)")
                    # 显示分析类型
                    result_data = result.get("result", {})
                    if isinstance(result_data, dict):
                        analysis_type = result_data.get("analysis_type", "未知")
                        print(f"  分析类型: {analysis_type}")
                else:
                    print(f"✗ 失败: {result.get('error', '未知错误')}")
            except Exception as e:
                print(f"✗ 异常: {str(e)}")
                
    except Exception as e:
        print(f"✗ Financial Agent初始化失败: {str(e)}")


def test_money_flow_agent():
    """测试Money Flow Agent模块化版本"""
    print("\n=== 测试 Money Flow Agent ===")
    try:
        from agents.money_flow_agent_modular import MoneyFlowAgentModular
        
        agent = MoneyFlowAgentModular()
        
        # 测试用例
        test_cases = [
            "分析贵州茅台的资金流向",
            "宁德时代的主力资金情况",
            "银行板块的资金流向如何"
        ]
        
        for query in test_cases:
            print(f"\n查询: {query}")
            start_time = datetime.now()
            try:
                result = agent.analyze(query)
                end_time = datetime.now()
                elapsed = (end_time - start_time).total_seconds()
                
                if result.get("success"):
                    print(f"✓ 成功 (耗时: {elapsed:.2f}秒)")
                    # 显示部分分析结果
                    analysis = result.get("analysis", "")
                    if analysis:
                        preview = analysis[:200] + "..." if len(analysis) > 200 else analysis
                        print(f"  分析预览: {preview}")
                else:
                    print(f"✗ 失败: {result.get('error', '未知错误')}")
            except Exception as e:
                print(f"✗ 异常: {str(e)}")
                
    except Exception as e:
        print(f"✗ Money Flow Agent初始化失败: {str(e)}")


def test_hybrid_agent():
    """测试Hybrid Agent模块化版本"""
    print("\n=== 测试 Hybrid Agent ===")
    try:
        from agents.hybrid_agent_modular import HybridAgentModular
        
        agent = HybridAgentModular()
        
        # 测试用例 - 覆盖不同类型的查询
        test_cases = [
            ("SQL查询", "贵州茅台最新股价"),
            ("RAG查询", "贵州茅台最新公告说了什么"),
            ("财务分析", "分析平安银行的财务状况"),
            ("资金流向", "分析宁德时代的资金流向"),
            ("混合查询", "贵州茅台的股价和最新公告")
        ]
        
        for query_type, query in test_cases:
            print(f"\n{query_type}: {query}")
            start_time = datetime.now()
            try:
                result = asyncio.run(agent.query(query))
                end_time = datetime.now()
                elapsed = (end_time - start_time).total_seconds()
                
                if result.get("success"):
                    print(f"✓ 成功 (耗时: {elapsed:.2f}秒)")
                    # 显示查询类型
                    query_type_detected = result.get("query_type", "未知")
                    print(f"  检测到的查询类型: {query_type_detected}")
                else:
                    print(f"✗ 失败: {result.get('error', '未知错误')}")
            except Exception as e:
                print(f"✗ 异常: {str(e)}")
                
    except Exception as e:
        print(f"✗ Hybrid Agent初始化失败: {str(e)}")


def main():
    """主测试函数"""
    print("=== Phase 3 模块化Agent功能测试 ===")
    print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 测试各个Agent
    test_rag_agent()
    test_financial_agent()
    test_money_flow_agent()
    test_hybrid_agent()
    
    print("\n=== 测试完成 ===")
    print("\n建议:")
    print("1. 如果有失败的测试，检查相应Agent的模块化实现")
    print("2. 确保所有公共模块（参数提取器等）工作正常")
    print("3. 检查数据库连接和API密钥配置")
    print("4. 逐个修复问题，保持向后兼容性")


if __name__ == "__main__":
    main()