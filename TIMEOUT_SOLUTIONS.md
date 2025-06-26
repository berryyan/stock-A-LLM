# Bash超时问题解决方案总结

## 问题描述
Claude Code的Bash工具有2分钟（120秒）的硬性超时限制，这对于复杂的股票分析查询是不够的。

## 已尝试的解决方案

### 1. ✅ 异步查询助手 (推荐)
**文件**: `scripts/utils/async_query_helper.py`
**使用方法**:
```bash
source venv/bin/activate
python scripts/utils/async_query_helper.py "查询问题" --type sql --timeout 600
```
**优点**: 
- 支持自定义超时时间
- 异步执行，不受Bash限制
- 可以保存结果到文件

### 2. ✅ 查询任务管理器 (最佳方案)
**文件**: `scripts/utils/query_job_manager.py`
**使用方法**:
```bash
# 提交任务
python scripts/utils/query_job_manager.py submit "复杂查询" --type financial_analysis

# 查看状态
python scripts/utils/query_job_manager.py status <job_id>

# 列出所有任务
python scripts/utils/query_job_manager.py list
```
**优点**:
- 完全后台执行，不受任何超时限制
- 可以提交任务后离开，稍后查看结果
- 支持任务管理和历史记录

### 3. ✅ Python包装器
**示例**: `/tmp/long_running_wrapper.py`
```bash
python /tmp/long_running_wrapper.py --timeout 600 curl -X POST ...
```

### 4. ✅ 后台任务执行器
**文件**: `scripts/utils/background_runner.py`
- 创建独立进程执行长时间任务
- 支持任务状态跟踪

### 5. ❌ 环境变量方法
经测试，以下环境变量无效：
- BASH_TIMEOUT
- COMMAND_TIMEOUT
- SHELL_TIMEOUT
- SUBPROCESS_TIMEOUT

### 6. ✅ GNU timeout命令
```bash
timeout 600 command  # 设置600秒超时
```
但这仍受Claude Code的2分钟限制

## 推荐的工作流程

### 开发阶段（WSL2）
1. **快速测试** (<30秒): 直接使用curl或简单脚本
2. **中等查询** (30秒-2分钟): 使用异步查询助手
3. **长时间查询** (>2分钟): 使用查询任务管理器

### 测试阶段（Windows）
- 所有完整功能测试在Windows环境执行
- 无超时限制，可以运行任意时长

## 实际使用示例

### 财务分析查询（预计3-5分钟）
```bash
# WSL2中提交任务
source venv/bin/activate
JOB_ID=$(python scripts/utils/query_job_manager.py submit \
  "分析贵州茅台的财务健康度" \
  --type financial_analysis | grep "任务ID" | awk '{print $3}')

# 稍后检查结果
python scripts/utils/query_job_manager.py status $JOB_ID
```

### 资金流向分析（预计2-3分钟）
```bash
# 使用异步助手，设置5分钟超时
python scripts/utils/async_query_helper.py \
  "贵州茅台最近30天的资金流向" \
  --type money_flow \
  --timeout 300 \
  --output result.json
```

## 总结
虽然无法直接修改Claude Code的Bash超时限制，但通过：
1. 后台任务管理器
2. 异步Python脚本
3. 合理的开发/测试环境分工

我们可以有效地处理长时间运行的查询任务。