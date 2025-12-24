"""
BM25 索引构建器
"""
import os
import pickle
from rank_bm25 import BM25Okapi
import jieba
from typing import List, Dict, Any

from src.config import Config


class BM25Builder:
    """BM25 索引构建器"""
    
    def __init__(self, cache_path: str = None):
        """
        初始化构建器
        
        Args:
            cache_path: 缓存文件路径
        """
        if cache_path is None:
            cache_path = Config.BM25_CACHE_FILE
        self.cache_path = cache_path
    
    def build_from_collection(self, collection) -> BM25Okapi:
        """
        从 ChromaDB 集合构建 BM25 索引
        
        Args:
            collection: ChromaDB 集合对象
            
        Returns:
            BM25Okapi 模型
        """
        print("\n" + "=" * 50)
        print("开始构建 BM25 索引")
        print("=" * 50)
        
        # 从 ChromaDB 导出数据
        print("\n1. 从 ChromaDB 导出数据...")
        all_data = collection.get(
            include=["ids", "documents", "metadatas"]
        )
        
        doc_ids = all_data["ids"]
        print(f"   ✓ 导入 {len(doc_ids)} 条记录")
        
        # 构建综合搜索文本
        print("\n2. 构建搜索文本（标题 + 类型 + 描述）...")
        doc_texts = []
        for doc, meta in zip(all_data["documents"], all_data["metadatas"]):
            parts = []
            if meta.get('title'):
                parts.append(meta['title'])
            if meta.get('genres'):
                parts.append(meta['genres'])
            if doc:
                parts.append(doc)
            doc_texts.append(" ".join(parts))
        
        print(f"   ✓ 文本构建完成")
        
        # 中文分词
        print(f"\n3. 中文分词...")
        tokenized_corpus = [
            list(jieba.cut(text)) 
            for text in doc_texts
        ]
        print(f"   ✓ 分词完成")
        
        # 构建 BM25 模型
        print(f"\n4. 构建 BM25 模型...")
        bm25 = BM25Okapi(tokenized_corpus)
        print(f"   ✓ 模型构建完成")
        
        # 保存到缓存
        print(f"\n5. 保存缓存...")
        os.makedirs(os.path.dirname(self.cache_path), exist_ok=True)
        
        cache_data = {
            'bm25': bm25,
            'doc_ids': doc_ids,
            'doc_texts': doc_texts
        }
        
        with open(self.cache_path, 'wb') as f:
            pickle.dump(cache_data, f, protocol=pickle.HIGHEST_PROTOCOL)
        
        print(f"   ✓ 缓存已保存到: {self.cache_path}")
        
        print("\n" + "=" * 50)
        print("BM25 索引构建完成!")
        print("=" * 50)
        
        return bm25
    
    def load_from_cache(self) -> BM25Okapi:
        """
        从缓存加载 BM25 索引
        
        Returns:
            BM25Okapi 模型
        """
        if not os.path.exists(self.cache_path):
            raise FileNotFoundError(f"缓存文件不存在: {self.cache_path}")
        
        print(f"\n正在从缓存加载 BM25 索引...")
        print(f"   路径: {self.cache_path}")
        
        with open(self.cache_path, 'rb') as f:
            cache_data = pickle.load(f)
        
        print(f"✅ 缓存加载成功 ({len(cache_data['doc_ids'])} 条文档)")
        
        return cache_data['bm25'], cache_data['doc_ids'], cache_data['doc_texts']
    
    def build_or_load(self, collection, force_rebuild: bool = False):
        """
        构建或加载 BM25 索引
        
        Args:
            collection: ChromaDB 集合对象
            force_rebuild: 是否强制重建
            
        Returns:
            (bm25, doc_ids, doc_texts)
        """
        if force_rebuild or not os.path.exists(self.cache_path):
            bm25 = self.build_from_collection(collection)
            all_data = collection.get(include=["ids", "documents", "metadatas"])
            doc_ids = all_data["ids"]
            doc_texts = []
            for doc, meta in zip(all_data["documents"], all_data["metadatas"]):
                parts = []
                if meta.get('title'):
                    parts.append(meta['title'])
                if meta.get('genres'):
                    parts.append(meta['genres'])
                if doc:
                    parts.append(doc)
                doc_texts.append(" ".join(parts))
            return bm25, doc_ids, doc_texts
        else:
            return self.load_from_cache()


# 创建全局实例
bm25_builder = BM25Builder()
