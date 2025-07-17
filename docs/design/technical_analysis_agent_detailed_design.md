# Technical Analysis Agent 详细设计文档

版本：v1.0  
创建时间：2025-07-13  
作者：Stock Analysis System Team

## 1. 概述

### 1.1 背景

Technical Analysis Agent是v2.4.0计划中的首个新Agent，旨在提供专业的技术分析功能。该Agent将基于现有的模块化架构，提供快速、准确的技术指标查询和分析服务。

### 1.2 目标

- **性能目标**：常用指标查询<0.1秒，高级指标<2秒
- **功能目标**：支持20+种技术指标，智能形态识别，买卖信号提示
- **质量目标**：测试覆盖率>90%，查询准确率100%

### 1.3 设计原则

- **模块化设计**：继承现有的统一模块体系
- **混合模式**：数据库存储（高频）+ API调用（低频）
- **渐进式开发**：从基础指标到高级功能逐步实现
- **向后兼容**：不影响现有系统功能

## 2. 技术架构

### 2.1 系统集成

```
用户查询
    ↓
HybridAgent (路由)
    ↓
TechnicalAgentModular
    ├── ParameterExtractor (参数提取)
    ├── QueryValidator (参数验证)
    ├── TechnicalAnalyzer (核心分析)
    │   ├── DatabaseQuery (快速路径)
    │   └── APIQuery (高级指标)
    └── ResultFormatter (结果格式化)
```

### 2.2 核心组件

#### 2.2.1 TechnicalAgentModular

```python
class TechnicalAgentModular:
    """技术分析Agent模块化版本"""
    
    def __init__(self):
        self.parameter_extractor = ParameterExtractor()
        self.query_validator = QueryValidator()
        self.technical_analyzer = TechnicalAnalyzer()
        self.result_formatter = ResultFormatter()
        self.error_handler = ErrorHandler()
    
    async def process_query(self, query: str) -> AgentResponse:
        """处理技术分析查询"""
        try:
            # 1. 参数提取
            params = self.parameter_extractor.extract(query)
            
            # 2. 参数验证
            validation_result = self.query_validator.validate(
                params, template_type="technical"
            )
            
            # 3. 技术分析
            if self._is_quick_query(params):
                result = await self.technical_analyzer.quick_query(params)
            else:
                result = await self.technical_analyzer.advanced_query(params)
            
            # 4. 结果格式化
            formatted_result = self.result_formatter.format(result)
            
            return AgentResponse.success(formatted_result)
            
        except Exception as e:
            return self.error_handler.handle(e)
```

#### 2.2.2 TechnicalAnalyzer

```python
class TechnicalAnalyzer:
    """技术分析核心模块"""
    
    def __init__(self):
        self.db_connector = MySQLConnector()
        self.api_client = TechnicalAPIClient()
        self.cache_manager = CacheManager()
        self.pattern_recognizer = PatternRecognizer()
    
    async def quick_query(self, params: Dict) -> Dict:
        """快速查询（数据库）"""
        # 支持的快速查询类型
        query_types = {
            "ma": self._query_ma,           # 均线
            "macd": self._query_macd,       # MACD
            "kdj": self._query_kdj,         # KDJ
            "rsi": self._query_rsi,         # RSI
            "boll": self._query_boll,       # 布林带
            "volume": self._query_volume,   # 成交量指标
            "cross": self._query_cross      # 金叉死叉
        }
        
        indicator_type = params.get("indicator_type")
        if indicator_type in query_types:
            return await query_types[indicator_type](params)
        
        raise ValueError(f"不支持的指标类型：{indicator_type}")
    
    async def advanced_query(self, params: Dict) -> Dict:
        """高级查询（API + 分析）"""
        # 1. 检查缓存
        cache_key = self._build_cache_key(params)
        cached_result = await self.cache_manager.get(cache_key)
        if cached_result:
            return cached_result
        
        # 2. API调用
        api_data = await self.api_client.get_indicators(params)
        
        # 3. 高级分析
        analysis_result = {
            "raw_data": api_data,
            "patterns": self.pattern_recognizer.recognize(api_data),
            "signals": self._generate_signals(api_data),
            "trend": self._analyze_trend(api_data)
        }
        
        # 4. 缓存结果
        await self.cache_manager.set(cache_key, analysis_result, ttl=3600)
        
        return analysis_result
```

