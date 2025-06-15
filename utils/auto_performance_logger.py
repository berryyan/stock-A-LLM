"""
自动性能记录器 V2 - 支持并发模式
"""
import json
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional
from collections import defaultdict
import statistics


class AutoPerformanceLogger:
    """自动批次性能记录器"""
    
    def __init__(self, log_dir: str = "data/performance_logs"):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        # 当前批次数据
        self.current_batch = None
        self.batch_records = []
        self.sleep_records = []
        
        # 批次日志文件
        self.batch_log_file = self.log_dir / "batch_performance.jsonl"
        
    def start_batch(self, task_type: str, start_date: str, end_date: str,
                    filter_enabled: bool, max_count: int, total_to_process: int,
                    concurrent_mode: bool = False, max_workers: int = 1):
        """开始新批次"""
        self.current_batch = {
            "batch_id": datetime.now().strftime("%Y%m%d_%H%M%S"),
            "start_time": time.time(),
            "task_type": task_type,
            "date_range": f"{start_date}-{end_date}",
            "filter_enabled": filter_enabled,
            "max_count": max_count,
            "total_to_process": total_to_process,
            "concurrent_mode": concurrent_mode,
            "max_workers": max_workers if concurrent_mode else 1
        }
        self.batch_records = []
        self.sleep_records = []
        
    def add_record(self, record: Dict):
        """添加处理记录"""
        if self.current_batch:
            self.batch_records.append(record)
            
    def record_sleep(self, sleep_time: float):
        """记录休眠时间"""
        if self.current_batch:
            self.sleep_records.append(sleep_time)
            
    def finish_batch(self):
        """完成批次并生成报告"""
        if not self.current_batch:
            return
            
        # 计算统计数据
        end_time = time.time()
        batch_duration = end_time - self.current_batch["start_time"]
        
        # 基础统计
        success_records = [r for r in self.batch_records if r.get("success")]
        failed_records = [r for r in self.batch_records if not r.get("success")]
        
        # 计算各阶段耗时
        download_times = []
        vectorize_times = []
        store_times = []
        total_times = []
        
        for record in success_records:
            if "stages" in record:
                stages = record["stages"]
                if "download" in stages:
                    download_times.append(stages["download"])
                if "vectorize" in stages:
                    vectorize_times.append(stages["vectorize"])
                if "store" in stages:
                    store_times.append(stages["store"])
            if "total_time" in record:
                total_times.append(record["total_time"])
                
        # 计算休眠时间
        total_sleep_time = sum(self.sleep_records)
        actual_work_time = batch_duration - total_sleep_time
        
        # 按文档类型统计
        doc_type_stats = defaultdict(lambda: {"count": 0, "times": []})
        for record in success_records:
            doc_type = record.get("doc_type", "未分类")
            doc_type_stats[doc_type]["count"] += 1
            if "total_time" in record:
                doc_type_stats[doc_type]["times"].append(record["total_time"])
                
        # 生成报告
        report = {
            "batch_id": self.current_batch["batch_id"],
            "task_type": self.current_batch["task_type"],
            "date_range": self.current_batch["date_range"],
            "concurrent_mode": self.current_batch["concurrent_mode"],
            "max_workers": self.current_batch["max_workers"],
            "start_time": datetime.fromtimestamp(self.current_batch["start_time"]).isoformat(),
            "end_time": datetime.fromtimestamp(end_time).isoformat(),
            "batch_duration": batch_duration,
            "actual_work_time": actual_work_time,
            "total_sleep_time": total_sleep_time,
            "sleep_percentage": (total_sleep_time / batch_duration * 100) if batch_duration > 0 else 0,
            "total_processed": len(self.batch_records),
            "success_count": len(success_records),
            "failed_count": len(failed_records),
            "success_rate": len(success_records) / len(self.batch_records) if self.batch_records else 0,
            "performance": {
                "avg_total_time": statistics.mean(total_times) if total_times else 0,
                "median_total_time": statistics.median(total_times) if total_times else 0,
                "avg_download_time": statistics.mean(download_times) if download_times else 0,
                "avg_vectorize_time": statistics.mean(vectorize_times) if vectorize_times else 0,
                "avg_store_time": statistics.mean(store_times) if store_times else 0,
                "throughput_per_minute": len(success_records) / (actual_work_time / 60) if actual_work_time > 0 else 0
            },
            "doc_type_breakdown": {
                doc_type: {
                    "count": stats["count"],
                    "avg_time": statistics.mean(stats["times"]) if stats["times"] else 0
                }
                for doc_type, stats in doc_type_stats.items()
            },
            "error_summary": self._get_error_summary(failed_records)
        }
        
        # 保存报告
        self._save_batch_report(report)
        
        # 打印报告
        self._print_batch_report(report)
        
        # 重置
        self.current_batch = None
        self.batch_records = []
        self.sleep_records = []
        
    def _get_error_summary(self, failed_records: List[Dict]) -> Dict:
        """获取错误摘要"""
        error_counts = defaultdict(int)
        for record in failed_records:
            error_type = record.get("error", "unknown")
            if "无法从PDF提取文本" in error_type:
                error_counts["ocr_needed"] += 1
            elif "store_failed" in error_type:
                error_counts["store_failed"] += 1
            else:
                error_counts["other"] += 1
        return dict(error_counts)
        
    def _save_batch_report(self, report: Dict):
        """保存批次报告"""
        with open(self.batch_log_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(report, ensure_ascii=False) + '\n')
            
    def _print_batch_report(self, report: Dict):
        """打印批次报告"""
        print("\n" + "=" * 60)
        print("批次处理报告")
        print("=" * 60)
        
        print(f"\n基本信息:")
        print(f"  任务类型: {report['task_type']}")
        print(f"  日期范围: {report['date_range']}")
        print(f"  处理模式: {'并发' if report['concurrent_mode'] else '串行'}")
        if report['concurrent_mode']:
            print(f"  并发线程: {report['max_workers']}")
            
        print(f"\n时间统计:")
        print(f"  批次总时间: {report['batch_duration']:.1f}秒")
        print(f"  实际工作时间: {report['actual_work_time']:.1f}秒")
        print(f"  休眠时间: {report['total_sleep_time']:.1f}秒 ({report['sleep_percentage']:.1f}%)")
        
        print(f"\n处理统计:")
        print(f"  总处理数: {report['total_processed']}")
        print(f"  成功数: {report['success_count']}")
        print(f"  失败数: {report['failed_count']}")
        print(f"  成功率: {report['success_rate']:.1%}")
        print(f"  吞吐率: {report['performance']['throughput_per_minute']:.1f}个/分钟")
        
        print(f"\n性能指标:")
        print(f"  平均处理时间: {report['performance']['avg_total_time']:.1f}秒")
        print(f"  中位处理时间: {report['performance']['median_total_time']:.1f}秒")
        
        print(f"\n各阶段平均耗时:")
        perf = report['performance']
        if perf['avg_download_time'] > 0:
            total = perf['avg_download_time'] + perf['avg_vectorize_time'] + perf['avg_store_time']
            print(f"  下载: {perf['avg_download_time']:.1f}秒 ({perf['avg_download_time']/total*100:.0f}%)")
            print(f"  向量化: {perf['avg_vectorize_time']:.1f}秒 ({perf['avg_vectorize_time']/total*100:.0f}%)")
            print(f"  存储: {perf['avg_store_time']:.1f}秒 ({perf['avg_store_time']/total*100:.0f}%)")
            
        if report['doc_type_breakdown']:
            print(f"\n文档类型分布:")
            for doc_type, stats in report['doc_type_breakdown'].items():
                print(f"  {doc_type}: {stats['count']}个, 平均{stats['avg_time']:.1f}秒")
                
        if report['error_summary']:
            print(f"\n错误统计:")
            for error_type, count in report['error_summary'].items():
                print(f"  {error_type}: {count}次")
                
    def show_performance_summary(self, days: int = 7):
        """显示最近几天的性能摘要"""
        if not self.batch_log_file.exists():
            print("暂无批次记录")
            return
            
        # 读取最近的批次
        recent_batches = []
        cutoff_time = datetime.now() - timedelta(days=days)
        
        with open(self.batch_log_file, 'r', encoding='utf-8') as f:
            for line in f:
                try:
                    batch = json.loads(line.strip())
                    batch_time = datetime.fromisoformat(batch['start_time'])
                    if batch_time > cutoff_time:
                        recent_batches.append(batch)
                except:
                    continue
                    
        if not recent_batches:
            print(f"最近{days}天暂无批次记录")
            return
            
        print(f"\n最近{days}天的批次摘要 (共{len(recent_batches)}个批次)")
        print("-" * 60)
        
        # 统计汇总
        total_processed = sum(b['total_processed'] for b in recent_batches)
        total_success = sum(b['success_count'] for b in recent_batches)
        total_time = sum(b['batch_duration'] for b in recent_batches)
        total_work_time = sum(b['actual_work_time'] for b in recent_batches)
        
        # 并发vs串行对比
        concurrent_batches = [b for b in recent_batches if b.get('concurrent_mode')]
        serial_batches = [b for b in recent_batches if not b.get('concurrent_mode')]
        
        print(f"\n总体统计:")
        print(f"  总处理文档: {total_processed}")
        print(f"  总成功数: {total_success}")
        print(f"  总耗时: {total_time/3600:.1f}小时")
        print(f"  实际工作时间: {total_work_time/3600:.1f}小时")
        print(f"  整体成功率: {total_success/total_processed*100:.1f}%")
        
        if concurrent_batches:
            print(f"\n并发模式统计 ({len(concurrent_batches)}个批次):")
            avg_throughput = sum(b['performance']['throughput_per_minute'] for b in concurrent_batches) / len(concurrent_batches)
            print(f"  平均吞吐率: {avg_throughput:.1f}个/分钟")
            avg_time = sum(b['performance']['avg_total_time'] for b in concurrent_batches) / len(concurrent_batches)
            print(f"  平均处理时间: {avg_time:.1f}秒")
            
        if serial_batches:
            print(f"\n串行模式统计 ({len(serial_batches)}个批次):")
            avg_throughput = sum(b['performance']['throughput_per_minute'] for b in serial_batches) / len(serial_batches)
            print(f"  平均吞吐率: {avg_throughput:.1f}个/分钟")
            avg_time = sum(b['performance']['avg_total_time'] for b in serial_batches) / len(serial_batches)
            print(f"  平均处理时间: {avg_time:.1f}秒")
            
    def export_for_analysis(self, days: int = 7) -> str:
        """导出数据用于分析"""
        if not self.batch_log_file.exists():
            return None
            
        # 读取数据
        cutoff_time = datetime.now() - timedelta(days=days)
        batches = []
        
        with open(self.batch_log_file, 'r', encoding='utf-8') as f:
            for line in f:
                try:
                    batch = json.loads(line.strip())
                    batch_time = datetime.fromisoformat(batch['start_time'])
                    if batch_time > cutoff_time:
                        batches.append(batch)
                except:
                    continue
                    
        # 导出文件
        export_file = self.log_dir / f"batch_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(export_file, 'w', encoding='utf-8') as f:
            json.dump({
                "export_date": datetime.now().isoformat(),
                "days_included": days,
                "batch_count": len(batches),
                "batches": batches
            }, f, ensure_ascii=False, indent=2)
            
        return str(export_file)
