# 技术指标API集成方案

版本：v1.0  
创建时间：2025-07-13  
作者：Stock Analysis System Team

## 1. 概述

本文档描述Technical Analysis Agent的API集成方案，包括高级技术指标的实时计算、第三方数据源集成以及降级策略。

## 2. API架构设计

### 2.1 整体架构

```
Technical Agent
    ├── 快速路径（数据库查询）
    │   └── 基础指标（MA, MACD, KDJ等）
    └── API路径（实时计算）
        ├── 内部API（自建计算服务）
        └── 外部API（第三方服务）
```

### 2.2 API选型分析

| 方案 | 优点 | 缺点 | 适用场景 |
|------|------|------|----------|
| Tushare Pro | 数据全面，接口稳定 | 需要积分，有调用限制 | 历史数据回补 |
| 自建计算服务 | 完全可控，无限制 | 开发成本高 | 核心指标计算 |
| Alpha Vantage | 免费额度，国际化 | 国内股票支持有限 | 美股技术指标 |
| 聚宽API | A股数据完整 | 收费较高 | 专业量化需求 |

## 3. 内部API设计

### 3.1 技术指标计算服务

```python
# technical_calculator_service.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Optional
import numpy as np
import pandas as pd

app = FastAPI(title="Technical Indicator Calculator")

class IndicatorRequest(BaseModel):
    ts_code: str
    indicator: str
    params: Optional[Dict] = {}
    start_date: Optional[str]
    end_date: Optional[str]

class IndicatorResponse(BaseModel):
    success: bool
    data: Dict
    message: Optional[str]

@app.post("/api/v1/calculate", response_model=IndicatorResponse)
async def calculate_indicator(request: IndicatorRequest):
    """计算技术指标"""
    try:
        # 获取股票数据
        df = await get_stock_data(
            request.ts_code, 
            request.start_date, 
            request.end_date
        )
        
        # 根据指标类型计算
        calculator = IndicatorCalculator(df)
        result = calculator.calculate(request.indicator, request.params)
        
        return IndicatorResponse(
            success=True,
            data=result
        )
    except Exception as e:
        return IndicatorResponse(
            success=False,
            data={},
            message=str(e)
        )

class IndicatorCalculator:
    """技术指标计算器"""
    
    def __init__(self, df: pd.DataFrame):
        self.df = df
    
    def calculate(self, indicator: str, params: Dict) -> Dict:
        """统一计算接口"""
        calculators = {
            "cci": self.calculate_cci,
            "dmi": self.calculate_dmi,
            "atr": self.calculate_atr,
            "william": self.calculate_william,
            "obv": self.calculate_obv,
            "sar": self.calculate_sar,
            "trix": self.calculate_trix,
            "vr": self.calculate_vr,
            "cr": self.calculate_cr,
            "psy": self.calculate_psy
        }
        
        if indicator not in calculators:
            raise ValueError(f"不支持的指标: {indicator}")
        
        return calculators[indicator](**params)
    
    def calculate_cci(self, period: int = 14) -> Dict:
        """计算CCI指标（商品通道指数）"""
        tp = (self.df['high'] + self.df['low'] + self.df['close']) / 3
        ma = tp.rolling(window=period).mean()
        md = tp.rolling(window=period).apply(
            lambda x: np.abs(x - x.mean()).mean()
        )
        cci = (tp - ma) / (0.015 * md)
        
        return {
            "values": cci.tolist(),
            "dates": self.df['trade_date'].tolist(),
            "params": {"period": period}
        }
    
    def calculate_dmi(self, period: int = 14) -> Dict:
        """计算DMI指标（趋向指标）"""
        high = self.df['high']
        low = self.df['low']
        close = self.df['close']
        
        # 计算+DM和-DM
        plus_dm = high.diff()
        minus_dm = -low.diff()
        plus_dm[plus_dm < 0] = 0
        minus_dm[minus_dm < 0] = 0
        
        # 计算TR
        tr = pd.concat([
            high - low,
            (high - close.shift()).abs(),
            (low - close.shift()).abs()
        ], axis=1).max(axis=1)
        
        # 计算+DI和-DI
        atr = tr.rolling(window=period).mean()
        plus_di = 100 * (plus_dm.rolling(window=period).mean() / atr)
        minus_di = 100 * (minus_dm.rolling(window=period).mean() / atr)
        
        # 计算ADX
        dx = 100 * ((plus_di - minus_di).abs() / (plus_di + minus_di))
        adx = dx.rolling(window=period).mean()
        
        return {
            "plus_di": plus_di.tolist(),
            "minus_di": minus_di.tolist(),
            "adx": adx.tolist(),
            "dates": self.df['trade_date'].tolist(),
            "params": {"period": period}
        }
```

