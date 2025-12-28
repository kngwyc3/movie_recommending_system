"""
Chat ViewModel - AI对话业务逻辑层
"""
from src.repositories.chat_repository import chat_repository
from src.models.chat_model import ChatModel
import uuid


class ChatViewModel:
    """AI对话视图模型类"""
    
    def __init__(self):
        self.repository = chat_repository
    
    def save_chat(self, user_id, question, answer, related_movies=None):
        """保存对话记录"""
        try:
            # 生成唯一的对话ID
            chat_id = int(uuid.uuid4().int % 1000000)
            
            chat = ChatModel(
                id=chat_id,
                user_id=user_id,
                question=question,
                answer=answer,
                related_movies=related_movies or []
            )
            
            result = self.repository.create(chat)
            return result.to_dict() if result else None
        except Exception as e:
            print(f"❌ 保存对话失败: {str(e)}")
            return None
    
    def get_chat_history(self, user_id, page=1, per_page=20):
        """获取用户的对话历史"""
        try:
            chats = self.repository.find_by_user_id(user_id, page, per_page)
            total = self.repository.count_by_user_id(user_id)
            
            return {
                'total': total,
                'page': page,
                'per_page': per_page,
                'chats': [chat.to_dict() for chat in chats]
            }
        except Exception as e:
            print(f"❌ 获取对话历史失败: {str(e)}")
            return {
                'total': 0,
                'page': page,
                'per_page': per_page,
                'chats': []
            }
    
    def get_chat_by_id(self, chat_id):
        """获取单条对话"""
        try:
            chat = self.repository.find_by_id(chat_id)
            return chat.to_dict() if chat else None
        except Exception as e:
            print(f"❌ 获取对话失败: {str(e)}")
            return None
    
    def rate_chat(self, chat_id, rating):
        """评分对话（1-5星）"""
        try:
            if not (0 <= rating <= 5):
                return None
            
            chat = self.repository.find_by_id(chat_id)
            if not chat:
                return None
            
            chat.rating = rating
            result = self.repository.update(chat)
            return result.to_dict() if result else None
        except Exception as e:
            print(f"❌ 评分对话失败: {str(e)}")
            return None
    
    def delete_chat(self, chat_id):
        """删除对话"""
        try:
            return self.repository.delete(chat_id)
        except Exception as e:
            print(f"❌ 删除对话失败: {str(e)}")
            return False
    
    def search_similar_chats(self, query, user_id=None, limit=5):
        """搜索相似的对话"""
        try:
            chats = self.repository.search_by_question(query, user_id, limit)
            return [chat.to_dict() for chat in chats]
        except Exception as e:
            print(f"❌ 搜索对话失败: {str(e)}")
            return []


# 创建全局ViewModel实例
chat_viewmodel = ChatViewModel()
