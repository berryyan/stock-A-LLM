# Concept Agent Day 1 开发任务清单

## 任务概览
第一天目标：搭建Concept Agent基础框架，实现输入处理和基本配置系统

## 具体任务列表

### 1. 创建目录结构（30分钟）
```bash
# 创建以下目录和文件
agents/concept_agent_modular.py      # 主Agent文件
utils/concept/                       # 概念相关工具目录
├── __init__.py
├── input_processor.py              # 输入处理器
├── concept_matcher.py              # 概念匹配器  
├── scoring_config.py               # 评分配置
├── data_models.py                  # 数据模型
└── cache_manager.py                # 缓存管理器

tests/
├── test_concept_agent.py           # Agent主测试
└── test_concept_utils.py           # 工具类测试
```

### 2. 实现数据模型（1小时）

创建 `utils/concept/data_models.py`:
```python
from dataclasses import dataclass
from typing import List, Dict, Any, Optional
from datetime import datetime

@dataclass
class ConceptStock:
    """概念股数据模型"""
    ts_code: str
    name: str
    concept_names: List[str]
    
    # 评分相关
    concept_relevance_score: float = 0.0
    money_flow_score: float = 0.0
    technical_pattern_score: float = 0.0
    total_score: float = 0.0
    
    # 详细数据
    score_details: Dict[str, Any] = None
    financial_data: Dict[str, Any] = None
    technical_data: Dict[str, Any] = None
    
    # 元数据
    update_time: datetime = None
    data_source: List[str] = None

@dataclass
class ConceptInfo:
    """概念板块信息"""
    concept_code: str
    concept_name: str
    source: str  # 'ths' or 'dc'
    member_count: int
    update_date: str
    
@dataclass
class ConceptAnalysisResult:
    """概念分析结果"""
    query: str
    query_type: str
    matched_concepts: List[str]
    analyzed_stocks: List[ConceptStock]
    report: str
    metadata: Dict[str, Any]
```

### 3. 实现输入处理器（1.5小时）

创建 `utils/concept/input_processor.py`:
```python
import re
from typing import Dict, List
from enum import Enum

class InputType(Enum):
    KEYWORD = "keyword"
    CONCEPT_QUERY = "concept_query"
    NEWS = "news"

class ConceptInputProcessor:
    """概念股输入处理器"""
    
    def __init__(self):
        self.concept_patterns = [
            r'(.+)概念股',
            r'(.+)概念',
            r'(.+)板块'
        ]
    
    def process_input(self, user_input: str) -> Dict:
        """处理用户输入，识别输入类型和内容"""
        input_type = self._detect_input_type(user_input)
        
        return {
            "type": input_type.value,
            "content": self._extract_content(user_input, input_type),
            "original": user_input
        }
    
    def _detect_input_type(self, text: str) -> InputType:
        """检测输入类型"""
        # 长文本判定为新闻
        if len(text) > 100:
            return InputType.NEWS
        
        # 包含概念股等关键词
        for pattern in self.concept_patterns:
            if re.search(pattern, text):
                return InputType.CONCEPT_QUERY
        
        # 默认为关键词
        return InputType.KEYWORD
    
    def _extract_content(self, text: str, input_type: InputType) -> str:
        """提取核心内容"""
        if input_type == InputType.CONCEPT_QUERY:
            # 提取概念名称
            for pattern in self.concept_patterns:
                match = re.search(pattern, text)
                if match:
                    return match.group(1).strip()
        
        return text.strip()
    
    def extract_keywords_from_news(self, news_text: str) -> List[str]:
        """从新闻文本提取关键词（简单实现，后续用LLM）"""
        # 简单的关键词提取逻辑
        keywords = []
        
        # 提取引号内的词
        quoted = re.findall(r'["\']([^"\']+)["\']', news_text)
        keywords.extend(quoted)
        
        # 提取《》内的词
        titled = re.findall(r'《([^》]+)》', news_text)
        keywords.extend(titled)
        
        return keywords
```

### 4. 实现评分配置（1小时）

