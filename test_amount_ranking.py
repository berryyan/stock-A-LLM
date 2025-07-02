#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试成交额排名功能
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.sql_agent import SQLAgent
import time

def test_amount_ranking():
    """测试成交额排名的各种查询格式"""
    
    print("成交额排名功能测试")
    print("=" * 100)
    
    sql_agent = SQLAgent()
    
    # 测试不同格式的成交额排名查询
    test_queries = [
        # 基础查询（无数字默认前10）
        ("成交额排名", "基础查询，应默认返回前10"),
        ("成交额排行", "使用'排行'词汇"),
        
        # 带数字的查询
        ("成交额排名前20", "指定前20名"),
        ("成交额最大的前5只股票", "最大的前N格式"),
        ("成交额前15", "简化格式"),
        
        # TOP格式
        ("成交额TOP10", "TOP格式查询"),
        ("成交额TOP5", "TOP5查询"),
        
        # 带日期的查询
        ("今天的成交额排名", "今天的数据"),
        ("昨天成交额排名前10", "昨天的数据"),
        ("最新成交额排名", "最新数据"),
        ("2025-07-01成交额排名", "指定日期"),
        ("2025年7月1日成交额前10", "中文日期格式"),
        
        # 复杂组合
        ("2025-07-01成交额排名前20", "日期+数量"),
        ("昨天成交额TOP15", "日期+TOP格式"),
        
        # 测试成交量查询（个股）
        ("贵州茅台的成交量", "个股成交量查询"),
        ("平安银行昨天的成交额", "个股历史成交额"),
    ]
    
    success_count = 0
    quick_route_count = 0
    
    for query, desc in test_queries:
        print(f"\n{'='*80}")
        print(f"测试: {desc}")
        print(f"查询: {query}")
        print("-" * 80)
        
        try:
            start_time = time.time()
            result = sql_agent.query(query)
            end_time = time.time()
            
            if result['success']:
                success_count += 1
                print(f"✅ 查询成功 (耗时: {end_time - start_time:.2f}秒)")
                
                # 检查是否使用了快速路由
                if result.get('quick_path'):
                    quick_route_count += 1
                    print("⚡ 使用了快速路由")
                    
                # 显示部分结果
                result_text = result['result']
                lines = result_text.split('\n')
                
                # 显示前10行
                for i, line in enumerate(lines[:10]):
                    print(line)
                    
                if len(lines) > 10:
                    print("... (更多结果省略)")
                    
                # 检查输出格式
                if "##" in result_text and "|" in result_text:
                    print("\n✅ 输出格式：Markdown表格")
                else:
                    print("\n⚠️ 输出格式可能需要检查")
                    
            else:
                print(f"❌ 查询失败: {result.get('error', '未知错误')}")
                
        except Exception as e:
            print(f"❌ 执行异常: {str(e)}")
            import traceback
            traceback.print_exc()
        
        # 短暂延时，避免过快
        time.sleep(0.5)
    
    # 统计结果
    print("\n\n" + "="*100)
    print("测试统计:")
    print(f"- 总测试数: {len(test_queries)}")
    print(f"- 成功数: {success_count}")
    print(f"- 快速路由数: {quick_route_count}")
    print(f"- 成功率: {success_count/len(test_queries)*100:.1f}%")
    print(f"- 快速路由率: {quick_route_count/len(test_queries)*100:.1f}%")


def test_output_format():
    """测试成交额排名的输出格式"""
    
    print("\n\n成交额排名输出格式测试")
    print("=" * 100)
    
    sql_agent = SQLAgent()
    
    # 执行一个简单查询
    result = sql_agent.query("成交额TOP5")
    
    if result['success']:
        print("查询成功，输出内容：")
        print("-" * 80)
        print(result['result'])
        print("-" * 80)
        
        # 检查格式要素
        content = result['result']
        checks = [
            ("Markdown标题 (##)", "##" in content),
            ("表格分隔符 (|)", "|" in content),
            ("成交额字段", "成交额(亿)" in content),
            ("不包含市值", "市值" not in content),
            ("包含股价", "股价(元)" in content),
            ("包含涨跌幅", "涨跌幅" in content),
        ]
        
        print("\n格式检查：")
        for check_name, check_result in checks:
            status = "✅" if check_result else "❌"
            print(f"{status} {check_name}")
    else:
        print("查询失败")


if __name__ == "__main__":
    # 测试成交额排名功能
    test_amount_ranking()
    
    # 测试输出格式
    test_output_format()