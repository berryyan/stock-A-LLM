#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
路由决策监控和统计系统
用于追踪和分析HybridAgent的路由决策模式
"""

import json
import time
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple
from collections import defaultdict, Counter
from threading import Lock
import os

from utils.logger import setup_logger


class RoutingMonitor:
    """路由决策监控器"""
    
    _instance = None
    _lock = Lock()
    
    def __new__(cls):
        """单例模式"""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        """初始化监控器"""
        if hasattr(self, '_initialized'):
            return
            
        self.logger = setup_logger("routing_monitor")
        
        # 统计数据
        self.routing_stats = {
            'total_queries': 0,
            'routing_distribution': defaultdict(int),
            'success_rate': defaultdict(lambda: {'success': 0, 'total': 0}),
            'response_time': defaultdict(list),
            'keyword_hits': defaultdict(int),
            'entity_recognition': defaultdict(int),
            'hourly_distribution': defaultdict(lambda: defaultdict(int)),
            'error_patterns': defaultdict(int),
            'query_patterns': []
        }
        
        # 会话数据
        self.session_data = {
            'session_start': datetime.now(),
            'last_save': datetime.now(),
            'active_queries': {}
        }
        
        # 配置
        self.config = {
            'save_interval': 300,  # 5分钟保存一次
            'max_query_patterns': 1000,  # 最多保存1000个查询模式
            'stats_file': 'data/routing_stats.json',
            'pattern_analysis_enabled': True
        }
        
        # 加载历史数据
        self._load_stats()
        
        self._initialized = True
        self.logger.info("路由监控器初始化完成")
    
    def _load_stats(self):
        """加载历史统计数据"""
        try:
            if os.path.exists(self.config['stats_file']):
                with open(self.config['stats_file'], 'r', encoding='utf-8') as f:
                    saved_stats = json.load(f)
                    
                # 合并历史数据
                self.routing_stats['total_queries'] = saved_stats.get('total_queries', 0)
                
                # 转换defaultdict
                for key in ['routing_distribution', 'keyword_hits', 'entity_recognition', 'error_patterns']:
                    if key in saved_stats:
                        self.routing_stats[key] = defaultdict(int, saved_stats[key])
                
                self.logger.info(f"加载历史统计数据: {self.routing_stats['total_queries']}条查询记录")
        except Exception as e:
            self.logger.warning(f"加载历史数据失败: {e}")
    
    def record_routing_decision(self, 
                              query: str,
                              decision: Dict[str, Any],
                              query_id: Optional[str] = None) -> str:
        """记录路由决策"""
        try:
            # 生成查询ID
            if not query_id:
                query_id = f"q_{int(time.time() * 1000)}"
            
            # 记录基本信息
            self.routing_stats['total_queries'] += 1
            
            # 记录路由类型分布
            query_type = decision.get('query_type', 'UNKNOWN')
            self.routing_stats['routing_distribution'][query_type] += 1
            
            # 记录实体识别
            entities = decision.get('entities', [])
            for entity in entities:
                self.routing_stats['entity_recognition'][entity] += 1
            
            # 分析查询关键词
            if self.config['pattern_analysis_enabled']:
                self._analyze_query_pattern(query, query_type)
            
            # 记录时间分布
            current_hour = datetime.now().strftime("%Y-%m-%d %H:00")
            self.routing_stats['hourly_distribution'][current_hour][query_type] += 1
            
            # 记录活跃查询
            self.session_data['active_queries'][query_id] = {
                'query': query,
                'query_type': query_type,
                'start_time': time.time(),
                'decision': decision
            }
            
            # 定期保存
            self._auto_save()
            
            self.logger.info(f"记录路由决策: {query_id} -> {query_type}")
            return query_id
            
        except Exception as e:
            self.logger.error(f"记录路由决策失败: {e}")
            return ""
    
    def record_query_result(self,
                          query_id: str,
                          success: bool,
                          response_time: float,
                          error_msg: Optional[str] = None):
        """记录查询结果"""
        try:
            if query_id not in self.session_data['active_queries']:
                self.logger.warning(f"未找到查询ID: {query_id}")
                return
            
            query_info = self.session_data['active_queries'].pop(query_id)
            query_type = query_info['query_type']
            
            # 更新成功率
            self.routing_stats['success_rate'][query_type]['total'] += 1
            if success:
                self.routing_stats['success_rate'][query_type]['success'] += 1
            
            # 记录响应时间
            self.routing_stats['response_time'][query_type].append(response_time)
            
            # 记录错误模式
            if not success and error_msg:
                self._analyze_error_pattern(error_msg, query_type)
            
            self.logger.info(f"记录查询结果: {query_id} -> {'成功' if success else '失败'} ({response_time:.2f}s)")
            
        except Exception as e:
            self.logger.error(f"记录查询结果失败: {e}")
    
    def _analyze_query_pattern(self, query: str, query_type: str):
        """分析查询模式"""
        try:
            # 提取关键词
            keywords = self._extract_keywords(query)
            for keyword in keywords:
                self.routing_stats['keyword_hits'][keyword] += 1
            
            # 保存查询模式（限制数量）
            if len(self.routing_stats['query_patterns']) < self.config['max_query_patterns']:
                self.routing_stats['query_patterns'].append({
                    'query': query[:100],  # 限制长度
                    'type': query_type,
                    'keywords': keywords,
                    'timestamp': datetime.now().isoformat()
                })
                
        except Exception as e:
            self.logger.error(f"分析查询模式失败: {e}")
    
    def _extract_keywords(self, query: str) -> List[str]:
        """提取查询关键词"""
        # 定义关键词模式
        patterns = {
            '财务': ['财务', '营收', '利润', '资产', '负债', '现金流', 'ROE', 'ROA'],
            '股价': ['股价', '价格', '涨跌', '涨幅', '跌幅', '成交量', '市值'],
            '资金': ['资金', '主力', '流入', '流出', '大单', '超大单'],
            '公告': ['公告', '年报', '季报', '披露', '发布'],
            '技术': ['均线', 'MACD', 'KDJ', 'RSI', '技术指标'],
            '时间': ['最新', '最近', '今天', '昨天', '本周', '本月']
        }
        
        keywords = []
        for category, words in patterns.items():
            for word in words:
                if word in query:
                    keywords.append(f"{category}:{word}")
        
        return keywords
    
    def _analyze_error_pattern(self, error_msg: str, query_type: str):
        """分析错误模式"""
        # 定义错误模式
        error_patterns = {
            'timeout': '超时',
            'parse_error': 'parse.*error|解析.*错误',
            'no_data': '没有.*数据|找不到|无结果',
            'connection': '连接.*失败|网络.*错误',
            'invalid_input': '无效.*输入|参数.*错误'
        }
        
        for pattern_name, pattern in error_patterns.items():
            import re
            if re.search(pattern, error_msg, re.IGNORECASE):
                self.routing_stats['error_patterns'][f"{query_type}:{pattern_name}"] += 1
                break
    
    def get_statistics(self) -> Dict[str, Any]:
        """获取统计数据"""
        stats = {
            'total_queries': self.routing_stats['total_queries'],
            'routing_distribution': dict(self.routing_stats['routing_distribution']),
            'success_rates': {},
            'avg_response_times': {},
            'top_keywords': [],
            'top_entities': [],
            'recent_patterns': []
        }
        
        # 计算成功率
        for query_type, data in self.routing_stats['success_rate'].items():
            if data['total'] > 0:
                stats['success_rates'][query_type] = {
                    'rate': data['success'] / data['total'] * 100,
                    'total': data['total'],
                    'success': data['success']
                }
        
        # 计算平均响应时间
        for query_type, times in self.routing_stats['response_time'].items():
            if times:
                stats['avg_response_times'][query_type] = {
                    'avg': sum(times) / len(times),
                    'min': min(times),
                    'max': max(times),
                    'count': len(times)
                }
        
        # 获取Top关键词
        keyword_counter = Counter(self.routing_stats['keyword_hits'])
        stats['top_keywords'] = keyword_counter.most_common(10)
        
        # 获取Top实体
        entity_counter = Counter(self.routing_stats['entity_recognition'])
        stats['top_entities'] = entity_counter.most_common(10)
        
        # 获取最近的查询模式
        if self.routing_stats['query_patterns']:
            stats['recent_patterns'] = self.routing_stats['query_patterns'][-10:]
        
        return stats
    
    def get_hourly_report(self, hours: int = 24) -> Dict[str, Any]:
        """获取小时级报告"""
        end_time = datetime.now()
        start_time = end_time - timedelta(hours=hours)
        
        hourly_data = {}
        for hour_str, data in self.routing_stats['hourly_distribution'].items():
            hour_time = datetime.strptime(hour_str, "%Y-%m-%d %H:00")
            if start_time <= hour_time <= end_time:
                hourly_data[hour_str] = dict(data)
        
        return {
            'period': f"最近{hours}小时",
            'start': start_time.isoformat(),
            'end': end_time.isoformat(),
            'hourly_distribution': hourly_data
        }
    
    def _auto_save(self):
        """自动保存统计数据"""
        current_time = datetime.now()
        if (current_time - self.session_data['last_save']).seconds > self.config['save_interval']:
            self.save_stats()
            self.session_data['last_save'] = current_time
    
    def save_stats(self):
        """保存统计数据到文件"""
        try:
            # 确保目录存在
            os.makedirs(os.path.dirname(self.config['stats_file']), exist_ok=True)
            
            # 准备保存的数据
            save_data = {
                'total_queries': self.routing_stats['total_queries'],
                'routing_distribution': dict(self.routing_stats['routing_distribution']),
                'keyword_hits': dict(self.routing_stats['keyword_hits']),
                'entity_recognition': dict(self.routing_stats['entity_recognition']),
                'error_patterns': dict(self.routing_stats['error_patterns']),
                'last_update': datetime.now().isoformat()
            }
            
            # 保存到文件
            with open(self.config['stats_file'], 'w', encoding='utf-8') as f:
                json.dump(save_data, f, ensure_ascii=False, indent=2)
            
            self.logger.info(f"统计数据已保存: {self.routing_stats['total_queries']}条记录")
            
        except Exception as e:
            self.logger.error(f"保存统计数据失败: {e}")
    
    def generate_report(self) -> str:
        """生成统计报告"""
        stats = self.get_statistics()
        hourly_report = self.get_hourly_report()
        
        report = f"""