### 3.2 批量计算优化

```python
@app.post("/api/v1/batch_calculate")
async def batch_calculate(requests: List[IndicatorRequest]):
    """批量计算技术指标"""
    results = []
    
    # 按股票代码分组
    grouped = {}
    for req in requests:
        if req.ts_code not in grouped:
            grouped[req.ts_code] = []
        grouped[req.ts_code].append(req)
    
    # 并行计算
    tasks = []
    for ts_code, reqs in grouped.items():
        # 获取数据一次，计算多个指标
        task = calculate_multiple_indicators(ts_code, reqs)
        tasks.append(task)
    
    results = await asyncio.gather(*tasks)
    return {"success": True, "results": results}
```

## 4. 外部API集成

### 4.1 Tushare Pro集成

```python
class TushareProClient:
    """Tushare Pro API客户端"""
    
    def __init__(self):
        self.token = config.TUSHARE_TOKEN
        self.pro = ts.pro_api(self.token)
        self.daily_limit = 200  # 每分钟限制
        self.request_queue = Queue()
    
    async def get_technical_factors(
        self, 
        ts_code: str, 
        start_date: str,
        end_date: str,
        fields: List[str] = None
    ):
        """获取技术因子数据"""
        try:
            # 限流控制
            await self._rate_limit()
            
            # 调用stk_factor接口
            df = self.pro.stk_factor(
                ts_code=ts_code,
                start_date=start_date,
                end_date=end_date,
                fields=fields or [
                    'ts_code', 'trade_date', 
                    'macd_dif', 'macd_dea', 'macd',
                    'kdj_k', 'kdj_d', 'kdj_j',
                    'rsi_6', 'rsi_12', 'rsi_24',
                    'boll_upper', 'boll_mid', 'boll_lower',
                    'cci', 'wr_6', 'wr_10'
                ]
            )
            
            return df.to_dict('records')
            
        except Exception as e:
            logger.error(f"Tushare API调用失败: {e}")
            raise
    
    async def _rate_limit(self):
        """速率限制"""
        current_minute = datetime.now().minute
        if not hasattr(self, '_last_minute'):
            self._last_minute = current_minute
            self._minute_count = 0
        
        if current_minute != self._last_minute:
            self._last_minute = current_minute
            self._minute_count = 0
        
        if self._minute_count >= self.daily_limit:
            wait_time = 60 - datetime.now().second
            await asyncio.sleep(wait_time)
            self._minute_count = 0
        
        self._minute_count += 1
```

### 4.2 降级策略

```python
class APIFallbackStrategy:
    """API降级策略"""
    
    def __init__(self):
        self.primary_api = TechnicalCalculatorAPI()
        self.secondary_api = TushareProClient()
        self.cache = RedisCache()
    
    async def get_indicator(
        self, 
        ts_code: str, 
        indicator: str,
        params: Dict
    ) -> Dict:
        """获取指标数据，自动降级"""
        
        # 1. 尝试从缓存获取
        cache_key = f"tech:{ts_code}:{indicator}:{hash(str(params))}"
        cached = await self.cache.get(cache_key)
        if cached:
            return cached
        
        # 2. 尝试主API
        try:
            result = await self.primary_api.calculate(
                ts_code, indicator, params
            )
            await self.cache.set(cache_key, result, ttl=3600)
            return result
        except Exception as e:
            logger.warning(f"主API失败: {e}")
        
        # 3. 尝试备用API
        try:
            result = await self.secondary_api.get_indicator(
                ts_code, indicator, params
            )
            await self.cache.set(cache_key, result, ttl=1800)
            return result
        except Exception as e:
            logger.error(f"备用API失败: {e}")
        
        # 4. 使用简化计算
        try:
            result = await self.simple_calculate(
                ts_code, indicator, params
            )
            await self.cache.set(cache_key, result, ttl=600)
            return result
        except Exception as e:
            logger.error(f"简化计算失败: {e}")
            raise APIError("所有API均不可用")
```

