#!/bin/bash
# 激活虚拟环境并运行Python脚本的便捷脚本

# 激活虚拟环境
source venv/bin/activate

# 执行传入的命令
exec "$@"