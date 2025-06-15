# config/settings.py
import os
from pathlib import Path
from dotenv import load_dotenv
from urllib.parse import quote_plus

# 加载环境变量
load_dotenv()

class Settings:
    """系统配置类"""
    
    # MySQL配置
    MYSQL_HOST = os.getenv("MYSQL_HOST", "10.0.0.77")
    MYSQL_PORT = int(os.getenv("MYSQL_PORT", 3306))
    MYSQL_DATABASE = os.getenv("MYSQL_DATABASE", "Tushare")
    MYSQL_USER = os.getenv("MYSQL_USER", "readonly_user")
    MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", "")

    # MySQL连接URL - 不需要特殊处理了
    MYSQL_URL = f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DATABASE}"
    
    # Milvus配置
    MILVUS_HOST = os.getenv("MILVUS_HOST", "10.0.0.77")
    MILVUS_PORT = int(os.getenv("MILVUS_PORT", 19530))
    MILVUS_USER = os.getenv("MILVUS_USER", "root")
    MILVUS_PASSWORD = os.getenv("MILVUS_PASSWORD", "Milvus")
    MILVUS_COLLECTION_NAME = os.getenv("MILVUS_COLLECTION_NAME", "stock_announcements")
    
    # LLM配置
    DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "")
    DEEPSEEK_BASE_URL = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com/v1")
    DASHSCOPE_API_KEY = os.getenv("DASHSCOPE_API_KEY", "")
    
    # 文件路径配置
    PDF_STORAGE_PATH = Path(os.getenv("PDF_STORAGE_PATH", "./data/pdfs"))
    VECTOR_DB_PATH = Path(os.getenv("VECTOR_DB_PATH", "./data/milvus"))
    
    # 确保目录存在
    PDF_STORAGE_PATH.mkdir(parents=True, exist_ok=True)
    VECTOR_DB_PATH.mkdir(parents=True, exist_ok=True)
    
    # 系统配置
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    MAX_WORKERS = int(os.getenv("MAX_WORKERS", 4))
    
    # 文本处理配置
    CHUNK_SIZE = 1000
    CHUNK_OVERLAP = 200
    
    # 数据库连接池配置
    DB_POOL_SIZE = 20
    DB_MAX_OVERFLOW = 30
    DB_POOL_TIMEOUT = 30
    
    # 嵌入模型配置
    EMBEDDING_MODEL_NAME = "BAAI/bge-m3"
    EMBEDDING_DEVICE = "cuda" if os.getenv("USE_GPU", "false").lower() == "true" else "cpu"
    EMBEDDING_DIM = 1024  # BGE-M3 的向量维度
    
    # 查询配置
    DEFAULT_TOP_K = 5
    DEFAULT_SCORE_THRESHOLD = 0.7

    # ========== 内容过滤配置（基于分析结果优化） ==========
    # 默认启用的核心报告类型
    ENABLED_CORE_TYPES = [
        '年度报告',
        '年度报告摘要',
        '第一季度报告',
        '半年度报告',
        '第三季度报告',
        '业绩预告',
        '业绩快报'
    ]

    # 默认启用的扩展内容类型（保守策略）
    ENABLED_EXTENDED_TYPES = [
        '问询回复',  # 监管问询回复
        '利润分配'  # 分红实施公告
    ]

    # ========== 性能监控配置 ==========
    # 性能日志文件
    PERFORMANCE_LOG_FILE = os.path.join(os.path.dirname(PDF_STORAGE_PATH), "performance_log.json")

    # OCR失败记录文件
    OCR_FAILED_LOG = os.path.join(os.path.dirname(PDF_STORAGE_PATH), "ocr_needed_files.json")

    # 处理超时配置（秒）
    DOWNLOAD_TIMEOUT = 30
    PDF_EXTRACT_TIMEOUT = 120  # PDF解析可能需要更长时间

    # 批处理配置
    DEFAULT_BATCH_SIZE = 10

    # 休眠时间配置（根据时段）
    SLEEP_TIME_CONFIG = {
        'night': (0, 6, 5),  # 0-6点：5秒
        'morning': (6, 9, 10),  # 6-9点：10秒
        'work': (9, 17, 20),  # 9-17点：20秒（工作时间保守）
        'evening': (17, 22, 10),  # 17-22点：10秒
        'late': (22, 24, 5)  # 22-24点：5秒
    }

settings = Settings()