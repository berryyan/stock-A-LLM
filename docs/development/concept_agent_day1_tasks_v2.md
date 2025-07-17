# Concept Agent Day 1 开发任务清单 V2（复用公共模块版）

## 重要提醒
1. **严格复用现有公共模块**，不要重新实现
2. **测试数据需要确认**，不要自己编造
3. **坚持设计要点**，不要偏离

## 任务概览
第一天目标：搭建Concept Agent基础框架，最大程度复用现有模块

## 具体任务列表

### 1. 创建目录结构（30分钟）
```bash
# 创建以下目录和文件
agents/concept_agent_modular.py      # 主Agent文件

utils/concept/                       # 概念专用工具目录
├── __init__.py
├── concept_matcher.py              # 概念匹配器（新增）
├── scoring_config.py               # 评分配置（新增）
├── concept_data_collector.py       # 概念数据采集器（新增）
└── concept_scorer.py               # 概念评分器（新增）

tests/
├── test_concept_agent.py           # Agent主测试
└── test_concept_tools.py           # 工具类测试
```

### 2. 创建主Agent框架（2小时）

创建 `agents/concept_agent_modular.py`:

```python
"""
Concept Agent - 概念股分析专家
负责概念股的智能发现、分析和推荐

设计要点：
1. 评分系统：概念关联度(40%) + 资金流向(30%) + 技术形态(30%)
2. 两次LLM调用：概念扩展 + 报告生成
3. 17:00盘后更新，失败重试3次
"""

import asyncio
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime

from langchain.prompts import ChatPromptTemplate
from langchain_community.chat_models import ChatDeepSeek
from langchain_core.output_parsers import JsonOutputParser

from database.mysql_connector import MySQLConnector

# 复用现有公共模块
from utils.parameter_extractor import ParameterExtractor, ExtractedParams
from utils.unified_stock_validator import UnifiedStockValidator
from utils.date_intelligence import DateIntelligence
from utils.agent_response import create_agent_response
from utils.error_handler import ErrorHandler
from utils.result_formatter import ResultFormatter
from utils.logger import setup_logger

# 概念专用模块
from utils.concept.concept_matcher import ConceptMatcher
from utils.concept.scoring_config import ScoringConfigManager
from utils.concept.concept_data_collector import ConceptDataCollector
from utils.concept.concept_scorer import ConceptScorer

# 配置日志
logger = setup_logger("concept_agent")

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
        
        # 复用的公共组件
        self.param_extractor = ParameterExtractor()
        self.stock_validator = UnifiedStockValidator()
        self.date_intelligence = DateIntelligence()
        self.error_handler = ErrorHandler()
        self.result_formatter = ResultFormatter()
        
        # 概念专用组件
        self.concept_matcher = ConceptMatcher(self.db, self.llm)
        self.scoring_manager = ScoringConfigManager()
        self.data_collector = ConceptDataCollector(self.db)
        self.concept_scorer = ConceptScorer(self.scoring_manager)
        
        # 统计信息
        self.stats = {
            "query_count": 0,
            "success_count": 0,
            "cache_hits": 0,
            "avg_response_time": 0
        }
        
        logger.info("Concept Agent 初始化完成")
    
    async def analyze_concept(self, query: str) -> Dict:
        """
        分析概念股 - 主入口
        
        设计要点：
        1. 支持三种输入：关键词、概念查询、新闻文本
        2. 两次LLM调用：概念扩展、报告生成
        3. 三维评分系统
        """
        start_time = datetime.now()
        self.stats["query_count"] += 1
        
        try:
            # 1. 参数提取（复用现有模块）
            extracted_params = self._extract_query_params(query)
            
            # 2. 输入类型识别
            input_type = self._detect_input_type(query)
            logger.info(f"输入类型: {input_type}")
            
            # 3. 概念扩展（第一次LLM调用）
            matched_concepts = await self.concept_matcher.expand_concepts(
                query, input_type
            )
            
            if not matched_concepts:
                return create_agent_response(
                    success=False,
                    message="未找到匹配的概念板块",
                    data={},
                    agent_name="ConceptAgent"
                )
            
            logger.info(f"匹配到概念: {matched_concepts}")
            
            # 4. 获取概念成分股
            all_stocks = await self.data_collector.get_concept_stocks(
                matched_concepts
            )
            
            if not all_stocks:
                return create_agent_response(
                    success=False,
                    message="未找到相关概念股",
                    data={},
                    agent_name="ConceptAgent"
                )
            
            logger.info(f"找到 {len(all_stocks)} 只相关股票")
            
            # 5. 数据采集（并行）
            stock_data = await self.data_collector.collect_all_data(
                all_stocks, matched_concepts
            )
            
            # 6. 评分计算
            scored_stocks = await self.concept_scorer.calculate_scores(
                stock_data
            )
            
            # 7. 排序和筛选
            top_stocks = self._rank_and_filter(scored_stocks)
            
            # 8. 生成报告（第二次LLM调用）
            report = await self._generate_report(
                top_stocks, 
                matched_concepts[0],  # 主概念
                len(all_stocks)
            )
            
            # 9. 格式化结果（复用ResultFormatter）
            formatted_result = self._format_result(
                query, matched_concepts, top_stocks, report
            )
            
            self.stats["success_count"] += 1
            
            return create_agent_response(
                success=True,
                message="概念股分析完成",
                data=formatted_result,
                agent_name="ConceptAgent"
            )
            
        except Exception as e:
            # 使用统一错误处理
            return self.error_handler.handle_error(
                error=e,
                context={
                    "agent": "ConceptAgent",
                    "query": query,
                    "stage": "analyze_concept"
                }
            )
    
    def _extract_query_params(self, query: str) -> ExtractedParams:
        """提取查询参数（复用现有模块）"""
        return self.param_extractor.extract_all(query)
    
    def _detect_input_type(self, query: str) -> str:
        """检测输入类型"""
        # 长文本判定为新闻
        if len(query) > 100:
            return "news"
        
        # 包含概念股等关键词
        concept_patterns = ['概念股', '概念', '板块']
        for pattern in concept_patterns:
            if pattern in query:
                return "concept_query"
        
        # 默认为关键词
        return "keyword"
    
    def _rank_and_filter(self, stocks: List[Dict], top_n: int = 20) -> List[Dict]:
        """排序和筛选"""
        # 按总分降序排序
        sorted_stocks = sorted(
            stocks, 
            key=lambda x: x.get('total_score', 0), 
            reverse=True
        )
        return sorted_stocks[:top_n]
    
    async def _generate_report(
        self, 
        stocks: List[Dict], 
        concept: str, 
        total: int
    ) -> str:
        """生成分析报告（第二次LLM调用）"""
        # TODO: Day 7实现
        return f"## {concept}概念股分析报告\\n\\n找到{total}只相关股票。"
    
    def _format_result(
        self, 
        query: str,
        concepts: List[str],
        stocks: List[Dict],
        report: str
    ) -> Dict:
        """格式化结果"""
        # 使用ResultFormatter进行表格格式化
        if stocks:
            # 准备表格数据
            table_data = []
            for stock in stocks[:10]:  # TOP10
                table_data.append({
                    "股票代码": stock.get("ts_code", ""),
                    "股票名称": stock.get("name", ""),
                    "概念关联": f"{stock.get('concept_relevance_score', 0):.1f}",
                    "资金流向": f"{stock.get('money_flow_score', 0):.1f}",
                    "技术形态": f"{stock.get('technical_pattern_score', 0):.1f}",
                    "综合得分": f"{stock.get('total_score', 0):.1f}"
                })
            
            # 生成表格
            score_table = self.result_formatter.format_as_table(
                table_data,
                title="概念股评分排名"
            )
        else:
            score_table = ""
        
        return {
            "query": query,
            "matched_concepts": concepts,
            "report": report,
            "score_table": score_table,
            "top_stocks": stocks[:5],  # TOP5详细信息
            "metadata": {
                "total_stocks": len(stocks),
                "update_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
        }
    
    def get_stats(self) -> Dict:
        """获取统计信息"""
        return self.stats
```

