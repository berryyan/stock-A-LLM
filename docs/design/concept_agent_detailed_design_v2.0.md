# Concept Agent 详细设计文档 v2.0

版本：v2.0  
创建时间：2025-07-16  
作者：Stock Analysis System Team

## 1. 概述

Concept Agent（概念股分析专家）是股票分析系统的核心Agent之一，专门负责概念股的智能发现、分析和推荐。通过整合多源概念数据、资金流向分析和技术指标筛选，为用户提供基于事实依据的概念股投资建议。

### 1.1 核心功能
- 概念识别：支持关键词、概念查询、新闻文本等多种输入
- 智能匹配：通过LLM扩展相关概念，提高查全率
- 多维评分：概念关联度(40%) + 资金流向(30%) + 技术形态(30%)
- 专业输出：生成包含详细评分和分析的投资报告

### 1.2 技术特点
- 配置化评分系统，灵活调整评分规则
- 三级缓存架构，平衡性能和实时性
- 支持新闻文本解析，捕捉市场热点
- 盘后批量更新 + 按需实时更新

## 2. 系统架构

### 2.1 整体架构
```
Concept Agent
├── 输入处理层
│   ├── 输入类型识别（关键词/概念查询/新闻文本）
│   └── LLM概念扩展（第一次调用）
├── 数据采集层
│   ├── 概念板块数据（tu_ths_index, tu_dc_index）
│   ├── 成分股数据（tu_ths_member, tu_dc_member）
│   ├── 资金流向数据（tu_moneyflow_dc）
│   ├── 技术指标数据（Tushare stk_factor_pro API）
│   └── 补充数据（涨停、财报、公告、互动）
├── 评分计算层
│   ├── 概念关联度评分（40分）
│   ├── 资金流向评分（30分）
│   └── 技术形态评分（30分）
├── 结果生成层
│   ├── 评分排序
│   └── LLM报告生成（第二次调用）
└── 缓存管理层
    ├── 内存缓存（LRU）
    ├── 数据库缓存
    └── Redis缓存（第二阶段）
```

### 2.2 数据流程
1. 用户输入 → 输入类型识别
2. LLM概念扩展 → 获取相关概念列表
3. 并行数据采集 → 概念成分股 + 资金数据 + 技术数据
4. 评分计算 → 三维度评分汇总
5. 结果排序 → TOP5推荐 + 完整列表
6. LLM分析 → 生成专业报告

## 3. 输入处理设计

### 3.1 输入类型识别
```python
class ConceptInputProcessor:
    """概念输入处理器"""
    
    def process_input(self, user_input: str) -> Dict:
        """处理用户输入，识别类型"""
        input_type = self._detect_input_type(user_input)
        
        if input_type == "keyword":
            # 简单关键词："固态电池"
            return {"type": "keyword", "content": user_input}
            
        elif input_type == "concept_query":
            # 概念股查询："新能源汽车概念股"
            keyword = user_input.replace("概念股", "").strip()
            return {"type": "concept", "content": keyword}
            
        elif input_type == "news":
            # 新闻文本：长段落政策信息
            return {"type": "news", "content": user_input}
    
    def _detect_input_type(self, text: str) -> str:
        if len(text) > 100:  # 长文本判定为新闻
            return "news"
        elif "概念股" in text:
            return "concept_query"
        else:
            return "keyword"
```

### 3.2 LLM概念扩展（第一次调用）
```python
def expand_concepts(self, user_input: str, input_type: str) -> List[str]:
    """通过LLM扩展相关概念"""
    
    # 获取系统所有概念板块
    system_concepts = self.get_all_concept_names()
    
    if input_type == "news":
        prompt = f"""
        分析以下新闻内容，提取关键概念和相关板块：
        
        新闻内容：{user_input}
        
        系统内所有概念板块：{system_concepts}
        
        任务：
        1. 提取新闻中的核心概念关键词
        2. 从系统概念板块中匹配相关板块
        3. 识别可能的受益行业和细分领域
        
        返回JSON格式：
        {{
            "core_concepts": ["固态电池", "储能", "新能源汽车"],
            "matched_concepts": ["固态电池", "锂电池", "储能概念", "新能源汽车"],
            "analysis": "新闻主要涉及固态电池政策支持..."
        }}
        """
    else:
        prompt = f"""
        用户查询：{user_input}
        系统内所有概念板块：{system_concepts}
        
        请从系统概念板块中选出与用户查询相关的板块，返回JSON格式：
        {{
            "matched_concepts": ["新能源汽车", "锂电池", "充电桩", ...]
        }}
        """
    
    # 调用LLM
    response = self.llm.invoke(prompt)
    return self.parse_llm_response(response)
```

