#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试模块化Agent的初始化
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config.modular_settings import USE_MODULAR_AGENTS
print(f"USE_MODULAR_AGENTS = {USE_MODULAR_AGENTS}")

try:
    print("\n尝试导入HybridAgent...")
    from agents.hybrid_agent import HybridAgent
    
    print("\n尝试初始化HybridAgent...")
    agent = HybridAgent()
    
    print("\n检查子Agent类型...")
    print(f"SQL Agent类型: {type(agent.sql_agent).__name__}")
    print(f"RAG Agent类型: {type(agent.rag_agent).__name__}")
    print(f"Financial Agent类型: {type(agent.financial_agent).__name__}")
    print(f"Money Flow Agent类型: {type(agent.money_flow_agent).__name__}")
    
    print("\n✅ 初始化成功！")
    
except Exception as e:
    print(f"\n❌ 初始化失败: {str(e)}")
    import traceback
    traceback.print_exc()