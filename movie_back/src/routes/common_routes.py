"""
通用路由 - 健康检查、错误处理
"""
from flask import jsonify
from src.utils.helpers import not_found_response, error_response


def register_routes(app):
    """注册所有通用路由"""

    @app.route('/api/health', methods=['GET'])
    def health_check():
        """健康检查接口"""
        return jsonify({
            'success': True,
            'message': 'Movie API is running!',
            'version': '1.0.0'
        }), 200

    @app.errorhandler(404)
    def not_found(error):
        """404 错误处理"""
        return not_found_response()

    @app.errorhandler(500)
    def internal_error(error):
        """500 错误处理"""
        return error_response('服务器内部错误')
