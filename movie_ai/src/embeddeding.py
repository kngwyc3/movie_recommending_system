"""
Embedding 处理模块
负责将文本转换为向量表示
"""
import os
from typing import List, Union
import numpy as np
from sentence_transformers import SentenceTransformer
from src.config import Config


class EmbeddingService:
    """Embedding 服务类"""
    
    def __init__(self):
        """初始化 Embedding 服务"""
        self.model = None
        self.device = Config.EMBEDDING_DEVICE
        self.dimension = Config.EMBEDDING_DIMENSION
        
    def load_model(self):
        """加载 embedding 模型（仅从本地加载）"""
        if self.model is None:
            self.model = SentenceTransformer(
                Config.EMBEDDING_MODEL_NAME,
                device=self.device
            )
        return self.model
    
    def encode(self, texts: Union[str, List[str]], batch_size: int = 32) -> np.ndarray:
        """
        将文本转换为向量
        
        Args:
            texts: 单个文本或文本列表
            batch_size: 批处理大小
            
        Returns:
            嵌入向量，形状为 (n_samples, embedding_dim)
        """
        if self.model is None:
            self.load_model()
        
        # 转换为列表格式
        if isinstance(texts, str):
            texts = [texts]
        
        # 生成 embeddings
        embeddings = self.model.encode(
            texts,
            batch_size=batch_size,
            show_progress_bar=False,
            convert_to_numpy=True,
            normalize_embeddings=True  # 归一化
        )
        
        return embeddings
    
    def encode_documents(self, documents: List[str], batch_size: int = 32) -> List[List[float]]:
        """
        编码文档列表为 ChromaDB 格式
        
        Args:
            documents: 文档列表
            batch_size: 批处理大小
            
        Returns:
            嵌入向量列表
        """
        embeddings = self.encode(documents, batch_size)
        
        # 转换为列表格式
        embedding_list = [emb.tolist() for emb in embeddings]
        
        return embedding_list


# 创建全局实例
embedding_service = EmbeddingService()