### 2.3 数据库设计

#### 2.3.1 技术指标表 (tu_technical_indicators)

```sql
CREATE TABLE tu_technical_indicators (
    -- 主键
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    ts_code VARCHAR(20) NOT NULL COMMENT '股票代码',
    trade_date VARCHAR(8) NOT NULL COMMENT '交易日期',
    
    -- 价格数据（冗余存储以提高查询效率）
    close_price DECIMAL(10,2) COMMENT '收盘价',
    high_price DECIMAL(10,2) COMMENT '最高价',
    low_price DECIMAL(10,2) COMMENT '最低价',
    
    -- 均线指标
    ma_5 DECIMAL(10,2) COMMENT '5日均线',
    ma_10 DECIMAL(10,2) COMMENT '10日均线',
    ma_20 DECIMAL(10,2) COMMENT '20日均线',
    ma_30 DECIMAL(10,2) COMMENT '30日均线',
    ma_60 DECIMAL(10,2) COMMENT '60日均线',
    ma_120 DECIMAL(10,2) COMMENT '120日均线',
    ma_250 DECIMAL(10,2) COMMENT '250日均线',
    
    -- 指数移动平均线
    ema_12 DECIMAL(10,2) COMMENT '12日EMA',
    ema_26 DECIMAL(10,2) COMMENT '26日EMA',
    
    -- MACD指标
    macd_dif DECIMAL(10,4) COMMENT 'MACD DIF值',
    macd_dea DECIMAL(10,4) COMMENT 'MACD DEA值',
    macd_histogram DECIMAL(10,4) COMMENT 'MACD柱状图',
    
    -- KDJ指标
    kdj_k DECIMAL(10,2) COMMENT 'KDJ-K值',
    kdj_d DECIMAL(10,2) COMMENT 'KDJ-D值',
    kdj_j DECIMAL(10,2) COMMENT 'KDJ-J值',
    
    -- RSI指标
    rsi_6 DECIMAL(10,2) COMMENT '6日RSI',
    rsi_12 DECIMAL(10,2) COMMENT '12日RSI',
    rsi_24 DECIMAL(10,2) COMMENT '24日RSI',
    
    -- 布林带
    boll_upper DECIMAL(10,2) COMMENT '布林带上轨',
    boll_middle DECIMAL(10,2) COMMENT '布林带中轨',
    boll_lower DECIMAL(10,2) COMMENT '布林带下轨',
    
    -- 成交量指标
    volume_ratio DECIMAL(10,2) COMMENT '量比',
    volume_ma_5 BIGINT COMMENT '5日成交量均值',
    volume_ma_10 BIGINT COMMENT '10日成交量均值',
    
    -- 其他指标
    turnover_rate DECIMAL(10,2) COMMENT '换手率',
    amplitude DECIMAL(10,2) COMMENT '振幅',
    
    -- 信号标记
    ma_cross_signal VARCHAR(20) COMMENT '均线交叉信号',
    macd_cross_signal VARCHAR(20) COMMENT 'MACD交叉信号',
    
    -- 时间戳
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    -- 索引
    UNIQUE KEY idx_code_date (ts_code, trade_date),
    INDEX idx_trade_date (trade_date),
    INDEX idx_ts_code (ts_code),
    INDEX idx_ma_cross (ts_code, ma_cross_signal),
    INDEX idx_macd_cross (ts_code, macd_cross_signal)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='技术指标数据表';
```

#### 2.3.2 形态识别结果表 (tu_pattern_recognition)

