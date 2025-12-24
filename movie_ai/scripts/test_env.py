"""
测试虚拟环境和依赖安装
"""
import sys
sys.path.insert(0, 'd:/code/vue/movie_ai')

print("=== Python环境信息 ===")
print(f"Python版本: {sys.version}")

print("\n=== 测试导入依赖包 ===")
packages = {
    'flask': 'Flask',
    'flask_cors': 'Flask-CORS',
    'sentence_transformers': 'Sentence-Transformers',
    'chromadb': 'ChromaDB',
    'openai': 'OpenAI',
    'dotenv': 'python-dotenv',
    'numpy': 'NumPy',
    'pandas': 'Pandas',
    'recbole': 'RecBole',
    'torch': 'PyTorch',
    'scipy': 'SciPy'
}

for pkg, name in packages.items():
    try:
        mod = __import__(pkg)
        print(f"✓ {name} ({pkg})")
    except ImportError as e:
        print(f"✗ {name} ({pkg}): {e}")

print("\n=== 测试ChromaDB连接 ===")
try:
    import chromadb
    from src.config import Config
    
    print(f"连接ChromaDB: {Config.CHROMA_HOST}:{Config.CHROMA_PORT}")
    
    client = chromadb.HttpClient(
        host=Config.CHROMA_HOST,
        port=Config.CHROMA_PORT
    )
    
    # 获取所有collection
    collections = client.list_collections()
    print(f"\n现有Collections:")
    for coll in collections:
        print(f"  - {coll.name}")
    
    # 检查是否存在movie_ai_collection
    try:
        rag_collection = client.get_collection(name="movie_ai_collection")
        print(f"\n✓ 找到movie_ai_collection，文档数: {rag_collection.count()}")
    except Exception as e:
        print(f"\n✗ movie_ai_collection 不存在")
    
    print("\n=== 环境测试完成 ===")
    
except Exception as e:
    print(f"✗ 连接失败: {e}")
    import traceback
    traceback.print_exc()
