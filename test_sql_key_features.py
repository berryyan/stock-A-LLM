#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
SQL Agent关键功能测试
测试快速模板和日期解析的核心功能
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import time
from agents.sql_agent import SQLAgent
from utils.logger import setup_logger

logger = setup_logger("test_sql_key")

def test_key_features():
    """测试关键功能"""
    sql_agent = SQLAgent()
    
    # 关键测试用例
    test_cases = [
        # 日期解析测试
        ("贵州茅台最新股价", "测试最新->日期转换"),
        ("贵州茅台昨天的股价", "测试昨天->日期转换"),
        ("平安银行20250627的股价", "测试YYYYMMDD格式"),
        ("中国平安2025-06-27的股价", "测试YYYY-MM-DD格式"),
        ("格力电器2025年06月27日的股价", "测试中文日期格式"),
        
        # 排名查询测试
        ("今天涨幅前10", "测试涨幅排名"),
        ("昨天跌幅最大的10只股票", "测试跌幅排名"),
        ("20250627总市值排名前5", "测试市值排名+日期"),
        
        # 股票简称验证
        ("茅台最新股价", "测试股票简称提示"),
        ("平安的市盈率", "测试股票简称提示2"),
    ]
    
    results = []
    
    for query, description in test_cases:
        logger.info(f"\n{'='*60}")
        logger.info(f"测试: {description}")
        logger.info(f"查询: {query}")
        
        start_time = time.time()
        
        try:
            result = sql_agent.query(query)
            elapsed_time = time.time() - start_time
            
            test_result = {
                'query': query,
                'description': description,
                'success': result.get('success', False),
                'quick_path': result.get('quick_path', False),
                'elapsed_time': elapsed_time,
                'error': result.get('error')
            }
            
            logger.info(f"成功: {result.get('success')}")
            logger.info(f"快速路径: {result.get('quick_path', False)}")
            logger.info(f"耗时: {elapsed_time:.2f}秒")
            
            if result.get('success'):
                if result.get('result'):
                    # 只显示结果的前100个字符
                    logger.info(f"结果预览: {str(result['result'])[:100]}...")
            else:
                logger.info(f"错误: {result.get('error')}")
            
            results.append(test_result)
            
        except Exception as e:
            logger.error(f"异常: {str(e)}")
            results.append({
                'query': query,
                'description': description,
                'success': False,
                'error': str(e),
                'elapsed_time': time.time() - start_time
            })
        
        # 避免请求过快
        time.sleep(0.5)
    
    # 生成报告
    logger.info(f"\n\n{'='*60}")
    logger.info("测试报告总结")
    logger.info(f"{'='*60}")
    
    total = len(results)
    passed = sum(1 for r in results if r['success'])
    quick_path_count = sum(1 for r in results if r.get('quick_path', False))
    
    logger.info(f"总测试数: {total}")
    logger.info(f"成功: {passed}")
    logger.info(f"失败: {total - passed}")
    logger.info(f"快速路径使用: {quick_path_count}")
    logger.info(f"成功率: {passed/total*100:.1f}%")
    
    # 失败案例分析
    failed = [r for r in results if not r['success']]
    if failed:
        logger.info("\n失败案例:")
        for f in failed:
            logger.info(f"- {f['description']}: {f.get('error', 'Unknown error')}")
    
    # 性能分析
    avg_time = sum(r['elapsed_time'] for r in results) / len(results)
    logger.info(f"\n平均响应时间: {avg_time:.2f}秒")
    
    # 快速路径分析
    quick_results = [r for r in results if r.get('quick_path', False)]
    if quick_results:
        avg_quick = sum(r['elapsed_time'] for r in quick_results) / len(quick_results)
        logger.info(f"快速路径平均时间: {avg_quick:.2f}秒")


if __name__ == "__main__":
    logger.info("开始SQL Agent关键功能测试")
    test_key_features()
    logger.info("\n测试完成！")