## 4. 评分系统设计

### 4.1 配置化评分架构
```python
# concept_scoring_config.py
SCORING_CONFIG = {
    "concept_relevance": {
        "total_score": 40,
        "items": [
            {
                "name": "board_membership",
                "description": "在概念板块成分股中",
                "score": 10,
                "enabled": True,
                "data_source": ["tu_ths_member", "tu_dc_member"]
            },
            {
                "name": "board_leading_limit",
                "description": "板块内率先涨停",
                "score": 10,
                "enabled": True,
                "params": {"days": 5},  # 可配置天数
                "data_source": ["tu_stk_limit"]
            },
            {
                "name": "financial_mention",
                "description": "财报提及相关概念",
                "score": 5,
                "enabled": True,
                "data_source": ["financial_reports"]
            },
            {
                "name": "qa_mention",
                "description": "互动平台提及",
                "score": 5,
                "enabled": True,
                "data_source": ["tu_irm_qa_sz", "tu_irm_qa_sh"]
            },
            {
                "name": "announcement_mention",
                "description": "公告提及",
                "score": 5,
                "enabled": True,
                "data_source": ["tu_anns_d"]
            },
            {
                "name": "board_activity",
                "description": "概念板块活跃度",
                "score": 5,
                "enabled": True,
                "params": {"top_percent": 20}
            }
        ]
    },
    "money_flow": {
        "total_score": 30,
        "items": [
            {
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
                "name": "board_money_performance",
                "description": "所属板块资金表现",
                "score": 5,
                "enabled": True
            },
            {
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
        "items": [
            {
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
                "name": "ma_arrangement",
                "description": "均线排列",
                "score": 15,
                "enabled": True,
                "condition": "MA5>MA10",
                "optional_condition": "MA5>MA10>MA20"  # 可配置升级
            }
        ]
    }
}
```

### 4.2 评分计算引擎
```python
class FlexibleScoringEngine:
    """灵活的评分引擎"""
    
    def calculate_score(self, stock_data: Dict, config: Dict = None) -> Dict:
        """计算股票综合得分"""
        config = config or SCORING_CONFIG
        scores = {}
        details = {}
        
        # 计算各维度得分
        for category, category_config in config.items():
            category_score = 0
            category_details = []
            
            for item in category_config["items"]:
                if not item.get("enabled", True):
                    continue
                
                # 计算单项得分
                item_score, item_detail = self._calculate_item_score(
                    stock_data, item
                )
                category_score += item_score
                category_details.append({
                    "name": item["description"],
                    "score": item_score,
                    "max_score": item["score"],
                    "detail": item_detail
                })
            
            # 确保不超过该维度总分
            scores[category] = min(category_score, category_config["total_score"])
            details[category] = category_details
        
        return {
            "scores": scores,
            "details": details,
            "total": sum(scores.values())
        }
```

## 5. 数据采集设计

