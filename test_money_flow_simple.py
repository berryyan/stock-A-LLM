#!/usr/bin/env python
"""
简单测试资金流向分析功能
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.money_flow_agent import MoneyFlowAgent
from utils.money_flow_analyzer import MoneyFlowAnalyzer, format_money_flow_report

def test_money_flow_analyzer():
    """测试资金流向分析器"""
    print("🔍 测试资金流向分析器...")
    
    try:
        # 创建分析器
        analyzer = MoneyFlowAnalyzer()
        
        # 分析贵州茅台
        print("📊 分析贵州茅台资金流向...")
        result = analyzer.analyze_money_flow("600519.SH", days=7)
        
        # 生成报告
        report = format_money_flow_report(result, "600519.SH")
        print("\n" + "="*50)
        print("资金流向分析报告")
        print("="*50)
        print(report)
        
        return True
        
    except Exception as e:
        print(f"❌ 分析器测试失败: {e}")
        return False

def test_money_flow_agent():
    """测试资金流向Agent"""
    print("\n🤖 测试资金流向Agent...")
    
    try:
        # 创建Agent
        agent = MoneyFlowAgent()
        
        # 测试查询
        questions = [
            "分析贵州茅台的资金流向",
            "600519.SH最近的主力资金流入情况",
            "茅台的超大单资金如何"
        ]
        
        for question in questions:
            print(f"\n📝 查询: {question}")
            result = agent.query(question)
            
            if result['success']:
                print("✅ 成功")
                print(f"答案: {result['answer'][:200]}...")
            else:
                print(f"❌ 失败: {result['error']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Agent测试失败: {e}")
        return False

if __name__ == "__main__":
    print("🚀 开始测试资金流向分析功能")
    
    # 测试分析器
    analyzer_ok = test_money_flow_analyzer()
    
    # 测试Agent
    agent_ok = test_money_flow_agent()
    
    print("\n" + "="*50)
    print("测试结果汇总")
    print("="*50)
    print(f"资金流向分析器: {'✅ 通过' if analyzer_ok else '❌ 失败'}")
    print(f"资金流向Agent: {'✅ 通过' if agent_ok else '❌ 失败'}")
    
    if analyzer_ok and agent_ok:
        print("\n🎉 所有测试通过！资金流向分析功能正常。")
    else:
        print("\n⚠️ 部分测试失败，请检查错误信息。")