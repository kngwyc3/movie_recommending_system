"""
ChromaDB数据库配置和连接管理
"""
import chromadb
from chromadb.config import Settings


class Database:
    """数据库管理类"""
    
    def __init__(self):
        # 初始化 ChromaDB 客户端
        self.client = chromadb.PersistentClient(
            path="./chroma_db",
            settings=Settings(
                anonymized_telemetry=False,
                allow_reset=True
            )
        )
        
        # 创建或获取电影集合
        try:
            self.collection = self.client.get_collection(name="movies")
            print("✅ 已连接到现有的电影数据库")
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
