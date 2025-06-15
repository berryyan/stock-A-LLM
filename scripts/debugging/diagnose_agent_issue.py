"""
诊断 SQL Agent 和 Hybrid Agent 之间的接口问题
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.sql_agent import SQLAgent
from agents.hybrid_agent import HybridAgent
import json

def test_sql_agent_directly():
    """直接测试 SQL Agent 的返回值"""
    print("=" * 60)
    print("1. 直接测试 SQL Agent")
    print("=" * 60)
    
    try:
        sql_agent = SQLAgent()
        
        # 测试查询
        result = sql_agent.query("贵州茅台最新股价")
        
        print(f"返回类型: {type(result)}")
        print(f"返回内容: {result}")
        
        if isinstance(result, dict):
            print("\n字典内容:")
            for key, value in result.items():
                print(f"  {key}: {type(value).__name__} = {value}")
        
        return result
        
    except Exception as e:
        print(f"错误: {e}")
        import traceback
        traceback.print_exc()
        return None

def test_hybrid_agent_directly():
    """直接测试 Hybrid Agent"""
    print("\n" + "=" * 60)
    print("2. 直接测试 Hybrid Agent")
    print("=" * 60)
    
    try:
        hybrid_agent = HybridAgent()
        
        # 测试查询
        result = hybrid_agent.query("贵州茅台最新股价")
        
        print(f"返回类型: {type(result)}")
        print(f"返回内容: {result}")
        
        if isinstance(result, dict):
            print("\n字典内容:")
            for key, value in result.items():
                print(f"  {key}: {type(value).__name__} = {value}")
        
        return result
        
    except Exception as e:
        print(f"错误: {e}")
        import traceback
        traceback.print_exc()
        return None

def analyze_hybrid_agent_code():
    """分析 Hybrid Agent 的代码"""
    print("\n" + "=" * 60)
    print("3. 分析 Hybrid Agent 处理 SQL 结果的代码")
    print("=" * 60)
    
    try:
        # 读取 hybrid_agent.py 文件
        with open('agents/hybrid_agent.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 查找处理 SQL 结果的代码
        import re
        
        # 查找 _execute_sql_query 方法
        sql_method = re.search(r'def _execute_sql_query.*?(?=\n    def|\nclass|\Z)', content, re.DOTALL)
        if sql_method:
            print("找到 _execute_sql_query 方法:")
            lines = sql_method.group(0).split('\n')
            for i, line in enumerate(lines[:20]):  # 只显示前20行
                print(f"{i+1:3d}: {line}")
        
        # 查找错误处理部分
        error_handling = re.findall(r'string indices.*?\n.*?\n.*?\n', content, re.DOTALL)
        if error_handling:
            print("\n可能的错误位置:")
            for match in error_handling:
                print(match)
                
    except Exception as e:
        print(f"分析失败: {e}")

def simulate_hybrid_processing():
    """模拟 Hybrid Agent 处理 SQL Agent 返回值的过程"""
    print("\n" + "=" * 60)
    print("4. 模拟 Hybrid Agent 处理过程")
    print("=" * 60)
    
    # 模拟 SQL Agent 的返回值
    sql_result = "The closing price of 贵州茅台(600519.SH) on 2025-06-06 was 1506.39."
    
    print(f"模拟 SQL Agent 返回: {sql_result}")
    print(f"类型: {type(sql_result)}")
    
    # 如果 Hybrid Agent 期望字典格式
    try:
        # 尝试作为字典访问
        print("\n尝试作为字典访问 ['result']:")
        print(sql_result['result'])
    except TypeError as e:
        print(f"错误: {e}")
        print("这就是 'string indices must be integers' 错误的来源!")
    
    # 正确的处理方式
    print("\n正确的处理方式:")
    if isinstance(sql_result, str):
        print("检测到字符串，直接使用")
    elif isinstance(sql_result, dict):
        print("检测到字典，提取内容")

if __name__ == "__main__":
    print("股票分析系统 - Agent 返回格式诊断工具")
    print("=" * 60)
    
    # 运行诊断
    test_sql_agent_directly()
    test_hybrid_agent_directly()
    analyze_hybrid_agent_code()
    simulate_hybrid_processing()
    
    print("\n" + "=" * 60)
    print("诊断建议:")
    print("1. SQL Agent 返回的是字符串，但 Hybrid Agent 期望字典")
    print("2. 需要修改 Hybrid Agent 的 _execute_sql_query 方法")
    print("3. 或者让 SQL Agent 返回统一的字典格式")
