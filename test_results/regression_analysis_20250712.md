# v2.3.0 回归测试分析报告

生成时间: 2025-07-13 00:30:13

## 测试环境
- 操作系统: Windows
- Python环境: Anaconda (stock-frontend)
- 测试类型: 完整综合测试

## 总体统计
- 总测试用例: 456
- 通过: 202
- 失败: 254
- 总体通过率: 44.3%

## 各Agent测试结果

| Agent | 测试数 | 通过 | 失败 | 通过率 |
|-------|--------|------|------|--------|
| SQL Agent | 328 | 138 | 190 | 42.1% |
| Money Flow Agent | 0 | 0 | 0 | 0.0% |
| Financial Agent | 128 | 64 | 64 | 50.0% |
| RAG Agent | 0 | 0 | 0 | 0.0% |
| Hybrid Agent | 0 | 0 | 0 | 0.0% |

## 详细问题分析

### SQL Agent

**主要错误:**
1. sh
2. Exception: 'gbk' codec can't encode character '\u2705' in position 4: illegal multibyte sequence
3. 'gbk' codec can't encode character '\u2705' in position 4: illegal multibyte sequence

### Money Flow Agent

**主要错误:**
1. 'gbk' codec can't encode character '\u2717' in position 4: illegal multibyte sequence
2. 'gbk' codec can't encode character '\u2713' in position 4: illegal multibyte sequence

### Financial Agent

**主要错误:**
1. sh
2. sz
3. 'gbk' codec can't encode character '\u2705' in position 4: illegal multibyte sequence

