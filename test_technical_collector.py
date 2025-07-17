#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试技术指标采集器
验证TechnicalCollector是否能正确获取技术指标数据
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.concept.technical_collector import TechnicalCollector
from utils.logger import setup_logger

# 设置日志
logger = setup_logger('test_technical_collector')

def test_technical_collector():
    """测试技术指标采集功能"""
    print("\n=== 测试技术指标采集器 ===\n")
    
    try:
        # 初始化采集器
        collector = TechnicalCollector()
        print("✓ 技术指标采集器初始化成功")
        
        # 测试股票列表
        test_stocks = [
            "600519.SH",  # 贵州茅台
            "000858.SZ",  # 五粮液
            "300750.SZ",  # 宁德时代
        ]
        
        print(f"\n开始测试{len(test_stocks)}只股票的技术指标获取...")
        
        # 获取技术指标
        results = collector.get_latest_technical_indicators(test_stocks, days=21)
        
        # 打印结果
        success_count = 0
        for ts_code in test_stocks:
            print(f"\n{'='*50}")
            print(f"股票代码: {ts_code}")
            
            if ts_code in results:
                data = results[ts_code]
                
                if data['trade_date']:  # 有有效数据
                    success_count += 1
                    print(f"✓ 数据获取成功")
                    print(f"  交易日期: {data['trade_date']}")
                    print(f"  收盘价: {data['close']:.2f}")
                    print(f"  MACD指标:")
                    print(f"    - MACD: {data['macd']:.3f}")
                    print(f"    - DIF: {data['macd_dif']:.3f}")
                    print(f"    - DEA: {data['macd_dea']:.3f}")
                    print(f"    - MACD水上: {'是' if data['macd_above_water'] else '否'}")
                    print(f"  均线指标:")
                    print(f"    - MA5: {data['ma5']:.2f}")
                    print(f"    - MA10: {data['ma10']:.2f}")
                    print(f"    - 均线多头: {'是' if data['ma_bullish'] else '否'}")
                else:
                    print("✗ 获取失败：无有效数据")
            else:
                print("✗ 获取失败：无返回结果")
        
        print(f"\n{'='*50}")
        print(f"测试完成！成功率: {success_count}/{len(test_stocks)}")
        
        # 测试缓存功能
        print("\n\n=== 测试缓存功能 ===")
        print("再次获取相同股票数据（应该从缓存读取）...")
        
        import time
        start_time = time.time()
        results2 = collector.get_latest_technical_indicators(test_stocks[:1], days=21)
        elapsed = time.time() - start_time
        
        print(f"获取{test_stocks[0]}数据耗时: {elapsed:.3f}秒")
        if elapsed < 0.1:
            print("✓ 缓存功能正常（读取速度快）")
        else:
            print("⚠ 可能未使用缓存（读取速度慢）")
        
        return success_count == len(test_stocks)
        
    except Exception as e:
        print(f"\n✗ 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_edge_cases():
    """测试边界情况"""
    print("\n\n=== 测试边界情况 ===")
    
    collector = TechnicalCollector()
    
    # 测试无效股票代码
    print("\n1. 测试无效股票代码...")
    results = collector.get_latest_technical_indicators(["999999.SH"], days=21)
    
    if "999999.SH" in results:
        data = results["999999.SH"]
        if not data['trade_date']:
            print("✓ 正确处理无效股票代码（返回空数据）")
        else:
            print("✗ 无效股票代码处理异常")
    
    # 测试空列表
    print("\n2. 测试空列表...")
    results = collector.get_latest_technical_indicators([], days=21)
    if len(results) == 0:
        print("✓ 正确处理空列表")
    else:
        print("✗ 空列表处理异常")
    
    print("\n边界测试完成！")


if __name__ == "__main__":
    # 运行测试
    print("开始测试TechnicalCollector...")
    
    # 基础功能测试
    basic_test_passed = test_technical_collector()
    
    # 边界情况测试
    test_edge_cases()
    
    # 总结
    print("\n\n=== 测试总结 ===")
    if basic_test_passed:
        print("✓ 技术指标采集器测试通过！可以继续开发ConceptScorer。")
    else:
        print("✗ 技术指标采集器存在问题，需要修复。")