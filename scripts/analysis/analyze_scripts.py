#!/usr/bin/env python3
"""
脚本深度分析工具 - 用于判断脚本是一次性还是可重复使用
"""

import os
import re
import ast
from pathlib import Path
from typing import Dict, List, Tuple, Set
from datetime import datetime

class ScriptAnalyzer:
    def __init__(self):
        self.results = {
            "one_time_scripts": [],
            "reusable_tools": [],
            "utility_scripts": [],
            "analysis_needed": []
        }
        
        # 一次性脚本的特征
        self.one_time_indicators = [
            # 文件操作相关
            r"\.replace\(",                    # 字符串替换
            r"content\s*=\s*content\.replace", # 内容替换
            r"with\s+open\(.*,\s*['\"]w['\"]", # 写入文件
            r"\.write\(content\)",             # 写入内容
            r"shutil\.move\(",                 # 移动文件
            r"os\.rename\(",                   # 重命名文件
            
            # 修复/补丁相关
            r"fix_",                           # fix_开头的函数
            r"patch_",                         # patch_开头的函数
            r"#\s*(修复|fix|patch|临时)",      # 注释中的关键词
            r"backup.*=.*backup",              # 创建备份
            r"\.backup_",                      # 备份文件
            
            # 代码修改相关
            r"if.*not in content:",           # 检查内容是否存在
            r"content\.find\(",                # 查找内容
            r"re\.sub\(",                      # 正则替换
            r"import.*#.*fix",                 # 修复相关的导入
        ]
        
        # 可重复使用工具的特征
        self.reusable_indicators = [
            # 功能性操作
            r"def\s+main\(\s*\):",             # 主函数
            r"argparse\.ArgumentParser",       # 命令行参数
            r"if\s+__name__.*==.*__main__",   # 可执行脚本
            r"class\s+\w+:",                   # 类定义
            
            # 查询/分析操作
            r"SELECT.*FROM",                   # SQL查询
            r"collection\.query\(",            # 向量查询
            r"\.connect\(",                    # 数据库连接
            r"print\(.*统计|分析|结果",        # 输出分析结果
            
            # 工具性功能
            r"def\s+analyze",                  # 分析函数
            r"def\s+process",                  # 处理函数
            r"def\s+load",                     # 加载函数
            r"def\s+test",                     # 测试函数
            
            # 不修改源文件
            r"with\s+open\(.*,\s*['\"]r['\"]", # 只读文件
            r"\.read\(\)",                     # 读取操作
            r"return\s+",                      # 返回结果
        ]
        
        # 破坏性操作（强烈暗示一次性）
        self.destructive_indicators = [
            r"os\.remove\(",                   # 删除文件
            r"shutil\.rmtree\(",              # 删除目录
            r"DROP\s+TABLE",                   # 删除表
            r"DELETE\s+FROM",                  # 删除数据
            r"TRUNCATE",                       # 清空表
        ]

    def analyze_file(self, filepath: Path) -> Dict:
        """深度分析单个Python文件"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
        except:
            return {"error": "无法读取文件"}
        
        analysis = {
            "filename": filepath.name,
            "path": str(filepath),
            "one_time_score": 0,
            "reusable_score": 0,
            "features": [],
            "imports": [],
            "functions": [],
            "classes": [],
            "main_block": False,
            "modifies_files": False,
            "creates_backup": False,
            "has_argparse": False,
            "is_test": False,
            "is_fix": False,
            "description": ""
        }
        
        # 分析文件名
        filename_lower = filepath.name.lower()
        if any(keyword in filename_lower for keyword in ['fix', 'patch', 'temp', 'quick']):
            analysis["one_time_score"] += 3
            analysis["is_fix"] = True
            analysis["features"].append("文件名暗示临时修复")
        
        if any(keyword in filename_lower for keyword in ['test', 'check', 'verify']):
            analysis["is_test"] = True
            analysis["features"].append("测试相关脚本")
        
        # 分析导入
        imports = re.findall(r'^(?:from|import)\s+([^\s]+)', content, re.MULTILINE)
        analysis["imports"] = list(set(imports))
        
        # 使用AST分析代码结构
        try:
            tree = ast.parse(content)
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    analysis["functions"].append(node.name)
                elif isinstance(node, ast.ClassDef):
                    analysis["classes"].append(node.name)
                    analysis["reusable_score"] += 2
        except:
            pass
        
        # 检查主执行块
        if re.search(r'if\s+__name__.*==.*__main__', content):
            analysis["main_block"] = True
            analysis["reusable_score"] += 1
        
        # 检查argparse
        if 'argparse' in content:
            analysis["has_argparse"] = True
            analysis["reusable_score"] += 3
            analysis["features"].append("支持命令行参数")
        
        # 检查一次性特征
        for pattern in self.one_time_indicators:
            matches = len(re.findall(pattern, content, re.IGNORECASE))
            if matches > 0:
                analysis["one_time_score"] += matches
                
        # 检查可重复使用特征
        for pattern in self.reusable_indicators:
            matches = len(re.findall(pattern, content, re.IGNORECASE))
            if matches > 0:
                analysis["reusable_score"] += matches
        
        # 检查破坏性操作
        for pattern in self.destructive_indicators:
            if re.search(pattern, content, re.IGNORECASE):
                analysis["one_time_score"] += 5
                analysis["features"].append("包含破坏性操作")
        
        # 特定检查
        if re.search(r"with\s+open\(.*['\"]w['\"]", content):
            analysis["modifies_files"] = True
            analysis["features"].append("修改文件内容")
            
        if re.search(r"backup", content, re.IGNORECASE):
            analysis["creates_backup"] = True
            analysis["features"].append("创建备份文件")
        
        # 提取描述（从注释或docstring）
        desc_match = re.search(r'"""(.*?)"""', content, re.DOTALL)
        if desc_match:
            analysis["description"] = desc_match.group(1).strip().split('\n')[0]
        else:
            # 尝试从文件开头的注释获取
            comment_match = re.search(r'^#\s*(.+)$', content, re.MULTILINE)
            if comment_match:
                analysis["description"] = comment_match.group(1).strip()
        
        return analysis

    def categorize_script(self, analysis: Dict) -> str:
        """根据分析结果对脚本进行分类"""
        one_time = analysis["one_time_score"]
        reusable = analysis["reusable_score"]
        
        # 决策逻辑
        if analysis["is_fix"] and analysis["modifies_files"]:
            return "one_time"
        
        if one_time > reusable * 2:
            return "one_time"
        
        if reusable > one_time * 2:
            return "reusable"
        
        if analysis["has_argparse"] or len(analysis["classes"]) > 0:
            return "reusable"
        
        if analysis["modifies_files"] and not analysis["creates_backup"]:
            return "one_time"
        
        # 默认需要进一步分析
        return "needs_analysis"

    def analyze_directory(self, directory: str = "."):
        """分析目录中的所有Python脚本"""
        test_patterns = [
            r"^test_", r"^check_", r"^verify_", r"^debug_",
            r"^fix_", r"^patch_", r"^quick_", r"^temp_",
            r"^analyze_", r"^diagnose_"
        ]
        
        root_path = Path(directory)
        py_files = []
        
        # 收集根目录的Python文件
        for file in root_path.glob("*.py"):
            if any(re.match(pattern, file.name) for pattern in test_patterns):
                py_files.append(file)
        
        # 收集tests目录的文件
        tests_dir = root_path / "tests"
        if tests_dir.exists():
            for file in tests_dir.glob("*.py"):
                py_files.append(file)
        
        print(f"🔍 分析 {len(py_files)} 个脚本文件...\n")
        
        for filepath in sorted(py_files):
            if filepath.name == "__init__.py":
                continue
                
            analysis = self.analyze_file(filepath)
            category = self.categorize_script(analysis)
            
            # 生成报告项
            report_item = {
                "file": filepath.name,
                "path": str(filepath.relative_to(root_path)),
                "description": analysis["description"],
                "one_time_score": analysis["one_time_score"],
                "reusable_score": analysis["reusable_score"],
                "features": analysis["features"],
                "category": category
            }
            
            if category == "one_time":
                self.results["one_time_scripts"].append(report_item)
            elif category == "reusable":
                self.results["reusable_tools"].append(report_item)
            else:
                self.results["analysis_needed"].append(report_item)

    def generate_report(self):
        """生成详细的分析报告"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = f"script_analysis_report_{timestamp}.md"
        
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write("# 脚本类型分析报告\n\n")
            f.write(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            # 统计
            f.write("## 📊 统计摘要\n\n")
            f.write(f"- 一次性脚本: {len(self.results['one_time_scripts'])} 个\n")
            f.write(f"- 可重复使用工具: {len(self.results['reusable_tools'])} 个\n")
            f.write(f"- 需要人工判断: {len(self.results['analysis_needed'])} 个\n\n")
            
            # 可重复使用的工具
            f.write("## ✅ 可重复使用的工具\n\n")
            f.write("这些脚本可以多次运行，应该保留并整理：\n\n")
            for item in sorted(self.results['reusable_tools'], key=lambda x: x['reusable_score'], reverse=True):
                f.write(f"### 📌 {item['file']}\n")
                f.write(f"- **路径**: `{item['path']}`\n")
                f.write(f"- **描述**: {item['description'] or '无描述'}\n")
                f.write(f"- **可重用评分**: {item['reusable_score']}\n")
                f.write(f"- **特征**: {', '.join(item['features']) if item['features'] else '无'}\n")
                f.write(f"- **建议**: 移动到 `scripts/tools/` 目录\n\n")
            
            # 一次性脚本
            f.write("## ❌ 一次性脚本\n\n")
            f.write("这些脚本是临时修复或补丁，应该归档：\n\n")
            for item in sorted(self.results['one_time_scripts'], key=lambda x: x['one_time_score'], reverse=True):
                f.write(f"### 🔧 {item['file']}\n")
                f.write(f"- **路径**: `{item['path']}`\n")
                f.write(f"- **描述**: {item['description'] or '无描述'}\n")
                f.write(f"- **一次性评分**: {item['one_time_score']}\n")
                f.write(f"- **特征**: {', '.join(item['features']) if item['features'] else '无'}\n")
                f.write(f"- **建议**: 移动到 `archive/fixes/` 目录\n\n")
            
            # 需要人工判断
            f.write("## ❓ 需要人工判断\n\n")
            f.write("这些脚本特征不明确，需要人工确认：\n\n")
            for item in self.results['analysis_needed']:
                f.write(f"### 🤔 {item['file']}\n")
                f.write(f"- **路径**: `{item['path']}`\n")
                f.write(f"- **描述**: {item['description'] or '无描述'}\n")
                f.write(f"- **一次性评分**: {item['one_time_score']}\n")
                f.write(f"- **可重用评分**: {item['reusable_score']}\n")
                f.write(f"- **特征**: {', '.join(item['features']) if item['features'] else '无'}\n\n")
            
            # 建议的目录结构
            f.write("## 🏗️ 建议的脚本组织结构\n\n")
            f.write("```\n")
            f.write("scripts/\n")
            f.write("├── tools/              # 可重复使用的工具\n")
            f.write("│   ├── load_milvus_collection.py\n")
            f.write("│   ├── analyze_announcement_titles.py\n")
            f.write("│   └── tushare_db_analyzer.py\n")
            f.write("├── maintenance/        # 维护脚本\n")
            f.write("│   ├── batch_process_manager.py\n")
            f.write("│   └── milvus_dedup_script_v2.py\n")
            f.write("└── processing/         # 处理脚本\n")
            f.write("    ├── smart_processor_v5_1.py\n")
            f.write("    └── rag_query_interface.py\n")
            f.write("\n")
            f.write("archive/\n")
            f.write("├── fixes/              # 一次性修复\n")
            f.write("│   ├── fix_*.py\n")
            f.write("│   └── patch_*.py\n")
            f.write("└── old_versions/       # 旧版本\n")
            f.write("    └── smart_processor_v1-v5.py\n")
            f.write("```\n")
        
        print(f"✅ 分析报告已生成: {report_file}")
        return report_file

def main():
    analyzer = ScriptAnalyzer()
    analyzer.analyze_directory()
    analyzer.generate_report()
    
    # 输出简要总结
    print("\n📊 分析结果总结：")
    print(f"- 🔧 一次性脚本: {len(analyzer.results['one_time_scripts'])} 个")
    print(f"- ✅ 可重复工具: {len(analyzer.results['reusable_tools'])} 个")
    print(f"- ❓ 需要判断: {len(analyzer.results['analysis_needed'])} 个")

if __name__ == "__main__":
    main()