创建 `utils/concept/scoring_config.py`:
```python
from typing import Dict, List, Any

# 默认评分配置
DEFAULT_SCORING_CONFIG = {
    "concept_relevance": {
        "total_score": 40,
        "enabled": True,
        "items": [
            {
                "id": "board_membership",
                "name": "board_membership",
                "description": "在概念板块成分股中",
                "score": 10,
                "enabled": True,
                "required": False,
                "data_source": ["tu_ths_member", "tu_dc_member"]
            },
            {
                "id": "board_leading_limit",
                "name": "board_leading_limit", 
                "description": "板块内率先涨停",
                "score": 10,
                "enabled": True,
                "required": False,
                "params": {"days": 5, "rank": 3},
                "data_source": ["tu_stk_limit"]
            },
            {
                "id": "financial_mention",
                "name": "financial_mention",
                "description": "财报提及相关概念",
                "score": 5,
                "enabled": True,
                "required": False,
                "data_source": ["financial_reports"]
            },
            {
                "id": "qa_mention",
                "name": "qa_mention",
                "description": "互动平台提及",
                "score": 5,
                "enabled": True,
                "required": False,
                "data_source": ["tu_irm_qa_sz", "tu_irm_qa_sh"]
            },
            {
                "id": "announcement_mention",
                "name": "announcement_mention",
                "description": "公告提及",
                "score": 5,
                "enabled": True,
                "required": False,
                "data_source": ["tu_anns_d"]
            },
            {
                "id": "board_activity",
                "name": "board_activity",
                "description": "概念板块活跃度",
                "score": 5,
                "enabled": True,
                "required": False,
                "params": {"top_percent": 20, "days": 5}
            }
        ]
    },
    "money_flow": {
        "total_score": 30,
        "enabled": True,
        "items": [
            {
                "id": "daily_weekly_inflow",
                "name": "daily_weekly_inflow",
                "description": "日周双净流入",
                "score": 10,
                "enabled": True,
                "sub_items": [
                    {"name": "daily_inflow", "score": 5},
                    {"name": "weekly_inflow", "score": 5}
                ]
            },
            {
                "id": "inflow_ratio_rank",
                "name": "inflow_ratio_rank",
                "description": "净流入占流通市值比例排名",
                "score": 10,
                "enabled": True,
                "tiers": [
                    {"top_percent": 10, "score": 10},
                    {"top_percent": 30, "score": 7},
                    {"top_percent": 50, "score": 5}
                ]
            },
            {
                "id": "board_money_performance",
                "name": "board_money_performance",
                "description": "所属板块资金表现",
                "score": 5,
                "enabled": True
            },
            {
                "id": "continuous_inflow",
                "name": "continuous_inflow",
                "description": "连续净流入",
                "score": 5,
                "enabled": True,
                "tiers": [
                    {"days": 5, "score": 5},
                    {"days": 3, "score": 3}
                ]
            }
        ]
    },
    "technical_pattern": {
        "total_score": 30,
        "enabled": True,
        "items": [
            {
                "id": "macd_status",
                "name": "macd_status",
                "description": "MACD状态",
                "score": 15,
                "enabled": True,
                "sub_items": [
                    {
                        "name": "macd_above_water",
                        "description": "MACD水上红柱",
                        "score": 10,
                        "condition": "MACD>0 AND DIF>0"
                    },
                    {
                        "name": "first_in_board",
                        "description": "板块内率先水上",
                        "score": 5,
                        "params": {"days": 2}
                    }
                ]
            },
            {
                "id": "ma_arrangement",
                "name": "ma_arrangement",
                "description": "均线排列",
                "score": 15,
                "enabled": True,
                "condition": "MA5>MA10",
                "optional_condition": "MA5>MA10>MA20"
            }
        ]
    }
}

class ScoringConfigManager:
    """评分配置管理器"""
    
    def __init__(self, config: Dict = None):
        self.config = config or DEFAULT_SCORING_CONFIG
    
    def get_config(self) -> Dict:
        """获取当前配置"""
        return self.config
    
    def update_config(self, updates: Dict) -> None:
        """更新配置"""
        # 深度更新配置
        self._deep_update(self.config, updates)
    
    def enable_item(self, category: str, item_id: str) -> None:
        """启用某个评分项"""
        self._set_item_enabled(category, item_id, True)
    
    def disable_item(self, category: str, item_id: str) -> None:
        """禁用某个评分项"""
        self._set_item_enabled(category, item_id, False)
    
    def _set_item_enabled(self, category: str, item_id: str, enabled: bool) -> None:
        """设置评分项启用状态"""
        if category in self.config:
            items = self.config[category].get("items", [])
            for item in items:
                if item.get("id") == item_id:
                    item["enabled"] = enabled
                    break
    
    def _deep_update(self, base: Dict, updates: Dict) -> None:
        """深度更新字典"""
        for key, value in updates.items():
            if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                self._deep_update(base[key], value)
            else:
                base[key] = value
```

