#!/bin/bash
cd /mnt/e/PycharmProjects/stock_analysis_system

# 添加所有更改
git add .

# 查看状态
echo "=== Git Status ==="
git status --short

# 提交更改
echo -e "\n=== Committing changes ==="
git commit -m "docs: 更新核心文档至v1.5.4

- 更新CLAUDE.md: 添加重要目录说明，记录流式响应功能完成
- 更新CURRENT_STATUS.md: 添加v1.5.4版本更新记录
- 更新test-guide.md: 添加流式响应功能测试部分
- 删除混淆的stock-analysis-frontend旧目录
- 完善项目结构，避免未来目录混淆"

# 查看提交日志
echo -e "\n=== Recent commits ==="
git log --oneline -5

# 显示当前分支
echo -e "\n=== Current branch ==="
git branch --show-current