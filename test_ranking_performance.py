#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试排名查询性能 - 对比快速路径与LLM路由
"""

import time
import json
from agents.sql_agent import SQLAgent
from agents.money_flow_agent import MoneyFlowAgent
from agents.hybrid_agent import HybridAgent
from utils.logger import setup_logger


def test_ranking_performance():
    """测试排名查询性能"""
    
    print("=" * 80)
    print("排名查询性能测试")
    print("=" * 80)
    
    # 初始化agents
    sql_agent = SQLAgent()
    hybrid_agent = HybridAgent()
    
    # 测试用例
    test_cases = [
        # 市值排名
        ("市值排名", "市值排名 - 应该使用快速路径"),
        ("市值前20", "市值前20 - 应该使用快速路径"),
        ("今天的市值TOP10", "今天市值TOP10 - 应该使用快速路径"),
        
        # 涨跌幅排名
        ("涨幅前10", "涨幅前10 - 应该使用快速路径"),
        ("跌幅最大的20只股票", "跌幅前20 - 应该使用快速路径"),
        ("昨天涨幅排名", "昨天涨幅排名 - 应该使用快速路径"),
        
        # 成交额排名
        ("成交额排名", "成交额排名 - 应该使用快速路径"),
        ("成交额TOP20", "成交额TOP20 - 应该使用快速路径"),
        ("今天成交额最大的10只股票", "成交额前10 - 应该使用快速路径"),
        
        # 主力净流入排名
        ("主力净流入排名", "主力净流入排名 - 应该使用快速路径"),
        ("主力资金流入TOP10", "主力资金TOP10 - 应该使用快速路径"),
        ("今天主力净流入前20", "主力净流入前20 - 应该使用快速路径"),
    ]
    
    # 性能统计
    performance_stats = {
        "fast_path": [],
        "llm_route": []
    }
    
    for query, description in test_cases:
        print(f"\n### 测试: {description}")
        print(f"查询: {query}")
        print("-" * 60)
        
        # 测试快速路径
        print("\n1. 测试快速路径（SQL Agent直接处理）:")
        start_time = time.time()
        
        try:
            # 直接调用SQL Agent的query方法
            result = sql_agent.query(query)
            elapsed = time.time() - start_time
            
            if result['success']:
                print(f"✅ 成功 - 耗时: {elapsed:.2f}秒")
                if result.get('quick_path'):
                    print("   使用了快速路径")
                    performance_stats["fast_path"].append(elapsed)
                else:
                    print("   ⚠️ 未使用快速路径")
                    performance_stats["llm_route"].append(elapsed)
                    
                # 显示部分结果
                result_preview = result.get('result', '')[:200]
                print(f"   结果预览: {result_preview}...")
            else:
                print(f"❌ 失败: {result.get('error')}")
                
        except Exception as e:
            print(f"❌ 异常: {e}")
            
        # 测试LLM路由（通过Hybrid Agent）
        print("\n2. 测试LLM路由（Hybrid Agent）:")
        start_time = time.time()
        
        try:
            # 通过Hybrid Agent触发LLM路由
            result = hybrid_agent.query(query)
            elapsed = time.time() - start_time
            
            if result['success']:
                print(f"✅ 成功 - 耗时: {elapsed:.2f}秒")
                performance_stats["llm_route"].append(elapsed)
                
                # 显示路由信息
                if 'query_type' in result:
                    print(f"   路由类型: {result['query_type']}")
                    
            else:
                print(f"❌ 失败: {result.get('error')}")
                
        except Exception as e:
            print(f"❌ 异常: {e}")
    
    # 性能分析
    print("\n\n" + "=" * 80)
    print("性能分析总结")
    print("=" * 80)
    
    if performance_stats["fast_path"]:
        avg_fast = sum(performance_stats["fast_path"]) / len(performance_stats["fast_path"])
        print(f"\n快速路径性能:")
        print(f"  - 平均耗时: {avg_fast:.2f}秒")
        print(f"  - 最快: {min(performance_stats['fast_path']):.2f}秒")
        print(f"  - 最慢: {max(performance_stats['fast_path']):.2f}秒")
        print(f"  - 样本数: {len(performance_stats['fast_path'])}")
    
    if performance_stats["llm_route"]:
        avg_llm = sum(performance_stats["llm_route"]) / len(performance_stats["llm_route"])
        print(f"\nLLM路由性能:")
        print(f"  - 平均耗时: {avg_llm:.2f}秒")
        print(f"  - 最快: {min(performance_stats['llm_route']):.2f}秒")
        print(f"  - 最慢: {max(performance_stats['llm_route']):.2f}秒")
        print(f"  - 样本数: {len(performance_stats['llm_route'])}")
    
    if performance_stats["fast_path"] and performance_stats["llm_route"]:
        speedup = avg_llm / avg_fast
        print(f"\n性能提升: 快速路径比LLM路由快 {speedup:.1f}倍")


def test_current_templates():
    """测试当前已实现的快速路径模板"""
    
    print("\n\n" + "=" * 80)
    print("当前快速路径模板覆盖情况")
    print("=" * 80)
    
    from utils.query_templates import query_templates, TemplateType
    
    # 获取所有排名类模板
    ranking_templates = query_templates.get_template_by_type(TemplateType.RANKING)
    
    print(f"\n共有 {len(ranking_templates)} 个排名类模板:")
    print("-" * 60)
    
    for template in ranking_templates:
        print(f"\n模板名称: {template.name}")
        print(f"路由类型: {template.route_type}")
        print(f"示例查询: {template.example}")
        print(f"默认参数: {template.default_params}")
        
        # 测试模板匹配
        test_query = template.example
        sql_agent = SQLAgent()
        
        # 检查是否能触发快速路径
        try:
            matched_template = sql_agent._match_quick_query_template(test_query)
            if matched_template:
                print(f"✅ 可触发快速路径")
            else:
                print(f"⚠️ 无法触发快速路径")
        except:
            print(f"❌ 检查失败")


if __name__ == "__main__":
    # 测试性能对比
    test_ranking_performance()
    
    # 测试当前模板覆盖
    test_current_templates()