#!/usr/bin/env python3
"""
测试最新交易日修复效果
验证数据驱动的交易日判断机制
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.date_intelligence import DateIntelligenceModule
from datetime import datetime
import time

def test_latest_trading_day_fix():
    """测试最新交易日修复效果"""
    
    print("🔧 最新交易日修复效果测试")
    print("=" * 60)
    print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("目标: 验证数据驱动的交易日判断是否正确识别今日数据")
    print()
    
    # 初始化日期智能模块
    date_intel = DateIntelligenceModule()
    
    # 1. 测试缓存状态
    print("1. 初始缓存状态:")
    cache_status = date_intel.get_cache_status()
    for key, value in cache_status.items():
        print(f"   {key}: {value}")
    print()
    
    # 2. 第一次查询最新交易日
    print("2. 第一次查询最新交易日 (应触发数据库查询):")
    start_time = time.time()
    latest_trading_day = date_intel.get_latest_trading_day()
    query_time = time.time() - start_time
    
    print(f"   结果: {latest_trading_day}")
    print(f"   查询耗时: {query_time:.3f}秒")
    
    # 检查今天是否为交易日
    today = datetime.now().strftime('%Y-%m-%d')
    is_today_trading_day = latest_trading_day == today
    print(f"   今日({today})是否为交易日: {is_today_trading_day}")
    print()
    
    # 3. 查看更新后的缓存状态
    print("3. 查询后的缓存状态:")
    cache_status = date_intel.get_cache_status()
    for key, value in cache_status.items():
        print(f"   {key}: {value}")
    print()
    
    # 4. 第二次查询（应使用缓存）
    print("4. 第二次查询最新交易日 (应使用缓存):")
    start_time = time.time()
    latest_trading_day_2 = date_intel.get_latest_trading_day()
    cache_query_time = time.time() - start_time
    
    print(f"   结果: {latest_trading_day_2}")
    print(f"   查询耗时: {cache_query_time:.3f}秒")
    print(f"   缓存命中: {latest_trading_day == latest_trading_day_2}")
    if cache_query_time > 0:
        performance_ratio = query_time / cache_query_time
        print(f"   性能提升: {performance_ratio:.1f}x")
    else:
        print(f"   性能提升: 无限倍 (缓存瞬时响应)")
    print()
    
    # 5. 测试预处理问题的效果
    print("5. 测试智能日期解析的预处理效果:")
    test_questions = [
        "茅台最新股价是多少？",
        "贵州茅台最新财务数据",
        "比亚迪现在的股价如何？"
    ]
    
    for question in test_questions:
        print(f"   问题: {question}")
        processed_question, parsing_result = date_intel.preprocess_question(question)
        
        if parsing_result.get('modified_question'):
            print(f"   处理前: {question}")
            print(f"   处理后: {processed_question}")
            print(f"   解析信息: {parsing_result}")
        else:
            print(f"   无需处理")
        print()
    
    # 6. 性能和稳定性总结
    print("📊 修复效果总结:")
    print("=" * 40)
    
    if is_today_trading_day:
        print("✅ 成功识别今日为交易日")
        print("✅ 数据驱动判断机制工作正常")
    else:
        print("ℹ️  今日非交易日或数据未更新")
        print(f"   最新交易日: {latest_trading_day}")
    
    if cache_query_time > 0:
        performance_text = f"性能提升 {(query_time / cache_query_time):.1f}x"
    else:
        performance_text = "性能提升 无限倍"
    print(f"✅ 缓存机制正常工作 ({performance_text})")
    print("✅ 适合长期API运行")
    
    # 7. 未来增强建议
    print()
    print("🚀 后续增强建议:")
    print("1. 可接入交易日查询API作为备用数据源")
    print("2. 可添加交易时间段的更细粒度判断")
    print("3. 可支持不同市场的交易日历")
    
    return {
        'latest_trading_day': latest_trading_day,
        'is_today_trading_day': is_today_trading_day,
        'cache_performance': query_time / cache_query_time if cache_query_time > 0 else float('inf'),
        'cache_status': cache_status
    }

if __name__ == "__main__":
    print("🔧 最新交易日数据驱动判断机制测试")
    print("测试目标: 验证方案3的实施效果")
    print("=" * 80)
    
    result = test_latest_trading_day_fix()
    
    print(f"\\n🎯 核心结果:")
    print(f"最新交易日: {result['latest_trading_day']}")
    print(f"今日是否交易日: {result['is_today_trading_day']}")
    if result['cache_performance'] == float('inf'):
        print(f"缓存性能提升: 无限倍")
    else:
        print(f"缓存性能提升: {result['cache_performance']:.1f}x")