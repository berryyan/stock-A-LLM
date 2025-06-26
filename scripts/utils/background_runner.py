#!/usr/bin/env python3
"""
后台任务执行器 - 处理长时间运行的任务
通过创建独立进程来避免超时限制
"""

import subprocess
import json
import os
import time
import uuid
from datetime import datetime
import argparse
import sys

class BackgroundTaskRunner:
    def __init__(self, task_dir="/tmp/stock_analysis_tasks"):
        self.task_dir = task_dir
        os.makedirs(task_dir, exist_ok=True)
    
    def create_task(self, command, task_name=None):
        """创建后台任务"""
        task_id = str(uuid.uuid4())[:8]
        task_name = task_name or f"task_{task_id}"
        
        # 任务文件路径
        status_file = os.path.join(self.task_dir, f"{task_id}_status.json")
        output_file = os.path.join(self.task_dir, f"{task_id}_output.txt")
        error_file = os.path.join(self.task_dir, f"{task_id}_error.txt")
        
        # 初始状态
        status = {
            "task_id": task_id,
            "task_name": task_name,
            "command": command,
            "status": "running",
            "start_time": datetime.now().isoformat(),
            "end_time": None,
            "output_file": output_file,
            "error_file": error_file
        }
        
        with open(status_file, 'w') as f:
            json.dump(status, f, indent=2)
        
        # 创建后台执行脚本
        script = f"""#!/bin/bash
# 任务ID: {task_id}
# 任务名称: {task_name}

# 执行命令并保存输出
({command}) > {output_file} 2> {error_file}

# 更新状态
python3 -c "
import json
from datetime import datetime

with open('{status_file}', 'r') as f:
    status = json.load(f)

status['status'] = 'completed' if $? == 0 else 'failed'
status['end_time'] = datetime.now().isoformat()
status['exit_code'] = $?

with open('{status_file}', 'w') as f:
    json.dump(status, f, indent=2)
"
"""
        
        script_file = os.path.join(self.task_dir, f"{task_id}_script.sh")
        with open(script_file, 'w') as f:
            f.write(script)
        
        os.chmod(script_file, 0o755)
        
        # 在后台执行
        subprocess.Popen(['nohup', 'bash', script_file], 
                        stdout=subprocess.DEVNULL, 
                        stderr=subprocess.DEVNULL,
                        preexec_fn=os.setpgrp)
        
        print(f"✅ 任务已创建并在后台运行")
        print(f"📋 任务ID: {task_id}")
        print(f"📁 任务目录: {self.task_dir}")
        
        return task_id
    
    def check_status(self, task_id):
        """检查任务状态"""
        status_file = os.path.join(self.task_dir, f"{task_id}_status.json")
        
        if not os.path.exists(status_file):
            return {"error": "Task not found"}
        
        with open(status_file, 'r') as f:
            status = json.load(f)
        
        # 如果任务完成，读取输出
        if status['status'] in ['completed', 'failed']:
            if os.path.exists(status['output_file']):
                with open(status['output_file'], 'r') as f:
                    status['output'] = f.read()
            
            if os.path.exists(status['error_file']):
                with open(status['error_file'], 'r') as f:
                    error_content = f.read()
                    if error_content:
                        status['error'] = error_content
        
        return status
    
    def list_tasks(self):
        """列出所有任务"""
        tasks = []
        for file in os.listdir(self.task_dir):
            if file.endswith('_status.json'):
                with open(os.path.join(self.task_dir, file), 'r') as f:
                    tasks.append(json.load(f))
        
        return sorted(tasks, key=lambda x: x['start_time'], reverse=True)

def main():
    parser = argparse.ArgumentParser(description='后台任务执行器')
    subparsers = parser.add_subparsers(dest='action', help='操作')
    
    # 创建任务
    create_parser = subparsers.add_parser('create', help='创建新任务')
    create_parser.add_argument('command', help='要执行的命令')
    create_parser.add_argument('--name', help='任务名称')
    
    # 检查状态
    status_parser = subparsers.add_parser('status', help='检查任务状态')
    status_parser.add_argument('task_id', help='任务ID')
    
    # 列出任务
    list_parser = subparsers.add_parser('list', help='列出所有任务')
    
    args = parser.parse_args()
    
    runner = BackgroundTaskRunner()
    
    if args.action == 'create':
        task_id = runner.create_task(args.command, args.name)
        print(f"\n使用以下命令检查状态:")
        print(f"python {__file__} status {task_id}")
        
    elif args.action == 'status':
        status = runner.check_status(args.task_id)
        print(json.dumps(status, ensure_ascii=False, indent=2))
        
    elif args.action == 'list':
        tasks = runner.list_tasks()
        for task in tasks:
            print(f"\n任务ID: {task['task_id']}")
            print(f"名称: {task['task_name']}")
            print(f"状态: {task['status']}")
            print(f"开始时间: {task['start_time']}")
    else:
        parser.print_help()

if __name__ == "__main__":
    main()