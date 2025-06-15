"""
简单测试脚本 - 逐步调试
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.mysql_connector import MySQLConnector
from sqlalchemy import text


def test_basic_connection():
    """测试基本连接"""
    print("1. 测试数据库连接...")
    try:
        mysql = MySQLConnector()
        if mysql.test_connection():
            print("✓ 数据库连接成功")
            return mysql
        else:
            print("✗ 数据库连接失败")
            return None
    except Exception as e:
        print(f"✗ 连接错误: {e}")
        return None


def test_simple_query(mysql):
    """测试简单查询"""
    print("\n2. 测试简单查询...")
    try:
        # 不使用LIKE的简单查询
        query = """
        SELECT ts_code, name, title, url, ann_date
        FROM tu_anns_d
        WHERE ann_date = '20250422'
        LIMIT 5
        """
        
        results = mysql.execute_query(query)
        print(f"✓ 查询成功，返回 {len(results)} 条记录")
        
        for i, r in enumerate(results):
            print(f"\n记录 {i+1}:")
            print(f"  股票代码: {r['ts_code']}")
            print(f"  公司名称: {r['name']}")
            print(f"  标题: {r['title']}")
            
        return True
    except Exception as e:
        print(f"✗ 查询错误: {e}")
        return False


def test_like_query(mysql):
    """测试LIKE查询"""
    print("\n3. 测试LIKE查询...")
    try:
        # 测试不同的LIKE查询方法
        
        # 方法1: 使用参数化查询
        print("\n方法1: 参数化查询")
        query1 = """
        SELECT ts_code, name, title
        FROM tu_anns_d
        WHERE ann_date = :ann_date
        AND title LIKE :title_pattern
        LIMIT 3
        """
        params1 = {
            'ann_date': '20250422',
            'title_pattern': '%年度报告%'
        }
        results1 = mysql.execute_query(query1, params1)
        print(f"✓ 参数化查询成功，返回 {len(results1)} 条记录")
        
        # 方法2: 直接拼接（使用双百分号）
        print("\n方法2: 直接拼接查询")
        query2 = """
        SELECT ts_code, name, title
        FROM tu_anns_d
        WHERE ann_date = '20250422'
        AND title LIKE '%%年度报告%%'
        LIMIT 3
        """
        results2 = mysql.execute_query(query2)
        print(f"✓ 直接查询成功，返回 {len(results2)} 条记录")
        
        # 显示结果
        if results1:
            print("\n找到的年度报告:")
            for r in results1:
                print(f"  {r['ts_code']} - {r['name']} - {r['title']}")
        
        return True
    except Exception as e:
        print(f"✗ LIKE查询错误: {e}")
        return False


def test_announcement_url():
    """测试公告URL格式"""
    print("\n4. 测试公告URL格式...")
    mysql = MySQLConnector()
    
    try:
        # 获取一条有URL的公告
        query = """
        SELECT ts_code, name, title, url, ann_date
        FROM tu_anns_d
        WHERE ann_date = '20250422'
        AND url IS NOT NULL
        AND url != ''
        LIMIT 1
        """
        
        results = mysql.execute_query(query)
        if not results:
            print("✗ 没有找到带URL的公告")
            return False
        
        announcement = results[0]
        print(f"✓ 找到公告:")
        print(f"  股票: {announcement['ts_code']} - {announcement['name']}")
        print(f"  标题: {announcement['title']}")
        print(f"  URL: {announcement['url']}")
        
        # 尝试解析URL
        from rag.document_processor import DocumentProcessor
        processor = DocumentProcessor()
        
        try:
            stock_code, ann_id, ann_time = processor.extract_params_from_url(announcement['url'])
            print(f"\n✓ URL解析成功:")
            print(f"  股票代码: {stock_code}")
            print(f"  公告ID: {ann_id}")
            print(f"  公告时间: {ann_time}")
            
            # 构造PDF URL
            pdf_url = processor.construct_pdf_url(stock_code, ann_id, ann_time)
            print(f"\n✓ PDF URL: {pdf_url}")
            
            return True
        except Exception as e:
            print(f"\n✗ URL解析失败: {e}")
            return False
            
    except Exception as e:
        print(f"✗ 测试错误: {e}")
        return False


def main():
    """主测试流程"""
    print("开始简单测试流程")
    print("=" * 60)
    
    # 测试1: 连接
    mysql = test_basic_connection()
    if not mysql:
        print("\n请检查数据库配置后重试")
        return
    
    # 测试2: 简单查询
    if not test_simple_query(mysql):
        print("\n基本查询失败，请检查表结构")
        return
    
    # 测试3: LIKE查询
    test_like_query(mysql)
    
    # 测试4: URL解析
    test_announcement_url()
    
    print("\n" + "=" * 60)
    print("测试完成!")


if __name__ == "__main__":
    main()
