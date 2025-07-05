# RAG Agent 模块化版本字段映射修复

## 问题描述

在执行RAG查询时，系统报错：
```
field stock_code not exist
field stock_name not exist  
field announcement_date not exist
```

## 问题原因

RAG Agent模块化版本（`rag_agent_modular.py`）在构建Milvus查询过滤表达式时，使用了错误的字段名，与实际数据库schema不匹配。

### 数据库实际字段（从 `milvus_connector.py` 确认）:
- `ts_code` - 股票代码（如 "600519.SH"）
- `ann_date` - 公告日期（如 "2025-07-05"）
- `title` - 公告标题
- `text` - 公告内容
- `doc_id` - 文档ID
- `chunk_id` - 块ID
- `embeddings` - 向量嵌入
- `metadata` - 元数据JSON

### RAG Agent错误使用的字段:
- `stock_code` ❌ → 应该是 `ts_code`
- `stock_name` ❌ → 字段不存在
- `announcement_date` ❌ → 应该是 `ann_date`

## 修复方案

修改 `agents/rag_agent_modular.py` 中的 `_build_milvus_expr` 方法：

```python
def _build_milvus_expr(self, filter_dict: Dict) -> str:
    """构建Milvus过滤表达式"""
    expressions = []
    
    # 股票过滤 - 修正字段名
    if 'stock_filter' in filter_dict:
        stock_conditions = []
        for stock in filter_dict['stock_filter']:
            # 只使用实际存在的字段 ts_code
            stock_conditions.append(f'ts_code == "{stock}"')
        if stock_conditions:
            expressions.append(f"({' or '.join(stock_conditions)})")
    
    # 日期过滤 - 修正字段名
    if 'date' in filter_dict:
        expressions.append(f'ann_date == "{filter_dict["date"]}"')
    elif 'date_range' in filter_dict:
        start, end = filter_dict['date_range']
        expressions.append(f'ann_date >= "{start}" and ann_date <= "{end}"')
    
    return ' and '.join(expressions) if expressions else ""
```

## 测试验证

创建了测试脚本 `test_field_mapping_simple.py` 验证修复效果：

### 测试结果：
```
测试结果: 5 通过, 0 失败

✓ 字段映射修复验证成功！
```

### 测试用例覆盖：
1. 单个股票过滤
2. 多个股票过滤
3. 日期过滤
4. 日期范围过滤
5. 复合过滤（股票+日期）

## 影响范围

- 仅影响 RAG Agent 模块化版本的查询功能
- 不影响原始 RAG Agent（`rag_agent.py`）
- 修复后可正常进行股票和日期过滤的文档搜索

## 后续建议

1. **统一字段命名规范**：在整个项目中统一使用相同的字段名
2. **添加字段验证**：在查询前验证字段是否存在
3. **完善错误处理**：提供更友好的错误提示
4. **文档化数据库Schema**：创建数据库字段文档，避免类似问题

## 相关文件

- 修改文件：`agents/rag_agent_modular.py`
- 测试文件：`test_field_mapping_simple.py`
- 数据库连接器：`database/milvus_connector.py`