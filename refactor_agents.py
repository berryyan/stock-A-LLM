#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Agent重构脚本 - 统一命名和整合
"""

import os
import shutil
import re
from datetime import datetime


def backup_files():
    """备份所有Agent文件"""
    backup_dir = f"agents/backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    os.makedirs(backup_dir, exist_ok=True)
    
    files_to_backup = [
        "sql_agent.py",
        "sql_agent_v2.py", 
        "sql_agent_modular.py",
        "rag_agent.py",
        "rag_agent_modular.py",
        "financial_agent.py",
        "financial_agent_modular.py",
        "money_flow_agent.py",
        "money_flow_agent_modular.py",
    ]
    
    for filename in files_to_backup:
        src = f"agents/{filename}"
        if os.path.exists(src):
            dst = os.path.join(backup_dir, filename)
            shutil.copy2(src, dst)
            print(f"✅ 备份: {filename}")
    
    return backup_dir


def analyze_implementations():
    """分析各个实现的特点"""
    print("\n分析各个实现...")
    
    # 比较 sql_agent_v2.py 和 sql_agent_modular.py
    with open("agents/sql_agent_v2.py", 'r', encoding='utf-8') as f:
        v2_content = f.read()
    
    with open("agents/sql_agent_modular.py", 'r', encoding='utf-8') as f:
        modular_content = f.read()
    
    print("\nsql_agent_v2.py 特点:")
    print("- 完全重新实现，不继承原版")
    print("- 使用所有模块化组件")
    print(f"- 代码行数: {len(v2_content.splitlines())}")
    
    print("\nsql_agent_modular.py 特点:")
    print("- 继承自 sql_agent.py")
    print("- 部分使用模块化组件")
    print(f"- 代码行数: {len(modular_content.splitlines())}")


def update_references(old_name, new_name):
    """更新所有文件中的引用"""
    files_to_update = []
    
    # 搜索所有Python文件
    for root, dirs, files in os.walk("."):
        # 跳过备份目录和虚拟环境
        if "backup" in root or "venv" in root or ".venv" in root or "__pycache__" in root:
            continue
            
        for file in files:
            if file.endswith(".py"):
                filepath = os.path.join(root, file)
                files_to_update.append(filepath)
    
    updated_files = []
    
    for filepath in files_to_update:
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 检查是否包含需要更新的引用
            if old_name in content:
                # 更新import语句
                content = re.sub(
                    f'from agents\\.{old_name} import',
                    f'from agents.{new_name} import',
                    content
                )
                content = re.sub(
                    f'import agents\\.{old_name}',
                    f'import agents.{new_name}',
                    content
                )
                
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                updated_files.append(filepath)
                
        except Exception as e:
            print(f"❌ 更新文件失败 {filepath}: {e}")
    
    return updated_files


def main():
    print("="*60)
    print("Agent重构脚本")
    print("="*60)
    
    # 1. 备份
    print("\n步骤1: 备份现有文件")
    backup_dir = backup_files()
    print(f"备份完成: {backup_dir}")
    
    # 2. 分析
    print("\n步骤2: 分析实现差异")
    analyze_implementations()
    
    # 3. 询问用户选择
    print("\n步骤3: 选择方案")
    print("="*60)
    print("发现两个模块化实现:")
    print("1. sql_agent_v2.py - 完全重新实现")
    print("2. sql_agent_modular.py - 继承实现")
    print("\n建议方案:")
    print("A. 使用 sql_agent_v2.py 作为主要模块化版本")
    print("B. 保留两个版本，但重命名以明确区别")
    print("C. 手动决定每个文件")
    
    choice = input("\n请选择方案 (A/B/C): ").upper()
    
    if choice == 'A':
        print("\n执行方案A: 使用sql_agent_v2.py作为主要版本")
        
        # 重命名计划
        rename_plan = [
            ("sql_agent_v2.py", "sql_agent_modular.py", "SQLAgentV2", "SQLAgentModular"),
            ("sql_agent_modular.py", "sql_agent_inherited.py", "SQLAgentModular", "SQLAgentInherited"),
        ]
        
        for old_file, new_file, old_class, new_class in rename_plan:
            old_path = f"agents/{old_file}"
            new_path = f"agents/{new_file}"
            
            if old_file == "sql_agent_v2.py":
                # 删除现有的 sql_agent_modular.py
                if os.path.exists("agents/sql_agent_modular.py"):
                    os.remove("agents/sql_agent_modular.py")
                    print(f"✅ 删除旧的 sql_agent_modular.py")
                
                # 重命名 v2 为 modular
                os.rename(old_path, new_path)
                print(f"✅ 重命名: {old_file} -> {new_file}")
                
                # 更新类名
                with open(new_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                content = content.replace(old_class, new_class)
                with open(new_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                # 更新所有引用
                print(f"更新引用...")
                # 更新 sql_agent_v2 的引用
                updated = update_references("sql_agent_v2", "sql_agent_modular")
                print(f"  更新了 {len(updated)} 个文件")
                
                # 更新 SQLAgentV2 类名引用
                for filepath in updated:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        content = f.read()
                    content = content.replace("SQLAgentV2", "SQLAgentModular")
                    with open(filepath, 'w', encoding='utf-8') as f:
                        f.write(content)
        
        print("\n✅ 重构完成！")
        print("\n当前结构:")
        print("- sql_agent.py: 原始实现")
        print("- sql_agent_modular.py: 模块化实现（原sql_agent_v2.py）")
        
    elif choice == 'B':
        print("\n执行方案B: 保留两个版本但重命名")
        # 实现方案B
        pass
    else:
        print("\n取消操作")
        return
    
    print("\n下一步:")
    print("1. 运行测试确保一切正常")
    print("2. 提交代码变更")
    print("3. 更新文档")


if __name__ == "__main__":
    main()