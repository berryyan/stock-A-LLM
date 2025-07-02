#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试市值排名的各种表达方式
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.query_templates import match_query_template
from agents.sql_agent import SQLAgent
import time

def test_various_expressions():
    """测试各种市值排名的表达方式"""
    
    print("市值排名表达方式测试")
    print("=" * 100)
    
    # 测试快速路由识别
    test_expressions = [
        # 总市值相关
        ("总市值最大的前10只股票", "标准表达"),
        ("总市值排名", "简单表达"),
        ("市值排名前10", "省略'总'字"),
        ("市值最大的10只股票", "变体1"),
        ("A股市值排名", "添加'A股'"),
        ("总市值TOP10", "使用TOP"),
        ("市值前20名", "使用'名'"),
        
        # 流通市值相关
        ("流通市值最大的前10只股票", "流通市值标准"),
        ("流通市值排名", "流通市值简单"),
        ("流通市值前10", "流通市值省略"),
        ("流通市值TOP20", "流通市值TOP"),
        
        # 带时间的表达
        ("今天总市值最大的前10只股票", "今天"),
        ("最新市值排名", "最新"),
        ("昨天的市值排名", "昨天"),
        ("2025-07-01市值排名", "指定日期"),
        ("本周市值排名", "本周"),
        
        # 其他表达（可能不匹配快速路由）
        ("查询市值数据", "查询动词"),
        ("分析市值情况", "分析动词"),
        ("市值分布", "分布"),
        ("市值统计", "统计"),
    ]
    
    print("\n1. 快速路由匹配测试")
    print("-" * 80)
    
    for expr, desc in test_expressions:
        result = match_query_template(expr)
        if result:
            template, params = result
            print(f"\n✅ {desc}: '{expr}'")
            print(f"   模板: {template.name}")
            print(f"   参数: {params}")
        else:
            print(f"\n❌ {desc}: '{expr}' - 未匹配快速路由")
    
    # 测试实际查询效果
    print("\n\n2. 实际查询效果测试（仅测试匹配的表达）")
    print("=" * 100)
    
    sql_agent = SQLAgent()
    
    # 只测试能匹配快速路由的查询
    quick_test_queries = [
        "总市值最大的前10只股票",
        "今天总市值排名",
        "流通市值前10",
        "2025-07-01总市值最大的前5只股票",
    ]
    
    for query in quick_test_queries:
        print(f"\n查询: {query}")
        print("-" * 40)
        
        try:
            start_time = time.time()
            # 直接测试快速路由
            result = sql_agent._try_quick_query(query)
            end_time = time.time()
            
            if result and result.get('success'):
                print(f"✅ 成功 (耗时: {end_time - start_time:.2f}秒)")
                
                # 提取日期信息
                result_text = str(result.get('result', ''))
                import re
                dates = re.findall(r'\d{4}-\d{2}-\d{2}', result_text)
                if dates:
                    print(f"数据日期: {dates[0]}")
                
                # 显示第一条记录
                lines = result_text.split('\n')
                for line in lines:
                    if '工商银行' in line or '建设银行' in line:
                        print(f"示例数据: {line.strip()}")
                        break
            else:
                print("❌ 查询失败或未使用快速路由")
                
        except Exception as e:
            print(f"❌ 错误: {str(e)}")


def test_edge_cases():
    """测试边界情况"""
    
    print("\n\n3. 边界情况测试")
    print("=" * 100)
    
    edge_cases = [
        # 数字表达
        ("总市值前5", "最小数字"),
        ("总市值前100", "大数字"),
        ("总市值前1000只", "超大数字"),
        
        # 混合表达
        ("2025年7月1日总市值前10", "中文日期"),
        ("上个交易日市值排名", "相对日期"),
        ("最近5天市值排名", "时间范围"),
        
        # 错误表达
        ("总市值前", "缺少数字"),
        ("前10总市值", "顺序错误"),
        ("总市值第10名", "单个排名"),
    ]
    
    for expr, desc in edge_cases:
        result = match_query_template(expr)
        if result:
            template, params = result
            print(f"\n✅ {desc}: '{expr}'")
            print(f"   模板: {template.name}")
            print(f"   参数: {params}")
        else:
            print(f"\n❌ {desc}: '{expr}' - 未匹配")


if __name__ == "__main__":
    # 运行测试
    test_various_expressions()
    test_edge_cases()