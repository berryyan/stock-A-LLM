"""
文档处理模块
负责处理上市公司公告的下载、解析和向量化
"""
import os
import re
import time
import random
import hashlib
from pathlib import Path
from typing import List, Dict, Tuple, Optional, Any
from datetime import datetime
from urllib.parse import urlparse, parse_qs
import logging

import requests
import pandas as pd
from tqdm import tqdm
import pdfplumber
import PyPDF2
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document

from config.settings import settings
from database.mysql_connector import MySQLConnector
from database.milvus_connector import MilvusConnector
from models.embedding_model import EmbeddingModel
from utils.logger import setup_logger


class PDFDownloadError(Exception):
    """PDF下载错误"""
    pass


class DocumentProcessor:
    """文档处理器：负责公告的下载、解析和向量化"""
    
    def __init__(self):
        self.logger = setup_logger("document_processor")
        self.mysql_conn = MySQLConnector()
        self.milvus_conn = MilvusConnector()
        self.embedding_model = EmbeddingModel()
        
        # 文本分割器
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=settings.CHUNK_SIZE,
            chunk_overlap=settings.CHUNK_OVERLAP,
            separators=["\n\n", "\n", "。", "！", "？", "；", "，", " ", ""],
            length_function=len,
        )
        
        # 创建缓存目录
        self.pdf_cache_dir = settings.PDF_STORAGE_PATH / "cache"
        self.pdf_cache_dir.mkdir(parents=True, exist_ok=True)
        
        # 下载重试配置
        self.max_retries = 3
        self.retry_delay = 2
        
        # HTTP请求头
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'application/pdf,*/*',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
        }
        
        # 会话对象（延迟初始化）
        self._session = None
        self._session_initialized = False
        
        self.logger.info("文档处理器初始化完成")
    
    def _get_session(self, need_init=False):
        """获取请求会话，按需初始化"""
        if self._session is None:
            self._session = requests.Session()
            self._session.headers.update(self.headers)
        
        if need_init and not self._session_initialized:
            self._init_session()
            
        return self._session
    
    def _init_session(self):
        """初始化会话，访问主站获取cookies"""
        try:
            self.logger.info("初始化会话，访问巨潮主站...")
            session = self._get_session(need_init=False)
            response = session.get('https://www.cninfo.com.cn', timeout=10)
            if response.status_code == 200:
                self.logger.info("成功访问主站，获取cookies")
                self._session_initialized = True
                # 小延迟，模拟正常浏览行为
                time.sleep(random.uniform(0.5, 1.0))
                return True
            else:
                self.logger.warning(f"访问主站失败，状态码: {response.status_code}")
                return False
        except Exception as e:
            self.logger.error(f"初始化会话失败: {e}")
            return False
    
    def extract_params_from_url(self, url: str) -> Tuple[str, str, str]:
        """
        从cninfo URL中提取参数
        
        Args:
            url: cninfo公告页面URL
            
        Returns:
            (stock_code, announcement_id, announcement_time)
        """
        try:
            parsed_url = urlparse(url)
            query_params = parse_qs(parsed_url.query)
            
            stock_code = query_params.get('stockCode', [None])[0]
            announcement_id = query_params.get('announcementId', [None])[0]
            announcement_time = query_params.get('announcementTime', [None])[0]
            
            if not all([stock_code, announcement_id, announcement_time]):
                raise ValueError(f"无法从URL中提取所有必要的参数: {url}")
            
            return stock_code, announcement_id, announcement_time
        except Exception as e:
            self.logger.error(f"解析URL失败: {url}, 错误: {e}")
            raise
    
    def construct_pdf_url(self, stock_code: str, announcement_id: str, 
                         announcement_time: str) -> str:
        """
        构造PDF下载链接
        
        Args:
            stock_code: 股票代码
            announcement_id: 公告ID
            announcement_time: 公告时间 (格式: YYYY-MM-DD)
            
        Returns:
            PDF下载链接
        """
        base_url = "https://static.cninfo.com.cn/finalpage"
        pdf_url = f"{base_url}/{announcement_time}/{announcement_id}.pdf"
        return pdf_url
    
    def _try_download_pdf(self, url: str, save_path: Path, use_session=False) -> Tuple[bool, Optional[str]]:
        """
        尝试下载PDF文件（单次尝试）
        
        Args:
            url: PDF下载链接
            save_path: 保存路径
            use_session: 是否使用会话（带cookies）
            
        Returns:
            (是否成功, 错误信息)
        """
        try:
            self.logger.debug(f"尝试下载: {url} (use_session={use_session})")
            
            # 选择使用session还是普通requests
            if use_session:
                session = self._get_session(need_init=True)
                response = session.get(
                    url, 
                    timeout=30,
                    stream=True,
                    allow_redirects=True
                )
            else:
                # 普通请求，不使用session
                response = requests.get(
                    url, 
                    headers=self.headers, 
                    timeout=30,
                    stream=True,
                    allow_redirects=True
                )
            
            if response.status_code == 200:
                # 检查Content-Type
                content_type = response.headers.get('content-type', '')
                if 'pdf' not in content_type.lower() and 'octet-stream' not in content_type.lower():
                    self.logger.warning(f"Content-Type不是PDF: {content_type}")
                
                # 流式写入文件
                with open(save_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                
                # 验证文件是否为PDF
                if save_path.stat().st_size > 0:
                    with open(save_path, 'rb') as f:
                        header = f.read(4)
                        if header.startswith(b'%PDF'):
                            self.logger.info(f"PDF下载成功: {save_path}")
                            return True, None
                        else:
                            os.remove(save_path)
                            return False, "下载的文件不是有效的PDF"
                else:
                    os.remove(save_path)
                    return False, "下载的文件为空"
                    
            elif response.status_code == 404:
                return False, f"404 Not Found: {url}"
            else:
                return False, f"HTTP {response.status_code}: {url}"
                
        except requests.exceptions.Timeout:
            return False, f"请求超时: {url}"
        except requests.exceptions.ConnectionError:
            return False, f"连接错误: {url}"
        except requests.exceptions.RequestException as e:
            return False, f"请求异常: {type(e).__name__}: {str(e)}"
        except Exception as e:
            return False, f"未知错误: {type(e).__name__}: {str(e)}"
        finally:
            if 'response' in locals():
                response.close()
    
    def download_pdf(self, pdf_url: str, save_path: Path, 
                    max_retries: Optional[int] = None) -> bool:
        """
        下载PDF文件，智能处理大小写问题和会话初始化
        
        策略：
        1. 先尝试原始URL（不使用session）
        2. 如果失败，尝试大小写变体（不使用session）
        3. 如果还失败，使用session重试所有变体
        
        Args:
            pdf_url: PDF下载链接
            save_path: 保存路径
            max_retries: 最大重试次数
            
        Returns:
            是否下载成功
            
        Raises:
            PDFDownloadError: 下载失败时抛出详细错误
        """
        if max_retries is None:
            max_retries = self.max_retries
        
        # 如果文件已存在，跳过下载
        if save_path.exists() and save_path.stat().st_size > 0:
            self.logger.info(f"PDF文件已存在，跳过下载: {save_path}")
            return True
        
        # 确保目录存在
        save_path.parent.mkdir(parents=True, exist_ok=True)
        
        # 记录所有尝试的结果
        all_attempts = []
        
        # 阶段1：尝试原始URL（不使用session）
        self.logger.info(f"阶段1：尝试原始URL: {pdf_url}")
        for attempt in range(max_retries):
            success, error_msg = self._try_download_pdf(pdf_url, save_path, use_session=False)
            
            if success:
                return True
                
            all_attempts.append({
                'phase': 1,
                'url': pdf_url,
                'attempt': attempt + 1,
                'error': error_msg,
                'use_session': False
            })
            
            # 如果不是404错误，继续重试
            if "404" not in error_msg and attempt < max_retries - 1:
                wait_time = self.retry_delay * (attempt + 1)
                self.logger.info(f"等待 {wait_time} 秒后重试...")
                time.sleep(wait_time)
            else:
                break
        
        # 阶段2：如果原始URL失败，尝试大小写变体（不使用session）
        if "404" in all_attempts[-1]['error']:
            # 生成大小写变体
            url_variant = None
            if pdf_url.endswith('.pdf'):
                url_variant = pdf_url[:-4] + '.PDF'
            elif pdf_url.endswith('.PDF'):
                url_variant = pdf_url[:-4] + '.pdf'
            
            if url_variant:
                self.logger.info(f"阶段2：尝试大小写变体: {url_variant}")
                for attempt in range(max_retries):
                    success, error_msg = self._try_download_pdf(url_variant, save_path, use_session=False)
                    
                    if success:
                        return True
                        
                    all_attempts.append({
                        'phase': 2,
                        'url': url_variant,
                        'attempt': attempt + 1,
                        'error': error_msg,
                        'use_session': False
                    })
                    
                    if "404" not in error_msg and attempt < max_retries - 1:
                        wait_time = self.retry_delay * (attempt + 1)
                        self.logger.info(f"等待 {wait_time} 秒后重试...")
                        time.sleep(wait_time)
                    else:
                        break
        
        # 阶段3：如果都失败了，使用session（访问主站后）重试
        self.logger.info("阶段3：使用会话重试所有URL变体")
        
        # 生成所有可能的URL
        urls_to_try = [pdf_url]
        if pdf_url.endswith('.pdf'):
            urls_to_try.append(pdf_url[:-4] + '.PDF')
        elif pdf_url.endswith('.PDF'):
            urls_to_try.append(pdf_url[:-4] + '.pdf')
        
        for url_variant in urls_to_try:
            self.logger.info(f"使用会话尝试: {url_variant}")
            success, error_msg = self._try_download_pdf(url_variant, save_path, use_session=True)
            
            if success:
                return True
                
            all_attempts.append({
                'phase': 3,
                'url': url_variant,
                'attempt': 1,
                'error': error_msg,
                'use_session': True
            })
        
        # 构建详细的错误信息
        error_details = []
        for attempt in all_attempts:
            error_details.append(
                f"阶段{attempt['phase']}: URL: {attempt['url']}, "
                f"尝试: {attempt['attempt']}, Session: {attempt['use_session']}, "
                f"错误: {attempt['error']}"
            )
        
        error_msg = f"PDF下载失败: {pdf_url}\n所有尝试详情:\n" + "\n".join(error_details)
        self.logger.error(error_msg)
        
        # 抛出详细异常
        raise PDFDownloadError(error_msg)
    
    def extract_text_from_pdf(self, pdf_path: Path) -> str:
        """
        从PDF中提取文本，优先使用pdfplumber，失败时使用PyPDF2
        
        Args:
            pdf_path: PDF文件路径
            
        Returns:
            提取的文本内容
        """
        text = ""
        
        # 首先尝试使用pdfplumber
        try:
            with pdfplumber.open(pdf_path) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
            
            if text.strip():
                self.logger.info(f"使用pdfplumber成功提取文本: {pdf_path}")
                return text
        except Exception as e:
            self.logger.warning(f"pdfplumber提取失败: {e}")
        
        # 如果pdfplumber失败，尝试PyPDF2
        try:
            with open(pdf_path, 'rb') as f:
                pdf_reader = PyPDF2.PdfReader(f)
                for page_num in range(len(pdf_reader.pages)):
                    page = pdf_reader.pages[page_num]
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
            
            if text.strip():
                self.logger.info(f"使用PyPDF2成功提取文本: {pdf_path}")
                return text
        except Exception as e:
            self.logger.error(f"PyPDF2提取失败: {e}")
        
        # 如果两种方法都失败
        if not text.strip():
            self.logger.error(f"无法从PDF提取文本: {pdf_path}")
            raise ValueError(f"无法从PDF提取文本: {pdf_path}")
        
        return text
    
    def clean_text(self, text: str) -> str:
        """
        清理文本内容
        
        Args:
            text: 原始文本
            
        Returns:
            清理后的文本
        """
        # 移除多余的空白字符
        text = re.sub(r'\s+', ' ', text)
        # 移除特殊字符
        text = re.sub(r'[^\u4e00-\u9fa5a-zA-Z0-9\s\.\,\!\?\-\+\*\/\=\(\)\[\]\{\}\:\;\"\'\%]', '', text)
        # 移除多个连续的标点符号
        text = re.sub(r'[。，！？；：]{2,}', '。', text)
        return text.strip()
    
    def create_document_chunks(self, text: str, metadata: Dict[str, Any]) -> List[Document]:
        """
        将文本分割成chunks并创建Document对象
        
        Args:
            text: 文本内容
            metadata: 元数据
            
        Returns:
            Document对象列表
        """
        # 清理文本
        cleaned_text = self.clean_text(text)
        
        # 分割文本
        chunks = self.text_splitter.split_text(cleaned_text)
        
        # 创建Document对象
        documents = []
        for i, chunk in enumerate(chunks):
            chunk_metadata = metadata.copy()
            chunk_metadata['chunk_id'] = i
            chunk_metadata['total_chunks'] = len(chunks)
            
            doc = Document(
                page_content=chunk,
                metadata=chunk_metadata
            )
            documents.append(doc)
        
        self.logger.info(f"文本分割完成，共 {len(documents)} 个chunks")
        return documents
    
    def process_announcement(self, announcement: Dict[str, Any]) -> Optional[List[Document]]:
        """
        处理单个公告
        
        Args:
            announcement: 公告信息字典
            
        Returns:
            Document对象列表，失败返回None
        """
        try:
            # 提取公告信息
            ts_code = announcement['ts_code']
            name = announcement['name']
            title = announcement['title']
            url = announcement['url']
            ann_date = announcement['ann_date']
            
            # 清理name和title
            name = re.sub(r'\s+', '', name)
            title = re.sub(r'\s+', '', title)
            
            self.logger.info(f"处理公告: {ts_code} - {title}")
            
            # 提取URL参数
            stock_code, announcement_id, announcement_time = self.extract_params_from_url(url)
            
            # 构造PDF URL
            pdf_url = self.construct_pdf_url(stock_code, announcement_id, announcement_time)
            
            # 生成缓存文件名（使用MD5避免文件名过长）
            file_key = f"{announcement_time}_{stock_code}_{announcement_id}"
            file_hash = hashlib.md5(file_key.encode()).hexdigest()[:8]
            pdf_filename = f"{ann_date}_{stock_code}_{file_hash}.pdf"
            pdf_path = self.pdf_cache_dir / pdf_filename
            
            # 下载PDF（使用新的异常处理机制）
            try:
                self.download_pdf(pdf_url, pdf_path)
            except PDFDownloadError as e:
                self.logger.error(f"PDF下载失败: {e}")
                return None
            
            # 提取文本
            text = self.extract_text_from_pdf(pdf_path)
            
            # 创建元数据
            metadata = {
                'ts_code': ts_code,
                'stock_code': stock_code,
                'company_name': name,
                'title': title,
                'ann_date': str(ann_date) if not isinstance(ann_date, str) else ann_date,
                'announcement_id': announcement_id,
                'url': url,
                'pdf_url': pdf_url,
                'pdf_path': str(pdf_path),
                'process_time': datetime.now().isoformat()
            }
            
            # 创建文档chunks
            documents = self.create_document_chunks(text, metadata)
            
            return documents
            
        except Exception as e:
            self.logger.error(f"处理公告失败: {e}, URL: {announcement.get('url', 'N/A')}")
            return None
    
    def batch_process_announcements(self, 
                                  start_date: str, 
                                  end_date: str,
                                  ts_codes: Optional[List[str]] = None,
                                  title_keywords: Optional[List[str]] = None,
                                  batch_size: int = 10,
                                  sleep_range: Tuple[int, int] = (2, 5)) -> int:
        """
        批量处理公告
        
        Args:
            start_date: 开始日期 (YYYYMMDD)
            end_date: 结束日期 (YYYYMMDD)
            ts_codes: 股票代码列表（可选）
            title_keywords: 标题关键词列表（可选）
            batch_size: 批次大小
            sleep_range: 随机睡眠时间范围
            
        Returns:
            处理成功的公告数量
        """
        # 查询公告
        query = f"""
        SELECT ts_code, name, title, url, ann_date
        FROM tu_anns_d
        WHERE ann_date BETWEEN '{start_date}' AND '{end_date}'
        """
        
        if ts_codes:
            codes_str = "','".join(ts_codes)
            query += f" AND ts_code IN ('{codes_str}')"
        
        announcements = self.mysql_conn.execute_query(query)
        
        # 过滤标题关键词
        if title_keywords:
            filtered_announcements = []
            for ann in announcements:
                if any(keyword in ann['title'] for keyword in title_keywords):
                    filtered_announcements.append(ann)
            announcements = filtered_announcements
        
        self.logger.info(f"查询到 {len(announcements)} 条公告待处理")
        
        # 批量处理
        success_count = 0
        all_documents = []
        
        for i in tqdm(range(0, len(announcements), batch_size), desc="处理批次"):
            batch = announcements[i:i+batch_size]
            batch_documents = []
            
            for ann in batch:
                docs = self.process_announcement(ann)
                if docs:
                    batch_documents.extend(docs)
                    success_count += 1
                
                # 随机睡眠
                time.sleep(random.uniform(*sleep_range))
            
            # 批量向量化和存储
            if batch_documents:
                self.store_documents_to_milvus(batch_documents)
                all_documents.extend(batch_documents)
            
            self.logger.info(f"完成批次 {i//batch_size + 1}, 成功处理 {len(batch_documents)} 个文档")
        
        self.logger.info(f"批量处理完成，成功处理 {success_count}/{len(announcements)} 条公告")
        return success_count
    
    def store_documents_to_milvus(self, documents: List[Document]) -> bool:
        """
        将文档存储到Milvus向量数据库
        
        Args:
            documents: Document对象列表
            
        Returns:
            是否存储成功
        """
        try:
            # 提取文本和元数据
            texts = [doc.page_content for doc in documents]
            metadatas = [doc.metadata for doc in documents]
            
            # 批量生成向量
            embeddings = self.embedding_model.encode_batch(texts)
            
            # 准备数据
            data = []
            for i, (text, embedding, metadata) in enumerate(zip(texts, embeddings, metadatas)):
                # 生成唯一ID
                doc_id = f"{metadata['announcement_id']}_{metadata['chunk_id']}"
                
                # 处理embedding格式
                if hasattr(embedding, 'tolist'):
                    embedding_list = embedding.tolist()
                else:
                    embedding_list = embedding  # 已经是list格式
                
                data.append({
                    'id': doc_id,
                    'embedding': embedding_list,
                    'text': text,
                    'ts_code': metadata['ts_code'],
                    'company_name': metadata['company_name'],
                    'title': metadata['title'],
                    'ann_date': str(metadata['ann_date']) if not isinstance(metadata['ann_date'], str) else metadata['ann_date'],
                    'chunk_id': metadata['chunk_id'],
                    'metadata': str(metadata)  # 存储完整元数据的JSON字符串
                })
            
            # 插入到Milvus
            self.milvus_conn.insert_data(data)
            self.logger.info(f"成功存储 {len(data)} 个向量到Milvus")
            return True
            
        except Exception as e:
            self.logger.error(f"存储到Milvus失败: {e}")
            return False
    
    def search_similar_documents(self, 
                                query: str, 
                                top_k: int = 5,
                                ts_codes: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """
        搜索相似文档
        
        Args:
            query: 查询文本
            top_k: 返回结果数量
            ts_codes: 限定股票代码（可选）
            
        Returns:
            相似文档列表
        """
        # 生成查询向量
        query_embedding = self.embedding_model.encode(query)
        
        # 构建过滤条件
        filter_expr = None
        if ts_codes:
            codes_str = "','".join(ts_codes)
            filter_expr = f"ts_code in ['{codes_str}']"
        
        # 搜索
        results = self.milvus_conn.search(
            query_vectors=[query_embedding.tolist()],
            top_k=top_k,
            filter_expr=filter_expr
        )
        
        return results
    
    def update_announcement_vectors(self, announcement_ids: List[str]) -> int:
        """
        更新指定公告的向量
        
        Args:
            announcement_ids: 公告ID列表
            
        Returns:
            更新成功的数量
        """
        # 查询公告信息
        ids_str = "','".join(announcement_ids)
        query = f"""
        SELECT ts_code, name, title, url, ann_date
        FROM tu_anns_d
        WHERE announcement_id IN ('{ids_str}')
        """
        
        announcements = self.mysql_conn.execute_query(query)
        
        # 删除旧向量
        for ann_id in announcement_ids:
            self.milvus_conn.delete_by_expr(f"announcement_id == '{ann_id}'")
        
        # 重新处理和存储
        success_count = 0
        for ann in announcements:
            docs = self.process_announcement(ann)
            if docs:
                self.store_documents_to_milvus(docs)
                success_count += 1
        
        return success_count


# 使用示例
if __name__ == "__main__":
    # 初始化处理器
    processor = DocumentProcessor()
    
    # 测试单个URL
    test_url = "https://static.cninfo.com.cn/finalpage/2025-04-23/1223214399.pdf"
    test_path = Path("test_download.pdf")
    
    try:
        processor.download_pdf(test_url, test_path)
        print("下载成功！")
    except PDFDownloadError as e:
        print(f"下载失败: {e}")
