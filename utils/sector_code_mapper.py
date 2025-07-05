#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
板块代码映射工具
实现板块名称到板块代码(如BK1036.DC)的统一映射
"""

import sys
import os
from typing import Optional, Dict, List
from datetime import datetime, timedelta
import threading

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.mysql_connector import MySQLConnector
from utils.logger import setup_logger


class SectorCodeMapper:
    """板块代码映射器 - 统一转换为板块代码"""
    
    def __init__(self, cache_ttl_minutes: int = 60):
        """
        初始化映射器
        
        Args:
            cache_ttl_minutes: 缓存过期时间（分钟）
        """
        self.logger = setup_logger("sector_code_mapper")
        self.mysql = MySQLConnector()
        self.cache_ttl = timedelta(minutes=cache_ttl_minutes)
        
        # 缓存数据
        self._cache: Dict[str, str] = {}  # name -> ts_code
        self._reverse_cache: Dict[str, str] = {}  # ts_code -> name
        self._cache_time: Optional[datetime] = None
        self._cache_lock = threading.Lock()
        
        # 预加载缓存
        self._refresh_cache()
    
    def _refresh_cache(self) -> None:
        """刷新缓存数据"""
        try:
            self.logger.info("开始刷新板块代码缓存")
            
            # 查询所有板块信息
            query = """
            SELECT DISTINCT ts_code, name 
            FROM tu_moneyflow_ind_dc 
            WHERE content_type = '行业' 
            AND ts_code IS NOT NULL 
            AND name IS NOT NULL
            """
            
            result = self.mysql.execute_query(query)
            
            # 构建缓存
            new_cache = {}
            new_reverse_cache = {}
            
            for row in result:
                ts_code = row['ts_code']
                name = row['name']
                
                # 正向映射：名称 -> 代码
                new_cache[name] = ts_code
                
                # 反向映射：代码 -> 名称
                new_reverse_cache[ts_code] = name
            
            # 原子更新缓存
            with self._cache_lock:
                self._cache = new_cache
                self._reverse_cache = new_reverse_cache
                self._cache_time = datetime.now()
            
            self.logger.info(f"板块代码缓存刷新完成，共缓存{len(new_cache)}个板块映射")
            
        except Exception as e:
            self.logger.error(f"刷新板块缓存失败: {e}")
            # 保留旧缓存
    
    def _check_cache_validity(self) -> bool:
        """检查缓存是否有效"""
        if not self._cache_time:
            return False
        return datetime.now() - self._cache_time < self.cache_ttl
    
    def get_sector_code(self, sector_name: str) -> Optional[str]:
        """
        根据板块名称获取板块代码
        
        Args:
            sector_name: 板块名称
            
        Returns:
            板块代码，如 BK1036.DC
        """
        # 检查缓存有效性
        if not self._check_cache_validity():
            self._refresh_cache()
        
        # 精确匹配
        with self._cache_lock:
            return self._cache.get(sector_name)
    
    def get_sector_name(self, sector_code: str) -> Optional[str]:
        """
        根据板块代码获取板块名称
        
        Args:
            sector_code: 板块代码
            
        Returns:
            板块名称
        """
        # 检查缓存有效性
        if not self._check_cache_validity():
            self._refresh_cache()
        
        with self._cache_lock:
            return self._reverse_cache.get(sector_code)
    
    def get_all_sectors(self) -> List[Dict[str, str]]:
        """
        获取所有板块信息
        
        Returns:
            板块列表，每项包含 code 和 name
        """
        # 检查缓存有效性
        if not self._check_cache_validity():
            self._refresh_cache()
        
        with self._cache_lock:
            return [
                {"code": code, "name": name} 
                for name, code in self._cache.items()
            ]
    
    def search_sectors(self, keyword: str) -> List[Dict[str, str]]:
        """
        搜索包含关键词的板块
        
        Args:
            keyword: 搜索关键词
            
        Returns:
            匹配的板块列表
        """
        # 检查缓存有效性
        if not self._check_cache_validity():
            self._refresh_cache()
        
        results = []
        with self._cache_lock:
            for name, code in self._cache.items():
                if keyword in name:
                    results.append({"code": code, "name": name})
        
        return results


# 创建全局实例
sector_mapper = SectorCodeMapper()


# 便捷函数
def get_sector_code(sector_name: str) -> Optional[str]:
    """获取板块代码"""
    return sector_mapper.get_sector_code(sector_name)


def get_sector_name(sector_code: str) -> Optional[str]:
    """获取板块名称"""
    return sector_mapper.get_sector_name(sector_code)


# 测试代码
if __name__ == "__main__":
    # 测试板块映射
    test_names = ["银行", "半导体", "软件开发", "互联网服务", "新能源", "白酒"]
    
    print("测试板块代码映射")
    print("=" * 60)
    
    for name in test_names:
        code = get_sector_code(name)
        if code:
            print(f"{name} -> {code}")
            # 反向验证
            reverse_name = get_sector_name(code)
            print(f"  反向验证: {code} -> {reverse_name}")
        else:
            print(f"{name} -> 未找到对应代码")
    
    print("\n搜索包含'科技'的板块:")
    results = sector_mapper.search_sectors("科技")
    for sector in results:
        print(f"  {sector['name']} -> {sector['code']}")