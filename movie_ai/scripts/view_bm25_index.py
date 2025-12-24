"""
查看 BM25 索引内容
"""
import os
import sys
import pickle

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.config import Config


def view_bm25_index(cache_path: str = None):
    """查看 BM25 索引内容

    Args:
        cache_path: 索引缓存文件路径
    """
    if cache_path is None:
        cache_path = Config.BM25_CACHE_FILE

    if not os.path.exists(cache_path):
        print(f"❌ 索引文件不存在: {cache_path}")
        return

    print("=" * 60)
    print("BM25 索引内容查看")
    print("=" * 60)

    # 加载索引
    print(f"\n📂 加载索引: {cache_path}")
    with open(cache_path, 'rb') as f:
        cache_data = pickle.load(f)

    bm25 = cache_data['bm25']
    doc_ids = cache_data['doc_ids']
    doc_texts = cache_data['doc_texts']
    tokenized_corpus = cache_data.get('tokenized_corpus')

    print(f"✅ 加载成功！")
    print(f"   - 文档数量: {len(doc_ids)}")
    print(f"   - 词汇表大小: {len(bm25.idf)}")

    # 显示前5个文档
    print("\n" + "=" * 60)
    print("前 5 个文档示例:")
    print("=" * 60)
    for i in range(min(5, len(doc_ids))):
        print(f"\n【文档 {i + 1}】")
        print(f"ID: {doc_ids[i]}")
        print(f"文本: {doc_texts[i][:100]}..." if len(doc_texts[i]) > 100 else f"文本: {doc_texts[i]}")

    # 显示词汇表统计
    print("\n" + "=" * 60)
    print("词汇表统计:")
    print("=" * 60)
    idf_scores = bm25.idf
    sorted_vocab = sorted(idf_scores.items(), key=lambda x: x[1], reverse=True)

    print(f"\nIDF 最高的 10 个词:")
    for word, idf in sorted_vocab[:10]:
        print(f"   {word}: {idf:.3f}")

    print(f"\nIDF 最低的 10 个词:")
    for word, idf in sorted_vocab[-10:]:
        print(f"   {word}: {idf:.3f}")

    # 词频统计
    print("\n" + "=" * 60)
    print("词频统计:")
    print("=" * 60)
    if tokenized_corpus:
        from collections import Counter
        word_freq = Counter()
        for tokens in tokenized_corpus:
            word_freq.update(tokens)

        sorted_freq = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)

        print(f"\n词频最高的 20 个词:")
        total_words = sum(word_freq.values())
        for word, freq in sorted_freq[:20]:
            percentage = (freq / total_words) * 100
            print(f"   {word}: {freq} 次 ({percentage:.2f}%)")

        print(f"\n词汇总数: {total_words}")
        print(f"不同词数: {len(word_freq)}")
    else:
        print("   (旧缓存，无分词数据)")

    # 分词后的文档示例
    print("\n" + "=" * 60)
    print("分词示例 (前3个文档):")
    print("=" * 60)
    if tokenized_corpus:
        for i in range(min(3, len(tokenized_corpus))):
            print(f"\n文档 {i + 1}:")
            tokens = tokenized_corpus[i]
            print(f"   分词结果: {tokens}")
            print(f"   词数: {len(tokens)}")
    else:
        print("   (旧缓存，无分词数据)")

    print("\n" + "=" * 60)


if __name__ == '__main__':
    view_bm25_index()
