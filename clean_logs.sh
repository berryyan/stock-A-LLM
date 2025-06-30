#!/bin/bash
# 日志清理脚本 - v2.1.2测试前准备

echo "开始清理日志文件..."

# 1. 删除超大的pdf_cache_check.log
if [ -f "logs/pdf_cache_check.log" ]; then
    echo "删除 pdf_cache_check.log (108MB)..."
    rm logs/pdf_cache_check.log
    touch logs/pdf_cache_check.log  # 创建空文件以保持日志功能
fi

# 2. 删除所有空日志文件
echo "删除空日志文件..."
find logs -type f -size 0 -name "*.log" -delete

# 3. 截断大于10MB的日志文件，保留最后1000行
echo "截断大型日志文件..."
for logfile in logs/*.log; do
    if [ -f "$logfile" ]; then
        size=$(stat -f%z "$logfile" 2>/dev/null || stat -c%s "$logfile" 2>/dev/null)
        if [ "$size" -gt 10485760 ]; then  # 10MB = 10 * 1024 * 1024
            echo "截断 $(basename $logfile) (保留最后1000行)..."
            tail -n 1000 "$logfile" > "$logfile.tmp"
            mv "$logfile.tmp" "$logfile"
        fi
    fi
done

# 4. 显示清理后的状态
echo -e "\n清理完成！当前日志状态："
du -sh logs/
echo -e "\n主要日志文件："
ls -lh logs/*.log | grep -v '^-rw.*0B' | head -10

echo -e "\n提示：已为测试准备就绪！"