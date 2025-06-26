# Claude.ai前端配套的后端响应格式设计指南

本文档详细说明了后端API应该如何设计响应格式，以便与Claude.ai风格的前端界面完美配合。通过遵循这些规范，你将能够创建一个前后端高度协调的智能对话系统。

## 一、核心设计理念

后端响应格式的设计必须遵循三个核心原则：

1. **内容与展示分离**：AI生成的内容应该与展示控制信息分离，让前端能够灵活处理
2. **渐进增强**：基础信息必须完整，高级功能通过额外字段提供
3. **类型安全**：所有响应都应该有明确的类型定义，便于前后端协作

## 二、基础响应结构

### 2.1 标准响应格式

每个API响应都应该遵循这个基础结构：

```typescript
interface StandardResponse<T = any> {
  // 请求状态
  success: boolean;
  
  // 核心数据
  data: T;
  
  // 元信息
  meta: {
    requestId: string;        // 请求追踪ID
    timestamp: string;        // ISO 8601格式时间戳
    processingTime: number;   // 处理耗时（毫秒）
    version: string;          // API版本
  };
  
  // 错误信息（仅在失败时存在）
  error?: {
    code: string;             // 错误代码
    message: string;          // 用户友好的错误信息
    details?: any;            // 详细错误信息（开发模式）
  };
}
```

### 2.2 对话查询响应格式

对于聊天对话的查询请求，响应格式应该包含丰富的信息层次：

```typescript
interface ChatQueryResponse extends StandardResponse {
  data: {
    // 主要回答内容（必需）
    answer: string;           // Markdown格式的回答
    
    // 查询分类信息
    queryAnalysis: {
      type: QueryType;        // 查询类型
      intent: string[];       // 识别的意图
      entities: Entity[];     // 提取的实体
      confidence: number;     // 置信度 0-1
    };
    
    // 数据源信息
    sources?: {
      primary: DataSource[];   // 主要数据源
      references: Reference[]; // 参考资料
      citations: Citation[];   // 引用信息
    };
    
    // 附加内容
    artifacts?: {
      tables?: TableArtifact[];
      charts?: ChartArtifact[];
      code?: CodeArtifact[];
      documents?: DocumentArtifact[];
      interactive?: InteractiveArtifact[];
    };
    
    // 展示控制
    display: {
      layout: LayoutType;              // 布局建议
      primaryView: ViewType;           // 主视图类型
      secondaryView?: ViewType;        // 次视图类型
      highlights?: HighlightInfo[];    // 高亮信息
      animations?: AnimationHint[];    // 动画提示
    };
    
    // 后续操作
    suggestions?: {
      followUpQuestions: string[];     // 后续问题建议
      relatedTopics: string[];         // 相关主题
      actions: Action[];               // 可执行操作
    };
  };
}
```

## 三、Markdown内容规范

### 3.1 基础Markdown格式要求

后端返回的`answer`字段必须是格式规范的Markdown：

```markdown
## 主标题使用二级标题

正文内容直接书写，注意段落之间要有空行。

### 子标题使用三级标题

**重要内容**使用粗体标记，*次要强调*使用斜体。

- 无序列表项
- 支持嵌套
  - 子项目
  - 另一个子项目

1. 有序列表
2. 自动编号
3. 便于阅读
```

### 3.2 特殊标记系统

为了触发前端的特定展示逻辑，后端应该在Markdown中嵌入特殊标记：

```markdown
<!-- artifact:start type="chart" id="revenue-trend" -->
{
  "title": "营收趋势图",
  "description": "2024年季度营收变化",
  "data": {...}
}
<!-- artifact:end -->

<!-- highlight:start color="primary" -->
这段内容会在前端被特殊高亮显示
<!-- highlight:end -->

<!-- collapsible:start title="详细说明" defaultOpen="false" -->
这里是可折叠的详细内容，默认收起状态
<!-- collapsible:end -->
```

### 3.3 代码块的元数据

代码块应该包含丰富的元数据以支持高级功能：

