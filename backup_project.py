#!/usr/bin/env python3
"""
股票分析系统 - 智能备份工具
支持增量备份、压缩备份、选择性备份等功能
"""

import os
import shutil
import zipfile
from datetime import datetime
from pathlib import Path
import argparse
import json
import time

class ProjectBackup:
    def __init__(self):
        self.project_root = Path.cwd()
        self.backup_base_dir = self.project_root.parent
        self.timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # 默认排除的文件和目录
        self.default_ignore_patterns = [
            # Python相关
            '__pycache__',
            '*.pyc',
            '*.pyo',
            '*.pyd',
            '.Python',
            'pip-log.txt',
            'pip-delete-this-directory.txt',
            '.tox/',
            '.coverage',
            '.coverage.*',
            '.cache',
            '.pytest_cache/',
            'htmlcov/',
            '*.egg-info/',
            '*.egg',
            
            # 虚拟环境
            'stock_analysis_env/',
            'venv/',
            'env/',
            'ENV/',
            
            # IDE
            '.idea/',
            '.vscode/',
            '*.swp',
            '*.swo',
            '*~',
            
            # Git
            '.git/',
            '.gitignore',
            
            # 日志
            '*.log',
            'logs/',
            
            # 大文件和缓存
            'data/pdfs/cache/',
            'data/milvus/',
            'models/bge-m3/.git/',
            'models/bge-m3/onnx/',
            '*.bin',
            '*.pth',
            '*.h5',
            '*.safetensors',
            
            # 临时文件
            '.DS_Store',
            'Thumbs.db',
            'desktop.ini',
            
            # 备份文件
            '*.backup',
            '*.bak',
            'backup_*',
            'archive/',
        ]
        
        # 重要文件列表（即使在忽略目录中也要备份）
        self.important_files = [
            '.env.example',
            'requirements.txt',
            'README.md',
            'setup.py',
        ]

    def calculate_size(self, path):
        """计算目录大小"""
        total_size = 0
        for dirpath, dirnames, filenames in os.walk(path):
            for filename in filenames:
                filepath = os.path.join(dirpath, filename)
                if os.path.exists(filepath):
                    total_size += os.path.getsize(filepath)
        return total_size

    def format_size(self, size):
        """格式化文件大小"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024.0:
                return f"{size:.2f} {unit}"
            size /= 1024.0
        return f"{size:.2f} TB"

    def create_backup_info(self, backup_path, start_time, file_count):
        """创建备份信息文件"""
        end_time = time.time()
        info = {
            "backup_date": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            "source_path": str(self.project_root),
            "backup_path": str(backup_path),
            "file_count": file_count,
            "backup_size": self.format_size(self.calculate_size(backup_path)),
            "duration_seconds": round(end_time - start_time, 2),
            "python_version": os.sys.version,
            "ignore_patterns": self.default_ignore_patterns
        }
        
        info_file = backup_path / "backup_info.json"
        with open(info_file, 'w', encoding='utf-8') as f:
            json.dump(info, f, indent=2, ensure_ascii=False)
        
        return info

    def should_ignore(self, path, ignore_patterns):
        """检查是否应该忽略某个路径"""
        path_str = str(path)
        
        # 检查是否是重要文件
        for important in self.important_files:
            if path_str.endswith(important):
                return False
        
        # 检查忽略模式
        for pattern in ignore_patterns:
            if pattern.endswith('/'):
                # 目录模式
                if f"/{pattern}" in path_str or path_str.endswith(pattern[:-1]):
                    return True
            elif '*' in pattern:
                # 通配符模式
                import fnmatch
                if fnmatch.fnmatch(path_str, pattern):
                    return True
            else:
                # 精确匹配
                if pattern in path_str:
                    return True
        
        return False

    def copy_with_progress(self, src, dst, ignore_patterns=None):
        """带进度显示的复制"""
        if ignore_patterns is None:
            ignore_patterns = self.default_ignore_patterns
        
        total_files = 0
        copied_files = 0
        skipped_files = 0
        
        # 先计算总文件数
        print("📊 正在统计文件...")
        for root, dirs, files in os.walk(src):
            dirs[:] = [d for d in dirs if not self.should_ignore(Path(root) / d, ignore_patterns)]
            for file in files:
                if not self.should_ignore(Path(root) / file, ignore_patterns):
                    total_files += 1
        
        print(f"📁 发现 {total_files} 个需要备份的文件\n")
        
        # 开始复制
        for root, dirs, files in os.walk(src):
            # 过滤目录
            dirs[:] = [d for d in dirs if not self.should_ignore(Path(root) / d, ignore_patterns)]
            
            # 创建目标目录
            rel_path = Path(root).relative_to(src)
            dst_dir = dst / rel_path
            if not dst_dir.exists():
                dst_dir.mkdir(parents=True, exist_ok=True)
            
            # 复制文件
            for file in files:
                src_file = Path(root) / file
                dst_file = dst_dir / file
                
                if self.should_ignore(src_file, ignore_patterns):
                    skipped_files += 1
                    continue
                
                try:
                    shutil.copy2(src_file, dst_file)
                    copied_files += 1
                    
                    # 显示进度
                    if copied_files % 100 == 0 or copied_files == total_files:
                        progress = (copied_files / total_files) * 100
                        bar_length = 30
                        filled_length = int(bar_length * copied_files // total_files)
                        bar = '█' * filled_length + '░' * (bar_length - filled_length)
                        print(f'\r进度: [{bar}] {progress:.1f}% ({copied_files}/{total_files})', end='')
                        
                except Exception as e:
                    print(f"\n⚠️  复制失败: {src_file} - {e}")
        
        print(f"\n\n✅ 复制完成: {copied_files} 个文件")
        if skipped_files > 0:
            print(f"⏭️  跳过文件: {skipped_files} 个")
        
        return copied_files

    def create_full_backup(self, compress=False, custom_name=None):
        """创建完整备份"""
        backup_name = custom_name or f"stock_analysis_backup_{self.timestamp}"
        backup_path = self.backup_base_dir / backup_name
        
        print(f"🚀 开始备份项目...")
        print(f"📍 源目录: {self.project_root}")
        print(f"📍 目标目录: {backup_path}")
        print(f"📅 时间戳: {self.timestamp}\n")
        
        start_time = time.time()
        
        try:
            # 创建备份目录
            backup_path.mkdir(parents=True, exist_ok=True)
            
            # 复制文件
            file_count = self.copy_with_progress(self.project_root, backup_path)
            
            # 创建备份信息
            info = self.create_backup_info(backup_path, start_time, file_count)
            
            # 如果需要压缩
            if compress:
                print("\n📦 正在压缩备份...")
                zip_path = backup_path.with_suffix('.zip')
                
                with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                    for root, dirs, files in os.walk(backup_path):
                        for file in files:
                            file_path = Path(root) / file
                            arcname = file_path.relative_to(backup_path)
                            zipf.write(file_path, arcname)
                
                # 删除未压缩的备份
                shutil.rmtree(backup_path)
                
                zip_size = self.format_size(os.path.getsize(zip_path))
                print(f"✅ 压缩完成！压缩包大小: {zip_size}")
                print(f"📍 压缩包位置: {zip_path}")
            else:
                print(f"\n📊 备份统计:")
                print(f"  - 备份文件数: {info['file_count']}")
                print(f"  - 备份大小: {info['backup_size']}")
                print(f"  - 耗时: {info['duration_seconds']} 秒")
                print(f"\n✅ 备份完成！")
                print(f"📍 备份位置: {backup_path.absolute()}")
                
        except Exception as e:
            print(f"\n❌ 备份失败: {e}")
            if backup_path.exists():
                print("🧹 清理未完成的备份...")
                shutil.rmtree(backup_path)
            raise

    def create_code_only_backup(self):
        """只备份代码文件（不包括数据和模型）"""
        # 添加额外的忽略模式
        code_ignore_patterns = self.default_ignore_patterns + [
            'data/',
            'models/',
            '*.pdf',
            '*.csv',
            '*.xlsx',
            '*.json',
            '*.pkl',
            '*.npy',
            '*.npz',
        ]
        
        backup_name = f"stock_analysis_code_only_{self.timestamp}"
        backup_path = self.backup_base_dir / backup_name
        
        print(f"🚀 开始备份代码文件...")
        print(f"📍 源目录: {self.project_root}")
        print(f"📍 目标目录: {backup_path}")
        print("📝 类型: 仅代码文件\n")
        
        start_time = time.time()
        
        try:
            backup_path.mkdir(parents=True, exist_ok=True)
            
            # 使用自定义忽略模式复制
            old_patterns = self.default_ignore_patterns
            self.default_ignore_patterns = code_ignore_patterns
            
            file_count = self.copy_with_progress(self.project_root, backup_path)
            
            self.default_ignore_patterns = old_patterns
            
            info = self.create_backup_info(backup_path, start_time, file_count)
            
            print(f"\n✅ 代码备份完成！")
            print(f"📍 备份位置: {backup_path.absolute()}")
            
        except Exception as e:
            print(f"\n❌ 备份失败: {e}")
            if backup_path.exists():
                shutil.rmtree(backup_path)
            raise

    def list_backups(self):
        """列出所有备份"""
        print("📋 现有备份列表:\n")
        
        backups = []
        for item in self.backup_base_dir.iterdir():
            if item.is_dir() and 'stock_analysis_backup' in item.name:
                info_file = item / 'backup_info.json'
                if info_file.exists():
                    with open(info_file, 'r', encoding='utf-8') as f:
                        info = json.load(f)
                        backups.append((item.name, info))
                else:
                    # 旧备份可能没有info文件
                    size = self.format_size(self.calculate_size(item))
                    backups.append((item.name, {"backup_size": size}))
        
        if not backups:
            print("❌ 没有找到备份")
            return
        
        for name, info in sorted(backups, reverse=True):
            print(f"📁 {name}")
            if 'backup_date' in info:
                print(f"   日期: {info['backup_date']}")
            if 'file_count' in info:
                print(f"   文件: {info['file_count']} 个")
            print(f"   大小: {info.get('backup_size', '未知')}")
            print()

def main():
    parser = argparse.ArgumentParser(description='股票分析系统备份工具')
    parser.add_argument('--compress', '-c', action='store_true', 
                       help='创建压缩备份（ZIP格式）')
    parser.add_argument('--code-only', action='store_true',
                       help='只备份代码文件（不包括数据和模型）')
    parser.add_argument('--name', type=str,
                       help='自定义备份名称')
    parser.add_argument('--list', '-l', action='store_true',
                       help='列出所有备份')
    
    args = parser.parse_args()
    
    backup = ProjectBackup()
    
    try:
        if args.list:
            backup.list_backups()
        elif args.code_only:
            backup.create_code_only_backup()
        else:
            backup.create_full_backup(compress=args.compress, custom_name=args.name)
    except KeyboardInterrupt:
        print("\n\n⚠️  备份被用户中断")
    except Exception as e:
        print(f"\n❌ 错误: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
