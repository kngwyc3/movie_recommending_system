"""
将 MovieLens 数据导入 ChromaDB
包含 embedding 生成和数据导入功能
"""
import os
import sys
import json
from typing import Dict, Any, List

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import chromadb
from chromadb.config import Settings
from src.config import Config
from src.embeddeding import embedding_service


class ChromaDBImporter:
    """ChromaDB 数据导入器"""
    
    def __init__(self, collection_name: str = 'movies'):
        """
        初始化导入器
        
        Args:
            collection_name: 集合名称
        """
        self.collection_name = collection_name
        self.client = None
        self.collection = None
    
    def connect(self, db_path: str = None):
        """
        连接到 ChromaDB
        
        Args:
            db_path: 数据库路径，默认为 movie_back 的 chroma_db
        """
        if db_path is None:
            db_path = Config.CHROMA_DB_PATH
        
        print(f"正在连接到 ChromaDB: {db_path}")
        self.client = chromadb.PersistentClient(
            path=db_path,
            settings=Settings(
                anonymized_telemetry=False,
                allow_reset=True
            )
        )
        
        # 获取或创建集合
        try:
            self.collection = self.client.get_collection(name=self.collection_name)
            print(f"✅ 已连接到现有集合: {self.collection_name}")
            print(f"   当前记录数: {self.collection.count()}")
        except Exception:
            self.collection = self.client.create_collection(
                name=self.collection_name,
                metadata={"description": "MovieLens 电影数据库"}
            )
            print(f"✅ 创建新集合: {self.collection_name}")
    
    def load_data(self, json_path: str) -> Dict[str, Any]:
        """
        加载 JSON 数据文件
        
        Args:
            json_path: JSON 文件路径
            
        Returns:
            数据字典
        """
        print(f"\n正在加载数据文件: {json_path}")
        
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        print(f"✅ 数据加载完成")
        print(f"   - IDs: {len(data['ids'])} 个")
        print(f"   - Documents: {len(data['documents'])} 个")
        print(f"   - Metadatas: {len(data['metadatas'])} 个")
        
        return data
    
    def generate_embeddings(self, documents: List[str]) -> List[List[float]]:
        """
        生成 embeddings
        
        Args:
            documents: 文档列表
            
        Returns:
            嵌入向量列表
        """
        print(f"\n正在生成 {len(documents)} 个文档的 embeddings...")
        print(f"   模型: {Config.EMBEDDING_MODEL_NAME}")
        print(f"   设备: {Config.EMBEDDING_DEVICE}")
        
        embeddings = embedding_service.encode_documents(
            documents=documents,
            batch_size=32
        )
        
        print(f"✅ Embeddings 生成完成")
        print(f"   - 维度: {Config.EMBEDDING_DIMENSION}")
        
        return embeddings
    
    def import_data(self, ids: List[str], documents: List[str], 
                   metadatas: List[Dict[str, Any]], 
                   embeddings: List[List[float]] = None,
                   batch_size: int = 100):
        """
        导入数据到 ChromaDB
        
        Args:
            ids: ID 列表
            documents: 文档列表
            metadatas: 元数据列表
            embeddings: 嵌入向量列表（可选，不提供则由 ChromaDB 生成）
            batch_size: 批处理大小
        """
        total = len(ids)
        print(f"\n正在导入 {total} 条记录到 ChromaDB...")
        
        # 分批导入
        for i in range(0, total, batch_size):
            batch_end = min(i + batch_size, total)
            batch_ids = ids[i:batch_end]
            batch_docs = documents[i:batch_end]
            batch_metas = metadatas[i:batch_end]
            
            if embeddings:
                batch_embs = embeddings[i:batch_end]
            else:
                batch_embs = None
            
            # 添加到集合
            self.collection.add(
                ids=batch_ids,
                documents=batch_docs,
                metadatas=batch_metas,
                embeddings=batch_embs
            )
            
            print(f"   进度: {batch_end}/{total} ({batch_end/total*100:.1f}%)")
        
        print(f"✅ 数据导入完成")
        print(f"   - 集合记录总数: {self.collection.count()}")
    
    def clear_collection(self):
        """清空集合"""
        try:
            self.client.delete_collection(self.collection_name)
            self.collection = self.client.create_collection(
                name=self.collection_name,
                metadata={"description": "MovieLens 电影数据库"}
            )
            print(f"✅ 集合已清空")
        except Exception as e:
            print(f"❌ 清空集合失败: {e}")
    
    def show_sample(self, count: int = 3):
        """显示样本数据"""
        print(f"\n=== 集合样本数据 (前 {count} 条) ===")
        try:
            results = self.collection.get(limit=count, include=['metadatas', 'documents'])
            
            for i, doc_id in enumerate(results['ids']):
                print(f"\n--- 记录 {i+1} (ID: {doc_id}) ---")
                if 'metadatas' in results and results['metadatas']:
                    metadata = results['metadatas'][i]
                    print(f"  标题: {metadata.get('title', 'N/A')}")
                    print(f"  类型: {metadata.get('genres', 'N/A')}")
                    print(f"  评分: {metadata.get('avg_rating', 'N/A')}")
                    print(f"  评分次数: {metadata.get('rating_count', 'N/A')}")
                if 'documents' in results and results['documents']:
                    print(f"  描述: {results['documents'][i][:100]}...")
        except Exception as e:
            print(f"获取样本失败: {e}")


def main():
    """主函数"""
    print("=" * 60)
    print("MovieLens 数据导入 ChromaDB")
    print("=" * 60)
    
    # 配置路径
    json_path = r'D:\code\vue\movie_ai\datasets\chroma_movies_with_descriptions.json'
    
    # 检查文件是否存在
    if not os.path.exists(json_path):
        print(f"\n❌ 错误: 文件不存在 - {json_path}")
        print("请先运行 llmdata.py 生成电影描述数据")
        return
    
    # 初始化导入器
    importer = ChromaDBImporter(collection_name='movies')
    
    # 连接数据库
    importer.connect()
    
    # 询问是否清空现有数据
    print(f"\n当前集合中有 {importer.collection.count()} 条记录")
    clear_input = input("是否清空现有数据后导入? (y/n): ").strip().lower()
    if clear_input == 'y':
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
