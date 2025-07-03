"""
中文数字转换单元测试

快速验证中文数字转换功能是否正常工作
"""

from utils.chinese_number_converter import (
    chinese_to_arabic,
    extract_number_from_chinese,
    extract_limit_from_query,
    normalize_quantity_expression
)

def test_chinese_to_arabic():
    """测试中文数字到阿拉伯数字的转换"""
    test_cases = [
        ("一", 1),
        ("二", 2),
        ("三", 3),
        ("五", 5),
        ("十", 10),
        ("十五", 15),
        ("二十", 20),
        ("二十三", 23),
        ("三十", 30),
        ("五十", 50),
        ("一百", 100),
        ("一百零五", 105),
        ("两百", 200),
        ("三千", 3000),
        ("五千五百", 5500),
        ("一万", 10000),
    ]
    
    print("=== 测试 chinese_to_arabic ===")
    passed = 0
    for chinese, expected in test_cases:
        result = chinese_to_arabic(chinese)
        status = "✓" if result == expected else "✗"
        if result == expected:
            passed += 1
        print(f"{status} '{chinese}' -> {result} (期望: {expected})")
    
    print(f"\n通过率: {passed}/{len(test_cases)} ({passed/len(test_cases)*100:.1f}%)\n")

def test_extract_limit_from_query():
    """测试从查询中提取数量限制"""
    test_cases = [
        # 中文数字
        ("前十", 10),
        ("前二十", 20),
        ("前三十", 30),
        ("前五十", 50),
        ("前一百", 100),
        
        # TOP格式
        ("TOP十", 10),
        ("TOP二十", 20),
        ("top五", 5),
        
        # 混合查询
        ("涨幅前十", 10),
        ("跌幅前二十", 20),
        ("市值排名前五十", 50),
        ("成交额TOP十", 10),
        
        # 阿拉伯数字
        ("前10", 10),
        ("TOP20", 20),
        ("前100名", 100),
        
        # 默认值测试
        ("涨幅排名", 10),  # 使用默认值
        ("市值排行", 10),  # 使用默认值
    ]
    
    print("=== 测试 extract_limit_from_query ===")
    passed = 0
    for query, expected in test_cases:
        result = extract_limit_from_query(query, default=10)
        status = "✓" if result == expected else "✗"
        if result == expected:
            passed += 1
        print(f"{status} '{query}' -> {result} (期望: {expected})")
    
    print(f"\n通过率: {passed}/{len(test_cases)} ({passed/len(test_cases)*100:.1f}%)\n")

def test_normalize_quantity_expression():
    """测试查询语句规范化"""
    test_cases = [
        ("涨幅前十", "涨幅前10"),
        ("跌幅前二十", "跌幅前20"),
        ("市值排名前五十", "市值排名前50"),
        ("TOP十的股票", "TOP10的股票"),
        ("前一百名公司", "前100名公司"),
        ("第三个交易日", "第3个交易日"),
        ("前三十只股票", "前30只股票"),
        
        # 已经是阿拉伯数字的不变
        ("前10名", "前10名"),
        ("TOP20", "TOP20"),
    ]
    
    print("=== 测试 normalize_quantity_expression ===")
    passed = 0
    for query, expected in test_cases:
        result = normalize_quantity_expression(query)
        status = "✓" if result == expected else "✗"
        if result == expected:
            passed += 1
        print(f"{status} '{query}' -> '{result}' (期望: '{expected}')")
    
    print(f"\n通过率: {passed}/{len(test_cases)} ({passed/len(test_cases)*100:.1f}%)\n")

def run_all_tests():
    """运行所有测试"""
    print("\n" + "="*60)
    print("中文数字转换单元测试")
    print("="*60 + "\n")
    
    test_chinese_to_arabic()
    test_extract_limit_from_query()
    test_normalize_quantity_expression()
    
    print("="*60)
    print("测试完成！")
    print("="*60)

if __name__ == "__main__":
    run_all_tests()