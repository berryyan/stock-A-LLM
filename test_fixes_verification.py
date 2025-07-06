#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
验证修复效果
"""
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.rag_agent_modular import RAGAgentModular
from agents.hybrid_agent_modular import HybridAgentModular


def test_rag_agent():
    """测试RAG Agent修复"""
    print("测试RAG Agent修复")
    print("="*60)
    
    agent = RAGAgentModular()
    query = "贵州茅台的发展战略"
    
    try:
        result = agent.query(query)
        if result.get("success"):
            print("✅ RAG Agent查询成功")
            # 检查结果是否正常
            answer = result.get("result", "")
            if isinstance(answer, str) and len(answer) > 0:
                print(f"返回结果长度: {len(answer)} 字符")
                print(f"结果预览: {answer[:100]}...")
            else:
                print("⚠️ 返回结果异常")
        else:
            print(f"❌ 查询失败: {result.get('error')}")
    except Exception as e:
        print(f"❌ 异常: {str(e)}")
    
    print()


def test_hybrid_agent():
    """测试Hybrid Agent复合查询修复"""
    print("测试Hybrid Agent复合查询修复")
    print("="*60)
    
    agent = HybridAgentModular()
    query = "贵州茅台的股价和主要业务"
    
    try:
        result = agent.query(query)
        if result.get("success"):
            print("✅ Hybrid Agent查询成功")
            print(f"查询类型: {result.get('query_type', 'unknown')}")
            
            # 检查是否返回了复合信息
            answer = str(result.get("answer", result.get("result", "")))
            has_price = any(kw in answer for kw in ["股价", "收盘价", "开盘价", "价格"])
            has_business = any(kw in answer for kw in ["业务", "主营", "产品", "白酒"])
            
            print(f"包含股价信息: {'✅' if has_price else '❌'}")
            print(f"包含业务信息: {'✅' if has_business else '❌'}")
            
            if has_price and has_business:
                print("\n🎉 复合查询成功！")
            else:
                print("\n⚠️ 复合查询可能未完全成功")
                
        else:
            print(f"❌ 查询失败: {result.get('error')}")
    except Exception as e:
        print(f"❌ 异常: {str(e)}")


if __name__ == "__main__":
    test_rag_agent()
    print("\n" + "="*60 + "\n")
    test_hybrid_agent()