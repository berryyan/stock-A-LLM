# optimize_api_system.py
# 优化API系统性能和修复已知问题

import os
import json

def analyze_issues():
    """分析当前系统存在的问题"""
    print("=== 系统问题分析 ===\n")
    
    issues = [
        {
            "问题": "查询超时",
            "原因": "某些查询（如'600519今天的成交量'）处理时间过长",
            "解决方案": "增加超时时间，优化查询逻辑"
        },
        {
            "问题": "SQL Agent返回英文",
            "原因": "LLM默认使用英文回复",
            "解决方案": "在提示词中明确要求使用中文"
        },
        {
            "问题": "缺少财务数据表",
            "原因": "数据库中没有财务报表相关的表",
            "解决方案": "使用RAG查询财务信息，或添加财务数据表"
        },
        {
            "问题": "stock_basic表不存在",
            "原因": "表名可能是tu_stock_basic或其他",
            "解决方案": "检查实际表名并更新配置"
        }
    ]
    
    for i, issue in enumerate(issues, 1):
        print(f"{i}. {issue['问题']}")
        print(f"   原因: {issue['原因']}")
        print(f"   解决: {issue['解决方案']}\n")

def create_config_patch():
    """创建配置补丁"""
    
    config_patch = '''# patch_config.py
# 修复配置问题

import json

def update_api_config():
    """更新API配置"""
    
    # 更新超时设置
    config_updates = {
        "request_timeout": 60,  # 增加到60秒
        "sql_timeout": 30,
        "rag_timeout": 45,
        "hybrid_timeout": 90
    }
    
    # 保存配置
    with open("config/api_config.json", "w", encoding="utf-8") as f:
        json.dump(config_updates, f, indent=2, ensure_ascii=False)
    
    print("✅ 配置已更新")

def update_sql_agent_prompt():
    """更新SQL Agent的提示词"""
    
    file_path = "agents/sql_agent.py"
    
    # 读取文件
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 查找并更新提示词
    if "You are a SQL expert" in content:
        content = content.replace(
            "You are a SQL expert",
            "你是一个SQL专家，请用中文回答所有问题"
        )
    
    # 添加中文回复要求
    if "Final Answer:" in content:
        content = content.replace(
            "Final Answer:",
            "Final Answer (请用中文):"
        )
    
    # 写回文件
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ SQL Agent提示词已更新")

if __name__ == "__main__":
    update_api_config()
    update_sql_agent_prompt()
'''
    
    with open("patch_config.py", "w", encoding="utf-8") as f:
        f.write(config_patch)
    
    print("已创建 patch_config.py")

def create_check_tables_script():
    """创建检查数据库表的脚本"""
    
    check_script = '''# check_database_tables.py
# 检查数据库中的所有表

from database.mysql_connector import MySQLConnector
from config.settings import settings

def check_tables():
    """检查所有可用的表"""
    
    print("=== 检查MySQL数据库表 ===\\n")
    
    # 连接数据库
    db = MySQLConnector(settings)
    
    try:
        # 获取所有表名
        query = "SHOW TABLES"
        result = db.execute_query(query)
        
        tables = [row[0] for row in result]
        
        print(f"找到 {len(tables)} 个表:\\n")
        
        # 分类显示
        categories = {
            "股票基础": [],
            "交易数据": [],
            "财务数据": [],
            "公告数据": [],
            "其他": []
        }
        
        for table in sorted(tables):
            if "stock" in table or "basic" in table:
                categories["股票基础"].append(table)
            elif "daily" in table or "trade" in table or "price" in table:
                categories["交易数据"].append(table)
            elif "finance" in table or "income" in table or "balance" in table:
                categories["财务数据"].append(table)
            elif "ann" in table or "notice" in table:
                categories["公告数据"].append(table)
            else:
                categories["其他"].append(table)
        
        # 显示分类结果
        for category, table_list in categories.items():
            if table_list:
                print(f"{category} ({len(table_list)}个):")
                for table in table_list:
                    print(f"  - {table}")
                print()
        
        # 检查特定表的结构
        important_tables = [
            "tu_daily_detail",
            "tu_stock_basic",
            "stock_basic",
            "tu_anns_d"
        ]
        
        print("\\n=== 重要表结构 ===\\n")
        
        for table in important_tables:
            if table in tables:
                print(f"表 {table}:")
                query = f"DESCRIBE {table}"
                result = db.execute_query(query)
                for row in result[:5]:  # 只显示前5个字段
                    print(f"  - {row[0]}: {row[1]}")
                print()
            else:
                print(f"❌ 表 {table} 不存在\\n")
                
    except Exception as e:
        print(f"错误: {str(e)}")
    finally:
        db.close()

if __name__ == "__main__":
    check_tables()
'''
    
    with open("check_database_tables.py", "w", encoding="utf-8") as f:
        f.write(check_script)
    
    print("已创建 check_database_tables.py")