### 5. 实现基础缓存管理器（1小时）

创建 `utils/concept/cache_manager.py`:
```python
from typing import Dict, Optional, Any
from datetime import datetime, timedelta
from collections import OrderedDict
import json
import os

class LRUCache:
    """简单的LRU缓存实现"""
    
    def __init__(self, maxsize: int = 1000):
        self.cache = OrderedDict()
        self.maxsize = maxsize
        self.stats = {
            "hits": 0,
            "misses": 0,
            "evictions": 0
        }
    
    def get(self, key: str) -> Optional[Any]:
        """获取缓存值"""
        if key in self.cache:
            # 移到最后（最近使用）
            self.cache.move_to_end(key)
            self.stats["hits"] += 1
            return self.cache[key]["data"]
        
        self.stats["misses"] += 1
        return None
    
    def set(self, key: str, value: Any, ttl: int = 300) -> None:
        """设置缓存值"""
        # 检查是否需要淘汰
        if len(self.cache) >= self.maxsize and key not in self.cache:
            # 淘汰最早的
            self.cache.popitem(last=False)
            self.stats["evictions"] += 1
        
        self.cache[key] = {
            "data": value,
            "expire_at": datetime.now() + timedelta(seconds=ttl)
        }
    
    def is_expired(self, key: str) -> bool:
        """检查是否过期"""
        if key not in self.cache:
            return True
        
        return datetime.now() > self.cache[key]["expire_at"]
    
    def clear_expired(self) -> None:
        """清理过期数据"""
        expired_keys = [k for k in self.cache if self.is_expired(k)]
        for key in expired_keys:
            del self.cache[key]
    
    def get_stats(self) -> Dict:
        """获取缓存统计"""
        total = self.stats["hits"] + self.stats["misses"]
        hit_rate = self.stats["hits"] / total if total > 0 else 0
        
        return {
            **self.stats,
            "size": len(self.cache),
            "hit_rate": f"{hit_rate:.2%}"
        }

class ConceptCacheManager:
    """概念股缓存管理器"""
    
    def __init__(self, cache_dir: str = "data/concept_cache"):
        self.cache_dir = cache_dir
        self.memory_cache = LRUCache(maxsize=1000)
        
        # 创建缓存目录
        os.makedirs(cache_dir, exist_ok=True)
    
    async def get_concept_members(self, concept_name: str) -> Optional[List[str]]:
        """获取概念成分股（带缓存）"""
        cache_key = f"members:{concept_name}"
        
        # 1. 检查内存缓存
        cached = self.memory_cache.get(cache_key)
        if cached and not self.memory_cache.is_expired(cache_key):
            return cached
        
        # 2. 检查文件缓存
        file_cached = self._read_file_cache(cache_key)
        if file_cached:
            # 更新内存缓存
            self.memory_cache.set(cache_key, file_cached, ttl=3600)
            return file_cached
        
        return None
    
    async def set_concept_members(self, concept_name: str, members: List[str]) -> None:
        """设置概念成分股缓存"""
        cache_key = f"members:{concept_name}"
        
        # 更新内存缓存
        self.memory_cache.set(cache_key, members, ttl=3600)
        
        # 更新文件缓存
        self._write_file_cache(cache_key, members)
    
    def _read_file_cache(self, key: str) -> Optional[Any]:
        """读取文件缓存"""
        file_path = os.path.join(self.cache_dir, f"{key.replace(':', '_')}.json")
        
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                # 检查过期时间
                expire_at = datetime.fromisoformat(data["expire_at"])
                if datetime.now() < expire_at:
                    return data["value"]
                    
            except Exception as e:
                print(f"读取缓存文件失败: {e}")
        
        return None
    
    def _write_file_cache(self, key: str, value: Any, ttl: int = 86400) -> None:
        """写入文件缓存"""
        file_path = os.path.join(self.cache_dir, f"{key.replace(':', '_')}.json")
        
        data = {
            "key": key,
            "value": value,
            "created_at": datetime.now().isoformat(),
            "expire_at": (datetime.now() + timedelta(seconds=ttl)).isoformat()
        }
        
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"写入缓存文件失败: {e}")
```

