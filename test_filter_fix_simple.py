#!/usr/bin/env python3
"""
简化的过滤表达式修复测试
只测试核心转换逻辑，避免依赖问题
"""
import sys
import os
import re
from typing import Dict, List, Any, Optional

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def convert_entity_to_stock_code(entity: str) -> Optional[str]:
    """将实体（公司名称或代码）转换为标准股票代码"""
    if not entity:
        return None
    
    # 如果已经是股票代码格式，直接返回
    if re.match(r'^\d{6}\.[SH|SZ]{2}$', entity):
        return entity
    
    # 扩展公司名称映射
    company_mapping = {
        '茅台': '600519.SH',
        '贵州茅台': '600519.SH',
        '五粮液': '000858.SZ',
        '宁德时代': '300750.SZ',
        '比亚迪': '002594.SZ',
        '招商银行': '600036.SH',
        '平安银行': '000001.SZ',
        '万科A': '000002.SZ',
        '万科': '000002.SZ',
        '中国平安': '601318.SH',
        '工商银行': '601398.SH',
        '建设银行': '601939.SH',
        '农业银行': '601288.SH',
        '中国银行': '601988.SH',
        '中石油': '601857.SH',
        '中石化': '600028.SH',
        '腾讯控股': '700.HK',  # 港股，但保留映射
        '阿里巴巴': '9988.HK'   # 港股，但保留映射
    }
    
    # 精确匹配
    if entity in company_mapping:
        return company_mapping[entity]
    
    # 模糊匹配（包含关系）
    for name, code in company_mapping.items():
        if name in entity or entity in name:
            return code
    
    # 如果没有匹配到，返回原始实体（可能是其他股票代码）
    return entity

def build_rag_filters(routing: Dict) -> Dict[str, Any]:
    """构建RAG查询过滤器（修复后的版本）"""
    filters = {}
    
    # 添加实体过滤
    if routing.get('entities'):
        # 确保转换为股票代码而不是公司名称
        entities = routing['entities']
        if isinstance(entities, list):
            # 转换所有实体为股票代码
            converted_entities = []
            for entity in entities:
                converted_entity = convert_entity_to_stock_code(entity)
                if converted_entity:
                    converted_entities.append(converted_entity)
            if converted_entities:
                if len(converted_entities) == 1:
                    filters['ts_code'] = converted_entities[0]
                else:
                    filters['ts_code'] = converted_entities
        else:
            # 单个实体
            converted_entity = convert_entity_to_stock_code(entities)
            if converted_entity:
                filters['ts_code'] = converted_entity
    
    # 添加时间过滤
    if routing.get('time_range'):
        time_range = routing['time_range']
        if time_range.startswith('recent_'):
            # 最近N天（简化处理）
            days = int(time_range.split('_')[1].replace('d', ''))
            filters['ann_date'] = {'start': '20250601', 'end': '20250624'}  # 简化的日期范围
        elif 'Q' in time_range:
            # 季度
            year = time_range[:4]
            quarter = time_range[-1]
            quarter_ranges = {
                '1': {'start': f"{year}0101", 'end': f"{year}0331"},
                '2': {'start': f"{year}0401", 'end': f"{year}0630"},
                '3': {'start': f"{year}0701", 'end': f"{year}0930"},
                '4': {'start': f"{year}1001", 'end': f"{year}1231"}
            }
            filters['ann_date'] = quarter_ranges.get(quarter, {})
        else:
            # 年度 - 确保正确的日期格式
            # 清理可能的中文字符
            clean_time_range = time_range.replace('年', '').replace('月', '').replace('日', '')
            if clean_time_range.isdigit() and len(clean_time_range) == 4:
                filters['ann_date'] = {'start': f"{clean_time_range}0101", 'end': f"{clean_time_range}1231"}
    
    return filters

def build_filter_expr(filters: Optional[Dict[str, Any]]) -> Optional[str]:
    """构建Milvus过滤表达式"""
    if not filters:
        return None
    
    conditions = []
    
    # 股票代码过滤
    if 'ts_code' in filters:
        if isinstance(filters['ts_code'], list):
            codes = ', '.join([f'"{code}"' for code in filters['ts_code']])
            conditions.append(f"ts_code in [{codes}]")
        else:
            conditions.append(f'ts_code == "{filters["ts_code"]}"')
    
    # 日期过滤
    if 'ann_date' in filters:
        date = filters['ann_date']
        if isinstance(date, dict):
            if 'start' in date:
                conditions.append(f'ann_date >= "{date["start"]}"')
            if 'end' in date:
                conditions.append(f'ann_date <= "{date["end"]}"')
        else:
            conditions.append(f'ann_date == "{date}"')
    
    return ' and '.join(conditions) if conditions else None