````markdown
```python {title="ROI计算器" executable=true lineNumbers=true highlight=[3,4]}
def calculate_roi(initial_investment, final_value):
    """计算投资回报率"""
    profit = final_value - initial_investment
    roi_percentage = (profit / initial_investment) * 100
    return roi_percentage

# 示例计算
roi = calculate_roi(10000, 15000)
print(f"ROI: {roi:.2f}%")
```
````

## 四、数据类型定义

### 4.1 查询类型枚举

```typescript
enum QueryType {
  // 基础类型
  GENERAL = 'general',           // 一般查询
  FACTUAL = 'factual',           // 事实查询
  ANALYTICAL = 'analytical',     // 分析查询
  CREATIVE = 'creative',         // 创造性查询
  
  // 股票特定类型
  STOCK_PRICE = 'stock_price',   // 股价查询
  FINANCIAL = 'financial',       // 财务分析
  TECHNICAL = 'technical',       // 技术分析
  NEWS = 'news',                 // 新闻资讯
  COMPARISON = 'comparison',     // 对比分析
  PREDICTION = 'prediction'      // 预测分析
}
```

### 4.2 布局类型定义

```typescript
enum LayoutType {
  DEFAULT = 'default',           // 默认单列布局
  SPLIT = 'split',              // 左右分屏布局
  FULLWIDTH = 'fullwidth',      // 全宽布局
  FOCUSED = 'focused',          // 聚焦布局（隐藏侧边栏）
  DASHBOARD = 'dashboard'       // 仪表板布局
}

enum ViewType {
  CHAT = 'chat',                // 对话视图
  DOCUMENT = 'document',        // 文档视图
  CODE = 'code',                // 代码视图
  TABLE = 'table',              // 表格视图
  CHART = 'chart',              // 图表视图
  MARKDOWN = 'markdown'         // Markdown视图
}
```

### 4.3 工件（Artifact）类型定义

```typescript
// 表格工件
interface TableArtifact {
  id: string;
  title: string;
  description?: string;
  
  // 表格配置
  config: {
    sortable?: boolean;         // 是否可排序
    filterable?: boolean;       // 是否可筛选
    exportable?: boolean;       // 是否可导出
    paginated?: boolean;        // 是否分页
    pageSize?: number;          // 每页条数
  };
  
  // 表格数据
  data: {
    headers: TableHeader[];
    rows: any[][];
    footer?: any[][];
  };
  
  // 样式提示
  styling?: {
    striped?: boolean;          // 斑马纹
    bordered?: boolean;         // 边框
    hoverable?: boolean;        // 悬停效果
    compact?: boolean;          // 紧凑模式
  };
}

// 图表工件
interface ChartArtifact {
  id: string;
  title: string;
  type: ChartType;
  
  // 图表配置
  config: {
    responsive?: boolean;       // 响应式
    animated?: boolean;         // 动画效果
    interactive?: boolean;      // 交互功能
    theme?: 'light' | 'dark' | 'auto';
  };
  
  // 图表数据
  data: {
    datasets: Dataset[];
    labels?: string[];
    categories?: string[];
  };
  
  // 图表选项（ECharts配置）
  options?: any;
}

// 代码工件
interface CodeArtifact {
  id: string;
  title: string;
  language: string;
  
  // 代码内容
  content: string;
  
  // 代码配置
  config: {
    executable?: boolean;       // 是否可执行
    editable?: boolean;         // 是否可编辑
    collapsible?: boolean;      // 是否可折叠
    lineNumbers?: boolean;      // 显示行号
    wordWrap?: boolean;         // 自动换行
  };
  
  // 元数据
  meta?: {
    filename?: string;          // 文件名
    description?: string;       // 描述
    dependencies?: string[];    // 依赖
    output?: string;           // 预期输出
  };
}
```

## 五、股票系统特定格式

### 5.1 股票查询响应