### 3. 创建概念匹配器（1.5小时）

创建 `utils/concept/concept_matcher.py`:

```python
"""
概念匹配器
负责概念扩展和匹配
"""

import json
from typing import List, Dict, Optional
from langchain.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser

from utils.logger import setup_logger

logger = setup_logger("concept_matcher")

class ConceptMatcher:
    """概念匹配器"""
    
    def __init__(self, db, llm):
        self.db = db
        self.llm = llm
        self.json_parser = JsonOutputParser()
        
        # 缓存所有概念列表
        self._concept_cache = None
    
    async def expand_concepts(self, query: str, input_type: str) -> List[str]:
        """
        扩展概念（第一次LLM调用）
        
        设计要点：
        - 从系统概念列表中匹配相关概念
        - 支持新闻文本的概念提取
        """
        # 获取系统所有概念
        system_concepts = await self._get_all_concepts()
        
        if input_type == "news":
            prompt = ChatPromptTemplate.from_template("""
分析以下新闻内容，提取关键概念和相关板块。

新闻内容：{query}

系统内所有概念板块（部分）：{concepts}

任务：
1. 提取新闻中的核心概念关键词
2. 从系统概念板块中匹配相关板块（必须是系统中存在的）
3. 最多返回5个最相关的概念

返回JSON格式：
{{
    "core_keywords": ["关键词1", "关键词2"],
    "matched_concepts": ["概念1", "概念2", "概念3"]
}}
""")
        else:
            prompt = ChatPromptTemplate.from_template("""
用户查询：{query}

系统内所有概念板块（部分）：{concepts}

请从系统概念板块中选出与用户查询最相关的板块。
最多返回5个相关概念。

返回JSON格式：
{{
    "matched_concepts": ["概念1", "概念2", "概念3"]
}}
""")
        
        try:
            # 只显示部分概念避免prompt过长
            sample_concepts = system_concepts[:100] if len(system_concepts) > 100 else system_concepts
            
            chain = prompt | self.llm | self.json_parser
            result = await chain.ainvoke({
                "query": query,
                "concepts": ", ".join(sample_concepts)
            })
            
            matched = result.get("matched_concepts", [])
            
            # 验证匹配的概念确实存在
            valid_concepts = [c for c in matched if c in system_concepts]
            
            return valid_concepts
            
        except Exception as e:
            logger.error(f"LLM概念扩展失败: {e}")
            # 降级到简单匹配
            return self._simple_match(query, system_concepts)
    
    async def _get_all_concepts(self) -> List[str]:
        """获取所有概念列表"""
        if self._concept_cache is not None:
            return self._concept_cache
        
        # TODO: 需要确认实际的表名和字段名
        # 这里需要向用户确认
        query = """
        SELECT DISTINCT name 
        FROM tu_ths_index
        UNION
        SELECT DISTINCT index_name 
        FROM tu_dc_index
        """
        
        # 暂时返回模拟数据，需要确认
        self._concept_cache = []
        return self._concept_cache
    
    def _simple_match(self, query: str, concepts: List[str]) -> List[str]:
        """简单匹配（降级方案）"""
        matched = []
        query_lower = query.lower()
        
        for concept in concepts:
            if any(keyword in concept.lower() for keyword in query_lower.split()):
                matched.append(concept)
        
        return matched[:5]  # 最多返回5个
```

