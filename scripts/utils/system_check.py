# 文件名: verify_system.py
# 验证系统所有组件

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def verify_imports():
    """验证所有导入"""
    print("1. 验证导入")
    print("-" * 40)
    
    imports = [
        ("langchain", "LangChain"),
        ("langchain_openai", "LangChain OpenAI"),
        ("fastapi", "FastAPI"),
        ("openai", "OpenAI"),
        ("pymilvus", "PyMilvus"),
    ]
    
    success = True
    for module, name in imports:
        try:
            exec(f"import {module}")
            print(f"✓ {name} 导入成功")
        except Exception as e:
            print(f"✗ {name} 导入失败: {e}")
            success = False
    
    return success

def verify_agents():
    """验证Agent模块"""
    print("\n2. 验证Agent模块")
    print("-" * 40)
    
    agents = [
        ("agents.sql_agent", "SQLAgent"),
        ("agents.rag_agent", "RAGAgent"),
        ("agents.hybrid_agent", "HybridAgent"),
    ]
    
    success = True
    for module_path, class_name in agents:
        try:
            exec(f"from {module_path} import {class_name}")
            print(f"✓ {class_name} 加载成功")
        except Exception as e:
            print(f"✗ {class_name} 加载失败: {e}")
            success = False
    
    return success

def verify_config():
    """验证配置"""
    print("\n3. 验证配置")
    print("-" * 40)
    
    try:
        from config.settings import settings
        
        checks = [
            ("MySQL Host", settings.MYSQL_HOST),
            ("MySQL Port", settings.MYSQL_PORT),
            ("Milvus Host", settings.MILVUS_HOST),
            ("Milvus Port", settings.MILVUS_PORT),
            ("DeepSeek API Key", "已配置" if settings.DEEPSEEK_API_KEY else "未配置"),
        ]
        
        for name, value in checks:
            print(f"  {name}: {value}")
        
        if not settings.DEEPSEEK_API_KEY:
            print("\n⚠️ 警告: DeepSeek API Key 未配置!")
            print("请在 .env 文件中添加: DEEPSEEK_API_KEY=your_key")
            return False
            
        return True
        
    except Exception as e:
        print(f"✗ 配置验证失败: {e}")
        return False

def verify_database_connections():
    """验证数据库连接"""
    print("\n4. 验证数据库连接")
    print("-" * 40)
    
    success = True
    
    # MySQL
    try:
        from database.mysql_connector import MySQLConnector
        mysql = MySQLConnector()
        if mysql.test_connection():
            print("✓ MySQL 连接成功")
        else:
            print("✗ MySQL 连接失败")
            success = False
    except Exception as e:
        print(f"✗ MySQL 测试失败: {e}")
        success = False
    
    # Milvus
    try:
        from database.milvus_connector import MilvusConnector
        milvus = MilvusConnector()
        stats = milvus.get_collection_stats()
        print(f"✓ Milvus 连接成功 (文档数: {stats.get('row_count', 0)})")
    except Exception as e:
        print(f"✗ Milvus 测试失败: {e}")
        success = False
    
    return success

def verify_api():
    """验证API模块"""
    print("\n5. 验证API模块")
    print("-" * 40)
    
    try:
        from api.main import app
        print("✓ FastAPI 应用加载成功")
        print("  可以运行: python -m api.main")
        return True
    except Exception as e:
        print(f"✗ API 模块加载失败: {e}")
        return False

def main():
    print("股票分析系统 - 组件验证")
    print("=" * 60)
    
    results = []
    
    # 运行所有验证
    results.append(("导入", verify_imports()))
    results.append(("Agent模块", verify_agents()))
    results.append(("配置", verify_config()))
    results.append(("数据库连接", verify_database_connections()))
    results.append(("API模块", verify_api()))
    
    # 总结
    print("\n" + "=" * 60)
    print("验证结果总结:")
    print("-" * 40)
    
    all_success = True
    for name, success in results:
        status = "✓ 通过" if success else "✗ 失败"
        print(f"{name}: {status}")
        if not success:
            all_success = False
    
    print("\n" + "=" * 60)
    
    if all_success:
        print("✅ 所有组件验证通过！")
        print("\n下一步:")
        print("1. 运行测试: python test_agents.py")
        print("2. 启动API: python -m api.main")
        print("3. 访问文档: http://localhost:8000/docs")
    else:
        print("❌ 部分组件验证失败，请检查错误信息")
        print("\n建议:")
        print("1. 检查错误信息并修复")
        print("2. 确保数据库服务正在运行")
        print("3. 确保DeepSeek API Key已配置")

if __name__ == "__main__":
    main()