```typescript
interface StockQueryResponse extends ChatQueryResponse {
  data: {
    answer: string;
    
    // 股票特定数据
    stockInfo?: {
      basic: {
        symbol: string;         // 股票代码
        name: string;           // 股票名称
        market: string;         // 市场
        industry: string;       // 行业
        sector: string;         // 板块
      };
      
      // 实时行情
      realtime?: {
        price: number;          // 当前价
        change: number;         // 涨跌额
        changePercent: number;  // 涨跌幅
        volume: number;         // 成交量
        amount: number;         // 成交额
        high: number;           // 最高价
        low: number;            // 最低价
        open: number;           // 开盘价
        preClose: number;       // 昨收价
        timestamp: string;      // 时间戳
        status: 'trading' | 'halted' | 'closed';
      };
      
      // K线数据
      kline?: {
        period: KlinePeriod;
        data: KlineData[];
        indicators?: {
          ma?: number[];        // 移动均线
          ema?: number[];       // 指数移动均线
          bollinger?: BollingerBands;
          macd?: MACDData;
          rsi?: number[];
        };
      };
      
      // 财务数据
      financial?: {
        summary: FinancialSummary;
        income: IncomeStatement[];
        balance: BalanceSheet[];
        cashflow: CashflowStatement[];
        ratios: FinancialRatios;
      };
    };
    
    // 展示配置覆盖
    display: {
      layout: 'split';          // 股票查询默认分屏
      primaryView: 'chat';
      secondaryView: 'chart' | 'table' | 'document';
      chartConfig?: {
        defaultType: 'candlestick' | 'line' | 'area';
        indicators: string[];
        period: string;
      };
    };
  };
}
```

### 5.2 财务数据格式规范

```typescript
interface FinancialDataFormat {
  // 数值格式化规则
  formatting: {
    currency: {
      code: 'CNY' | 'USD' | 'HKD';
      symbol: '¥' | '$' | 'HK$';
      precision: 2;
      useGrouping: true;        // 千分位分隔
    };
    
    percentage: {
      precision: 2;
      suffix: '%';
      positiveColor?: string;   // 正值颜色
      negativeColor?: string;   // 负值颜色
    };
    
    number: {
      notation: 'standard' | 'scientific' | 'compact';
      precision: number;
      unit?: '万' | '亿' | 'M' | 'B';
    };
  };
  
  // 对比数据的展示规则
  comparison: {
    baselineIndex: number;      // 基准索引
    highlightBest: boolean;     // 高亮最佳值
    highlightWorst: boolean;    // 高亮最差值
    showTrend: boolean;         // 显示趋势箭头
  };
}
```

## 六、流式响应支持

### 6.1 流式响应协议

对于长内容或实时生成的内容，后端应支持流式响应：

```typescript
interface StreamingProtocol {
  // 初始握手消息
  handshake: {
    type: 'stream:start';
    streamId: string;
    totalChunks?: number;       // 预计块数（如果已知）
    contentType: string;        // 内容类型
    metadata: any;
  };
  
  // 内容块
  chunk: {
    type: 'stream:chunk';
    streamId: string;
    index: number;              // 块索引
    content: string;            // 内容片段
    isMarkdown: boolean;        // 是否为Markdown
    artifacts?: any[];          // 该块附带的工件
  };
  
  // 流结束
  complete: {
    type: 'stream:complete';
    streamId: string;
    summary?: string;           // 内容摘要
    totalChunks: number;        // 实际块数
    processingTime: number;     // 总处理时间
  };
  
  // 错误处理
  error: {
    type: 'stream:error';
    streamId: string;
    error: {
      code: string;
      message: string;
      recoverable: boolean;     // 是否可恢复
    };
  };
}
```

### 6.2 Server-Sent Events (SSE) 格式

```typescript
// SSE 事件格式
interface SSEEvent {
  event: string;                // 事件类型
  data: string;                 // JSON字符串
  id?: string;                  // 事件ID
  retry?: number;               // 重连时间（毫秒）
}

// 示例SSE输出
`event: chunk
data: {"type":"stream:chunk","streamId":"abc123","index":0,"content":"## 分析结果\\n\\n"}
id: 1

event: chunk  
data: {"type":"stream:chunk","streamId":"abc123","index":1,"content":"根据最新数据显示..."}
id: 2

event: complete
data: {"type":"stream:complete","streamId":"abc123","totalChunks":2}
id: 3
`
```

## 七、错误处理规范

### 7.1 错误响应格式