```sql
CREATE TABLE tu_pattern_recognition (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    ts_code VARCHAR(20) NOT NULL,
    pattern_type VARCHAR(50) NOT NULL COMMENT '形态类型',
    start_date VARCHAR(8) NOT NULL COMMENT '形态开始日期',
    end_date VARCHAR(8) NOT NULL COMMENT '形态结束日期',
    confidence DECIMAL(5,2) COMMENT '置信度(0-100)',
    description TEXT COMMENT '形态描述',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    INDEX idx_code_type (ts_code, pattern_type),
    INDEX idx_date_range (start_date, end_date)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='K线形态识别结果表';
```

### 2.4 查询模板设计

#### 2.4.1 新增查询模板 (query_templates.py)

```python
# 技术指标查询模板
TECHNICAL_TEMPLATES = {
    # 均线查询
    "MA_QUERY": {
        "pattern": r"(.*?)的?(5|10|20|30|60|120|250)?日?均线",
        "params": ["stock", "ma_period"],
        "quick": True
    },
    
    # MACD查询
    "MACD_QUERY": {
        "pattern": r"(.*?)的?MACD(金叉|死叉|指标)?",
        "params": ["stock", "signal_type"],
        "quick": True
    },
    
    # KDJ查询
    "KDJ_QUERY": {
        "pattern": r"(.*?)的?KDJ(指标|超买|超卖)?",
        "params": ["stock", "condition"],
        "quick": True
    },
    
    # RSI查询
    "RSI_QUERY": {
        "pattern": r"(.*?)的?RSI(指标|超买|超卖)?",
        "params": ["stock", "condition"],
        "quick": True
    },
    
    # 布林带查询
    "BOLL_QUERY": {
        "pattern": r"(.*?)的?布林带|BOLL",
        "params": ["stock"],
        "quick": True
    },
    
    # 技术形态
    "PATTERN_QUERY": {
        "pattern": r"(.*?)的?(头肩顶|双底|三角形|旗形|楔形)",
        "params": ["stock", "pattern"],
        "quick": False
    },
    
    # 趋势分析
    "TREND_QUERY": {
        "pattern": r"(分析|判断)(.*?)的?(技术)?趋势",
        "params": ["stock"],
        "quick": False
    },
    
    # 买卖信号
    "SIGNAL_QUERY": {
        "pattern": r"(.*?)的?(买入|卖出|买卖)信号",
        "params": ["stock", "signal_type"],
        "quick": False
    }
}
```

#### 2.4.2 SQL模板 (sql_templates.py)

```python
# 均线查询
TECHNICAL_MA = """
SELECT 
    ts_code,
    trade_date,
    close_price,
    ma_5, ma_10, ma_20, ma_30, ma_60, ma_120, ma_250
FROM tu_technical_indicators
WHERE ts_code = %(ts_code)s 
  AND trade_date = %(trade_date)s
"""

# MACD查询
TECHNICAL_MACD = """
SELECT 
    ts_code,
    trade_date,
    macd_dif,
    macd_dea,
    macd_histogram,
    macd_cross_signal
FROM tu_technical_indicators
WHERE ts_code = %(ts_code)s
  AND trade_date >= %(start_date)s
ORDER BY trade_date DESC
LIMIT %(limit)s
"""

# 金叉死叉查询
TECHNICAL_CROSS = """
SELECT 
    trade_date,
    close_price,
    ma_5, ma_20,
    macd_dif, macd_dea,
    ma_cross_signal,
    macd_cross_signal
FROM tu_technical_indicators
WHERE ts_code = %(ts_code)s
  AND (ma_cross_signal IS NOT NULL OR macd_cross_signal IS NOT NULL)
  AND trade_date >= %(start_date)s
ORDER BY trade_date DESC
LIMIT 10
"""

# 技术指标综合查询
TECHNICAL_COMPREHENSIVE = """
SELECT 
    t.*,
    CASE 
        WHEN t.rsi_6 > 70 THEN '超买'
        WHEN t.rsi_6 < 30 THEN '超卖'
        ELSE '正常'
    END as rsi_status,
    CASE
        WHEN t.close_price > t.boll_upper THEN '突破上轨'
        WHEN t.close_price < t.boll_lower THEN '突破下轨'
        ELSE '轨道内'
    END as boll_status
FROM tu_technical_indicators t
WHERE t.ts_code = %(ts_code)s
  AND t.trade_date = %(trade_date)s
"""
```

