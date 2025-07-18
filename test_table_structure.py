#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
查看数据表结构
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


def check_table_structure(mysql: MySQLConnector, table_name: str):
    """查看表结构"""
    logger.info(f"\n=== {table_name} 表结构 ===")
    
    query = f"DESCRIBE {table_name}"
    try:
        columns = mysql.execute_query(query)
        logger.info(f"字段列表:")
        for col in columns:
            logger.info(f"  {col['Field']} - {col['Type']} - {col['Null']}")
    except Exception as e:
        logger.error(f"查询表结构失败: {e}")


def check_sample_data(mysql: MySQLConnector, table_name: str, limit: int = 3):
    """查看样例数据"""
    logger.info(f"\n=== {table_name} 样例数据 ===")
    
    query = f"SELECT * FROM {table_name} LIMIT {limit}"
    try:
        data = mysql.execute_query(query)
        if data:
            logger.info(f"找到 {len(data)} 条记录")
            for i, row in enumerate(data, 1):
                logger.info(f"\n记录 {i}:")
                for key, value in row.items():
                    logger.info(f"  {key}: {value}")
        else:
            logger.info("表中无数据")
    except Exception as e:
        logger.error(f"查询样例数据失败: {e}")


def main():
    """主函数"""
    mysql = MySQLConnector()
    
    try:
        # 检查三个数据源的表结构
        tables = [
            'tu_ths_index',      # 同花顺概念
            'tu_ths_member',     # 同花顺成分股
            'tu_dc_index',       # 东财板块
            'tu_dc_member',      # 东财成分股
            'tu_kpl_concept_list',  # 开盘啦题材
            'tu_kpl_concept_cons'   # 开盘啦成分股
        ]
        
        for table in tables:
            check_table_structure(mysql, table)
            check_sample_data(mysql, table)
            
    except Exception as e:
        logger.error(f"检查失败: {e}", exc_info=True)
    finally:
        mysql.close()


if __name__ == "__main__":
    main()