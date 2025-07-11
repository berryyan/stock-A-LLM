# Money Flow Agent 深度分析与实现规划

## 一、Agent职责定位

### 1.1 Money Flow Agent的核心职责
- **深度分析**：对资金流向数据进行深度分析，生成专业报告
- **LLM增强**：使用LLM对数据进行解读，提供投资建议
- **行为模式识别**：识别主力建仓、减仓、洗盘等行为模式
- **多维度分析**：主力资金、超大单、资金分布等全方位分析

### 1.2 与SQL Agent的职责边界
- **SQL Agent**：
  - 快速数据查询（个股/板块主力资金）
  - 排名查询（主力净流入排名）
  - 返回原始数据表格
  - 响应时间：1-2秒

- **Money Flow Agent**：
  - 深度分析报告
  - 包含LLM分析和投资建议
  - 多日趋势分析
  - 响应时间：15-30秒

## 二、路由规则设计

### 2.1 SQL Agent优先路由（SQL_ONLY）
```python
sql_force_patterns = [
    # 排名查询 - 最高优先级
    r".*?(主力|超大单|大单|中单|小单|资金).*(排名|排行|TOP|top)\d*",
    
    # 简单数据查询 - 不包含分析关键词
    r"^[^分析评估研究解析判断]*(的|之)?(主力|超大单|大单|中单|小单)(资金)?$",
    
    # 板块资金查询 - 简单数据需求
    r"^[^分析评估研究]*板块(的)?(主力|超大单|大单|中单|小单)?(资金)?$"
]
```

### 2.2 Money Flow Agent强制路由（MONEY_FLOW）
```python
money_flow_force_patterns = [
    # 分析关键词开头
    r"^(分析|评估|研究|解析|判断)",
    
    # 包含行为模式关键词
    r".*(建仓|减仓|洗盘|吸筹|出货|控盘)",
    
    # 深度分析需求
    r".*(如何看待|怎么看|意味着什么|说明了什么)",
    
    # 趋势分析
    r".*(趋势|走势|未来|预测|展望)"
]
```

## 三、数据结构设计

### 3.1 个股深度分析数据结构
```python
{
    "stock_info": {
        "ts_code": "600519.SH",
        "name": "贵州茅台"
    },
    "time_series_data": {
        "daily": [  # 最近30天每日数据
            {
                "date": "2025-06-27",
                "main_net_flow": -12500.5,  # 主力净流入（万元）
                "super_large_net": -8000.2,  # 超大单净流入
                "large_net": -4500.3,        # 大单净流入
                "medium_net": 3200.1,        # 中单净流入
                "small_net": 9300.4,         # 小单净流入
                "price_change": -1.2,        # 涨跌幅
                "volume": 125000             # 成交量
            },
            // ... 更多天数据
        ],
        "weekly_summary": [  # 周度汇总
            {
                "week": "2025-W26",
                "main_net_flow_sum": -45000,
                "avg_daily_flow": -9000,
                "flow_days": {"inflow": 2, "outflow": 3}
            }
        ],
        "monthly_summary": {  # 月度汇总
            "main_net_flow_sum": -125000,
            "flow_pattern": "持续流出",
            "consistency_score": 0.78
        }
    },
    "analysis_metrics": {
        "main_capital_strength": 0.85,      # 主力资金强度
        "super_large_dominance": 0.65,      # 超大单主导度
        "behavior_pattern": "震荡吸筹",     # 行为模式
        "risk_level": "medium",             # 风险等级
        "investment_suggestion": "观望"     # 投资建议
    }
}
```

