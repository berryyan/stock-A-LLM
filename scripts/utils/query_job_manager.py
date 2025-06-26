#!/usr/bin/env python3
"""
查询任务管理器 - 处理长时间查询的完整解决方案
支持创建、监控和获取查询结果
"""

import os
import sys
import json
import time
import uuid
import signal
import pickle
import argparse
import requests
from datetime import datetime
from pathlib import Path

class QueryJobManager:
    def __init__(self, job_dir="/tmp/stock_query_jobs"):
        self.job_dir = Path(job_dir)
        self.job_dir.mkdir(exist_ok=True)
        self.api_url = "http://10.0.0.66:8000"
    
    def submit_query(self, question, query_type="hybrid", job_name=None):
        """提交查询任务"""
        job_id = str(uuid.uuid4())[:8]
        job_name = job_name or f"query_{job_id}"
        
        job_info = {
            "job_id": job_id,
            "job_name": job_name,
            "question": question,
            "query_type": query_type,
            "status": "submitted",
            "created_at": datetime.now().isoformat(),
            "started_at": None,
            "completed_at": None,
            "result": None,
            "error": None
        }
        
        # 保存任务信息
        job_file = self.job_dir / f"{job_id}.json"
        with open(job_file, 'w', encoding='utf-8') as f:
            json.dump(job_info, f, ensure_ascii=False, indent=2)
        
        # 创建执行脚本
        script_content = f"""#!/usr/bin/env python3
import requests
import json
from datetime import datetime

job_file = "{job_file}"

# 读取任务信息
with open(job_file, 'r', encoding='utf-8') as f:
    job_info = json.load(f)

# 更新状态为运行中
job_info['status'] = 'running'
job_info['started_at'] = datetime.now().isoformat()
with open(job_file, 'w', encoding='utf-8') as f:
    json.dump(job_info, f, ensure_ascii=False, indent=2)

# 执行查询
try:
    response = requests.post(
        "{self.api_url}/query",
        json={{
            "question": job_info['question'],
            "query_type": job_info['query_type'],
            "top_k": 5
        }},
        timeout=3600  # 1小时超时
    )
    
    job_info['result'] = response.json()
    job_info['status'] = 'completed'
    
except Exception as e:
    job_info['error'] = str(e)
    job_info['status'] = 'failed'

# 更新完成时间
job_info['completed_at'] = datetime.now().isoformat()

# 保存结果
with open(job_file, 'w', encoding='utf-8') as f:
    json.dump(job_info, f, ensure_ascii=False, indent=2)
"""
        
        script_file = self.job_dir / f"{job_id}_script.py"
        with open(script_file, 'w') as f:
            f.write(script_content)
        
        # 在后台执行
        os.system(f"nohup {sys.executable} {script_file} > /dev/null 2>&1 &")
        
        print(f"✅ 查询任务已提交")
        print(f"📋 任务ID: {job_id}")
        print(f"❓ 问题: {question}")
        print(f"🔄 查询类型: {query_type}")
        print(f"\n使用以下命令查看状态:")
        print(f"python {__file__} status {job_id}")
        
        return job_id
    
    def get_status(self, job_id):
        """获取任务状态"""
        job_file = self.job_dir / f"{job_id}.json"
        
        if not job_file.exists():
            return {"error": f"Job {job_id} not found"}
        
        with open(job_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def list_jobs(self, limit=10):
        """列出最近的任务"""
        jobs = []
        
        for job_file in self.job_dir.glob("*.json"):
            if "_script" not in job_file.stem:
                with open(job_file, 'r', encoding='utf-8') as f:
                    jobs.append(json.load(f))
        
        # 按创建时间排序
        jobs.sort(key=lambda x: x['created_at'], reverse=True)
        
        return jobs[:limit]
    
    def wait_for_completion(self, job_id, check_interval=5, max_wait=3600):
        """等待任务完成"""
        start_time = time.time()
        
        while True:
            status = self.get_status(job_id)
            
            if 'error' in status:
                return status
            
            if status['status'] in ['completed', 'failed']:
                return status
            
            elapsed = time.time() - start_time
            if elapsed > max_wait:
                return {"error": f"Timeout waiting for job {job_id}"}
            
            print(f"⏳ 等待中... (已过 {int(elapsed)}秒)")
            time.sleep(check_interval)

def main():
    parser = argparse.ArgumentParser(description='查询任务管理器')
    subparsers = parser.add_subparsers(dest='action', help='操作')
    
    # 提交查询
    submit_parser = subparsers.add_parser('submit', help='提交查询任务')
    submit_parser.add_argument('question', help='查询问题')
    submit_parser.add_argument('--type', default='hybrid', 
                              choices=['sql', 'rag', 'financial_analysis', 'money_flow', 'hybrid'],
                              help='查询类型')
    submit_parser.add_argument('--name', help='任务名称')
    submit_parser.add_argument('--wait', action='store_true', help='等待任务完成')
    
    # 查看状态
    status_parser = subparsers.add_parser('status', help='查看任务状态')
    status_parser.add_argument('job_id', help='任务ID')
    
    # 列出任务
    list_parser = subparsers.add_parser('list', help='列出最近的任务')
    list_parser.add_argument('--limit', type=int, default=10, help='显示数量')
    
    args = parser.parse_args()
    
    manager = QueryJobManager()
    
    if args.action == 'submit':
        job_id = manager.submit_query(args.question, args.type, args.name)
        
        if args.wait:
            print("\n⏳ 等待任务完成...")
            result = manager.wait_for_completion(job_id)
            print("\n📋 查询结果:")
            print(json.dumps(result, ensure_ascii=False, indent=2))
            
    elif args.action == 'status':
        status = manager.get_status(args.job_id)
        print(json.dumps(status, ensure_ascii=False, indent=2))
        
    elif args.action == 'list':
        jobs = manager.list_jobs(args.limit)
        
        print(f"\n📋 最近的 {len(jobs)} 个任务:\n")
        for job in jobs:
            print(f"ID: {job['job_id']} | 状态: {job['status']} | 问题: {job['question'][:30]}...")
            print(f"   创建时间: {job['created_at']}")
            print()
    else:
        parser.print_help()

if __name__ == "__main__":
    main()