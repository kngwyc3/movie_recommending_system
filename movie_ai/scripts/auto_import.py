"""
自动将 MovieLens 数据导入 ChromaDB（非交互模式）
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.import_to_chroma import ChromaDBImporter

def main():
    """主函数"""
    print("=" * 60)
    print("MovieLens 数据自动导入 ChromaDB")
    print("=" * 60)

    # 配置路径
    json_path = r'D:\code\vue\movie_ai\datasets\chroma_movies_with_descriptions.json'

    # 检查文件是否存在
    if not os.path.exists(json_path):
        print(f"\n❌ 错误: 文件不存在 - {json_path}")
        return

    # 初始化导入器
    importer = ChromaDBImporter(collection_name='movies')

    # 连接数据库
    importer.connect()

    # 如果集合为空，直接导入；否则先清空
    if importer.collection.count() > 0:
        print(f"\n集合中已有 {importer.collection.count()} 条记录，清空后重新导入...")
        importer.clear_collection()

    # 加载数据
    data = importer.load_data(json_path)

    # 生成 embeddings
    embeddings = importer.generate_embeddings(data['documents'])

    # 导入数据
    importer.import_data(
        ids=data['ids'],
        documents=data['documents'],
        metadatas=data['metadatas'],
        embeddings=embeddings,
        batch_size=100
    )

    # 显示样本
    importer.show_sample()

    print("\n" + "=" * 60)
    print("导入完成!")
    print("=" * 60)


if __name__ == '__main__':
    main()
