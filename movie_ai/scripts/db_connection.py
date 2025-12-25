"""
ChromaDB 连接管理
"""
import os
import sys

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import chromadb
from chromadb.config import Settings
from src.config import Config


class DBConnection:
    """数据库连接类"""
    
    def __init__(self, collection_name: str = 'movies'):
        """
        初始化连接
        
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
        except Exception:
            self.collection = self.client.create_collection(
                name=self.collection_name,
                metadata={"description": "MovieLens 电影数据库"}
            )
    
    def get_collection(self):
        """获取集合实例"""
        return self.collection


# 创建全局实例
db_connection = DBConnection()
