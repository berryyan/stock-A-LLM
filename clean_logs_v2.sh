#!/bin/bash
# 日志清理脚本 - v2.1.4 Phase 1开发前准备
# 兼容Linux和macOS环境

echo "开始清理日志文件..."
echo "当前日志目录大小："
du -sh logs/

# 1. 清理特定的大日志文件（如果存在）
if [ -f "logs/pdf_cache_check.log" ]; then
    echo "清理 pdf_cache_check.log..."
    > logs/pdf_cache_check.log  # 清空文件内容但保留文件
fi

# 2. 清理测试相关的日志文件
echo -e "\n清理测试日志文件..."
for testlog in logs/test_*.log; do
    if [ -f "$testlog" ]; then
        echo "清空 $(basename $testlog)..."
        > "$testlog"
    fi
done

# 3. 清理已经不存在的Agent日志（Phase 2回滚后的残留）
for oldlog in logs/rank_agent.log logs/anns_agent.log logs/qa_agent.log; do
    if [ -f "$oldlog" ]; then
        echo "删除 $(basename $oldlog)..."
        rm "$oldlog"
    fi
done

# 4. 清理旧的去重和扫描日志
echo -e "\n清理旧的维护日志..."
for oldlog in logs/milvus_dedup.log logs/milvus_final_dedup.log logs/milvus_full_scan.log logs/verify_integrity.log; do
    if [ -f "$oldlog" ]; then
        echo "清空 $(basename $oldlog)..."
        > "$oldlog"
    fi
done

# 5. 截断大于1MB的日志文件，保留最后1000行
echo -e "\n处理大型日志文件..."
for logfile in logs/*.log; do
    if [ -f "$logfile" ]; then
        # 使用跨平台的方式获取文件大小
        if command -v stat >/dev/null 2>&1; then
            # Linux方式
            size=$(stat -c%s "$logfile" 2>/dev/null)
            # 如果失败，尝试macOS方式
            if [ -z "$size" ]; then
                size=$(stat -f%z "$logfile" 2>/dev/null)
            fi
        else
            # 备用方案：使用ls
            size=$(ls -l "$logfile" | awk '{print $5}')
        fi
        
        if [ -n "$size" ] && [ "$size" -gt 1048576 ]; then  # 1MB = 1024 * 1024
            filename=$(basename "$logfile")
            echo "截断 $filename ($(echo "scale=2; $size/1048576" | bc)MB -> 保留最后2000行)..."
            tail -n 2000 "$logfile" > "$logfile.tmp"
            mv "$logfile.tmp" "$logfile"
        fi
    fi
done

# 6. 删除所有空日志文件
echo -e "\n删除空日志文件..."
find logs -type f -size 0 -name "*.log" -delete

# 7. 创建清理报告
echo -e "\n=== 清理完成！==="
echo "清理后的日志目录大小："
du -sh logs/

echo -e "\n主要日志文件（前10个）："
ls -lh logs/*.log 2>/dev/null | grep -v '^total' | sort -k5 -h -r | head -10

echo -e "\n日志文件总数："
find logs -name "*.log" -type f | wc -l

echo -e "\n✅ 日志清理完成，系统已准备好进行Phase 1开发！"