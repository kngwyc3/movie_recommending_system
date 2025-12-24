"""
构建 BM25 索引脚本
"""
import os
import sys

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.bm25_builder import bm25_builder
from src.retriever import retriever


def main():
    """主函数"""
    # 1. 获取 collection（retriever 已自动连接）
    collection = retriever.collection

    # 2. 构建索引
    bm25, doc_ids, doc_texts = bm25_builder.build_or_load(
        collection,
        force_rebuild=True  # 强制重建以应用停用词过滤
    )

    # 3. 更新检索器
    retriever.bm25 = bm25
    retriever.doc_ids = doc_ids
    retriever.doc_texts = doc_texts

    print("\n✅ 索引构建完成，检索器已更新！")


if __name__ == '__main__':
    main()
