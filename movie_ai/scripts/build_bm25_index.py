"""
构建 BM25 索引脚本
"""
from scripts.db_connection import db_connection
from src.bm25_builder import bm25_builder


def main():
    """主函数"""
    # 1. 连接数据库
    db_connection.connect()
    
    # 2. 构建索引
    collection = db_connection.get_collection()
    bm25, doc_ids, doc_texts = bm25_builder.build_or_load(
        collection, 
        force_rebuild=False  # 设为 True 则强制重建
    )
    
    # 3. 更新检索器
    from src.retriever import retriever
    retriever.bm25 = bm25
    retriever.doc_ids = doc_ids
    retriever.doc_texts = doc_texts
    
    print("\n✅ 索引构建完成，检索器已更新！")


if __name__ == '__main__':
    main()
