#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试SQL Agent快速模板功能
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.sql_agent import SQLAgent
from utils.logger import setup_logger
import time

logger = setup_logger("test_sql_templates")

def test_sql_quick_templates():
    """测试SQL快速模板"""
    sql_agent = SQLAgent()
    
    # 测试用例
    test_cases = [
        # 基础股价查询
        ("贵州茅台最新股价", "最新股价查询"),
        ("贵州茅台今天的价格", "今日股价查询"),
        
        # 估值指标查询
        ("中国平安的市盈率", "估值指标查询"),
        ("贵州茅台的PE和PB", "估值指标查询"),
        
        # 排名查询
        ("今天涨幅最大的前10只股票", "涨幅排名"),
        ("总市值最大的前20只股票", "总市值排名"),
        ("流通市值排名前10", "流通市值排名"),
        
        # 历史K线查询
        ("贵州茅台最近90天的K线走势", "历史K线查询"),
        ("平安银行过去30天的股价走势", "历史K线查询"),
    ]
    
    results = []
    
    for query, expected_template in test_cases:
        logger.info(f"\n{'='*60}")
        logger.info(f"测试查询: {query}")
        logger.info(f"期望模板: {expected_template}")
        
        start_time = time.time()
        result = sql_agent.query(query)
        end_time = time.time()
        
        elapsed_time = end_time - start_time
        
        if result['success']:
            # 检查是否使用了快速路径
            quick_path = result.get('quick_path', False)
            cached = result.get('cached', False)
            
            logger.info(f"查询成功! 耗时: {elapsed_time:.2f}秒")
            logger.info(f"使用快速路径: {quick_path}")
            logger.info(f"使用缓存: {cached}")
            
            # 打印部分结果
            result_preview = result['result'][:200] if len(result['result']) > 200 else result['result']
            logger.info(f"结果预览:\n{result_preview}")
            
            if result.get('sql'):
                logger.info(f"执行的SQL: {result['sql'][:100]}...")
                
            results.append({
                'query': query,
                'template': expected_template,
                'success': True,
                'quick_path': quick_path,
                'cached': cached,
                'time': elapsed_time
            })
        else:
            logger.error(f"查询失败: {result.get('error', '未知错误')}")
            results.append({
                'query': query,
                'template': expected_template,
                'success': False,
                'error': result.get('error'),
                'time': elapsed_time
            })
    
    # 统计结果
    logger.info(f"\n{'='*60}")
    logger.info("测试统计:")
    logger.info(f"总测试数: {len(results)}")
    
    success_count = sum(1 for r in results if r['success'])
    logger.info(f"成功数: {success_count}")
    
    quick_path_count = sum(1 for r in results if r.get('quick_path', False))
    logger.info(f"使用快速路径: {quick_path_count}")
    
    cached_count = sum(1 for r in results if r.get('cached', False))
    logger.info(f"使用缓存: {cached_count}")
    
    # 计算平均响应时间
    quick_times = [r['time'] for r in results if r.get('quick_path', False)]
    if quick_times:
        avg_quick_time = sum(quick_times) / len(quick_times)
        logger.info(f"快速路径平均响应时间: {avg_quick_time:.2f}秒")
    
    non_quick_times = [r['time'] for r in results if r['success'] and not r.get('quick_path', False) and not r.get('cached', False)]
    if non_quick_times:
        avg_non_quick_time = sum(non_quick_times) / len(non_quick_times)
        logger.info(f"非快速路径平均响应时间: {avg_non_quick_time:.2f}秒")
        
        if quick_times:
            speedup = avg_non_quick_time / avg_quick_time
            logger.info(f"快速路径加速比: {speedup:.1f}x")

if __name__ == "__main__":
    test_sql_quick_templates()