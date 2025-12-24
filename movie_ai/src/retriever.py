"""
检索模块 - 支持 Vector 检索、BM25 检索和混合检索
"""
from typing import List, Dict, Any
import numpy as np
from rank_bm25 import BM25Okapi

from src.config import Config
from src.embeddeding import embedding_service
from src.bm25_builder import preprocess_text
from scripts.db_connection import db_connection

class Retriever:
    """检索器类 - 只负责检索"""
    
    def __init__(self, bm25: BM25Okapi = None, doc_ids: List[str] = None, 
                 doc_texts: List[str] = None):
        """
        初始化检索器
        
        Args:
            bm25: BM25 模型（用于 BM25 检索）
            doc_ids: 文档 ID 列表
            doc_texts: 文档文本列表
        """
        self.bm25 = bm25
        self.doc_ids = doc_ids or []
        self.doc_texts = doc_texts or []
        
        # 连接数据库
        db_connection.connect()
        self.collection = db_connection.get_collection()
    
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
        
        # 在 ChromaDB 中搜索
        results = self.collection.query(
            query_embeddings=[query_embedding.tolist()],
            n_results=top_k,
            include=["documents", "metadatas", "distances"]
        )
        
        # 格式化结果
        retrievals = []
        for i in range(len(results['ids'][0])):
            retrievals.append({
                'id': results['ids'][0][i],
                'document': results['documents'][0][i],
                'metadata': results['metadatas'][0][i],
                'score': 1 - results['distances'][0][i],
                'method': 'vector'
            })
        
        return retrievals
    
    def bm25_search(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        BM25 检索（关键词匹配）
        
        Args:
            query: 查询文本
            top_k: 返回前K个结果
            
        Returns:
            检索结果列表
        """
        if self.bm25 is None:
            raise RuntimeError("BM25 模型未初始化，请先构建索引")
        
        # 查询分词（带预处理）
        tokenized_query = preprocess_text(query)
        
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
                     alpha: float = 0.5) -> List[Dict[str, Any]]:
        """
        混合检索（向量 + BM25）
        
        Args:
            query: 查询文本
            top_k: 返回前K个结果
            alpha: 向量检索权重 (0-1)
            
        Returns:
            检索结果列表
        """
        if self.bm25 is None:
            raise RuntimeError("BM25 模型未初始化，请先构建索引")
        
        # 分别获取两种检索结果
        vector_results = self.vector_search(query, top_k * 2)
        bm25_results = self.bm25_search(query, top_k * 2)
        
        # 合并结果
        combined_scores = {}
        
        for result in vector_results:
            doc_id = result['id']
            if doc_id not in combined_scores:
                combined_scores[doc_id] = {
                    'vector_score': 0.0,
                    'bm25_score': 0.0,
                    'data': result
                }
            combined_scores[doc_id]['vector_score'] = result['score']
        
        for result in bm25_results:
            doc_id = result['id']
            if doc_id not in combined_scores:
                combined_scores[doc_id] = {
                    'vector_score': 0.0,
                    'bm25_score': 0.0,
                    'data': result
                }
            combined_scores[doc_id]['bm25_score'] = result['score']
        
        # 归一化分数并计算混合分数
        vector_scores = [v['vector_score'] for v in combined_scores.values()]
        bm25_scores = [v['bm25_score'] for v in combined_scores.values()]
        
        max_vector = max(vector_scores) if vector_scores else 1.0
        max_bm25 = max(bm25_scores) if bm25_scores else 1.0
        
        for data in combined_scores.values():
            normalized_vector = data['vector_score'] / max_vector
            normalized_bm25 = data['bm25_score'] / max_bm25
            data['combined_score'] = alpha * normalized_vector + (1 - alpha) * normalized_bm25
        
        # 排序并返回 top_k
        sorted_results = sorted(
            combined_scores.items(),
            key=lambda x: x[1]['combined_score'],
            reverse=True
        )[:top_k]
        
        # 格式化结果
        retrievals = []
        for doc_id, data in sorted_results:
            result = data['data'].copy()
            result['score'] = data['combined_score']
            result['method'] = 'hybrid'
            retrievals.append(result)
        
        return retrievals
    
    def search(self, query: str, method: str = 'hybrid', 
               top_k: int = 5, **kwargs) -> List[Dict[str, Any]]:
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
