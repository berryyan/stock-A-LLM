#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试SQL Agent修复效果
验证Schema知识库使用和输出解析错误处理
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.sql_agent import SQLAgent
from utils.logger import setup_logger

logger = setup_logger("test_sql_fix")

def test_sql_agent():
    """测试SQL Agent"""
    print("="*60)
    print("测试SQL Agent修复效果")
    print("="*60)
    
    # 创建SQL Agent
    print("\n1. 创建SQL Agent...")
    agent = SQLAgent()
    
    # 测试查询
    test_query = "贵州茅台最新股价是多少？"
    print(f"\n2. 测试查询: {test_query}")
    
    try:
        result = agent.query(test_query)
        
        print("\n3. 查询结果:")
        print(f"   成功: {result.get('success', False)}")
        
        if result['success']:
            print(f"   结果: {result.get('result', 'N/A')}")
        else:
            print(f"   错误: {result.get('error', 'N/A')}")
            
        # 检查是否使用缓存
        if result.get('cached', False):
            print("   注意: 使用了缓存结果")
            
    except Exception as e:
        print(f"\n错误: {e}")
        logger.error(f"测试失败: {e}")
    
    # 再测试一个查询
    test_query2 = "查询比亚迪今天的成交量"
    print(f"\n4. 测试第二个查询: {test_query2}")
    
    try:
        result2 = agent.query(test_query2)
        
        print("\n5. 查询结果:")
        print(f"   成功: {result2.get('success', False)}")
        
        if result2['success']:
            print(f"   结果: {result2.get('result', 'N/A')[:200]}...")  # 只显示前200字符
        else:
            print(f"   错误: {result2.get('error', 'N/A')}")
            
    except Exception as e:
        print(f"\n错误: {e}")
        logger.error(f"第二个测试失败: {e}")

def check_logs():
    """检查日志输出"""
    print("\n\n6. 检查最近的日志:")
    print("-"*60)
    
    try:
        # 读取最近的SQL Agent日志
        with open("logs/sql_agent.log", "r", encoding="utf-8") as f:
            lines = f.readlines()
            
        # 查找Schema相关日志
        recent_lines = lines[-50:]  # 最后50行
        schema_logs = [line for line in recent_lines if "Schema" in line or "知识库" in line]
        
        if schema_logs:
            print("Schema知识库相关日志:")
            for log in schema_logs[-10:]:  # 显示最后10条
                print(f"   {log.strip()}")
        else:
            print("未找到Schema知识库相关日志")
            
    except Exception as e:
        print(f"读取日志失败: {e}")

if __name__ == "__main__":
    test_sql_agent()
    check_logs()
    
    print("\n" + "="*60)
    print("测试完成！")
    print("请检查：")
    print("1. 是否还有输出解析错误")
    print("2. Schema知识库是否正常工作")
    print("3. 查询结果是否正确返回")
    print("="*60)