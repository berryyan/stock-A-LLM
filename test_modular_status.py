#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试模块化系统的当前状态
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def check_modular_status():
    """检查模块化系统的当前状态"""
    print("=== 检查模块化系统状态 ===\n")
    
    # 1. 检查模块化组件
    print("1. 检查模块化组件:")
    components = [
        ("参数提取器", "utils.parameter_extractor", "ParameterExtractor"),
        ("查询验证器", "utils.query_validator", "QueryValidator"),
        ("结果格式化器", "utils.result_formatter", "ResultFormatter"),
        ("错误处理器", "utils.error_handler", "ErrorHandler"),
        ("统一响应格式", "utils.agent_response", "AgentResponse"),
    ]
    
    for name, module_name, class_name in components:
        try:
            module = __import__(module_name, fromlist=[class_name])
            cls = getattr(module, class_name)
            print(f"   ✓ {name}: {cls.__name__} 已实现")
        except Exception as e:
            print(f"   ✗ {name}: 导入失败 - {e}")
    
    print("\n2. 检查模块化Agent:")
    agents = [
        ("SQL Agent", "agents.sql_agent_modular", "SQLAgentModular"),
        ("RAG Agent", "agents.rag_agent_modular", "RAGAgentModular"),
        ("Financial Agent", "agents.financial_agent_modular", "FinancialAgentModular"),
        ("Money Flow Agent", "agents.money_flow_agent_modular", "MoneyFlowAgentModular"),
        ("Hybrid Agent", "agents.hybrid_agent_modular", "HybridAgentModular"),
    ]
    
    for name, module_name, class_name in agents:
        try:
            module = __import__(module_name, fromlist=[class_name])
            cls = getattr(module, class_name)
            print(f"   ✓ {name}: {cls.__name__} 已实现")
        except Exception as e:
            print(f"   ✗ {name}: 导入失败 - {e}")
    
    print("\n3. 检查API层:")
    apis = [
        ("原始API", "api.main", "app"),
        ("模块化API", "api.main_modular", "app"),
    ]
    
    for name, module_name, var_name in apis:
        try:
            module = __import__(module_name, fromlist=[var_name])
            app = getattr(module, var_name)
            print(f"   ✓ {name}: FastAPI应用已定义")
        except Exception as e:
            print(f"   ✗ {name}: 导入失败 - {e}")
    
    print("\n4. 测试基础功能:")
    try:
        # 测试参数提取器
        from utils.parameter_extractor import ParameterExtractor
        extractor = ParameterExtractor()
        
        # 测试股票提取
        query = "贵州茅台的最新股价"
        params = extractor.extract_all_params(query)
        print(f"   ✓ 参数提取测试: {query}")
        print(f"     - 股票: {params.stocks}")
        print(f"     - 日期: {params.start_date}")
        
        # 测试结果格式化器
        from utils.result_formatter import ResultFormatter
        formatter = ResultFormatter()
        
        # 测试表格格式化
        data = [{"股票": "贵州茅台", "代码": "600519.SH", "价格": 1403}]
        result = formatter.format_as_table(data)
        print(f"\n   ✓ 结果格式化测试:")
        print(result)
        
    except Exception as e:
        print(f"   ✗ 功能测试失败: {e}")
    
    print("\n=== 状态检查完成 ===")


if __name__ == "__main__":
    check_modular_status()