路由决策统计报告
生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
{'='*60}

1. 总体统计
- 总查询数: {stats['total_queries']}
- 会话开始: {self.session_data['session_start'].strftime('%Y-%m-%d %H:%M:%S')}

2. 路由类型分布
"""
        for query_type, count in stats['routing_distribution'].items():
            percentage = count / stats['total_queries'] * 100 if stats['total_queries'] > 0 else 0
            report += f"   {query_type:<15} : {count:>6} ({percentage:>5.1f}%)\n"
        
        report += "\n3. 查询成功率\n"
        for query_type, data in stats['success_rates'].items():
            report += f"   {query_type:<15} : {data['rate']:>5.1f}% ({data['success']}/{data['total']})\n"
        
        report += "\n4. 平均响应时间\n"
        for query_type, data in stats['avg_response_times'].items():
            report += f"   {query_type:<15} : {data['avg']:>5.2f}s (min: {data['min']:.2f}s, max: {data['max']:.2f}s)\n"
        
        report += "\n5. Top 10 关键词\n"
        for keyword, count in stats['top_keywords']:
            report += f"   {keyword:<20} : {count}\n"
        
        report += "\n6. Top 10 实体\n"
        for entity, count in stats['top_entities']:
            report += f"   {entity:<20} : {count}\n"
        
        report += f"\n7. 最近24小时查询分布\n"
        total_24h = sum(sum(data.values()) for data in hourly_report['hourly_distribution'].values())
        report += f"   总查询数: {total_24h}\n"
        
        return report


# 全局实例
routing_monitor = RoutingMonitor()


# 便捷函数
def record_routing(query: str, decision: Dict[str, Any]) -> str:
    """记录路由决策"""
    return routing_monitor.record_routing_decision(query, decision)


def record_result(query_id: str, success: bool, response_time: float, error_msg: Optional[str] = None):
    """记录查询结果"""
    routing_monitor.record_query_result(query_id, success, response_time, error_msg)


def get_routing_stats() -> Dict[str, Any]:
    """获取路由统计"""
    return routing_monitor.get_statistics()


def generate_routing_report() -> str:
    """生成路由报告"""
    return routing_monitor.generate_report()


# 测试代码
if __name__ == "__main__":
    # 测试监控器
    monitor = RoutingMonitor()
    
    # 模拟一些查询
    test_queries = [
        ("贵州茅台最新股价", {"query_type": "SQL_ONLY", "entities": ["600519.SH"]}),
        ("分析茅台的财务健康度", {"query_type": "FINANCIAL", "entities": ["600519.SH"]}),
        ("茅台最新公告", {"query_type": "RAG_ONLY", "entities": ["600519.SH"]}),
        ("茅台的资金流向", {"query_type": "MONEY_FLOW", "entities": ["600519.SH"]}),
    ]
    
    for query, decision in test_queries:
        query_id = monitor.record_routing_decision(query, decision)
        # 模拟执行
        time.sleep(0.1)
        monitor.record_query_result(query_id, True, 2.5)
    
    # 生成报告
    print(monitor.generate_report())
    
    # 保存统计
    monitor.save_stats()