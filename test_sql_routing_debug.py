#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
SQL Agent快速路由调试工具
用于诊断为什么某些模板没有触发快速路由
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.sql_agent import SQLAgent
from utils.query_templates import match_query_template
from utils.date_intelligence import date_intelligence
import json


def test_template_matching():
    """测试模板匹配"""
    test_queries = [
        # K线查询
        "中国平安最近10天的K线",
        "万科A从20250620到20250625的走势",
        
        # 估值指标
        "平安银行的市盈率",
        "中国平安昨天的PE",
        
        # 市值排名
        "市值最大的前10只股票",
        "今天市值排名前20",
        
        # 主力净流入排名
        "主力净流入排行前10",
        "昨天主力资金净流入前10",
        
        # 成交额排名
        "成交额最大的前10只股票",
        "今天成交额排名前20"
    ]
    
    print("测试模板匹配结果：")
    print("="*80)
    
    for query in test_queries:
        print(f"\n查询: {query}")
        
        # 1. 日期预处理
        processed_query, date_info = date_intelligence.preprocess_question(query)
        print(f"处理后: {processed_query}")
        
        # 2. 模板匹配
        match_result = match_query_template(processed_query)
        if match_result:
            template, params = match_result
            print(f"匹配模板: {template.name}")
            print(f"路由类型: {template.route_type}")
            print(f"参数: {json.dumps(params, ensure_ascii=False, indent=2)}")
        else:
            print("未匹配到模板")
        print("-"*40)


def test_quick_route():
    """测试快速路由执行"""
    sql_agent = SQLAgent()
    
    test_queries = [
        # 已实现的快速路由
        ("中国平安最新股价", "股价查询"),
        ("平安银行的市盈率", "估值指标查询"),
        ("涨幅最大的前10只股票", "涨跌幅排名"),
        ("市值最大的前10只股票", "市值排名"),
        
        # 需要修复的快速路由
        ("中国平安最近10天的K线", "K线查询"),
        ("主力净流入排行前10", "主力净流入排行"),
        ("成交额最大的前10只股票", "成交额排名"),
    ]
    
    print("\n\n快速路由测试结果：")
    print("="*80)
    
    for query, expected_template in test_queries:
        print(f"\n查询: {query}")
        print(f"期望模板: {expected_template}")
        
        # 测试快速路由
        try:
            # 使用_try_quick_query方法测试
            result = sql_agent._try_quick_query(query)
            if result:
                print("✅ 快速路由成功")
                print(f"使用快速路径: {result.get('quick_path', False)}")
                if result.get('success'):
                    print("结果预览:", result['result'][:200] + "..." if len(result['result']) > 200 else result['result'])
            else:
                print("❌ 快速路由失败 - 返回None")
                
                # 尝试通过完整流程
                full_result = sql_agent.query(query)
                if full_result.get('success'):
                    print("但通过完整流程成功")
                    print("耗时可能较长")
        except Exception as e:
            print(f"❌ 错误: {e}")
        
        print("-"*40)


def check_sql_agent_templates():
    """检查SQL Agent中实现的模板"""
    print("\n\n检查SQL Agent实现的模板：")
    print("="*80)
    
    # 读取sql_agent.py中的模板处理代码
    with open('agents/sql_agent.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 查找所有template.name的判断
    import re
    template_checks = re.findall(r"template\.name\s*==\s*['\"]([^'\"]+)['\"]", content)
    in_list_checks = re.findall(r"template\.name\s+in\s+\[([^\]]+)\]", content)
    
    print("单独判断的模板:")
    for i, template in enumerate(template_checks, 1):
        print(f"{i}. {template}")
    
    print("\n列表判断的模板:")
    for check in in_list_checks:
        templates = re.findall(r"['\"]([^'\"]+)['\"]", check)
        for template in templates:
            print(f"- {template}")
    
    # 查找SQLTemplates引用
    sql_template_refs = re.findall(r"SQLTemplates\.(\w+)", content)
    print(f"\n引用的SQL模板: {len(set(sql_template_refs))}个")
    print("包括:", ", ".join(sorted(set(sql_template_refs))[:10]), "...")


if __name__ == "__main__":
    # 1. 测试模板匹配
    test_template_matching()
    
    # 2. 检查SQL Agent实现
    check_sql_agent_templates()
    
    # 3. 测试快速路由
    test_quick_route()