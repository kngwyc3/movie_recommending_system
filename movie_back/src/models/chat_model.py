"""
Chat Model - AI对话历史模型
"""
from datetime import datetime


class ChatModel:
    """AI对话历史模型"""
    
    def __init__(self, id=None, user_id=None, question='', answer='', 
                 related_movies=None, rating=0, created_at=None):
        self.id = id
        self.user_id = user_id
        self.question = question
        self.answer = answer
        self.related_movies = related_movies or []
        self.rating = rating  # 0-5 星评分，0表示未评分
        self.created_at = created_at or datetime.now().isoformat()
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'question': self.question,
            'answer': self.answer,
            'related_movies': self.related_movies,
            'rating': self.rating,
            'created_at': self.created_at
        }
    
    def to_metadata(self):
        """转换为ChromaDB元数据格式"""
        return {
            'user_id': str(self.user_id),
            'question': self.question,
            'answer': self.answer,
            'related_movies': str(self.related_movies),  # 列表转字符串
            'rating': self.rating,
            'created_at': self.created_at
        }
    
    @staticmethod
    def from_metadata(chat_id, metadata):
        """从ChromaDB元数据创建对象"""
        import ast
        
        # 将字符串列表转回列表
        related_movies_str = metadata.get('related_movies', '[]')
        try:
            related_movies = ast.literal_eval(related_movies_str)
        except:
            related_movies = []
        
        return ChatModel(
            id=int(chat_id),
            user_id=int(metadata.get('user_id', 0)),
            question=metadata.get('question', ''),
            answer=metadata.get('answer', ''),
            related_movies=related_movies,
            rating=int(metadata.get('rating', 0)),
            created_at=metadata.get('created_at', datetime.now().isoformat())
        )
