#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试真正的模块化SQL Agent V2
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.sql_agent_modular import SQLAgentModular
import json


def main():
    print("="*60)
    print("测试SQL Agent（真正的模块化版本）")
    print("="*60)
    
    try:
        print("\n初始化SQL Agent Modular...")
        agent = SQLAgentModular()
        print("✅ 初始化成功")
        
        test_queries = [
            "贵州茅台的最新股价",
            "市值排名前3",
            "银行板块的主力资金"
        ]
        
        for query in test_queries:
            print(f"\n{'='*40}")
            print(f"查询: {query}")
            print('='*40)
            
            try:
                result = agent.query(query)
                
                print(f"成功: {result.get('success')}")
                
                if result.get('success'):
                    print(f"\n结果预览:")
                    result_text = str(result.get('result', ''))
                    print(result_text[:300] + "..." if len(result_text) > 300 else result_text)
                else:
                    print(f"\n错误: {result.get('error')}")
                    
            except Exception as e:
                print(f"\n❌ 查询异常: {str(e)}")
                import traceback
                traceback.print_exc()
                
    except Exception as e:
        print(f"\n❌ 初始化失败: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()