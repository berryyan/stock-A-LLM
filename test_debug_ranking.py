"""
调试排名查询问题
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.sql_agent import SQLAgent
import logging

# 设置日志级别为DEBUG
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

def test_ranking_query():
    # 初始化SQL Agent
    sql_agent = SQLAgent()
    
    # 测试涨幅前十查询
    print("="*60)
    print("测试涨幅前十查询")
    print("="*60)
    
    result = sql_agent.query("涨幅前十")
    
    print(f"\n查询结果: {result}")
    
    if result['success']:
        print(f"\n成功! 结果:\n{result['result']}")
    else:
        print(f"\n失败! 错误: {result.get('error', '未知错误')}")

if __name__ == "__main__":
    test_ranking_query()