"""
批量处理公告管理器
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from rag.document_processor import DocumentProcessor
from database.mysql_connector import MySQLConnector
from database.milvus_connector import MilvusConnector
import time
from datetime import datetime, timedelta
import json
from pathlib import Path


class BatchProcessManager:
    """批量处理管理器"""
    
    def __init__(self):
        self.processor = DocumentProcessor()
        self.mysql = MySQLConnector()
        self.milvus = MilvusConnector()
        self.progress_file = Path("data/processing_progress.json")
        self.load_progress()
    
    def load_progress(self):
        """加载处理进度"""
        if self.progress_file.exists():
            with open(self.progress_file, 'r', encoding='utf-8') as f:
                self.progress = json.load(f)
        else:
            self.progress = {
                'processed_dates': [],
                'processed_types': {},
                'total_processed': 0,
                'last_update': None
            }
    
    def save_progress(self):
        """保存处理进度"""
        self.progress['last_update'] = datetime.now().isoformat()
        self.progress_file.parent.mkdir(exist_ok=True)
        with open(self.progress_file, 'w', encoding='utf-8') as f:
            json.dump(self.progress, f, ensure_ascii=False, indent=2)
    
    def get_announcement_stats(self, start_date, end_date):
        """获取公告统计信息"""
        query = f"""
        SELECT 
            ann_date,
            CASE 
                WHEN title LIKE '%年度报告%' THEN '年度报告'
                WHEN title LIKE '%第一季度%' OR title LIKE '%一季报%' THEN '一季度报告'
                WHEN title LIKE '%半年度报告%' OR title LIKE '%半年报%' THEN '半年度报告'
                WHEN title LIKE '%第三季度%' OR title LIKE '%三季报%' THEN '三季度报告'
                WHEN title LIKE '%业绩预告%' THEN '业绩预告'
                WHEN title LIKE '%业绩快报%' THEN '业绩快报'
                ELSE '其他'
            END as report_type,
            COUNT(*) as count
        FROM tu_anns_d
        WHERE ann_date BETWEEN '{start_date}' AND '{end_date}'
        GROUP BY ann_date, report_type
        ORDER BY ann_date DESC, count DESC
        """
        
        results = self.mysql.execute_query(query)
        
        # 汇总统计
        stats = {}
        for row in results:
            date = row['ann_date']
            if date not in stats:
                stats[date] = {}
            stats[date][row['report_type']] = row['count']
        
        return stats
    
    def process_by_date_and_type(self, date, report_types, batch_config):
        """处理指定日期和类型的公告"""
        date_str = date if isinstance(date, str) else date.strftime('%Y%m%d')
        
        print(f"\n处理 {date_str} 的 {', '.join(report_types)}")
        print("-" * 60)
        
        # 检查是否已处理
        key = f"{date_str}_{'-'.join(sorted(report_types))}"  # 排序以确保一致性
        
        # 调试信息
        print(f"检查键: {key}")
        print(f"已处理的键: {list(self.progress.get('processed_types', {}).keys())[:5]}...")
        
        if key in self.progress.get('processed_types', {}):
            processed_info = self.progress['processed_types'][key]
            print(f"✓ 已处理过，处理了 {processed_info['count']} 条，跳过")
            return 0
        
        # 获取关键词
        keywords_map = {
            '年度报告': ['年度报告'],
            '一季度报告': ['第一季度', '一季报'],
            '半年度报告': ['半年度报告', '半年报'],
            '三季度报告': ['第三季度', '三季报'],
            '业绩预告': ['业绩预告'],
            '业绩快报': ['业绩快报']
        }
        
        keywords = []
        for rt in report_types:
            keywords.extend(keywords_map.get(rt, [rt]))
        
        # 处理
        try:
            success_count = self.processor.batch_process_announcements(
                start_date=date_str,
                end_date=date_str,
                title_keywords=keywords,
                **batch_config
            )
            
            # 更新进度
            self.progress['processed_types'][key] = {
                'date': date_str,
                'types': report_types,
                'count': success_count,
                'timestamp': datetime.now().isoformat()
            }
            self.progress['total_processed'] += success_count
            self.save_progress()
            
            return success_count
            
        except Exception as e:
            print(f"✗ 处理失败: {e}")
            return 0
    
    def smart_batch_process(self, start_date, end_date, target_types=None):
        """智能批量处理"""
        print(f"\n智能批量处理")
        print(f"日期范围: {start_date} 至 {end_date}")
        print("=" * 60)
        
        # 获取统计信息
        stats = self.get_announcement_stats(start_date, end_date)
        
        # 显示统计
        print("\n公告分布统计:")
        total_by_type = {}
        for date, types in stats.items():
            print(f"\n{date}:")
            for report_type, count in types.items():
                print(f"  {report_type}: {count} 条")
                total_by_type[report_type] = total_by_type.get(report_type, 0) + count
        
        print(f"\n总计:")
        for report_type, count in sorted(total_by_type.items(), key=lambda x: x[1], reverse=True):
            print(f"  {report_type}: {count} 条")
        
        # 确认处理
        if not target_types:
            target_types = ['年度报告', '一季度报告', '业绩快报']
        
        print(f"\n计划处理类型: {target_types}")
        response = input("\n是否开始处理? (y/n): ")
        if response.lower() != 'y':
            print("已取消")
            return
        
        # 根据时间段选择处理策略
        current_hour = datetime.now().hour
        if 22 <= current_hour or current_hour < 6:
            # 夜间模式：快速处理
            batch_config = {
                'batch_size': 20,
                'sleep_range': (5, 10)
            }
            print("\n使用夜间模式（快速）")
        elif 9 <= current_hour <= 17:
            # 工作时间：保守处理
            batch_config = {
                'batch_size': 5,
                'sleep_range': (20, 30)
            }
            print("\n使用日间模式（保守）")
        else:
            # 其他时间：标准处理
            batch_config = {
                'batch_size': 10,
                'sleep_range': (10, 20)
            }
            print("\n使用标准模式")
        
        # 按日期处理
        total_processed = 0
        start_dt = datetime.strptime(start_date, '%Y%m%d')
        end_dt = datetime.strptime(end_date, '%Y%m%d')
        
        current_dt = start_dt
        while current_dt <= end_dt:
            date_str = current_dt.strftime('%Y%m%d')
            
            if date_str in stats:
                # 处理该日期的目标类型
                for report_type in target_types:
                    if report_type in stats[date_str] and stats[date_str][report_type] > 0:
                        count = self.process_by_date_and_type(
                            date_str,
                            [report_type],
                            batch_config
                        )
                        total_processed += count
                        
                        # 每处理完一个类型，休息一下
                        if count > 0:
                            print(f"休息30秒...")
                            time.sleep(30)
            
            current_dt += timedelta(days=1)
        
        print(f"\n" + "=" * 60)
        print(f"批量处理完成!")
        print(f"本次处理: {total_processed} 个文档")
        print(f"累计处理: {self.progress['total_processed']} 个文档")
    
    def show_progress(self):
        """显示处理进度"""
        print("\n处理进度统计")
        print("=" * 60)
        
        print(f"累计处理文档: {self.progress['total_processed']}")
        print(f"最后更新: {self.progress.get('last_update', 'N/A')}")
        
        # 获取Milvus统计
        milvus_stats = self.milvus.get_collection_stats()
        print(f"Milvus文档数: {milvus_stats['row_count']}")
        
        # 显示已处理的类型
        print("\n已处理的日期和类型:")
        processed = self.progress.get('processed_types', {})
        
        # 按日期排序
        sorted_items = sorted(processed.items(), 
                            key=lambda x: x[1]['date'], 
                            reverse=True)
        
        for key, info in sorted_items[:20]:  # 只显示最近20条
            print(f"  {info['date']} - {', '.join(info['types'])}: {info['count']} 条")


def main():
    """主函数"""
    manager = BatchProcessManager()
    
    while True:
        print("\n批量处理管理器")
        print("=" * 60)
        print("1. 查看处理进度")
        print("2. 处理指定日期范围")
        print("3. 处理最近一周")
        print("4. 处理最近一月")
        print("5. 夜间批量模式")
        print("0. 退出")
        
        choice = input("\n选择: ")
        
        if choice == '1':
            manager.show_progress()
        
        elif choice == '2':
            start = input("开始日期 (YYYYMMDD): ")
            end = input("结束日期 (YYYYMMDD): ")
            types = input("报告类型 (逗号分隔，空=默认): ").strip()
            types = [t.strip() for t in types.split(',')] if types else None
            manager.smart_batch_process(start, end, types)
        
        elif choice == '3':
            end_date = datetime.now()
            start_date = end_date - timedelta(days=7)
            manager.smart_batch_process(
                start_date.strftime('%Y%m%d'),
                end_date.strftime('%Y%m%d')
            )
        
        elif choice == '4':
            end_date = datetime.now()
            start_date = end_date - timedelta(days=30)
            manager.smart_batch_process(
                start_date.strftime('%Y%m%d'),
                end_date.strftime('%Y%m%d')
            )
        
        elif choice == '5':
            print("\n夜间批量模式（建议22:00后运行）")
            days = int(input("处理最近多少天? (默认30): ") or "30")
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            # 夜间快速配置
            manager.smart_batch_process(
                start_date.strftime('%Y%m%d'),
                end_date.strftime('%Y%m%d'),
                target_types=['年度报告', '一季度报告', '业绩快报', '业绩预告']
            )
        
        elif choice == '0':
            print("再见!")
            break
        
        else:
            print("无效选择")


if __name__ == "__main__":
    main()
