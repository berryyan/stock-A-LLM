#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试哪些排名模板已配置快速路径
"""

import time
from utils.query_templates import query_templates, TemplateType
from agents.sql_agent import SQLAgent


def test_ranking_templates():
    """测试排名模板的快速路径配置"""
    
    print("=" * 80)
    print("排名模板快速路径配置测试")
    print("=" * 80)
    
    # 获取所有排名类模板
    ranking_templates = query_templates.get_template_by_type(TemplateType.RANKING)
    
    print(f"\n共有 {len(ranking_templates)} 个排名类模板:")
    print("-" * 60)
    
    sql_agent = SQLAgent()
    
    # 统计结果
    fast_path_enabled = []
    fast_path_disabled = []
    
    for template in ranking_templates:
        print(f"\n模板名称: {template.name}")
        print(f"路由类型: {template.route_type}")
        print(f"示例查询: {template.example}")
        
        # 测试是否能触发快速路径
        test_query = template.example
        start_time = time.time()
        
        try:
            result = sql_agent._try_quick_query(test_query)
            elapsed = time.time() - start_time
            
            if result:
                print(f"✅ 快速路径已启用 - 耗时: {elapsed:.2f}秒")
                fast_path_enabled.append({
                    'name': template.name,
                    'example': template.example,
                    'time': elapsed
                })
            else:
                print(f"⚠️ 快速路径未启用")
                fast_path_disabled.append({
                    'name': template.name,
                    'example': template.example
                })
        except Exception as e:
            print(f"❌ 测试失败: {e}")
            fast_path_disabled.append({
                'name': template.name,
                'example': template.example,
                'error': str(e)
            })
    
    # 汇总报告
    print("\n\n" + "=" * 80)
    print("快速路径配置汇总")
    print("=" * 80)
    
    print(f"\n✅ 已启用快速路径的模板 ({len(fast_path_enabled)}):")
    for item in fast_path_enabled:
        print(f"  - {item['name']} (平均耗时: {item['time']:.2f}秒)")
    
    print(f"\n⚠️ 未启用快速路径的模板 ({len(fast_path_disabled)}):")
    for item in fast_path_disabled:
        print(f"  - {item['name']}")
        if 'error' in item:
            print(f"    错误: {item['error']}")
    
    # 性能分析
    if fast_path_enabled:
        avg_time = sum(item['time'] for item in fast_path_enabled) / len(fast_path_enabled)
        print(f"\n快速路径平均响应时间: {avg_time:.2f}秒")


def test_specific_ranking_queries():
    """测试特定的排名查询"""
    
    print("\n\n" + "=" * 80)
    print("特定排名查询测试")
    print("=" * 80)
    
    sql_agent = SQLAgent()
    
    # 特定测试用例
    test_cases = [
        "涨幅前10",
        "跌幅前20", 
        "今天涨幅排名",
        "昨天跌幅最大的10只股票",
        "PE最高的前10",
        "PB最低的前10",
        "利润排名前20",
        "营收增长率前10"
    ]
    
    for query in test_cases:
        print(f"\n测试查询: {query}")
        print("-" * 40)
        
        start_time = time.time()
        result = sql_agent._try_quick_query(query)
        elapsed = time.time() - start_time
        
        if result:
            print(f"✅ 触发快速路径 - 耗时: {elapsed:.2f}秒")
        else:
            print(f"⚠️ 未触发快速路径")
            # 尝试模板匹配看是否有对应模板
            from utils.query_templates import match_query_template
            template_match = match_query_template(query)
            if template_match:
                template, params = template_match
                print(f"   匹配到模板: {template.name}")
                print(f"   路由类型: {template.route_type}")
            else:
                print(f"   未匹配到任何模板")


if __name__ == "__main__":
    # 测试排名模板配置
    test_ranking_templates()
    
    # 测试特定查询
    test_specific_ranking_queries()