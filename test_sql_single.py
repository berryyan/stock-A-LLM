#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
单个SQL Agent测试 - 验证基本功能
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.sql_agent import SQLAgent
from utils.logger import setup_logger

logger = setup_logger("test_sql_single")

def test_single_query():
    """测试单个查询"""
    sql_agent = SQLAgent()
    
    # 测试查询
    queries = [
        "贵州茅台最新股价",
        "贵州茅台20250627的股价",
        "茅台最新股价",  # 预期股票简称错误
    ]
    
    for query in queries:
        logger.info(f"\n{'='*60}")
        logger.info(f"测试查询: {query}")
        
        try:
            result = sql_agent.query(query)
            
            logger.info(f"成功: {result.get('success')}")
            logger.info(f"快速路径: {result.get('quick_path', False)}")
            logger.info(f"缓存: {result.get('cached', False)}")
            
            if result.get('success'):
                if result.get('result'):
                    logger.info(f"结果:\n{result['result'][:300]}...")
                if result.get('sql'):
                    logger.info(f"SQL: {result['sql'][:100]}...")
            else:
                logger.info(f"错误: {result.get('error')}")
                
        except Exception as e:
            logger.error(f"异常: {str(e)}")


if __name__ == "__main__":
    logger.info("开始单个SQL Agent测试")
    test_single_query()
    logger.info("\n测试完成！")