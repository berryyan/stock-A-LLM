"""
测试数据库Schema中文映射系统
验证动态读取数据库字段注释和中文查询解析功能
Created: 2025-06-28
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.schema_cache_manager import SchemaCacheManager
from utils.chinese_query_parser import ChineseQueryParser
import json

def test_schema_cache_manager():
    """测试Schema缓存管理器"""
    print("=" * 80)
    print("测试 Schema 缓存管理器")
    print("=" * 80)
    
    # 创建管理器实例
    manager = SchemaCacheManager()
    
    # 1. 获取统计信息
    stats = manager.get_stats()
    print(f"\n缓存统计信息:")
    print(f"- 表数量: {stats['table_count']}")
    print(f"- 字段总数: {stats['field_count']}")
    print(f"- 中文字段名数量: {stats['chinese_field_count']}")
    
    # 2. 获取所有表信息
    print(f"\n数据库表列表:")
    tables = manager.get_all_tables()
    for i, table in enumerate(tables[:5]):  # 只显示前5个
        print(f"{i+1}. {table['table_name']} - {table['table_cn']} "
              f"(记录数: {table['record_count']:,}, 字段数: {table['field_count']})")
    
    # 3. 测试表名映射
    print(f"\n测试表名映射:")
    test_table_names = ['股票日线行情', '利润表', '资金流向']
    for cn_name in test_table_names:
        en_name = manager.get_table_by_chinese(cn_name)
        print(f"- {cn_name} -> {en_name}")
    
    # 4. 测试字段映射
    print(f"\n测试字段映射:")
    test_fields = ['股票代码', '收盘价', '净利润', '总资产']
    for field_cn in test_fields:
        field_info = manager.get_field_by_chinese(field_cn)
        if field_info:
            print(f"- {field_cn} -> {field_info['table']}.{field_info['field']}")
            if field_info['info'].get('unit'):
                print(f"  单位: {field_info['info']['unit']}")
    
    # 5. 搜索字段
    print(f"\n搜索包含'市'的字段:")
    search_results = manager.search_fields('市')
    for result in search_results[:5]:  # 只显示前5个
        print(f"- {result['table']}.{result['field']} ({result['field_cn']})")
    
    # 6. 查看特定表的结构
    print(f"\n查看 tu_daily_detail 表结构:")
    table_info = manager.get_table_info('tu_daily_detail')
    if table_info:
        print(f"表名: {table_info['table_cn']}")
        print(f"描述: {table_info['description']}")
        print(f"字段列表:")
        for field_name, field_info in list(table_info['fields'].items())[:10]:  # 只显示前10个字段
            unit = f"({field_info['unit']})" if field_info.get('unit') else ""
            print(f"  - {field_name}: {field_info['cn']} {unit} [{field_info['type']}]")

def test_chinese_query_parser():
    """测试中文查询解析器"""
    print("\n" + "=" * 80)
    print("测试中文查询解析器")
    print("=" * 80)
    
    parser = ChineseQueryParser()
    
    # 测试查询列表
    test_queries = [
        "查询贵州茅台最新股价",
        "茅台最近30天的收盘价和成交量",
        "市值最大的前10只股票",
        "贵州茅台的财务状况",
        "600519的资金流向",
        "茅台的市盈率是多少",
        "涨幅最大的5只股票",
        "分析平安银行的净资产收益率"
    ]
    
    for i, query in enumerate(test_queries):
        print(f"\n{i+1}. 查询: {query}")
        print("-" * 40)
        
        # 解析查询
        result = parser.parse_query(query)
        
        # 显示解析结果
        print(f"查询类型: {result.get('query_type', '未识别')}")
        
        if result.get('tables'):
            print(f"查询表: {result['tables']}")
        
        if result.get('fields'):
            print(f"查询字段: {result['fields']}")
        
        if result.get('conditions'):
            print(f"查询条件: {result['conditions']}")
        
        if result.get('order_by'):
            print(f"排序: {result['order_by']} {result.get('order_dir', 'DESC')}")
        
        if result.get('limit'):
            print(f"限制: {result['limit']}条")
        
        # 生成SQL
        sql = parser.generate_sql(result)
        if sql:
            print(f"生成SQL: {sql}")
        
        # 显示解析说明
        if result.get('explain'):
            print("解析过程:")
            for step in result['explain']:
                print(f"  - {step}")

def test_sql_generation():
    """测试SQL生成功能"""
    print("\n" + "=" * 80)
    print("测试SQL生成功能")
    print("=" * 80)
    
    manager = SchemaCacheManager()
    
    # 测试查询意图
    test_intents = [
        {
            'tables': ['股票日线行情表'],
            'fields': ['收盘价', '成交量'],
            'conditions': {'股票代码': '600519.SH', 'days': 30}
        },
        {
            'tables': ['利润表'],
            'fields': ['营业收入', '净利润'],
            'conditions': {'股票代码': '000001.SZ'},
            'order_by': '报告期',
            'order_dir': 'DESC',
            'limit': 4
        },
        {
            'tables': ['资金流向表'],
            'fields': ['特大单买入金额', '特大单卖出金额', '净流入金额'],
            'conditions': {'股票代码': '600519.SH', 'days': 5}
        }
    ]
    
    for i, intent in enumerate(test_intents):
        print(f"\n{i+1}. 查询意图: {json.dumps(intent, ensure_ascii=False, indent=2)}")
        sql, mapping = manager.generate_sql_with_chinese(intent)
        if sql:
            print(f"生成的SQL:\n{sql}")
            print(f"字段映射: {mapping}")

def main():
    """主测试函数"""
    print("开始测试数据库Schema中文映射系统\n")
    
    try:
        # 测试Schema缓存管理器
        test_schema_cache_manager()
        
        # 测试中文查询解析器
        test_chinese_query_parser()
        
        # 测试SQL生成
        test_sql_generation()
        
        print("\n" + "=" * 80)
        print("测试完成！")
        print("=" * 80)
        
    except Exception as e:
        print(f"\n错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()