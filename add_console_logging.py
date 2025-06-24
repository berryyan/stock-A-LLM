#!/usr/bin/env python
"""
添加控制台日志输出的脚本
"""

import os

# 修改logger配置文件
logger_file = "utils/logger.py"

# 读取当前内容
with open(logger_file, 'r', encoding='utf-8') as f:
    content = f.read()

# 查找是否已经有控制台处理器
if 'console_handler' not in content:
    # 在文件处理器后添加控制台处理器
    insert_position = content.find('file_handler.setFormatter(formatter)')
    if insert_position != -1:
        insert_position = content.find('\n', insert_position) + 1
        
        console_handler_code = '''
    # 添加控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
'''
        
        # 插入代码
        new_content = content[:insert_position] + console_handler_code + content[insert_position:]
        
        # 备份原文件
        import shutil
        shutil.copy(logger_file, logger_file + '.backup')
        
        # 写入新内容
        with open(logger_file, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        print("✅ 已成功添加控制台日志输出！")
        print("📝 原文件已备份为 utils/logger.py.backup")
        print("🔄 重启API服务器后，您将在控制台看到查询日志。")
    else:
        print("⚠️ 无法定位插入位置，请手动修改。")
else:
    print("ℹ️ 控制台日志处理器已存在。")