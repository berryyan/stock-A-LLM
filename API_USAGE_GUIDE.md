# 股票分析系统 API 使用指南 v1.4.0

## 🚀 快速开始

### 启动API服务器

```bash
# 激活虚拟环境
source venv/bin/activate

# 启动API服务器
python -m uvicorn api.main:app --reload --host 0.0.0.0 --port 8000

# 或者使用后台运行
nohup python -m uvicorn api.main:app --host 0.0.0.0 --port 8000 &
```

### 访问API文档

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **API根路径**: http://localhost:8000/

## 📊 API功能总览

### 核心功能
- 🧠 **智能查询路由**: 自动识别查询类型并路由到合适的分析引擎
- 💾 **SQL数据查询**: 结构化数据查询（股价、财务指标、排名等）
- 📄 **RAG文档检索**: 语义搜索年报、季报、公告内容
- 💰 **专业财务分析**: 四表联合分析、财务健康度评分、杜邦分析、现金流质量分析

## 🛠️ API端点详解

### 1. 通用智能查询 (推荐)

**端点**: `POST /query`

**功能**: 自动识别查询意图并路由到相应的分析引擎

#### 请求示例

```bash
curl -X POST "http://localhost:8000/query" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "分析贵州茅台的财务健康状况",
    "context": null,
    "filters": null,
    "top_k": 5
  }'
```

#### 支持的查询类型

##### 财务分析查询（自动路由到财务分析引擎）
```json
{
  "question": "分析贵州茅台的财务健康状况"
}
```

```json
{
  "question": "600519.SH的杜邦分析"
}
```

```json
{
  "question": "茅台的现金流质量如何"
}
```

```json
{
  "question": "平安银行的多期财务对比"
}
```

##### SQL数据查询（自动路由到SQL引擎）
```json
{
  "question": "贵州茅台最新股价"
}
```

```json
{
  "question": "A股市值排名前10的公司"
}
```

##### 文档检索查询（自动路由到RAG引擎）
```json
{
  "question": "贵州茅台最新年报说了什么"
}
```

```json
{
  "question": "平安银行的风险提示"
}
```

#### 响应格式

```json
{
  "success": true,
  "question": "分析贵州茅台的财务健康状况",
  "answer": "### 财务健康度分析报告...",
  "query_type": "financial",
  "sources": {
    "financial": {
      "health_score": {
        "total_score": 81.0,
        "rating": "AA",
        "dimension_scores": {
          "profitability": 85,
          "solvency": 100,
          "operation": 50,
          "growth": 90
        }
      }
    }
  },
  "error": null,
  "query_id": "12345678-1234-5678-9012-123456789012",
  "timestamp": "2025-06-23T01:00:00"
}
```

### 2. 专门财务分析

**端点**: `POST /financial-analysis`

**功能**: 直接调用财务分析功能，支持四种分析类型

#### 请求参数

| 参数 | 类型 | 必需 | 描述 |
|------|------|------|------|
| ts_code | string | 是 | 股票代码 (如: 600519.SH) |
| analysis_type | string | 是 | 分析类型 |

#### 支持的分析类型

| 类型 | 描述 | 功能 |
|------|------|------|
| `financial_health` | 财务健康度分析 | 四维度评分、AAA-CCC评级 |
| `dupont_analysis` | 杜邦分析 | ROE分解、三要素分析 |
| `cash_flow_quality` | 现金流质量分析 | 现金含量比率、稳定性评分 |
| `multi_period_comparison` | 多期财务对比 | 同比环比增长率、趋势分析 |

#### 请求示例

```bash
# 财务健康度分析
curl -X POST "http://localhost:8000/financial-analysis" \
  -H "Content-Type: application/json" \
  -d '{
    "ts_code": "600519.SH",
    "analysis_type": "financial_health"
  }'

# 杜邦分析
curl -X POST "http://localhost:8000/financial-analysis" \
  -H "Content-Type: application/json" \
  -d '{
    "ts_code": "000001.SZ",
    "analysis_type": "dupont_analysis"
  }'
```

#### 响应示例

