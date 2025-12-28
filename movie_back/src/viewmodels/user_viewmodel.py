"""
User ViewModel - 用户业务逻辑层
"""
from src.repositories.user_repository import user_repository
from src.repositories.movie_repository import movie_repository
from src.models.user_model import UserModel


class UserViewModel:
    """用户视图模型类"""
    
    def get_user_profile(self, user_id):
        """获取用户信息"""
        user = user_repository.find_by_id(user_id)
        if user:
            return user.to_dict()
        return None
    
    def update_user_profile(self, user_id, data):
        """更新用户信息"""
        user = user_repository.find_by_id(user_id)
        if not user:
            return None
        
        # 更新用户信息
        if 'username' in data:
            user.username = data['username']
        if 'email' in data:
            user.email = data['email']
        if 'avatar' in data:
            user.avatar = data['avatar']
        
        return user_repository.update(user)
    
    def update_preferences(self, user_id, preferences):
        """更新用户偏好设置"""
        user = user_repository.find_by_id(user_id)
        if not user:
            return None
        
        user.preferences.update(preferences)
        return user_repository.update(user)
    
    def update_privacy_settings(self, user_id, privacy_settings):
        """更新隐私设置"""
        user = user_repository.find_by_id(user_id)
        if not user:
            return None
        
        user.privacy_settings.update(privacy_settings)
        return user_repository.update(user)
    
    def get_favorites(self, user_id):
        """获取用户收藏的电影列表"""
        user = user_repository.find_by_id(user_id)
        if not user:
            return []
        
        # 获取收藏的电影详情
        movies = []
        for movie_id in user.favorites:
            movie = movie_repository.find_by_id(movie_id)
            if movie:
                movies.append(movie.to_dict())
        
        return movies
    
    def add_favorite(self, user_id, movie_id):
        """添加收藏"""
        user = user_repository.find_by_id(user_id)
        if not user:
            return False
        
        user.add_favorite(movie_id)
        user_repository.update(user)
        return True
    
    def remove_favorite(self, user_id, movie_id):
        """移除收藏"""
        user = user_repository.find_by_id(user_id)
        if not user:
            return False
        
        user.remove_favorite(movie_id)
        user_repository.update(user)
        return True
    
    def get_watch_history(self, user_id):
        """获取观看历史"""
        user = user_repository.find_by_id(user_id)
        if not user:
            return []
        
        # 获取观看历史的电影详情
        history = []
        for item in user.watch_history:
            movie = movie_repository.find_by_id(item['movie_id'])
            if movie:
                movie_dict = movie.to_dict()
                history.append({
                    'id': movie_dict.get('id'),
                    'title': movie_dict.get('title'),
                    'genre': movie_dict.get('genre'),
                    'image': movie_dict.get('image'),
                    'watch_time': item.get('watched_at'),
                    'rating': movie_dict.get('rating', 0)
                })
        
        return history
    
    def add_watch_history(self, user_id, movie_id):
        """添加观看历史"""
        print(f'🔍 UserViewModel.add_watch_history: user_id={user_id}, movie_id={movie_id}')
        user = user_repository.find_by_id(user_id)
        if not user:
            print(f'❌ 用户不存在: user_id={user_id}')
            return False
        
        print(f'✅ 找到用户: {user.username}')
        user.add_watch_history(movie_id)
        print(f'📝 观看历史已更新，当前历史数量: {len(user.watch_history)}')
        
        updated_user = user_repository.update(user)
        if not updated_user:
            print(f'❌ 更新用户失败')
            return False
            
        print(f'✅ 用户更新成功')
        return True
    
    def rate_movie(self, user_id, movie_id, rating):
        """评分电影"""
        user = user_repository.find_by_id(user_id)
        if not user:
            return False
        
        user.rate_movie(movie_id, rating)
        user_repository.update(user)
        return True
    
    def get_user_ratings(self, user_id):
        """获取用户评分"""
        user = user_repository.find_by_id(user_id)
        if not user:
            return []
        
        # 获取评分的电影详情
        ratings = []
        for movie_id, rating_data in user.ratings.items():
            movie = movie_repository.find_by_id(int(movie_id))
            if movie:
                ratings.append({
                    'movie': movie.to_dict(),
                    'rating': rating_data['rating'],
                    'rated_at': rating_data['rated_at']
                })
        
        return ratings


# 创建全局视图模型实例
user_viewmodel = UserViewModel()