```typescript
interface ErrorResponse extends StandardResponse {
  success: false;
  error: {
    // 标准错误字段
    code: string;               // 机器可读的错误代码
    message: string;            // 用户友好的错误信息
    
    // 详细信息
    details?: {
      field?: string;           // 出错字段
      reason?: string;          // 详细原因
      suggestion?: string;      // 修复建议
      documentation?: string;   // 文档链接
    };
    
    // 错误上下文
    context?: {
      requestId: string;
      timestamp: string;
      path: string;
      method: string;
    };
    
    // 重试信息
    retry?: {
      available: boolean;       // 是否可重试
      after?: number;          // 建议重试时间（秒）
      maxAttempts?: number;    // 最大重试次数
    };
  };
}
```

### 7.2 错误代码规范

```typescript
enum ErrorCode {
  // 通用错误 (1xxx)
  INTERNAL_ERROR = 'ERR_1000',
  INVALID_REQUEST = 'ERR_1001',
  UNAUTHORIZED = 'ERR_1002',
  FORBIDDEN = 'ERR_1003',
  NOT_FOUND = 'ERR_1004',
  RATE_LIMITED = 'ERR_1005',
  
  // 数据错误 (2xxx)
  DATA_NOT_FOUND = 'ERR_2000',
  DATA_INVALID = 'ERR_2001',
  DATA_EXPIRED = 'ERR_2002',
  DATA_CONFLICT = 'ERR_2003',
  
  // 股票特定错误 (3xxx)
  INVALID_SYMBOL = 'ERR_3000',
  MARKET_CLOSED = 'ERR_3001',
  TRADING_HALTED = 'ERR_3002',
  INSUFFICIENT_DATA = 'ERR_3003',
  
  // AI/模型错误 (4xxx)
  MODEL_UNAVAILABLE = 'ERR_4000',
  GENERATION_FAILED = 'ERR_4001',
  CONTEXT_TOO_LONG = 'ERR_4002',
  UNSAFE_CONTENT = 'ERR_4003'
}
```

## 八、性能优化建议

### 8.1 响应大小控制

```typescript
interface ResponseOptimization {
  // 分页支持
  pagination?: {
    page: number;
    pageSize: number;
    total: number;
    hasNext: boolean;
    hasPrevious: boolean;
  };
  
  // 字段过滤
  fields?: {
    include?: string[];         // 包含字段
    exclude?: string[];         // 排除字段
  };
  
  // 数据压缩提示
  compression?: {
    algorithm: 'gzip' | 'brotli';
    originalSize: number;
    compressedSize: number;
  };
}
```

### 8.2 缓存控制

```typescript
interface CacheControl {
  // HTTP缓存头
  headers: {
    'Cache-Control': string;    // 如: 'public, max-age=300'
    'ETag'?: string;           // 实体标签
    'Last-Modified'?: string;  // 最后修改时间
  };
  
  // 自定义缓存提示
  hints: {
    cacheKey: string;          // 缓存键
    ttl: number;               // 生存时间（秒）
    scope: 'user' | 'global';  // 缓存范围
    invalidateOn?: string[];   // 失效条件
  };
}
```

## 九、实际响应示例

### 9.1 简单查询响应

```json
{
  "success": true,
  "data": {
    "answer": "贵州茅台（600519.SH）当前股价为 **1,835.20元**，今日上涨 42.30元（+2.36%）。\n\n该股今日表现强势，成交量达到 156.8万手，成交额 28.79亿元。",
    
    "queryAnalysis": {
      "type": "stock_price",
      "intent": ["price_query", "realtime_data"],
      "entities": [
        {
          "type": "stock",
          "value": "600519.SH",
          "name": "贵州茅台"
        }
      ],
      "confidence": 0.98
    },
    
    "display": {
      "layout": "default",
      "primaryView": "chat",
      "highlights": [
        {
          "text": "1,835.20元",
          "type": "price",
          "color": "primary"
        },
        {
          "text": "+2.36%",
          "type": "change",
          "color": "success"
        }
      ]
    }
  },
  
  "meta": {
    "requestId": "req_123456",
    "timestamp": "2024-06-27T15:30:00Z",
    "processingTime": 126,
    "version": "1.0.0"
  }
}
```

### 9.2 复杂分析响应