```json
{
  "success": true,
  "ts_code": "600519.SH",
  "analysis_type": "financial_health",
  "analysis_report": "### 财务健康度分析报告\n\n#### 1. 核心结论\n...",
  "financial_data": {
    "health_score": {
      "total_score": 81.0,
      "rating": "AA",
      "dimension_scores": {
        "profitability": 85,
        "solvency": 100,
        "operation": 50,
        "growth": 90
      }
    },
    "period": "20250331"
  },
  "error": null,
  "processing_time": 28.5,
  "timestamp": "2025-06-23T01:00:00"
}
```

### 3. 其他辅助端点

#### 健康检查
```bash
GET /health
```

#### 系统状态
```bash
GET /status
```

#### 公司列表
```bash
GET /companies?sector=银行业&limit=20
```

#### 最近报告
```bash
GET /reports/recent?days=7&limit=20
```

## 🧪 在Swagger UI中测试

### 访问Swagger UI

1. 启动API服务器后，访问 http://localhost:8000/docs
2. 页面会显示所有可用的API端点

### 测试自然语言查询

#### 方法一：使用通用查询端点

1. 在Swagger UI中找到 `POST /query` 端点
2. 点击 "Try it out" 按钮
3. 在请求体中输入：

```json
{
  "question": "分析贵州茅台的财务健康状况",
  "context": null,
  "filters": null,
  "top_k": 5
}
```

4. 点击 "Execute" 执行查询
5. 查看响应结果，应该看到 `"query_type": "financial"` 表示成功路由到财务分析

#### 方法二：使用专门财务分析端点

1. 找到 `POST /financial-analysis` 端点
2. 点击 "Try it out"
3. 输入：

```json
{
  "ts_code": "600519.SH",
  "analysis_type": "financial_health"
}
```

4. 执行并查看结果

### 测试其他查询类型

#### SQL查询测试
```json
{
  "question": "贵州茅台2025年6月20日的股价"
}
```

#### RAG查询测试
```json
{
  "question": "贵州茅台最新年报的主要内容"
}
```

## 🎯 实际应用场景

### 1. 投资研究工作流

```python
import requests

# 设置API基础URL
api_base = "http://localhost:8000"

# 1. 财务健康度筛选
def screen_stocks_by_health(stock_list):
    healthy_stocks = []
    for stock in stock_list:
        response = requests.post(f"{api_base}/financial-analysis", 
                               json={"ts_code": stock, "analysis_type": "financial_health"})
        if response.status_code == 200:
            data = response.json()
            if data.get('success') and data['financial_data']['health_score']['total_score'] > 70:
                healthy_stocks.append({
                    'ts_code': stock,
                    'score': data['financial_data']['health_score']['total_score'],
                    'rating': data['financial_data']['health_score']['rating']
                })
    return healthy_stocks

# 2. 深度分析
def deep_analysis(ts_code):
    analyses = ['financial_health', 'dupont_analysis', 'cash_flow_quality', 'multi_period_comparison']
    results = {}
    
    for analysis_type in analyses:
        response = requests.post(f"{api_base}/financial-analysis", 
                               json={"ts_code": ts_code, "analysis_type": analysis_type})
        if response.status_code == 200:
            results[analysis_type] = response.json()
    
    return results

# 使用示例
stocks = ["600519.SH", "000858.SZ", "000568.SZ"]  # 白酒板块
healthy_stocks = screen_stocks_by_health(stocks)
print("优质标的:", healthy_stocks)

# 深度分析最优标的
if healthy_stocks:
    best_stock = max(healthy_stocks, key=lambda x: x['score'])
    detailed_analysis = deep_analysis(best_stock['ts_code'])
    print(f"最优标的 {best_stock['ts_code']} 详细分析完成")
```

### 2. 风险监控

```python
def risk_monitoring(portfolio):
    risk_alerts = []
    
    for stock in portfolio:
        # 财务健康度检查
        response = requests.post(f"{api_base}/financial-analysis", 
                               json={"ts_code": stock, "analysis_type": "financial_health"})
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                score = data['financial_data']['health_score']['total_score']
                if score < 50:
                    risk_alerts.append({
                        'ts_code': stock,
                        'risk': '财务健康度低',
                        'score': score
                    })
        
        # 现金流质量检查
        response = requests.post(f"{api_base}/financial-analysis", 
                               json={"ts_code": stock, "analysis_type": "cash_flow_quality"})
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                rating = data['financial_data']['quality_analysis']['overall_rating']
                if rating in ['D', 'F']:
                    risk_alerts.append({
                        'ts_code': stock,
                        'risk': '现金流质量差',
                        'rating': rating
                    })
    
    return risk_alerts
```

