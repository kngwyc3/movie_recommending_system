"""查看数据库结构"""
import sys
sys.path.insert(0, '.')

from src.config.database import db

def show_database_structure():
    """显示数据库中所有集合的结构"""
    
    print("=" * 80)
    print("ChromaDB 数据库结构")
    print("=" * 80)
    
    # 获取所有集合
    collections = db.client.list_collections()
    
    print(f"\n📊 总共有 {len(collections)} 个集合\n")
    
    for collection in collections:
        print(f"\n{'=' * 80}")
        print(f"📁 集合名称: {collection.name}")
        print(f"{'=' * 80}")
        
        # 获取集合的元数据
        print(f"\n集合元数据:")
        if collection.metadata:
            for key, value in collection.metadata.items():
                print(f"  - {key}: {value}")
        else:
            print("  (无)")
        
        # 获取集合中的数据
        try:
            results = collection.get()
            count = len(results['ids'])
            print(f"\n📈 数据量: {count} 条记录")
            
            if count > 0:
                # 显示第一条记录的结构
                print(f"\n📝 数据结构示例 (第一条记录):")
                print(f"  ID: {results['ids'][0]}")
                
                if results['metadatas'] and len(results['metadatas']) > 0:
                    print(f"\n  字段列表:")
                    metadata = results['metadatas'][0]
                    for key, value in metadata.items():
                        value_type = type(value).__name__
                        # 截断长字符串
                        if isinstance(value, str) and len(value) > 50:
                            value_preview = value[:50] + "..."
                        elif isinstance(value, list) and len(value) > 3:
                            value_preview = f"[{len(value)} items]"
                        elif isinstance(value, dict) and len(value) > 3:
                            value_preview = f"{{{len(value)} keys}}"
                        else:
                            value_preview = value
                        print(f"    • {key}: {value_type} = {value_preview}")
                
                # 显示前3条记录的ID
                if count > 1:
                    print(f"\n  前5条记录ID:")
                    for i, record_id in enumerate(results['ids'][:5]):
                        print(f"    {i+1}. {record_id}")
                    
                    if count > 5:
                        print(f"    ... (还有 {count - 5} 条)")
        
        except Exception as e:
            print(f"\n❌ 获取数据失败: {str(e)}")
    
    print(f"\n{'=' * 80}")
    print("查询完成")
    print("=" * 80)

if __name__ == '__main__':
    show_database_structure()
