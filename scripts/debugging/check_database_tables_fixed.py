# check_database_tables_fixed.py
# 修复版 - 检查数据库中的所有表

import pymysql
from config.settings import settings
import pandas as pd

def check_tables_direct():
    """直接使用pymysql检查数据库表"""
    
    print("=== 检查MySQL数据库表 ===\n")
    
    # 数据库连接参数
    db_config = {
        'host': settings.MYSQL_HOST,
        'port': settings.MYSQL_PORT,
        'user': settings.MYSQL_USER,
        'password': settings.MYSQL_PASSWORD,
        'database': settings.MYSQL_DATABASE,
        'charset': 'utf8mb4'
    }
    
    try:
        # 建立连接
        connection = pymysql.connect(**db_config)
        cursor = connection.cursor()
        
        print(f"✅ 已连接到数据库: {db_config['host']}:{db_config['port']}/{db_config['database']}\n")
        
        # 获取所有表名
        cursor.execute("SHOW TABLES")
        tables = [row[0] for row in cursor.fetchall()]
        
        print(f"找到 {len(tables)} 个表\n")
        
        # 分类显示
        categories = {
            "股票基础信息": [],
            "交易数据": [],
            "财务数据": [],
            "公告数据": [],
            "资金流向": [],
            "问答互动": [],
            "其他": []
        }
        
        # 分类规则
        for table in sorted(tables):
            if "stock" in table or "basic" in table:
                categories["股票基础信息"].append(table)
            elif "daily" in table or "trade" in table or "price" in table:
                categories["交易数据"].append(table)
            elif "finance" in table or "income" in table or "balance" in table or "cashflow" in table:
                categories["财务数据"].append(table)
            elif "ann" in table or "notice" in table:
                categories["公告数据"].append(table)
            elif "moneyflow" in table:
                categories["资金流向"].append(table)
            elif "irm" in table or "qa" in table:
                categories["问答互动"].append(table)
            else:
                categories["其他"].append(table)
        
        # 显示分类结果
        for category, table_list in categories.items():
            if table_list:
                print(f"【{category}】({len(table_list)}个表):")
                for table in table_list:
                    # 获取表的行数
                    cursor.execute(f"SELECT COUNT(*) FROM {table}")
                    count = cursor.fetchone()[0]
                    print(f"  - {table:<30} (记录数: {count:,})")
                print()
        
        # 检查重要表的详细结构
        print("\n" + "="*60)
        print("重要表结构详情")
        print("="*60 + "\n")
        
        important_tables = {
            "tu_daily_detail": "日线行情数据",
            "tu_anns_d": "公告数据",
            "tu_stock_basic": "股票基础信息",
            "stock_basic": "股票基础信息(备选)"
        }
        
        for table, description in important_tables.items():
            if table in tables:
                print(f"\n📊 表名: {table} - {description}")
                print("-" * 50)
                
                # 获取表结构
                cursor.execute(f"DESCRIBE {table}")
                columns = cursor.fetchall()
                
                print(f"字段数: {len(columns)}")
                print("\n主要字段:")
                for i, (field, type_, null, key, default, extra) in enumerate(columns[:10]):
                    key_info = f" [{key}]" if key else ""
                    print(f"  {i+1:2d}. {field:<20} {type_:<20}{key_info}")
                
                if len(columns) > 10:
                    print(f"  ... 还有 {len(columns)-10} 个字段")
                
                # 显示样例数据
                print("\n样例数据 (前3行):")
                cursor.execute(f"SELECT * FROM {table} LIMIT 3")
                rows = cursor.fetchall()
                
                if rows:
                    # 获取列名
                    col_names = [desc[0] for desc in cursor.description]
                    
                    # 创建DataFrame显示
                    df = pd.DataFrame(rows, columns=col_names)
                    print(df.to_string(index=False, max_cols=5))
                else:
                    print("  (表为空)")
                    
            else:
                print(f"\n❌ 表 {table} 不存在")
        
        # 查找财务相关的表
        print("\n" + "="*60)
        print("查找财务数据相关表")
        print("="*60 + "\n")
        
        finance_keywords = ['finance', 'income', 'balance', 'cash', 'profit', 'revenue']
        finance_tables = []
        
        for table in tables:
            if any(keyword in table.lower() for keyword in finance_keywords):
                finance_tables.append(table)
        
        if finance_tables:
            print(f"找到 {len(finance_tables)} 个可能的财务数据表:")
            for table in finance_tables:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                count = cursor.fetchone()[0]
                print(f"  - {table} (记录数: {count:,})")
        else:
            print("❌ 未找到明显的财务数据表")
            print("\n建议：财务数据可能需要通过RAG从公告中提取")
        
        # 生成建议
        print("\n" + "="*60)
        print("优化建议")
        print("="*60 + "\n")
        
        suggestions = []
        
        # 检查stock_basic问题
        if "stock_basic" not in tables and "tu_stock_basic" in tables:
            suggestions.append("将代码中的 'stock_basic' 改为 'tu_stock_basic'")
        
        # 检查财务数据
        if not finance_tables:
            suggestions.append("考虑导入财务数据表，或加强RAG对财务公告的解析")
        
        # 检查数据完整性
        if "tu_daily_detail" in tables:
            cursor.execute("SELECT MAX(trade_date) FROM tu_daily_detail")
            latest_date = cursor.fetchone()[0]
            suggestions.append(f"股价数据最新日期: {latest_date}")
        
        for i, suggestion in enumerate(suggestions, 1):
            print(f"{i}. {suggestion}")
            
    except Exception as e:
        print(f"❌ 错误: {str(e)}")
        print(f"   类型: {type(e).__name__}")
        import traceback
        traceback.print_exc()
        
    finally:
        if 'connection' in locals():
            cursor.close()
            connection.close()
            print("\n✅ 数据库连接已关闭")

def save_table_info():
    """保存表信息到文件"""
    
    print("\n正在保存表信息到文件...")
    
    try:
        # 建立连接
        connection = pymysql.connect(
            host=settings.MYSQL_HOST,
            port=settings.MYSQL_PORT,
            user=settings.MYSQL_USER,
            password=settings.MYSQL_PASSWORD,
            database=settings.MYSQL_DATABASE,
            charset='utf8mb4'
        )
        cursor = connection.cursor()
        
        # 获取所有表信息
        cursor.execute("SHOW TABLES")
        tables = [row[0] for row in cursor.fetchall()]
        
        # 保存到文件
        with open("database_tables_info.txt", "w", encoding="utf-8") as f:
            f.write(f"数据库表信息\n")
            f.write(f"生成时间: {pd.Timestamp.now()}\n")
            f.write(f"数据库: {settings.MYSQL_DATABASE}\n")
            f.write(f"总表数: {len(tables)}\n")
            f.write("="*60 + "\n\n")
            
            for table in sorted(tables):
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                count = cursor.fetchone()[0]
                
                cursor.execute(f"DESCRIBE {table}")
                columns = cursor.fetchall()
                
                f.write(f"\n表名: {table}\n")
                f.write(f"记录数: {count:,}\n")
                f.write(f"字段数: {len(columns)}\n")
                f.write("字段列表:\n")
                
                for field, type_, null, key, default, extra in columns:
                    f.write(f"  - {field}: {type_}\n")
                
                f.write("-"*40 + "\n")
        
        print("✅ 表信息已保存到: database_tables_info.txt")
        
        cursor.close()
        connection.close()
        
    except Exception as e:
        print(f"❌ 保存失败: {str(e)}")

if __name__ == "__main__":
    check_tables_direct()
    save_table_info()