### 6. 创建主Agent框架（1.5小时）

创建 `agents/concept_agent_modular.py`:
```python
"""
Concept Agent - 概念股分析专家
负责概念股的智能发现、分析和推荐
"""

import asyncio
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime

from langchain.prompts import ChatPromptTemplate
from langchain_community.chat_models import ChatDeepSeek
from langchain_core.output_parsers import JsonOutputParser

from database.mysql_connector import MySQLConnector
from utils.concept.input_processor import ConceptInputProcessor
from utils.concept.scoring_config import ScoringConfigManager
from utils.concept.cache_manager import ConceptCacheManager
from utils.concept.data_models import (
    ConceptStock, ConceptInfo, ConceptAnalysisResult
)
from utils.agent_response import create_agent_response
from config.settings import CONCEPT_AGENT_CONFIG

# 配置日志
logger = logging.getLogger(__name__)

class ConceptAgentModular:
    """模块化的概念股分析Agent"""
    
    def __init__(self):
        """初始化Agent"""
        # 基础组件
        self.db = MySQLConnector()
        self.llm = ChatDeepSeek(
            temperature=0.1,
            model="deepseek-chat"
        )
        
        # 概念股专用组件
        self.input_processor = ConceptInputProcessor()
        self.scoring_manager = ScoringConfigManager()
        self.cache_manager = ConceptCacheManager()
        
        # 统计信息
        self.stats = {
            "query_count": 0,
            "success_count": 0,
            "cache_hits": 0,
            "avg_response_time": 0
        }
        
        logger.info("Concept Agent 初始化完成")
    
    async def analyze_concept(self, query: str) -> Dict:
        """分析概念股 - 主入口"""
        start_time = datetime.now()
        self.stats["query_count"] += 1
        
        try:
            # 1. 处理输入
            input_data = self.input_processor.process_input(query)
            logger.info(f"输入类型: {input_data['type']}, 内容: {input_data['content']}")
            
            # 2. 概念扩展（第一次LLM调用）
            matched_concepts = await self._expand_concepts(input_data)
            
            if not matched_concepts:
                return create_agent_response(
                    success=False,
                    message="未找到匹配的概念板块",
                    data={},
                    agent_name="ConceptAgent"
                )
            
            logger.info(f"匹配到概念: {matched_concepts}")
            
            # 3. 获取概念成分股
            all_stocks = await self._get_concept_stocks(matched_concepts)
            
            if not all_stocks:
                return create_agent_response(
                    success=False,
                    message="未找到相关概念股",
                    data={},
                    agent_name="ConceptAgent"
                )
            
            logger.info(f"找到 {len(all_stocks)} 只相关股票")
            
            # 4. 数据采集（并行）
            stock_data = await self._collect_stock_data(all_stocks)
            
            # 5. 评分计算
            scored_stocks = await self._calculate_scores(stock_data)
            
            # 6. 排序和筛选
            top_stocks = self._rank_and_filter(scored_stocks)
            
            # 7. 生成报告（第二次LLM调用）
            report = await self._generate_report(
                top_stocks, 
                matched_concepts[0],  # 主概念
                len(all_stocks)
            )
            
            # 8. 组装结果
            result = ConceptAnalysisResult(
                query=query,
                query_type=input_data['type'],
                matched_concepts=matched_concepts,
                analyzed_stocks=top_stocks,
                report=report,
                metadata={
                    "total_stocks": len(all_stocks),
                    "analyzed_stocks": len(top_stocks),
                    "response_time": (datetime.now() - start_time).total_seconds()
                }
            )
            
            self.stats["success_count"] += 1
            
            return create_agent_response(
                success=True,
                message="概念股分析完成",
                data=self._format_result(result),
                agent_name="ConceptAgent"
            )
            
        except Exception as e:
            logger.error(f"概念股分析失败: {str(e)}", exc_info=True)
            return create_agent_response(
                success=False,
                message=f"分析失败: {str(e)}",
                data={},
                agent_name="ConceptAgent"
            )
    
    async def _expand_concepts(self, input_data: Dict) -> List[str]:
        """扩展概念（第一次LLM调用）"""
        # TODO: Day 2实现
        # 临时返回模拟数据
        if "新能源" in input_data['content']:
            return ["新能源汽车", "锂电池", "充电桩"]
        return [input_data['content']]
    
    async def _get_concept_stocks(self, concepts: List[str]) -> List[str]:
        """获取概念成分股"""
        # TODO: Day 3实现
        # 临时返回模拟数据
        return ["002594.SZ", "300750.SZ", "002460.SZ"]
    
    async def _collect_stock_data(self, stocks: List[str]) -> List[Dict]:
        """采集股票数据"""
        # TODO: Day 3-4实现
        # 临时返回模拟数据
        return [
            {"ts_code": stock, "name": f"股票{stock[:6]}"} 
            for stock in stocks
        ]
    
    async def _calculate_scores(self, stock_data: List[Dict]) -> List[ConceptStock]:
        """计算评分"""
        # TODO: Day 5-6实现
        # 临时返回模拟数据
        scored_stocks = []
        for data in stock_data:
            stock = ConceptStock(
                ts_code=data["ts_code"],
                name=data["name"],
                concept_names=["新能源汽车"],
                concept_relevance_score=35,
                money_flow_score=25,
                technical_pattern_score=28,
                total_score=88
            )
            scored_stocks.append(stock)
        return scored_stocks
    
    def _rank_and_filter(self, stocks: List[ConceptStock], top_n: int = 20) -> List[ConceptStock]:
        """排序和筛选"""
        # 按总分降序排序
        sorted_stocks = sorted(stocks, key=lambda x: x.total_score, reverse=True)
        return sorted_stocks[:top_n]
    
    async def _generate_report(self, stocks: List[ConceptStock], concept: str, total: int) -> str:
        """生成分析报告（第二次LLM调用）"""
        # TODO: Day 7实现
        return f"## {concept}概念股分析报告\n\n找到{total}只相关股票，推荐关注前{len(stocks)}只。"
    
    def _format_result(self, result: ConceptAnalysisResult) -> Dict:
        """格式化结果"""
        return {
            "query": result.query,
            "matched_concepts": result.matched_concepts,
            "report": result.report,
            "top_stocks": [
                {
                    "ts_code": s.ts_code,
                    "name": s.name,
                    "total_score": s.total_score,
                    "scores": {
                        "concept_relevance": s.concept_relevance_score,
                        "money_flow": s.money_flow_score,
                        "technical_pattern": s.technical_pattern_score
                    }
                }
                for s in result.analyzed_stocks[:5]  # TOP5
            ],
            "metadata": result.metadata
        }
    
    def get_stats(self) -> Dict:
        """获取统计信息"""
        return {
            **self.stats,
            **self.cache_manager.memory_cache.get_stats()
        }
```

