"""
文件服务路由
"""
from flask import send_from_directory
from src.config.app_config import UPLOAD_FOLDER
from src.utils.helpers import bad_request_response
import os


def register_routes(app):
    """注册所有文件服务路由"""

    @app.route('/uploads/<path:filename>', methods=['GET'])
    def serve_upload(filename):
        """提供上传文件下载"""
        try:
            # UPLOAD_FOLDER 是 movie_back/uploads/avatars
            # 我们需要 movie_back/uploads 作为根目录
            uploads_dir = os.path.dirname(UPLOAD_FOLDER)
            return send_from_directory(uploads_dir, filename)
        except Exception as e:
            print(f'❌ 文件服务错误: {str(e)}')
            return bad_request_response('文件不存在', status_code=404)
