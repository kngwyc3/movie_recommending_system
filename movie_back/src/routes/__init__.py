"""
路由模块初始化
"""
# 这些导入延迟进行，避免模块初始化时的循环依赖问题

__all__ = [
    'register_movie_routes',
    'register_auth_routes',
    'register_user_routes',
    'register_file_routes',
    'register_common_routes',
    'register_ai_routes',
]
