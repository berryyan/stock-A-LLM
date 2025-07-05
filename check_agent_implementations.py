#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查各个Agent实现的差异
"""

import os
import re

def check_file_implementation(filepath):
    """检查文件的实现方式"""
    if not os.path.exists(filepath):
        return "文件不存在"
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 检查关键特征
    features = {
        "继承自原版": bool(re.search(r'from agents\.(?:sql_agent|rag_agent|financial_agent|money_flow_agent) import (?:SQLAgent|RAGAgent|FinancialAnalysisAgent|MoneyFlowAgent)', content)),
        "导入模块化组件": bool(re.search(r'from utils\.(?:parameter_extractor|query_validator|result_formatter|error_handler)', content)),
        "使用ParameterExtractor": bool(re.search(r'ParameterExtractor\(\)', content)),
        "使用QueryValidator": bool(re.search(r'QueryValidator\(\)', content)),
        "使用ResultFormatter": bool(re.search(r'ResultFormatter\(\)', content)),
        "使用ErrorHandler": bool(re.search(r'ErrorHandler\(\)', content)),
        "重写query方法": bool(re.search(r'def query\(self', content)),
        "重写_extract_query_params": bool(re.search(r'def _extract_query_params\(self', content)),
    }
    
    return features


def main():
    print("="*80)
    print("Agent实现方式检查")
    print("="*80)
    
    agents = [
        ("sql_agent.py", "原始版本"),
        ("sql_agent_v2.py", "V2版本"),
        ("sql_agent_modular.py", "Modular版本"),
        ("rag_agent.py", "原始RAG"),
        ("rag_agent_modular.py", "Modular RAG"),
        ("financial_agent.py", "原始Financial"),
        ("financial_agent_modular.py", "Modular Financial"),
        ("money_flow_agent.py", "原始MoneyFlow"),
        ("money_flow_agent_modular.py", "Modular MoneyFlow"),
    ]
    
    for filename, desc in agents:
        filepath = os.path.join("agents", filename)
        print(f"\n{'='*60}")
        print(f"{desc} ({filename}):")
        print('='*60)
        
        features = check_file_implementation(filepath)
        if isinstance(features, str):
            print(f"  {features}")
        else:
            for feature, has_it in features.items():
                if has_it:
                    print(f"  ✅ {feature}")
                else:
                    print(f"  ❌ {feature}")
    
    # 建议
    print("\n\n建议的命名方案：")
    print("="*60)
    print("1. sql_agent_v2.py -> sql_agent_modular.py (真正的模块化实现)")
    print("2. sql_agent_modular.py -> sql_agent_adapter.py (适配器模式)")
    print("3. 保持其他命名不变，但在文件头部添加清晰的说明")


if __name__ == "__main__":
    main()