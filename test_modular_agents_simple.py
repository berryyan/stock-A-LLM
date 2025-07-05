#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
模块化Agent简单集成测试
测试基本查询功能
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.sql_agent_modular import SQLAgentModular
from utils.logger import setup_logger
import asyncio

logger = setup_logger("test_modular_agents")


def test_sql_agent_simple():
    """测试SQL Agent基本功能"""
    print("\n" + "="*60)
    print("测试SQL Agent模块化版本")
    print("="*60)
    
    try:
        # 初始化Agent
        print("\n初始化SQL Agent...")
        agent = SQLAgentModular()
        print("✅ 初始化成功")
        
        # 测试查询
        test_queries = [
            "贵州茅台的最新股价",
            "比较贵州茅台和五粮液的市值",
            "涨幅排名前5",
            "银行板块的主力资金"
        ]
        
        for query in test_queries:
            print(f"\n{'='*40}")
            print(f"测试查询: {query}")
            print('='*40)
            
            try:
                # 调用query方法
                result = agent.query(query)
                
                if result.get("success"):
                    print("✅ 查询成功")
                    # 只打印前500个字符
                    result_text = str(result.get("result", ""))
                    print(f"结果预览: {result_text[:500]}...")
                else:
                    print(f"❌ 查询失败: {result.get('error', '未知错误')}")
                    
            except Exception as e:
                print(f"❌ 执行出错: {str(e)}")
                logger.error(f"查询执行异常: {query}", exc_info=True)
                
    except Exception as e:
        print(f"❌ Agent初始化失败: {str(e)}")
        logger.error("Agent初始化异常", exc_info=True)


def test_sql_agent_direct():
    """直接测试SQL Agent的_extract_query_params方法"""
    print("\n" + "="*60)
    print("测试SQL Agent参数提取")
    print("="*60)
    
    try:
        agent = SQLAgentModular()
        
        # 测试_extract_query_params方法签名
        print("\n检查_extract_query_params方法...")
        import inspect
        sig = inspect.signature(agent._extract_query_params)
        print(f"方法签名: {sig}")
        
        # 获取最新交易日
        from utils import date_intelligence
        last_trading_date = date_intelligence.get_latest_trading_day()
        print(f"最新交易日: {last_trading_date}")
        
        # 测试参数提取
        query = "贵州茅台的最新股价"
        print(f"\n测试查询: {query}")
        
        # 根据方法签名调用
        params = agent._extract_query_params(query, last_trading_date)
        print(f"提取到的参数: {params}")
        
    except Exception as e:
        print(f"❌ 测试失败: {str(e)}")
        logger.error("参数提取测试异常", exc_info=True)


def main():
    """主测试函数"""
    print("="*60)
    print("模块化Agent简单集成测试")
    print("="*60)
    
    # 先测试参数提取
    test_sql_agent_direct()
    
    # 再测试完整功能
    test_sql_agent_simple()
    
    print("\n" + "="*60)
    print("测试完成")
    print("="*60)


if __name__ == "__main__":
    main()