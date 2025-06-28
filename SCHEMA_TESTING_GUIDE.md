# 数据库Schema中文映射系统测试指南

## 系统概述

**核心目标**：性能优化 - 将Schema查询时间从3-5秒降低到<10ms

**解决的问题**：
- Agent每次查询都需要先查INFORMATION_SCHEMA了解表结构（耗时3-5秒）
- 用户等待时间长，体验差
- 系统资源浪费在重复的Schema查询上

**优化方案**：
- 启动时一次性加载所有Schema信息到内存
- 提供快速的数据定位服务（<10ms响应）
- 让Agent立即知道数据在哪里，无需"思考"

## 测试步骤

### 1. 环境准备

```bash
# 激活虚拟环境
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate  # Windows

# 确认数据库连接正常
python scripts/tests/test_databases.py
```

### 2. 运行基础功能测试

```bash
# 测试Schema知识库核心功能
python test_schema_knowledge_base.py
```

**预期输出**：
```
系统概况:
  表数量: 20+
  字段总数: 1000+
  主题分类: 6
  查询模板: 4
  中文映射: 25+

1. 测试基础功能
数据定位测试:
✓ 营业收入     -> tu_income.revenue (耗时: 0.5ms)
✓ 收盘价       -> tu_daily_detail.close (耗时: 0.3ms)
✓ 净利润       -> tu_income.n_income (耗时: 0.4ms)

4. 性能对比测试
知识库查询1000次: 0.008秒 (平均: 0.008ms)
数据库查询1000次(模拟): 3500.0秒 (平均: 3500.0ms)
性能提升: 437倍
```

### 3. 运行集成测试

```bash
# 测试与各Agent的集成
python test_schema_integration.py
```

**预期输出**：
```
测试SQL Agent集成
查询: 贵州茅台最新股价
  知识库定位耗时: 0.8ms
  建议查询表: tu_daily_detail
  总查询耗时: 5.2秒
  查询成功: 是

性能改进效果对比
旧方案模拟（查询数据库Schema）:
  平均时间: 3.9秒
新方案（使用Schema知识库）:
  平均时间: 8.5ms
性能提升: 459倍
```

### 4. 验证Agent查询性能提升

#### 测试SQL查询（对比测试）

```bash
# 使用API测试
curl -X POST http://localhost:8000/api/query \
  -H "Content-Type: application/json" \
  -d '{
    "question": "贵州茅台最新股价",
    "query_type": "sql"
  }'
```

**关注点**：
- 查询响应时间应该明显减少
- 日志中不应该再看到"查询INFORMATION_SCHEMA"的记录
- Agent应该直接生成SQL，无需先查询表结构

#### 测试财务分析查询

```bash
curl -X POST http://localhost:8000/api/query \
  -H "Content-Type: application/json" \
  -d '{
    "question": "分析贵州茅台的财务健康度",
    "query_type": "financial"
  }'
```

**关注点**：
- Financial Agent应该立即知道需要查询哪些表
- 不再有"寻找财务数据表"的延迟

### 5. 性能基准测试

创建一个性能对比脚本：

```bash
# 创建性能基准测试
python -c "
import time
from agents.sql_agent import SQLAgent

agent = SQLAgent()
queries = [
    '贵州茅台最新股价',
    '平安银行成交量',
    '比亚迪市值'
]

print('测试查询性能...')
for query in queries:
    start = time.time()
    result = agent.process_query(query)
    elapsed = time.time() - start
    print(f'{query}: {elapsed:.1f}秒')
"
```

### 6. 监控和验证

#### 查看日志验证优化效果

```bash
# 查看Schema知识库日志
tail -f logs/schema_knowledge_base.log

# 应该看到：
# INFO - Schema知识库构建完成，耗时: X.XX秒
# INFO - 数据定位: 营业收入 -> tu_income.revenue (0.5ms)
```

#### 查看SQL Agent日志

```bash
tail -f logs/sql_agent.log

# 不应该再看到：
# INFO - 查询INFORMATION_SCHEMA获取表结构...
# 
# 应该看到：
# INFO - 使用Schema知识库快速定位数据
```

### 7. 压力测试

```bash
# 运行并发测试验证高负载下的性能
python -c "
import threading
import time
from utils.schema_knowledge_base import SchemaKnowledgeBase

kb = SchemaKnowledgeBase()

def stress_test(thread_id):
    for i in range(1000):
        kb.locate_data('营业收入')
        kb.locate_data('股价')
        kb.get_tables_for_topic('财务')

threads = []
start = time.time()

for i in range(50):
    t = threading.Thread(target=stress_test, args=(i,))
    threads.append(t)
    t.start()

for t in threads:
    t.join()

elapsed = time.time() - start
total_queries = 50 * 1000 * 3
qps = total_queries / elapsed

print(f'总查询数: {total_queries}')
print(f'总耗时: {elapsed:.1f}秒')
print(f'QPS: {qps:.0f}')
"
```

## 测试检查清单

- [ ] Schema知识库启动时成功加载（<5秒）
- [ ] 单次数据定位查询 <10ms
- [ ] 中文名称正确映射到英文字段
- [ ] 主题分类查询正确返回相关表
- [ ] 查询模板包含正确的SQL片段
- [ ] SQL Agent不再查询INFORMATION_SCHEMA
- [ ] Financial Agent快速获取财务表结构
- [ ] MoneyFlow Agent快速获取资金流向字段
- [ ] 并发访问性能稳定
- [ ] 内存使用合理（<100MB）

## 故障排查

### 问题1：知识库加载失败
```bash
# 检查数据库连接
python scripts/tests/test_databases.py

# 手动测试加载
python utils/schema_knowledge_base.py
```

### 问题2：查询性能没有提升
```bash
# 检查是否正确集成
grep -r "SchemaKnowledgeBase" agents/

# 确认Agent使用了知识库
grep -r "locate_data" agents/
```

### 问题3：中文映射不工作
```bash
# 测试中文映射
python -c "
from utils.schema_knowledge_base import SchemaKnowledgeBase
kb = SchemaKnowledgeBase()
print(kb.locate_data('营业收入'))
print(kb.chinese_mapping)
"
```

## 性能指标基准

| 指标 | 优化前 | 优化后 | 提升倍数 |
|-----|--------|--------|----------|
| Schema查询时间 | 3-5秒 | <10ms | 300-500倍 |
| SQL生成时间 | 5-8秒 | 1-2秒 | 4-5倍 |
| 并发QPS | 10-20 | 1000+ | 50-100倍 |
| 内存占用 | 基础 | +50-100MB | 可接受 |

## 总结

这个Schema知识库系统是纯粹的**性能优化**，不改变任何功能，只是让系统更快：

1. **对用户透明**：用户查询方式不变，但响应更快
2. **对Agent优化**：Agent不再需要"思考"数据在哪里
3. **系统级提升**：减少数据库负载，提高并发能力

成功标志：
- ✅ 用户明显感觉查询变快了
- ✅ 日志中不再有重复的Schema查询
- ✅ 系统可以处理更多并发请求