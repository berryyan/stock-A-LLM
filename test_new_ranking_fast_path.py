#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试新增排名模板的快速路径
"""

import time
from agents.sql_agent import SQLAgent
from utils.query_templates import match_query_template


def test_new_ranking_templates():
    """测试新增排名模板"""
    
    print("=" * 80)
    print("新增排名模板快速路径测试")
    print("=" * 80)
    
    sql_agent = SQLAgent()
    
    # 测试用例
    test_cases = [
        # PE排名
        ("PE最高的前10", "PE排名-最高"),
        ("市盈率排名前20", "PE排名-最高"), 
        ("PE最低的前10", "PE排名-最低"),
        ("今天PE排名", "PE排名-今天"),
        
        # PB排名
        ("PB最低的前10", "PB排名-最低"),
        ("市净率排名前20", "PB排名-最高"),
        ("破净股排名", "PB排名-破净"),
        
        # 净利润排名
        ("利润排名前20", "净利润排名"),
        ("净利润最高的前10", "净利润排名"),
        ("亏损最多的前10", "净利润排名-亏损"),
        
        # 营收排名
        ("营收排名前10", "营收排名"),
        ("营业收入最高的前20", "营收排名"),
        
        # ROE排名
        ("ROE排名前10", "ROE排名"),
        ("净资产收益率最高的前20", "ROE排名"),
    ]
    
    success_count = 0
    fail_count = 0
    
    for query, description in test_cases:
        print(f"\n### 测试: {description}")
        print(f"查询: {query}")
        print("-" * 60)
        
        # 测试模板匹配
        template_match = match_query_template(query)
        if template_match:
            template, params = template_match
            print(f"✅ 匹配到模板: {template.name}")
            print(f"   路由类型: {template.route_type}")
            print(f"   提取参数: {params}")
        else:
            print(f"❌ 未匹配到模板")
            fail_count += 1
            continue
        
        # 测试快速路径
        start_time = time.time()
        
        try:
            result = sql_agent._try_quick_query(query)
            elapsed = time.time() - start_time
            
            if result:
                print(f"✅ 快速路径成功 - 耗时: {elapsed:.2f}秒")
                # 显示部分结果
                result_lines = result['result'].split('\n')
                print(f"   结果预览:")
                for line in result_lines[:5]:
                    print(f"   {line}")
                if len(result_lines) > 5:
                    print(f"   ... (共{len(result_lines)}行)")
                success_count += 1
            else:
                print(f"❌ 快速路径失败")
                fail_count += 1
                
        except Exception as e:
            print(f"❌ 异常: {e}")
            fail_count += 1
    
    # 测试总结
    print("\n\n" + "=" * 80)
    print("测试总结")
    print("=" * 80)
    print(f"总测试用例: {len(test_cases)}")
    print(f"成功: {success_count}")
    print(f"失败: {fail_count}")
    print(f"成功率: {success_count/len(test_cases)*100:.1f}%")


def test_limit_extraction():
    """测试数字提取"""
    
    print("\n\n" + "=" * 80)
    print("数字提取测试")
    print("=" * 80)
    
    test_queries = [
        "PE排名前5",
        "市盈率最高的前30", 
        "PB排名",  # 默认应该是10
        "利润前100",
    ]
    
    for query in test_queries:
        template_match = match_query_template(query)
        if template_match:
            template, params = template_match
            limit = params.get('limit', 10)
            print(f"查询: {query}")
            print(f"  提取的limit: {limit}")
        else:
            print(f"查询: {query} - 未匹配到模板")


def test_edge_cases():
    """测试边界情况"""
    
    print("\n\n" + "=" * 80)
    print("边界情况测试")
    print("=" * 80)
    
    sql_agent = SQLAgent()
    
    edge_cases = [
        # 无效查询
        ("XYZ排名前10", "无效指标"),
        
        # 参数边界
        ("PE排名前0", "limit=0"),
        ("PB排名前200", "limit过大"),
        
        # 混合查询
        ("PE和PB排名前10", "混合指标"),
    ]
    
    for query, case_type in edge_cases:
        print(f"\n测试 {case_type}: {query}")
        
        template_match = match_query_template(query)
        if template_match:
            print("  意外匹配到模板")
        else:
            print("  ✅ 正确拒绝")


if __name__ == "__main__":
    # 测试新增模板
    test_new_ranking_templates()
    
    # 测试数字提取
    test_limit_extraction()
    
    # 测试边界情况
    test_edge_cases()