### 4. 创建评分配置（1小时）

创建 `utils/concept/scoring_config.py`:

```python
"""
概念股评分配置
支持灵活的配置管理

设计要点：
- 概念关联度(40%)
- 资金流向(30%)
- 技术形态(30%)
"""

from typing import Dict, List, Any

# 默认评分配置
DEFAULT_SCORING_CONFIG = {
    "concept_relevance": {
        "total_score": 40,
        "enabled": True,
        "items": [
            {
                "id": "board_membership",
                "name": "板块成分股",
                "score": 10,
                "enabled": True,
                "description": "在概念板块成分股中"
            },
            {
                "id": "board_leading_limit",
                "name": "板块率先涨停",
                "score": 10,
                "enabled": True,
                "params": {"days": 5, "rank": 3},
                "description": "最近5天内板块前3个涨停"
            },
            {
                "id": "financial_mention",
                "name": "财报提及",
                "score": 5,
                "enabled": True,
                "description": "财报提及相关概念"
            },
            {
                "id": "qa_mention",
                "name": "互动平台提及",
                "score": 5,
                "enabled": True,
                "description": "董秘互动平台提及"
            },
            {
                "id": "announcement_mention",
                "name": "公告提及",
                "score": 5,
                "enabled": True,
                "description": "公司公告提及"
            },
            {
                "id": "board_activity",
                "name": "板块活跃度",
                "score": 5,
                "enabled": True,
                "params": {"top_percent": 20},
                "description": "板块涨幅排名前20%"
            }
        ]
    },
    "money_flow": {
        "total_score": 30,
        "enabled": True,
        "items": [
            {
                "id": "daily_weekly_inflow",
                "name": "日周双净流入",
                "score": 10,
                "enabled": True,
                "description": "日和周均净流入"
            },
            {
                "id": "inflow_ratio_rank",
                "name": "净流入占比排名",
                "score": 10,
                "enabled": True,
                "tiers": [
                    {"top_percent": 10, "score": 10},
                    {"top_percent": 30, "score": 7},
                    {"top_percent": 50, "score": 5}
                ],
                "description": "净流入占流通市值比例在概念内排名"
            },
            {
                "id": "board_money_performance",
                "name": "板块资金表现",
                "score": 5,
                "enabled": True,
                "description": "所属板块资金流入表现"
            },
            {
                "id": "continuous_inflow",
                "name": "连续净流入",
                "score": 5,
                "enabled": True,
                "tiers": [
                    {"days": 5, "score": 5},
                    {"days": 3, "score": 3}
                ],
                "description": "连续多天净流入"
            }
        ]
    },
    "technical_pattern": {
        "total_score": 30,
        "enabled": True,
        "items": [
            {
                "id": "macd_status",
                "name": "MACD状态",
                "score": 15,
                "enabled": True,
                "sub_items": [
                    {
                        "name": "macd_above_water",
                        "score": 10,
                        "condition": "MACD>0 AND DIF>0",
                        "description": "MACD水上红柱"
                    },
                    {
                        "name": "first_in_board",
                        "score": 5,
                        "params": {"days": 2},
                        "description": "板块内率先水上"
                    }
                ]
            },
            {
                "id": "ma_arrangement",
                "name": "均线排列",
                "score": 15,
                "enabled": True,
                "condition": "MA5>MA10",
                "optional_condition": "MA5>MA10>MA20",
                "description": "均线多头排列"
            }
        ]
    }
}

class ScoringConfigManager:
    """评分配置管理器"""
    
    def __init__(self, config: Dict = None):
        self.config = config or DEFAULT_SCORING_CONFIG.copy()
    
    def get_config(self) -> Dict:
        """获取当前配置"""
        return self.config
    
    def get_category_config(self, category: str) -> Dict:
        """获取某个维度的配置"""
        return self.config.get(category, {})
    
    def enable_item(self, category: str, item_id: str) -> None:
        """启用某个评分项"""
        if category in self.config:
            items = self.config[category].get("items", [])
            for item in items:
                if item.get("id") == item_id:
                    item["enabled"] = True
                    break
    
    def disable_item(self, category: str, item_id: str) -> None:
        """禁用某个评分项"""
        if category in self.config:
            items = self.config[category].get("items", [])
            for item in items:
                if item.get("id") == item_id:
                    item["enabled"] = False
                    break
    
    def update_score(self, category: str, item_id: str, score: float) -> None:
        """更新评分值"""
        if category in self.config:
            items = self.config[category].get("items", [])
            for item in items:
                if item.get("id") == item_id:
                    item["score"] = score
                    break
```

