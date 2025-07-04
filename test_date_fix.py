#!/usr/bin/env python3
"""
测试日期解析修复
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.date_intelligence import date_intelligence

def test_date_expressions():
    """测试各种日期表达"""
    test_cases = [
        # 当前时间点测试
        "贵州茅台最新股价",
        "贵州茅台今天的股价",
        "贵州茅台最后一个交易日的股价",  # 修复后应该等同于"最新"
        "贵州茅台最近一个交易日的股价",  # 修复后应该等同于"最新"
        
        # 前一个交易日测试
        "贵州茅台昨天的股价",
        "贵州茅台前一个交易日的股价",
        "贵州茅台上一个交易日的股价",
        "贵州茅台上个交易日的股价",
        
        # 前N个交易日测试
        "贵州茅台前3个交易日的股价",
        "贵州茅台上5个交易日的股价",
        
        # 时间段测试
        "贵州茅台前5天的K线",
        "贵州茅台最近10天的走势",
    ]
    
    print("=" * 80)
    print("日期解析测试")
    print("=" * 80)
    
    for query in test_cases:
        result = date_intelligence.parse_time_expressions(query)
        print(f"\n原始查询: {query}")
        print(f"修改后: {result.modified_question}")
        
        if result.expressions:
            for expr in result.expressions:
                print(f"  - 表达式: '{expr.original_text}'")
                print(f"    类型: {expr.type.value}")
                if expr.result_date:
                    print(f"    结果: {expr.result_date}")
                elif expr.result_range:
                    print(f"    结果: {expr.result_range[0]} 至 {expr.result_range[1]}")
        else:
            print("  - 无时间表达式")

def test_nth_trading_day():
    """测试前N个交易日的计算逻辑"""
    from utils.date_intelligence import TradingDayCalculator
    from database.mysql_connector import MySQLConnector
    
    calc = TradingDayCalculator(MySQLConnector())
    
    print("\n" + "=" * 80)
    print("前N个交易日计算测试")
    print("=" * 80)
    
    # 获取最新交易日作为基准
    base_date = calc.get_latest_trading_day()
    print(f"\n基准日期（最新交易日）: {base_date}")
    
    # 测试前N个交易日
    for n in [1, 2, 3, 5]:
        result = calc.get_nth_trading_day_before(n, base_date)
        print(f"前{n}个交易日: {result}")
    
    # 测试交易日范围
    print("\n交易日范围测试:")
    for days in [5, 10]:
        result = calc.get_trading_days_range(days, base_date)
        if result:
            print(f"最近{days}个交易日: {result[0]} 至 {result[1]}")

if __name__ == "__main__":
    test_date_expressions()
    test_nth_trading_day()