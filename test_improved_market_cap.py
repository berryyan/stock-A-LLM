#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试改进后的市值排名功能
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.query_templates import match_query_template
from agents.sql_agent import SQLAgent
import time

def test_new_patterns():
    """测试新增的模式支持"""
    
    print("改进后的市值排名模式测试")
    print("=" * 80)
    
    # 测试用例
    test_cases = [
        # 无数字的查询（应该默认返回前10）
        ("总市值排名", "无数字-总市值"),
        ("市值排名", "无数字-市值"),
        ("流通市值排名", "无数字-流通市值"),
        ("市值排行", "排行"),
        
        # TOP格式
        ("总市值TOP10", "TOP格式"),
        ("市值TOP20", "TOP20"),
        ("流通市值TOP5", "流通市值TOP"),
        
        # 最新
        ("最新市值排名", "最新"),
        ("最新总市值排名", "最新总市值"),
        ("最新流通市值排名", "最新流通"),
        
        # 组合测试
        ("今天的市值排名", "今天+无数字"),
        ("昨天市值TOP10", "昨天+TOP"),
        ("2025-07-01总市值排名", "日期+无数字"),
        
        # 其他变体
        ("A股市值排名", "A股前缀"),
        ("中国市值排名", "中国前缀"),
        ("全部市值排名", "全部前缀"),
    ]
    
    print("1. 模式匹配测试")
    print("-" * 60)
    
    for query, desc in test_cases:
        result = match_query_template(query)
        if result:
            template, params = result
            print(f"\n✅ {desc}: '{query}'")
            print(f"   模板: {template.name}")
            print(f"   限制数: {params.get('limit', '默认10')}")
            print(f"   时间范围: {params.get('time_range', 'specified')}")
        else:
            print(f"\n❌ {desc}: '{query}' - 未匹配")


def test_quick_route_execution():
    """测试快速路由执行"""
    
    print("\n\n2. 快速路由执行测试")
    print("=" * 80)
    
    sql_agent = SQLAgent()
    
    # 重点测试无数字和新格式的查询
    test_queries = [
        "总市值排名",
        "市值TOP10",
        "最新市值排名",
        "流通市值排名",
        "今天的市值排行",
    ]
    
    for query in test_queries:
        print(f"\n查询: {query}")
        print("-" * 40)
        
        try:
            start_time = time.time()
            result = sql_agent._try_quick_query(query)
            end_time = time.time()
            
            if result and result.get('success'):
                print(f"✅ 成功 (耗时: {end_time - start_time:.2f}秒)")
                
                # 分析结果
                result_text = str(result.get('result', ''))
                
                # 计算返回的记录数
                lines = result_text.split('\n')
                data_lines = [line for line in lines if '|' in line and not line.startswith('排名')]
                record_count = len([line for line in data_lines if line.strip() and not line.startswith('-')])
                
                print(f"返回记录数: {record_count}")
                
                # 显示第一条记录
                for line in data_lines[:1]:
                    if line.strip() and not line.startswith('-'):
                        print(f"第一条: {line.strip()}")
                        
            else:
                print("❌ 查询失败或未使用快速路由")
                
        except Exception as e:
            print(f"❌ 错误: {str(e)}")


def verify_default_behavior():
    """验证默认行为"""
    
    print("\n\n3. 默认值验证")
    print("=" * 80)
    
    # 测试参数提取的默认值行为
    from utils.query_templates import query_templates
    
    test_queries = [
        "总市值排名",      # 应该默认limit=10
        "市值前20",        # 应该limit=20
        "市值TOP30",       # 应该limit=30
        "流通市值排名",    # 应该默认limit=10
    ]
    
    for query in test_queries:
        template = query_templates.match_template(query)
        if template:
            params = query_templates.extract_params(query, template)
            print(f"\n查询: {query}")
            print(f"提取的limit: {params.get('limit', '未提取到')}")
            print(f"使用的limit: {params.get('limit', template.default_params.get('limit', 10))}")


if __name__ == "__main__":
    # 运行测试
    test_new_patterns()
    verify_default_behavior()
    test_quick_route_execution()