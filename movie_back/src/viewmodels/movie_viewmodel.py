"""
Movie ViewModel - 电影视图模型/业务逻辑层
"""
from src.repositories.movie_repository import movie_repository


class MovieViewModel:
    """电影视图模型类 - 处理业务逻辑"""
    
    def __init__(self):
        self.repository = movie_repository
        self.categories = ['全部', '科幻', '动作', '冒险', '悬疑', '爱情', '动画']
    
    def get_hot_movies(self, page=1, per_page=8):
        """获取热门电影列表"""
        movies = self.repository.find_hot_movies(page, per_page)
        return [movie.to_dict() for movie in movies]
    
    def get_new_movies(self, page=1, per_page=4):
        """获取最新电影列表"""
        movies = self.repository.find_new_movies(page, per_page)
        return [movie.to_dict() for movie in movies]
    
    def get_featured_movie(self):
        """获取特色推荐电影"""
        movie = self.repository.find_featured_movie()
        return movie.to_dict() if movie else None
    
    def get_all_movies(self, page=1, per_page=12):
        """获取所有电影列表"""
        movies = self.repository.find_all(page, per_page)
        return [movie.to_dict() for movie in movies]
    
    def get_movies_by_category(self, category, page=1, per_page=12):
        """根据分类获取电影"""
        movies = self.repository.find_by_category(category, page, per_page)
        return [movie.to_dict() for movie in movies]
    
    def get_category_count(self, category):
        """获取指定分类的电影数量"""
        return self.repository.count_by_category(category)
    
    def get_all_categories(self):
        """获取所有分类"""
        return self.categories
    
    def search_movies(self, query, page=1, per_page=12):
        """搜索电影"""
        # 获取所有匹配的电影
        all_matched_movies = self.repository.search(query)
        
        # 手动分页
        start = (page - 1) * per_page
        end = start + per_page
        paged_movies = all_matched_movies[start:end]
        
        return [movie.to_dict() for movie in paged_movies]
    
    def get_search_count(self, query):
        """获取搜索结果数量"""
        all_matched_movies = self.repository.search(query)
        return len(all_matched_movies)
    
    def get_movie_by_id(self, movie_id):
        """根据ID获取电影详情"""
        movie = self.repository.find_by_id(movie_id)
        return movie.to_dict() if movie else None
    
    def chat_with_assistant(self, question, conversation_history=None):
        """电影智能助手（简单的关键词匹配）"""
        # 使用搜索功能找相关电影
        movies = self.search_movies(question, page=1, per_page=3)
        
        response = {
            'answer': f'我找到了 {len(movies)} 部与您问题相关的电影。',
            'related_movies': movies,
            'question': question
        }
        
        return response


# 创建全局ViewModel实例
movie_viewmodel = MovieViewModel()
