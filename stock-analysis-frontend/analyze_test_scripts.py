#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
分析根目录下所有测试脚本的价值和状态
"""

import os
import sys
import time
import subprocess
from datetime import datetime
from typing import Dict, List, Tuple

# 测试脚本列表
TEST_SCRIPTS = [
    "baseline_functionality_test.py",
    "baseline_test.py", 
    "check_available_dates.py",
    "comprehensive_system_test.py",
    "comprehensive_test_with_date_intelligence.py",
    "comprehensive_verification.py",
    "debug_openapi_issue.py",
    "debug_rag_step_by_step.py",
    "diagnose_date_intelligence_issue.py",
    "diagnose_rag_issue.py",
    "diagnose_rag_issue_fixed.py",
    "enhanced_system_test.py",
    "quick_functionality_test.py",
    "quick_system_test.py",
    "quick_test.py",
    "simple_date_test.py",
    "test_advanced_financial_features.py",
    "test_date_intelligence.py",
    "test_date_intelligence_quick.py",
    "test_financial_agent.py"
]

def analyze_script_content(script_path: str) -> Dict:
    """分析脚本内容，判断其类型和价值"""
    try:
        with open(script_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 分析脚本特征
        features = {
            'lines': len(content.splitlines()),
            'has_main': '__main__' in content,
            'has_imports': 'import' in content,
            'is_diagnostic': any(word in script_path.lower() for word in ['diagnose', 'debug', 'check']),
            'is_comprehensive': 'comprehensive' in script_path.lower(),
            'is_quick': 'quick' in script_path.lower(),
            'is_baseline': 'baseline' in script_path.lower(),
            'test_agent': 'agent' in content.lower(),
            'test_api': 'api' in content.lower() or 'requests' in content,
            'test_database': any(db in content.lower() for db in ['mysql', 'milvus']),
            'has_docstring': '"""' in content[:500],
            'creation_time': os.path.getctime(script_path),
            'modification_time': os.path.getmtime(script_path)
        }
        
        # 判断脚本类型
        if features['is_diagnostic']:
            script_type = "诊断工具"
        elif features['is_comprehensive']:
            script_type = "综合测试"
        elif features['is_quick']:
            script_type = "快速测试"
        elif features['is_baseline']:
            script_type = "基线测试"
        else:
            script_type = "功能测试"
            
        return {
            'exists': True,
            'type': script_type,
            'features': features,
            'error': None
        }
        
    except Exception as e:
        return {
            'exists': False,
            'type': '未知',
            'features': {},
            'error': str(e)
        }

def run_script_test(script_path: str, timeout: int = 30) -> Dict:
    """运行脚本并获取结果"""
    start_time = time.time()
    
    try:
        # 构建命令
        cmd = f"cd .. && source venv/bin/activate && python {os.path.basename(script_path)}"
        
        # 运行脚本
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            timeout=timeout
        )
        
        elapsed_time = time.time() - start_time
        
        return {
            'success': result.returncode == 0,
            'elapsed_time': elapsed_time,
            'stdout_lines': len(result.stdout.splitlines()),
            'stderr_lines': len(result.stderr.splitlines()),
            'has_error': 'error' in result.stderr.lower() or 'exception' in result.stderr.lower(),
            'timeout': False
        }
        
    except subprocess.TimeoutExpired:
        return {
            'success': False,
            'elapsed_time': timeout,
            'stdout_lines': 0,
            'stderr_lines': 0,
            'has_error': False,
            'timeout': True
        }
    except Exception as e:
        return {
            'success': False,
            'elapsed_time': time.time() - start_time,
            'stdout_lines': 0,
            'stderr_lines': 0,
            'has_error': True,
            'timeout': False,
            'error': str(e)
        }