```json
{
  "success": true,
  "data": {
    "answer": "## 贵州茅台（600519.SH）综合财务分析\n\n### 财务健康度评分：92/100 🏆\n\n公司展现出**极其优秀**的财务健康状况，在行业内处于绝对领先地位。\n\n### 核心财务指标\n\n<!-- artifact:start type=\"table\" id=\"financial-metrics\" -->\n<!-- artifact:end -->\n\n### 详细分析\n\n#### 1. 盈利能力（评分：95/100）\n- **毛利率**：91.5%，远超行业平均水平（65.2%）\n- **净利率**：51.8%，展现极强的盈利能力\n- **ROE**：32.5%，资本回报率优秀\n\n#### 2. 成长性（评分：88/100）\n营收和利润保持稳健增长：\n- 营收同比增长：+18.5%\n- 净利润同比增长：+19.2%\n- 连续5年保持双位数增长\n\n<!-- collapsible:start title=\"查看详细财务数据\" -->\n这里包含更详细的财务报表数据...\n<!-- collapsible:end -->",
    
    "queryAnalysis": {
      "type": "financial",
      "intent": ["financial_analysis", "comprehensive_review"],
      "entities": [
        {
          "type": "stock",
          "value": "600519.SH",
          "name": "贵州茅台"
        }
      ],
      "confidence": 0.96
    },
    
    "artifacts": {
      "tables": [
        {
          "id": "financial-metrics",
          "title": "核心财务指标对比",
          "config": {
            "sortable": true,
            "exportable": true
          },
          "data": {
            "headers": [
              { "key": "metric", "label": "指标", "type": "string" },
              { "key": "current", "label": "本期", "type": "number" },
              { "key": "previous", "label": "上期", "type": "number" },
              { "key": "change", "label": "变化", "type": "percentage" }
            ],
            "rows": [
              ["营业收入（亿元）", 1241.90, 1047.87, 0.185],
              ["净利润（亿元）", 626.45, 525.38, 0.192],
              ["毛利率", 0.915, 0.912, 0.003],
              ["净利率", 0.518, 0.502, 0.016]
            ]
          }
        }
      ],
      
      "charts": [
        {
          "id": "growth-trend",
          "title": "营收增长趋势",
          "type": "line",
          "config": {
            "responsive": true,
            "animated": true
          },
          "data": {
            "labels": ["2020", "2021", "2022", "2023", "2024"],
            "datasets": [
              {
                "label": "营业收入",
                "data": [889.23, 1061.94, 1094.64, 1229.47, 1241.90]
              }
            ]
          }
        }
      ]
    },
    
    "display": {
      "layout": "split",
      "primaryView": "chat",
      "secondaryView": "table",
      "animations": [
        {
          "target": "score",
          "type": "countUp",
          "duration": 1000
        }
      ]
    },
    
    "suggestions": {
      "followUpQuestions": [
        "对比茅台与五粮液的财务指标",
        "分析茅台的现金流状况",
        "查看茅台的股东结构变化"
      ],
      "relatedTopics": [
        "白酒行业分析",
        "消费股投资机会",
        "A股核心资产"
      ]
    }
  },
  
  "meta": {
    "requestId": "req_789012",
    "timestamp": "2024-06-27T15:35:00Z",
    "processingTime": 1832,
    "version": "1.0.0"
  }
}
```

## 十、实施建议

### 10.1 开发顺序

1. **第一步**：实现基础响应结构和错误处理
2. **第二步**：完善Markdown生成和特殊标记
3. **第三步**：添加工件（Artifact）支持
4. **第四步**：实现流式响应
5. **第五步**：优化性能和缓存

### 10.2 测试要点

- 确保所有响应都符合TypeScript类型定义
- 验证Markdown格式的正确性
- 测试各种错误场景的处理
- 检查大数据量响应的性能
- 验证流式响应的稳定性

### 10.3 最佳实践

1. **版本控制**：在API响应中包含版本信息，便于前后端协调升级
2. **向后兼容**：新增字段应该是可选的，避免破坏现有前端
3. **错误友好**：提供清晰的错误信息和修复建议
4. **性能监控**：记录每个请求的处理时间，持续优化
5. **文档同步**：保持API文档与实际响应格式同步

通过遵循这个指南，你的后端API将能够完美支持Claude.ai风格的前端界面，提供丰富、灵活、高性能的数据服务。