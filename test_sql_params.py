#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试SQL参数传递是否正常
"""

import logging
import sys

# 添加项目根目录到系统路径
sys.path.insert(0, '/mnt/e/PycharmProjects/stock_analysis_system')

from database.mysql_connector import MySQLConnector

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def test_named_params():
    """测试命名参数"""
    logger.info("=== 测试命名参数 ===")
    
    db = MySQLConnector()
    
    # 测试1: 简单查询
    query = """
    SELECT ts_code, name 
    FROM tu_stock_basic 
    WHERE ts_code = :ts_code
    LIMIT 1
    """
    
    try:
        result = db.execute_query(query, {'ts_code': '600519.SH'})
        if result:
            logger.info(f"查询成功: {result[0]['ts_code']} - {result[0]['name']}")
        else:
            logger.info("未找到数据")
    except Exception as e:
        logger.error(f"查询失败: {e}")
    
    # 测试2: LIKE查询
    query = """
    SELECT ts_code, q, a
    FROM tu_irm_qa_sh
    WHERE ts_code = :ts_code
    AND (q LIKE :pattern OR a LIKE :pattern)
    ORDER BY trade_date DESC
    LIMIT 2
    """
    
    try:
        result = db.execute_query(query, {
            'ts_code': '603421.SH',
            'pattern': '%储能%'
        })
        logger.info(f"找到 {len(result)} 条互动记录")
        for i, row in enumerate(result, 1):
            logger.info(f"  记录{i}: 问题长度={len(row['q'])}, 回答长度={len(row['a'])}")
    except Exception as e:
        logger.error(f"查询失败: {e}")
    
    # 测试3: 多个不同参数
    query = """
    SELECT ts_code, name
    FROM tu_stock_basic
    WHERE name LIKE :name_pattern
    AND ts_code LIKE :code_pattern
    LIMIT 5
    """
    
    try:
        result = db.execute_query(query, {
            'name_pattern': '%茅台%',
            'code_pattern': '600%'
        })
        logger.info(f"找到 {len(result)} 只股票:")
        for row in result:
            logger.info(f"  - {row['ts_code']} {row['name']}")
    except Exception as e:
        logger.error(f"查询失败: {e}")


def main():
    """主函数"""
    try:
        test_named_params()
        logger.info("\n测试完成!")
    except Exception as e:
        logger.error(f"测试失败: {e}", exc_info=True)


if __name__ == "__main__":
    main()