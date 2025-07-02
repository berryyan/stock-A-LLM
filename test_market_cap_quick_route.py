#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试市值排名的快速路由功能
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.sql_agent import SQLAgent
from database.mysql_connector import MySQLConnector
import time

def test_quick_route_only():
    """只测试快速路由功能"""
    
    print("市值排名快速路由测试")
    print("=" * 80)
    
    # 初始化SQL Agent
    sql_agent = SQLAgent()
    
    # 测试用例
    test_cases = [
        ("总市值最大的前10只股票", "默认日期"),
        ("今天总市值最大的前10只股票", "今天"),
        ("2025-07-01总市值排名", "指定日期"),
        ("流通市值前10", "流通市值"),
    ]
    
    for query, test_type in test_cases:
        print(f"\n测试: {test_type}")
        print(f"查询: {query}")
        print("-" * 40)
        
        try:
            # 测试快速路由
            start_time = time.time()
            quick_result = sql_agent._try_quick_query(query)
            end_time = time.time()
            
            if quick_result:
                print(f"✅ 快速路由成功 (耗时: {end_time - start_time:.2f}秒)")
                
                # 分析结果中的日期
                result_text = str(quick_result.get('result', ''))
                import re
                dates = re.findall(r'\d{4}-\d{2}-\d{2}', result_text)
                if dates:
                    print(f"结果日期: {dates[0]}")
                
                # 显示前几行
                lines = result_text.split('\n')
                for i, line in enumerate(lines[:8]):
                    if line.strip():
                        print(f"  {line}")
            else:
                print("❌ 未触发快速路由")
                
        except Exception as e:
            print(f"❌ 错误: {str(e)}")


def test_date_extraction():
    """测试日期提取功能"""
    
    print("\n\n日期提取功能测试")
    print("=" * 80)
    
    sql_agent = SQLAgent()
    
    test_queries = [
        "总市值排名",
        "今天总市值排名",
        "2025-07-01总市值排名",
        "昨天的市值排名",
        "最新市值数据",
    ]
    
    for query in test_queries:
        # 先进行日期智能解析
        from utils.date_intelligence import date_intelligence
        processed_query, parsing_result = date_intelligence.preprocess_question(query)
        
        print(f"\n原始查询: {query}")
        print(f"处理后: {processed_query}")
        
        # 测试日期提取
        extracted_date = sql_agent._extract_date_from_query(processed_query)
        print(f"提取的日期: {extracted_date}")
        
        # 获取最新交易日
        last_trading_date = sql_agent._get_last_trading_date()
        print(f"最新交易日: {last_trading_date}")
        print(f"最终使用日期: {extracted_date or last_trading_date}")


def check_data_availability():
    """检查数据可用性"""
    
    print("\n\n数据可用性检查")
    print("=" * 80)
    
    mysql_connector = MySQLConnector()
    
    try:
        # 检查tu_daily_basic最新数据
        sql = """
        SELECT trade_date, COUNT(*) as count 
        FROM tu_daily_basic 
        WHERE trade_date >= '20250625'
        GROUP BY trade_date 
        ORDER BY trade_date DESC
        """
        
        result = mysql_connector.execute_query(sql)
        
        print("\ntu_daily_basic表近期数据:")
        for row in result[:5]:
            print(f"  {row['trade_date']}: {row['count']} 条记录")
            
        # 检查特定日期的市值数据
        test_date = '20250701'
        sql = f"""
        SELECT COUNT(*) as total_count,
               COUNT(CASE WHEN total_mv > 0 THEN 1 END) as valid_mv_count,
               COUNT(CASE WHEN circ_mv > 0 THEN 1 END) as valid_circ_mv_count
        FROM tu_daily_basic
        WHERE trade_date = '{test_date}'
        """
        
        result = mysql_connector.execute_query(sql)
        if result:
            row = result[0]
            print(f"\n{test_date}数据统计:")
            print(f"  总记录数: {row['total_count']}")
            print(f"  有效总市值记录: {row['valid_mv_count']}")
            print(f"  有效流通市值记录: {row['valid_circ_mv_count']}")
            
    finally:
        mysql_connector.close()


if __name__ == "__main__":
    # 数据可用性检查
    check_data_availability()
    
    # 日期提取测试
    test_date_extraction()
    
    # 快速路由测试
    test_quick_route_only()