### 7. 创建测试文件（1小时）

创建 `tests/test_concept_agent.py`:
```python
import pytest
import asyncio
from datetime import datetime

from agents.concept_agent_modular import ConceptAgentModular
from utils.concept.input_processor import ConceptInputProcessor, InputType
from utils.concept.scoring_config import ScoringConfigManager
from utils.concept.cache_manager import LRUCache
from utils.concept.data_models import ConceptStock

class TestConceptInputProcessor:
    """测试输入处理器"""
    
    def setup_method(self):
        self.processor = ConceptInputProcessor()
    
    def test_detect_keyword_input(self):
        """测试关键词输入识别"""
        result = self.processor.process_input("固态电池")
        assert result["type"] == InputType.KEYWORD.value
        assert result["content"] == "固态电池"
    
    def test_detect_concept_query(self):
        """测试概念查询识别"""
        queries = [
            "新能源汽车概念股",
            "锂电池概念",
            "半导体板块"
        ]
        
        for query in queries:
            result = self.processor.process_input(query)
            assert result["type"] == InputType.CONCEPT_QUERY.value
    
    def test_detect_news_input(self):
        """测试新闻文本识别"""
        news = "国家部委及地方政府近期密集出台固态电池鼓励政策。" * 10
        result = self.processor.process_input(news)
        assert result["type"] == InputType.NEWS.value
    
    def test_extract_content(self):
        """测试内容提取"""
        result = self.processor.process_input("新能源汽车概念股")
        assert result["content"] == "新能源汽车"
        
        result = self.processor.process_input("半导体板块")
        assert result["content"] == "半导体"

class TestScoringConfig:
    """测试评分配置"""
    
    def setup_method(self):
        self.manager = ScoringConfigManager()
    
    def test_default_config(self):
        """测试默认配置"""
        config = self.manager.get_config()
        
        assert "concept_relevance" in config
        assert "money_flow" in config
        assert "technical_pattern" in config
        
        assert config["concept_relevance"]["total_score"] == 40
        assert config["money_flow"]["total_score"] == 30
        assert config["technical_pattern"]["total_score"] == 30
    
    def test_enable_disable_item(self):
        """测试启用/禁用评分项"""
        # 禁用某个评分项
        self.manager.disable_item("concept_relevance", "board_membership")
        
        config = self.manager.get_config()
        items = config["concept_relevance"]["items"]
        
        board_item = next(i for i in items if i["id"] == "board_membership")
        assert board_item["enabled"] == False
        
        # 重新启用
        self.manager.enable_item("concept_relevance", "board_membership")
        board_item = next(i for i in items if i["id"] == "board_membership")
        assert board_item["enabled"] == True

class TestLRUCache:
    """测试LRU缓存"""
    
    def setup_method(self):
        self.cache = LRUCache(maxsize=3)
    
    def test_basic_operations(self):
        """测试基本操作"""
        # 设置缓存
        self.cache.set("key1", "value1")
        self.cache.set("key2", "value2")
        
        # 获取缓存
        assert self.cache.get("key1") == "value1"
        assert self.cache.get("key2") == "value2"
        assert self.cache.get("key3") is None
        
        # 统计信息
        stats = self.cache.get_stats()
        assert stats["hits"] == 2
        assert stats["misses"] == 1
    
    def test_lru_eviction(self):
        """测试LRU淘汰"""
        # 填满缓存
        self.cache.set("key1", "value1")
        self.cache.set("key2", "value2")
        self.cache.set("key3", "value3")
        
        # 访问key1，使其成为最近使用
        self.cache.get("key1")
        
        # 添加新键，应该淘汰key2
        self.cache.set("key4", "value4")
        
        assert self.cache.get("key1") == "value1"  # 还在
        assert self.cache.get("key2") is None      # 被淘汰
        assert self.cache.get("key3") == "value3"  # 还在
        assert self.cache.get("key4") == "value4"  # 新增的

class TestConceptAgent:
    """测试Concept Agent主功能"""
    
    @pytest.fixture
    async def agent(self):
        """创建测试用Agent"""
        agent = ConceptAgentModular()
        yield agent
        # 清理
        agent.db.close()
    
    @pytest.mark.asyncio
    async def test_analyze_concept_basic(self, agent):
        """测试基本概念分析"""
        result = await agent.analyze_concept("新能源汽车概念股")
        
        # 由于是模拟数据，只测试基本结构
        assert "success" in result
        assert "data" in result
        assert "agent_name" in result
        assert result["agent_name"] == "ConceptAgent"
    
    @pytest.mark.asyncio  
    async def test_input_validation(self, agent):
        """测试输入验证"""
        # 空输入
        result = await agent.analyze_concept("")
        assert result["success"] == False
        
        # 过长输入
        long_input = "a" * 10000
        result = await agent.analyze_concept(long_input)
        # 应该作为新闻处理，不会报错

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
```

