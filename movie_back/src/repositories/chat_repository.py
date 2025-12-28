"""
Chat Repository - AI对话历史数据访问层
"""
from src.config.database import db
from src.models.chat_model import ChatModel


class ChatRepository:
    """AI对话历史仓库类"""
    
    def __init__(self):
        # 创建或获取对话集合
        try:
            self.collection = db.client.get_collection(name="ai_chat_history")
            print("✅ 已连接到现有的AI对话历史数据库")
        except:
            self.collection = db.client.create_collection(
                name="ai_chat_history",
                metadata={"description": "AI对话历史数据库"}
            )
            print("✅ 创建了新的AI对话历史数据库")
    
    def create(self, chat):
        """创建新对话记录"""
        try:
            self.collection.add(
                ids=[str(chat.id)],
                documents=[chat.question],  # 用问题作为文档内容，便于向量搜索
                metadatas=[chat.to_metadata()]
            )
            print(f"✅ 对话记录已保存: ID={chat.id}")
            return chat
        except Exception as e:
            print(f"❌ 创建对话记录失败: {str(e)}")
            return None
    
    def find_by_id(self, chat_id):
        """根据ID查找对话"""
        try:
            results = self.collection.get(ids=[str(chat_id)])
            
            if results['ids'] and len(results['ids']) > 0:
                return ChatModel.from_metadata(
                    results['ids'][0],
                    results['metadatas'][0]
                )
            return None
        except Exception as e:
            print(f"❌ 查找对话失败: {str(e)}")
            return None
    
    def find_by_user_id(self, user_id, page=1, per_page=20):
        """获取用户的所有对话记录（分页）"""
        try:
            # 查询该用户的所有对话
            results = self.collection.get(where={"user_id": str(user_id)})
            
            if not results['ids']:
                return []
            
            # 转换为ChatModel对象
            chats = []
            for i, chat_id in enumerate(results['ids']):
                chat = ChatModel.from_metadata(
                    chat_id,
                    results['metadatas'][i]
                )
                chats.append(chat)
            
            # 按创建时间倒序排列（最新的在前）
            chats.sort(key=lambda x: x.created_at, reverse=True)
            
            # 手动分页
            start = (page - 1) * per_page
            end = start + per_page
            return chats[start:end]
        except Exception as e:
            print(f"❌ 获取用户对话失败: {str(e)}")
            return []
    
    def count_by_user_id(self, user_id):
        """统计用户的对话数量"""
        try:
            results = self.collection.get(where={"user_id": str(user_id)})
            return len(results['ids'])
        except Exception as e:
            print(f"❌ 统计用户对话数失败: {str(e)}")
            return 0
    
    def update(self, chat):
        """更新对话记录"""
        try:
            self.collection.update(
                ids=[str(chat.id)],
                documents=[chat.question],
                metadatas=[chat.to_metadata()]
            )
            print(f"✅ 对话记录已更新: ID={chat.id}")
            return chat
        except Exception as e:
            print(f"❌ 更新对话记录失败: {str(e)}")
            return None
    
    def delete(self, chat_id):
        """删除对话记录"""
        try:
            self.collection.delete(ids=[str(chat_id)])
            print(f"✅ 对话记录已删除: ID={chat_id}")
            return True
        except Exception as e:
            print(f"❌ 删除对话记录失败: {str(e)}")
            return False
    
    def search_by_question(self, query, user_id=None, limit=5):
        """搜索相似的问题"""
        try:
            if user_id:
                # 只搜索该用户的对话
                results = self.collection.query(
                    query_texts=[query],
                    where={"user_id": str(user_id)},
                    n_results=limit
                )
            else:
                # 搜索所有对话
                results = self.collection.query(
                    query_texts=[query],
                    n_results=limit
                )
            
            chats = []
            if results['ids'] and len(results['ids']) > 0:
                for i, chat_id in enumerate(results['ids'][0]):
                    chat = ChatModel.from_metadata(
                        chat_id,
                        results['metadatas'][0][i]
                    )
                    chats.append(chat)
            
            return chats
        except Exception as e:
            print(f"❌ 搜索对话失败: {str(e)}")
            return []
    
    def get_all(self, page=1, per_page=20):
        """获取所有对话记录"""
        try:
            results = self.collection.get()
            
            if not results['ids']:
                return []
            
            # 转换为ChatModel对象
            chats = []
            for i, chat_id in enumerate(results['ids']):
                chat = ChatModel.from_metadata(
                    chat_id,
                    results['metadatas'][i]
                )
                chats.append(chat)
            
            # 按创建时间倒序排列
            chats.sort(key=lambda x: x.created_at, reverse=True)
            
            # 手动分页
            start = (page - 1) * per_page
            end = start + per_page
            return chats[start:end]
        except Exception as e:
            print(f"❌ 获取所有对话失败: {str(e)}")
            return []


# 创建全局仓库实例
chat_repository = ChatRepository()