### 5.1 技术指标数据采集
```python
class TechnicalDataCollector:
    """技术指标数据采集器"""
    
    async def collect_technical_data(self, ts_codes: List[str]) -> Dict:
        """采集技术指标数据"""
        # 检查缓存
        cached_data = await self.cache.get_batch(ts_codes)
        need_update = [code for code in ts_codes if code not in cached_data]
        
        if need_update:
            # 提示用户
            await self.notify_update(
                f"正在更新{len(need_update)}只股票的技术指标数据..."
            )
            
            # 批量获取
            for batch in self._batch_stocks(need_update, batch_size=50):
                df = pro.stk_factor_pro(
                    ts_code=','.join(batch),
                    start_date=self._get_start_date(21),  # 21天数据
                    end_date=self._get_today(),
                    fields='ts_code,trade_date,close_qfq,macd_qfq,macd_dif_qfq,macd_dea_qfq,ma_qfq_5,ma_qfq_10,ma_qfq_20'
                )
                
                # 缓存数据
                await self._cache_technical_data(df)
        
        return self._merge_data(cached_data, new_data)
```

### 5.2 盘后数据更新任务
```python
class DailyUpdateScheduler:
    """每日数据更新调度器"""
    
    def __init__(self):
        self.update_time = "17:00"  # 每天17:00更新
        self.retry_times = 3
        self.retry_interval = 30  # 分钟
    
    async def schedule_daily_update(self):
        """调度每日更新任务"""
        while True:
            now = datetime.now()
            
            # 检查是否是交易日
            if not self.is_trading_day(now.strftime('%Y%m%d')):
                await asyncio.sleep(3600)  # 非交易日每小时检查一次
                continue
            
            # 检查是否到更新时间
            if now.strftime('%H:%M') >= self.update_time:
                success = await self.update_all_data()
                
                if not success:
                    # 重试机制
                    for i in range(self.retry_times):
                        await asyncio.sleep(self.retry_interval * 60)
                        if await self.update_all_data():
                            break
                
                # 等待到第二天
                await self.wait_until_tomorrow()
            else:
                await asyncio.sleep(60)  # 每分钟检查一次
```

## 6. 缓存策略

### 6.1 三级缓存架构
```python
class ConceptCacheManager:
    """概念股缓存管理器"""
    
    def __init__(self):
        # L1: 内存缓存（5分钟）
        self.memory_cache = LRUCache(maxsize=1000)
        self.memory_ttl = 300
        
        # L2: 数据库缓存（永久）
        self.db_cache = DatabaseCache()
        
        # L3: Redis缓存（预留接口）
        self.redis_cache = None  # 第二阶段实现
    
    async def get(self, key: str) -> Optional[Dict]:
        """获取缓存数据"""
        # L1查询
        if key in self.memory_cache:
            if self._is_valid(self.memory_cache[key]):
                return self.memory_cache[key]['data']
        
        # L2查询
        db_data = await self.db_cache.get(key)
        if db_data:
            # 回填L1
            self.memory_cache[key] = {
                'data': db_data,
                'timestamp': datetime.now()
            }
            return db_data
        
        return None
```

### 6.2 交易日历缓存
```python
class TradingCalendarCache:
    """交易日历本地缓存"""
    
    def __init__(self, cache_file="data/trading_calendar.json"):
        self.cache_file = cache_file
        self.cache_data = self._load_cache()
    
    def get_trading_days(self, start_date: str, end_date: str) -> List[str]:
        """获取交易日列表"""
        # 检查缓存是否需要更新
        if self._need_update(end_date):
            self._update_cache()
        
        # 从缓存返回数据
        return [day for day in self.cache_data 
                if start_date <= day <= end_date]
    
    def _update_cache(self):
        """更新缓存，获取未来3个月数据"""
        end_date = (datetime.now() + timedelta(days=90)).strftime('%Y%m%d')
        df = pro.trade_cal(
            exchange='SSE',
            start_date='20250101',
            end_date=end_date
        )
        
        trading_days = df[df['is_open'] == 1]['cal_date'].tolist()
        with open(self.cache_file, 'w') as f:
            json.dump(trading_days, f)
```

## 7. 输出格式设计