### 8. 创建简单测试脚本（30分钟）

创建 `test_concept_basic.py`:
```python
#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Concept Agent 基础功能测试
"""

import asyncio
from utils.concept.input_processor import ConceptInputProcessor
from utils.concept.scoring_config import ScoringConfigManager
from utils.concept.cache_manager import LRUCache

def test_input_processor():
    """测试输入处理器"""
    print("=== 测试输入处理器 ===")
    processor = ConceptInputProcessor()
    
    test_cases = [
        "固态电池",
        "新能源汽车概念股",
        "半导体板块",
        "国家部委及地方政府近期密集出台固态电池鼓励政策..." * 5
    ]
    
    for test_input in test_cases:
        result = processor.process_input(test_input)
        print(f"\n输入: {test_input[:50]}...")
        print(f"类型: {result['type']}")
        print(f"内容: {result['content'][:50]}...")

def test_scoring_config():
    """测试评分配置"""
    print("\n\n=== 测试评分配置 ===")
    manager = ScoringConfigManager()
    config = manager.get_config()
    
    print("\n评分维度:")
    for category, settings in config.items():
        total = settings['total_score']
        items = len(settings['items'])
        print(f"- {category}: {total}分, {items}个评分项")

def test_cache():
    """测试缓存"""
    print("\n\n=== 测试缓存 ===")
    cache = LRUCache(maxsize=5)
    
    # 添加数据
    for i in range(7):
        cache.set(f"key{i}", f"value{i}")
    
    # 获取统计
    stats = cache.get_stats()
    print(f"缓存统计: {stats}")
    
    # 测试获取
    print("\n测试获取:")
    for i in range(7):
        value = cache.get(f"key{i}")
        print(f"key{i}: {value}")

async def test_agent_basic():
    """测试Agent基础功能"""
    print("\n\n=== 测试Agent基础功能 ===")
    
    from agents.concept_agent_modular import ConceptAgentModular
    
    agent = ConceptAgentModular()
    
    # 测试分析
    result = await agent.analyze_concept("新能源汽车概念股")
    
    print(f"\n分析结果:")
    print(f"成功: {result['success']}")
    print(f"消息: {result.get('message', '')}")
    
    if result['success'] and 'data' in result:
        data = result['data']
        print(f"匹配概念: {data.get('matched_concepts', [])}")
        print(f"报告预览: {data.get('report', '')[:100]}...")

def main():
    """主测试函数"""
    print("Concept Agent Day 1 基础测试")
    print("=" * 50)
    
    # 同步测试
    test_input_processor()
    test_scoring_config()
    test_cache()
    
    # 异步测试
    asyncio.run(test_agent_basic())
    
    print("\n\n测试完成!")

if __name__ == "__main__":
    main()
```

## 检查清单

完成以上任务后，请确认：

- [ ] 目录结构创建完成
- [ ] 数据模型定义完整
- [ ] 输入处理器可以识别三种输入类型
- [ ] 评分配置支持动态调整
- [ ] 缓存管理器基本功能正常
- [ ] Agent主框架可以运行
- [ ] 单元测试全部通过
- [ ] 基础测试脚本运行正常

## 明天任务预览

Day 2 主要任务：
1. 实现LLM概念扩展功能
2. 连接数据库获取概念列表
3. 实现概念匹配逻辑
4. 添加交易日历缓存

---
祝开发顺利！如有问题随时沟通。