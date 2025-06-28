# 数据库Schema中文映射系统测试指南

## 📋 概述

本指南帮助你全面测试数据库Schema中文映射系统，确保系统正常工作。

## 🚀 快速开始

### 1. 环境准备

```bash
# Windows环境
cd E:\PycharmProjects\stock_analysis_system
venv\Scripts\activate

# WSL2环境
cd /mnt/e/PycharmProjects/stock_analysis_system
source venv/bin/activate
```

### 2. 快速测试（推荐）

```bash
# 运行快速测试（约30秒）
python test_schema_mapping_guide.py --quick
```

预期输出：
```
Schema映射系统 - 快速测试
================================================================================

1. 测试Schema加载...
✅ 加载成功: 14个表, 535个字段

2. 测试字段映射...
✅ 股票代码 -> ts_code
✅ 收盘价 -> close
✅ 成交量 -> vol

3. 测试查询解析...
✅ 解析成功: 类型=stock_price, 字段=6个

4. 测试SQL生成...
✅ SQL生成成功: SELECT open, high, low, close, vol, amount FROM tu_daily_detail...

快速测试完成！
```

### 3. 完整测试

```bash
# 运行完整测试套件（约3-5分钟）
python test_schema_mapping_guide.py
```

选择选项1运行完整测试。

## 📊 测试项目详解

### 测试1: Schema加载和统计
- **目的**: 验证系统能否从数据库动态加载表结构
- **检查点**:
  - 表数量应为14个
  - 字段总数应超过500个
  - 中文字段名应超过400个
- **常见问题**: 如果加载失败，检查数据库连接配置

### 测试2: 中文字段映射
- **目的**: 验证常用中文字段名能正确映射到英文
- **测试字段**:
  - 股票代码 → ts_code
  - 收盘价 → close
  - 成交量 → vol
  - 净利润 → n_income
  - 总资产 → total_assets
- **通过标准**: 80%以上映射正确

### 测试3: 中文表名映射
- **目的**: 验证中文表名能正确映射
- **测试表名**:
  - 日线行情 → tu_daily_detail
  - 利润表 → tu_income
  - 资产负债表 → tu_balancesheet
- **通过标准**: 70%以上映射正确

### 测试4: 中文查询解析
- **目的**: 验证自然语言查询的理解能力
- **测试查询**:
  - "查询贵州茅台最新股价"
  - "茅台最近30天的收盘价和成交量"
  - "分析平安银行的财务状况"
- **检查内容**: 查询类型、字段、股票代码、时间条件

### 测试5: SQL生成
- **目的**: 验证能否生成正确的SQL语句
- **检查点**: SQL包含必要的关键词（SELECT、FROM、WHERE等）

### 测试6: Hybrid Agent集成
- **目的**: 验证与主查询系统的集成
- **注意**: 需要初始化所有Agent，耗时较长（30秒+）

## 🔍 手动测试方法

### 1. Python交互式测试

```python
# 启动Python交互环境
python

# 测试Schema加载
from utils.schema_cache_manager import SchemaCacheManager
manager = SchemaCacheManager()
stats = manager.get_stats()
print(f"表数量: {stats['table_count']}")
print(f"字段数: {stats['field_count']}")

# 测试字段映射
field_info = manager.get_field_by_chinese("收盘价")
print(f"收盘价 -> {field_info['table']}.{field_info['field']}")

# 测试查询解析
from utils.chinese_query_parser import ChineseQueryParser
parser = ChineseQueryParser()
result = parser.parse_query("查询茅台最新股价")
print(result)

# 生成SQL
sql = parser.generate_sql(result)
print(sql)
```

### 2. API测试

```bash
# 启动API服务
python -m uvicorn api.main:app --reload --host 0.0.0.0 --port 8000

# 测试查询（新终端）
curl -X POST http://localhost:8000/api/query \
  -H "Content-Type: application/json" \
  -d '{
    "question": "查询贵州茅台最新股价",
    "query_type": "hybrid"
  }'
```

## 🛠️ 故障排查

### 问题1: Schema加载失败
- **症状**: 表数量为0或报错
- **解决方案**:
  1. 检查数据库连接：`python scripts/tests/test_databases.py`
  2. 确认.env文件中的数据库配置正确
  3. 检查网络连接是否正常

### 问题2: 中文映射不准确
- **症状**: 字段映射到错误的英文名
- **原因**: 数据库字段注释可能不标准
- **解决方案**:
  1. 查看具体字段的注释：
     ```sql
     SELECT COLUMN_NAME, COLUMN_COMMENT 
     FROM INFORMATION_SCHEMA.COLUMNS 
     WHERE TABLE_SCHEMA = 'Tushare' 
       AND TABLE_NAME = 'tu_daily_detail';
     ```
  2. 手动调整解析规则

### 问题3: 查询解析失败
- **症状**: 无法识别查询类型或提取信息
- **解决方案**:
  1. 检查查询语句是否包含关键词
  2. 查看解析日志了解匹配过程
  3. 必要时添加新的查询模式

## 📈 性能基准

正常情况下的性能指标：

| 操作 | 预期时间 |
|------|---------|
| Schema加载 | < 1秒 |
| 字段映射查询 | < 10ms |
| 查询解析 | < 50ms |
| SQL生成 | < 20ms |
| 端到端查询 | < 100ms |

## 🔄 持续测试

建议在以下情况运行测试：
1. 数据库表结构变更后
2. 更新映射规则后
3. 每日例行检查（快速测试）
4. 版本发布前（完整测试）

## 📝 测试报告

测试完成后，记录以下信息：
- 测试日期和时间
- 测试环境（Windows/WSL2）
- 通过/失败的测试项
- 发现的问题和解决方案
- 性能指标

## 🤝 需要帮助？

如果遇到问题：
1. 查看日志文件：`logs/`目录
2. 运行系统检查：`python scripts/utils/system_check.py`
3. 查看项目文档：`docs/`目录
4. 提交Issue到GitHub仓库