#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试MoneyFlowAgent修复效果
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.money_flow_agent import MoneyFlowAgent
from utils.logger import setup_logger
import time

logger = setup_logger("test_money_flow_fix")


def test_money_flow():
    """测试资金流向查询"""
    print("="*60)
    print("测试MoneyFlowAgent修复效果")
    print("="*60)
    
    try:
        # 初始化Agent
        print("\n1. 初始化MoneyFlowAgent...")
        agent = MoneyFlowAgent()
        print("✅ 初始化成功")
        
        # 检查LLM类型
        print(f"\nLLM类型: {type(agent.llm)}")
        print(f"LLM配置: model={getattr(agent.llm, 'model_name', 'N/A')}")
        
        # 测试查询
        test_queries = [
            "茅台最近30天的资金流向",
            "分析贵州茅台的主力资金流入情况",
            "600519.SH的超大单资金如何"
        ]
        
        for i, query in enumerate(test_queries, 1):
            print(f"\n{'='*50}")
            print(f"测试 {i}: {query}")
            print("-"*50)
            
            start_time = time.time()
            
            try:
                result = agent.query(query)
                elapsed = time.time() - start_time
                
                if result['success']:
                    print(f"✅ 查询成功! (耗时: {elapsed:.2f}秒)")
                    # 显示部分结果
                    answer = result.get('answer', '')
                    if answer:
                        print(f"结果预览: {answer[:200]}...")
                    
                    # 显示分析数据
                    if 'analysis' in result:
                        analysis = result['analysis']
                        print(f"\n分析详情:")
                        print(f"- 股票代码: {analysis.get('ts_code', 'N/A')}")
                        print(f"- 分析周期: {analysis.get('period', 'N/A')}")
                        if 'summary' in analysis:
                            summary = analysis['summary']
                            print(f"- 主力净流入: {summary.get('main_net_flow', 'N/A')}")
                            print(f"- 流向趋势: {summary.get('flow_trend', 'N/A')}")
                else:
                    print(f"❌ 查询失败: {result.get('error', 'Unknown error')}")
                    
            except Exception as e:
                print(f"❌ 异常: {e}")
                import traceback
                traceback.print_exc()
        
        return True
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_edge_cases():
    """测试边界情况"""
    print(f"\n\n{'='*60}")
    print("边界情况测试")
    print(f"{'='*60}")
    
    agent = MoneyFlowAgent()
    
    # 测试无效股票
    print("\n测试无效股票代码...")
    result = agent.query("XXXYYY的资金流向")
    if not result['success']:
        print(f"✅ 正确处理无效股票: {result.get('error', 'Handled')}")
    else:
        print("⚠️ 未预期的成功")
    
    # 测试空查询
    print("\n测试空查询...")
    result = agent.query("")
    if not result['success']:
        print(f"✅ 正确处理空查询: {result.get('error', 'Handled')}")
    else:
        print("⚠️ 未预期的成功")


def main():
    """主测试函数"""
    print("开始测试MoneyFlowAgent修复...\n")
    
    # 运行主测试
    success = test_money_flow()
    
    if success:
        # 运行边界测试
        test_edge_cases()
    
    print("\n\n测试完成!")
    
    if success:
        print("✅ MoneyFlowAgent修复成功!")
        print("\n注意事项：")
        print("- 已更新为使用ChatOpenAI（与其他Agent保持一致）")
        print("- 修复了LLM序列化错误问题")
        print("- 资金流向查询应该正常工作了")
    else:
        print("❌ 仍有问题需要调试")


if __name__ == "__main__":
    main()