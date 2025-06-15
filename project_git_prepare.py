#!/usr/bin/env python3
"""
股票分析系统 - Git版本管理准备脚本
用于分析项目结构、清理文件、生成.gitignore等
"""

import os
import re
import json
import shutil
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Set, Tuple
import hashlib

class ProjectGitPreparer:
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root).absolute()
        self.analysis_results = {
            "core_files": [],
            "test_files": [],
            "temp_files": [],
            "data_files": [],
            "config_files": [],
            "documentation": [],
            "to_archive": [],
            "to_delete": [],
            "to_gitignore": [],
            "duplicate_files": [],
            "large_files": []
        }
        
        # 核心模块模式（基于完整分析更新）
        self.core_patterns = {
            "modules": [
                r"^(config|database|rag|agents|models|api|utils)/.*\.py$",
                r"^requirements\.txt$",
                r"^setup\.py$",
                r"^README\.md$"
            ],
            "important_scripts": [
                # 最新版本的核心脚本
                r"^smart_processor_v5_1\.py$",  # 最新的智能处理器（三阶段下载策略）
                r"^document_processor\.py$",     # 文档处理核心（支持特殊PDF下载）
                r"^batch_process_manager\.py$",  # 批量处理管理
                r"^milvus_dedup_script_v2\.py$", # 去重维护脚本
                r"^rag_query_interface\.py$",    # RAG查询界面
                # 项目管理工具
                r"^project_git_prepare\.py$",    # Git准备工具（保留在根目录）
            ]
        }
        
        # 测试文件模式
        self.test_patterns = [
            r"^test_.*\.py$",
            r"^.*_test\.py$",
            r"^quick_test.*\.py$",
            r"^debug_.*\.py$",
            r"^check_.*\.py$",
            r"^verify_.*\.py$",
            r"^fix_.*\.py$",
            r"^patch_.*\.py$",
            r"^diagnose_.*\.py$",
            r"^analyze_.*\.py$"
        ]
        
        # 临时/开发文件模式
        self.temp_patterns = [
            r"^temp_.*",
            r"^tmp_.*",
            r"^\..*_cache",
            r"__pycache__",
            r"\.pyc$",
            r"\.pyo$",
            r"\.pyd$",
            r"\.so$",
            r"\.egg-info",
            r"\.pytest_cache",
            r"\.coverage"
        ]
        
        # 数据文件模式
        self.data_patterns = [
            r"^data/",
            r"\.db$",
            r"\.sqlite$",
            r"\.csv$",
            r"\.xlsx?$",
            r"\.pdf$",
            r"\.json$",
            r"\.pkl$",
            r"\.npy$",
            r"\.npz$"
        ]
        
        # 配置文件模式
        self.config_patterns = [
            r"^\.env.*",
            r"^config\..*",
            r".*\.ini$",
            r".*\.yaml$",
            r".*\.yml$",
            r".*\.toml$"
        ]
        
        # 文档模式
        self.doc_patterns = [
            r".*\.md$",
            r".*\.rst$",
            r"^docs/",
            r"^LICENSE.*",
            r"^CHANGELOG.*"
        ]
        
        # 需要归档的一次性脚本（基于分析结果）
        self.one_time_scripts = [
            # SQL Agent修复系列
            r"^fix_sql_agent_indent\.py$",
            r"^fix_sql_agent_indent_error\.py$",
            r"^quick_patch_sql_agent\.py$",
            r"^safe_patch_sql_agent\.py$",
            r"^safe_restore_sql_agent\.py$",
            r"^patch_sql_agent_opt\.py$",
            # API响应格式修复
            r"^fix_api_response\.py$",
            r"^final_fix_return_format\.py$",
            r"^auto_fix_hybrid\.py$",
            r"^manual_fix_guide\.py$",
            r"^fix_remaining_issue\.py$",
            # 枚举和类型修复
            r"^fix_hybrid_agent_enum\.py$",
            r"^fix_query_type\.py$",
            r"^temporary_fix\.py$",
            # 超时和配置修复
            r"^fix_timeout_simple\.py$",
            r"^fix_timeout_issue\.py$",
            r"^patch_api_timeout_opt\.py$",
            r"^patch_config\.py$",
            # 导入修复
            r"^fix_import\.py$",
            r"^fix_imports\.py$",
            # 其他修复
            r"^final_fixes\.py$",
            r"^quick_fixes\.py$",
            r"^test_sql_agent_fix\.py$"
        ]
        
        # 需要归档的旧版本模式（基于项目历史）
        self.archive_patterns = [
            # 处理器历史版本
            r"^smart_processor\.py$",        # v1版本
            r"^smart_processor_v2\.py$",     # v2版本
            r"^smart_processor_v3\.py$",     # v3版本（被v5_1取代）
            r"^smart_processor_v3_bak\.py$", # v3备份
            r"^smart_processor_v4\.py$",     # v4版本
            r"^smart_processor_v5\.py$",     # v5版本（被v5_1取代）
            # 其他旧版本
            r"^milvus_dedup_script\.py$",    # v1版本（被v2取代）
            r"^dedup_tool\.py$",             # 旧的去重工具
            r"^continue_processing\.py$",    # 旧的续处理脚本
            r"^create_essential_tables\.py$", # 临时表创建脚本
            r"^sample_queries\.py$",         # 示例查询脚本
            r"^check_database_tables\.py$",  # 被fixed版本取代
            # 通用旧版本模式
            r".*_old\.py$",
            r".*_backup\.py$",
            r".*\(copy\).*",
            r".*_deprecated.*"
        ]
        
        # 可重复使用的工具脚本（基于分析结果）
        self.reusable_tools = [
            # 核心工具
            r"^test_api_correct\.py$",
            r"^tushare-db-analyzer\.py$", 
            r"^analyze_announcement_titles\.py$",
            r"^verify_system\.py$",
            r"^load_milvus_collection\.py$",
            r"^test_agents\.py$",
            r"^final_api_test\.py$",
            # 调试诊断工具
            r"^debug_batch_processor\.py$",
            r"^diagnose_agent_issue\.py$",
            r"^check_sql_agent\.py$",
            r"^check_api_enums\.py$",
            r"^check_database_tables_fixed\.py$",
            r"^test_cninfo_pdf\.py$",
            r"^test_pdf_case\.py$",
            # 测试工具
            r"^test_components\.py$",
            r"^test_timeout_fixed\.py$",
            r"^minimal_api_test\.py$",
            r"^optimized_test\.py$",
            # 其他工具
            r"^analyze_scripts\.py$",
            r"^optimize_api_system\.py$",
            r"^verify_api\.py$",
            r"^test_gpu\.py$",
            r"^install_dependencies\.py$"
        ]
        
        # 大文件阈值 (10MB)
        self.large_file_threshold = 10 * 1024 * 1024

    def analyze_project(self):
        """分析整个项目结构"""
        print("🔍 开始分析项目结构...")
        
        all_files = []
        for root, dirs, files in os.walk(self.project_root):
            # 跳过已知的临时目录
            dirs[:] = [d for d in dirs if not any(
                re.match(pattern, d) for pattern in self.temp_patterns
            )]
            
            for file in files:
                file_path = Path(root) / file
                rel_path = file_path.relative_to(self.project_root)
                all_files.append(rel_path)
        
        # 分类文件
        for file_path in all_files:
            self._categorize_file(file_path)
        
        # 检测重复文件
        self._find_duplicates()
        
        # 生成报告
        self._generate_report()

    def _categorize_file(self, file_path: Path):
        """对文件进行分类"""
        str_path = str(file_path).replace('\\', '/')
        full_path = self.project_root / file_path
        
        # 检查文件大小
        try:
            file_size = full_path.stat().st_size
            if file_size > self.large_file_threshold:
                self.analysis_results["large_files"].append({
                    "path": str_path,
                    "size_mb": round(file_size / (1024 * 1024), 2)
                })
        except:
            pass
        
        # 优先级分类
        # 1. 检查是否是临时文件
        if any(re.match(pattern, str_path) for pattern in self.temp_patterns):
            self.analysis_results["to_delete"].append(str_path)
            return
        
        # 2. 检查是否是核心文件
        is_core = False
        for pattern in self.core_patterns["modules"] + self.core_patterns["important_scripts"]:
            if re.match(pattern, str_path):
                self.analysis_results["core_files"].append(str_path)
                is_core = True
                break
        
        if is_core:
            return
        
        # 3. 检查是否是可重复使用的工具
        if any(re.match(pattern, str_path) for pattern in self.reusable_tools):
            self.analysis_results["test_files"].append(str_path)  # 标记为可保留的测试/工具
            return
        
        # 4. 检查是否是一次性脚本
        if any(re.match(pattern, str_path) for pattern in self.one_time_scripts):
            self.analysis_results["to_archive"].append(str_path)
            return
        
        # 5. 检查是否需要归档（旧版本）
        if any(re.match(pattern, str_path) for pattern in self.archive_patterns):
            self.analysis_results["to_archive"].append(str_path)
            return
        
        # 6. 检查是否是测试文件
        if any(re.match(pattern, str_path) for pattern in self.test_patterns):
            self.analysis_results["test_files"].append(str_path)
            return
        
        # 7. 检查是否是数据文件
        if any(re.match(pattern, str_path) for pattern in self.data_patterns):
            self.analysis_results["data_files"].append(str_path)
            self.analysis_results["to_gitignore"].append(str_path)
            return
        
        # 8. 检查是否是配置文件
        if any(re.match(pattern, str_path) for pattern in self.config_patterns):
            self.analysis_results["config_files"].append(str_path)
            if ".env" in str_path and not str_path.endswith('.example'):
                self.analysis_results["to_gitignore"].append(str_path)
            return
        
        # 9. 检查是否是文档
        if any(re.match(pattern, str_path) for pattern in self.doc_patterns):
            self.analysis_results["documentation"].append(str_path)
            # 项目状态文档应该保留
            if "project_status" in str_path:
                self.analysis_results["core_files"].append(str_path)
            return
        
        # 10. 其他Python文件可能需要检查
        if str_path.endswith('.py'):
            # 检查是否是独立的测试/调试脚本
            content = self._check_file_content(full_path)
            if content and self._is_standalone_test_script(content):
                self.analysis_results["test_files"].append(str_path)
            else:
                # 可能是遗漏的重要文件，需要人工确认
                print(f"⚠️  需要人工确认: {str_path}")

    def _check_file_content(self, file_path: Path) -> str:
        """读取文件内容"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except:
            return ""

    def _is_standalone_test_script(self, content: str) -> bool:
        """判断是否是独立的测试脚本"""
        test_indicators = [
            r"if __name__ == ['\"]__main__['\"]:",
            r"def test_",
            r"print\(.*(测试|test|debug)",
            r"# test",
            r"# debug",
            r"# 测试"
        ]
        
        for indicator in test_indicators:
            if re.search(indicator, content, re.IGNORECASE):
                return True
        return False

    def _find_duplicates(self):
        """查找重复文件"""
        file_hashes = {}
        
        for category in ["core_files", "test_files", "to_archive"]:
            for file_path in self.analysis_results[category]:
                full_path = self.project_root / file_path
                if full_path.exists() and full_path.is_file():
                    file_hash = self._get_file_hash(full_path)
                    if file_hash:
                        if file_hash in file_hashes:
                            self.analysis_results["duplicate_files"].append({
                                "file1": file_hashes[file_hash],
                                "file2": file_path,
                                "hash": file_hash
                            })
                        else:
                            file_hashes[file_hash] = file_path

    def _get_file_hash(self, file_path: Path) -> str:
        """计算文件的MD5哈希"""
        try:
            with open(file_path, 'rb') as f:
                return hashlib.md5(f.read()).hexdigest()
        except:
            return ""

    def _generate_report(self):
        """生成分析报告"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = f"git_prepare_report_{timestamp}.md"
        
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write("# 股票分析系统 - Git版本管理准备报告\n\n")
            f.write(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            # 统计摘要
            f.write("## 📊 文件统计摘要\n\n")
            f.write(f"- 核心文件: {len(self.analysis_results['core_files'])} 个\n")
            f.write(f"- 测试文件: {len(self.analysis_results['test_files'])} 个\n")
            f.write(f"- 待归档文件: {len(self.analysis_results['to_archive'])} 个\n")
            f.write(f"- 待删除文件: {len(self.analysis_results['to_delete'])} 个\n")
            f.write(f"- 数据文件: {len(self.analysis_results['data_files'])} 个\n")
            f.write(f"- 配置文件: {len(self.analysis_results['config_files'])} 个\n")
            f.write(f"- 文档文件: {len(self.analysis_results['documentation'])} 个\n")
            f.write(f"- 重复文件: {len(self.analysis_results['duplicate_files'])} 组\n")
            f.write(f"- 大文件(>10MB): {len(self.analysis_results['large_files'])} 个\n\n")
            
            # 核心文件列表（基于项目状态文档）
            f.write("## 🔧 核心文件（必须保留）\n\n")
            f.write("### 核心模块\n")
            core_modules = [f for f in self.analysis_results['core_files'] if '/' in f and not f.endswith('.md')]
            for file in sorted(core_modules):
                f.write(f"- ✅ {file}\n")
            
            f.write("\n### 重要脚本（最新版本）\n")
            core_scripts = [f for f in self.analysis_results['core_files'] if '/' not in f and f.endswith('.py')]
            for file in sorted(core_scripts):
                desc = ""
                if "v5_1" in file:
                    desc = " (三阶段PDF下载策略)"
                elif "document_processor" in file:
                    desc = " (支持巨潮特殊PDF)"
                elif "milvus_dedup_script_v2" in file:
                    desc = " (向量去重维护)"
                elif "batch_process_manager" in file:
                    desc = " (批量处理管理)"
                elif "rag_query_interface" in file:
                    desc = " (RAG查询界面)"
                elif "test_api_correct" in file:
                    desc = " (API测试)"
                f.write(f"- ✅ {file}{desc}\n")
            
            f.write("\n### 项目文档\n")
            docs = [f for f in self.analysis_results['core_files'] if f.endswith('.md')]
            for file in sorted(docs):
                f.write(f"- ✅ {file}\n")
            
            # 可重复使用的工具（基于分析结果分类）
            f.write("\n## 🛠️ 可重复使用的工具（建议保留）\n\n")
            f.write("建议移动到 `scripts/` 相应目录:\n\n")
            
            # 分类显示
            tool_categories = {
                "分析工具": ["tushare-db-analyzer", "analyze_announcement", "analyze_scripts"],
                "测试工具": ["test_api_correct", "test_agents", "test_components", "final_api_test"],
                "调试工具": ["debug_", "diagnose_", "check_"],
                "系统工具": ["verify_system", "load_milvus", "install_dependencies"],
                "其他工具": []
            }
            
            reusable = [f for f in self.analysis_results['test_files'] 
                       if any(re.match(p, f) for p in self.reusable_tools)]
            
            categorized = set()
            for category, keywords in tool_categories.items():
                f.write(f"\n### {category}\n")
                for file in sorted(reusable):
                    if any(keyword in file.lower() for keyword in keywords):
                        f.write(f"- ✅ {file} → `scripts/{category.replace('工具', '').lower()}/`\n")
                        categorized.add(file)
            
            # 未分类的
            uncategorized = set(reusable) - categorized
            if uncategorized:
                f.write("\n### 其他工具\n")
                for file in sorted(uncategorized):
                    f.write(f"- ✅ {file} → `scripts/tools/`\n")
            
            # 待归档文件（基于分析结果）
            f.write("\n## 📦 待归档文件（一次性脚本和旧版本）\n\n")
            f.write("建议移动到 `archive/` 相应目录:\n")
            
            # 分类归档文件
            archive_categories = {
                "SQL Agent修复": ["fix_sql_agent", "patch_sql_agent", "safe_patch_sql", "safe_restore_sql"],
                "API响应修复": ["fix_api_response", "final_fix_return", "auto_fix_hybrid", "manual_fix_guide"],
                "超时修复": ["fix_timeout", "patch_api_timeout", "patch_config"],
                "导入修复": ["fix_import"],
                "枚举修复": ["fix_hybrid_agent_enum", "fix_query_type"],
                "处理器旧版本": ["smart_processor", "smart_processor_v"],
                "其他旧版本": []
            }
            
            categorized_archives = set()
            for category, keywords in archive_categories.items():
                category_files = []
                for file in sorted(self.analysis_results['to_archive']):
                    if any(keyword in file.lower() for keyword in keywords):
                        category_files.append(file)
                        categorized_archives.add(file)
                
                if category_files:
                    f.write(f"\n### {category}\n")
                    for file in category_files:
                        f.write(f"- 📁 {file} → `archive/fixes/{category.replace(' ', '_').lower()}/`\n")
            
            # 未分类的归档文件
            uncategorized_archives = set(self.analysis_results['to_archive']) - categorized_archives
            if uncategorized_archives:
                f.write("\n### 其他归档文件\n")
                for file in sorted(uncategorized_archives):
                    f.write(f"- 📁 {file} → `archive/other/`\n")
            
            # 待删除文件
            f.write("\n## 🗑️ 待删除文件（临时文件）\n\n")
            for file in sorted(self.analysis_results['to_delete']):
                f.write(f"- ❌ {file}\n")
            
            # 大文件警告
            if self.analysis_results['large_files']:
                f.write("\n## ⚠️ 大文件警告\n\n")
                for file_info in sorted(self.analysis_results['large_files'], 
                                       key=lambda x: x['size_mb'], reverse=True):
                    f.write(f"- {file_info['path']} ({file_info['size_mb']} MB)\n")
            
            # 重复文件
            if self.analysis_results['duplicate_files']:
                f.write("\n## 🔄 重复文件\n\n")
                for dup in self.analysis_results['duplicate_files']:
                    f.write(f"- {dup['file1']} = {dup['file2']}\n")
            
            # .gitignore 建议
            f.write("\n## 📝 .gitignore 建议\n\n")
            f.write("```gitignore\n")
            gitignore_patterns = self._generate_gitignore_content()
            f.write(gitignore_patterns)
            f.write("```\n")
            
            # 项目结构建议（基于最新项目状态）
            f.write("\n## 🏗️ 建议的项目结构\n\n")
            f.write("```\n")
            f.write(self._generate_suggested_structure())
            f.write("```\n")
            
            # 添加数据统计
            f.write("\n## 📊 项目数据统计\n\n")
            f.write("基于项目状态文档（2025-06-14）:\n")
            f.write("- MySQL记录数: 2800万+条\n")
            f.write("- Milvus向量数: 95,662+个\n")
            f.write("- 已处理公司: 500+家\n")
            f.write("- PDF文档: 数千份\n")
            f.write("- 代码规模: 约20,000行\n")
            
            # 执行步骤
            f.write("\n## 🚀 建议的执行步骤\n\n")
            f.write("1. **备份当前项目**\n")
            f.write("   ```bash\n")
            f.write("   cp -r . ../stock_analysis_backup_$(date +%Y%m%d)\n")
            f.write("   ```\n\n")
            
            f.write("2. **创建必要的目录**\n")
            f.write("   ```bash\n")
            f.write("   mkdir -p tests archive docs/examples\n")
            f.write("   ```\n\n")
            
            f.write("3. **移动测试文件**\n")
            f.write("   ```bash\n")
            f.write("   mv test_*.py tests/\n")
            f.write("   mv *_test.py tests/\n")
            f.write("   ```\n\n")
            
            f.write("4. **归档旧版本**\n")
            f.write("   ```bash\n")
            f.write("   mv *_v[0-4].py archive/  # 保留v5_1\n")
            f.write("   mv *_old.py archive/\n")
            f.write("   mv *_backup.py archive/\n")
            f.write("   ```\n\n")
            
            f.write("5. **清理临时文件**\n")
            f.write("   ```bash\n")
            f.write("   find . -type d -name __pycache__ -exec rm -rf {} +\n")
            f.write("   find . -name '*.pyc' -delete\n")
            f.write("   find . -name '*.pyo' -delete\n")
            f.write("   rm -rf .pytest_cache .coverage\n")
            f.write("   ```\n\n")
            
            f.write("6. **创建.gitignore**\n")
            f.write("   ```bash\n")
            f.write("   python project_git_prepare.py --create-gitignore\n")
            f.write("   ```\n\n")
            
            f.write("7. **初始化Git仓库**\n")
            f.write("   ```bash\n")
            f.write("   git init\n")
            f.write("   git add .\n")
            f.write("   git commit -m 'Initial commit: Stock Analysis System v1.2'\n")
            f.write("   ```\n\n")
            
            f.write("8. **创建GitHub仓库并推送**\n")
            f.write("   ```bash\n")
            f.write("   git remote add origin https://github.com/YOUR_USERNAME/stock-analysis-system.git\n")
            f.write("   git branch -M main\n")
            f.write("   git push -u origin main\n")
            f.write("   ```\n")
        
        print(f"✅ 报告已生成: {report_file}")
        return report_file

    def _generate_gitignore_content(self) -> str:
        """生成.gitignore内容"""
        gitignore_content = """# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg
MANIFEST

# Virtual Environment
venv/
ENV/
env/
stock_analysis_env/

# IDE
.vscode/
.idea/
*.swp
*.swo
*~
.project
.pydevproject

# Testing
.pytest_cache/
.coverage
.tox/
htmlcov/
.hypothesis/

# Logs
logs/
*.log

# Environment variables
.env
.env.*
!.env.example

# Data files
data/
*.db
*.sqlite
*.csv
*.xlsx
*.xls
*.pdf
*.pkl
*.npy
*.npz

# Jupyter Notebook
.ipynb_checkpoints

# macOS
.DS_Store

# Windows
Thumbs.db
ehthumbs.db

# Project specific
archive/
temp/
tmp/
downloads/
output/
backup/

# Large model files
*.bin
*.pth
*.h5
*.safetensors

# Secrets
secrets/
credentials/
*.key
*.pem
"""
        return gitignore_content

    def _generate_suggested_structure(self) -> str:
        """生成建议的项目结构"""
        return """stock_analysis_system/
├── config/                 # 配置模块
│   ├── __init__.py
│   └── settings.py
├── database/              # 数据库连接
│   ├── __init__.py
│   ├── mysql_connector.py
│   └── milvus_connector.py
├── rag/                   # RAG系统
│   ├── __init__.py
│   ├── document_processor.py    # 三阶段PDF下载
│   └── vector_store.py
├── agents/                # 智能代理
│   ├── __init__.py
│   ├── sql_agent.py             # SQL查询
│   ├── rag_agent.py             # RAG查询
│   └── hybrid_agent.py          # 混合查询
├── models/                # 模型配置
│   ├── __init__.py
│   ├── llm_models.py            # DeepSeek配置
│   ├── embedding_model.py       # BGE-M3模型
│   └── bge-m3/                  # 模型文件
├── api/                   # API服务
│   ├── __init__.py
│   └── main.py                  # FastAPI主程序
├── utils/                 # 工具函数
│   ├── __init__.py
│   ├── helpers.py
│   ├── logger.py
│   ├── performance_tracker.py
│   └── auto_performance_logger.py
├── scripts/               # 独立脚本
│   ├── smart_processor_v5_1.py  # 最新处理器
│   ├── batch_process_manager.py # 批量管理
│   ├── milvus_dedup_script_v2.py # 去重工具
│   └── rag_query_interface.py  # 查询界面
├── tests/                 # 测试文件
│   ├── test_api_correct.py      # API测试
│   ├── test_databases.py        # 数据库测试
│   ├── test_embedding_model.py  # 模型测试
│   ├── test_cninfo_pdf.py       # PDF测试
│   └── test_milvus_connection.py
├── archive/               # 归档旧版本
│   ├── smart_processor_v1-v3/   # 历史版本
│   ├── old_tests/               # 旧测试文件
│   └── deprecated/              # 废弃代码
├── docs/                  # 文档
│   ├── README.md
│   ├── API.md                   # API文档
│   ├── deployment.md            # 部署指南
│   ├── examples/                # 使用示例
│   └── project_status/          # 项目状态历史
├── data/                  # 数据目录（不提交）
│   ├── pdfs/                    # PDF缓存
│   ├── logs/                    # 运行日志
│   └── milvus/                  # 向量数据
├── requirements.txt       # 依赖清单
├── setup.py              # 安装配置
├── .gitignore            # Git忽略
├── .env.example          # 环境变量示例
├── LICENSE               # MIT许可证
└── README.md             # 项目说明"""

    def create_gitignore(self):
        """创建.gitignore文件"""
        gitignore_path = self.project_root / ".gitignore"
        with open(gitignore_path, 'w', encoding='utf-8') as f:
            f.write(self._generate_gitignore_content())
        print(f"✅ .gitignore 文件已创建: {gitignore_path}")

    def create_env_example(self):
        """创建.env.example文件"""
        env_example_content = """# MySQL数据库配置
MYSQL_HOST=10.0.0.77
MYSQL_PORT=3306
MYSQL_DATABASE=Tushare
MYSQL_USER=your_username
MYSQL_PASSWORD=your_password

# Milvus向量数据库配置
MILVUS_HOST=localhost
MILVUS_PORT=19530
MILVUS_COLLECTION_NAME=stock_announcements

# LLM配置 - DeepSeek
DEEPSEEK_API_KEY=your_api_key_here
DEEPSEEK_BASE_URL=https://api.deepseek.com/v1

# 或者使用通义千问
DASHSCOPE_API_KEY=your_api_key_here

# 文档存储路径
PDF_STORAGE_PATH=./data/pdfs
VECTOR_DB_PATH=./data/milvus

# 系统配置
LOG_LEVEL=INFO
MAX_WORKERS=4
USE_GPU=false
"""
        env_example_path = self.project_root / ".env.example"
        with open(env_example_path, 'w', encoding='utf-8') as f:
            f.write(env_example_content)
        print(f"✅ .env.example 文件已创建: {env_example_path}")

    def create_readme(self):
        """创建README.md文件"""
        readme_content = """# 股票分析系统 (Stock Analysis System)

基于LangChain的智能股票分析系统，集成SQL查询、RAG检索和混合查询功能。

## 🚀 功能特性

### 核心功能（100%完成）
- **SQL查询系统**: 实时股价、历史数据、排行统计、数据对比
- **RAG查询系统**: 财务报告分析、公告内容检索（95,662+文档已索引）
- **混合查询系统**: 智能路由，SQL+RAG自动整合
- **API服务**: RESTful接口，完整的Swagger文档
- **文档处理**: 三阶段智能PDF下载策略，100%成功率

### 技术亮点
- 支持巨潮网站特殊PDF下载（解决session和大小写问题）
- BGE-M3向量模型（1024维）进行语义检索
- 智能去重和批量处理管理
- 完整的性能监控和日志系统

## 📊 数据规模

- **股票数据**: 1500万+条日线行情记录
- **公告文档**: 200万+条公告元数据，95,662+向量化文档
- **财务数据**: 完整的三大报表和财务指标
- **实时更新**: 支持每日数据同步

## 📋 系统要求

- Python 3.8+
- MySQL 5.7+
- Milvus 2.0+
- CUDA (可选，用于GPU加速)
- 16GB+ RAM推荐

## 🔧 快速开始

### 1. 克隆项目
```bash
git clone https://github.com/YOUR_USERNAME/stock-analysis-system.git
cd stock-analysis-system
```

### 2. 创建虚拟环境
```bash
python -m venv stock_analysis_env
source stock_analysis_env/bin/activate  # Linux/Mac
# 或
stock_analysis_env\\Scripts\\activate  # Windows
```

### 3. 安装依赖
```bash
pip install -r requirements.txt
```

### 4. 配置环境变量
```bash
cp .env.example .env
# 编辑.env文件，填入你的数据库和API配置
```

### 5. 启动服务
```bash
python -m uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

访问 http://localhost:8000/docs 查看API文档

## 📖 使用示例

### SQL查询
```python
# 查询贵州茅台最新股价
POST /api/query
{
    "question": "贵州茅台最新股价",
    "query_type": "sql"
}

# 查询涨幅排行
{
    "question": "今天涨幅最大的10只股票",
    "query_type": "sql"
}
```

### RAG查询
```python
# 查询财务报告
POST /api/query
{
    "question": "贵州茅台2024年第一季度营收情况",
    "query_type": "rag"
}

# 分析毛利率
{
    "question": "分析白酒行业主要公司的毛利率对比",
    "query_type": "rag"
}
```

### 混合查询
```python
# 综合分析
POST /api/query
{
    "question": "分析贵州茅台的财务状况和股价表现",
    "query_type": "hybrid"
}
```

## 🛠️ 主要组件

### 核心模块
- `config/` - 系统配置管理
- `database/` - MySQL和Milvus连接器
- `rag/` - RAG系统实现
- `agents/` - SQL、RAG和混合Agent
- `models/` - LLM和嵌入模型配置
- `api/` - FastAPI服务接口
- `utils/` - 工具函数和日志系统

### 重要脚本
- `smart_processor_v5_1.py` - 智能文档处理器（最新版）
- `batch_process_manager.py` - 批量处理管理器
- `milvus_dedup_script_v2.py` - 向量数据库去重工具
- `rag_query_interface.py` - RAG查询交互界面

## 📈 性能指标

- SQL查询响应：5-30秒
- RAG查询响应：3-15秒
- PDF处理速度：30秒/文档
- 并发支持：多用户同时访问
- 系统稳定性：生产环境验证

## 🔍 高级功能

### 文档处理
- 自动识别和下载上市公司公告PDF
- 智能文本提取和分块（chunk_size=1000）
- 支持pdfplumber和PyPDF2双引擎
- OCR失败文件自动记录

### 查询优化
- 查询缓存机制
- 智能查询路由
- 相似度阈值过滤
- 元数据增强检索

## 🤝 贡献指南

欢迎提交Issue和Pull Request！请确保：
- 遵循现有代码风格
- 添加适当的测试
- 更新相关文档

## 📄 许可证

MIT License

## 👥 作者

[Your Name]

## 🙏 致谢

- LangChain团队提供的优秀框架
- Tushare提供的金融数据接口
- DeepSeek提供的LLM API支持
- BGE-M3模型提供的中文语义理解能力

## 📞 联系方式

- GitHub Issues: [链接]
- Email: [邮箱]

---

⭐ 如果觉得这个项目有帮助，请给个Star支持一下！
"""
        readme_path = self.project_root / "README.md"
        with open(readme_path, 'w', encoding='utf-8') as f:
            f.write(readme_content)
        print(f"✅ README.md 文件已创建: {readme_path}")

    def execute_cleanup(self, dry_run: bool = True):
        """执行清理操作"""
        if dry_run:
            print("\n🔍 模拟执行（不会真正删除/移动文件）")
        else:
            print("\n⚠️  警告：即将执行实际的文件操作！")
            confirm = input("确认继续？(yes/no): ")
            if confirm.lower() != 'yes':
                print("操作已取消")
                return
        
        # 创建必要的目录
        dirs_to_create = [
            'scripts/analysis',
            'scripts/maintenance', 
            'scripts/tools',
            'scripts/tests',
            'scripts/debugging',
            'scripts/utils',
            'scripts/setup',
            'archive/fixes/sql_agent_fixes',
            'archive/fixes/api_response_fixes',
            'archive/fixes/timeout_fixes',
            'archive/fixes/import_fixes',
            'archive/fixes/enum_fixes',
            'archive/old_versions',
            'archive/other',
            'docs/project_status',
            'docs/examples'
        ]
        
        for dir_name in dirs_to_create:
            dir_path = self.project_root / dir_name
            if not dir_path.exists():
                if not dry_run:
                    dir_path.mkdir(parents=True, exist_ok=True)
                print(f"{'[模拟]' if dry_run else '✅'} 创建目录: {dir_name}")
        
        # 移动可重复使用的工具
        tool_mappings = {
            'tushare-db-analyzer.py': 'scripts/analysis/db_analyzer.py',
            'analyze_announcement_titles.py': 'scripts/analysis/announcement_analyzer.py',
            'test_api_correct.py': 'scripts/tests/test_api.py',
            'test_agents.py': 'scripts/tests/',
            'verify_system.py': 'scripts/utils/system_check.py',
            'load_milvus_collection.py': 'scripts/tools/',
            'install_dependencies.py': 'scripts/setup/',
        }
        
        for src_name, dst_path in tool_mappings.items():
            src = self.project_root / src_name
            if src.exists():
                if dst_path.endswith('/'):
                    dst = self.project_root / dst_path / src_name
                else:
                    dst = self.project_root / dst_path
                if not dry_run:
                    shutil.move(str(src), str(dst))
                print(f"{'[模拟]' if dry_run else '✅'} 移动: {src_name} -> {dst_path}")
        
        # 移动项目状态文档
        for doc in self.analysis_results['documentation']:
            if 'project_status' in doc:
                src = self.project_root / doc
                dst = self.project_root / 'docs' / 'project_status' / Path(doc).name
                if src.exists() and src != dst:
                    if not dry_run:
                        shutil.move(str(src), str(dst))
                    print(f"{'[模拟]' if dry_run else '✅'} 移动: {doc} -> docs/project_status/")
        
        # 归档一次性脚本
        fix_mappings = {
            'sql_agent': 'archive/fixes/sql_agent_fixes/',
            'api_response': 'archive/fixes/api_response_fixes/',
            'timeout': 'archive/fixes/timeout_fixes/',
            'import': 'archive/fixes/import_fixes/',
            'enum': 'archive/fixes/enum_fixes/',
            'processor': 'archive/old_versions/'
        }
        
        for archive_file in self.analysis_results['to_archive']:
            src = self.project_root / archive_file
            if src.exists():
                # 确定目标目录
                target_dir = 'archive/other/'
                for key, dir_path in fix_mappings.items():
                    if key in archive_file.lower():
                        target_dir = dir_path
                        break
                
                dst = self.project_root / target_dir / Path(archive_file).name
                if not dry_run:
                    shutil.move(str(src), str(dst))
                print(f"{'[模拟]' if dry_run else '✅'} 归档: {archive_file} -> {target_dir}")
        
        # 删除临时文件
        for temp_file in self.analysis_results['to_delete']:
            file_path = self.project_root / temp_file
            if file_path.exists():
                if not dry_run:
                    if file_path.is_dir():
                        shutil.rmtree(file_path)
                    else:
                        file_path.unlink()
                print(f"{'[模拟]' if dry_run else '✅'} 删除: {temp_file}")
        
        if not dry_run:
            print("\n✅ 清理完成！")
        else:
            print("\n💡 模拟完成！使用 --execute 参数来执行实际操作")

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Git版本管理准备工具")
    parser.add_argument("--analyze", action="store_true", help="分析项目结构")
    parser.add_argument("--create-gitignore", action="store_true", help="创建.gitignore文件")
    parser.add_argument("--create-env-example", action="store_true", help="创建.env.example文件")
    parser.add_argument("--create-readme", action="store_true", help="创建README.md文件")
    parser.add_argument("--cleanup", action="store_true", help="执行清理操作（模拟）")
    parser.add_argument("--execute", action="store_true", help="执行实际的清理操作")
    parser.add_argument("--all", action="store_true", help="执行所有操作")
    
    args = parser.parse_args()
    
    preparer = ProjectGitPreparer()
    
    if args.all or args.analyze:
        preparer.analyze_project()
    
    if args.all or args.create_gitignore:
        preparer.create_gitignore()
    
    if args.all or args.create_env_example:
        preparer.create_env_example()
    
    if args.all or args.create_readme:
        preparer.create_readme()
    
    if args.cleanup or args.execute:
        preparer.execute_cleanup(dry_run=not args.execute)
    
    if not any(vars(args).values()):
        print("使用 --help 查看可用选项")
        print("\n快速开始:")
        print("1. python project_git_prepare.py --analyze  # 分析项目")
        print("2. python project_git_prepare.py --all      # 创建所有必要文件")
        print("3. python project_git_prepare.py --cleanup  # 模拟清理")
        print("4. python project_git_prepare.py --execute  # 执行清理")

if __name__ == "__main__":
    main()
