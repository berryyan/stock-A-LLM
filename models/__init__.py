# models/__init__.py
"""
模型模块
"""

from .embedding_model import (
    EmbeddingModel,
    get_embedding_model,
    encode_text,
    batch_encode_texts
)

__all__ = [
    'EmbeddingModel',
    'get_embedding_model',
    'encode_text',
    'batch_encode_texts'
]