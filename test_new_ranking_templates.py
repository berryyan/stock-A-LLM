#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试新增排名模板 - 设计测试用例
"""

import json


def design_new_ranking_templates():
    """设计新的排名模板"""
    
    print("=" * 80)
    print("新增排名模板设计")
    print("=" * 80)
    
    # 新增模板设计
    new_templates = [
        {
            "name": "PE排名",
            "description": "市盈率排名查询",
            "test_cases": [
                # 正向测试用例
                {
                    "query": "PE最高的前10",
                    "expected_behavior": "返回PE最高的10只股票",
                    "required_fields": ["ts_code", "name", "pe", "close"],
                    "order_by": "pe DESC"
                },
                {
                    "query": "市盈率排名前20",
                    "expected_behavior": "返回PE最高的20只股票",
                    "required_fields": ["ts_code", "name", "pe", "close"],
                    "order_by": "pe DESC"
                },
                {
                    "query": "PE最低的前10",
                    "expected_behavior": "返回PE最低的10只股票（排除负值）",
                    "required_fields": ["ts_code", "name", "pe", "close"],
                    "order_by": "pe ASC",
                    "filter": "pe > 0"
                },
                {
                    "query": "今天PE排名",
                    "expected_behavior": "返回今天PE最高的10只股票",
                    "required_fields": ["ts_code", "name", "pe", "close"],
                    "order_by": "pe DESC",
                    "default_limit": 10
                }
            ],
            "pattern": r"(?:PE|市盈率)(?:最高|最低|排名|前).*?(\d+)?|.*前(\d+).*(?:PE|市盈率)",
            "sql_template": "SELECT ts_code, close, pe FROM tu_daily_basic WHERE trade_date = :trade_date AND pe > 0 ORDER BY pe {order} LIMIT :limit"
        },
        
        {
            "name": "PB排名",
            "description": "市净率排名查询",
            "test_cases": [
                {
                    "query": "PB最低的前10",
                    "expected_behavior": "返回PB最低的10只股票（破净股）",
                    "required_fields": ["ts_code", "name", "pb", "close"],
                    "order_by": "pb ASC",
                    "filter": "pb > 0"
                },
                {
                    "query": "市净率排名前20",
                    "expected_behavior": "返回PB最高的20只股票",
                    "required_fields": ["ts_code", "name", "pb", "close"],
                    "order_by": "pb DESC"
                },
                {
                    "query": "破净股排名",
                    "expected_behavior": "返回PB<1的股票，按PB升序",
                    "required_fields": ["ts_code", "name", "pb", "close"],
                    "order_by": "pb ASC",
                    "filter": "pb < 1 AND pb > 0"
                }
            ],
            "pattern": r"(?:PB|市净率|破净)(?:最高|最低|排名|前).*?(\d+)?|.*前(\d+).*(?:PB|市净率)",
            "sql_template": "SELECT ts_code, close, pb FROM tu_daily_basic WHERE trade_date = :trade_date AND pb > 0 ORDER BY pb {order} LIMIT :limit"
        },
        
        {
            "name": "净利润排名",
            "description": "净利润排名查询",
            "test_cases": [
                {
                    "query": "利润排名前20",
                    "expected_behavior": "返回最新报告期净利润最高的20家公司",
                    "required_fields": ["ts_code", "name", "net_profit", "end_date"],
                    "order_by": "net_profit DESC"
                },
                {
                    "query": "净利润最高的前10",
                    "expected_behavior": "返回最新报告期净利润最高的10家公司",
                    "required_fields": ["ts_code", "name", "net_profit", "end_date"],
                    "order_by": "net_profit DESC"
                },
                {
                    "query": "亏损最多的前10",
                    "expected_behavior": "返回净利润为负且亏损最多的10家公司",
                    "required_fields": ["ts_code", "name", "net_profit", "end_date"],
                    "order_by": "net_profit ASC",
                    "filter": "net_profit < 0"
                }
            ],
            "pattern": r"(?:净利润|利润|盈利|亏损)(?:最高|最多|排名|前).*?(\d+)?",
            "sql_template": """
                SELECT DISTINCT ts_code, net_profit, end_date 
                FROM tu_income 
                WHERE end_date = (SELECT MAX(end_date) FROM tu_income WHERE ts_code = t.ts_code)
                ORDER BY net_profit {order} 
                LIMIT :limit
            """
        },
        
        {
            "name": "营收排名",
            "description": "营业收入排名查询",
            "test_cases": [
                {
                    "query": "营收排名前10",
                    "expected_behavior": "返回最新报告期营收最高的10家公司",
                    "required_fields": ["ts_code", "name", "revenue", "end_date"],
                    "order_by": "revenue DESC"
                },
                {
                    "query": "营业收入最高的前20",
                    "expected_behavior": "返回最新报告期营收最高的20家公司",
                    "required_fields": ["ts_code", "name", "revenue", "end_date"],
                    "order_by": "revenue DESC"
                }
            ],
            "pattern": r"(?:营收|营业收入|收入)(?:最高|排名|前).*?(\d+)?",
            "sql_template": """
                SELECT DISTINCT ts_code, revenue, end_date 
                FROM tu_income 
                WHERE end_date = (SELECT MAX(end_date) FROM tu_income WHERE ts_code = t.ts_code)
                ORDER BY revenue DESC 
                LIMIT :limit
            """
        },
        
        {
            "name": "ROE排名",
            "description": "净资产收益率排名查询",
            "test_cases": [
                {
                    "query": "ROE排名前10",
                    "expected_behavior": "返回ROE最高的10家公司",
                    "required_fields": ["ts_code", "name", "roe", "end_date"],
                    "order_by": "roe DESC"
                },
                {
                    "query": "净资产收益率最高的前20",
                    "expected_behavior": "返回ROE最高的20家公司",
                    "required_fields": ["ts_code", "name", "roe", "end_date"],
                    "order_by": "roe DESC"
                }
            ],
            "pattern": r"(?:ROE|净资产收益率)(?:最高|排名|前).*?(\d+)?",
            "sql_template": """
                SELECT DISTINCT ts_code, roe, end_date 
                FROM tu_fina_indicator 
                WHERE end_date = (SELECT MAX(end_date) FROM tu_fina_indicator WHERE ts_code = t.ts_code)
                AND roe > 0
                ORDER BY roe DESC 
                LIMIT :limit
            """
        }
    ]
    
    # 输出设计结果
    for template in new_templates:
        print(f"\n### {template['name']} - {template['description']}")
        print("-" * 60)
        print(f"正则模式: {template['pattern']}")
        print(f"\n测试用例:")
        for i, case in enumerate(template['test_cases'], 1):
            print(f"\n{i}. {case['query']}")
            print(f"   期望: {case['expected_behavior']}")
            if 'filter' in case:
                print(f"   过滤: {case['filter']}")
    
    # 保存为JSON文件
    with open('new_ranking_templates_design.json', 'w', encoding='utf-8') as f:
        json.dump(new_templates, f, ensure_ascii=False, indent=2)
    
    print("\n\n设计已保存到: new_ranking_templates_design.json")


def test_error_cases():
    """设计错误测试用例"""
    
    print("\n\n" + "=" * 80)
    print("错误测试用例设计")
    print("=" * 80)
    
    error_cases = [
        {
            "category": "无效指标",
            "cases": [
                {
                    "query": "XYZ排名前10",
                    "expected": "无法识别的排名指标"
                },
                {
                    "query": "随机指标最高的前10",
                    "expected": "不支持的查询类型"
                }
            ]
        },
        {
            "category": "参数异常",
            "cases": [
                {
                    "query": "PE排名前0",
                    "expected": "限制数量必须大于0"
                },
                {
                    "query": "PB排名前1000",
                    "expected": "限制数量不能超过100"
                }
            ]
        },
        {
            "category": "日期异常",
            "cases": [
                {
                    "query": "2099年PE排名",
                    "expected": "日期超出数据范围"
                },
                {
                    "query": "明天的利润排名",
                    "expected": "不能查询未来数据"
                }
            ]
        }
    ]
    
    for category in error_cases:
        print(f"\n{category['category']}:")
        for case in category['cases']:
            print(f"  - {case['query']}")
            print(f"    预期错误: {case['expected']}")


def generate_implementation_guide():
    """生成实现指南"""
    
    print("\n\n" + "=" * 80)
    print("实现指南")
    print("=" * 80)
    
    steps = [
        {
            "step": 1,
            "title": "更新query_templates.py",
            "tasks": [
                "在QueryTemplateLibrary的__init__方法中添加新模板",
                "设置type=TemplateType.RANKING",
                "设置route_type='SQL_ONLY'",
                "配置required_fields和optional_fields",
                "设置default_params"
            ]
        },
        {
            "step": 2,
            "title": "更新sql_templates.py",
            "tasks": [
                "添加PE_RANKING SQL模板",
                "添加PB_RANKING SQL模板",
                "添加PROFIT_RANKING SQL模板",
                "添加REVENUE_RANKING SQL模板",
                "添加ROE_RANKING SQL模板",
                "添加对应的format_方法"
            ]
        },
        {
            "step": 3,
            "title": "更新sql_agent.py的_try_quick_query",
            "tasks": [
                "在elif分支中添加新模板处理",
                "实现参数提取逻辑",
                "调用对应的SQL模板",
                "格式化返回结果"
            ]
        },
        {
            "step": 4,
            "title": "测试验证",
            "tasks": [
                "运行test_new_ranking_templates.py",
                "验证快速路径触发",
                "检查响应时间（目标<2秒）",
                "验证结果准确性"
            ]
        }
    ]
    
    for step_info in steps:
        print(f"\n步骤{step_info['step']}: {step_info['title']}")
        print("-" * 40)
        for task in step_info['tasks']:
            print(f"  ✓ {task}")


if __name__ == "__main__":
    # 设计新模板
    design_new_ranking_templates()
    
    # 设计错误用例
    test_error_cases()
    
    # 生成实现指南
    generate_implementation_guide()