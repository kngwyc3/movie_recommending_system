"""
检查movie_back中的ChromaDB数据结构
"""
import chromadb
from chromadb.config import Settings

# 连接到movie_back的ChromaDB
db_path = 'd:/code/vue/movie_back/chroma_db'
client = chromadb.PersistentClient(
    path=db_path,
    settings=Settings(
        anonymized_telemetry=False,
        allow_reset=True
    )
)

print("=== ChromaDB Collections ===")
collections = client.list_collections()
for col in collections:
    print(f"\nCollection: {col.name}")
    print(f"Count: {col.count()}")
    
    # 获取前3条数据样本
    results = col.get(limit=3, include=['metadatas', 'documents', 'embeddings'])
    
    if results['ids']:
        print("\n数据样本:")
        for i, doc_id in enumerate(results['ids']):
            print(f"\n--- 记录 {i+1} (ID: {doc_id}) ---")
            if 'metadatas' in results and results['metadatas']:
                print(f"Metadata: {results['metadatas'][i]}")
            if 'documents' in results and results['documents']:
                print(f"Document: {results['documents'][i]}")
            if 'embeddings' in results and results['embeddings']:
                emb = results['embeddings'][i]
                if emb:
                    print(f"Embedding维度: {len(emb)}")

print("\n" + "="*60)
print("数据库检查完成!")
