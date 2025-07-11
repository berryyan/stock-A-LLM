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
        
        # 缓存数据 - 增强版，包含content_type
        self._cache: Dict[str, Dict[str, str]] = {}  # name -> {ts_code, content_type}
        self._reverse_cache: Dict[str, Dict[str, str]] = {}  # ts_code -> {name, content_type}
        self._type_cache: Dict[str, List[Dict[str, str]]] = {  # content_type -> [{name, ts_code}]
            '行业': [],
            '概念': [],
            '地域': []
        }
        self._cache_time: Optional[datetime] = None
        self._cache_lock = threading.Lock()
        
        # 预加载缓存
        self._refresh_cache()
    
    def _refresh_cache(self) -> None:
        """刷新缓存数据"""
        try:
            self.logger.info("开始刷新板块代码缓存")
            
            # 查询所有板块信息（包括行业、概念、地域）
            query = """
            SELECT DISTINCT ts_code, name, content_type
            FROM tu_moneyflow_ind_dc 
            WHERE ts_code IS NOT NULL 
            AND name IS NOT NULL
            """
            
            result = self.mysql.execute_query(query)
            
            # 构建缓存
            new_cache = {}
            new_reverse_cache = {}
            new_type_cache = {'行业': [], '概念': [], '地域': []}
            
            for row in result:
                ts_code = row['ts_code']
                name = row['name']
                content_type = row['content_type']
                
                # 正向映射：名称 -> {代码, 类型}
                new_cache[name] = {
                    'ts_code': ts_code,
                    'content_type': content_type
                }
                
                # 反向映射：代码 -> {名称, 类型}
                new_reverse_cache[ts_code] = {
                    'name': name,
                    'content_type': content_type
                }
                
                # 类型缓存
                if content_type in new_type_cache:
                    new_type_cache[content_type].append({
                        'name': name,
                        'ts_code': ts_code
                    })
            
            # 原子更新缓存
            with self._cache_lock:
                self._cache = new_cache
                self._reverse_cache = new_reverse_cache
                self._type_cache = new_type_cache
                self._cache_time = datetime.now()
            
            # 统计信息
            total_count = len(new_cache)
            type_counts = {t: len(items) for t, items in new_type_cache.items()}
            self.logger.info(f"板块代码缓存刷新完成，共缓存{total_count}个板块映射")
            self.logger.info(f"板块类型分布: {type_counts}")
            
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
            sector_info = self._cache.get(sector_name)
            return sector_info['ts_code'] if sector_info else None
    
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
            sector_info = self._reverse_cache.get(sector_code)
            return sector_info['name'] if sector_info else None
    
    def get_all_sectors(self) -> List[Dict[str, str]]:
        """
        获取所有板块信息
        
        Returns:
            板块列表，每项包含 code、name 和 content_type
        """
        # 检查缓存有效性
        if not self._check_cache_validity():
            self._refresh_cache()
        
        with self._cache_lock:
            return [
                {
                    "code": info['ts_code'], 
                    "name": name,
                    "content_type": info['content_type']
                } 
                for name, info in self._cache.items()
            ]
    
    def get_sector_info(self, sector_name_or_code: str) -> Optional[Dict[str, str]]:
        """
        获取板块的完整信息
        
        Args:
            sector_name_or_code: 板块名称或代码
            
        Returns:
            包含name、ts_code、content_type的字典，或None
        """
        # 检查缓存有效性
        if not self._check_cache_validity():
            self._refresh_cache()
        
        with self._cache_lock:
            # 先尝试作为名称查询
            if sector_name_or_code in self._cache:
                info = self._cache[sector_name_or_code]
                return {
                    'name': sector_name_or_code,
                    'ts_code': info['ts_code'],
                    'content_type': info['content_type']
                }
            
            # 再尝试作为代码查询
            if sector_name_or_code in self._reverse_cache:
                info = self._reverse_cache[sector_name_or_code]
                return {
                    'name': info['name'],
                    'ts_code': sector_name_or_code,
                    'content_type': info['content_type']
                }
            
            return None
    
    def get_sectors_by_type(self, content_type: str) -> List[Dict[str, str]]:
        """
        根据类型获取板块列表
        
        Args:
            content_type: 板块类型（行业/概念/地域）
            
        Returns:
            该类型的板块列表
        """
        # 检查缓存有效性
        if not self._check_cache_validity():
            self._refresh_cache()
        
        with self._cache_lock:
            return self._type_cache.get(content_type, []).copy()
    
    def search_sectors(self, keyword: str) -> List[Dict[str, str]]:
        """
        搜索包含关键词的板块
        
        Args:
            keyword: 搜索关键词
            
        Returns:
            匹配的板块列表，包含code、name和content_type
        """
        # 检查缓存有效性
        if not self._check_cache_validity():
            self._refresh_cache()
        
        keyword_lower = keyword.lower()
        results = []
        
        with self._cache_lock:
            for name, info in self._cache.items():
                if keyword_lower in name.lower():
                    results.append({
                        "code": info['ts_code'], 
                        "name": name,
                        "content_type": info['content_type']
                    })
        
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