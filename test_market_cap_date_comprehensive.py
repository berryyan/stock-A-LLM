#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
全面测试市值排名的日期处理 - 普通模板和快速模板
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.sql_agent import SQLAgent
from utils.date_intelligence import date_intelligence
import time

def test_market_cap_queries():
    """测试各种市值排名查询的日期处理"""
    
    print("市值排名日期处理全面测试")
    print("=" * 100)
    
    # 初始化SQL Agent
    sql_agent = SQLAgent()
    
    # 测试用例列表
    test_cases = [
        # 1. 快速模板测试 - 总市值
        ("总市值最大的前10只股票", "快速模板-默认日期"),
        ("今天总市值最大的前10只股票", "快速模板-今天"),
        ("最新总市值排名前10", "快速模板-最新"),
        ("2025-07-01总市值最大的前10只股票", "快速模板-指定日期"),
        ("昨天总市值排名", "快速模板-昨天"),
        
        # 2. 快速模板测试 - 流通市值
        ("流通市值最大的前10只股票", "快速模板-流通市值默认"),
        ("今天流通市值排名", "快速模板-流通市值今天"),
        ("2025-07-01流通市值前10", "快速模板-流通市值指定日期"),
        
        # 3. 普通模板测试（不匹配快速路由的查询）
        ("查询A股市值最大的公司", "普通模板-总市值"),
        ("分析今日市值排行榜", "普通模板-今日"),
        ("显示最新的市值TOP20", "普通模板-TOP20"),
        ("2025年7月1日的市值排名情况", "普通模板-指定日期"),
        
        # 4. 复杂查询测试
        ("总市值超过1000亿的股票", "普通模板-条件查询"),
        ("银行板块的市值排名", "普通模板-板块查询"),
    ]
    
    # 执行测试
    for query, test_type in test_cases:
        print(f"\n{'='*80}")
        print(f"测试类型: {test_type}")
        print(f"查询语句: {query}")
        print("-" * 80)
        
        try:
            # 记录开始时间
            start_time = time.time()
            
            # 执行查询
            result = sql_agent.query(query)
            
            # 记录结束时间
            end_time = time.time()
            elapsed_time = end_time - start_time
            
            if result['success']:
                print(f"✅ 查询成功 (耗时: {elapsed_time:.2f}秒)")
                
                # 分析结果中的日期
                result_text = str(result.get('result', ''))
                
                # 查找日期信息
                import re
                date_patterns = [
                    r'(\d{4}-\d{2}-\d{2})',
                    r'(\d{8})',
                    r'(\d{4})年(\d{1,2})月(\d{1,2})日'
                ]
                
                found_dates = []
                for pattern in date_patterns:
                    matches = re.findall(pattern, result_text)
                    if matches:
                        found_dates.extend(matches)
                
                if found_dates:
                    print(f"结果中的日期: {found_dates}")
                
                # 检查是否使用了快速路由
                if hasattr(sql_agent, '_last_route_type'):
                    print(f"路由类型: {sql_agent._last_route_type}")
                
                # 显示部分结果
                lines = result_text.split('\n')
                print("\n结果预览:")
                for i, line in enumerate(lines[:10]):  # 显示前10行
                    print(f"  {line}")
                if len(lines) > 10:
                    print(f"  ... (共{len(lines)}行)")
                    
            else:
                print(f"❌ 查询失败")
                print(f"错误信息: {result.get('error', '未知错误')}")
                
        except Exception as e:
            print(f"❌ 执行异常: {str(e)}")
            import traceback
            traceback.print_exc()
        
        # 短暂延时
        time.sleep(0.5)
    
    print("\n" + "="*100)
    print("测试完成！")
    
    # 测试日期智能解析
    print("\n\n日期智能解析测试")
    print("="*100)
    
    test_dates = ["今天", "昨天", "最新", "2025-07-01", "前5天"]
    
    for date_expr in test_dates:
        try:
            processed_query, parsing_result = date_intelligence.preprocess_question(f"{date_expr}的市值排名")
            if parsing_result and parsing_result.get('modified_question'):
                print(f"\n'{date_expr}' 解析结果:")
                print(f"  原始查询: {parsing_result.get('original_query')}")
                print(f"  处理后查询: {parsing_result.get('modified_question')}")
                print(f"  时间类型: {parsing_result.get('temporal_type')}")
                if 'date_params' in parsing_result:
                    print(f"  日期参数: {parsing_result['date_params']}")
            else:
                print(f"\n'{date_expr}' 未检测到日期信息")
        except Exception as e:
            print(f"\n'{date_expr}' 解析失败: {e}")


def check_quick_route_detection():
    """检查快速路由的检测机制"""
    
    print("\n\n快速路由检测机制测试")
    print("="*100)
    
    from utils.query_templates import match_query_template
    
    # 测试各种查询是否能匹配到快速路由
    test_queries = [
        # 应该匹配的查询
        "总市值最大的前10只股票",
        "今天总市值最大的前10只股票",
        "2025-07-01总市值最大的前10只股票",
        "流通市值排名",
        "流通市值前20",
        
        # 不应该匹配的查询
        "市值分析",
        "查询市值数据",
        "A股市值情况",
    ]
    
    for query in test_queries:
        result = match_query_template(query)
        if result:
            template, params = result
            print(f"\n✅ '{query}'")
            print(f"   匹配模板: {template.name}")
            print(f"   路由类型: {template.route_type}")
            print(f"   提取参数: {params}")
        else:
            print(f"\n❌ '{query}' - 未匹配到快速路由")


if __name__ == "__main__":
    # 运行主测试
    test_market_cap_queries()
    
    # 运行快速路由检测测试
    check_quick_route_detection()