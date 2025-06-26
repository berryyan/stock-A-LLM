#!/usr/bin/env python3
"""
Anaconda环境检查脚本
帮助决定是复制现有环境还是创建新环境
"""

import subprocess
import json
import os
from pathlib import Path


def run_command(cmd):
    """运行命令并返回输出"""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        return result.stdout.strip()
    except Exception as e:
        return f"Error: {str(e)}"


def get_conda_info():
    """获取conda环境信息"""
    print("=== Conda环境信息 ===\n")
    
    # 获取conda版本
    conda_version = run_command("conda --version")
    print(f"Conda版本: {conda_version}")
    
    # 获取所有环境
    print("\n可用的Conda环境:")
    envs = run_command("conda env list")
    print(envs)
    
    # 获取当前环境
    current_env = run_command("conda info --json")
    try:
        info = json.loads(current_env)
        active_env = info.get('active_prefix_name', 'base')
        print(f"\n当前激活的环境: {active_env}")
    except:
        print("\n无法解析当前环境信息")


def check_env_size(env_name='base'):
    """检查环境大小"""
    print(f"\n=== 检查环境 '{env_name}' 的大小 ===\n")
    
    # 获取环境路径
    conda_info = run_command("conda info --json")
    try:
        info = json.loads(conda_info)
        envs_dirs = info.get('envs_dirs', [])
        
        # 查找环境路径
        env_path = None
        for env_dir in envs_dirs:
            potential_path = Path(env_dir) / env_name
            if potential_path.exists():
                env_path = potential_path
                break
        
        if not env_path:
            # 检查是否是base环境
            root_prefix = info.get('root_prefix')
            if root_prefix and env_name == 'base':
                env_path = Path(root_prefix)
        
        if env_path and env_path.exists():
            # 计算大小（简化版）
            total_size = sum(f.stat().st_size for f in env_path.rglob('*') if f.is_file())
            size_gb = total_size / (1024**3)
            print(f"环境路径: {env_path}")
            print(f"环境大小: {size_gb:.2f} GB")
            
            # 提供建议
            if size_gb > 5:
                print("\n⚠️ 环境较大(>5GB)，建议创建新的轻量级环境")
            else:
                print("\n✅ 环境大小适中，可以复制此环境")
        else:
            print(f"未找到环境 '{env_name}'")
            
    except Exception as e:
        print(f"检查环境大小时出错: {str(e)}")


def list_key_packages():
    """列出关键包"""
    print("\n=== 当前环境的关键包 ===\n")
    
    packages = run_command("conda list")
    lines = packages.split('\n')
    
    # 筛选关键包
    key_packages = ['python', 'nodejs', 'numpy', 'pandas', 'fastapi', 
                    'langchain', 'torch', 'tensorflow', 'jupyter']
    
    print("已安装的关键包:")
    for line in lines:
        for pkg in key_packages:
            if line.startswith(pkg + ' '):
                print(f"  {line}")
                break


def provide_recommendation():
    """提供环境策略建议"""
    print("\n=== 环境策略建议 ===\n")
    
    print("基于你的项目特点，建议采用以下策略：")
    print("\n1. 【推荐】复制现有环境方案:")
    print("   conda create -n stock-frontend --clone [your-current-env]")
    print("   conda activate stock-frontend")
    print("   conda install -c conda-forge nodejs=18")
    print("\n   优势：")
    print("   - 保留所有Python依赖，方便前后端联调")
    print("   - 继承已有配置，减少重复设置")
    print("   - 适合需要同时运行Python和Node.js的场景")
    
    print("\n2. 【备选】创建轻量级环境:")
    print("   conda create -n stock-frontend-minimal python=3.10")
    print("   conda activate stock-frontend-minimal")
    print("   conda install -c conda-forge nodejs=18")
    print("\n   适用场景：")
    print("   - 现有环境过大(>5GB)")
    print("   - 只做纯前端开发")
    print("   - 想要最快的启动速度")
    
    print("\n3. 【进阶】使用mamba加速:")
    print("   conda install mamba -n base -c conda-forge")
    print("   mamba create -n stock-frontend --clone [your-current-env]")
    print("   (mamba比conda快5-10倍)")


if __name__ == "__main__":
    print("股票分析系统 - Anaconda环境检查工具\n")
    print("="*50)
    
    # 检查conda是否可用
    conda_check = run_command("conda --version")
    if "conda" not in conda_check.lower():
        print("错误：未检测到conda，请确保已安装Anaconda并添加到PATH")
        exit(1)
    
    # 执行检查
    get_conda_info()
    
    # 检查常用环境
    print("\n" + "="*50)
    check_env_size('base')
    
    # 列出关键包
    print("\n" + "="*50)
    list_key_packages()
    
    # 提供建议
    print("\n" + "="*50)
    provide_recommendation()
    
    print("\n" + "="*50)
    print("\n运行完成！请根据上述信息选择合适的环境策略。")