"""
Movie Model - 电影数据模型
"""
import json


class MovieModel:
    """电影模型类"""
    
    def __init__(self, id=None, title='', image='', genre='', rating=0.0, 
                 badge='', description='', year=0, director='', cast=None,
                 is_hot=False, is_new=False, is_featured=False):
        self.id = id
        self.title = title
        self.image = image
        self.genre = genre
        self.rating = rating
        self.badge = badge
        self.description = description
        self.year = year
        self.director = director
        self.cast = cast if cast else []
        self.is_hot = is_hot
        self.is_new = is_new
        self.is_featured = is_featured
    
    @classmethod
    def from_metadata(cls, id, metadata):
        """从ChromaDB元数据创建Movie对象"""
        cast = json.loads(metadata.get('cast', '[]')) if metadata.get('cast') else []
        
        return cls(
            id=int(id),
            title=metadata.get('title', ''),
            image=metadata.get('image', ''),
            genre=metadata.get('genre', ''),
            rating=metadata.get('rating', 0.0),
            badge=metadata.get('badge', ''),
            description=metadata.get('description', ''),
            year=metadata.get('year', 0),
            director=metadata.get('director', ''),
            cast=cast,
            is_hot=metadata.get('is_hot', False),
            is_new=metadata.get('is_new', False),
            is_featured=metadata.get('is_featured', False)
        )
    
    def to_dict(self):
        """转换为字典格式"""
        data = {
            'id': self.id,
            'title': self.title,
            'image': self.image,
            'genre': self.genre,
            'rating': self.rating,
            'description': self.description,
            'plot': self.description,  # 兼容前端字段
            'year': self.year,
            'director': self.director,
            'cast': self.cast
        }
        
        if self.badge:
            data['badge'] = self.badge
        
        return data
    
    def to_metadata(self):
        """转换为ChromaDB元数据格式"""
        return {
            'title': self.title,
            'image': self.image,
            'genre': self.genre,
            'rating': self.rating,
            'badge': self.badge,
            'description': self.description,
            'year': self.year,
            'director': self.director,
            'cast': json.dumps(self.cast, ensure_ascii=False),
            'is_hot': self.is_hot,
            'is_new': self.is_new,
            'is_featured': self.is_featured
        }
