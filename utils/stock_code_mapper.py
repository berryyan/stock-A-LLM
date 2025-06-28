# 文件路径: E:\PycharmProjects\stock_analysis_system\utils\stock_code_mapper.py

"""
股票代码映射工具
实现股票名称、股票代码到证券代码(ts_code)的统一映射
使用缓存+数据库的方案，提高查询效率
"""

import sys
import os
import re
from typing import Optional, Dict, Set
from datetime import datetime, timedelta
import threading
from functools import lru_cache

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.mysql_connector import MySQLConnector
from utils.logger import setup_logger


class StockCodeMapper:
    """股票代码映射器 - 统一转换为ts_code"""
    
    def __init__(self, cache_ttl_minutes: int = 60):
        """
        初始化映射器
        
        Args:
            cache_ttl_minutes: 缓存过期时间（分钟）
        """
        self.logger = setup_logger("stock_code_mapper")
        self.mysql = MySQLConnector()
        self.cache_ttl = timedelta(minutes=cache_ttl_minutes)
        
        # 缓存数据
        self._cache: Dict[str, str] = {}
        self._reverse_cache: Dict[str, str] = {}  # ts_code -> name的反向映射
        self._cache_time: Optional[datetime] = None
        self._cache_lock = threading.Lock()
        
        # 预加载缓存
        self._refresh_cache()
        
    def _refresh_cache(self) -> None:
        """刷新缓存数据"""
        try:
            self.logger.info("开始刷新股票代码缓存")
            
            # 查询所有股票基础信息
            query = """
            SELECT ts_code, symbol, name 
            FROM tu_stock_basic 
            WHERE list_status = 'L'  -- 只查询上市股票
            """
            
            results = self.mysql.execute_query(query)
            
            if not results:
                self.logger.warning("未能获取股票基础数据")
                return
                
            # 构建映射缓存
            new_cache = {}
            new_reverse_cache = {}
            
            for row in results:
                ts_code = row['ts_code']
                symbol = row['symbol']
                name = row['name']
                
                # 构建反向映射（ts_code -> name）
                if name:
                    new_reverse_cache[ts_code] = name
                
                # ts_code映射到自己
                new_cache[ts_code.lower()] = ts_code
                new_cache[ts_code.upper()] = ts_code
                
                # symbol映射到ts_code
                if symbol:
                    new_cache[symbol.lower()] = ts_code
                    new_cache[symbol.upper()] = ts_code
                    
                # name映射到ts_code（精确匹配）
                if name:
                    new_cache[name] = ts_code
                    # 处理常见简称
                    # 去除"股份有限公司"等后缀
                    short_name = name.replace('股份有限公司', '').replace('有限公司', '').replace('集团', '').replace('股份', '')
                    if short_name != name:
                        new_cache[short_name] = ts_code
                    
                    # 注意：不再支持简称映射，用户必须使用完整股票名称
                    # 这是为了避免歧义和错误匹配
                    # 例如："茅台"可能指"贵州茅台"也可能指其他含"茅台"的公司
            
            # 原子性更新缓存
            with self._cache_lock:
                self._cache = new_cache
                self._reverse_cache = new_reverse_cache
                self._cache_time = datetime.now()
                
            self.logger.info(f"股票代码缓存刷新完成，共缓存{len(self._cache)}个映射")
            
        except Exception as e:
            self.logger.error(f"刷新缓存失败: {e}")
    
    def _is_cache_expired(self) -> bool:
        """检查缓存是否过期"""
        if not self._cache_time:
            return True
        return datetime.now() - self._cache_time > self.cache_ttl
    
    def convert_to_ts_code(self, entity: str) -> Optional[str]:
        """
        将实体（股票名称、股票代码）转换为证券代码(ts_code)
        
        Args:
            entity: 股票名称或代码
            
        Returns:
            ts_code格式的证券代码，如果无法转换则返回None
        """
        if not entity:
            return None
            
        # 清理输入
        entity = entity.strip()
        
        # 检查是否已经是ts_code格式 (XXXXXX.SH/SZ)
        if re.match(r'^\d{6}\.[A-Z]{2}$', entity.upper()):
            return entity.upper()
        
        # 检查并刷新缓存
        if self._is_cache_expired():
            self._refresh_cache()
        
        # 从缓存查找
        with self._cache_lock:
            # 尝试直接匹配
            result = self._cache.get(entity)
            if result:
                return result
                
            # 尝试大小写变体
            result = self._cache.get(entity.lower())
            if result:
                return result
                
            result = self._cache.get(entity.upper())
            if result:
                return result
        
        # 如果是纯数字（可能是symbol），尝试数据库查询
        if entity.isdigit() and len(entity) == 6:
            return self._query_by_symbol(entity)
        
        # 缓存未命中，记录日志
        self.logger.warning(f"无法转换实体到ts_code: {entity}")
        return None
    
    def _query_by_symbol(self, symbol: str) -> Optional[str]:
        """通过symbol查询ts_code"""
        try:
            query = """
            SELECT ts_code 
            FROM tu_stock_basic 
            WHERE symbol = %s AND list_status = 'L'
            LIMIT 1
            """
            results = self.mysql.execute_query(query, (symbol,))
            
            if results and len(results) > 0:
                ts_code = results[0]['ts_code']
                # 更新缓存
                with self._cache_lock:
                    self._cache[symbol] = ts_code
                return ts_code
                
        except Exception as e:
            self.logger.error(f"查询symbol失败: {e}")
            
        return None
    
    def batch_convert(self, entities: list) -> Dict[str, Optional[str]]:
        """
        批量转换实体到ts_code
        
        Args:
            entities: 实体列表
            
        Returns:
            {entity: ts_code} 的映射字典
        """
        results = {}
        for entity in entities:
            results[entity] = self.convert_to_ts_code(entity)
        return results
    
    def get_cache_stats(self) -> Dict[str, any]:
        """获取缓存统计信息"""
        with self._cache_lock:
            return {
                'cache_size': len(self._cache),
                'cache_time': self._cache_time.isoformat() if self._cache_time else None,
                'is_expired': self._is_cache_expired()
            }
    
    def force_refresh(self) -> None:
        """强制刷新缓存"""
        self._refresh_cache()
    
    def get_stock_name(self, ts_code: str) -> str:
        """
        根据ts_code获取股票名称
        
        Args:
            ts_code: 证券代码（如600519.SH）
            
        Returns:
            股票名称，如果找不到则返回ts_code本身
        """
        if not ts_code:
            return ts_code
            
        # 检查并刷新缓存
        if self._is_cache_expired():
            self._refresh_cache()
            
        # 从反向缓存查找
        with self._cache_lock:
            return self._reverse_cache.get(ts_code, ts_code)


