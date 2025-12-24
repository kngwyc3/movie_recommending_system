import chromadb
from chromadb.config import Settings
from typing import List, Dict, Optional
from src.config import Config

class VectorStore:
    """ChromaDB向量数据库操作封装"""
    
    def __init__(self):
        """初始化ChromaDB客户端"""
        self.client = chromadb.PersistentClient(
            path=Config.CHROMA_DB_PATH,
            settings=Settings(
                anonymized_telemetry=False,
                allow_reset=True
            )
        )
        self.collection = self._get_or_create_collection()
    
    def _get_or_create_collection(self):
        """获取或创建collection"""
        try:
            collection = self.client.get_collection(name=Config.CHROMA_COLLECTION_NAME)
            print(f"Found existing collection: {Config.CHROMA_COLLECTION_NAME}")
            return collection
        except Exception:
            print(f"Creating new collection: {Config.CHROMA_COLLECTION_NAME}")
            return self.client.create_collection(
                name=Config.CHROMA_COLLECTION_NAME,
                metadata={"hnsw:space": "cosine"}
            )
    
    def add_documents(
        self,
        ids: List[str],
        embeddings: List[List[float]],
        documents: List[str],
        metadatas: Optional[List[Dict]] = None
    ):
        """添加文档到向量库"""
        self.collection.add(
            ids=ids,
            embeddings=embeddings,
            documents=documents,
            metadatas=metadatas
        )
        print(f"Added {len(ids)} documents to collection")
    
    def search(
        self,
        query_embedding: List[float],
        top_k: int = None
    ) -> Dict:
        """
        相似度搜索
        
        Returns:
            {
                'ids': [...],
                'documents': [...],
                'metadatas': [...],
                'distances': [...]
            }
        """
        top_k = top_k or Config.TOP_K
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k
        )
        return results
    
    def get_collection_info(self) -> Dict:
        """获取collection信息"""
        count = self.collection.count()
        return {
            'name': Config.CHROMA_COLLECTION_NAME,
            'count': count,
            'dimension': Config.EMBEDDING_DIMENSION
        }
