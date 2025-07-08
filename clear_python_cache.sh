#!/bin/bash
# 清除Python缓存脚本

echo "清除Python缓存..."
echo "=================="

# 1. 清除所有__pycache__目录
echo "1. 清除__pycache__目录..."
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null

# 2. 清除所有.pyc文件
echo "2. 清除.pyc文件..."
find . -type f -name "*.pyc" -delete

# 3. 清除所有.pyo文件
echo "3. 清除.pyo文件..."
find . -type f -name "*.pyo" -delete

# 4. 清除pytest缓存
echo "4. 清除pytest缓存..."
find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null

# 5. 清除Python egg-info
echo "5. 清除egg-info..."
find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null

echo ""
echo "✅ Python缓存清除完成！"
echo ""
echo "现在可以运行综合测试了："
echo "python test_sql_agent_comprehensive.py"