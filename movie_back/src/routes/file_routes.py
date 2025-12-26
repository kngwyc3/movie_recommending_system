"""
文件服务路由
"""
from flask import send_from_directory, jsonify
from utils.helpers import not_found_response, bad_request_response


def register_routes(app):
    """注册所有文件服务路由"""

    @app.route('/uploads/<path:filename>', methods=['GET'])
    def serve_upload(filename):
        """提供上传文件下载

        说明：
        - 头像等文件会保存在 uploads/avatars/ 下
        - URL 形式如 /uploads/avatars/<file>
        - 需要用 uploads 作为根目录来解析子路径，避免重复拼接 avatars 目录
        """
        try:
            return send_from_directory('uploads', filename)
        except Exception:
            return bad_request_response('文件不存在', status_code=404)