## ⚡ 性能和限制

### 响应时间参考

| 查询类型 | 典型响应时间 | 最大超时 |
|----------|-------------|----------|
| SQL查询 | 5-15秒 | 60秒 |
| RAG查询 | 10-30秒 | 120秒 |
| 财务分析 | 25-45秒 | 180秒 |
| 混合查询 | 30-60秒 | 300秒 |

### 使用建议

1. **批量查询**: 对多个股票进行分析时，建议加入适当延时（3-5秒）
2. **错误处理**: 始终检查响应的 `success` 字段
3. **超时设置**: 客户端设置足够的超时时间（建议300秒）
4. **结果缓存**: 对同一查询的结果可以缓存使用

### 限制说明

- **并发限制**: 建议同时进行的查询不超过5个
- **查询频率**: 建议单个查询间隔3-5秒
- **数据覆盖**: 主要覆盖A股市场，5400+只股票
- **数据时效**: 基于Tushare数据，通常有1-2个交易日的延迟

## 🔧 故障排查

### 常见问题

#### 1. 连接失败
```
ConnectionError: Failed to establish a new connection
```
**解决方案**: 确认API服务器已启动，检查端口8000是否被占用

#### 2. 查询超时
```
ReadTimeoutError: HTTPSConnectionPool(...): Read timed out
```
**解决方案**: 增加客户端超时设置，或者简化查询内容

#### 3. 数据不存在
```json
{
  "success": false,
  "error": "未找到股票 XXX.XX 的财务数据"
}
```
**解决方案**: 检查股票代码格式（如600519.SH），确认是A股代码

#### 4. 服务器错误
```json
{
  "success": false,
  "error": "系统未初始化"
}
```
**解决方案**: 重启API服务器，检查数据库连接状态

### 健康检查

```bash
# 检查API状态
curl http://localhost:8000/health

# 检查系统状态
curl http://localhost:8000/status
```

## 🚀 进阶使用

### 使用Python客户端

```python
import requests
import json
from typing import Dict, Any

class StockAnalysisClient:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
    
    def query(self, question: str, **kwargs) -> Dict[str, Any]:
        """通用查询"""
        payload = {"question": question, **kwargs}
        response = requests.post(f"{self.base_url}/query", json=payload, timeout=300)
        return response.json()
    
    def financial_analysis(self, ts_code: str, analysis_type: str) -> Dict[str, Any]:
        """财务分析"""
        payload = {"ts_code": ts_code, "analysis_type": analysis_type}
        response = requests.post(f"{self.base_url}/financial-analysis", json=payload, timeout=300)
        return response.json()
    
    def health_check(self) -> Dict[str, Any]:
        """健康检查"""
        response = requests.get(f"{self.base_url}/health")
        return response.json()

# 使用示例
client = StockAnalysisClient()

# 检查服务状态
if client.health_check().get('status') == 'healthy':
    # 财务分析
    result = client.financial_analysis("600519.SH", "financial_health")
    print(f"茅台财务评级: {result['financial_data']['health_score']['rating']}")
    
    # 自然语言查询
    result = client.query("分析平安银行的现金流质量")
    print(f"查询类型: {result['query_type']}")
```

## 📝 更新日志

### v1.4.0 (2025-06-22)
- ✅ 新增专业财务分析功能
- ✅ 四表联合分析（利润表+资产负债表+现金流量表+财务指标）
- ✅ 财务健康度智能评分系统
- ✅ 杜邦分析和现金流质量分析
- ✅ 智能查询路由优化
- ✅ API文档完善

### v1.3.8 (2025-06-22)
- ✅ LangChain现代化升级
- ✅ 输入验证增强
- ✅ 系统稳定性提升

---

**技术支持**: 如遇问题请检查日志文件或联系系统管理员  
**API文档**: http://localhost:8000/docs  
**系统版本**: v1.4.0