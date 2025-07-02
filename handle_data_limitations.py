#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
处理数据更新限制的方案
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database.mysql_connector import MySQLConnector

def get_data_update_status():
    """获取各数据表的更新状态"""
    
    mysql_connector = MySQLConnector()
    
    status = {}
    
    # 检查关键数据表
    tables = {
        'tu_daily_basic': ('trade_date', '市值/估值数据'),
        'tu_daily_detail': ('trade_date', '股价/成交数据'),
        'tu_moneyflow_dc': ('trade_date', '资金流向数据'),
        'tu_income': ('end_date', '利润表数据'),
        'tu_balancesheet': ('end_date', '资产负债表数据'),
    }
    
    for table, (date_col, desc) in tables.items():
        try:
            sql = f"SELECT MAX({date_col}) as latest_date FROM {table}"
            result = mysql_connector.execute_query(sql)
            if result and result[0]['latest_date']:
                status[table] = {
                    'latest_date': str(result[0]['latest_date']),
                    'description': desc
                }
        except Exception as e:
            status[table] = {
                'latest_date': None,
                'description': desc,
                'error': str(e)
            }
    
    mysql_connector.close()
    return status

def format_query_result_with_data_notice(result: str, query_type: str, actual_date: str) -> str:
    """在查询结果中添加数据时效性说明"""
    
    # 需要特别说明的查询类型
    notice_required = {
        '市值排名': 'tu_daily_basic',
        '流通市值排名': 'tu_daily_basic', 
        '估值指标': 'tu_daily_basic',
        'PE查询': 'tu_daily_basic',
        'PB查询': 'tu_daily_basic',
    }
    
    if query_type in notice_required:
        # 获取数据更新状态
        status = get_data_update_status()
        table = notice_required[query_type]
        
        if table in status and status[table]['latest_date']:
            latest_date = status[table]['latest_date']
            
            # 如果实际查询日期早于用户期望，添加说明
            notice = f"\n\n📌 数据说明：由于{status[table]['description']}更新延迟，"
            notice += f"本次查询返回的是 {latest_date} 的数据。"
            
            result += notice
    
    return result

def suggest_alternative_query(original_query: str, data_status: dict) -> str:
    """根据数据状态建议替代查询"""
    
    suggestions = []
    
    # 如果查询最新市值但数据过时
    if '最新' in original_query and '市值' in original_query:
        latest_basic = data_status.get('tu_daily_basic', {}).get('latest_date')
        latest_detail = data_status.get('tu_daily_detail', {}).get('latest_date')
        
        if latest_basic and latest_detail and latest_basic < latest_detail:
            suggestions.append(f"💡 建议：市值数据更新至{latest_basic}，但股价数据已更新至{latest_detail}")
            suggestions.append("您可以查询：")
            suggestions.append("- 最新涨跌幅排名")
            suggestions.append("- 最新成交额排名")
            suggestions.append("- 最新资金流向排名")
    
    return "\n".join(suggestions) if suggestions else ""

def demo_usage():
    """演示如何使用数据限制处理"""
    
    print("数据更新状态检查")
    print("=" * 80)
    
    # 获取数据状态
    status = get_data_update_status()
    
    # 显示各表状态
    for table, info in status.items():
        print(f"\n{info['description']} ({table}):")
        if info['latest_date']:
            print(f"  最新数据: {info['latest_date']}")
        else:
            print(f"  错误: {info.get('error', '无数据')}")
    
    # 模拟查询结果处理
    print("\n" + "=" * 80)
    print("查询结果处理示例")
    
    # 示例1：市值排名查询
    mock_result = """
总市值排名 - 20250623

排名 | 股票名称 | 股票代码 | 股价 | 涨跌幅 | 总市值(亿) | 流通市值(亿)
------------------------------------------------------------
 1 | 贵州茅台   | 600519.SH | 1234.56 |  1.23% |   15000.00 |   15000.00
 2 | 工商银行   | 601398.SH |    5.67 |  0.45% |   20000.00 |   18000.00
"""
    
    enhanced_result = format_query_result_with_data_notice(
        mock_result, 
        '市值排名',
        '20250623'
    )
    
    print("\n原始结果:")
    print(mock_result)
    print("\n增强后的结果:")
    print(enhanced_result)
    
    # 显示替代建议
    print("\n" + "=" * 80)
    print("替代查询建议")
    suggestions = suggest_alternative_query("最新市值排名", status)
    if suggestions:
        print(suggestions)


if __name__ == "__main__":
    demo_usage()