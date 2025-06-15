"""
性能统计跟踪模块
用于记录和分析处理性能数据
"""
import json
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
import statistics


class PerformanceTracker:
    """性能跟踪器"""
    
    def __init__(self, log_file: str = "data/performance_log.json"):
        self.log_file = Path(log_file)
        self.log_file.parent.mkdir(parents=True, exist_ok=True)
        
        # 当前批次的统计数据
        self.current_batch = {
            'start_time': None,
            'end_time': None,
            'total_count': 0,
            'success_count': 0,
            'failed_count': 0,
            'ocr_needed_count': 0,
            'details': []
        }
        
        # 加载历史数据
        self.history = self._load_history()
    
    def _load_history(self) -> List[Dict]:
        """加载历史性能数据"""
        if self.log_file.exists():
            try:
                with open(self.log_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return []
        return []
    
    def _save_history(self):
        """保存性能数据"""
        with open(self.log_file, 'w', encoding='utf-8') as f:
            json.dump(self.history, f, ensure_ascii=False, indent=2)
    
    def start_batch(self, total_count: int):
        """开始新批次"""
        self.current_batch = {
            'start_time': time.time(),
            'date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'total_count': total_count,
            'success_count': 0,
            'failed_count': 0,
            'ocr_needed_count': 0,
            'details': []
        }
    
    def record_processing(self, 
                         announcement_id: str,
                         success: bool,
                         stages: Dict[str, float],
                         error_type: Optional[str] = None,
                         file_size: Optional[int] = None,
                         chunks_count: Optional[int] = None):
        """
        记录单个处理结果
        
        Args:
            announcement_id: 公告ID
            success: 是否成功
            stages: 各阶段耗时 {'download': 1.2, 'pdf_extract': 2.3, 'vectorize': 0.5, 'store': 0.3}
            error_type: 错误类型 ('download_failed', 'pdf_extract_failed', 'ocr_needed', etc.)
            file_size: PDF文件大小（字节）
            chunks_count: 生成的chunks数量
        """
        total_time = sum(stages.values())
        
        record = {
            'announcement_id': announcement_id,
            'success': success,
            'total_time': total_time,
            'stages': stages,
            'timestamp': time.time()
        }
        
        if error_type:
            record['error_type'] = error_type
            if error_type == 'ocr_needed':
                self.current_batch['ocr_needed_count'] += 1
        
        if file_size:
            record['file_size'] = file_size
        
        if chunks_count:
            record['chunks_count'] = chunks_count
        
        self.current_batch['details'].append(record)
        
        if success:
            self.current_batch['success_count'] += 1
        else:
            self.current_batch['failed_count'] += 1
    
    def end_batch(self) -> Dict:
        """结束批次并返回统计结果"""
        self.current_batch['end_time'] = time.time()
        self.current_batch['total_time'] = self.current_batch['end_time'] - self.current_batch['start_time']
        
        # 计算统计信息
        stats = self._calculate_batch_stats()
        self.current_batch['stats'] = stats
        
        # 保存到历史
        batch_summary = {
            'date': self.current_batch['date'],
            'total_count': self.current_batch['total_count'],
            'success_count': self.current_batch['success_count'],
            'failed_count': self.current_batch['failed_count'],
            'ocr_needed_count': self.current_batch['ocr_needed_count'],
            'total_time': self.current_batch['total_time'],
            'stats': stats
        }
        
        self.history.append(batch_summary)
        self._save_history()
        
        # 同时保存详细数据
        detail_file = self.log_file.parent / f"performance_detail_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(detail_file, 'w', encoding='utf-8') as f:
            json.dump(self.current_batch, f, ensure_ascii=False, indent=2)
        
        return stats
    
    def _calculate_batch_stats(self) -> Dict:
        """计算批次统计信息"""
        details = self.current_batch['details']
        successful_details = [d for d in details if d['success']]
        
        if not successful_details:
            return {}
        
        # 计算各阶段平均耗时
        stage_times = {}
        for stage in ['download', 'pdf_extract', 'vectorize', 'store']:
            times = [d['stages'].get(stage, 0) for d in successful_details if stage in d['stages']]
            if times:
                stage_times[f'avg_{stage}_time'] = statistics.mean(times)
                stage_times[f'max_{stage}_time'] = max(times)
                stage_times[f'min_{stage}_time'] = min(times)
        
        # 计算总体统计
        total_times = [d['total_time'] for d in successful_details]
        
        stats = {
            'success_rate': self.current_batch['success_count'] / self.current_batch['total_count'] if self.current_batch['total_count'] > 0 else 0,
            'avg_process_time': statistics.mean(total_times),
            'max_process_time': max(total_times),
            'min_process_time': min(total_times),
            'median_process_time': statistics.median(total_times),
            **stage_times
        }
        
        # 如果有文件大小信息，计算处理速度
        file_sizes = [d['file_size'] for d in successful_details if 'file_size' in d]
        if file_sizes:
            stats['avg_file_size'] = statistics.mean(file_sizes)
            stats['total_data_processed'] = sum(file_sizes)
            # 计算每秒处理的字节数
            stats['processing_speed_bps'] = stats['total_data_processed'] / self.current_batch['total_time']
        
        # 错误类型统计
        error_types = {}
        for d in details:
            if 'error_type' in d:
                error_type = d['error_type']
                error_types[error_type] = error_types.get(error_type, 0) + 1
        stats['error_types'] = error_types
        
        return stats
    
    def get_performance_summary(self, last_n_batches: int = 10) -> Dict:
        """获取性能摘要"""
        recent_batches = self.history[-last_n_batches:] if len(self.history) > last_n_batches else self.history
        
        if not recent_batches:
            return {}
        
        # 汇总统计
        total_processed = sum(b['total_count'] for b in recent_batches)
        total_success = sum(b['success_count'] for b in recent_batches)
        total_failed = sum(b['failed_count'] for b in recent_batches)
        total_ocr_needed = sum(b.get('ocr_needed_count', 0) for b in recent_batches)
        
        avg_success_rates = [b['stats'].get('success_rate', 0) for b in recent_batches if 'stats' in b]
        avg_process_times = [b['stats'].get('avg_process_time', 0) for b in recent_batches if 'stats' in b]
        
        summary = {
            'batches_analyzed': len(recent_batches),
            'total_processed': total_processed,
            'total_success': total_success,
            'total_failed': total_failed,
            'total_ocr_needed': total_ocr_needed,
            'overall_success_rate': total_success / total_processed if total_processed > 0 else 0,
            'avg_batch_success_rate': statistics.mean(avg_success_rates) if avg_success_rates else 0,
            'avg_process_time': statistics.mean(avg_process_times) if avg_process_times else 0
        }
        
        return summary
    
    def export_for_analysis(self) -> str:
        """导出数据用于分析"""
        export_file = self.log_file.parent / f"performance_export_{datetime.now().strftime('%Y%m%d')}.json"
        
        export_data = {
            'summary': self.get_performance_summary(),
            'recent_batches': self.history[-20:],  # 最近20批次
            'export_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        with open(export_file, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, ensure_ascii=False, indent=2)
        
        return str(export_file)


# 使用示例
if __name__ == "__main__":
    tracker = PerformanceTracker()
    
    # 模拟一个批次
    tracker.start_batch(total_count=10)
    
    # 模拟处理
    for i in range(10):
        if i < 8:  # 80%成功
            tracker.record_processing(
                announcement_id=f"test_{i}",
                success=True,
                stages={
                    'download': 1.5 + i * 0.1,
                    'pdf_extract': 2.0 + i * 0.2,
                    'vectorize': 0.5,
                    'store': 0.3
                },
                file_size=1024 * 1024 * (i + 1),
                chunks_count=50 + i * 10
            )
        else:  # 20%失败
            tracker.record_processing(
                announcement_id=f"test_{i}",
                success=False,
                stages={'download': 1.5},
                error_type='ocr_needed' if i == 8 else 'download_failed'
            )
    
    # 结束批次
    stats = tracker.end_batch()
    
    print("批次统计:")
    print(json.dumps(stats, ensure_ascii=False, indent=2))
    
    print("\n性能摘要:")
    print(json.dumps(tracker.get_performance_summary(), ensure_ascii=False, indent=2))