### 5. 创建数据采集器框架（1小时）

创建 `utils/concept/concept_data_collector.py`:

```python
"""
概念数据采集器
负责采集概念股相关的所有数据
"""

import asyncio
from typing import List, Dict, Optional
from datetime import datetime, timedelta

from utils.logger import setup_logger

logger = setup_logger("concept_data_collector")

class ConceptDataCollector:
    """概念数据采集器"""
    
    def __init__(self, db):
        self.db = db
        self._concept_members_cache = {}
    
    async def get_concept_stocks(self, concepts: List[str]) -> List[str]:
        """
        获取概念成分股
        
        TODO: 需要确认实际的表结构
        """
        all_stocks = set()
        
        for concept in concepts:
            # 检查缓存
            if concept in self._concept_members_cache:
                stocks = self._concept_members_cache[concept]
            else:
                # TODO: 需要确认实际查询
                stocks = await self._query_concept_members(concept)
                self._concept_members_cache[concept] = stocks
            
            all_stocks.update(stocks)
        
        return list(all_stocks)
    
    async def _query_concept_members(self, concept: str) -> List[str]:
        """
        查询概念成分股
        
        TODO: 需要确认实际的表名和字段
        """
        # 暂时返回空列表，需要确认
        logger.warning(f"需要实现概念成分股查询: {concept}")
        return []
    
    async def collect_all_data(
        self, 
        stocks: List[str], 
        concepts: List[str]
    ) -> List[Dict]:
        """
        并行采集所有数据
        
        设计要点：
        - 并行采集提高效率
        - 包含资金流向、技术指标等数据
        """
        # 创建并行任务
        tasks = []
        
        for stock in stocks:
            # 基础信息
            task1 = self._get_stock_info(stock)
            # 资金流向
            task2 = self._get_money_flow(stock)
            # 技术指标
            task3 = self._get_technical_indicators(stock)
            # 涨停信息
            task4 = self._get_limit_info(stock, concepts)
            
            tasks.extend([task1, task2, task3, task4])
        
        # 并行执行
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # 整理数据
        stock_data_list = []
        # TODO: 实现数据整理逻辑
        
        return stock_data_list
    
    async def _get_stock_info(self, ts_code: str) -> Dict:
        """获取股票基础信息"""
        # TODO: 实现
        return {"ts_code": ts_code}
    
    async def _get_money_flow(self, ts_code: str) -> Dict:
        """获取资金流向数据"""
        # TODO: 实现
        return {}
    
    async def _get_technical_indicators(self, ts_code: str) -> Dict:
        """获取技术指标数据"""
        # TODO: 实现
        return {}
    
    async def _get_limit_info(self, ts_code: str, concepts: List[str]) -> Dict:
        """获取涨停信息"""
        # TODO: 实现
        return {}
```