# 单例实例
_mapper_instance = None
_mapper_lock = threading.Lock()


def get_stock_mapper() -> StockCodeMapper:
    """获取股票代码映射器的单例实例"""
    global _mapper_instance
    
    if _mapper_instance is None:
        with _mapper_lock:
            if _mapper_instance is None:
                _mapper_instance = StockCodeMapper()
                
    return _mapper_instance


# 便捷函数
@lru_cache(maxsize=1000)
def convert_to_ts_code(entity: str) -> Optional[str]:
    """
    便捷函数：转换实体到ts_code
    使用LRU缓存进一步提升性能
    """
    mapper = get_stock_mapper()
    return mapper.convert_to_ts_code(entity)


@lru_cache(maxsize=1000)
def get_stock_name(ts_code: str) -> str:
    """
    便捷函数：根据ts_code获取股票名称
    使用LRU缓存进一步提升性能
    """
    mapper = get_stock_mapper()
    return mapper.get_stock_name(ts_code)


if __name__ == "__main__":
    # 测试代码
    mapper = get_stock_mapper()
    
    test_cases = [
        "600519",
        "600519.SH", 
        "贵州茅台",
        "茅台",
        "000858",
        "五粮液",
        "诺德股份",
        "600110",
        "600110.SH"
    ]
    
    print("股票代码映射测试:")
    for test in test_cases:
        result = mapper.convert_to_ts_code(test)
        print(f"{test:20} -> {result}")
    
    print("\n缓存统计:")
    print(mapper.get_cache_stats())