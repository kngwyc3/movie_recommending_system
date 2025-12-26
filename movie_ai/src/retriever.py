"""
检索模块 - 支持 Vector 检索、BM25 检索和混合检索
"""
from typing import List, Dict, Any
import numpy as np
import pickle
import os
from rank_bm25 import BM25Okapi

from src.embeddeding import embedding_service
from src.bm25_builder import preprocess_text
from src.config import Config
from utils.translator import extract_movie_keywords
from scripts.db_connection import db_connection

class Retriever:
    """检索器类 - 只负责检索"""
    
    # 类变量 - 全局缓存（所有实例共享，只加载一次）
    _bm25_cache = None
    _doc_ids_cache = None
    _doc_texts_cache = None
    _cache_loaded = False
    
    def __init__(self, bm25: BM25Okapi = None, doc_ids: List[str] = None, 
                 doc_texts: List[str] = None):
        """
        初始化检索器
        
        Args:
            bm25: BM25 模型（用于 BM25 检索）
            doc_ids: 文档 ID 列表
            doc_texts: 文档文本列表
        """
        # 如果还没有加载全局缓存，则加载一次
        if not Retriever._cache_loaded and bm25 is None:
            Retriever._load_bm25_cache()
        
        # 使用提供的参数或使用缓存的数据
        self.bm25 = bm25 or Retriever._bm25_cache
        self.doc_ids = doc_ids or Retriever._doc_ids_cache or []
        self.doc_texts = doc_texts or Retriever._doc_texts_cache or []
        
        # 连接数据库
        db_connection.connect()
        self.collection = db_connection.get_collection()
    
    @classmethod
    def _load_bm25_cache(cls):
        """
        加载 BM25 索引到全局缓存（只执行一次）
        """
        if cls._cache_loaded:
            return
        
        try:
            cache_file = Config.BM25_CACHE_FILE
            if os.path.exists(cache_file):
                with open(cache_file, 'rb') as f:
                    data = pickle.load(f)
                
                cls._bm25_cache = data['bm25']
                cls._doc_ids_cache = data['doc_ids']
                cls._doc_texts_cache = data['doc_texts']
            else:
                print(f"⚠️  BM25 索引文件不存在: {cache_file}")
        except Exception as e:
            print(f"⚠️  BM25 索引加载失败: {e}")
        finally:
            cls._cache_loaded = True  # 标记已尝试加载，避免重复
    
    @classmethod
    def preload_bm25(cls):
        """
        主动预加载 BM25 索引（可选）
        """
        cls._load_bm25_cache()
    
    def vector_search(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        向量检索（使用 embedding 相似度）
        
        Args:
            query: 查询文本
            top_k: 返回前K个结果
            
        Returns:
            检索结果列表
        """
        # 生成查询的 embedding
        query_embedding = embedding_service.encode(query)
        
        # 确保是一维数组
        if query_embedding.ndim > 1:
            query_embedding = query_embedding.flatten()
        
        # 在 ChromaDB 中搜索
        results = self.collection.query(
            query_embeddings=[query_embedding.tolist()],
            n_results=top_k,
            include=["documents", "metadatas", "distances"]
        )
        
        # 格式化结果
        retrievals = []
        for i in range(len(results['ids'][0])):
            score = 1 - results['distances'][0][i]
            # 过滤分数低于 0.1 的结果
            if score >= 0.1:
                retrievals.append({
                    'id': results['ids'][0][i],
                    'document': results['documents'][0][i],
                    'metadata': results['metadatas'][0][i],
                    'score': score,
                    'method': 'vector'
                })
        
        return retrievals
    
    def bm25_search(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        BM25 检索（关键词匹配）

        Args:
            query: 查询文本（中文）
            top_k: 返回前K个结果

        Returns:
            检索结果列表
        """
        if self.bm25 is None:
            raise RuntimeError("BM25 模型未初始化，请先构建索引")

        # 从查询中提取关键词（电影类型、名称等，不发散）
        keywords = extract_movie_keywords(query)

        # 查询分词（带预处理）
        tokenized_query = preprocess_text(keywords)
        
        # BM25 检索
        scores = self.bm25.get_scores(tokenized_query)
        top_indices = np.argsort(scores)[::-1][:top_k]
        
        # 获取结果
        results = self.collection.get(
            ids=[self.doc_ids[i] for i in top_indices],
            include=["documents", "metadatas"]
        )
        
        # 格式化结果
        retrievals = []
        for idx, doc_id in enumerate(results['ids']):
            original_idx = top_indices[idx]
            retrievals.append({
                'id': doc_id,
                'document': results['documents'][idx],
                'metadata': results['metadatas'][idx],
                'score': float(scores[original_idx]),
                'method': 'bm25'
            })
        
        return retrievals
    
    def hybrid_search(self, query: str, top_k: int = 5,
                     alpha: float = 0.5, separate: bool = False) -> Dict[str, List[Dict[str, Any]]]:
        """
        混合检索（向量 + BM25）

        Args:
            query: 查询文本
            top_k: 返回前K个结果
            alpha: 向量检索权重 (0-1)
            separate: 是否分别返回向量检索和BM25结果

        Returns:
            如果 separate=True，返回 {'vector_results': ..., 'bm25_results': ..., 'combined_results': ...}
            如果 separate=False，返回合并后的检索结果列表
        """
        if self.bm25 is None:
            raise RuntimeError("BM25 模型未初始化，请先构建索引")

        # 分别获取两种检索结果
        vector_results = self.vector_search(query, top_k * 2)
        bm25_results = self.bm25_search(query, top_k * 2)

        # 合并结果 (只做去重合并)
        combined_docs = {}

        # 添加向量检索结果
        for result in vector_results:
            doc_id = result['id']
            combined_docs[doc_id] = result

        # 添加 BM25 检索结果 (不改变向量结果)
        for result in bm25_results:
            doc_id = result['id']
            if doc_id not in combined_docs:
                combined_docs[doc_id] = result

        # 转换为列表并返回 top_k
        combined_results = list(combined_docs.values())[:top_k]

        # 根据参数返回不同格式
        if separate:
            return {
                'vector_results': vector_results,
                'bm25_results': bm25_results,
                'combined_results': combined_results
            }
        else:
            return combined_results
    
    def search(self, query: str, method: str = 'hybrid', 
               top_k: int = 3, **kwargs) -> List[Dict[str, Any]]:
        """
        统一检索接口
        
        Args:
            query: 查询文本
            method: 检索方法 ('vector', 'bm25', 'hybrid')
            top_k: 返回前K个结果
            **kwargs: 其他参数
            
        Returns:
            检索结果列表
        """
        if method == 'vector':
            return self.vector_search(query, top_k)
        elif method == 'bm25':
            return self.bm25_search(query, top_k)
        elif method == 'hybrid':
            return self.hybrid_search(query, top_k, **kwargs)
        else:
            raise ValueError(f"不支持的检索方法: {method}")


# 创建全局实例（空初始化，需要手动加载 BM25）
retriever = Retriever()