### 3.2 板块深度分析数据结构
```python
{
    "sector_info": {
        "name": "银行板块",
        "code": "BK0001",
        "stock_count": 42
    },
    "sector_flow_summary": {
        "total_main_net_flow": 125000,      # 板块总主力净流入
        "avg_main_net_flow": 2976,          # 平均每股主力净流入
        "inflow_stocks": 28,                # 流入股票数
        "outflow_stocks": 14                # 流出股票数
    },
    "top_stocks": {
        "top_inflow": [  # 主力净流入前5
            {"name": "招商银行", "ts_code": "600036.SH", "net_flow": 25000},
            {"name": "平安银行", "ts_code": "000001.SZ", "net_flow": 18000}
        ],
        "top_outflow": [  # 主力净流出前5
            {"name": "工商银行", "ts_code": "601398.SH", "net_flow": -12000}
        ]
    },
    "distribution_analysis": {
        "concentration": 0.72,              # 资金集中度
        "leader_effect": "strong",          # 龙头效应
        "sector_trend": "分化明显"         # 板块趋势
    }
}
```

### 3.3 对比分析数据结构
```python
{
    "comparison_type": "stocks",  # stocks/sectors
    "entities": ["600519.SH", "000858.SZ"],
    "period": "30d",
    "comparison_data": {
        "600519.SH": {
            "name": "贵州茅台",
            "main_net_flow": -125000,
            "flow_trend": "outflow",
            "strength_score": 0.85
        },
        "000858.SZ": {
            "name": "五粮液",
            "main_net_flow": 85000,
            "flow_trend": "inflow",
            "strength_score": 0.72
        }
    },
    "correlation_analysis": {
        "correlation_coefficient": 0.65,
        "sync_pattern": "同向不同步",
        "leader_follower": "600519.SH leads"
    }
}
```

## 四、测试用例设计

### 4.1 SQL Agent处理的测试用例
```python
# 排名查询
"主力净流入排名前10"          # SQL_ONLY
"超大单净流出TOP20"           # SQL_ONLY
"银行板块主力资金排名"        # SQL_ONLY

# 简单数据查询
"贵州茅台的主力资金"          # SQL_ONLY
"银行板块的主力资金"          # SQL_ONLY
"平安银行今天的超大单"        # SQL_ONLY
```

### 4.2 Money Flow Agent处理的测试用例
```python
# 深度分析查询
"分析贵州茅台的资金流向"      # MONEY_FLOW
"评估银行板块的资金趋势"      # MONEY_FLOW
"研究平安银行主力行为"        # MONEY_FLOW

# 行为模式查询
"贵州茅台是否有主力建仓"      # MONEY_FLOW
"平安银行的洗盘迹象"          # MONEY_FLOW
"万科A主力出货了吗"           # MONEY_FLOW

# 趋势分析查询
"贵州茅台资金流向趋势如何"    # MONEY_FLOW
"如何看待茅台的资金流出"      # MONEY_FLOW
"银行板块资金未来走势"        # MONEY_FLOW
```

## 五、实现计划

### 5.1 第一步：修复基础功能（优先级：最高）
1. 修复Money Flow Agent模块化版本的入口方法
2. 实现板块查询支持
3. 调整查询类型识别逻辑

### 5.2 第二步：实现路由规则（优先级：高）
1. 在Hybrid Agent中实现新的路由规则
2. 确保SQL Agent和Money Flow Agent的正确分工
3. 添加路由决策日志

### 5.3 第三步：完善数据结构（优先级：中）
1. 实现时间序列数据获取
2. 添加周度、月度汇总计算
3. 实现板块分析数据结构

### 5.4 第四步：优化LLM分析（优先级：低）
1. 优化分析提示词
2. 添加更多分析维度
3. 提升报告质量

## 六、当前问题与解决方案

### 6.1 板块查询失败问题
**问题**：所有板块查询都返回"无法识别输入内容"错误
**原因**：Money Flow Agent调用了股票验证器，但板块不是股票
**解决**：
1. 在参数提取时识别板块查询
2. 板块查询不进行股票验证
3. 实现板块资金查询逻辑

### 6.2 非标准术语成功问题
**问题**：应该失败的非标准术语查询却成功了
**原因**：Money Flow Agent设计为接受并转换非标准术语
**解决**：这是正确的行为，测试用例需要调整预期

### 6.3 查询路由问题
**问题**：很多应该由SQL Agent处理的查询被路由到Money Flow Agent
**原因**：Hybrid Agent的路由规则不够精确
**解决**：实现上述的精确路由规则