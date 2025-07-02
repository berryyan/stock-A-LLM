#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
快速测试成交额排名的时间+排名查询
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.sql_agent import SQLAgent
import time

def test_date_queries():
    """专门测试带日期的成交额排名查询"""
    
    print("成交额排名-时间查询测试")
    print("=" * 100)
    
    sql_agent = SQLAgent()
    
    # 测试带日期的查询
    test_queries = [
        # 时间+排名测试
        ("今天的成交额排名", "今天+排名"),
        ("最新成交额排名", "最新+排名"),
        ("昨天成交额排名前10", "昨天+排名+数量"),
        ("2025-07-01成交额排名", "具体日期+排名"),
        ("2025年7月1日成交额前10", "中文日期+排名+数量"),
        
        # 对比测试（无日期）
        ("成交额排名", "基础查询（对比）"),
        ("成交额TOP10", "TOP格式（对比）"),
    ]
    
    quick_route_count = 0
    slow_count = 0
    
    for query, desc in test_queries:
        print(f"\n{'='*80}")
        print(f"测试: {desc}")
        print(f"查询: {query}")
        print("-" * 80)
        
        try:
            start_time = time.time()
            result = sql_agent.query(query)
            end_time = time.time()
            elapsed = end_time - start_time
            
            if result['success']:
                # 检查是否使用了快速路由
                if result.get('quick_path'):
                    quick_route_count += 1
                    print(f"⚡ 快速路由 (耗时: {elapsed:.2f}秒)")
                else:
                    slow_count += 1
                    print(f"🐌 慢速路由 (耗时: {elapsed:.2f}秒)")
                    
                # 检查输出格式
                result_text = result['result']
                if "##" in result_text and "|" in result_text:
                    print("✅ Markdown表格格式")
                else:
                    print("⚠️ 非Markdown格式")
                    
            else:
                print(f"❌ 查询失败: {result.get('error', '未知错误')}")
                
        except Exception as e:
            print(f"❌ 执行异常: {str(e)}")
        
        # 短暂延时
        time.sleep(0.5)
    
    # 统计
    print("\n\n" + "="*100)
    print("测试统计:")
    print(f"- 总测试数: {len(test_queries)}")
    print(f"- 快速路由: {quick_route_count}")
    print(f"- 慢速路由: {slow_count}")
    print(f"- 快速路由率: {quick_route_count/len(test_queries)*100:.1f}%")


if __name__ == "__main__":
    test_date_queries()