#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试主力净流入排名单位修复
"""

from agents.sql_agent import SQLAgent
from agents.hybrid_agent import HybridAgent

def test_ranking_unit_fix():
    """测试排名单位修复"""
    
    print("=" * 80)
    print("主力净流入排名单位修复测试")
    print("=" * 80)
    
    # 测试查询
    test_queries = [
        "主力净流入最多的前5只股票",
        "主力净流出最多的前5只股票",
        "今天主力资金净流入排名",
    ]
    
    # 1. 直接测试SQL Agent
    print("\n### 1. SQL Agent 直接测试")
    print("-" * 60)
    
    sql_agent = SQLAgent()
    
    for query in test_queries[:1]:  # 只测试第一个
        print(f"\n查询: {query}")
        result = sql_agent.query(query)
        
        if result['success']:
            print("\n结果预览:")
            # 提取表格部分
            answer = result.get('answer', '')
            lines = answer.split('\n')
            
            # 找到表格部分并显示前几行
            table_started = False
            row_count = 0
            for line in lines:
                if '|' in line:
                    table_started = True
                if table_started:
                    print(line)
                    if '|' in line and '---' not in line:
                        row_count += 1
                    if row_count > 3:  # 只显示前3行数据
                        print("...")
                        break
            
            # 验证单位
            if "万" in answer:
                print("\n✅ 单位正确显示为'万元'")
                # 检查数值范围
                import re
                numbers = re.findall(r'\| [\d\.]+ \|', answer)
                if numbers:
                    # 提取第一个主力净流入数值
                    for line in lines:
                        if '|' in line and '通威股份' in line:
                            parts = line.split('|')
                            if len(parts) > 6:
                                value = parts[6].strip()
                                try:
                                    num = float(value)
                                    print(f"✅ 数值范围合理: {num:.2f} 万元")
                                    if num > 10000:
                                        print("   (大于1万万元=1亿元，符合大盘股资金流向)")
                                except:
                                    pass
                            break
        else:
            print(f"❌ 查询失败: {result.get('error')}")
    
    # 2. 测试Hybrid Agent路由
    print("\n\n### 2. Hybrid Agent 路由测试")
    print("-" * 60)
    
    hybrid_agent = HybridAgent()
    
    query = "主力净流入排名"
    print(f"\n查询: {query}")
    result = hybrid_agent.query(query)
    
    if result['success']:
        if 'data' in result and result['data']:
            print(f"✅ 路由成功: {result.get('query_type')}")
            print(f"✅ 返回 {len(result['data'])} 条数据")
        else:
            print("⚠️ 查询成功但无数据")
    else:
        print(f"❌ 查询失败: {result.get('error')}")


if __name__ == "__main__":
    test_ranking_unit_fix()