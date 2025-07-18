#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
修复数据源查询逻辑
测试正确的查询方法
"""

import logging
import sys
import pandas as pd

# 添加项目根目录到系统路径
sys.path.insert(0, '/mnt/e/PycharmProjects/stock_analysis_system')

from database.mysql_connector import MySQLConnector

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def test_dc_query_fix(mysql: MySQLConnector):
    """测试东财查询修复"""
    logger.info("\n=== 测试东财查询修复 ===")
    
    # 先获取最新交易日
    latest_date_query = "SELECT MAX(trade_date) as latest_date FROM tu_dc_member"
    result = mysql.execute_query(latest_date_query)
    latest_date = result[0]['latest_date'] if result else '20250717'
    logger.info(f"东财最新交易日: {latest_date}")
    
    # 1. 先查看有哪些板块名称包含"储能"
    index_query = """
    SELECT DISTINCT ts_code, name
    FROM tu_dc_index
    WHERE name LIKE '%储能%'
    GROUP BY ts_code, name
    LIMIT 10
    """
    
    indexes = mysql.execute_query(index_query)
    logger.info(f"\n包含'储能'的板块: {len(indexes)}个")
    for idx in indexes[:5]:
        logger.info(f"  {idx['ts_code']}: {idx['name']}")
    
    # 2. 使用正确的方式查询成分股
    if indexes:
        # 选择第一个板块作为测试
        test_code = indexes[0]['ts_code']
        test_name = indexes[0]['name']
        
        member_query = """
        SELECT DISTINCT con_code, name
        FROM tu_dc_member
        WHERE trade_date = :trade_date
        AND ts_code = :ts_code
        LIMIT 20
        """
        
        members = mysql.execute_query(member_query, {'trade_date': latest_date, 'ts_code': test_code})
        logger.info(f"\n{test_name}({test_code})的成分股: {len(members)}只")
        for i, member in enumerate(members[:5], 1):
            logger.info(f"  {i}. {member['name']} ({member['con_code']})")
    
    # 3. 统计各板块的成分股数量
    count_query = """
    SELECT ts_code, COUNT(DISTINCT con_code) as stock_count
    FROM tu_dc_member
    WHERE trade_date = :trade_date
    AND ts_code IN (
        SELECT DISTINCT ts_code 
        FROM tu_dc_index 
        WHERE name LIKE '%储能%'
    )
    GROUP BY ts_code
    """
    
    counts = mysql.execute_query(count_query, {'trade_date': latest_date})
    if counts:
        logger.info("\n储能相关板块成分股数量:")
        for cnt in counts[:5]:
            logger.info(f"  {cnt['ts_code']}: {cnt['stock_count']}只")


def test_kpl_query_fix(mysql: MySQLConnector):
    """测试开盘啦查询修复"""
    logger.info("\n=== 测试开盘啦查询修复 ===")
    
    # 获取最新交易日
    latest_date_query = "SELECT MAX(trade_date) as latest_date FROM tu_kpl_concept_cons"
    result = mysql.execute_query(latest_date_query)
    latest_date = result[0]['latest_date'] if result else '20250716'
    logger.info(f"开盘啦最新交易日: {latest_date}")
    
    # 1. 查看包含"储能"的概念
    concept_query = """
    SELECT DISTINCT ts_code, name
    FROM tu_kpl_concept_cons
    WHERE name LIKE '%储能%'
    AND trade_date = :trade_date
    GROUP BY ts_code, name
    LIMIT 10
    """
    
    concepts = mysql.execute_query(concept_query, {'trade_date': latest_date})
    logger.info(f"\n包含'储能'的概念: {len(concepts)}个")
    for concept in concepts[:5]:
        logger.info(f"  {concept['ts_code']}: {concept['name']}")
    
    # 2. 查询某个概念的成分股
    if concepts:
        test_code = concepts[0]['ts_code']
        test_name = concepts[0]['name']
        
        member_query = """
        SELECT DISTINCT con_code, con_name
        FROM tu_kpl_concept_cons
        WHERE trade_date = :trade_date
        AND ts_code = :ts_code
        AND name = :name
        LIMIT 20
        """
        
        members = mysql.execute_query(member_query, {'trade_date': latest_date, 'ts_code': test_code, 'name': test_name})
        logger.info(f"\n{test_name}({test_code})的成分股: {len(members)}只")
        for i, member in enumerate(members[:5], 1):
            logger.info(f"  {i}. {member['con_name']} ({member['con_code']})")
    
    # 3. 查看所有概念名称（用于发现命名规律）
    all_concepts_query = """
    SELECT DISTINCT name, COUNT(DISTINCT con_code) as stock_count
    FROM tu_kpl_concept_cons
    WHERE trade_date = :trade_date
    GROUP BY name
    ORDER BY stock_count DESC
    LIMIT 30
    """
    
    all_concepts = mysql.execute_query(all_concepts_query, {'trade_date': latest_date})
    logger.info("\n开盘啦热门概念TOP30:")
    for i, concept in enumerate(all_concepts[:10], 1):
        logger.info(f"  {i}. {concept['name']} ({concept['stock_count']}只股票)")


def suggest_fix_strategy():
    """建议修复策略"""
    logger.info("\n=== 修复策略建议 ===")
    
    logger.info("\n1. 东财修复方案:")
    logger.info("   - 使用tu_dc_member表获取成分股")
    logger.info("   - 先从tu_dc_index找到板块代码")
    logger.info("   - 再用板块代码查询成分股")
    logger.info("   - 注意：东财是'板块'概念，不是'概念股'")
    
    logger.info("\n2. 开盘啦修复方案:")
    logger.info("   - 使用tu_kpl_concept_cons表")
    logger.info("   - 直接通过name字段匹配概念")
    logger.info("   - 注意：需要指定trade_date")
    
    logger.info("\n3. 概念名称映射:")
    logger.info("   - 同花顺：'储能'")
    logger.info("   - 东财：'储能'（板块）")
    logger.info("   - 开盘啦：'储能概念'或其他变体")
    logger.info("   - 建议：建立概念名称映射表")


def main():
    """主函数"""
    mysql = MySQLConnector()
    
    try:
        # 测试修复后的查询
        test_dc_query_fix(mysql)
        test_kpl_query_fix(mysql)
        
        # 建议修复策略
        suggest_fix_strategy()
        
    except Exception as e:
        logger.error(f"测试失败: {e}", exc_info=True)
    finally:
        mysql.close()


if __name__ == "__main__":
    main()