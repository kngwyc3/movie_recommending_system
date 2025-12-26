"""
初始化测试用户数据
"""
import sys
import os

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'src'))

from models.user_model import UserModel
from repositories.user_repository import user_repository


def init_test_user():
    """初始化测试用户"""
    
    # 检查用户是否已存在
    existing = user_repository.find_by_id(1)
    if existing:
        print("⚠️  测试用户已存在，跳过初始化")
        print(f"   用户名: {existing.username}")
        print(f"   邮箱: {existing.email}")
        print(f"   密码: 123456")
        return
    
    # 创建测试用户
    test_user = UserModel(
        id=1,
        username="星际探索者",
        email="explorer@scifi.com",
        avatar="https://api.dicebear.com/7.x/avataaars/svg?seed=explorer",
        favorites=[1, 2, 3],  # 收藏了黑客帝国、阿凡达、沙丘
        watch_history=[
            {'movie_id': 1, 'watched_at': '2024-12-20T10:30:00'},
            {'movie_id': 4, 'watched_at': '2024-12-21T14:20:00'},
            {'movie_id': 7, 'watched_at': '2024-12-22T20:15:00'}
        ],
        ratings={
            '1': {'rating': 9.5, 'rated_at': '2024-12-20T10:45:00'},
            '4': {'rating': 9.3, 'rated_at': '2024-12-21T14:30:00'},
            '7': {'rating': 8.5, 'rated_at': '2024-12-22T20:25:00'}
        },
        preferences={
            'favorite_genres': ['科幻', '动作'],
            'theme': 'dark',
            'auto_play': True,
            'quality': 'high'
        },
        privacy_settings={
            'public_watch_history': True,
            'public_favorites': True
        }
    )
    
    # 设置密码（会自动加密）
    test_user.set_password('123456')
    
    result = user_repository.create(test_user)
    
    if result:
        print("✅ 成功创建测试用户")
        print(f"   ID: {test_user.id}")
        print(f"   用户名: {test_user.username}")
        print(f"   邮箱: {test_user.email}")
        print(f"   密码: 123456")
        print(f"   收藏: {len(test_user.favorites)} 部电影")
        print(f"   观影历史: {len(test_user.watch_history)} 部")
        print(f"   评分: {len(test_user.ratings)} 部")
        print("")
        print("🔑 登录信息:")
        print(f"   邮箱: explorer@scifi.com")
        print(f"   密码: 123456")
    else:
        print("❌ 创建测试用户失败")


if __name__ == '__main__':
    init_test_user()