## 5. 缓存策略

### 5.1 多级缓存架构

```python
class TechnicalIndicatorCache:
    """技术指标缓存管理器"""
    
    def __init__(self):
        # L1: 进程内缓存
        self.memory_cache = LRUCache(maxsize=1000)
        
        # L2: Redis缓存
        self.redis_client = redis.Redis(
            host=config.REDIS_HOST,
            port=config.REDIS_PORT,
            decode_responses=True
        )
        
        # L3: 数据库缓存
        self.db_cache = DatabaseCache()
    
    async def get(self, key: str) -> Optional[Dict]:
        """获取缓存数据"""
        # L1查询
        if key in self.memory_cache:
            return self.memory_cache[key]
        
        # L2查询
        redis_data = self.redis_client.get(key)
        if redis_data:
            data = json.loads(redis_data)
            self.memory_cache[key] = data
            return data
        
        # L3查询
        db_data = await self.db_cache.get(key)
        if db_data:
            # 回填上层缓存
            self.redis_client.setex(key, 3600, json.dumps(db_data))
            self.memory_cache[key] = db_data
            return db_data
        
        return None
    
    async def set(self, key: str, value: Dict, ttl: int = 3600):
        """设置缓存数据"""
        # 写入所有层级
        self.memory_cache[key] = value
        self.redis_client.setex(key, ttl, json.dumps(value))
        await self.db_cache.set(key, value, ttl)
```

### 5.2 缓存预热

```python
class CacheWarmer:
    """缓存预热器"""
    
    async def warm_popular_stocks(self):
        """预热热门股票数据"""
        popular_stocks = await self.get_popular_stocks()
        
        indicators = ['ma', 'macd', 'kdj', 'rsi', 'boll']
        tasks = []
        
        for stock in popular_stocks:
            for indicator in indicators:
                task = self.warm_indicator(stock, indicator)
                tasks.append(task)
        
        await asyncio.gather(*tasks)
    
    async def warm_indicator(self, ts_code: str, indicator: str):
        """预热单个指标"""
        try:
            # 计算指标
            result = await self.calculator.calculate(
                ts_code, indicator, {}
            )
            
            # 写入缓存
            cache_key = f"tech:{ts_code}:{indicator}:latest"
            await self.cache.set(cache_key, result, ttl=7200)
            
        except Exception as e:
            logger.error(f"预热失败 {ts_code}-{indicator}: {e}")
```

## 6. 性能优化

### 6.1 并发控制

```python
class ConcurrencyController:
    """并发控制器"""
    
    def __init__(self, max_concurrent: int = 10):
        self.semaphore = asyncio.Semaphore(max_concurrent)
        self.rate_limiter = RateLimiter(
            max_requests=100,
            time_window=60
        )
    
    async def execute_with_limit(self, func, *args, **kwargs):
        """限流执行"""
        async with self.semaphore:
            await self.rate_limiter.acquire()
            return await func(*args, **kwargs)
```

### 6.2 数据压缩

```python
class DataCompressor:
    """数据压缩器"""
    
    @staticmethod
    def compress_indicator_data(data: Dict) -> bytes:
        """压缩指标数据"""
        # 移除冗余字段
        compressed = {
            'v': data['values'],  # values
            'd': data['dates'],   # dates
            'p': data.get('params', {})  # params
        }
        
        # 使用msgpack压缩
        return msgpack.packb(compressed)
    
    @staticmethod
    def decompress_indicator_data(data: bytes) -> Dict:
        """解压指标数据"""
        compressed = msgpack.unpackb(data)
        return {
            'values': compressed['v'],
            'dates': compressed['d'],
            'params': compressed.get('p', {})
        }
```

