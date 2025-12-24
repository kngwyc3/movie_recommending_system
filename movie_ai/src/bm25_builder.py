"""
BM25 索引构建器
"""
import os
import re
import pickle
from rank_bm25 import BM25Okapi
import jieba
from typing import List, Dict, Any

from src.config import Config


# 停用词列表（中文）
CHINESE_STOPWORDS = {
    '一个', '这部', '以及', '一位', '观众', '通过', '深刻', '展现',
    '是', '的', '了', '在', '和', '有', '就', '不', '人', '都',
    '一', '一个', '上', '也', '很', '到', '说', '要', '去', '你',
    '会', '着', '没有', '看', '好', '自己', '这', '那', '而', '能',
    '但', '与', '或', '及', '等', '或', '因为', '所以', '如果',
    '虽然', '可是', '还是', '为了', '之后', '之前', '当中', '之中',
    '之间', '方面', '之后', '之后', '这里', '那里', '这样', '那样'
}

# 停用词列表（英文）
ENGLISH_STOPWORDS = {
    'comedy', 'drama', 'action', 'thriller', 'horror', 'romance',
    'a', 'an', 'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to',
    'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be',
    'this', 'that', 'these', 'those', 'have', 'has', 'had', 'do',
    'does', 'did', 'will', 'would', 'should', 'could', 'may', 'might'
}

# 合并停用词
STOPWORDS = CHINESE_STOPWORDS.union(ENGLISH_STOPWORDS)


def preprocess_text(text):
    """预处理文本

    Args:
        text: 原始文本

    Returns:
        过滤后的分词列表
    """
    # 去除标点符号
    text = re.sub(r'[^\w\s]', ' ', text)
    # 转换为小写
    text = text.lower()
    # 分词
    tokens = list(jieba.cut(text))
    # 过滤停用词和短词
    tokens = [t for t in tokens if t.strip() and len(t) > 1 and t not in STOPWORDS]
    return tokens


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
    
    def build_from_collection(self, collection):
        """
        从 ChromaDB 集合构建 BM25 索引

        Args:
            collection: ChromaDB 集合对象

        Returns:
            (BM25Okapi 模型, doc_ids, tokenized_corpus)
        """
        print("\n" + "=" * 50)
        print("开始构建 BM25 索引")
        print("=" * 50)
        
        # 从 ChromaDB 导出数据
        print("\n1. 从 ChromaDB 导出数据...")
        all_data = collection.get(
            include=["documents", "metadatas"]
        )
        
        doc_ids = all_data["ids"]
        print(f"   ✓ 导入 {len(doc_ids)} 条记录")
        
        # 构建综合搜索文本（标题 + 类型 + 导演 + 演员）
        print("\n2. 构建搜索文本（标题 + 类型 + 导演 + 演员）...")
        doc_texts = []
        for doc, meta in zip(all_data["documents"], all_data["metadatas"]):
            parts = []
            if meta.get('title'):
                parts.append(meta['title'])
            if meta.get('genres'):
                parts.append(meta['genres'])
            if meta.get('director'):
                parts.append(meta['director'])
            if meta.get('cast'):
                # cast 可能是列表，需要展开
                cast_list = meta['cast'] if isinstance(meta['cast'], list) else [meta['cast']]
                parts.extend(cast_list)
            # 移除 description，减少噪音
            doc_texts.append(" ".join(parts))
        
        print(f"   ✓ 文本构建完成")
        
        # 中文分词（带预处理）
        print(f"\n3. 中文分词（带预处理）...")
        tokenized_corpus = [
            preprocess_text(text) 
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
            'doc_texts': doc_texts,
            'tokenized_corpus': tokenized_corpus
        }
        
        with open(self.cache_path, 'wb') as f:
            pickle.dump(cache_data, f, protocol=pickle.HIGHEST_PROTOCOL)
        
        print(f"   ✓ 缓存已保存到: {self.cache_path}")

        print("\n" + "=" * 50)
        print("BM25 索引构建完成!")
        print("=" * 50)

        return bm25, doc_ids, tokenized_corpus
    
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

        # 兼容旧缓存：如果没有 tokenized_corpus，则使用预处理生成
        if 'tokenized_corpus' in cache_data:
            return cache_data['bm25'], cache_data['doc_ids'], cache_data['tokenized_corpus']
        else:
            from src.bm25_builder import preprocess_text
            tokenized_corpus = [preprocess_text(text) for text in cache_data['doc_texts']]
            return cache_data['bm25'], cache_data['doc_ids'], tokenized_corpus
    
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
            return self.build_from_collection(collection)
        else:
            return self.load_from_cache()


# 创建全局实例
bm25_builder = BM25Builder()
