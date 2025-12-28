"""
认证相关路由
"""
from flask import request, jsonify
from src.viewmodels.auth_viewmodel import auth_viewmodel
from src.utils.helpers import success_response, error_response, bad_request_response


def register_routes(app):
    """注册所有认证路由"""

    @app.route('/api/auth/register', methods=['POST'])
    def register():
        """用户注册"""
        try:
            data = request.get_json()

            if not data:
                return bad_request_response('请提供注册信息')

            username = data.get('username', '').strip()
            email = data.get('email', '').strip()
            password = data.get('password', '')

            result = auth_viewmodel.register(username, email, password)

            if result['success']:
                return jsonify(result), 201
            else:
                return jsonify(result), 400
        except Exception as e:
            return error_response(f'注册失败: {str(e)}')

    @app.route('/api/auth/login', methods=['POST'])
    def login():
        """用户登录"""
        try:
            data = request.get_json()

            if not data:
                return bad_request_response('请提供登录信息')

            email = data.get('email', '').strip()
            password = data.get('password', '')

            result = auth_viewmodel.login(email, password)

            if result['success']:
                return jsonify(result), 200
            else:
                return jsonify(result), 401
        except Exception as e:
            return error_response(f'登录失败: {str(e)}')

    @app.route('/api/auth/verify', methods=['POST'])
    def verify_token():
        """验证token"""
        try:
            data = request.get_json()

            if not data or 'token' not in data:
                return bad_request_response('请提供token')

            token = data['token']
            user = auth_viewmodel.verify_token(token)

            if user:
                return success_response(user.to_dict())
            else:
                return bad_request_response('token无效或已过期', status_code=401)
        except Exception as e:
            return error_response(f'验证失败: {str(e)}')

    @app.route('/api/auth/change-password', methods=['POST'])
    def change_password():
        """修改密码"""
        try:
            data = request.get_json()

            if not data:
                return bad_request_response('请提供修改密码信息')

            email = data.get('email', '').strip()
            old_password = data.get('old_password', '')
            new_password = data.get('new_password', '')

            result = auth_viewmodel.change_password(email, old_password, new_password)

            if result['success']:
                return jsonify(result), 200
            else:
                return jsonify(result), 400
        except Exception as e:
            return error_response(f'修改密码失败: {str(e)}')
