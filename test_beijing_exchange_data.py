#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试北交所股票资金流向数据是否存在
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database.mysql_connector import MySQLConnector
from utils.logger import setup_logger

def test_beijing_exchange_data():
    """测试北交所股票数据"""
    logger = setup_logger("test_beijing_exchange")
    mysql = MySQLConnector()
    
    try:
        # 1. 检查tu_stock_basic表中的北交所股票数量
        sql1 = """
        SELECT COUNT(*) as count 
        FROM tu_stock_basic 
        WHERE ts_code LIKE '%.BJ'
        """
        result1 = mysql.execute_query(sql1)
        bj_stock_count = result1[0]['count'] if result1 else 0
        logger.info(f"tu_stock_basic表中北交所股票数量: {bj_stock_count}")
        
        # 2. 检查tu_moneyflow_dc表中是否有北交所股票的资金流向数据
        sql2 = """
        SELECT COUNT(DISTINCT m.ts_code) as count 
        FROM tu_moneyflow_dc m
        WHERE m.ts_code LIKE '%.BJ'
        """
        result2 = mysql.execute_query(sql2)
        bj_moneyflow_count = result2[0]['count'] if result2 else 0
        logger.info(f"tu_moneyflow_dc表中有资金流向数据的北交所股票数量: {bj_moneyflow_count}")
        
        # 3. 检查最新交易日的北交所股票资金流向数据
        sql3 = """
        SELECT trade_date 
        FROM tu_moneyflow_dc 
        ORDER BY trade_date DESC 
        LIMIT 1
        """
        result3 = mysql.execute_query(sql3)
        latest_date = result3[0]['trade_date'] if result3 else None
        
        if latest_date:
            sql4 = f"""
            SELECT ts_code, name, net_amount, trade_date
            FROM tu_moneyflow_dc
            WHERE ts_code LIKE '%.BJ' 
                AND trade_date = '{latest_date}'
            ORDER BY net_amount DESC
            LIMIT 10
            """
            result4 = mysql.execute_query(sql4)
            
            if result4:
                logger.info(f"\n{latest_date}北交所股票资金流向数据示例:")
                for row in result4:
                    logger.info(f"  {row['ts_code']} {row['name']}: {row['net_amount']/10000:.2f}万元")
            else:
                logger.warning(f"{latest_date}没有北交所股票的资金流向数据")
                
        # 4. 检查831689.BJ具体情况
        sql5 = """
        SELECT * FROM tu_stock_basic 
        WHERE ts_code = '831689.BJ'
        """
        result5 = mysql.execute_query(sql5)
        if result5:
            logger.info(f"\n831689.BJ股票信息: {result5[0]}")
            
            # 检查该股票是否有资金流向数据
            sql6 = """
            SELECT COUNT(*) as count 
            FROM tu_moneyflow_dc 
            WHERE ts_code = '831689.BJ'
            """
            result6 = mysql.execute_query(sql6)
            data_count = result6[0]['count'] if result6 else 0
            logger.info(f"831689.BJ在tu_moneyflow_dc表中的记录数: {data_count}")
        else:
            logger.warning("未找到831689.BJ股票信息")
            
    except Exception as e:
        logger.error(f"测试失败: {e}")
    finally:
        mysql.close()

if __name__ == "__main__":
    test_beijing_exchange_data()