"""
User Model - 用户数据模型
"""
import json
import bcrypt
from datetime import datetime


class UserModel:
    """用户模型类"""
    
    def __init__(self, id=None, username='', email='', avatar='', password_hash='',
                 favorites=None, watch_history=None, ratings=None,
                 preferences=None, privacy_settings=None, created_at=None):
        self.id = id
        self.username = username
        self.email = email
        self.avatar = avatar
        self.password_hash = password_hash  # 加密后的密码
        self.favorites = favorites if favorites else []  # 收藏的电影ID列表
        self.watch_history = watch_history if watch_history else []  # 观看历史
        self.ratings = ratings if ratings else {}  # 电影评分字典
        self.preferences = preferences if preferences else {
            'favorite_genres': [],  # 偏好类型
            'theme': 'dark',  # 主题
            'auto_play': True,  # 自动播放
            'quality': 'high'  # 画质偏好
        }
        self.privacy_settings = privacy_settings if privacy_settings else {
            'public_watch_history': True,  # 公开观影记录
            'public_favorites': True  # 公开收藏
        }
        self.created_at = created_at if created_at else datetime.now().isoformat()
    
    @classmethod
    def from_metadata(cls, id, metadata):
        """从ChromaDB元数据创建User对象"""
        favorites = json.loads(metadata.get('favorites', '[]')) if metadata.get('favorites') else []
        watch_history = json.loads(metadata.get('watch_history', '[]')) if metadata.get('watch_history') else []
        ratings = json.loads(metadata.get('ratings', '{}')) if metadata.get('ratings') else {}
        preferences = json.loads(metadata.get('preferences', '{}')) if metadata.get('preferences') else {}
        privacy_settings = json.loads(metadata.get('privacy_settings', '{}')) if metadata.get('privacy_settings') else {}
        
        return cls(
            id=int(id),
            username=metadata.get('username', ''),
            email=metadata.get('email', ''),
            avatar=metadata.get('avatar', ''),
            password_hash=metadata.get('password_hash', ''),
            favorites=favorites,
            watch_history=watch_history,
            ratings=ratings,
            preferences=preferences,
            privacy_settings=privacy_settings,
            created_at=metadata.get('created_at', '')
        )
    
    def to_dict(self):
        """转换为字典格式"""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'avatar': self.avatar,
            'stats': {
                'favorites': len(self.favorites),
                'watched': len(self.watch_history),
                'ratings': len(self.ratings)
            },
            'preferences': self.preferences,
            'privacy_settings': self.privacy_settings
        }
    
    def to_metadata(self):
        """转换为ChromaDB元数据格式"""
        return {
            'username': self.username,
            'email': self.email,
            'avatar': self.avatar,
            'password_hash': self.password_hash,
            'favorites': json.dumps(self.favorites, ensure_ascii=False),
            'watch_history': json.dumps(self.watch_history, ensure_ascii=False),
            'ratings': json.dumps(self.ratings, ensure_ascii=False),
            'preferences': json.dumps(self.preferences, ensure_ascii=False),
            'privacy_settings': json.dumps(self.privacy_settings, ensure_ascii=False),
            'created_at': self.created_at
        }
    
    def add_favorite(self, movie_id):
        """添加收藏"""
        if movie_id not in self.favorites:
            self.favorites.append(movie_id)
    
    def remove_favorite(self, movie_id):
        """移除收藏"""
        if movie_id in self.favorites:
            self.favorites.remove(movie_id)
    
    def add_watch_history(self, movie_id):
        """添加观看历史"""
        watch_item = {
            'movie_id': movie_id,
            'watched_at': datetime.now().isoformat()
        }
        # 移除旧记录，添加新记录到最前面
        self.watch_history = [h for h in self.watch_history if h.get('movie_id') != movie_id]
        self.watch_history.insert(0, watch_item)
        # 限制历史记录数量
        if len(self.watch_history) > 100:
            self.watch_history = self.watch_history[:100]
    
    def rate_movie(self, movie_id, rating):
        """评分电影"""
        self.ratings[str(movie_id)] = {
            'rating': rating,
            'rated_at': datetime.now().isoformat()
        }
    
    def set_password(self, password):
        """设置密码（加密存储）"""
        self.password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    def check_password(self, password):
        """验证密码"""
        if not self.password_hash:
            return False
        return bcrypt.checkpw(password.encode('utf-8'), self.password_hash.encode('utf-8'))
