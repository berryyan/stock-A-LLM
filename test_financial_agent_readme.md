# Financial Agent 测试说明

## 最新修复 (2025-07-11)

已修复的问题：
1. ✅ 方法名不匹配：`dupont_analysis` 和 `cash_flow_quality_analysis`
2. ✅ 不存在的方法调用：`_analyze_profitability`、`_analyze_solvency`、`_analyze_growth`、`compare_financial_periods`
3. ✅ 参数验证正常工作

## 测试脚本概述

本目录包含4个Financial Agent的测试脚本：

1. **test_financial_agent_fix_verify.py** - 修复验证脚本（最新）
   - 专门验证方法调用修复
   - 只测试之前失败的4个用例
   - 快速确认修复是否成功

2. **test_financial_agent_quick_verify.py** - 快速验证脚本（5-10分钟）
   - 验证方法名修复是否成功
   - 验证参数验证是否正常
   - 每个分析类型测试2个用例
   - 共16个测试用例

3. **test_financial_agent_comprehensive_windows.py** - Windows优化版综合测试（推荐）
   - 为Windows环境优化，考虑LLM响应时间
   - 支持多种运行模式
   - 64个完整测试用例
   - 生成详细JSON报告

4. **test_financial_agent_comprehensive_fixed.py** - 完整测试脚本
   - 基于test-guide-comprehensive.md标准
   - 涵盖所有边界情况
   - 适合深度测试

## 运行方法

### 0. 修复验证（最新，推荐先运行）
```bash
# Windows环境
python test_financial_agent_fix_verify.py

# 预计时间：30秒
# 用途：验证方法调用修复是否成功
```

### 1. 快速验证
```bash
# Windows环境
python test_financial_agent_quick_verify.py

# 预计时间：5-10分钟（包含LLM响应）
# 用途：快速验证核心功能是否正常
```

### 2. 综合测试 - Windows优化版

#### 完整测试（64个用例）
```bash
python test_financial_agent_comprehensive_windows.py

# 预计时间：30-40分钟（包含LLM响应时间）
```

#### 快速测试模式（16个用例）
```bash
python test_financial_agent_comprehensive_windows.py --quick

# 预计时间：8-10分钟
# 每个类别只测试2个用例（1正1负）
```

#### 只测试正向用例
```bash
python test_financial_agent_comprehensive_windows.py --positive

# 预计时间：20-25分钟
# 只测试应该成功的用例
```

#### 只测试负向用例
```bash
python test_financial_agent_comprehensive_windows.py --negative

# 预计时间：5-10分钟
# 只测试应该失败的用例（验证错误处理）
```

#### 测试特定类别
```bash
# 只测试财务健康度和杜邦分析
python test_financial_agent_comprehensive_windows.py --categories "1.财务健康度分析" "2.杜邦分析"
```

## 测试类别说明

1. **财务健康度分析** - 综合财务评分
2. **杜邦分析** - ROE三因素分解
3. **现金流质量分析** - 现金流评估
4. **多期财务对比** - 历史数据对比
5. **盈利能力分析** - 利润率等指标
6. **偿债能力分析** - 负债和流动性
7. **运营能力分析** - 周转率等效率指标
8. **成长能力分析** - 增长率和发展潜力

## 测试原则

- **严格验证**：不接受股票简称（如"茅台"），必须使用完整名称（如"贵州茅台"）
- **大小写敏感**：后缀必须大写（.SH/.SZ/.BJ）
- **完整性检查**：查询必须包含股票信息

## 已知问题修复

1. ✅ 方法名不匹配问题已修复
   - `perform_dupont_analysis` → `dupont_analysis`
   - `analyze_cash_flow_quality` → `cash_flow_quality_analysis`

2. ✅ 参数验证正常工作
   - 正确拒绝股票简称
   - 提供友好错误提示

## 测试报告

测试完成后会生成JSON格式的测试报告：
- 文件名：`test_financial_agent_report_YYYYMMDD_HHMMSS.json`
- 包含：总体统计、分类统计、详细测试结果

## 注意事项

1. **LLM响应时间**：财务分析需要调用LLM，单个成功查询可能需要20-40秒
2. **网络连接**：确保能访问DeepSeek API
3. **数据库连接**：确保能访问MySQL数据库
4. **环境激活**：Windows环境请先激活conda环境
   ```bash
   conda activate stock-frontend
   ```

## 目标

- 修复验证：100%通过率（方法调用不再报错）
- 快速验证：75%+通过率（已知运营能力会被识别为财务健康度）
- 综合测试：目标90%+通过率（考虑网络等因素）

## 已知限制

由于父类 `FinancialAgent` 的设计，某些分析类型会被合并处理：
- `profitability`（盈利能力）→ 实际调用 `analyze_financial_health`
- `solvency`（偿债能力）→ 实际调用 `analyze_financial_health`
- `growth`（成长能力）→ 实际调用 `analyze_financial_health`
- `comparison`（多期对比）→ 暂时调用 `analyze_financial_health`

这意味着虽然查询被正确识别，但返回的都是综合财务健康度分析结果。