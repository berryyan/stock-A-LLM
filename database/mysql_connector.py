"""
MySQL数据库连接器
"""
from typing import List, Dict, Any, Optional
import pandas as pd
from sqlalchemy import create_engine, text, Engine
from sqlalchemy.pool import QueuePool
import logging

from config.settings import settings
from utils.logger import setup_logger


class MySQLConnector:
    """MySQL数据库连接器"""
    
    def __init__(self):
        self.logger = setup_logger("mysql_connector")
        self.engine = self._create_engine()
        self.logger.info("MySQL连接器初始化完成")
    
    def _create_engine(self) -> Engine:
        """创建数据库引擎"""
        try:
            engine = create_engine(
                settings.MYSQL_URL,
                poolclass=QueuePool,
                pool_size=settings.DB_POOL_SIZE,
                max_overflow=settings.DB_MAX_OVERFLOW,
                pool_timeout=settings.DB_POOL_TIMEOUT,
                pool_recycle=3600,  # 1小时回收连接
                echo=False  # 不打印SQL语句
            )
            # 测试连接
            with engine.connect() as conn:
                result = conn.execute(text("SELECT 1"))
                result.fetchone()
            
            self.logger.info(f"MySQL连接成功: {settings.MYSQL_HOST}:{settings.MYSQL_PORT}/{settings.MYSQL_DATABASE}")
            return engine
            
        except Exception as e:
            self.logger.error(f"MySQL连接失败: {e}")
            raise
    
    def execute_query(self, query: str, params: Optional[Dict] = None) -> List[Dict[str, Any]]:
        """
        执行查询并返回结果
        
        Args:
            query: SQL查询语句
            params: 查询参数（可选）
            
        Returns:
            查询结果列表，每个元素是一个字典
        """
        try:
            with self.engine.connect() as conn:
                # 使用text()包装查询，避免格式化问题
                if params:
                    result = conn.execute(text(query), params)
                else:
                    result = conn.execute(text(query))
                
                # 获取列名
                columns = result.keys()
                
                # 转换为字典列表
                rows = []
                for row in result:
                    rows.append(dict(zip(columns, row)))
                
                self.logger.debug(f"查询执行成功，返回 {len(rows)} 条记录")
                return rows
                
        except Exception as e:
            self.logger.error(f"查询执行失败: {e}")
            self.logger.error(f"查询语句: {query}")
            raise
    
    def execute_query_df(self, query: str, params: Optional[Dict] = None) -> pd.DataFrame:
        """
        执行查询并返回DataFrame
        
        Args:
            query: SQL查询语句
            params: 查询参数（可选）
            
        Returns:
            查询结果DataFrame
        """
        try:
            with self.engine.connect() as conn:
                if params:
                    df = pd.read_sql(text(query), conn, params=params)
                else:
                    df = pd.read_sql(text(query), conn)
                
                self.logger.debug(f"查询执行成功，返回 {len(df)} 条记录")
                return df
                
        except Exception as e:
            self.logger.error(f"查询执行失败: {e}")
            self.logger.error(f"查询语句: {query}")
            raise
    
    def get_table_info(self, table_name: str) -> Dict[str, Any]:
        """
        获取表信息
        
        Args:
            table_name: 表名
            
        Returns:
            表信息字典
        """
        try:
            # 获取表结构
            query = f"""
            SELECT 
                COLUMN_NAME,
                DATA_TYPE,
                IS_NULLABLE,
                COLUMN_DEFAULT,
                COLUMN_COMMENT
            FROM INFORMATION_SCHEMA.COLUMNS
            WHERE TABLE_SCHEMA = '{settings.MYSQL_DATABASE}'
            AND TABLE_NAME = '{table_name}'
            ORDER BY ORDINAL_POSITION
            """
            
            columns = self.execute_query(query)
            
            # 获取表行数
            count_query = f"SELECT COUNT(*) as count FROM {table_name}"
            count_result = self.execute_query(count_query)
            row_count = count_result[0]['count'] if count_result else 0
            
            return {
                'table_name': table_name,
                'columns': columns,
                'row_count': row_count
            }
            
        except Exception as e:
            self.logger.error(f"获取表信息失败: {e}")
            raise
    
    def test_connection(self) -> bool:
        """测试数据库连接"""
        try:
            with self.engine.connect() as conn:
                result = conn.execute(text("SELECT 1"))
                result.fetchone()
            return True
        except Exception as e:
            self.logger.error(f"连接测试失败: {e}")
            return False
    
    def close(self):
        """关闭连接池"""
        self.engine.dispose()
        self.logger.info("MySQL连接池已关闭")
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


# 使用示例
if __name__ == "__main__":
    # 测试连接
    with MySQLConnector() as mysql:
        # 测试基本查询
        print("测试基本查询...")
        result = mysql.execute_query("SELECT DATABASE()")
        print(f"当前数据库: {result}")
        
        # 测试表信息
        print("\n获取表信息...")
        table_info = mysql.get_table_info("tu_anns_d")
        print(f"表名: {table_info['table_name']}")
        print(f"行数: {table_info['row_count']}")
        print(f"列数: {len(table_info['columns'])}")
        
        # 测试带参数的查询
        print("\n测试参数化查询...")
        query = """
        SELECT ts_code, name, title 
        FROM tu_anns_d 
        WHERE ann_date = :ann_date
        LIMIT 5
        """
        results = mysql.execute_query(query, {'ann_date': '20250422'})
        for r in results:
            print(f"{r['ts_code']} - {r['name']} - {r['title']}")
