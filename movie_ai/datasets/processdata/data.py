# 完成对数据集的处理
"""
将 MovieLens ml-100k 数据集转换为 ChromaDB 格式
"""
import os

# 类型列表
GENRES = ['unknown', 'Action', 'Adventure', 'Animation', "Children's",
          'Comedy', 'Crime', 'Documentary', 'Drama', 'Fantasy', 'Film-Noir',
          'Horror', 'Musical', 'Mystery', 'Romance', 'Sci-Fi', 'Thriller',
          'War', 'Western']


def load_movies(data_path):
    """
    加载电影信息
    
    Returns:
        dict: {movie_id: movie_info}
    """
    movies = {}
    item_file = os.path.join(data_path, 'u.item')
    
    with open(item_file, 'r', encoding='latin-1') as f:
        for line in f:
            parts = line.strip().split('|')
            movie_id = parts[0]
            title = parts[1]
            release_date = parts[2]
            video_release_date = parts[3]
            imdb_url = parts[4]
            genre_flags = [int(x) for x in parts[5:24]]  # 19个类型标志
            movie_genres = [GENRES[i] for i, flag in enumerate(genre_flags) if flag == 1]
            
            movies[movie_id] = {
                'movie_id': movie_id,
                'title': title,
                'release_date': release_date,
                'video_release_date': video_release_date,
                'imdb_url': imdb_url,
                'genres': movie_genres,
                'avg_rating': 0.0,
                'rating_count': 0
            }
    
    return movies


def load_ratings(data_path):
    """
    加载评分数据
    
    Returns:
        dict: {movie_id: [rating1, rating2, ...]}
    """
    ratings = {}
    data_file = os.path.join(data_path, 'u.data')
    
    with open(data_file, 'r') as f:
        for line in f:
            user_id, item_id, rating, timestamp = line.strip().split('\t')
            if item_id not in ratings:
                ratings[item_id] = []
            ratings[item_id].append(float(rating))
    
    return ratings


def calculate_avg_ratings(movies, ratings):
    """
    为每部电影计算平均评分
    """
    for movie_id in movies:
        if movie_id in ratings:
            rating_list = ratings[movie_id]
            movies[movie_id]['avg_rating'] = sum(rating_list) / len(rating_list)
            movies[movie_id]['rating_count'] = len(rating_list)


def convert_to_chroma_format(movies):
    """
    转换为 ChromaDB 格式
    
    Returns:
        tuple: (ids, documents, metadatas, embeddings)
        - ids: 电影ID列表
        - documents: 电影名列表（后续替换为AI生成的描述）
        - metadatas: 所有字段信息
        - embeddings: 空列表占位
    """
    ids = []
    documents = []
    metadatas = []
    embeddings = []
    
    for movie_id, movie_info in movies.items():
        # IDs: 使用 movie_id
        ids.append(movie_id)
        
        # Documents: 只使用电影名（后续替换为AI生成的描述）
        documents.append(movie_info['title'])
        
        # Metadatas: 保存所有字段信息
        metadatas.append({
            'movie_id': movie_info['movie_id'],
            'title': movie_info['title'],
            'release_date': movie_info['release_date'],
            'video_release_date': movie_info['video_release_date'],
            'imdb_url': movie_info['imdb_url'],
            'genres': ', '.join(movie_info['genres']),
            'avg_rating': movie_info['avg_rating'],
            'rating_count': movie_info['rating_count']
        })
        
        # Embeddings: 空列表占位
        embeddings.append([])
    
    return ids, documents, metadatas, embeddings


def save_chroma_data(output_path, ids, documents, metadatas, embeddings):
    """
    保存转换后的数据到文件（可选，用于调试）
    """
    import json
    
    output_dir = os.path.dirname(output_path)
    os.makedirs(output_dir, exist_ok=True)
    
    data = {
        'ids': ids,
        'documents': documents,
        'metadatas': metadatas,
        'count': len(ids)
    }
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"数据已保存到: {output_path}")


def main():
    # 数据路径
    data_path = r'D:\code\vue\movie_ai\datasets\ml-100k'
    output_path = r'D:\code\vue\movie_ai\data\chroma_movies.json'
    
    print("=" * 50)
    print("开始处理 MovieLens 数据")
    print("=" * 50)
    
    # 1. 加载电影信息
    print(f"\n1. 加载电影信息...")
    movies = load_movies(data_path)
    print(f"   ✓ 共加载 {len(movies)} 部电影")
    
    # 2. 加载评分数据
    print(f"\n2. 加载评分数据...")
    ratings = load_ratings(data_path)
    print(f"   ✓ 共加载 {len(ratings)} 部电影的评分")
    
    # 3. 计算平均评分
    print(f"\n3. 计算平均评分...")
    calculate_avg_ratings(movies, ratings)
    print(f"   ✓ 评分计算完成")
    
    # 4. 转换为 Chroma 格式
    print(f"\n4. 转换为 Chroma 格式...")
    ids, documents, metadatas, embeddings = convert_to_chroma_format(movies)
    print(f"   ✓ 转换完成")
    print(f"   - IDs: {len(ids)} 个")
    print(f"   - Documents: {len(documents)} 个")
    print(f"   - Metadatas: {len(metadatas)} 个")
    print(f"   - Embeddings: {len(embeddings)} 个（占位）")
    
    # 5. 显示示例数据
    print(f"\n5. 示例数据:")
    print(f"   ID: {ids[0]}")
    print(f"   Document: {documents[0]}")
    print(f"   Metadata: {metadatas[0]}")
    
    # 6. 保存到文件（可选）
    print(f"\n6. 保存数据文件...")
    save_chroma_data(output_path, ids, documents, metadatas, embeddings)
    
    print("\n" + "=" * 50)
    print("数据处理完成！")
    print("=" * 50)
    
    return ids, documents, metadatas, embeddings


if __name__ == '__main__':
    ids, documents, metadatas, embeddings = main()