### 6. 创建评分器框架（1小时）

创建 `utils/concept/concept_scorer.py`:

```python
"""
概念股评分器
负责计算三维评分

设计要点：
- 概念关联度(40%)
- 资金流向(30%)
- 技术形态(30%)
"""

from typing import List, Dict, Any
from utils.logger import setup_logger

logger = setup_logger("concept_scorer")

class ConceptScorer:
    """概念股评分器"""
    
    def __init__(self, scoring_manager):
        self.scoring_manager = scoring_manager
    
    async def calculate_scores(self, stock_data_list: List[Dict]) -> List[Dict]:
        """
        计算所有股票的评分
        
        返回包含评分的股票列表
        """
        scored_stocks = []
        
        for stock_data in stock_data_list:
            # 计算三个维度的得分
            concept_score = self._calculate_concept_relevance(stock_data)
            money_score = self._calculate_money_flow(stock_data)
            tech_score = self._calculate_technical_pattern(stock_data)
            
            # 总分
            total_score = concept_score + money_score + tech_score
            
            # 添加评分信息
            stock_data.update({
                "concept_relevance_score": concept_score,
                "money_flow_score": money_score,
                "technical_pattern_score": tech_score,
                "total_score": total_score,
                "score_details": {
                    "concept": self._get_score_details("concept_relevance", stock_data),
                    "money": self._get_score_details("money_flow", stock_data),
                    "technical": self._get_score_details("technical_pattern", stock_data)
                }
            })
            
            scored_stocks.append(stock_data)
        
        return scored_stocks
    
    def _calculate_concept_relevance(self, stock_data: Dict) -> float:
        """
        计算概念关联度得分（40分）
        
        评分项：
        - 板块成分股(10分)
        - 板块率先涨停(10分)
        - 财报提及(5分)
        - 互动平台提及(5分)
        - 公告提及(5分)
        - 板块活跃度(5分)
        """
        config = self.scoring_manager.get_category_config("concept_relevance")
        score = 0.0
        
        # TODO: 实现具体评分逻辑
        # 这里需要根据stock_data中的数据计算得分
        
        return min(score, config.get("total_score", 40))
    
    def _calculate_money_flow(self, stock_data: Dict) -> float:
        """
        计算资金流向得分（30分）
        
        评分项：
        - 日周双净流入(10分)
        - 净流入占比排名(10分)
        - 板块资金表现(5分)
        - 连续净流入(5分)
        """
        config = self.scoring_manager.get_category_config("money_flow")
        score = 0.0
        
        # TODO: 实现具体评分逻辑
        
        return min(score, config.get("total_score", 30))
    
    def _calculate_technical_pattern(self, stock_data: Dict) -> float:
        """
        计算技术形态得分（30分）
        
        评分项：
        - MACD状态(15分)
        - 均线排列(15分)
        """
        config = self.scoring_manager.get_category_config("technical_pattern")
        score = 0.0
        
        # TODO: 实现具体评分逻辑
        
        return min(score, config.get("total_score", 30))
    
    def _get_score_details(self, category: str, stock_data: Dict) -> Dict:
        """获取评分明细"""
        # TODO: 返回详细的评分项和得分
        return {}
```

