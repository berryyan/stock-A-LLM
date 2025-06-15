"""
文档处理模块测试脚本
用于安全地测试文档处理功能
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import datetime
import json
from rag.document_processor import DocumentProcessor
from database.mysql_connector import MySQLConnector


def test_single_announcement():
    """测试单个公告处理"""
    print("=" * 80)
    print("测试1: 单个公告处理测试")
    print("=" * 80)
    
    # 初始化
    processor = DocumentProcessor()
    mysql_conn = MySQLConnector()
    
    # 查询一条测试公告
    test_date = '20250422'  # 测试日期
    # 使用双百分号避免格式化问题
    query = f"""
    SELECT ts_code, name, title, url, ann_date
    FROM tu_anns_d
    WHERE ann_date = '{test_date}'
    AND title LIKE '%%年度报告%%'
    LIMIT 1
    """
    
    print(f"查询日期: {test_date}")
    print("查询条件: 标题包含'年度报告'")
    
    results = mysql_conn.execute_query(query)
    
    if not results:
        print("未找到符合条件的公告，请更换日期或条件")
        return False
    
    announcement = results[0]
    print("\n找到测试公告:")
    print(f"股票代码: {announcement['ts_code']}")
    print(f"公司名称: {announcement['name']}")
    print(f"公告标题: {announcement['title']}")
    print(f"公告URL: {announcement['url']}")
    
    # 测试URL解析
    print("\n步骤1: 测试URL解析...")
    try:
        stock_code, announcement_id, announcement_time = processor.extract_params_from_url(
            announcement['url']
        )
        print(f"✓ URL解析成功:")
        print(f"  - 股票代码: {stock_code}")
        print(f"  - 公告ID: {announcement_id}")
        print(f"  - 公告时间: {announcement_time}")
    except Exception as e:
        print(f"✗ URL解析失败: {e}")
        return False
    
    # 测试PDF URL构造
    print("\n步骤2: 构造PDF下载链接...")
    pdf_url = processor.construct_pdf_url(stock_code, announcement_id, announcement_time)
    print(f"✓ PDF URL: {pdf_url}")
    
    # 测试单个公告处理
    print("\n步骤3: 处理公告（下载PDF并提取文本）...")
    print("注意: 首次下载可能需要10-30秒")
    
    try:
        documents = processor.process_announcement(announcement)
        if documents:
            print(f"✓ 公告处理成功!")
            print(f"  - 生成文档chunks数: {len(documents)}")
            print(f"  - 第一个chunk预览: {documents[0].page_content[:100]}...")
            
            # 安全地打印元数据，处理日期对象
            metadata_display = {}
            for k, v in documents[0].metadata.items():
                if hasattr(v, 'isoformat'):  # 处理日期对象
                    metadata_display[k] = v.isoformat()
                else:
                    metadata_display[k] = v
            
            print(f"  - 元数据: {json.dumps(metadata_display, ensure_ascii=False, indent=2)}")
            return True
        else:
            print("✗ 公告处理失败")
            return False
    except Exception as e:
        print(f"✗ 处理出错: {e}")
        return False


def test_batch_process_minimal():
    """最小批量测试 - 只处理1条公告"""
    print("\n" + "=" * 80)
    print("测试2: 最小批量处理测试（1条公告）")
    print("=" * 80)
    
    processor = DocumentProcessor()
    
    # 测试参数
    test_date = '20250422'
    
    print(f"测试参数:")
    print(f"- 日期: {test_date}")
    print(f"- 批次大小: 1")
    print(f"- 随机睡眠: 10-20秒")
    print(f"- 标题关键词: ['年度报告']")
    
    try:
        success_count = processor.batch_process_announcements(
            start_date=test_date,
            end_date=test_date,
            title_keywords=["年度报告"],
            batch_size=1,  # 每次只处理1个
            sleep_range=(10, 20)  # 安全的睡眠时间
        )
        
        print(f"\n✓ 批量处理完成，成功处理: {success_count} 条公告")
        return success_count > 0
    except Exception as e:
        print(f"\n✗ 批量处理失败: {e}")
        return False


def test_vector_search():
    """测试向量搜索功能"""
    print("\n" + "=" * 80)
    print("测试3: 向量搜索测试")
    print("=" * 80)
    
    processor = DocumentProcessor()
    
    # 测试查询
    test_queries = [
        "公司业绩情况如何",
        "年度营业收入",
        "主营业务发展"
    ]
    
    for query in test_queries:
        print(f"\n查询: '{query}'")
        try:
            results = processor.search_similar_documents(
                query=query,
                top_k=3
            )
            
            if results:
                print(f"找到 {len(results)} 个相关文档:")
                for i, result in enumerate(results):
                    print(f"\n结果 {i+1}:")
                    print(f"  相似度: {result.get('score', 'N/A')}")
                    print(f"  公司: {result.get('company_name', 'N/A')}")
                    print(f"  标题: {result.get('title', 'N/A')}")
                    print(f"  内容预览: {result.get('text', '')[:100]}...")
            else:
                print("未找到相关文档")
                
        except Exception as e:
            print(f"搜索失败: {e}")


def main():
    """主测试流程"""
    print("开始文档处理模块测试")
    print("建议按顺序执行测试，确保每步成功后再进行下一步")
    
    # 测试1: 单个公告
    input("\n按Enter开始测试1（单个公告处理）...")
    if not test_single_announcement():
        print("\n测试1失败，请检查问题后重试")
        return
    
    # 测试2: 最小批量处理
    input("\n测试1成功! 按Enter开始测试2（最小批量处理）...")
    if not test_batch_process_minimal():
        print("\n测试2失败，请检查问题后重试")
        return
    
    # 测试3: 向量搜索
    input("\n测试2成功! 按Enter开始测试3（向量搜索）...")
    test_vector_search()
    
    print("\n" + "=" * 80)
    print("所有测试完成!")
    print("=" * 80)
    print("\n下一步建议:")
    print("1. 检查 data/pdfs/cache 目录确认PDF是否成功下载")
    print("2. 检查日志文件 logs/document_processor.log")
    print("3. 如果一切正常，可以逐步增加批量处理的数量")
    print("4. 建议的安全参数:")
    print("   - batch_size: 5-10")
    print("   - sleep_range: (15, 30) # 15-30秒随机睡眠")
    print("   - 每处理50-100个公告休息5-10分钟")


if __name__ == "__main__":
    main()
