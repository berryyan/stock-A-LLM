"""
智能处理器 V5.2 - 季度报告日期范围处理优化版
主要更新：
1. 季度报告支持日期范围处理（与年度报告保持一致）
2. 保持所有其他功能不变
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.mysql_connector import MySQLConnector
from database.milvus_connector import MilvusConnector
from rag.document_processor import DocumentProcessor
from config.settings import settings
from utils.performance_tracker import PerformanceTracker
from utils.auto_performance_logger import AutoPerformanceLogger
import time
import json
from datetime import datetime, timedelta
from typing import List, Dict, Tuple, Optional
from pathlib import Path
import threading
from collections import deque
import logging
import random

# 尝试导入显示优化库
try:
    from tqdm import tqdm
    TQDM_AVAILABLE = True
except ImportError:
    TQDM_AVAILABLE = False
    print("提示: 安装 tqdm 以获得更好的进度显示 (pip install tqdm)")

try:
    from colorama import init, Fore, Back, Style
    init(autoreset=True)
    COLORAMA_AVAILABLE = True
except ImportError:
    COLORAMA_AVAILABLE = False
    print("提示: 安装 colorama 以获得彩色输出 (pip install colorama)")
    # 定义空的颜色常量
    class Fore:
        GREEN = RED = YELLOW = BLUE = CYAN = MAGENTA = WHITE = RESET = ''
    class Style:
        BRIGHT = DIM = RESET_ALL = ''

try:
    from tabulate import tabulate
    TABULATE_AVAILABLE = True
except ImportError:
    TABULATE_AVAILABLE = False
    print("提示: 安装 tabulate 以获得更好的表格显示 (pip install tabulate)")

# 配置日志级别为WARNING，减少冗余输出
logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)


class ConsoleHelper:
    """控制台输出辅助类"""
    
    @staticmethod
    def print_header(title: str):
        """打印标题"""
        width = 80
        print("\n" + "=" * width)
        print(f"{Fore.CYAN}{Style.BRIGHT}{title.center(width)}{Style.RESET_ALL}")
        print("=" * width)
        
    @staticmethod
    def print_success(message: str):
        """打印成功信息"""
        print(f"{Fore.GREEN}✓ {message}{Style.RESET_ALL}")
        
    @staticmethod
    def print_error(message: str):
        """打印错误信息"""
        print(f"{Fore.RED}✗ {message}{Style.RESET_ALL}")
        
    @staticmethod
    def print_warning(message: str):
        """打印警告信息"""
        print(f"{Fore.YELLOW}⚠ {message}{Style.RESET_ALL}")
        
    @staticmethod
    def print_info(message: str):
        """打印信息"""
        print(f"{Fore.BLUE}ℹ {message}{Style.RESET_ALL}")
        
    @staticmethod
    def print_statistics(stats: Dict):
        """打印统计表格"""
        if TABULATE_AVAILABLE:
            headers = ["指标", "数值"]
            table_data = []
            for key, value in stats.items():
                if isinstance(value, float):
                    table_data.append([key, f"{value:.2f}"])
                else:
                    table_data.append([key, str(value)])
            print("\n" + tabulate(table_data, headers=headers, tablefmt="grid"))
        else:
            print("\n统计信息:")
            for key, value in stats.items():
                print(f"  {key}: {value}")


class AdaptiveThrottleStrategy:
    """自适应限流策略 - 仅在检测到问题时介入"""
    
    def __init__(self):
        self.error_window = deque(maxlen=20)  # 最近20次请求
        self.response_times = deque(maxlen=50)  # 最近50次响应时间
        self.last_429_time = None  # 上次429错误时间
        self.consecutive_errors = 0
        self.throttle_until = None  # 限流到某个时间点
        
    def record_success(self, response_time: float):
        """记录成功请求"""
        self.error_window.append(0)
        self.response_times.append(response_time)
        self.consecutive_errors = 0
        
    def record_error(self, error_type: str = 'general'):
        """记录错误"""
        self.error_window.append(1)
        self.consecutive_errors += 1
        
        if error_type == '429' or 'Too Many Requests' in error_type:
            self.last_429_time = time.time()
            # 429错误，强制限流30-60秒
            self.throttle_until = time.time() + random.uniform(30, 60)
            logger.warning(f"检测到429错误，限流至 {datetime.fromtimestamp(self.throttle_until)}")
            
    def should_throttle(self) -> Tuple[bool, float]:
        """
        判断是否需要限流
        返回: (是否限流, 建议等待时间)
        """
        # 强制限流期
        if self.throttle_until and time.time() < self.throttle_until:
            wait_time = self.throttle_until - time.time()
            return True, wait_time
            
        # 连续错误检测
        if self.consecutive_errors >= 3:
            # 指数退避：3次=5秒，4次=10秒，5次=20秒
            wait_time = min(5 * (2 ** (self.consecutive_errors - 3)), 60)
            return True, wait_time
            
        # 错误率检测
        if len(self.error_window) >= 10:
            error_rate = sum(self.error_window) / len(self.error_window)
            if error_rate > 0.3:  # 30%错误率
                return True, 10.0
                
        # 响应时间异常检测
        if len(self.response_times) >= 10:
            recent_avg = sum(list(self.response_times)[-10:]) / 10
            overall_avg = sum(self.response_times) / len(self.response_times)
            
            # 如果最近的响应时间是平均值的3倍以上
            if recent_avg > overall_avg * 3:
                return True, 5.0
                
        return False, 0
        
    def get_stats(self) -> Dict:
        """获取统计信息"""
        error_rate = sum(self.error_window) / len(self.error_window) if self.error_window else 0
        avg_response = sum(self.response_times) / len(self.response_times) if self.response_times else 0
        
        return {
            'error_rate': error_rate,
            'avg_response_time': avg_response,
            'consecutive_errors': self.consecutive_errors,
            'is_throttled': self.throttle_until and time.time() < self.throttle_until
        }


class ProcessedRecordManager:
    """已处理记录管理器"""
    
    def __init__(self):
        self.record_file = Path("data/processed_announcements.json")
        self.processed_ids = self._load_records()
        self._changes_count = 0  # 记录变更次数
        
    def _load_records(self) -> set:
        """加载已处理记录"""
        if self.record_file.exists():
            try:
                with open(self.record_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    ids = set(data.get('processed_ids', []))
                    print(f"加载了 {len(ids)} 个已处理记录")
                    return ids
            except Exception as e:
                logger.error(f"加载处理记录失败: {e}")
                return set()
        return set()
        
    def _save_records(self):
        """保存已处理记录"""
        self.record_file.parent.mkdir(parents=True, exist_ok=True)
        try:
            with open(self.record_file, 'w', encoding='utf-8') as f:
                json.dump({
                    'processed_ids': list(self.processed_ids),
                    'last_updated': datetime.now().isoformat(),
                    'total_count': len(self.processed_ids)
                }, f, ensure_ascii=False, indent=2)
            logger.info(f"保存了 {len(self.processed_ids)} 个处理记录")
        except Exception as e:
            logger.error(f"保存处理记录失败: {e}")
            
    def add_processed(self, ann_id: str):
        """添加已处理记录"""
        if ann_id not in self.processed_ids:
            self.processed_ids.add(ann_id)
            self._changes_count += 1
            
            # 每100次变更自动保存一次
            if self._changes_count >= 100:
                self._save_records()
                self._changes_count = 0
        
    def batch_save(self):
        """批量保存（在处理完成后调用）"""
        if self._changes_count > 0:
            self._save_records()
            self._changes_count = 0
        
    def is_processed(self, ann_id: str) -> bool:
        """检查是否已处理"""
        return ann_id in self.processed_ids
    
    def get_all_processed_ids(self) -> set:
        """获取所有已处理的ID"""
        return self.processed_ids.copy()


class SmartProcessorV5_2:
    """智能处理器 V5.2 - 季度报告日期范围处理优化版本"""
    
    def __init__(self):
        self.mysql = MySQLConnector()
        self.milvus = MilvusConnector()
        self.processor = DocumentProcessor()
        self.content_filter = ContentFilter()
        self.performance_tracker = PerformanceTracker()
        self.auto_perf_logger = AutoPerformanceLogger()
        
        # 自适应限流策略
        self.throttle_strategy = AdaptiveThrottleStrategy()
        
        # 性能模式
        self.performance_mode = 'aggressive'  # 'aggressive', 'normal', 'conservative'
        
        # OCR失败记录
        self.ocr_failed_file = Path(getattr(settings, 'OCR_FAILED_LOG', 'data/ocr_needed_files.json'))
        self.ocr_failed_file.parent.mkdir(parents=True, exist_ok=True)
        self._load_ocr_failed_list()
        
        # 控制台辅助
        self.console = ConsoleHelper()
        
        # 已处理记录管理器
        self.record_manager = ProcessedRecordManager()
        
    def _load_ocr_failed_list(self):
        """加载OCR失败列表"""
        if self.ocr_failed_file.exists():
            with open(self.ocr_failed_file, 'r', encoding='utf-8') as f:
                self.ocr_failed_list = json.load(f)
        else:
            self.ocr_failed_list = []
            
    def _save_ocr_failed_list(self):
        """保存OCR失败列表"""
        with open(self.ocr_failed_file, 'w', encoding='utf-8') as f:
            json.dump(self.ocr_failed_list, f, ensure_ascii=False, indent=2)
            
    def _record_ocr_failed(self, announcement: Dict, pdf_path: str):
        """记录需要OCR的文件"""
        record = {
            'ts_code': announcement['ts_code'],
            'name': announcement['name'],
            'title': announcement['title'],
            'ann_date': announcement['ann_date'],
            'url': announcement['url'],
            'pdf_path': pdf_path,
            'recorded_time': datetime.now().isoformat()
        }
        self.ocr_failed_list.append(record)
        self._save_ocr_failed_list()
        
    def get_processed_announcements(self):
        """获取已处理的公告ID - 使用本地记录管理器"""
        print("\n检查已处理的公告...", end='', flush=True)
        
        processed_ids = self.record_manager.get_all_processed_ids()
        self.console.print_success(f"已处理 {len(processed_ids)} 个公告")
        return processed_ids
            
    def _process_single_announcement(self, ann: Dict) -> Tuple[bool, Dict]:
        """处理单个公告"""
        stage_times = {}
        start_time = time.time()
        
        try:
            # 检查是否需要限流
            should_throttle, wait_time = self.throttle_strategy.should_throttle()
            if should_throttle:
                time.sleep(wait_time)
                self.auto_perf_logger.record_sleep(wait_time)
            
            # 下载阶段
            download_start = time.time()
            docs = self.processor.process_announcement(ann)
            download_end = time.time()
            download_time = download_end - download_start
            stage_times['download'] = download_time
            
            # 记录成功
            self.throttle_strategy.record_success(download_time)
            
            if docs:
                # 向量化和存储阶段
                store_start = time.time()
                if self.processor.store_documents_to_milvus(docs):
                    store_end = time.time()
                    stage_times['vectorize'] = (store_end - store_start) * 0.7
                    stage_times['store'] = (store_end - store_start) * 0.3
                    
                    return True, {
                        'stages': stage_times,
                        'chunks_count': len(docs),
                        'total_time': time.time() - start_time
                    }
                else:
                    return False, {
                        'error': 'store_failed',
                        'stages': stage_times,
                        'total_time': time.time() - start_time
                    }
            else:
                return False, {
                    'error': 'process_failed',
                    'stages': stage_times,
                    'total_time': time.time() - start_time
                }
                
        except Exception as e:
            # 记录错误
            error_msg = str(e)
            self.throttle_strategy.record_error(error_msg)
            
            # 特殊处理OCR错误
            if "无法从PDF提取文本" in error_msg:
                try:
                    pdf_path = error_msg.split(": ")[-1]
                    self._record_ocr_failed(ann, pdf_path)
                    return False, {
                        'error': 'ocr_needed',
                        'stages': {'download': time.time() - start_time},
                        'total_time': time.time() - start_time
                    }
                except:
                    pass
                    
            return False, {
                'error': error_msg,
                'stages': {'download': time.time() - start_time},
                'total_time': time.time() - start_time
            }
            
    def _record_performance(self, ann: Dict, success: bool, stages: Dict, 
                           chunks_count: int, doc_type: str, error_type: str = None):
        """记录性能数据"""
        # 记录到原有性能追踪器
        self.performance_tracker.record_processing(
            announcement_id=ann.get('announcement_id', f"{ann['ts_code']}_{ann['ann_date']}"),
            success=success,
            stages=stages,
            chunks_count=chunks_count if success else 0,
            error_type=error_type
        )
        
        # 记录到自动记录器
        self.auto_perf_logger.add_record({
            "ts_code": ann['ts_code'],
            "title": ann['title'],
            "doc_type": doc_type,
            "start_time": time.time() - sum(stages.values()),
            "stages": stages,
            "success": success,
            "chunks_count": chunks_count if success else 0,
            "error": error_type,
            "total_time": sum(stages.values())
        })
        
    def process_unprocessed_announcements(self,
                                          start_date='20250422',
                                          end_date='20250422',
                                          use_content_filter=True,
                                          max_count=10,
                                          task_type="未指定"):
        """处理未处理过的公告 - V5.2显示优化版本"""
        
        self.console.print_header(f"智能处理器 V5.2 - {task_type}")
        
        # 显示配置信息
        config_info = {
            "日期范围": f"{start_date} - {end_date}",
            "内容过滤": "启用" if use_content_filter else "禁用",
            "性能模式": self.performance_mode,
            "最大处理数": max_count
        }
        
        print("\n配置信息:")
        for key, value in config_info.items():
            print(f"  {Fore.CYAN}{key}:{Style.RESET_ALL} {value}")
        
        # 获取已处理的ID
        processed_ids = self.get_processed_announcements()
        
        # 构建SQL查询
        keywords = self.content_filter.get_keywords_for_sql()
        keyword_conditions = []
        for keyword in keywords:
            keyword_conditions.append(f"title LIKE '%{keyword}%'")
            
        if keyword_conditions and use_content_filter:
            keyword_sql = " OR ".join(keyword_conditions)
            query = f"""
            SELECT ts_code, name, title, url, ann_date
            FROM tu_anns_d
            WHERE ann_date BETWEEN '{start_date}' AND '{end_date}'
            AND ({keyword_sql})
            ORDER BY ts_code
            """
        else:
            query = f"""
            SELECT ts_code, name, title, url, ann_date
            FROM tu_anns_d
            WHERE ann_date BETWEEN '{start_date}' AND '{end_date}'
            ORDER BY ts_code
            """
            
        print("\n查询公告中...", end='', flush=True)
        all_announcements = self.mysql.execute_query(query)
        print(f" 找到 {Fore.YELLOW}{len(all_announcements)}{Style.RESET_ALL} 条")
        
        # 过滤未处理的
        print("过滤未处理公告...", end='', flush=True)
        unprocessed = []
        filtered_out = 0
        
        for ann in all_announcements:
            try:
                _, ann_id, _ = self.processor.extract_params_from_url(ann['url'])
                if ann_id in processed_ids:
                    continue
                    
                if use_content_filter:
                    passed, category, content_type = self.content_filter.filter_announcement(ann['title'])
                    if not passed:
                        filtered_out += 1
                        continue
                    ann['category'] = category
                    ann['content_type'] = content_type
                    
                unprocessed.append(ann)
            except:
                if use_content_filter:
                    passed, category, content_type = self.content_filter.filter_announcement(ann['title'])
                    if passed:
                        ann['category'] = category
                        ann['content_type'] = content_type
                        unprocessed.append(ann)
                    else:
                        filtered_out += 1
                else:
                    unprocessed.append(ann)
                    
        print(f" 完成 (过滤 {filtered_out} 条，待处理 {Fore.GREEN}{len(unprocessed)}{Style.RESET_ALL} 条)")
        
        if not unprocessed:
            self.console.print_warning("没有新的公告需要处理")
            return 0
            
        # 限制处理数量
        to_process = unprocessed[:max_count]
        
        # 显示待处理摘要
        print(f"\n本次将处理 {Fore.GREEN}{len(to_process)}{Style.RESET_ALL} 条公告:")
        
        # 按类型统计
        type_stats = {}
        for ann in to_process:
            content_type = ann.get('content_type', '未分类')
            type_stats[content_type] = type_stats.get(content_type, 0) + 1
            
        print("\n类型分布:")
        for doc_type, count in sorted(type_stats.items(), key=lambda x: x[1], reverse=True):
            print(f"  {doc_type}: {count} 条")
        
        # 确认处理
        response = input(f"\n{Fore.YELLOW}是否开始处理? (y/n):{Style.RESET_ALL} ")
        if response.lower() != 'y':
            self.console.print_warning("已取消")
            return 0
            
        # 开始性能跟踪
        self.performance_tracker.start_batch(len(to_process))
        self.auto_perf_logger.start_batch(
            task_type=task_type,
            start_date=start_date,
            end_date=end_date,
            filter_enabled=use_content_filter,
            max_count=max_count,
            total_to_process=len(to_process)
        )
        
        # 处理公告
        success_count = 0
        error_count = 0
        ocr_needed_count = 0
        batch_start_time = time.time()
        
        # 使用进度条
        if TQDM_AVAILABLE:
            progress_bar = tqdm(to_process, desc="处理进度", unit="个", 
                               bar_format='{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}]')
        else:
            progress_bar = to_process
            
        for i, ann in enumerate(progress_bar):
            # 更新进度条描述
            if TQDM_AVAILABLE:
                progress_bar.set_description(f"处理 {ann['ts_code']}")
                
            # 处理单个公告
            success, result = self._process_single_announcement(ann)
            
            if success:
                success_count += 1
                # 记录到已处理管理器
                try:
                    _, ann_id, _ = self.processor.extract_params_from_url(ann['url'])
                    self.record_manager.add_processed(ann_id)
                except:
                    pass
                    
                if not TQDM_AVAILABLE:
                    self.console.print_success(
                        f"[{i+1}/{len(to_process)}] {ann['ts_code']} - "
                        f"{result.get('chunks_count', 0)} 个文档, {result.get('total_time', 0):.1f}秒"
                    )
            else:
                error = result.get('error', 'unknown')
                if 'ocr_needed' in error:
                    ocr_needed_count += 1
                else:
                    error_count += 1
                    
                if not TQDM_AVAILABLE:
                    self.console.print_error(
                        f"[{i+1}/{len(to_process)}] {ann['ts_code']} - {error[:50]}"
                    )
                
            # 记录性能
            doc_type = ann.get('content_type', '')
            self._record_performance(
                ann, success, 
                result.get('stages', {}),
                result.get('chunks_count', 0),
                doc_type,
                result.get('error') if not success else None
            )
            
            # 更新进度条后缀信息
            if TQDM_AVAILABLE:
                progress_bar.set_postfix({
                    '成功': success_count,
                    '失败': error_count,
                    'OCR': ocr_needed_count,
                    '速度': f"{(i+1)/(time.time()-batch_start_time)*60:.1f}/分"
                })
                
        # 结束批次并显示统计
        batch_time = time.time() - batch_start_time
        stats = self.performance_tracker.end_batch()
        
        # 保存已处理记录
        self.record_manager.batch_save()
        
        # 显示处理结果
        self.console.print_header("处理完成")
        
        # 结果统计
        result_stats = {
            "总处理数": len(to_process),
            "成功数": success_count,
            "失败数": error_count,
            "需要OCR": ocr_needed_count,
            "成功率": f"{success_count/len(to_process)*100:.1f}%",
            "总耗时": f"{batch_time:.1f}秒",
            "平均速度": f"{len(to_process)/batch_time*60:.1f}个/分钟"
        }
        
        self.console.print_statistics(result_stats)
        
        # 显示性能详情
        if stats and 'avg_download_time' in stats:
            print(f"\n{Fore.CYAN}各阶段平均耗时:{Style.RESET_ALL}")
            stage_times = {
                "下载": f"{stats.get('avg_download_time', 0):.1f}秒",
                "向量化": f"{stats.get('avg_vectorize_time', 0):.1f}秒",
                "存储": f"{stats.get('avg_store_time', 0):.1f}秒"
            }
            for stage, time_str in stage_times.items():
                print(f"  {stage}: {time_str}")
                
        # 错误类型分布
        if stats and 'error_types' in stats and stats['error_types']:
            print(f"\n{Fore.RED}错误类型分布:{Style.RESET_ALL}")
            for error_type, count in stats['error_types'].items():
                print(f"  {error_type}: {count}次")
                
        self.auto_perf_logger.finish_batch()
        
        return success_count
        
    def _display_performance_stats(self, stats: Dict):
        """显示性能统计 - V5.2简化版"""
        # 性能统计已经集成到主流程中
        pass
                
    def set_performance_mode(self, mode: str):
        """设置性能模式"""
        if mode in ['aggressive', 'normal', 'conservative']:
            self.performance_mode = mode
            self.console.print_success(f"性能模式设置为: {mode}")
            
            # 根据模式调整参数
            mode_descriptions = {
                'aggressive': "无休眠，最大速度，仅在错误时限流",
                'normal': "智能限流，错误自动退避",
                'conservative': "保守策略，主动限流保护"
            }
            print(f"  {mode_descriptions[mode]}")
        else:
            self.console.print_error(f"无效的模式: {mode}")
            
    def show_statistics(self):
        """显示统计信息 - V5.2美化版"""
        self.console.print_header("系统统计")
        
        # Milvus统计
        stats = self.milvus.get_collection_stats()
        
        # 获取唯一公告数
        processed_ids = self.get_processed_announcements()
        
        # PDF统计
        pdf_dir = "data/pdfs/cache"
        pdf_count = 0
        if os.path.exists(pdf_dir):
            pdf_files = [f for f in os.listdir(pdf_dir) if f.endswith('.pdf')]
            pdf_count = len(pdf_files)
            
        # 显示基础统计
        basic_stats = {
            "Milvus文档总数": stats['row_count'],
            "已处理公告数": len(processed_ids),
            "已下载PDF数": pdf_count,
            "需要OCR的文件": len(self.ocr_failed_list)
        }
        
        print("\n基础统计:")
        for key, value in basic_stats.items():
            print(f"  {Fore.CYAN}{key}:{Style.RESET_ALL} {Fore.YELLOW}{value}{Style.RESET_ALL}")
        
        # 当前设置
        print(f"\n{Fore.BLUE}当前设置:{Style.RESET_ALL}")
        print(f"  性能模式: {self.performance_mode}")
        
        # 限流状态
        throttle_stats = self.throttle_strategy.get_stats()
        print(f"\n{Fore.BLUE}限流策略状态:{Style.RESET_ALL}")
        status_items = {
            "错误率": f"{throttle_stats['error_rate']:.1%}",
            "平均响应时间": f"{throttle_stats['avg_response_time']:.1f}秒",
            "连续错误数": throttle_stats['consecutive_errors'],
            "当前限流": "是" if throttle_stats['is_throttled'] else "否"
        }
        
        for key, value in status_items.items():
            color = Fore.RED if key == "当前限流" and value == "是" else Fore.GREEN
            print(f"  {key}: {color}{value}{Style.RESET_ALL}")
        
        # 内容过滤配置
        print(f"\n{Fore.BLUE}内容过滤配置:{Style.RESET_ALL}")
        print(f"  核心类型: {', '.join(self.content_filter.enabled_core_types)}")
        print(f"  扩展类型: {', '.join(self.content_filter.enabled_extended_types)}")
        
        # 性能摘要
        perf_summary = self.performance_tracker.get_performance_summary()
        if perf_summary:
            print(f"\n{Fore.BLUE}性能摘要 (最近10批次):{Style.RESET_ALL}")
            perf_stats = {
                "总处理数": perf_summary.get('total_processed', 0),
                "总成功数": perf_summary.get('total_success', 0),
                "平均成功率": f"{perf_summary.get('avg_batch_success_rate', 0):.1%}",
                "平均处理时间": f"{perf_summary.get('avg_process_time', 0):.1f}秒"
            }
            
            for key, value in perf_stats.items():
                print(f"  {key}: {Fore.YELLOW}{value}{Style.RESET_ALL}")
            
    def export_performance_data(self):
        """导出性能数据用于分析"""
        export_file = self.performance_tracker.export_for_analysis()
        self.console.print_success(f"性能数据已导出到: {export_file}")
        
        days = input(f"\n{Fore.YELLOW}导出最近几天的批次数据？(默认7):{Style.RESET_ALL} ").strip()
        days = int(days) if days else 7
        auto_export_file = self.auto_perf_logger.export_for_analysis(days)
        self.console.print_success(f"批次详细数据已导出到: {auto_export_file}")
        
        self.console.print_info("您可以将这些文件提供给我进行分析")


# 继承必要的类（从V5复制，保持不变）
class ContentFilter:
    """内容过滤器 - 继承自V5"""
    
    def __init__(self):
        # 核心报告类型配置（严格匹配）
        self.core_report_rules = {
            '年度报告': {
                'include_keywords': [('年度报告', '年报')],
                'exclude_keywords': ['摘要', '英文版', 'English', '更正', '补充', '关于', '会计师', '审计',
                                     '问询', '说明会', '提示性', '披露', '基金', '债券', '集团', '控股'],
                'strict': True
            },
            '年度报告摘要': {
                'include_keywords': [('年度报告摘要', '年报摘要')],
                'exclude_keywords': ['英文版', 'English', '更正', '补充'],
                'strict': True
            },
            '第一季度报告': {
                'include_keywords': [('第一季度报告', '一季度报告', '一季报')],
                'exclude_keywords': ['摘要', '英文版', '更正', '关于', '审核', '提示性', '基金'],
                'strict': True
            },
            '半年度报告': {
                'include_keywords': [('半年度报告', '半年报', '中期报告')],
                'exclude_keywords': ['摘要', '英文版', '更正', '关于', '提示性', '基金'],
                'strict': True
            },
            '第三季度报告': {
                'include_keywords': [('第三季度报告', '三季度报告', '三季报')],
                'exclude_keywords': ['摘要', '英文版', '更正', '关于', '提示性', '基金'],
                'strict': True
            },
            '业绩预告': {
                'include_keywords': [('业绩预告', '业绩预增', '业绩预减', '业绩预盈', '业绩预亏')],
                'exclude_keywords': ['更正', '补充', '取消', '说明会'],
                'strict': True
            },
            '业绩快报': {
                'include_keywords': [('业绩快报',)],
                'exclude_keywords': ['更正', '补充', '公告的公告'],
                'strict': True
            }
        }

        # 扩展内容类型配置
        self.extended_content_rules = {
            '问询回复': {
                'include_keywords': [('问询函回复', '问询函的回复', '监管函回复', '关注函回复')],
                'exclude_keywords': ['关于回复'],
                'strict': False
            },
            '利润分配': {
                'include_keywords': [('权益分派实施', '利润分配实施', '分红派息实施')],
                'exclude_keywords': ['预案', '提议', '方案'],
                'strict': False
            }
        }

        self.enabled_core_types = getattr(settings, 'ENABLED_CORE_TYPES',
                                          list(self.core_report_rules.keys()))
        self.enabled_extended_types = getattr(settings, 'ENABLED_EXTENDED_TYPES',
                                              ['问询回复', '利润分配'])

    def check_title(self, title: str, report_type: str, rules: Dict) -> bool:
        """检查标题是否匹配规则"""
        rule = rules.get(report_type, {})
        if not rule:
            return False

        include_keywords_groups = rule.get('include_keywords', [])
        matched = False
        for keyword_group in include_keywords_groups:
            if isinstance(keyword_group, tuple):
                if any(keyword in title for keyword in keyword_group):
                    matched = True
                    break
            else:
                if keyword_group in title:
                    matched = True
                    break

        if not matched:
            return False

        exclude_keywords = rule.get('exclude_keywords', [])
        if any(keyword in title for keyword in exclude_keywords):
            return False

        return True

    def filter_announcement(self, title: str) -> Tuple[bool, str, str]:
        """过滤公告"""
        for report_type in self.enabled_core_types:
            if self.check_title(title, report_type, self.core_report_rules):
                return True, 'core', report_type

        for content_type in self.enabled_extended_types:
            if self.check_title(title, content_type, self.extended_content_rules):
                return True, 'extended', content_type

        return False, 'none', ''

    def get_keywords_for_sql(self) -> List[str]:
        """获取SQL查询用的关键词"""
        keywords = []

        for report_type in self.enabled_core_types:
            if report_type in self.core_report_rules:
                for keyword_group in self.core_report_rules[report_type]['include_keywords']:
                    if isinstance(keyword_group, tuple):
                        keywords.extend(keyword_group)
                    else:
                        keywords.append(keyword_group)

        for content_type in self.enabled_extended_types:
            if content_type in self.extended_content_rules:
                for keyword_group in self.extended_content_rules[content_type]['include_keywords']:
                    if isinstance(keyword_group, tuple):
                        keywords.extend(keyword_group)
                    else:
                        keywords.append(keyword_group)

        return list(set(keywords))


class DateHelper:
    """日期辅助类"""
    
    @staticmethod
    def parse_date_input(date_input: str) -> Tuple[str, str]:
        """
        解析日期输入，支持单日期和日期范围
        
        支持格式：
        - 单日期：20250422 → (20250422, 20250422)
        - 日期范围：20250415-20250430 → (20250415, 20250430)
        
        返回: (start_date, end_date)
        """
        date_input = date_input.strip()
        
        # 检查是否为日期范围
        if '-' in date_input:
            parts = date_input.split('-')
            if len(parts) == 2:
                start = parts[0].strip()
                end = parts[1].strip()
                # 验证日期格式
                if len(start) == 8 and len(end) == 8:
                    return start, end
                else:
                    raise ValueError("日期格式错误，应为YYYYMMDD")
        
        # 单日期
        if len(date_input) == 8:
            return date_input, date_input
        
        raise ValueError("不支持的日期格式，请使用 YYYYMMDD 或 YYYYMMDD-YYYYMMDD")


def main():
    """主函数 - V5.2优化版"""
    processor = SmartProcessorV5_2()
    console = ConsoleHelper()
    
    while True:
        console.print_header("智能处理器 V5.2 - 控制台优化版")
        
        menu_options = [
            "1. 查看统计信息",
            "2. 处理未处理的年度报告",
            "3. 处理未处理的季度报告",
            "4. 处理最近的公告（带过滤）",
            "5. 处理最近的公告（无过滤）",
            "6. 自定义处理",
            "7. 查看需要OCR的文件",
            "8. 导出性能数据",
            "9. 性能模式设置",
            "0. 退出"
        ]
        
        print()
        for option in menu_options:
            print(f"  {option}")
        
        choice = input(f"\n{Fore.YELLOW}请选择:{Style.RESET_ALL} ")
        
        if choice == '1':
            processor.show_statistics()
            
        elif choice == '2':
            date_input = input(f"{Fore.YELLOW}日期 (YYYYMMDD 或 YYYYMMDD-YYYYMMDD, 默认20250422):{Style.RESET_ALL} ") or "20250422"
            
            try:
                start_date, end_date = DateHelper.parse_date_input(date_input)
                if start_date != end_date:
                    console.print_info(f"将处理日期范围: {start_date} 至 {end_date}")
            except ValueError as e:
                console.print_error(f"日期格式错误: {e}")
                continue
                
            count = int(input(f"{Fore.YELLOW}处理数量 (默认50):{Style.RESET_ALL} ") or "50")
            
            processor.content_filter.enabled_core_types = ['年度报告', '年度报告摘要']
            processor.content_filter.enabled_extended_types = []
            
            processor.process_unprocessed_announcements(
                start_date=start_date,
                end_date=end_date,
                use_content_filter=True,
                max_count=count,
                task_type="年度报告处理"
            )
            
        elif choice == '3':
            date_input = input(f"{Fore.YELLOW}日期 (YYYYMMDD 或 YYYYMMDD-YYYYMMDD, 默认20250430):{Style.RESET_ALL} ") or "20250430"
            
            try:
                start_date, end_date = DateHelper.parse_date_input(date_input)
                if start_date != end_date:
                    console.print_info(f"将处理日期范围: {start_date} 至 {end_date}")
            except ValueError as e:
                console.print_error(f"日期格式错误: {e}")
                continue
                
            count = int(input(f"{Fore.YELLOW}处理数量 (默认100):{Style.RESET_ALL} ") or "100")
            
            processor.content_filter.enabled_core_types = ['第一季度报告', '第三季度报告']
            processor.content_filter.enabled_extended_types = []
            
            processor.process_unprocessed_announcements(
                start_date=start_date,
                end_date=end_date,
                use_content_filter=True,
                max_count=count,
                task_type="季度报告处理"
            )
            
        elif choice == '4':
            days = int(input(f"{Fore.YELLOW}最近几天 (默认7):{Style.RESET_ALL} ") or "7")
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            processor.process_unprocessed_announcements(
                start_date=start_date.strftime('%Y%m%d'),
                end_date=end_date.strftime('%Y%m%d'),
                use_content_filter=True,
                max_count=50,
                task_type="最近公告处理(带过滤)"
            )
            
        elif choice == '5':
            days = int(input(f"{Fore.YELLOW}最近几天 (默认7):{Style.RESET_ALL} ") or "7")
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            processor.process_unprocessed_announcements(
                start_date=start_date.strftime('%Y%m%d'),
                end_date=end_date.strftime('%Y%m%d'),
                use_content_filter=False,
                max_count=50,
                task_type="最近公告处理(无过滤)"
            )
            
        elif choice == '6':
            start_input = input(f"{Fore.YELLOW}开始日期 (YYYYMMDD 或 YYYYMMDD-YYYYMMDD):{Style.RESET_ALL} ")
            
            try:
                # 如果输入了范围格式，直接解析
                if '-' in start_input:
                    start, end = DateHelper.parse_date_input(start_input)
                else:
                    # 传统的两次输入方式
                    start = start_input
                    end = input(f"{Fore.YELLOW}结束日期 (YYYYMMDD):{Style.RESET_ALL} ")
            except ValueError as e:
                console.print_error(f"日期格式错误: {e}")
                continue
                
            use_filter = input(f"{Fore.YELLOW}使用内容过滤? (y/n):{Style.RESET_ALL} ").lower() == 'y'
            count = int(input(f"{Fore.YELLOW}最大数量:{Style.RESET_ALL} ") or "50")
            
            processor.process_unprocessed_announcements(
                start_date=start,
                end_date=end,
                use_content_filter=use_filter,
                max_count=count,
                task_type="自定义处理"
            )
            
        elif choice == '7':
            console.print_header(f"需要OCR的文件 (共{len(processor.ocr_failed_list)}个)")
            
            for i, record in enumerate(processor.ocr_failed_list[-10:]):
                print(f"\n{Fore.CYAN}{i + 1}. {record['ts_code']} - {record['name']}{Style.RESET_ALL}")
                print(f"   标题: {record['title'][:60]}...")
                print(f"   PDF: {record['pdf_path']}")
                print(f"   记录时间: {record['recorded_time']}")
                
            if len(processor.ocr_failed_list) > 10:
                console.print_info(f"... 还有 {len(processor.ocr_failed_list) - 10} 个")
                
        elif choice == '8':
            processor.export_performance_data()
            
        elif choice == '9':
            console.print_header("性能模式设置")
            print(f"\n当前模式: {Fore.GREEN}{processor.performance_mode}{Style.RESET_ALL}")
            print("\n可选模式:")
            print("  1. aggressive - 激进模式（无休眠，最大速度）")
            print("  2. normal - 正常模式（智能限流）")
            print("  3. conservative - 保守模式（主动保护）")
            
            mode_choice = input(f"\n{Fore.YELLOW}选择模式 (1-3):{Style.RESET_ALL} ")
            if mode_choice == '1':
                processor.set_performance_mode('aggressive')
            elif mode_choice == '2':
                processor.set_performance_mode('normal')
            elif mode_choice == '3':
                processor.set_performance_mode('conservative')
                
        elif choice == '0':
            console.print_info("感谢使用，再见！")
            break
        
        # 等待用户按键继续
        input(f"\n{Fore.CYAN}按回车键继续...{Style.RESET_ALL}")
            

if __name__ == "__main__":
    main()
