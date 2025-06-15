"""
初次运行测试脚本 - 安全参数设置
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from rag.document_processor import DocumentProcessor
import time
from datetime import datetime


def print_section(title):
    """打印分节标题"""
    print("\n" + "=" * 80)
    print(f" {title} ")
    print("=" * 80)


def check_pdf_cache():
    """检查PDF缓存目录"""
    cache_dir = "data/pdfs/cache"
    if os.path.exists(cache_dir):
        files = os.listdir(cache_dir)
        print(f"\nPDF缓存目录中有 {len(files)} 个文件:")
        for f in files[:5]:  # 只显示前5个
            print(f"  - {f}")
        if len(files) > 5:
            print(f"  ... 还有 {len(files)-5} 个文件")
    else:
        print("\nPDF缓存目录不存在")


def run_minimal_test():
    """运行最小化测试"""
    processor = DocumentProcessor()
    
    # 测试配置
    config = {
        'start_date': '20250422',
        'end_date': '20250422',
        'title_keywords': ['年度报告'],  # 只搜索年度报告
        'batch_size': 1,  # 每次只处理1个
        'sleep_range': (20, 30),  # 安全的睡眠时间：20-30秒
        'ts_codes': None  # 不限制股票代码
    }
    
    print_section("初次运行测试配置")
    print(f"日期范围: {config['start_date']} 至 {config['end_date']}")
    print(f"标题关键词: {config['title_keywords']}")
    print(f"批次大小: {config['batch_size']} (每次处理1个公告)")
    print(f"休眠时间: {config['sleep_range'][0]}-{config['sleep_range'][1]}秒")
    print("\n⚠️  注意: 为避免被封IP，每个公告之间会随机休眠20-30秒")
    
    # 用户确认
    input("\n按Enter键开始测试（按Ctrl+C可随时中断）...")
    
    try:
        print_section("开始处理公告")
        start_time = time.time()
        
        success_count = processor.batch_process_announcements(
            start_date=config['start_date'],
            end_date=config['end_date'],
            title_keywords=config['title_keywords'],
            batch_size=config['batch_size'],
            sleep_range=config['sleep_range'],
            ts_codes=config['ts_codes']
        )
        
        elapsed_time = time.time() - start_time
        
        print_section("处理完成")
        print(f"成功处理: {success_count} 个公告")
        print(f"总耗时: {elapsed_time:.1f} 秒 ({elapsed_time/60:.1f} 分钟)")
        
        # 检查缓存
        check_pdf_cache()
        
        return success_count > 0
        
    except KeyboardInterrupt:
        print("\n\n用户中断处理")
        check_pdf_cache()
        return False
    except Exception as e:
        print(f"\n\n处理出错: {e}")
        check_pdf_cache()
        return False


def test_search_functionality():
    """测试搜索功能"""
    print_section("测试向量搜索功能")
    
    processor = DocumentProcessor()
    
    # 测试查询
    test_queries = [
        "公司2024年的营业收入是多少",
        "主营业务有哪些",
        "净利润同比增长情况"
    ]
    
    for query in test_queries:
        print(f"\n查询: '{query}'")
        try:
            results = processor.search_similar_documents(
                query=query,
                top_k=3
            )
            
            if results and len(results) > 0:
                # 检查结果格式
                if isinstance(results[0], list) and len(results[0]) > 0:
                    # Milvus返回的是嵌套列表格式
                    actual_results = results[0]
                else:
                    actual_results = results
                
                print(f"找到 {len(actual_results)} 个相关文档片段")
                
                for i, result in enumerate(actual_results[:2]):  # 只显示前2个
                    # 处理不同的结果格式
                    if hasattr(result, 'entity'):
                        # Milvus的Hit对象
                        entity = result.entity
                        score = result.score if hasattr(result, 'score') else result.distance
                        text = entity.get('text', '')[:150]
                        company = entity.get('company_name', 'N/A')
                        title = entity.get('title', 'N/A')
                    else:
                        # 字典格式
                        score = result.get('score', result.get('distance', 'N/A'))
                        text = result.get('text', '')[:150]
                        company = result.get('company_name', 'N/A')
                        title = result.get('title', 'N/A')
                    
                    print(f"\n  结果 {i+1}:")
                    print(f"    相似度分数: {score}")
                    print(f"    公司: {company}")
                    print(f"    文档: {title}")
                    print(f"    内容: {text}...")
            else:
                print("  未找到相关文档")
                
        except Exception as e:
            print(f"  搜索出错: {e}")


def show_next_steps():
    """显示下一步建议"""
    print_section("测试完成 - 下一步建议")
    
    print("\n✅ 如果测试成功，你可以：")
    print("\n1. 逐步增加处理量:")
    print("   - 第二次: batch_size=3, sleep_range=(15, 25)")
    print("   - 第三次: batch_size=5, sleep_range=(10, 20)")
    print("   - 稳定后: batch_size=10, sleep_range=(10, 15)")
    
    print("\n2. 扩大日期范围:")
    print("   - 一周数据: start_date='20250415', end_date='20250422'")
    print("   - 一个月数据: start_date='20250401', end_date='20250430'")
    
    print("\n3. 添加更多文档类型:")
    print("   - title_keywords=['年度报告', '半年度报告', '季度报告']")
    print("   - title_keywords=['业绩预告', '业绩快报']")
    
    print("\n4. 监控和优化:")
    print("   - 检查日志: logs/document_processor.log")
    print("   - 监控下载成功率")
    print("   - 如果失败率高，增加sleep_range")
    
    print("\n⚠️  重要提醒:")
    print("   - 避免在工作时间(9:00-17:00)大量下载")
    print("   - 建议在晚上或凌晨进行批量处理")
    print("   - 每处理100个公告，休息10-20分钟")
    print("   - 如果被封IP，通常24小时后会解封")


def main():
    """主流程"""
    print("股票公告RAG系统 - 初次运行测试")
    print(f"当前时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 运行最小化测试
    if run_minimal_test():
        # 如果成功，测试搜索功能
        input("\n\n处理成功! 按Enter测试搜索功能...")
        test_search_functionality()
    
    # 显示下一步建议
    show_next_steps()


if __name__ == "__main__":
    main()
