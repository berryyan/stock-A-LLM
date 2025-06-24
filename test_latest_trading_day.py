#!/usr/bin/env python3
"""
测试最新交易日查询 - 诊断日期判断问题
"""
from database.mysql_connector import MySQLConnector
from datetime import datetime

def test_trading_day_logic():
    """测试交易日查询逻辑"""
    mysql = MySQLConnector()
    
    print("🔍 诊断最新交易日查询问题")
    print("=" * 50)
    print(f"当前时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # 1. 检查最近几天的数据是否存在
    print("1. 检查最近几天的交易数据:")
    recent_days_query = """
    SELECT trade_date, COUNT(*) as record_count 
    FROM tu_daily_detail 
    WHERE trade_date >= '2025-06-20' 
    GROUP BY trade_date 
    ORDER BY trade_date DESC
    """
    
    try:
        recent_data = mysql.execute_query(recent_days_query)
        if recent_data:
            for row in recent_data:
                print(f"  {row['trade_date']}: {row['record_count']}条记录")
        else:
            print("  ❌ 未找到最近的交易数据")
    except Exception as e:
        print(f"  ❌ 查询失败: {e}")
    
    print()
    
    # 2. 测试当前逻辑：trade_date < CURDATE()
    print("2. 当前逻辑测试 (trade_date < CURDATE()):")
    current_logic_query = """
    SELECT trade_date 
    FROM tu_daily_detail 
    WHERE trade_date < CURDATE()
    ORDER BY trade_date DESC 
    LIMIT 1
    """
    
    try:
        current_result = mysql.execute_query(current_logic_query)
        if current_result:
            print(f"  当前逻辑结果: {current_result[0]['trade_date']}")
        else:
            print("  ❌ 当前逻辑未找到结果")
    except Exception as e:
        print(f"  ❌ 当前逻辑查询失败: {e}")
    
    print()
    
    # 3. 测试改进逻辑：trade_date <= CURDATE()  
    print("3. 改进逻辑测试 (trade_date <= CURDATE()):")
    improved_logic_query = """
    SELECT trade_date 
    FROM tu_daily_detail 
    WHERE trade_date <= CURDATE()
    ORDER BY trade_date DESC 
    LIMIT 1
    """
    
    try:
        improved_result = mysql.execute_query(improved_logic_query)
        if improved_result:
            print(f"  改进逻辑结果: {improved_result[0]['trade_date']}")
        else:
            print("  ❌ 改进逻辑未找到结果")
    except Exception as e:
        print(f"  ❌ 改进逻辑查询失败: {e}")
    
    print()
    
    # 4. 检查数据库服务器时间
    print("4. 检查数据库服务器时间:")
    time_query = "SELECT NOW() as server_time, CURDATE() as current_date"
    
    try:
        time_result = mysql.execute_query(time_query)
        if time_result:
            print(f"  数据库服务器时间: {time_result[0]['server_time']}")
            print(f"  数据库当前日期: {time_result[0]['current_date']}")
        else:
            print("  ❌ 无法获取数据库时间")
    except Exception as e:
        print(f"  ❌ 时间查询失败: {e}")
    
    print()
    
    # 5. 建议的时间感知逻辑
    print("5. 建议的时间感知逻辑测试:")
    print("   逻辑：如果当前时间 >= 20:00，则包含今天；否则排除今天")
    
    time_aware_query = """
    SELECT trade_date 
    FROM tu_daily_detail 
    WHERE trade_date <= 
        CASE 
            WHEN TIME(NOW()) >= '20:00:00' THEN CURDATE()
            ELSE DATE_SUB(CURDATE(), INTERVAL 1 DAY)
        END
    ORDER BY trade_date DESC 
    LIMIT 1
    """
    
    try:
        time_aware_result = mysql.execute_query(time_aware_query)
        if time_aware_result:
            print(f"  时间感知逻辑结果: {time_aware_result[0]['trade_date']}")
        else:
            print("  ❌ 时间感知逻辑未找到结果")
    except Exception as e:
        print(f"  ❌ 时间感知逻辑查询失败: {e}")
    
    print()
    print("📋 结论分析:")
    print("如果今天(2025-06-24)数据存在但当前逻辑返回2025-06-23，")
    print("说明需要将 WHERE trade_date < CURDATE() 改为 WHERE trade_date <= CURDATE()")
    print("或者实现更智能的时间感知逻辑。")

if __name__ == "__main__":
    test_trading_day_logic()