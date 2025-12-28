"""
Movie Repository - 电影数据访问层
负责所有数据库操作
"""
from src.config.database import db
from src.models.movie_model import MovieModel


class MovieRepository:
    """电影数据仓库类"""
    
    def __init__(self):
        self.collection = db.get_collection()
    
    def create(self, movie):
        """创建新电影"""
        try:
            # ChromaDB 添加数据
            self.collection.add(
                ids=[str(movie.id)],
                documents=[""],  # 占位文档
                metadatas=[movie.to_metadata()]
            )
            return movie
        except Exception as e:
            print(f"❌ 创建电影失败: {str(e)}")
            return None
    
    def find_by_id(self, movie_id):
        """根据ID查找电影"""
        try:
            print(f'🔍 Repository查找电影 ID: {movie_id}, 类型: {type(movie_id)}')
            movie_id_str = str(movie_id)
            print(f'🔍 转换为字符串: {movie_id_str}')
            
            results = self.collection.get(ids=[movie_id_str])
            print(f'📊 ChromaDB查询结果: ids={results["ids"]}, metadatas数量={len(results["metadatas"]) if results["metadatas"] else 0}')
            
            if results['ids'] and len(results['ids']) > 0:
                movie = MovieModel.from_metadata(
                    results['ids'][0],
                    results['metadatas'][0]
                )
                print(f'✅ 找到电影: {movie.title}')
                return movie
            
            print(f'❌ 未找到电影 ID: {movie_id}')
            return None
        except Exception as e:
            print(f"❌ 查找电影失败: {str(e)}")
            import traceback
            traceback.print_exc()
            return None
    
    def find_all(self, page=1, per_page=12):
        """获取所有电影（分页）"""
        try:
            # 获取所有非特色电影
            all_results = self.collection.get(where={"is_featured": False})
            
            # 手动分页
            movies = self._parse_results(all_results)
            start = (page - 1) * per_page
            end = start + per_page
            return movies[start:end]
        except Exception as e:
            print(f"❌ 获取所有电影失败: {str(e)}")
            return []
    
    def find_hot_movies(self, page=1, per_page=8):
        """获取热门电影"""
        try:
            results = self.collection.get(where={"is_hot": True})
            movies = self._parse_results(results)
            
            # 手动分页
            start = (page - 1) * per_page
            end = start + per_page
            return movies[start:end]
        except Exception as e:
            print(f"❌ 获取热门电影失败: {str(e)}")
            return []
    
    def find_new_movies(self, page=1, per_page=4):
        """获取最新电影"""
        try:
            results = self.collection.get(where={"is_new": True})
            movies = self._parse_results(results)
            
            # 手动分页
            start = (page - 1) * per_page
            end = start + per_page
            return movies[start:end]
        except Exception as e:
            print(f"❌ 获取最新电影失败: {str(e)}")
            return []
    
    def find_featured_movie(self):
        """获取特色推荐电影"""
        try:
            results = self.collection.get(where={"is_featured": True})
            
            movies = self._parse_results(results)
            return movies[0] if movies else None
        except Exception as e:
            print(f"❌ 获取特色电影失败: {str(e)}")
            return None
    
    def find_by_category(self, category, page=1, per_page=12):
        """根据分类查找电影"""
        try:
            if category == '全部':
                all_results = self.collection.get(where={"is_featured": False})
            else:
                # 获取所有该分类的电影，手动过滤非特色电影
                all_results = self.collection.get(where={"genre": category})
                
                # 手动过滤非特色电影
                filtered_ids = []
                filtered_metadatas = []
                for i, metadata in enumerate(all_results['metadatas']):
                    if not metadata.get('is_featured', False):
                        filtered_ids.append(all_results['ids'][i])
                        filtered_metadatas.append(metadata)
                
                all_results = {'ids': filtered_ids, 'metadatas': filtered_metadatas}
            
            # 手动分页
            movies = self._parse_results(all_results)
            start = (page - 1) * per_page
            end = start + per_page
            return movies[start:end]
        except Exception as e:
            print(f"❌ 按分类查找失败: {str(e)}")
            return []
    
    def count_by_category(self, category):
        """统计指定分类的电影数量"""
        try:
            if category == '全部':
                results = self.collection.get(where={"is_featured": False})
                return len(results['ids'])
            else:
                # 获取该分类所有电影，手动过滤非特色电影
                results = self.collection.get(where={"genre": category})
                count = 0
                for metadata in results['metadatas']:
                    if not metadata.get('is_featured', False):
                        count += 1
                return count
        except Exception as e:
            print(f"❌ 统计分类数量失败: {str(e)}")
            return 0
    
    def search(self, query):
        """搜索电影"""
        try:
            # 获取所有非特色电影
            all_results = self.collection.get(where={"is_featured": False})
            
            # 手动过滤匹配的电影
            matched_movies = []
            query_lower = query.lower()
            
            for i, metadata in enumerate(all_results['metadatas']):
                # 检查标题、导演、演员、描述是否包含查询词
                if (query_lower in metadata.get('title', '').lower() or
                    query_lower in metadata.get('director', '').lower() or
                    query_lower in metadata.get('cast', '').lower() or
                    query_lower in metadata.get('description', '').lower()):
                    
                    movie = MovieModel.from_metadata(
                        all_results['ids'][i],
                        metadata
                    )
                    matched_movies.append(movie)
            
            return matched_movies
        except Exception as e:
            print(f"❌ 搜索失败: {str(e)}")
            return []
    
    def update(self, movie):
        """更新电影信息"""
        try:
            self.collection.update(
                ids=[str(movie.id)],
                documents=[""],
                metadatas=[movie.to_metadata()]
            )
            return movie
        except Exception as e:
            print(f"❌ 更新电影失败: {str(e)}")
            return None
    
    def delete(self, movie_id):
        """删除电影"""
        try:
            self.collection.delete(ids=[str(movie_id)])
            return True
        except Exception as e:
            print(f"❌ 删除电影失败: {str(e)}")
            return False
    
    def _parse_results(self, results):
        """解析ChromaDB查询结果"""
        movies = []
        if results['ids']:
            for i, movie_id in enumerate(results['ids']):
                movie = MovieModel.from_metadata(
                    movie_id,
                    results['metadatas'][i]
                )
                movies.append(movie)
        return movies


# 创建全局仓库实例
movie_repository = MovieRepository()