def test_entity_conversion():
    """测试实体转换功能"""
    print("🧪 测试实体转换功能")
    print("=" * 60)
    
    test_cases = [
        {"input": "贵州茅台", "expected": "600519.SH"},
        {"input": "茅台", "expected": "600519.SH"},
        {"input": "平安银行", "expected": "000001.SZ"},
        {"input": "600519.SH", "expected": "600519.SH"},  # 已经是股票代码
        {"input": "工商银行", "expected": "601398.SH"},
        {"input": "", "expected": None},
        {"input": "未知公司", "expected": "未知公司"}  # 未匹配的应该返回原值
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        input_entity = test_case["input"]
        expected = test_case["expected"]
        
        result = convert_entity_to_stock_code(input_entity)
        
        if result == expected:
            print(f"✅ 测试 {i}: '{input_entity}' -> '{result}' (正确)")
        else:
            print(f"❌ 测试 {i}: '{input_entity}' -> '{result}' (期望: '{expected}')")

def test_filter_building():
    """测试过滤器构建功能"""
    print("\n🧪 测试过滤器构建功能")
    print("=" * 60)
    
    test_cases = [
        {
            "name": "贵州茅台2024年查询（公司名称）",
            "routing": {
                "entities": ["贵州茅台"],  # 输入公司名称
                "time_range": "2024"
            },
            "expected_ts_code": "600519.SH",
            "expected_date_format": "20240101"
        },
        {
            "name": "股票代码直接查询",
            "routing": {
                "entities": ["600519.SH"],  # 输入股票代码
                "time_range": "2024"
            },
            "expected_ts_code": "600519.SH",
            "expected_date_format": "20240101"
        },
        {
            "name": "多个实体查询",
            "routing": {
                "entities": ["贵州茅台", "平安银行"],
                "time_range": "2024"
            },
            "expected_ts_code": ["600519.SH", "000001.SZ"],
            "expected_date_format": "20240101"
        },
        {
            "name": "年度查询（中文日期清理）",
            "routing": {
                "entities": ["贵州茅台"],
                "time_range": "2024年"  # 包含中文字符
            },
            "expected_ts_code": "600519.SH",
            "expected_date_format": "20240101"
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n测试 {i}: {test_case['name']}")
        print(f"输入路由: {test_case['routing']}")
        
        # 构建过滤器
        filters = build_rag_filters(test_case['routing'])
        print(f"生成的过滤器: {filters}")
        
        # 验证股票代码
        if 'ts_code' in filters:
            actual_code = filters['ts_code']
            expected_code = test_case['expected_ts_code']
            
            if actual_code == expected_code:
                print(f"✅ 股票代码正确: {actual_code}")
            else:
                print(f"❌ 股票代码错误: 期望{expected_code}, 实际{actual_code}")
        else:
            print("⚠️  未生成股票代码过滤器")
        
        # 验证日期格式
        if 'ann_date' in filters:
            date_filter = filters['ann_date']
            if isinstance(date_filter, dict):
                start_date = date_filter.get('start', '')
                end_date = date_filter.get('end', '')
                
                # 检查日期格式是否为YYYYMMDD
                if start_date.isdigit() and len(start_date) == 8:
                    print(f"✅ 开始日期格式正确: {start_date}")
                else:
                    print(f"❌ 开始日期格式错误: {start_date}")
                
                if end_date.isdigit() and len(end_date) == 8:
                    print(f"✅ 结束日期格式正确: {end_date}")
                else:
                    print(f"❌ 结束日期格式错误: {end_date}")
        
        print("-" * 40)

def test_filter_expression_generation():
    """测试过滤表达式生成"""
    print("\n🧪 测试过滤表达式生成")
    print("=" * 60)
    
    # 模拟原来出问题的场景
    routing = {
        "entities": ["贵州茅台"],  # 输入公司名称（问题所在）
        "time_range": "2024"
    }
    
    print(f"问题场景路由: {routing}")
    
    # 使用修复后的函数
    filters = build_rag_filters(routing)
    print(f"修复后的过滤器: {filters}")
    
    # 生成过滤表达式
    filter_expr = build_filter_expr(filters)
    print(f"生成的过滤表达式: {filter_expr}")
    
    # 检查是否修复了关键问题
    if filter_expr:
        if '600519.SH' in filter_expr:
            print("✅ 股票代码正确转换: 贵州茅台 -> 600519.SH")
        else:
            print("❌ 股票代码转换失败")
        
        if '20240101' in filter_expr and '20241231' in filter_expr:
            print("✅ 日期格式正确: 使用YYYYMMDD格式")
        else:
            print("❌ 日期格式可能错误")
        
        if '年' not in filter_expr and '月' not in filter_expr:
            print("✅ 无中文字符: 日期格式清理成功")
        else:
            print("❌ 仍包含中文字符")
    
    print("\n对比原来的错误表达式:")
    print("❌ 错误: ts_code == \"贵州茅台\" and ann_date >= \"2024年0101\" and ann_date <= \"2024年1231\"")
    print(f"✅ 修复: {filter_expr}")

def main():
    """主测试函数"""
    print("🔧 RAG过滤表达式修复测试")
    print("目标: 修复公司名称和日期格式问题")
    print("=" * 80)
    
    # 测试实体转换
    test_entity_conversion()
    
    # 测试过滤器构建
    test_filter_building()
    
    # 测试过滤表达式生成
    test_filter_expression_generation()
    
    print("\n📋 测试总结:")
    print("✅ 关键修复点:")
    print("   1. 公司名称自动转换为股票代码")
    print("   2. 日期格式清理，去除中文字符") 
    print("   3. 生成正确的Milvus过滤表达式")
    print("\n💡 如果所有测试通过，RAG查询应该能找到相关文档了")

if __name__ == "__main__":
    main()