def create_optimized_test():
    """创建优化后的测试脚本"""
    
    test_script = '''# optimized_test.py
# 优化后的API测试

import requests
import json
import time

BASE_URL = "http://localhost:8000"

def test_with_timeout(query, timeout=60):
    """带超时控制的测试"""
    
    print(f"\\n查询: {query}")
    print(f"超时设置: {timeout}秒")
    
    try:
        start = time.time()
        response = requests.post(
            f"{BASE_URL}/query",
            json={"question": query},
            timeout=timeout
        )
        elapsed = time.time() - start
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                print(f"✅ 成功 (耗时: {elapsed:.2f}秒)")
                print(f"   类型: {result.get('query_type')}")
                answer = result.get('answer', '')
                if answer:
                    print(f"   回答: {answer[:100]}...")
            else:
                print(f"❌ 失败: {result.get('error')}")
        else:
            print(f"❌ HTTP {response.status_code}")
            
    except requests.exceptions.Timeout:
        print(f"⏱️  超时 (>{timeout}秒)")
    except Exception as e:
        print(f"❌ 错误: {str(e)}")

def main():
    print("=== 优化后的API测试 ===")
    
    # 测试不同类型的查询
    test_cases = [
        ("简单查询", "茅台股价", 30),
        ("带股票代码", "600519.SH最新价格", 30),
        ("成交量查询", "贵州茅台今天成交量", 45),
        ("复杂查询", "茅台最近5天平均价格", 60),
        ("RAG查询", "茅台2024年第一季度营收", 60),
    ]
    
    for desc, query, timeout in test_cases:
        print(f"\\n--- {desc} ---")
        test_with_timeout(query, timeout)
        time.sleep(2)  # 避免过于频繁
    
    print("\\n测试完成!")

if __name__ == "__main__":
    main()
'''
    
    with open("optimized_test.py", "w", encoding="utf-8") as f:
        f.write(test_script)
    
    print("已创建 optimized_test.py")

def create_system_status():
    """创建系统状态总结"""
    
    status_doc = '''# 系统当前状态总结

## ✅ 已完成功能

### 1. 基础架构
- MySQL连接正常（10.0.0.77）
- Milvus连接正常（83,074个文档）
- API服务运行正常（端口8000）
- 所有Agent初始化成功

### 2. 查询功能
- ✅ SQL查询：可以查询股价等数据
- ✅ RAG查询：可以搜索公告内容
- ✅ 混合查询：可以结合两种数据源

### 3. API端点
- GET /health - 健康检查
- GET /status - 系统状态
- POST /query - 通用查询
- GET /suggestions - 查询建议
- GET /reports/recent - 最近报告

## ⚠️ 已知问题

### 1. 性能问题
- 某些查询超时（如成交量查询）
- 需要优化查询逻辑

### 2. 数据问题
- 缺少财务数据表
- stock_basic表名不正确
- 需要更多数据源

### 3. 语言问题
- SQL Agent有时返回英文
- 需要统一使用中文

## 🚀 下一步计划

### 短期优化
1. 修复超时问题
2. 添加中文提示词
3. 检查并更新表名

### 功能扩展
1. 添加更多查询模板
2. 实现批量查询
3. 添加数据可视化

### 长期目标
1. 开发Web界面
2. 添加实时数据
3. 集成更多数据源
'''
    
    with open("system_status.md", "w", encoding="utf-8") as f:
        f.write(status_doc)
    
    print("已创建 system_status.md")

if __name__ == "__main__":
    print("API系统优化工具")
    print("="*60)
    
    # 分析问题
    analyze_issues()
    
    # 创建修复脚本
    create_config_patch()
    create_check_tables_script()
    create_optimized_test()
    create_system_status()
    
    print("\n" + "="*60)
    print("\n建议的操作步骤:")
    print("1. 检查数据库表: python check_database_tables.py")
    print("2. 应用配置补丁: python patch_config.py")
    print("3. 重启API服务")
    print("4. 运行优化测试: python optimized_test.py")
    print("\n查看系统状态: system_status.md")
