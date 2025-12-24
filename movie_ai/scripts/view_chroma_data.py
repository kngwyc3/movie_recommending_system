"""
查看 ChromaDB 数据
显示数据库中的完整记录，包括 embeddings
"""
import sys
import os

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import chromadb
from chromadb.config import Settings
from src.config import Config
import json
import numpy as np


def view_data(collection_name: str = 'movies', limit: int = 5, show_full_embedding: bool = False):
    """
    查看 ChromaDB 数据

    Args:
        collection_name: 集合名称
        limit: 查看记录数量
        show_full_embedding: 是否显示完整的 embedding 向量
    """
    print("=" * 80)
    print(f"查看 ChromaDB 集合: {collection_name}")
    print("=" * 80)

    # 连接数据库
    client = chromadb.PersistentClient(
        path=Config.CHROMA_DB_PATH,
        settings=Settings(
            anonymized_telemetry=False,
            allow_reset=True
        )
    )

    # 获取集合
    try:
        collection = client.get_collection(name=collection_name)
    except Exception as e:
        print(f"❌ 错误: 集合 '{collection_name}' 不存在 - {e}")
        return

    total_count = collection.count()
    print(f"\n📊 集合信息:")
    print(f"   总记录数: {total_count}")
    print(f"   数据库路径: {Config.CHROMA_DB_PATH}")

    if total_count == 0:
        print("\n⚠️  集合为空")
        return

    # 获取数据
    print(f"\n📋 获取前 {min(limit, total_count)} 条记录...")
    results = collection.get(
        limit=limit,
        include=['documents', 'metadatas', 'embeddings']
    )

    # 显示每条记录
    for idx, doc_id in enumerate(results['ids'], 1):
        print(f"\n{'=' * 80}")
        print(f"📄 记录 {idx} (ID: {doc_id})")
        print('=' * 80)

        # 显示 metadata
        if 'metadatas' in results and results['metadatas']:
            metadata = results['metadatas'][idx - 1]
            print(f"\n🏷️  Metadata:")
            for key, value in metadata.items():
                print(f"   {key}: {value}")

        # 显示 document
        if 'documents' in results and results['documents']:
            doc = results['documents'][idx - 1]
            print(f"\n📝 Document:")
            if len(doc) > 200:
                print(f"   {doc[:200]}...")
            else:
                print(f"   {doc}")

        # 显示 embedding
        if 'embeddings' in results and results['embeddings']:
            embedding = results['embeddings'][idx - 1]
            embedding_array = np.array(embedding)
            print(f"\n🔢 Embedding:")
            print(f"   维度: {len(embedding)}")
            print(f"   类型: {type(embedding)}")
            print(f"   范围: [{embedding_array.min():.4f}, {embedding_array.max():.4f}]")
            print(f"   范数: {np.linalg.norm(embedding_array):.4f}")

            if show_full_embedding:
                print(f"\n   完整向量 (前10个值):")
                print(f"   {embedding[:10]}")
                print(f"   ... (共 {len(embedding)} 维)")

    # 显示统计信息
    print(f"\n{'=' * 80}")
    print("📊 统计信息")
    print('=' * 80)

    # Embedding 统计
    if 'embeddings' in results and results['embeddings']:
        embeddings = np.array(results['embeddings'])
        print(f"\nEmbedding 统计:")
        print(f"   记录数: {len(embeddings)}")
        print(f"   维度: {embeddings.shape[1]}")
        print(f"   最小值: {embeddings.min():.6f}")
        print(f"   最大值: {embeddings.max():.6f}")
        print(f"   平均值: {embeddings.mean():.6f}")
        print(f"   标准差: {embeddings.std():.6f}")

    # 类型统计
    if 'metadatas' in results and results['metadatas']:
        genres = {}
        for meta in results['metadatas']:
            for genre in meta.get('genres', '').split(', '):
                if genre:
                    genres[genre] = genres.get(genre, 0) + 1

        print(f"\n📈 类型分布 (前{limit}条):")
        for genre, count in sorted(genres.items(), key=lambda x: x[1], reverse=True):
            print(f"   {genre}: {count}")

    # 评分统计
    if 'metadatas' in results and results['metadatas']:
        ratings = [meta.get('avg_rating', 0) for meta in results['metadatas'] if meta.get('avg_rating')]
        if ratings:
            print(f"\n⭐ 评分统计 (前{limit}条):")
            print(f"   平均评分: {np.mean(ratings):.2f}")
            print(f"   最高评分: {max(ratings):.2f}")
            print(f"   最低评分: {min(ratings):.2f}")


def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description='查看 ChromaDB 数据')
    parser.add_argument('--collection', '-c', default='movies', help='集合名称')
    parser.add_argument('--limit', '-l', type=int, default=5, help='查看记录数量')
    parser.add_argument('--full-embedding', '-f', action='store_true', help='显示完整 embedding 向量')

    args = parser.parse_args()

    view_data(
        collection_name=args.collection,
        limit=args.limit,
        show_full_embedding=args.full_embedding
    )


if __name__ == '__main__':
    main()
