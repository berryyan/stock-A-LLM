#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试复合查询修复
"""
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.hybrid_agent_modular import HybridAgentModular


def test_composite_query():
    """测试复合查询"""
    print("测试复合查询修复")
    print("="*60)
    
    agent = HybridAgentModular()
    
    # 测试查询
    query = "贵州茅台的股价和主要业务"
    print(f"查询: {query}")
    print("-"*60)
    
    result = agent.query(query)
    
    if result.get("success"):
        print("✅ 查询成功")
        print(f"查询类型: {result.get('query_type', 'unknown')}")
        print("\n返回结果:")
        print(result.get("answer", result.get("result", "无结果")))
        
        # 检查是否包含两种信息
        answer = str(result.get("answer", result.get("result", "")))
        has_price = any(kw in answer for kw in ["股价", "收盘价", "开盘价", "价格"])
        has_business = any(kw in answer for kw in ["业务", "主营", "产品", "白酒", "茅台酒"])
        
        print(f"\n包含股价信息: {'✅' if has_price else '❌'}")
        print(f"包含业务信息: {'✅' if has_business else '❌'}")
        
        if has_price and has_business:
            print("\n🎉 复合查询修复成功！")
        else:
            print("\n⚠️ 复合查询可能未完全修复")
    else:
        print("❌ 查询失败")
        print(f"错误: {result.get('error', '未知错误')}")


if __name__ == "__main__":
    test_composite_query()