### 2.5 API集成设计

#### 2.5.1 TechnicalAPIClient

```python
class TechnicalAPIClient:
    """技术指标API客户端"""
    
    def __init__(self):
        self.base_url = config.TECHNICAL_API_URL
        self.api_key = config.TECHNICAL_API_KEY
        self.session = aiohttp.ClientSession()
    
    async def get_indicators(self, params: Dict) -> Dict:
        """获取技术指标数据"""
        endpoint = "/api/v1/indicators"
        
        # API请求参数
        api_params = {
            "ts_code": params["ts_code"],
            "indicators": params.get("indicators", ["cci", "dmi", "atr"]),
            "start_date": params.get("start_date"),
            "end_date": params.get("end_date")
        }
        
        try:
            async with self.session.post(
                f"{self.base_url}{endpoint}",
                json=api_params,
                headers={"Authorization": f"Bearer {self.api_key}"}
            ) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    raise APIError(f"API返回错误：{response.status}")
                    
        except Exception as e:
            logger.error(f"API调用失败：{str(e)}")
            raise
```

### 2.6 缓存策略

#### 2.6.1 缓存层级

1. **L1缓存**：内存缓存（LRU，最大1000条）
2. **L2缓存**：Redis缓存（TTL 1小时）
3. **L3缓存**：数据库持久化（2年数据）

#### 2.6.2 缓存键设计

```python
def build_cache_key(params: Dict) -> str:
    """构建缓存键"""
    components = [
        "tech",
        params.get("ts_code"),
        params.get("indicator_type"),
        params.get("trade_date", "latest"),
        params.get("period", "default")
    ]
    return ":".join(filter(None, components))
```

## 3. 功能实现

### 3.1 核心功能列表

#### 3.1.1 基础指标查询
- [x] 均线查询（MA5/10/20/60/120/250）
- [x] MACD指标查询
- [x] KDJ指标查询
- [x] RSI指标查询
- [x] 布林带查询
- [x] 成交量指标查询

#### 3.1.2 高级分析功能
- [ ] K线形态识别
- [ ] 趋势强度评分
- [ ] 买卖信号生成
- [ ] 多股票对比
- [ ] 板块技术分析

#### 3.1.3 智能功能
- [ ] 自动识别关键价位
- [ ] 支撑压力位计算
- [ ] 趋势预测
- [ ] 风险提示

### 3.2 查询示例

```python
# 基础查询
"贵州茅台的5日均线"
"宁德时代的MACD金叉"
"比亚迪的KDJ指标"
"茅台突破20日均线了吗"

# 高级查询
"分析贵州茅台的技术趋势"
"宁德时代最近有什么买入信号"
"比较茅台和五粮液的技术指标"
"新能源板块的技术面分析"
```

## 4. 实施计划

### 4.1 Phase 1：数据库建设（第1周）

#### Day 1-2：表结构设计与创建
- 创建技术指标主表
- 创建形态识别表
- 设计索引优化

#### Day 3-4：历史数据导入
- 开发数据导入脚本
- 计算并导入2年技术指标
- 数据质量验证

#### Day 5：数据更新机制
- 实现每日定时更新
- 增量更新逻辑
- 异常处理机制

### 4.2 Phase 2：核心功能开发（第2周）

#### Day 6-7：Agent框架搭建
- 创建TechnicalAgentModular类
- 集成统一模块
- 基础查询实现

#### Day 8-9：快速查询实现
- 实现6个基础指标查询
- SQL模板优化
- 性能测试

#### Day 10：API集成
- 开发API客户端
- 实现高级指标查询
- 错误处理

### 4.3 Phase 3：高级功能（第3周）

