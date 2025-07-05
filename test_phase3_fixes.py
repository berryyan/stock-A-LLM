#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Phase 3 修复验证测试
验证修复后的功能是否正常
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import asyncio
from datetime import datetime


def test_financial_agent():
    """测试Financial Agent修复后的功能"""
    print("\n=== 测试 Financial Agent（修复后） ===")
    try:
        from agents.financial_agent_modular import FinancialAgentModular
        
        agent = FinancialAgentModular()
        print("✓ 初始化成功")
        
        # 测试财务健康度分析
        query = "分析贵州茅台的财务健康度"
        print(f"\n测试查询: {query}")
        
        start_time = datetime.now()
        result = agent.analyze(query)
        elapsed = (datetime.now() - start_time).total_seconds()
        
        if result.get("success"):
            print(f"✓ 查询成功 (耗时: {elapsed:.2f}秒)")
            print(f"  分析类型: {result.get('analysis_type', '未知')}")
            # 显示部分结果
            if 'result' in result:
                preview = str(result['result'])[:200] + "..." if len(str(result['result'])) > 200 else str(result['result'])
                print(f"  结果预览: {preview}")
        else:
            print(f"✗ 查询失败: {result.get('error', '未知错误')}")
            
    except Exception as e:
        print(f"✗ 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()


def test_money_flow_agent():
    """测试Money Flow Agent功能"""
    print("\n=== 测试 Money Flow Agent ===")
    try:
        from agents.money_flow_agent_modular import MoneyFlowAgentModular
        
        agent = MoneyFlowAgentModular()
        print("✓ 初始化成功")
        
        # 测试资金流向分析
        query = "分析贵州茅台的资金流向"
        print(f"\n测试查询: {query}")
        
        start_time = datetime.now()
        result = agent.analyze(query)
        elapsed = (datetime.now() - start_time).total_seconds()
        
        if result.get("success"):
            print(f"✓ 查询成功 (耗时: {elapsed:.2f}秒)")
            # 显示分析类型
            if 'data' in result:
                print(f"  数据条数: {len(result.get('data', []))}")
            if 'analysis' in result:
                preview = result['analysis'][:200] + "..." if len(result['analysis']) > 200 else result['analysis']
                print(f"  分析预览: {preview}")
        else:
            print(f"✗ 查询失败: {result.get('error', '未知错误')}")
            
    except Exception as e:
        print(f"✗ 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()


def test_hybrid_agent():
    """测试Hybrid Agent修复后的功能"""
    print("\n=== 测试 Hybrid Agent（修复后） ===")
    try:
        from agents.hybrid_agent_modular import HybridAgentModular
        
        agent = HybridAgentModular()
        print("✓ 初始化成功")
        
        # 测试SQL查询
        query = "贵州茅台最新股价"
        print(f"\n测试查询: {query}")
        
        start_time = datetime.now()
        result = agent.query(query)
        elapsed = (datetime.now() - start_time).total_seconds()
        
        if result.get("success"):
            print(f"✓ 查询成功 (耗时: {elapsed:.2f}秒)")
            print(f"  查询类型: {result.get('query_type', '未知')}")
            # 显示答案预览
            answer = result.get('answer', '')
            if answer:
                preview = answer[:200] + "..." if len(answer) > 200 else answer
                print(f"  答案预览: {preview}")
        else:
            print(f"✗ 查询失败: {result.get('error', '未知错误')}")
            
    except Exception as e:
        print(f"✗ 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()


def main():
    """主测试函数"""
    print("=== Phase 3 修复验证测试 ===")
    print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 测试各个Agent
    test_financial_agent()
    test_money_flow_agent()
    test_hybrid_agent()
    
    print("\n=== 测试完成 ===")


if __name__ == "__main__":
    main()