### 7.1 标准输出格式
```markdown
## {concept_name}概念股分析报告

### 推荐股票TOP5（按综合得分排序）

1. **{stock_name}({ts_code})** - 综合得分：{total_score}分
   
   **概念关联度：{concept_score}/40分**
   - 板块成分股：{board_score}/10分（{board_detail}）
   - 板块率先涨停：{limit_score}/10分（{limit_detail}）
   - 财报提及：{financial_score}/5分（{financial_detail}）
   - 互动平台：{qa_score}/5分（{qa_detail}）
   - 公告提及：{ann_score}/5分（{ann_detail}）
   - 板块活跃度：{activity_score}/5分（{activity_detail}）
   
   **资金流向：{money_score}/30分**
   - 日周双流入：{flow_score}/10分（日流入{daily}亿，周流入{weekly}亿）
   - 净流入占比排名：{ratio_score}/10分（概念内排名第{rank}，前{percent}%）
   - 板块资金表现：{board_money_score}/5分（{board_money_detail}）
   - 连续流入：{continuous_score}/5分（连续{days}天净流入）
   
   **技术形态：{tech_score}/30分**
   - MACD状态：{macd_score}/15分
     - 水上红柱：{macd_above}/10分（MACD={macd}, DIF={dif}）
     - 板块首发：{macd_first}/5分（{macd_first_detail}）
   - 均线排列：{ma_score}/15分（MA5={ma5} > MA10={ma10}）
   
   **推荐理由**：{llm_analysis}

[其他4只股票类似展示...]

### 概念股完整评分明细表

[详细表格展示所有股票的评分明细]

### 概念板块分析
{llm_board_analysis}

### 投资策略建议
{llm_strategy}

### 风险提示
{llm_risk}

*数据更新时间：{update_time}*
*注：评分系统采用动态权重，具体分值可能根据市场情况调整*
```

### 7.2 LLM报告生成（第二次调用）
```python
def generate_report(self, scored_stocks: List[Dict], concept_name: str) -> str:
    """生成分析报告"""
    
    top5_stocks = scored_stocks[:5]
    
    prompt = f"""
    基于以下{concept_name}概念股的评分数据，生成专业的投资分析报告。
    
    TOP5股票数据：
    {json.dumps(top5_stocks, ensure_ascii=False)}
    
    请包含以下内容：
    1. 每只股票的推荐理由（基于评分数据）
    2. 概念板块整体分析（政策面、基本面、技术面）
    3. 短中长期投资策略建议
    4. 风险提示（市场风险、政策风险、技术风险等）
    
    要求：
    - 基于数据事实进行分析
    - 语言专业、逻辑清晰
    - 突出重点、详略得当
    """
    
    response = self.llm.invoke(prompt)
    return self.format_report(response, scored_stocks)
```

## 8. 错误处理与降级策略

### 8.1 错误处理机制
```python
class ConceptAgentErrorHandler:
    """错误处理器"""
    
    def handle_error(self, error: Exception, context: Dict) -> Dict:
        """统一错误处理"""
        
        if isinstance(error, DataNotFoundError):
            return {
                "success": False,
                "error": "未找到相关概念数据",
                "suggestion": "请检查概念名称是否正确"
            }
        
        elif isinstance(error, APILimitError):
            return {
                "success": False,
                "error": "API调用超限",
                "suggestion": "请稍后再试或使用缓存数据"
            }
        
        elif isinstance(error, LLMError):
            # LLM调用失败，降级到规则匹配
            return self.fallback_to_rule_based(context)
        
        else:
            logger.error(f"未知错误: {error}", exc_info=True)
            return {
                "success": False,
                "error": "系统错误",
                "suggestion": "请联系管理员"
            }
```

### 8.2 降级策略
```python
def fallback_to_rule_based(self, context: Dict) -> Dict:
    """降级到基于规则的匹配"""
    # 使用关键词匹配代替LLM
    matched_concepts = self.rule_based_matcher.match(
        context['user_input']
    )
    
    # 使用简化评分代替完整评分
    simplified_scores = self.simplified_scorer.score(
        matched_concepts
    )
    
    return {
        "success": True,
        "data": simplified_scores,
        "message": "使用简化匹配模式"
    }
```

## 9. 性能优化

