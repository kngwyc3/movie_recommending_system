"""
路由模块初始化
"""
from routes.movie_routes import register_routes as register_movie_routes
from routes.auth_routes import register_routes as register_auth_routes
from routes.user_routes import register_routes as register_user_routes
from routes.file_routes import register_routes as register_file_routes
from routes.common_routes import register_routes as register_common_routes

__all__ = [
    'register_movie_routes',
    'register_auth_routes',
    'register_user_routes',
    'register_file_routes',
    'register_common_routes',
]
