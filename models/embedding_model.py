# models/embedding_model.py
"""
BGE-M3 嵌入模型模块
提供文本向量化功能
"""

import torch
import numpy as np
from typing import List, Union, Optional
from sentence_transformers import SentenceTransformer
import logging
from config.settings import settings
import warnings
import os

# 设置环境变量以避免警告
os.environ['TOKENIZERS_PARALLELISM'] = 'false'
warnings.filterwarnings('ignore', category=FutureWarning)

logger = logging.getLogger(__name__)

class EmbeddingModel:
    """BGE-M3 嵌入模型封装"""
    
    def __init__(self, model_name: Optional[str] = None, device: Optional[str] = None):
        """
        初始化嵌入模型
        
        Args:
            model_name: 模型名称，默认使用配置文件中的设置
            device: 运行设备，默认使用配置文件中的设置
        """
        self.model_name = model_name or settings.EMBEDDING_MODEL_NAME
        self.device = device or settings.EMBEDDING_DEVICE
        self.model = None
        self.dimension = settings.EMBEDDING_DIM
        
        # 初始化模型
        self._init_model()
    
    def _init_model(self):
        """初始化模型（Windows兼容版本）"""
        try:
            # 检查是否有本地模型
            import os
            import platform
            import threading
            
            local_model_path = os.path.join(os.path.dirname(__file__), "bge-m3")
            if os.path.exists(local_model_path):
                logger.info(f"发现本地模型: {local_model_path}")
                model_name_to_use = local_model_path
            else:
                model_name_to_use = self.model_name
            
            logger.info(f"正在加载嵌入模型: {model_name_to_use}")
            logger.info(f"使用设备: {self.device}")
            
            # Windows兼容的超时处理
            model_loaded = False
            load_error = None
            
            def load_model():
                nonlocal model_loaded, load_error
                try:
                    self.model = SentenceTransformer(
                        model_name_to_use,
                        device=self.device,
                        trust_remote_code=True
                    )
                    model_loaded = True
                except Exception as e:
                    load_error = e
            
            # 启动模型加载线程
            load_thread = threading.Thread(target=load_model)
            load_thread.daemon = True
            load_thread.start()
            
            # 等待60秒
            load_thread.join(timeout=60)
            
            if not model_loaded:
                if load_error:
                    raise load_error
                else:
                    raise TimeoutError("模型加载超时(60秒)")
            
            # 设置模型为评估模式
            self.model.eval()
            
            # 验证模型维度（带超时保护）
            test_embedding = None
            test_error = None
            
            def test_encode():
                nonlocal test_embedding, test_error
                try:
                    test_embedding = self.model.encode("测试文本", convert_to_numpy=True)
                except Exception as e:
                    test_error = e
            
            # 启动测试编码线程
            test_thread = threading.Thread(target=test_encode)
            test_thread.daemon = True
            test_thread.start()
            
            # 等待30秒
            test_thread.join(timeout=30)
            
            if test_error:
                raise test_error
            elif test_embedding is None:
                raise TimeoutError("模型测试编码超时(30秒)")
            
            actual_dim = test_embedding.shape[0]
            
            if actual_dim != self.dimension:
                logger.warning(f"模型实际维度 {actual_dim} 与配置维度 {self.dimension} 不匹配")
                self.dimension = actual_dim
                settings.EMBEDDING_DIM = actual_dim
            
            logger.info(f"模型加载成功，向量维度: {self.dimension}")
            
        except Exception as e:
            logger.error(f"模型加载失败: {e}")
            raise
    
    def encode(
        self, 
        texts: Union[str, List[str]], 
        batch_size: int = 32,
        show_progress_bar: bool = False,
        normalize_embeddings: bool = True,
        convert_to_numpy: bool = True
    ) -> Union[np.ndarray, List[np.ndarray]]:
        """
        将文本编码为向量
        
        Args:
            texts: 单个文本或文本列表
            batch_size: 批处理大小
            show_progress_bar: 是否显示进度条
            normalize_embeddings: 是否归一化向量
            convert_to_numpy: 是否转换为 numpy 数组
            
        Returns:
            文本向量或向量列表
        """
        if self.model is None:
            raise RuntimeError("模型未初始化")
        
        # 处理单个文本
        is_single = isinstance(texts, str)
        if is_single:
            texts = [texts]
        
        # 检查空文本
        if not texts or all(not text.strip() for text in texts):
            logger.warning("输入文本为空")
            empty_embedding = np.zeros(self.dimension)
            return empty_embedding if is_single else [empty_embedding]
        
        try:
            # Windows兼容的编码超时处理
            import threading
            encode_result = None
            encode_error = None
            
            def encode_texts():
                nonlocal encode_result, encode_error
                try:
                    encode_result = self.model.encode(
                        texts,
                        batch_size=batch_size,
                        show_progress_bar=show_progress_bar,
                        normalize_embeddings=normalize_embeddings,
                        convert_to_numpy=convert_to_numpy,
                        device=self.device
                    )
                except Exception as e:
                    encode_error = e
            
            # 启动编码线程
            encode_thread = threading.Thread(target=encode_texts)
            encode_thread.daemon = True
            encode_thread.start()
            
            # 等待30秒
            encode_thread.join(timeout=30)
            
            if encode_error:
                raise encode_error
            elif encode_result is None:
                raise TimeoutError(f"文本编码超时(30秒): {len(texts)}个文本")
            
            # 确保返回正确的格式
            if is_single:
                return encode_result[0]
            return encode_result
            
        except Exception as e:
            logger.error(f"文本编码失败: {e}")
            raise
    
    def encode_batch(
        self,
        texts: List[str],
        batch_size: int = 32,
        show_progress_bar: bool = True
    ) -> List[List[float]]:
        """
        批量编码文本（优化版本）
        
        Args:
            texts: 文本列表
            batch_size: 批处理大小
            show_progress_bar: 是否显示进度条
            
        Returns:
            向量列表（浮点数列表的列表）
        """
        if not texts:
            return []
        
        # 过滤空文本
        valid_indices = []
        valid_texts = []
        for i, text in enumerate(texts):
            if text and text.strip():
                valid_indices.append(i)
                valid_texts.append(text)
        
        if not valid_texts:
            logger.warning("所有文本都为空")
            return [[0.0] * self.dimension for _ in texts]
        
        # 编码有效文本
        embeddings = self.encode(
            valid_texts,
            batch_size=batch_size,
            show_progress_bar=show_progress_bar,
            normalize_embeddings=True,
            convert_to_numpy=True
        )
        
        # 构建结果，为空文本填充零向量
        result = []
        valid_idx = 0
        for i in range(len(texts)):
            if i in valid_indices:
                result.append(embeddings[valid_idx].tolist())
                valid_idx += 1
            else:
                result.append([0.0] * self.dimension)
        
        return result
    
    def compute_similarity(
        self,
        text1: Union[str, np.ndarray],
        text2: Union[str, np.ndarray]
    ) -> float:
        """
        计算两个文本的相似度
        
        Args:
            text1: 第一个文本或向量
            text2: 第二个文本或向量
            
        Returns:
            相似度分数（0-1）
        """
        # 如果输入是文本，先编码
        if isinstance(text1, str):
            vec1 = self.encode(text1, normalize_embeddings=True)
        else:
            vec1 = text1 / np.linalg.norm(text1)
        
        if isinstance(text2, str):
            vec2 = self.encode(text2, normalize_embeddings=True)
        else:
            vec2 = text2 / np.linalg.norm(text2)
        
        # 计算余弦相似度
        similarity = np.dot(vec1, vec2)
        
        # 确保结果在 [0, 1] 范围内
        return float(max(0, min(1, similarity)))
    
    def get_dimension(self) -> int:
        """获取向量维度"""
        return self.dimension
    
    def save_model(self, path: str):
        """保存模型到本地"""
        if self.model:
            self.model.save(path)
            logger.info(f"模型已保存到: {path}")
    
    @property
    def device_type(self) -> str:
        """获取设备类型"""
        return self.device

# 创建全局实例（延迟加载）
_embedding_model = None

def get_embedding_model() -> EmbeddingModel:
    """获取嵌入模型实例（单例模式）"""
    global _embedding_model
    if _embedding_model is None:
        _embedding_model = EmbeddingModel()
    return _embedding_model

# 便捷函数
def encode_text(text: Union[str, List[str]], **kwargs) -> Union[np.ndarray, List[np.ndarray]]:
    """便捷的文本编码函数"""
    model = get_embedding_model()
    return model.encode(text, **kwargs)

def batch_encode_texts(texts: List[str], **kwargs) -> List[List[float]]:
    """便捷的批量编码函数"""
    model = get_embedding_model()
    return model.encode_batch(texts, **kwargs)