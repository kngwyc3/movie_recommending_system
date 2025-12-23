"""
User Repository - 用户数据访问层
负责所有用户数据库操作
"""
from src.config.database import db
from src.models.user_model import UserModel
import chromadb


class UserRepository:
    """用户数据仓库类"""
    
    def __init__(self):
        # 创建或获取用户集合
        try:
            self.collection = db.client.get_collection(name="users")
        except:
            self.collection = db.client.create_collection(
                name="users",
                metadata={"description": "用户信息数据库"}
            )
    
    def create(self, user):
        """创建新用户"""
        try:
            self.collection.add(
                ids=[str(user.id)],
                documents=[""],
                metadatas=[user.to_metadata()]
            )
            return user
        except Exception as e:
            print(f"❌ 创建用户失败: {str(e)}")
            return None
    
    def find_by_id(self, user_id):
        """根据ID查找用户"""
        try:
            results = self.collection.get(ids=[str(user_id)])
            
            if results['ids'] and len(results['ids']) > 0:
                return UserModel.from_metadata(
                    results['ids'][0],
                    results['metadatas'][0]
                )
            return None
        except Exception as e:
            print(f"❌ 查找用户失败: {str(e)}")
            return None
    
    def find_by_email(self, email):
        """根据邮箱查找用户"""
        try:
            results = self.collection.get(where={"email": email})
            
            if results['ids'] and len(results['ids']) > 0:
                return UserModel.from_metadata(
                    results['ids'][0],
                    results['metadatas'][0]
                )
            return None
        except Exception as e:
            print(f"❌ 根据邮箱查找用户失败: {str(e)}")
            return None
    
    def update(self, user):
        """更新用户信息"""
        try:
            self.collection.update(
                ids=[str(user.id)],
                documents=[""],
                metadatas=[user.to_metadata()]
            )
            return user
        except Exception as e:
            print(f"❌ 更新用户失败: {str(e)}")
            return None
    
    def delete(self, user_id):
        """删除用户"""
        try:
            self.collection.delete(ids=[str(user_id)])
            return True
        except Exception as e:
            print(f"❌ 删除用户失败: {str(e)}")
            return False
    
    def get_user_favorites(self, user_id):
        """获取用户收藏的电影ID列表"""
        user = self.find_by_id(user_id)
        return user.favorites if user else []
    
    def get_user_watch_history(self, user_id):
        """获取用户观看历史"""
        user = self.find_by_id(user_id)
        return user.watch_history if user else []
    
    def get_user_ratings(self, user_id):
        """获取用户评分"""
        user = self.find_by_id(user_id)
        return user.ratings if user else {}
    
    def get_next_user_id(self):
        """获取下一个用户ID"""
        try:
            all_users = self.collection.get()
            if not all_users['ids']:
                return 1
            # 获取最大ID，加1
            max_id = max([int(uid) for uid in all_users['ids']])
            return max_id + 1
        except Exception as e:
            print(f"❌ 获取下一个ID失败: {str(e)}")
            return 1
    
    def email_exists(self, email):
        """检查邮箱是否已存在"""
        user = self.find_by_email(email)
        return user is not None
    
    def username_exists(self, username):
        """检查用户名是否已存在"""
        try:
            results = self.collection.get(where={"username": username})
            return results['ids'] and len(results['ids']) > 0
        except Exception as e:
            print(f"❌ 检查用户名失败: {str(e)}")
            return False


# 创建全局仓库实例
user_repository = UserRepository()
