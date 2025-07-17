# Claude快速恢复开发指南

更新时间：2025-07-13  
用途：帮助Claude快速恢复到当前开发状态

## 🚀 快速启动命令

```
请阅读QUICK_RESUME_GUIDE.md，快速恢复到v2.4.0 Concept Agent开发状态
```

## 📋 当前开发状态总结

### 项目版本
- **当前版本**：v2.3.0（已发布）
- **开发版本**：v2.4.0（进行中）
- **分支**：dev-react-frontend-v2

### 正在开发的功能
- **Concept Agent**（概念股分析专家）
- **状态**：初步设计完成，等待数据表创建
- **优先级**：最高（4个新Agent中的第1个）

### 关键文档位置
1. **Concept Agent设计**：`docs/design/concept_agent_preliminary_design.md`
2. **开发进度**：`docs/development/v2.4.0_progress_tracking.md`
3. **测试指南**：`test-guide-comprehensive.md`

## 🎯 Concept Agent核心要点

### 1. 核心价值
基于事实依据的概念股分析，不是网络瞎猜

### 2. 两类查询
- **A类**：概念发现 - "充电宝相关概念股"
- **B类**：技术筛选 - "半导体概念股+技术条件"

### 3. 关联度评分（100分）
- 软件收录：40分
- 财报证据：30分
- 互动平台：20分
- 公告证据：10分

### 4. 当前阻塞
等待外部项目创建以下数据表：
- tu_concept_blocks
- tu_concept_stocks
- tu_concept_evidence
- tu_concept_technical_cache

## 💡 待讨论细节

1. **模糊匹配算法**
   - 分词方案？
   - Embedding方案？
   - 混合方案？

2. **技术指标细节**
   - 多头排列定义
   - MACD状态判断
   - 成交量配合

3. **输出格式**
   - 分级显示
   - 证据展示
   - 排序规则

## 🔧 开发环境

### 激活虚拟环境
```bash
# WSL2环境
source venv/bin/activate

# Windows环境
venv\Scripts\activate
```

### 启动服务
```bash
# 后端API（Windows环境运行）
python -m uvicorn api.main_modular:app --reload --host 0.0.0.0 --port 8001

# 前端（可在WSL2开发）
cd frontend
npm run dev
```

### 运行测试
```bash
# 使用便捷脚本
./run_with_venv.sh python test_modular_comprehensive.py
```

## 📊 系统现状

### 已完成的5个Agent
1. **SQL Agent**：100%测试通过
2. **RAG Agent**：70.8%（数据覆盖限制）
3. **Financial Agent**：100%测试通过
4. **Money Flow Agent**：100%测试通过
5. **Hybrid Agent**：95%+路由准确性

### 计划的4个新Agent
1. **Concept Agent**：开发中
2. **Rank Agent**：待开始
3. **ANNS Agent**：待开始
4. **QA Agent**：待开始

## 🎬 快速恢复步骤

1. **查看最新状态**
   ```bash
   git status
   git log --oneline -5
   ```

2. **检查待办事项**
   - 查看TodoWrite工具的任务列表
   - 重点关注Concept Agent相关任务

3. **阅读关键文档**
   - CLAUDE.md - 项目整体说明
   - concept_agent_preliminary_design.md - 当前设计
   - v2.4.0_progress_tracking.md - 进度跟踪

4. **确认下一步**
   - 如果数据表已创建 → 开始详细设计和开发
   - 如果仍在等待 → 细化技术方案

## 🔗 重要链接

- [项目状态](docs/project_status/CURRENT_STATUS.md)
- [模块化系统指南](docs/MODULAR_SYSTEM_GUIDE.md)
- [API文档](http://localhost:8001/docs)

## 💬 最后的对话要点

1. 用户明确了Concept Agent是原计划的第4个Agent
2. 强调必须基于事实依据
3. 数据由外部项目提供
4. 需要支持复杂的技术筛选
5. 每日19点后更新数据

---

**提示**：如果需要更详细的上下文，可以查看最近的git提交和测试报告。