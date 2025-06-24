#!/usr/bin/env python
"""
测试日期BUG修复
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from datetime import datetime
from utils.date_intelligence import date_intelligence

def test_latest_trading_day():
    """测试最新交易日获取"""
    print("🔍 测试最新交易日获取...")
    
    # 清理缓存确保获取最新数据
    date_intelligence.clear_cache("latest_trading_day")
    
    # 获取最新交易日
    latest_day = date_intelligence.get_latest_trading_day()
    
    print(f"📅 当前日期: {datetime.now().strftime('%Y-%m-%d')}")
    print(f"📈 系统返回的最新交易日: {latest_day}")
    
    # 检查是否是今天（2025-06-23）
    today = datetime.now().strftime('%Y-%m-%d')
    
    if latest_day == today:
        print("✅ BUG已修复! 系统正确返回了今天的交易日")
        return True
    elif latest_day == "2025-06-20":
        print("❌ BUG仍存在! 系统仍然返回2025-06-20")
        return False
    else:
        print(f"⚠️ 返回了其他日期: {latest_day}")
        return False

def test_date_parsing():
    """测试日期解析功能"""
    print("\n🔍 测试日期智能解析...")
    
    test_queries = [
        "贵州茅台最新股价",
        "600519.SH最新的收盘价",
        "茅台现在多少钱",
        "000333.SZ当前股价"
    ]
    
    all_passed = True
    
    for query in test_queries:
        print(f"\n📝 测试查询: {query}")
        
        processed_query, result = date_intelligence.preprocess_question(query)
        
        print(f"🔄 处理后查询: {processed_query}")
        print(f"📅 解析的日期: {result.get('parsed_date', 'None')}")
        
        # 检查是否包含2025-06-23而不是2025-06-20
        if "2025-06-23" in processed_query:
            print("✅ 正确解析为今天的日期")
        elif "2025-06-20" in processed_query:
            print("❌ 仍然解析为过期日期")
            all_passed = False
        else:
            print("⚠️ 解析结果未包含预期日期")
            all_passed = False
    
    return all_passed

def test_database_data():
    """测试数据库中是否真的有今天的数据"""
    print("\n🔍 检查数据库中今天的数据...")
    
    try:
        from database.mysql_connector import MySQLConnector
        
        mysql = MySQLConnector()
        today = datetime.now().strftime('%Y-%m-%d')
        
        # 检查今天是否有交易数据
        query = """
        SELECT COUNT(*) as count, MIN(ts_code) as sample_code
        FROM tu_daily_detail 
        WHERE trade_date = :today
        """
        
        result = mysql.execute_query(query, {'today': today})
        
        if result and len(result) > 0:
            count = result[0]['count']
            sample_code = result[0]['sample_code']
            
            print(f"📊 今天({today})的交易数据条数: {count}")
            print(f"📈 示例股票代码: {sample_code}")
            
            if count > 0:
                print("✅ 数据库中确实有今天的交易数据")
                return True
            else:
                print("❌ 数据库中没有今天的交易数据")
                return False
        else:
            print("❌ 数据库查询失败")
            return False
            
    except Exception as e:
        print(f"❌ 数据库连接失败: {e}")
        return False

def main():
    """主函数"""
    print("🚀 开始测试日期BUG修复")
    print("=" * 60)
    
    # 执行各项测试
    tests = [
        ("数据库数据检查", test_database_data),
        ("最新交易日获取", test_latest_trading_day),
        ("日期智能解析", test_date_parsing)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ 测试失败: {e}")
            results.append((test_name, False))
    
    # 汇总结果
    print("\n" + "=" * 60)
    print("📊 测试结果汇总:")
    
    all_passed = True
    for test_name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"  {test_name}: {status}")
        if not result:
            all_passed = False
    
    if all_passed:
        print(f"\n🎉 所有测试通过! 日期BUG已修复。")
        print(f"💡 现在系统应该正确返回{datetime.now().strftime('%Y-%m-%d')}的最新数据。")
    else:
        print(f"\n⚠️ 部分测试失败，请查看详细信息。")
    
    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)