"""
最终批处理脚本 - 处理股票公告
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.mysql_connector import MySQLConnector
from database.milvus_connector import MilvusConnector
from models.embedding_model import EmbeddingModel
from rag.document_processor import DocumentProcessor
import time
from datetime import datetime
import json


def test_system():
    """测试系统各组件"""
    print("系统测试")
    print("=" * 60)
    
    # 测试MySQL
    print("\n1. 测试MySQL连接...")
    try:
        mysql = MySQLConnector()
        test_query = "SELECT COUNT(*) as count FROM tu_anns_d WHERE ann_date = '20250422'"
        result = mysql.execute_query(test_query)
        count = result[0]['count'] if result else 0
        print(f"✓ MySQL连接正常，20250422有 {count} 条公告")
    except Exception as e:
        print(f"✗ MySQL错误: {e}")
        return False
    
    # 测试Milvus
    print("\n2. 测试Milvus连接...")
    try:
        milvus = MilvusConnector()
        stats = milvus.get_collection_stats()
        print(f"✓ Milvus连接正常，当前有 {stats['row_count']} 条数据")
    except Exception as e:
        print(f"✗ Milvus错误: {e}")
        return False
    
    # 测试嵌入模型
    print("\n3. 测试嵌入模型...")
    try:
        model = EmbeddingModel()
        test_text = "测试文本"
        embedding = model.encode(test_text)
        print(f"✓ 嵌入模型正常，向量维度: {len(embedding) if hasattr(embedding, '__len__') else 'N/A'}")
    except Exception as e:
        print(f"✗ 嵌入模型错误: {e}")
        return False
    
    print("\n✓ 所有组件测试通过!")
    return True


def search_announcements():
    """搜索已存储的公告"""
    print("\n搜索已存储的公告")
    print("=" * 60)
    
    processor = DocumentProcessor()
    
    # 测试查询
    queries = [
        "2024年度营业收入情况",
        "公司主营业务发展",
        "净利润同比增长",
        "研发投入情况"
    ]
    
    for query in queries:
        print(f"\n查询: '{query}'")
        try:
            # 使用document_processor的搜索功能
            results = processor.search_similar_documents(
                query=query,
                top_k=3
            )
            
            if results and len(results) > 0:
                # 处理搜索结果
                if isinstance(results[0], list):
                    hits = results[0]
                else:
                    hits = results
                
                for i, hit in enumerate(hits[:2]):
                    print(f"\n  结果 {i+1}:")
                    
                    # 获取entity数据
                    if hasattr(hit, 'entity'):
                        entity = hit.entity
                        distance = hit.distance
                        
                        # 使用属性访问
                        text = entity.text if hasattr(entity, 'text') else 'N/A'
                        title = entity.title if hasattr(entity, 'title') else 'N/A'
                        ts_code = entity.ts_code if hasattr(entity, 'ts_code') else 'N/A'
                        
                        print(f"    相似度: {distance:.4f}")
                        print(f"    股票: {ts_code}")
                        print(f"    标题: {title}")
                        print(f"    内容: {text[:150]}...")
                    else:
                        print(f"    数据: {hit}")
            else:
                print("  没有找到相关结果")
                
        except Exception as e:
            print(f"  搜索错误: {e}")


def process_new_announcements():
    """处理新公告"""
    print("\n\n处理新公告")
    print("=" * 60)
    
    processor = DocumentProcessor()
    
    # 配置
    config = {
        'start_date': '20250422',
        'end_date': '20250422',
        'title_keywords': ['年度报告'],
        'batch_size': 3,  # 小批量测试
        'sleep_range': (15, 25)  # 安全的休眠时间
    }
    
    print("处理配置:")
    for k, v in config.items():
        print(f"  {k}: {v}")
    
    # 用户确认
    response = input("\n是否开始处理? (y/n): ")
    if response.lower() != 'y':
        print("已取消")
        return
    
    try:
        # 开始处理
        start_time = time.time()
        
        success_count = processor.batch_process_announcements(
            start_date=config['start_date'],
            end_date=config['end_date'],
            title_keywords=config['title_keywords'],
            batch_size=config['batch_size'],
            sleep_range=config['sleep_range']
        )
        
        elapsed = time.time() - start_time
        
        print(f"\n处理完成!")
        print(f"  成功: {success_count} 个公告")
        print(f"  耗时: {elapsed:.1f} 秒 ({elapsed/60:.1f} 分钟)")
        
    except KeyboardInterrupt:
        print("\n\n用户中断处理")
    except Exception as e:
        print(f"\n处理错误: {e}")


def show_statistics():
    """显示统计信息"""
    print("\n\n系统统计信息")
    print("=" * 60)
    
    # MySQL统计
    mysql = MySQLConnector()
    
    # 各日期的公告数量
    query = """
    SELECT ann_date, COUNT(*) as count
    FROM tu_anns_d
    WHERE ann_date >= '20250415'
    GROUP BY ann_date
    ORDER BY ann_date DESC
    LIMIT 10
    """
    
    results = mysql.execute_query(query)
    print("\n最近的公告统计:")
    for r in results:
        print(f"  {r['ann_date']}: {r['count']} 条")
    
    # Milvus统计
    milvus = MilvusConnector()
    stats = milvus.get_collection_stats()
    print(f"\nMilvus向量库:")
    print(f"  总文档数: {stats['row_count']}")
    
    # 已处理的PDF
    pdf_dir = "data/pdfs/cache"
    if os.path.exists(pdf_dir):
        pdf_count = len([f for f in os.listdir(pdf_dir) if f.endswith('.pdf')])
        print(f"\n已下载PDF: {pdf_count} 个")


def main():
    """主程序"""
    print("股票公告RAG系统")
    print(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # 系统测试
    if not test_system():
        print("\n系统测试失败，请检查配置")
        return
    
    # 显示统计
    show_statistics()
    
    while True:
        print("\n\n请选择操作:")
        print("1. 搜索已有公告")
        print("2. 处理新公告")
        print("3. 显示统计信息")
        print("0. 退出")
        
        choice = input("\n选择 (0-3): ")
        
        if choice == '1':
            search_announcements()
        elif choice == '2':
            process_new_announcements()
        elif choice == '3':
            show_statistics()
        elif choice == '0':
            print("\n再见!")
            break
        else:
            print("无效选择")


if __name__ == "__main__":
    main()