### 9.1 并发处理
```python
async def process_concepts_parallel(self, concepts: List[str]) -> Dict:
    """并行处理多个概念"""
    tasks = []
    
    for concept in concepts:
        # 并行获取成分股
        task1 = self.get_concept_members(concept)
        # 并行获取资金数据
        task2 = self.get_money_flow_data(concept)
        # 并行获取技术数据
        task3 = self.get_technical_data(concept)
        
        tasks.extend([task1, task2, task3])
    
    results = await asyncio.gather(*tasks, return_exceptions=True)
    return self.merge_results(results)
```

### 9.2 批量优化
```python
def batch_calculate_scores(self, stocks: List[str], batch_size: int = 100):
    """批量计算评分"""
    all_scores = []
    
    for i in range(0, len(stocks), batch_size):
        batch = stocks[i:i + batch_size]
        
        # 批量获取数据
        batch_data = self.get_batch_data(batch)
        
        # 批量计算
        batch_scores = self.calculate_batch_scores(batch_data)
        
        all_scores.extend(batch_scores)
    
    return all_scores
```

## 10. 监控与日志

### 10.1 性能监控
```python
class ConceptAgentMonitor:
    """性能监控器"""
    
    def __init__(self):
        self.metrics = {
            'query_count': 0,
            'success_count': 0,
            'avg_response_time': 0,
            'cache_hit_rate': 0
        }
    
    @timing_decorator
    async def monitor_query(self, func, *args, **kwargs):
        """监控查询性能"""
        start_time = time.time()
        
        try:
            result = await func(*args, **kwargs)
            self.metrics['success_count'] += 1
            return result
        except Exception as e:
            logger.error(f"查询失败: {e}")
            raise
        finally:
            self.metrics['query_count'] += 1
            elapsed = time.time() - start_time
            self._update_avg_time(elapsed)
```

### 10.2 日志记录
```python
# 日志配置
LOGGING_CONFIG = {
    'version': 1,
    'handlers': {
        'file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': 'logs/concept_agent.log',
            'maxBytes': 10485760,  # 10MB
            'backupCount': 5,
            'formatter': 'detailed'
        }
    },
    'loggers': {
        'concept_agent': {
            'handlers': ['file'],
            'level': 'INFO'
        }
    }
}
```

## 11. 测试策略

### 11.1 单元测试
```python
# tests/test_concept_agent.py
class TestConceptAgent:
    """Concept Agent单元测试"""
    
    def test_input_processor(self):
        """测试输入处理"""
        processor = ConceptInputProcessor()
        
        # 测试关键词
        assert processor.process_input("固态电池")['type'] == 'keyword'
        
        # 测试概念查询
        assert processor.process_input("新能源汽车概念股")['type'] == 'concept'
        
        # 测试新闻文本
        long_text = "国家部委..." * 50
        assert processor.process_input(long_text)['type'] == 'news'
    
    def test_scoring_engine(self):
        """测试评分引擎"""
        engine = FlexibleScoringEngine()
        
        test_data = {
            'is_member': True,
            'has_limit': True,
            'daily_inflow': 1000000,
            'macd': 0.5
        }
        
        scores = engine.calculate_score(test_data)
        assert scores['total'] <= 100
```

### 11.2 集成测试
```python
async def test_end_to_end():
    """端到端测试"""
    agent = ConceptAgent()
    
    # 测试完整流程
    result = await agent.analyze("新能源汽车概念股")
    
    assert result['success'] == True
    assert len(result['data']['recommendations']) >= 5
    assert 'report' in result['data']
```

## 12. 部署计划

### 12.1 第一阶段（核心功能）
- 实现基本的概念匹配和评分
- 使用内存缓存 + 数据库缓存
- 支持关键词和概念查询
- 基础的LLM集成

### 12.2 第二阶段（功能增强）
- 新闻文本解析能力
- Redis缓存集成
- 更丰富的评分维度
- 性能优化和监控

### 12.3 第三阶段（智能优化）
- 机器学习优化评分权重
- 实时数据集成
- 个性化推荐
- A/B测试框架

---

文档版本：v2.0  
最后更新：2025-07-16