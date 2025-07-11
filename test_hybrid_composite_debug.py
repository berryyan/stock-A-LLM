#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
调试Hybrid Agent复合查询功能
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.hybrid_agent_modular import HybridAgentModular

def debug_composite_queries():
    """调试复合查询"""
    print("=" * 80)
    print("Hybrid Agent 复合查询调试")
    print("=" * 80)
    
    agent = HybridAgentModular()
    
    # 测试复合查询检测
    test_queries = [
        "贵州茅台的股价和主要业务",
        "万科A的财务状况和最新公告",
        "比亚迪的股价及其资金流向",
        "宁德时代的财务健康度以及发展战略"
    ]
    
    for query in test_queries:
        print(f"\n查询: {query}")
        
        # 直接调用内部方法测试
        is_composite = agent._is_composite_query(query)
        print(f"是否复合查询: {is_composite}")
        
        if is_composite:
            parts = agent._analyze_composite_query(query)
            print(f"查询部分: {parts}")
        
        # 执行实际查询看结果
        print("\n执行查询...")
        try:
            result = agent.query(query)
            print(f"成功: {result.get('success', False)}")
            
            # 分析结果类型
            if result.get('success'):
                # Hybrid Agent返回的是'answer'字段，不是'result'
                result_text = str(result.get('answer', result.get('result', '')))
                print(f"结果长度: {len(result_text)}")
                
                # 检查是否包含多种信息
                has_price = any(word in result_text for word in ['股价', '元/股', '市值'])
                has_business = any(word in result_text for word in ['业务', '主营', '产品'])
                has_financial = any(word in result_text for word in ['财务', '健康度', 'ROE'])
                has_news = any(word in result_text for word in ['公告', '消息', '动态'])
                has_money = any(word in result_text for word in ['资金', '主力', '流向'])
                
                print(f"包含股价信息: {has_price}")
                print(f"包含业务信息: {has_business}")
                print(f"包含财务信息: {has_financial}")
                print(f"包含公告信息: {has_news}")
                print(f"包含资金信息: {has_money}")
                
                info_count = sum([has_price, has_business, has_financial, has_news, has_money])
                print(f"信息类型数: {info_count}")
                
                if info_count >= 2:
                    print("✅ 看起来是复合查询结果")
                else:
                    print("❌ 看起来只有单一类型信息")
                    
                # 打印部分结果预览
                print(f"\n结果预览:")
                print(result_text[:500] + "..." if len(result_text) > 500 else result_text)
                
        except Exception as e:
            print(f"错误: {str(e)}")
        
        print("-" * 80)

if __name__ == "__main__":
    debug_composite_queries()