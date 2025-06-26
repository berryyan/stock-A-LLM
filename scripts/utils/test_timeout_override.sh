#!/bin/bash
# 测试各种超时设置方法

echo "🔍 测试超时覆盖方法..."
echo "================================"

# 方法1: 使用timeout命令
echo "1. 使用GNU timeout命令:"
timeout --version 2>/dev/null || echo "❌ timeout命令不可用"

# 方法2: 检查环境变量
echo -e "\n2. 检查环境变量:"
echo "BASH_TIMEOUT=$BASH_TIMEOUT"
echo "COMMAND_TIMEOUT=$COMMAND_TIMEOUT"
echo "SHELL_TIMEOUT=$SHELL_TIMEOUT"
echo "SUBPROCESS_TIMEOUT=$SUBPROCESS_TIMEOUT"

# 方法3: 使用expect
echo -e "\n3. 检查expect可用性:"
which expect || echo "❌ expect不可用"

# 方法4: 使用Python subprocess
echo -e "\n4. Python subprocess测试:"
python3 -c "
import subprocess
import time

print('尝试运行5秒的sleep命令...')
start = time.time()
try:
    # 设置10秒超时
    result = subprocess.run(['sleep', '5'], timeout=10, capture_output=True)
    elapsed = time.time() - start
    print(f'✅ 成功! 耗时: {elapsed:.2f}秒')
except subprocess.TimeoutExpired:
    print('❌ 超时!')
"

# 方法5: 使用bash内置的TMOUT
echo -e "\n5. Bash TMOUT变量:"
echo "TMOUT=$TMOUT"

# 方法6: 创建Python包装器
echo -e "\n6. 创建Python包装器示例:"
cat << 'EOF' > /tmp/long_running_wrapper.py
#!/usr/bin/env python3
import sys
import subprocess
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--timeout', type=int, default=600)
parser.add_argument('command', nargs='+')
args = parser.parse_args()

try:
    result = subprocess.run(args.command, timeout=args.timeout, capture_output=True, text=True)
    print(result.stdout)
    if result.stderr:
        print(result.stderr, file=sys.stderr)
    sys.exit(result.returncode)
except subprocess.TimeoutExpired:
    print(f"Command timed out after {args.timeout} seconds", file=sys.stderr)
    sys.exit(124)
EOF

chmod +x /tmp/long_running_wrapper.py
echo "✅ 包装器已创建: /tmp/long_running_wrapper.py"

# 方法7: 使用nohup和后台任务
echo -e "\n7. 后台任务方法:"
echo "示例: nohup command > output.log 2>&1 & "
echo "然后使用tail -f output.log查看输出"

echo -e "\n================================"
echo "📊 建议的解决方案:"
echo "1. 使用Python异步查询助手 (async_query_helper.py)"
echo "2. 使用查询任务管理器 (query_job_manager.py)"
echo "3. 使用Python包装器运行长命令"
echo "4. 在Windows环境执行长时间任务"