#!/usr/bin/env python3
"""测试板块查询问题"""

import sys
sys.path.append('.')

from utils.date_intelligence import date_intelligence
from utils.query_templates import match_query_template
from utils.parameter_extractor import ParameterExtractor

# 测试查询
query = "银行板块昨天的主力资金"
print(f"原始查询: {query}")

# 1. 日期智能解析
processed_query, date_info = date_intelligence.preprocess_question(query)
print(f"日期处理后: {processed_query}")

# 2. 模板匹配
template_result = match_query_template(processed_query)
if template_result:
    template, params = template_result
    print(f"匹配到模板: {template.name}")
    print(f"模板类型: {template.type}")
    print(f"路由类型: {template.route_type}")
    print(f"需要股票: {template.requires_stock}")
else:
    print("未匹配到模板")

# 3. 参数提取
extractor = ParameterExtractor()
# 如果有模板，传入模板
if template_result:
    extracted_params = extractor.extract_all_params(processed_query, template)
else:
    extracted_params = extractor.extract_all_params(processed_query)
print(f"\n提取的参数:")
print(f"股票: {extracted_params.stocks}")
print(f"板块: {extracted_params.sector}")
print(f"日期: {extracted_params.date}")
print(f"错误: {extracted_params.error}")