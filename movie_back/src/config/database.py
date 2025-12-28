"""
ChromaDB数据库配置和连接管理
"""
import chromadb
from chromadb.config import Settings
import os


class Database:
    """数据库管理类"""
    
    def __init__(self):
        # 使用绝对路径，确保始终访问同一个数据库
        # 从 movie_back/src/config/database.py 向上两级到 movie_back
        current_dir = os.path.dirname(os.path.abspath(__file__))
        movie_back_dir = os.path.dirname(os.path.dirname(current_dir))
        db_path = os.path.join(movie_back_dir, "chroma_db")
        
        print(f"📂 数据库路径: {db_path}")
        
        # 初始化 ChromaDB 客户端
        self.client = chromadb.PersistentClient(
            path=db_path,
            settings=Settings(
                anonymized_telemetry=False,
                allow_reset=True
            )
        )
        
        # 创建或获取电影集合
        try:
            self.collection = self.client.get_collection(name="movies")
            # 获取集合中的电影数量
            count = len(self.collection.get()['ids'])
            print(f"✅ 已连接到现有的电影数据库 (共 {count} 部电影)")
        except:
            # 创建集合
            self.collection = self.client.create_collection(
                name="movies",
                metadata={"description": "电影信息数据库"}
            )
            print("✅ 创建了新的电影数据库")
    
    def get_collection(self):
        """获取集合实例"""
        return self.collection
    
    def reset(self):
        """重置数据库（谨慎使用）"""
        self.client.delete_collection("movies")
        self.collection = self.client.create_collection(
            name="movies",
            metadata={"description": "电影信息数据库"}
        )
        print("✅ 数据库已重置")


# 创建全局数据库实例
db = Database()
