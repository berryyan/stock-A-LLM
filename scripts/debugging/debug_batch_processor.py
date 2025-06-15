"""
调试批处理问题
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from rag.document_processor import DocumentProcessor
from pathlib import Path
import json


def check_progress_file():
    """检查进度文件"""
    print("1. 检查进度文件")
    print("-" * 60)
    
    progress_file = Path("data/processing_progress.json")
    if progress_file.exists():
        print(f"✓ 进度文件存在: {progress_file}")
        with open(progress_file, 'r', encoding='utf-8') as f:
            progress = json.load(f)
        print(f"\n内容:")
        print(json.dumps(progress, ensure_ascii=False, indent=2))
    else:
        print("✗ 进度文件不存在")
    
    # 检查其他可能的进度文件
    other_files = [
        "data/processing_log.json",
        "data/error_log.json"
    ]
    
    print("\n其他相关文件:")
    for file in other_files:
        if Path(file).exists():
            print(f"  ✓ {file}")
        else:
            print(f"  ✗ {file}")


def test_simple_process():
    """测试简单处理"""
    print("\n\n2. 测试简单处理")
    print("-" * 60)
    
    processor = DocumentProcessor()
    
    # 直接调用处理，不检查进度
    print("直接处理年度报告...")
    
    try:
        success_count = processor.batch_process_announcements(
            start_date='20250422',
            end_date='20250422',
            title_keywords=['年度报告'],
            batch_size=2,  # 只处理2个
            sleep_range=(5, 10)
        )
        
        print(f"\n处理结果: {success_count} 个文档")
        
    except Exception as e:
        print(f"处理错误: {e}")


def clear_progress():
    """清除进度记录"""
    print("\n\n3. 清除进度记录")
    print("-" * 60)
    
    files_to_clear = [
        "data/processing_progress.json",
        "data/processing_log.json",
        "data/error_log.json"
    ]
    
    for file in files_to_clear:
        file_path = Path(file)
        if file_path.exists():
            response = input(f"删除 {file}? (y/n): ")
            if response.lower() == 'y':
                file_path.unlink()
                print(f"✓ 已删除")
            else:
                print(f"✗ 跳过")


def check_safe_processor():
    """检查SafeBatchProcessor的状态"""
    print("\n\n4. 检查SafeBatchProcessor状态")
    print("-" * 60)
    
    try:
        from tests.safe_batch_processor import SafeBatchProcessor
        processor = SafeBatchProcessor()
        
        print(f"已处理的公告数: {len(processor.processed_ids)}")
        print(f"错误记录数: {len(processor.errors)}")
        
        if processor.processed_ids:
            print("\n已处理的公告ID (前10个):")
            for i, ann_id in enumerate(list(processor.processed_ids)[:10]):
                print(f"  {i+1}. {ann_id}")
        
    except Exception as e:
        print(f"无法加载SafeBatchProcessor: {e}")


def direct_process_test():
    """直接处理测试（绕过所有检查）"""
    print("\n\n5. 直接处理测试")
    print("-" * 60)
    
    from database.mysql_connector import MySQLConnector
    
    mysql = MySQLConnector()
    
    # 查询一条年度报告
    query = """
    SELECT ts_code, name, title, url, ann_date
    FROM tu_anns_d
    WHERE ann_date = '20250422'
    AND title LIKE '%年度报告%'
    AND url NOT IN (
        SELECT url FROM tu_anns_d 
        WHERE ts_code IN ('300607.SZ', '300290.SZ', '300207.SZ')
    )
    LIMIT 1
    """
    
    results = mysql.execute_query(query)
    
    if results:
        ann = results[0]
        print(f"找到未处理的公告:")
        print(f"  股票: {ann['ts_code']} - {ann['name']}")
        print(f"  标题: {ann['title']}")
        print(f"  URL: {ann['url']}")
        
        response = input("\n是否处理这个公告? (y/n): ")
        if response.lower() == 'y':
            processor = DocumentProcessor()
            try:
                docs = processor.process_announcement(ann)
                if docs:
                    print(f"✓ 处理成功，生成 {len(docs)} 个文档")
                    
                    # 存储到Milvus
                    if processor.store_documents_to_milvus(docs):
                        print("✓ 存储成功")
                    else:
                        print("✗ 存储失败")
                else:
                    print("✗ 处理失败")
            except Exception as e:
                print(f"✗ 错误: {e}")
    else:
        print("没有找到未处理的年度报告")


def main():
    """主函数"""
    print("批处理调试工具")
    print("=" * 60)
    
    # 检查进度文件
    check_progress_file()
    
    # 检查SafeBatchProcessor
    check_safe_processor()
    
    # 询问用户
    print("\n\n选项:")
    print("1. 清除所有进度记录")
    print("2. 测试简单处理")
    print("3. 直接处理单个公告")
    print("0. 退出")
    
    choice = input("\n选择: ")
    
    if choice == '1':
        clear_progress()
    elif choice == '2':
        test_simple_process()
    elif choice == '3':
        direct_process_test()


if __name__ == "__main__":
    main()
