#!/usr/bin/env python3
"""
统一版本同步脚本
一键更新项目中所有版本号
"""

import os
import re
import json
import sys

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from version import VERSION, VERSION_INFO


def update_file(filepath, updates):
    """更新文件内容"""
    if not os.path.exists(filepath):
        print(f"❌ 文件不存在: {filepath}")
        return False
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        for pattern, replacement in updates:
            content = re.sub(pattern, replacement, content, flags=re.MULTILINE)
        
        if content != original_content:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✅ 更新: {filepath}")
            return True
        else:
            print(f"⏭️  跳过: {filepath} (已是最新)")
            return False
    except Exception as e:
        print(f"❌ 错误: {filepath} - {str(e)}")
        return False


def update_json_file(filepath, key, value):
    """更新JSON文件"""
    if not os.path.exists(filepath):
        print(f"❌ 文件不存在: {filepath}")
        return False
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        if data.get(key) != value:
            data[key] = value
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
                f.write('\n')
            print(f"✅ 更新: {filepath}")
            return True
        else:
            print(f"⏭️  跳过: {filepath} (已是最新)")
            return False
    except Exception as e:
        print(f"❌ 错误: {filepath} - {str(e)}")
        return False


def main():
    """执行版本同步"""
    print(f"🚀 同步版本号到: v{VERSION}")
    print("=" * 60)
    
    updated_count = 0
    
    # 1. 更新文档文件
    print("\n📄 更新文档文件...")
    
    # CLAUDE.md
    if update_file('CLAUDE.md', [
        (r'Stock Analysis System \(v[\d.]+\)', f'Stock Analysis System (v{VERSION})'),
        (r'## Project Overview\n\nThis is a \*\*Stock Analysis System \(v[\d.]+\)\*\*', 
         f'## Project Overview\n\nThis is a **Stock Analysis System (v{VERSION})**')
    ]):
        updated_count += 1
    
    # docs/project_status/CURRENT_STATUS.md
    if update_file('docs/project_status/CURRENT_STATUS.md', [
        (r'\*\*版本\*\*: v[\d.]+', f'**版本**: v{VERSION}'),
        (r'\*\*更新日期\*\*: \d{4}-\d{2}-\d{2}', f'**更新日期**: {VERSION_INFO["release_date"]}'),
        (r'\*\*下一版本\*\*: v[\d.]+', f'**下一版本**: v{VERSION.split(".")[0]}.{int(VERSION.split(".")[1])+1}.0')
    ]):
        updated_count += 1
    
    # test-guide.md
    if update_file('test-guide.md', [
        (r'\*\*版本\*\*: v[\d.]+', f'**版本**: v{VERSION}'),
        (r'\*\*更新日期\*\*: \d{4}-\d{2}-\d{2}', f'**更新日期**: {VERSION_INFO["release_date"]}')
    ]):
        updated_count += 1
    
    # 2. 更新Python文件
    print("\n🐍 更新Python文件...")
    
    # setup.py
    if update_file('setup.py', [
        (r'version="[\d.]+"', f'version="{VERSION}"')
    ]):
        updated_count += 1
    
    # api/main.py
    if update_file('api/main.py', [
        (r'version="[\d.]+"', f'version="{VERSION}"'),
        (r'智能股票分析API \(v[\d.]+\)', f'智能股票分析API (v{VERSION})')
    ]):
        updated_count += 1
    
    # 3. 更新前端文件
    print("\n⚛️  更新前端文件...")
    
    # frontend/package.json
    if update_json_file('frontend/package.json', 'version', VERSION):
        updated_count += 1
    
    # 4. 生成版本摘要
    print("\n📊 版本摘要")
    print("=" * 60)
    print(f"版本号: v{VERSION}")
    print(f"发布日期: {VERSION_INFO['release_date']}")
    print(f"代号: {VERSION_INFO['codename']}")
    print(f"描述: {VERSION_INFO['description']}")
    print(f"\n✅ 共更新 {updated_count} 个文件")
    
    # 5. 提示下一步操作
    print("\n📌 下一步操作:")
    print("1. 检查更新是否正确: git diff")
    print("2. 提交更改: git add -A && git commit -m \"chore: sync version to v{VERSION}\"")
    print("3. 创建标签: git tag -a v{VERSION} -m \"Release v{VERSION}\"")
    print("4. 推送: git push origin dev-react-frontend-v2 --tags")


if __name__ == "__main__":
    main()