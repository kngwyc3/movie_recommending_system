import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """配置类"""
    
    # Flask配置
    FLASK_APP_NAME = 'Movie AI RAG Service'
    FLASK_HOST = os.getenv('FLASK_HOST', '0.0.0.0')
    FLASK_PORT = int(os.getenv('FLASK_PORT', 5001))
    FLASK_DEBUG = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    
    # Embedding模型配置
    EMBEDDING_MODEL_NAME = 'D:/code/vue/movie_ai/models/bge-small-zh-v1.5'
    EMBEDDING_DEVICE = 'cpu'  # 'cuda' 或 'cpu'
    EMBEDDING_DIMENSION = 512
    
    # LLM配置 (Qwen3 Max)
    QWEN_API_KEY = os.getenv('QWEN_API_KEY', '')
    QWEN_API_URL = os.getenv('QWEN_API_URL',
        'https://dashscope.aliyuncs.com/compatible-mode/v1')
    QWEN_MODEL = 'qwen-max'
    QWEN_TEMPERATURE = 0.7
    QWEN_MAX_TOKENS = 1000
    
    # ChromaDB配置 (复用movie_back)
    # 使用持久化模式，共享movie_back的chroma_db目录
    CHROMA_DB_PATH = os.path.join(os.path.dirname(__file__), '..', '..', 'movie_back', 'chroma_db')
    CHROMA_COLLECTION_NAME = 'movie_ai_collection'  # RAG专用的collection
    
    # RAG配置
    TOP_K = 5  # 检索Top-K相关文档
    CHUNK_SIZE = 200  # 文本分块大小
    CHUNK_OVERLAP = 50  # 分块重叠
    
    # 数据路径
    DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data')
    LOG_DIR = os.path.join(os.path.dirname(__file__), '..', 'logs')
    
    # BM25缓存文件
    CACHE_DIR = os.path.join(os.path.dirname(__file__), '..', 'data')
    BM25_CACHE_FILE = os.path.join(CACHE_DIR, 'bm25_index.pkl') 

    @classmethod
    def validate(cls):
        """验证配置"""
        if not cls.QWEN_API_KEY:
            raise ValueError("QWEN_API_KEY not set in environment variables")