## 7. 监控与告警

### 7.1 监控指标

```python
class APIMonitor:
    """API监控器"""
    
    def __init__(self):
        self.metrics = {
            'api_calls': Counter('api_calls_total'),
            'api_errors': Counter('api_errors_total'),
            'api_latency': Histogram('api_latency_seconds'),
            'cache_hits': Counter('cache_hits_total'),
            'cache_misses': Counter('cache_misses_total')
        }
    
    async def record_api_call(self, api_name: str, duration: float, success: bool):
        """记录API调用"""
        self.metrics['api_calls'].inc()
        self.metrics['api_latency'].observe(duration)
        
        if not success:
            self.metrics['api_errors'].inc()
        
        # 发送告警
        if duration > 5:  # 超过5秒
            await self.send_alert(
                f"API响应缓慢: {api_name}, 耗时: {duration}秒"
            )
```

### 7.2 健康检查

```python
@app.get("/health")
async def health_check():
    """API健康检查"""
    checks = {
        "database": await check_database_connection(),
        "redis": await check_redis_connection(),
        "external_api": await check_external_api(),
        "cache_hit_rate": calculate_cache_hit_rate()
    }
    
    overall_health = all(checks.values())
    
    return {
        "status": "healthy" if overall_health else "unhealthy",
        "checks": checks,
        "timestamp": datetime.now().isoformat()
    }
```

## 8. 部署方案

### 8.1 容器化部署

```dockerfile
# Dockerfile
FROM python:3.9-slim

WORKDIR /app

# 安装依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制代码
COPY . .

# 暴露端口
EXPOSE 8002

# 启动命令
CMD ["uvicorn", "technical_api:app", "--host", "0.0.0.0", "--port", "8002"]
```

### 8.2 部署配置

```yaml
# docker-compose.yml
version: '3.8'

services:
  technical-api:
    build: .
    ports:
      - "8002:8002"
    environment:
      - REDIS_HOST=redis
      - MYSQL_HOST=mysql
      - API_KEY=${TECHNICAL_API_KEY}
    depends_on:
      - redis
      - mysql
    restart: unless-stopped
    
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
      
volumes:
  redis_data:
```

## 9. 安全考虑

### 9.1 API认证

```python
class APIAuthentication:
    """API认证中间件"""
    
    async def verify_token(self, token: str) -> bool:
        """验证API令牌"""
        # 验证令牌格式
        if not token or not token.startswith("Bearer "):
            return False
        
        # 提取令牌
        api_key = token.replace("Bearer ", "")
        
        # 验证令牌有效性
        valid_key = await self.redis_client.get(f"api_key:{api_key}")
        if not valid_key:
            return False
        
        # 更新使用统计
        await self.update_usage_stats(api_key)
        
        return True
```

### 9.2 数据加密

```python
class DataEncryption:
    """数据加密工具"""
    
    def __init__(self):
        self.key = Fernet.generate_key()
        self.cipher = Fernet(self.key)
    
    def encrypt_sensitive_data(self, data: Dict) -> bytes:
        """加密敏感数据"""
        json_data = json.dumps(data)
        return self.cipher.encrypt(json_data.encode())
    
    def decrypt_sensitive_data(self, encrypted: bytes) -> Dict:
        """解密敏感数据"""
        decrypted = self.cipher.decrypt(encrypted)
        return json.loads(decrypted.decode())
```

## 10. 总结

本API集成方案通过混合模式设计，既保证了基础指标的快速响应，又提供了高级指标的灵活计算。多级缓存、降级策略和性能优化确保了系统的高可用性。

主要特点：
- 内部API + 外部API相结合
- 三级缓存架构
- 完善的降级策略
- 实时监控告警
- 容器化部署

预期效果：
- 基础指标响应 <100ms
- 高级指标响应 <2s
- 系统可用性 >99.9%
- 支持100+ QPS

---
文档版本：v1.0  
最后更新：2025-07-13