#### Day 11-12：形态识别
- 实现常见K线形态识别
- 置信度计算
- 结果存储

#### Day 13-14：智能分析
- 趋势分析算法
- 买卖信号生成
- 风险评估

#### Day 15：集成测试
- 功能完整性测试
- 性能压力测试
- 边界条件测试

### 4.4 Phase 4：优化与发布（第4周）

#### Day 16-17：性能优化
- 查询优化
- 缓存调优
- 并发处理

#### Day 18-19：文档与培训
- 用户文档编写
- 开发文档完善
- 团队培训

#### Day 20：正式发布
- 生产环境部署
- 监控配置
- 发布公告

## 5. 测试策略

### 5.1 单元测试

```python
class TestTechnicalAgent:
    """技术分析Agent单元测试"""
    
    def test_ma_query(self):
        """测试均线查询"""
        query = "贵州茅台的5日均线"
        result = agent.process_query(query)
        assert result.success
        assert "ma_5" in result.data
    
    def test_macd_cross(self):
        """测试MACD金叉查询"""
        query = "宁德时代最近的MACD金叉"
        result = agent.process_query(query)
        assert result.success
        assert result.data.get("cross_type") == "金叉"
    
    def test_pattern_recognition(self):
        """测试形态识别"""
        query = "比亚迪是否形成头肩顶"
        result = agent.process_query(query)
        assert result.success
        assert "pattern" in result.data
```

### 5.2 集成测试

- 与HybridAgent路由集成测试
- 数据库连接池测试
- API调用超时测试
- 缓存一致性测试

### 5.3 性能测试

| 测试场景 | 目标响应时间 | 并发数 |
|---------|------------|--------|
| 基础指标查询 | <0.1秒 | 100 |
| 金叉死叉查询 | <0.2秒 | 50 |
| API高级查询 | <2秒 | 20 |
| 形态识别 | <3秒 | 10 |

## 6. 监控与运维

### 6.1 监控指标

- **性能监控**：查询响应时间、API调用延迟
- **业务监控**：查询量、热门指标统计
- **系统监控**：CPU使用率、内存占用、数据库连接数
- **错误监控**：错误率、异常类型分布

### 6.2 告警规则

- 查询响应时间>5秒
- API调用失败率>5%
- 数据更新延迟>1小时
- 缓存命中率<80%

### 6.3 运维操作

- 每日数据更新检查
- 每周性能报告
- 每月数据清理（超过2年的数据）
- 季度容量规划

## 7. 风险与对策

### 7.1 技术风险

| 风险 | 影响 | 对策 |
|------|------|------|
| API限流 | 高级查询失败 | 实现降级策略，增加缓存 |
| 数据量过大 | 查询性能下降 | 分区表设计，定期归档 |
| 计算复杂度高 | 响应时间长 | 预计算+缓存，异步处理 |

### 7.2 业务风险

| 风险 | 影响 | 对策 |
|------|------|------|
| 指标准确性 | 用户信任度 | 多数据源验证，专家审核 |
| 实时性要求 | 用户体验 | 明确SLA，合理设置预期 |

## 8. 未来扩展

### 8.1 功能扩展
- 支持自定义指标
- 量化策略回测
- 机器学习预测
- 实时推送服务

### 8.2 性能扩展
- 分布式计算
- GPU加速
- 实时流处理
- 边缘计算

### 8.3 生态扩展
- 开放API接口
- 第三方指标集成
- 社区贡献机制
- 商业化服务

## 9. 总结

Technical Analysis Agent作为v2.4.0的核心功能，将大幅提升系统的技术分析能力。通过混合模式设计，既保证了常用查询的高性能，又提供了高级分析的灵活性。模块化架构确保了代码的可维护性和可扩展性。

预计4周完成全部开发工作，将为用户提供：
- 20+种技术指标查询
- <0.1秒的快速响应
- 智能化的分析建议
- 专业的投资参考

---
文档版本：v1.0  
最后更新：2025-07-13