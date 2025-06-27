# Markdown渲染测试文档

## 代码块测试

### Python代码示例
```python
def analyze_stock(stock_code):
    """分析股票数据"""
    data = fetch_data(stock_code)
    metrics = calculate_metrics(data)
    return {
        'score': metrics.score,
        'recommendation': 'BUY' if metrics.score > 0.7 else 'HOLD'
    }
```

### JavaScript代码示例
```javascript
const queryStock = async (code) => {
  const response = await fetch(`/api/stock/${code}`);
  const data = await response.json();
  return data;
};
```

### SQL查询示例
```sql
SELECT 
    ts_code,
    trade_date,
    close,
    volume
FROM daily
WHERE ts_code = '600519.SH'
ORDER BY trade_date DESC
LIMIT 10;
```

## 表格测试

| 股票代码 | 公司名称 | 最新价格 | 涨跌幅 | 成交量 |
|---------|---------|---------|--------|--------|
| 600519.SH | 贵州茅台 | 1,680.00 | +2.35% | 12,345 |
| 000858.SZ | 五粮液 | 180.50 | -0.82% | 23,456 |
| 000002.SZ | 万科A | 12.35 | +1.15% | 345,678 |

## 链接测试

查看更多信息请访问 [股票分析系统文档](https://example.com/docs)

## 引用块测试

> 投资有风险，入市需谨慎。本系统提供的分析结果仅供参考，不构成投资建议。
> 
> —— 系统声明

## 列表测试

### 无序列表
- 实时股价查询
- 财务数据分析
- 技术指标计算
- AI智能推荐

### 有序列表
1. 登录系统
2. 输入股票代码
3. 选择分析类型
4. 查看分析结果
5. 导出报告

## 内联代码测试

使用 `fetch_stock_data()` 函数获取股票数据，然后调用 `analyze()` 进行分析。

## 数学公式测试

股票收益率计算公式：$R = \frac{P_t - P_{t-1}}{P_{t-1}} \times 100\%$

夏普比率：$$SR = \frac{R_p - R_f}{\sigma_p}$$

## 标题层级测试

# 一级标题
## 二级标题
### 三级标题
#### 四级标题
##### 五级标题
###### 六级标题