### 7. 创建测试文件（30分钟）

创建 `test_concept_basic.py`:

```python
#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Concept Agent 基础功能测试
测试复用的公共模块
"""

import asyncio
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.parameter_extractor import ParameterExtractor
from utils.unified_stock_validator import UnifiedStockValidator
from utils.concept.scoring_config import ScoringConfigManager

def test_parameter_extraction():
    """测试参数提取（复用现有模块）"""
    print("=== 测试参数提取器 ===")
    extractor = ParameterExtractor()
    
    # 测试概念相关查询
    test_queries = [
        "新能源汽车概念股",
        "锂电池板块龙头股",
        "半导体概念最近5天涨幅排名",
        "固态电池概念股资金流入情况"
    ]
    
    for query in test_queries:
        params = extractor.extract_all(query)
        print(f"\n查询: {query}")
        print(f"板块: {params.sector}")
        print(f"限制: {params.limit}")
        print(f"日期: {params.date}")

def test_stock_validation():
    """测试股票验证（复用现有模块）"""
    print("\n\n=== 测试股票验证 ===")
    validator = UnifiedStockValidator()
    
    # 需要确认的测试数据
    test_stocks = [
        "比亚迪",      # 需要确认实际股票代码
        "宁德时代",    # 需要确认实际股票代码
        "002594.SZ",   # 需要确认是否正确
        "300750.SZ"    # 需要确认是否正确
    ]
    
    for stock in test_stocks:
        result = validator.validate_stock(stock)
        print(f"\n输入: {stock}")
        print(f"验证结果: {result}")

def test_scoring_config():
    """测试评分配置"""
    print("\n\n=== 测试评分配置 ===")
    manager = ScoringConfigManager()
    config = manager.get_config()
    
    print("\n评分体系：")
    for category, settings in config.items():
        print(f"\n{category} (总分: {settings['total_score']}分)")
        for item in settings.get('items', []):
            status = "✓" if item.get('enabled', True) else "✗"
            print(f"  {status} {item['name']}: {item['score']}分")

async def test_concept_agent():
    """测试Concept Agent基础框架"""
    print("\n\n=== 测试Concept Agent ===")
    
    try:
        from agents.concept_agent_modular import ConceptAgentModular
        agent = ConceptAgentModular()
        
        # 测试基础查询
        result = await agent.analyze_concept("新能源汽车概念股")
        
        print(f"查询成功: {result['success']}")
        print(f"Agent: {result['agent_name']}")
        
        # 测试统计信息
        stats = agent.get_stats()
        print(f"\n统计信息: {stats}")
        
    except Exception as e:
        print(f"测试失败: {e}")
        import traceback
        traceback.print_exc()

def main():
    """主测试函数"""
    print("Concept Agent Day 1 测试")
    print("=" * 50)
    
    # 测试复用的模块
    test_parameter_extraction()
    test_stock_validation()
    
    # 测试新增的模块
    test_scoring_config()
    
    # 测试Agent
    asyncio.run(test_concept_agent())
    
    print("\n\n测试完成!")

if __name__ == "__main__":
    main()
```

