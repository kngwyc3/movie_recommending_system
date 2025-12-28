"""
配置模块初始化
"""
from src.config.app_config import app, get_upload_folder, get_allowed_extensions

__all__ = [
    'app',
    'get_upload_folder',
    'get_allowed_extensions',
]
