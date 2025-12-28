"""
用户相关路由
"""
import os
import traceback
from flask import request, jsonify
from src.viewmodels.user_viewmodel import user_viewmodel
from src.utils.helpers import (
    success_response, error_response, bad_request_response,
    allowed_file, generate_avatar_filename, get_upload_folder
)


def register_routes(app):
    """注册所有用户路由"""

    @app.route('/api/user/<int:user_id>', methods=['GET'])
    def get_user_profile(user_id):
        """获取用户信息"""
        try:
            profile = user_viewmodel.get_user_profile(user_id)

            if profile is None:
                return bad_request_response('用户不存在', status_code=404)

            return success_response(profile)
        except Exception as e:
            return error_response(f'获取用户信息失败: {str(e)}')

    @app.route('/api/user/<int:user_id>', methods=['PUT'])
    def update_user_profile(user_id):
        """更新用户信息"""
        try:
            data = request.get_json()

            if not data:
                return bad_request_response('请提供更新数据')

            user = user_viewmodel.update_user_profile(user_id, data)

            if user is None:
                return bad_request_response('用户不存在或更新失败', status_code=404)

            return success_response(user.to_dict())
        except Exception as e:
            return error_response(f'更新用户信息失败: {str(e)}')

    @app.route('/api/user/<int:user_id>/preferences', methods=['PUT'])
    def update_preferences(user_id):
        """更新用户偏好设置"""
        try:
            data = request.get_json()

            if not data:
                return bad_request_response('请提供偏好设置数据')

            user = user_viewmodel.update_preferences(user_id, data)

            if user is None:
                return bad_request_response('用户不存在或更新失败', status_code=404)

            return success_response(user.to_dict())
        except Exception as e:
            return error_response(f'更新偏好设置失败: {str(e)}')

    @app.route('/api/user/<int:user_id>/avatar', methods=['POST'])
    def upload_avatar(user_id):
        """上传用户头像"""
        try:
            if 'avatar' not in request.files:
                return bad_request_response('没有提供avatar文件')

            file = request.files['avatar']

            if file.filename == '':
                return bad_request_response('需要选择一个文件')

            if not allowed_file(file.filename):
                return bad_request_response('仅支持 png, jpg, jpeg, gif 格式')

            upload_folder = get_upload_folder()

            if not os.path.exists(upload_folder):
                os.makedirs(upload_folder, exist_ok=True)

            filename = generate_avatar_filename(user_id, file.filename)
            file_path = os.path.join(upload_folder, filename)

            file.save(file_path)

            if not os.path.exists(file_path):
                return error_response('文件保存失败')

            print(f"✅ 文件已保存: {file_path}")

            avatar_url = f"/uploads/avatars/{filename}"
            user = user_viewmodel.update_user_profile(user_id, {'avatar': avatar_url})

            if user is None:
                return bad_request_response('用户不存在', status_code=404)

            return success_response({
                'avatar_url': avatar_url,
                'user': user.to_dict()
            }, message='上传成功')
        except Exception as e:
            traceback.print_exc()
            return error_response(f'上传失败: {str(e)}')

    @app.route('/api/user/<int:user_id>/privacy', methods=['PUT'])
    def update_privacy_settings(user_id):
        """更新隐私设置"""
        try:
            data = request.get_json()

            if not data:
                return bad_request_response('请提供隐私设置数据')

            user = user_viewmodel.update_privacy_settings(user_id, data)

            if user is None:
                return bad_request_response('用户不存在或更新失败', status_code=404)

            return success_response(user.to_dict())
        except Exception as e:
            return error_response(f'更新隐私设置失败: {str(e)}')

    @app.route('/api/user/<int:user_id>/favorites', methods=['GET'])
    def get_favorites(user_id):
        """获取用户收藏列表"""
        try:
            favorites = user_viewmodel.get_favorites(user_id)
            return success_response({
                'favorites': favorites,
                'total': len(favorites)
            })
        except Exception as e:
            return error_response(f'获取收藏列表失败: {str(e)}')

    @app.route('/api/user/<int:user_id>/favorites/<int:movie_id>', methods=['POST'])
    def add_favorite(user_id, movie_id):
        """添加收藏"""
        try:
            success = user_viewmodel.add_favorite(user_id, movie_id)

            if not success:
                return bad_request_response('添加收藏失败')

            return success_response(None, message='添加收藏成功')
        except Exception as e:
            return error_response(f'添加收藏失败: {str(e)}')

    @app.route('/api/user/<int:user_id>/favorites/<int:movie_id>', methods=['DELETE'])
    def remove_favorite(user_id, movie_id):
        """移除收藏"""
        try:
            success = user_viewmodel.remove_favorite(user_id, movie_id)

            if not success:
                return bad_request_response('移除收藏失败')

            return success_response(None, message='移除收藏成功')
        except Exception as e:
            return error_response(f'移除收藏失败: {str(e)}')

    @app.route('/api/user/<int:user_id>/history', methods=['GET'])
    def get_watch_history(user_id):
        """获取观看历史"""
        try:
            history = user_viewmodel.get_watch_history(user_id)
            return success_response({
                'history': history,
                'total': len(history)
            })
        except Exception as e:
            return error_response(f'获取观看历史失败: {str(e)}')

    @app.route('/api/user/<int:user_id>/history/<int:movie_id>', methods=['POST'])
    def add_watch_history(user_id, movie_id):
        """添加观看历史"""
        try:
            print(f'📝 添加观看历史: user_id={user_id}, movie_id={movie_id}')
            success = user_viewmodel.add_watch_history(user_id, movie_id)
            print(f'📝 添加结果: {success}')

            if not success:
                print(f'❌ 添加观看历史失败: user_id={user_id}, movie_id={movie_id}')
                return bad_request_response('添加观看历史失败')

            return success_response(None, message='添加观看历史成功')
        except Exception as e:
            print(f'❌ 添加观看历史异常: {str(e)}')
            import traceback
            traceback.print_exc()
            return error_response(f'添加观看历史失败: {str(e)}')

    @app.route('/api/user/<int:user_id>/ratings', methods=['GET'])
    def get_user_ratings(user_id):
        """获取用户评分列表"""
        try:
            ratings = user_viewmodel.get_user_ratings(user_id)
            return success_response({
                'ratings': ratings,
                'total': len(ratings)
            })
        except Exception as e:
            return error_response(f'获取评分列表失败: {str(e)}')

    @app.route('/api/user/<int:user_id>/rate/<int:movie_id>', methods=['POST'])
    def rate_movie(user_id, movie_id):
        """评分电影"""
        try:
            data = request.get_json()

            if not data or 'rating' not in data:
                return bad_request_response('请提供评分')

            rating = data['rating']
            if not isinstance(rating, (int, float)) or rating < 0 or rating > 10:
                return bad_request_response('评分必须在0-10之间')

            success = user_viewmodel.rate_movie(user_id, movie_id, rating)

            if not success:
                return bad_request_response('评分失败')

            return success_response(None, message='评分成功')
        except Exception as e:
            return error_response(f'评分失败: {str(e)}')