def categorize_script(script_name: str, analysis: Dict, test_result: Dict) -> str:
    """根据分析结果对脚本进行分类"""
    features = analysis.get('features', {})
    
    # 1. 诊断和调试脚本 - 通常是临时性的
    if features.get('is_diagnostic'):
        if test_result.get('success'):
            return "归档-诊断工具"
        else:
            return "删除-过时诊断"
    
    # 2. 综合测试脚本 - 通常很有价值
    if features.get('is_comprehensive'):
        if test_result.get('success'):
            return "保留-核心测试"
        else:
            return "归档-需要更新"
    
    # 3. 基线测试 - 重要的基础测试
    if features.get('is_baseline'):
        return "保留-基线测试"
    
    # 4. 快速测试脚本
    if features.get('is_quick'):
        if test_result.get('success'):
            return "保留-快速验证"
        else:
            return "归档-需要修复"
    
    # 5. 功能测试脚本
    if 'test_' in script_name:
        if test_result.get('success'):
            return "保留-功能测试"
        else:
            return "归档-需要更新"
    
    # 6. 其他脚本
    if features.get('lines', 0) < 50:
        return "删除-内容过少"
    
    return "归档-其他工具"

def main():
    print("=" * 80)
    print("根目录测试脚本分析报告")
    print("=" * 80)
    print(f"分析时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"脚本总数: {len(TEST_SCRIPTS)}")
    print()
    
    results = []
    categories = {
        "保留-核心测试": [],
        "保留-基线测试": [],
        "保留-功能测试": [],
        "保留-快速验证": [],
        "归档-诊断工具": [],
        "归档-需要更新": [],
        "归档-需要修复": [],
        "归档-其他工具": [],
        "删除-过时诊断": [],
        "删除-内容过少": []
    }
    
    # 分析每个脚本
    for i, script_name in enumerate(TEST_SCRIPTS, 1):
        script_path = os.path.join("..", script_name)
        print(f"\n[{i}/{len(TEST_SCRIPTS)}] 分析: {script_name}")
        print("-" * 60)
        
        # 分析脚本内容
        analysis = analyze_script_content(script_path)
        
        if not analysis['exists']:
            print(f"⚠️  文件不存在或无法读取")
            categories["删除-过时诊断"].append(script_name)
            continue
            
        print(f"类型: {analysis['type']}")
        print(f"行数: {analysis['features']['lines']}")
        
        # 运行测试（快速测试，30秒超时）
        print("运行测试...", end='', flush=True)
        test_result = run_script_test(script_path, timeout=30)
        
        if test_result['timeout']:
            print(" ⏱️  超时")
        elif test_result['success']:
            print(f" ✅ 成功 ({test_result['elapsed_time']:.2f}秒)")
        else:
            print(f" ❌ 失败")
            
        # 分类
        category = categorize_script(script_name, analysis, test_result)
        categories[category].append(script_name)
        print(f"建议: {category}")
        
        # 记录结果
        results.append({
            'script': script_name,
            'type': analysis['type'],
            'lines': analysis['features']['lines'],
            'test_success': test_result['success'],
            'category': category
        })
    
    # 生成总结报告
    print("\n" + "=" * 80)
    print("分类汇总")
    print("=" * 80)
    
    for category, scripts in categories.items():
        if scripts:
            print(f"\n{category} ({len(scripts)}个):")
            for script in scripts:
                print(f"  - {script}")
    
    # 统计信息
    print("\n" + "=" * 80)
    print("统计信息")
    print("=" * 80)
    
    total_scripts = len(TEST_SCRIPTS)
    keep_count = sum(len(scripts) for cat, scripts in categories.items() if cat.startswith("保留"))
    archive_count = sum(len(scripts) for cat, scripts in categories.items() if cat.startswith("归档"))
    delete_count = sum(len(scripts) for cat, scripts in categories.items() if cat.startswith("删除"))
    
    print(f"保留: {keep_count} ({keep_count/total_scripts*100:.1f}%)")
    print(f"归档: {archive_count} ({archive_count/total_scripts*100:.1f}%)")
    print(f"删除: {delete_count} ({delete_count/total_scripts*100:.1f}%)")
    
    # 生成建议的目录结构
    print("\n" + "=" * 80)
    print("建议的目录结构")
    print("=" * 80)
    print("""
    stock_analysis_system/
    ├── tests/                    # 保留的测试脚本
    │   ├── core/                # 核心测试
    │   ├── baseline/            # 基线测试
    │   ├── functional/          # 功能测试
    │   └── quick/               # 快速验证
    ├── scripts/
    │   └── archived/            # 归档的脚本
    │       ├── diagnostic/      # 诊断工具
    │       └── outdated/        # 需要更新的脚本
    └── (根目录保持清洁)
    """)

if __name__ == "__main__":
    main()