## 需要向用户确认的数据

### 1. 概念板块表结构
```sql
-- 需要确认这些表的实际结构
-- tu_ths_index: 同花顺概念指数表
-- tu_dc_index: 东财概念指数表
-- tu_ths_member: 同花顺概念成分股
-- tu_dc_member: 东财概念成分股

-- 需要确认的字段：
-- 概念代码字段名？
-- 概念名称字段名？
-- 成分股代码字段名？
```

### 2. 测试用概念名称
```python
# 需要确认实际存在的概念名称
test_concepts = [
    "新能源汽车",   # 是否存在？
    "锂电池",       # 是否存在？
    "固态电池",     # 是否存在？
    "半导体",       # 是否存在？
    "人工智能"      # 是否存在？
]
```

### 3. 测试用股票数据
```python
# 需要确认这些股票的正确信息
test_stocks = {
    "比亚迪": "002594.SZ?",     # 正确的代码？
    "宁德时代": "300750.SZ?",   # 正确的代码？
    "赣锋锂业": "??????.SZ?",   # 需要确认
    "天齐锂业": "??????.SZ?"    # 需要确认
}
```

## 检查清单

- [ ] 严格复用现有公共模块
- [ ] 不重新实现已有功能
- [ ] 测试数据需要确认
- [ ] 坚持设计要点（40%+30%+30%）
- [ ] 保持模块化和可配置性

## 提醒

1. **不要忘记设计要点**：
   - 概念关联度(40%) + 资金流向(30%) + 技术形态(30%)
   - 17:00盘后更新，失败重试3次
   - 两次LLM调用：概念扩展 + 报告生成

2. **复用优先**：
   - 参数提取用ParameterExtractor
   - 股票验证用UnifiedStockValidator
   - 日期处理用DateIntelligence
   - 错误处理用ErrorHandler
   - 结果格式化用ResultFormatter

3. **测试数据确认**：
   - 所有概念名称需要确认
   - 所有股票代码需要确认
   - 表结构和字段需要确认