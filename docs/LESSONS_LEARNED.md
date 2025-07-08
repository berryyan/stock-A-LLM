# 股票分析系统开发经验教训

## 模块化架构原则

### ✅ 正确做法

1. **使用公共模块**
   - SQL查询使用`utils/sql_templates.py`中的模板
   - 日期处理使用`utils/date_intelligence.py`的功能
   - 参数验证使用`utils/query_validator.py`的规则
   - 股票验证使用`utils/unified_stock_validator.py`

2. **功能集中化**
   - 相同功能只在一个地方实现
   - 其他模块通过调用而非复制代码
   - 修改时只需要改一处

3. **配置优于硬编码**
   - 使用配置文件管理查询模板
   - 使用字典映射管理术语转换
   - 避免在具体实现中硬编码规则

### ❌ 错误做法

1. **在具体Agent中硬编码功能**
   ```python
   # 错误：在sql_agent_modular.py中直接实现
   def _execute_volume_ranking(self, ...):
       sql = """SELECT ... FROM ..."""  # 硬编码SQL
   
   # 正确：使用公共模板
   def _execute_volume_ranking(self, ...):
       sql = SQLTemplates.VOLUME_RANKING  # 使用公共模板
   ```

2. **重复实现相同功能**
   ```python
   # 错误：在parameter_extractor中实现日期范围
   def _get_last_month_range(self):
       # 重复实现
   
   # 正确：调用date_intelligence的方法
   date_intelligence.calculator.get_last_month_range()
   ```

## 测试管理

### 测试预期一致性

1. **避免重复测试**
   - 同一个查询不应该在不同地方有不同预期
   - 例如："成交量排名"不能既期望成功又期望失败

2. **测试预期与功能设计一致**
   - 个股成交量查询应该成功
   - 成交量排名查询应该成功
   - 使用非标准术语应该失败

3. **分类清晰**
   - 正常用例：测试正常功能
   - 边界测试：测试边界条件
   - 错误用例：测试错误处理

## 验证规则实施

### 验证层次

1. **参数提取阶段**
   - 基础格式验证
   - 股票代码/名称验证

2. **增强验证阶段**
   - 业务规则验证（如个股不能排名）
   - 术语标准化验证
   - 数量范围验证

### 验证方法调用

```python
# 确保调用增强验证
validation_result = self.query_validator.validate_enhanced(params, template)

# 而不是只调用基础验证
validation_result = self.query_validator.validate_params(params, template)
```

## 日期处理

### 相对日期范围

1. **在date_intelligence模块实现**
   - get_last_month_range()
   - get_current_month_range()
   - get_last_year_range()
   - get_current_year_range()
   - get_last_quarter_range()
   - get_current_quarter_range()

2. **parameter_extractor调用**
   ```python
   date_intelligence.calculator.get_last_month_range()
   ```

### 日期格式统一

- 内部使用：YYYY-MM-DD
- 数据库查询：YYYYMMDD
- 转换在最后时刻进行

## 中文数字处理

### 处理时机

```python
# 在日期处理后，模板匹配前
processed_question = normalize_quantity_expression(processed_question)
```

### 支持范围

- 基础数字：一到九十九
- 百位数字：一百、二百等
- 特殊表达：前N、TOP N

## 调试技巧

### 添加充分日志

```python
self.logger.info(f"执行增强验证 - 查询: {params.raw_query}")
self.logger.info(f"拒绝查询 - 原因: {reason}")
self.logger.info("验证通过")
```

### 缓存清理

Windows环境下Python缓存可能导致修改不生效：
```bash
# 清理__pycache__
rmdir /s /q __pycache__
# 清理.pyc文件
del *.pyc /s
```

## 股票实体识别规则

### ✅ 支持的格式

1. **股票名称**（数据库中的标准名称）
   - 贵州茅台 ✓
   - 中国平安 ✓
   - 万科A ✓

2. **股票代码**（6位数字）
   - 600519 ✓
   - 000001 ✓

3. **证券代码**（带后缀）
   - 600519.SH ✓
   - 000001.SZ ✓

### ❌ 不支持的格式

1. **股票简称**
   - 茅台 ✗ （应使用"贵州茅台"）
   - 万科 ✗ （应使用"万科A"）
   - 平安 ✗ （歧义：平安银行？中国平安？）

2. **股票昵称**
   - 酱茅 ✗
   - 招商 ✗

3. **公司全称**
   - 贵州茅台酒股份有限公司 ✗
   - 万科企业股份有限公司 ✗

### 设计原因

1. **避免歧义**：如"平安"可能指多只股票
2. **保持一致性**：统一使用数据库中的标准名称
3. **减少复杂度**：不需要维护大量的别名映射

## 常见问题及解决方案

### 问题1：修改后测试结果没变化
**原因**：Python模块缓存
**解决**：清理缓存后重新运行

### 问题2：验证规则不生效
**原因**：没有调用正确的验证方法
**解决**：确保调用validate_enhanced而非validate_params

### 问题3：相对日期查询失败
**原因**：日期范围方法返回格式不正确
**解决**：确保返回YYYY-MM-DD格式

### 问题4：测试失败但功能正常
**原因**：测试预期错误
**解决**：检查并修正测试预期

## 开发流程建议

1. **先设计后实现**
   - 确定功能应该在哪个模块
   - 检查是否已有类似功能
   - 优先复用和扩展

2. **小步快进**
   - 每次只修改一个问题
   - 立即测试验证
   - 确认后再继续

3. **保持一致性**
   - 遵循现有代码风格
   - 使用统一的错误处理
   - 保持API稳定

4. **文档同步**
   - 修改功能时更新文档
   - 添加新功能时写清楚用法
   - 记录重要的设计决策