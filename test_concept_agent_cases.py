#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Concept Agent 测试用例
包含三种输入类型的测试
"""

# 测试用例定义
TEST_CASES = [
    {
        "id": "TC001",
        "type": "keyword",
        "input": "概念股分析：充电宝概念股有哪些？",
        "expected_input_type": "concept_query",
        "description": "简单概念查询"
    },
    {
        "id": "TC002", 
        "type": "concept_query",
        "input": "概念股分析：固态电池概念相关板块有哪些个股现在可以重点关注？",
        "expected_input_type": "concept_query",
        "description": "复杂概念查询"
    },
    {
        "id": "TC003",
        "type": "news",
        "input": """概念股分析：新闻"国家部委及地方政府近期密集出台固态电池鼓励政策。今年2月份，工信部等8部门印发《新型储能制造业高质量发展行动方案》，明确支持储能用固态电池发展，提出加快长寿命、高安全性固态电池技术攻关，推动锂电池和钠电池固态化发展。4月份工信部印发的《2025年工业和信息化标准工作要点》提出建立全固态电池标准体系，以加速其产业化进程。北京、上海等地更将固态电池纳入当地产业规划，凸显其在新能源汽车、储能、消费电子、低空经济等领域的应用潜力。"分析有哪些相关股票和板块有投资机会。""",
        "expected_input_type": "news",
        "description": "新闻文本分析"
    }
]


def test_input_processing():
    """测试输入处理功能"""
    print("=== Concept Agent 输入处理测试 ===\n")
    
    # 模拟输入处理器
    def detect_input_type(text: str) -> str:
        # 去掉前缀
        text = text.replace("概念股分析：", "").strip()
        
        # 长文本判定为新闻
        if len(text) > 100:
            return "news"
        
        # 包含概念股等关键词
        if any(kw in text for kw in ["概念股", "概念", "板块"]):
            return "concept_query"
        
        return "keyword"
    
    # 测试每个用例
    for case in TEST_CASES:
        print(f"测试用例 {case['id']}: {case['description']}")
        print(f"输入长度: {len(case['input'])} 字符")
        
        detected_type = detect_input_type(case['input'])
        print(f"检测类型: {detected_type}")
        print(f"预期类型: {case['expected_input_type']}")
        print(f"结果: {'✓ 通过' if detected_type == case['expected_input_type'] else '✗ 失败'}")
        print("-" * 80)
        print()


def test_concept_matching():
    """测试概念匹配功能"""
    print("\n=== 概念匹配测试 ===\n")
    
    # 从测试用例中提取关键词
    keywords = {
        "TC001": ["充电宝"],
        "TC002": ["固态电池"],
        "TC003": ["固态电池", "储能", "新能源汽车", "锂电池", "钠电池"]
    }
    
    # 模拟系统概念列表（基于实际查询结果）
    system_concepts = [
        "固态电池",      # 同花顺：886032.TI
        "锂电池概念",    # 同花顺：885710.TI
        "锂电池",        # 东财：BK0574.DC
        "储能",          # 需要确认
        "新能源汽车",    # 需要确认
        "充电桩",        # 需要确认
        "燃料电池",      # 同花顺：885775.TI，东财：BK0682.DC
        "钠离子电池",    # 同花顺：885928.TI
        "动力电池回收",  # 同花顺：885944.TI
    ]
    
    print("系统概念列表（示例）:")
    for concept in system_concepts:
        print(f"  - {concept}")
    print()
    
    # 测试每个用例的概念匹配
    for case_id, case_keywords in keywords.items():
        print(f"\n{case_id} 关键词匹配:")
        print(f"提取的关键词: {case_keywords}")
        
        # 简单的匹配逻辑
        matched = []
        for keyword in case_keywords:
            for concept in system_concepts:
                if keyword in concept or concept in keyword:
                    if concept not in matched:
                        matched.append(concept)
        
        print(f"匹配到的概念: {matched}")


def test_expected_flow():
    """测试预期的处理流程"""
    print("\n=== 预期处理流程 ===\n")
    
    for case in TEST_CASES:
        print(f"测试用例 {case['id']}:")
        print(f"1. 用户输入: {case['input'][:50]}...")
        print(f"2. 输入类型识别: {case['expected_input_type']}")
        print(f"3. LLM概念扩展:")
        
        if case['id'] == 'TC001':
            print("   - 可能匹配: 移动电源、充电设备、消费电子等")
        elif case['id'] == 'TC002':
            print("   - 可能匹配: 固态电池、锂电池、新能源汽车、储能等")
        elif case['id'] == 'TC003':
            print("   - 从新闻提取: 固态电池、储能、新能源汽车、锂电池、钠电池")
            print("   - 扩展相关: 电池材料、正极材料、负极材料、电解液等")
        
        print("4. 获取成分股（目前只有同花顺有完整数据）")
        print("5. 数据采集（资金流向、技术指标等）")
        print("6. 三维评分计算")
        print("7. 生成分析报告")
        print("-" * 80)
        print()


if __name__ == "__main__":
    test_input_processing()
    test_concept_matching()
    test_expected_flow()