from flask import Flask, jsonify, request
from flask_cors import CORS
from src.viewmodels.movie_viewmodel import movie_viewmodel
from src.viewmodels.user_viewmodel import user_viewmodel
from src.viewmodels.auth_viewmodel import auth_viewmodel
import os
import base64
from werkzeug.utils import secure_filename
from datetime import datetime
from datetime import timedelta

app = Flask(__name__)

# 配置文件上传


app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(minutes=10)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB最大文件大小
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
UPLOAD_FOLDER = 'uploads/avatars'

# 创建上传目录
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# 配置 CORS，允许前端跨域访问
CORS(app, resources={
    r"/api/*": {
        "origins": ["http://localhost:5173", "http://localhost:5174", "http://localhost:3000"],
        "methods": ["GET", "POST", "PUT", "DELETE"],
        "allow_headers": ["Content-Type"]
    }
})

# 配置
app.config['JSON_AS_ASCII'] = False  # 支持中文 JSON
app.config['JSONIFY_MIMETYPE'] = "application/json;charset=utf-8"


@app.route('/api/movies/hot', methods=['GET'])
def get_hot_movies():
    """获取热门电影列表"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 8, type=int)
        
        hot_movies = movie_viewmodel.get_hot_movies(page, per_page)
        
        return jsonify({
            'success': True,
            'data': hot_movies,
            'total': 8,
            'page': page,
            'per_page': per_page
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'获取热门电影失败: {str(e)}'
        }), 500


@app.route('/api/movies/new', methods=['GET'])
def get_new_movies():
    """获取最新上映电影列表"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 4, type=int)
        
        new_movies = movie_viewmodel.get_new_movies(page, per_page)
        
        return jsonify({
            'success': True,
            'data': new_movies,
            'total': 4,
            'page': page,
            'per_page': per_page
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'获取最新电影失败: {str(e)}'
        }), 500


@app.route('/api/movies/featured', methods=['GET'])
def get_featured_movie():
    """获取特色推荐电影（横幅展示）"""
    try:
        featured = movie_viewmodel.get_featured_movie()
        
        return jsonify({
            'success': True,
            'data': featured
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'获取特色电影失败: {str(e)}'
        }), 500


@app.route('/api/movies/category/<category>', methods=['GET'])
def get_movies_by_category(category):
    """根据分类筛选电影"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 12, type=int)
        
        movies = movie_viewmodel.get_movies_by_category(category, page, per_page)
        total = movie_viewmodel.get_category_count(category)
        
        return jsonify({
            'success': True,
            'data': movies,
            'total': total,
            'category': category,
            'page': page,
            'per_page': per_page
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'获取分类电影失败: {str(e)}'
        }), 500


@app.route('/api/movies/categories', methods=['GET'])
def get_categories():
    """获取所有电影分类"""
    try:
        categories = movie_viewmodel.get_all_categories()
        
        return jsonify({
            'success': True,
            'data': categories
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'获取分类失败: {str(e)}'
        }), 500


@app.route('/api/movies/search', methods=['GET'])
def search_movies():
    """搜索电影"""
    try:
        query = request.args.get('q', '', type=str)
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 12, type=int)
        
        if not query or len(query.strip()) == 0:
            return jsonify({
                'success': False,
                'message': '搜索关键词不能为空'
            }), 400
        
        movies = movie_viewmodel.search_movies(query, page, per_page)
        total = movie_viewmodel.get_search_count(query)
        
        return jsonify({
            'success': True,
            'data': movies,
            'total': total,
            'query': query,
            'page': page,
            'per_page': per_page
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'搜索电影失败: {str(e)}'
        }), 500


@app.route('/api/movies/<int:movie_id>', methods=['GET'])
def get_movie_detail(movie_id):
    """获取电影详情"""
    try:
        movie = movie_viewmodel.get_movie_by_id(movie_id)
        
        if movie is None:
            return jsonify({
                'success': False,
                'message': '电影不存在'
            }), 404
        
        return jsonify({
            'success': True,
            'data': movie
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'获取电影详情失败: {str(e)}'
        }), 500


@app.route('/api/chat/assistant', methods=['POST'])
def chat_with_assistant():
    """电影智能助手聊天接口"""
    try:
        data = request.get_json()
        
        if not data or 'question' not in data:
            return jsonify({
                'success': False,
                'message': '请提供问题内容'
            }), 400
        
        question = data['question']
        conversation_history = data.get('conversation_history', None)
        
        if not question or len(question.strip()) == 0:
            return jsonify({
                'success': False,
                'message': '问题内容不能为空'
            }), 400
        
        response = movie_viewmodel.chat_with_assistant(question, conversation_history)
        
        return jsonify({
            'success': True,
            'data': response
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'智能助手处理失败: {str(e)}'
        }), 500


@app.route('/api/movies', methods=['GET'])
def get_all_movies():
    """获取所有电影列表"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 12, type=int)
        
        movies = movie_viewmodel.get_all_movies(page, per_page)
        total = movie_viewmodel.get_category_count('全部')
        
        return jsonify({
            'success': True,
            'data': movies,
            'total': total,
            'page': page,
            'per_page': per_page
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'获取电影列表失败: {str(e)}'
        }), 500


@app.route('/api/health', methods=['GET'])
def health_check():
    """健康检查接口"""
    return jsonify({
        'success': True,
        'message': 'Movie API is running!',
        'version': '1.0.0'
    }), 200


# ==================== 认证相关接口 ====================

@app.route('/api/auth/register', methods=['POST'])
def register():
    """用户注册"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'message': '请提供注册信息'
            }), 400
        
        username = data.get('username', '').strip()
        email = data.get('email', '').strip()
        password = data.get('password', '')
        
        result = auth_viewmodel.register(username, email, password)
        
        if result['success']:
            return jsonify(result), 201
        else:
            return jsonify(result), 400
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'注册失败: {str(e)}'
        }), 500


@app.route('/api/auth/login', methods=['POST'])
def login():
    """用户登录"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'message': '请提供登录信息'
            }), 400
        
        email = data.get('email', '').strip()
        password = data.get('password', '')
        
        result = auth_viewmodel.login(email, password)
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 401
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'登录失败: {str(e)}'
        }), 500


@app.route('/api/auth/verify', methods=['POST'])
def verify_token():
    """验证token"""
    try:
        data = request.get_json()
        
        if not data or 'token' not in data:
            return jsonify({
                'success': False,
                'message': '请提供token'
            }), 400
        
        token = data['token']
        user = auth_viewmodel.verify_token(token)
        
        if user:
            return jsonify({
                'success': True,
                'data': user.to_dict()
            }), 200
        else:
            return jsonify({
                'success': False,
                'message': 'token无效或已过期'
            }), 401
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'验证失败: {str(e)}'
        }), 500


@app.route('/api/auth/change-password', methods=['POST'])
def change_password():
    """修改密码"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'message': '请提供修改密码信息'
            }), 400
        
        email = data.get('email', '').strip()
        old_password = data.get('old_password', '')
        new_password = data.get('new_password', '')
        
        result = auth_viewmodel.change_password(email, old_password, new_password)
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'修改密码失败: {str(e)}'
        }), 500


# ==================== 用户相关接口 ====================

@app.route('/api/user/<int:user_id>', methods=['GET'])
def get_user_profile(user_id):
    """获取用户信息"""
    try:
        profile = user_viewmodel.get_user_profile(user_id)
        
        if profile is None:
            return jsonify({
                'success': False,
                'message': '用户不存在'
            }), 404
        
        return jsonify({
            'success': True,
            'data': profile
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'获取用户信息失败: {str(e)}'
        }), 500


@app.route('/api/user/<int:user_id>', methods=['PUT'])
def update_user_profile(user_id):
    """更新用户信息"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'message': '请提供更新数据'
            }), 400
        
        user = user_viewmodel.update_user_profile(user_id, data)
        
        if user is None:
            return jsonify({
                'success': False,
                'message': '用户不存在或更新失败'
            }), 404
        
        return jsonify({
            'success': True,
            'data': user.to_dict()
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'更新用户信息失败: {str(e)}'
        }), 500


@app.route('/api/user/<int:user_id>/preferences', methods=['PUT'])
def update_preferences(user_id):
    """更新用户偏好设置"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'message': '请提供偏好设置数据'
            }), 400
        
        user = user_viewmodel.update_preferences(user_id, data)
        
        if user is None:
            return jsonify({
                'success': False,
                'message': '用户不存在或更新失败'
            }), 404
        
        return jsonify({
            'success': True,
            'data': user.to_dict()
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'更新偏好设置失败: {str(e)}'
        }), 500


@app.route('/api/user/<int:user_id>/avatar', methods=['POST'])
def upload_avatar(user_id):
    """上传用户头像"""
    try:
        # 检查是否有文件
        if 'avatar' not in request.files:
            return jsonify({
                'success': False,
                'message': '没有提供avatar文件'
            }), 400
        
        file = request.files['avatar']
        
        if file.filename == '':
            return jsonify({
                'success': False,
                'message': '需要选择一个文件'
            }), 400
        
        # 检查文件类型
        if not allowed_file(file.filename):
            return jsonify({
                'success': False,
                'message': '仅支持 png, jpg, jpeg, gif 格式'
            }), 400
        
        # 确保上传目录存在
        if not os.path.exists(UPLOAD_FOLDER):
            os.makedirs(UPLOAD_FOLDER, exist_ok=True)
        
        # 保存文件
        filename = secure_filename(f"user_{user_id}_{int(datetime.now().timestamp())}.{file.filename.rsplit('.', 1)[1].lower()}")
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        
        # 保存文件
        file.save(file_path)
        
        # 检查文件是否真的被保存
        if not os.path.exists(file_path):
            return jsonify({
                'success': False,
                'message': '文件保存失败'
            }), 500
        
        print(f"✅ 文件已保存: {file_path}")
        
        # 更新用户头像路径
        avatar_url = f"/uploads/avatars/{filename}"
        user = user_viewmodel.update_user_profile(user_id, {'avatar': avatar_url})
        
        if user is None:
            return jsonify({
                'success': False,
                'message': '用户不存在'
            }), 404
        
        return jsonify({
            'success': True,
            'message': '上传成功',
            'data': {
                'avatar_url': avatar_url,
                'user': user.to_dict()
            }
        }), 200
    except Exception as e:
        import traceback
        print(f"❌ 上传失败: {str(e)}")
        traceback.print_exc()
        return jsonify({
            'success': False,
            'message': f'上传失败: {str(e)}'
        }), 500


def allowed_file(filename):
    """检查文件是否允许"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/uploads/<path:filename>', methods=['GET'])
def serve_upload(filename):
    """提供上传文件下载

    说明：
    - 头像等文件会保存在 uploads/avatars/ 下
    - URL 形如 /uploads/avatars/<file>
    - 需要用 uploads 作为根目录来解析子路径，避免重复拼接 avatars 目录
    """
    from flask import send_from_directory
    try:
        # filename 可能包含子目录（如 avatars/<file>），使用 uploads 作为根目录即可
        return send_from_directory('uploads', filename)
    except Exception:
        return jsonify({
            'success': False,
            'message': '文件不存在'
        }), 404


@app.route('/api/user/<int:user_id>/privacy', methods=['PUT'])
def update_privacy_settings(user_id):
    """更新隐私设置"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'message': '请提供隐私设置数据'
            }), 400
        
        user = user_viewmodel.update_privacy_settings(user_id, data)
        
        if user is None:
            return jsonify({
                'success': False,
                'message': '用户不存在或更新失败'
            }), 404
        
        return jsonify({
            'success': True,
            'data': user.to_dict()
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'更新隐私设置失败: {str(e)}'
        }), 500


@app.route('/api/user/<int:user_id>/favorites', methods=['GET'])
def get_favorites(user_id):
    """获取用户收藏列表"""
    try:
        favorites = user_viewmodel.get_favorites(user_id)
        
        return jsonify({
            'success': True,
            'data': favorites,
            'total': len(favorites)
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'获取收藏列表失败: {str(e)}'
        }), 500


@app.route('/api/user/<int:user_id>/favorites/<int:movie_id>', methods=['POST'])
def add_favorite(user_id, movie_id):
    """添加收藏"""
    try:
        success = user_viewmodel.add_favorite(user_id, movie_id)
        
        if not success:
            return jsonify({
                'success': False,
                'message': '添加收藏失败'
            }), 400
        
        return jsonify({
            'success': True,
            'message': '添加收藏成功'
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'添加收藏失败: {str(e)}'
        }), 500


@app.route('/api/user/<int:user_id>/favorites/<int:movie_id>', methods=['DELETE'])
def remove_favorite(user_id, movie_id):
    """移除收藏"""
    try:
        success = user_viewmodel.remove_favorite(user_id, movie_id)
        
        if not success:
            return jsonify({
                'success': False,
                'message': '移除收藏失败'
            }), 400
        
        return jsonify({
            'success': True,
            'message': '移除收藏成功'
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'移除收藏失败: {str(e)}'
        }), 500


@app.route('/api/user/<int:user_id>/history', methods=['GET'])
def get_watch_history(user_id):
    """获取观看历史"""
    try:
        history = user_viewmodel.get_watch_history(user_id)
        
        return jsonify({
            'success': True,
            'data': history,
            'total': len(history)
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'获取观看历史失败: {str(e)}'
        }), 500


@app.route('/api/user/<int:user_id>/history/<int:movie_id>', methods=['POST'])
def add_watch_history(user_id, movie_id):
    """添加观看历史"""
    try:
        success = user_viewmodel.add_watch_history(user_id, movie_id)
        
        if not success:
            return jsonify({
                'success': False,
                'message': '添加观看历史失败'
            }), 400
        
        return jsonify({
            'success': True,
            'message': '添加观看历史成功'
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'添加观看历史失败: {str(e)}'
        }), 500


@app.route('/api/user/<int:user_id>/ratings', methods=['GET'])
def get_user_ratings(user_id):
    """获取用户评分列表"""
    try:
        ratings = user_viewmodel.get_user_ratings(user_id)
        
        return jsonify({
            'success': True,
            'data': ratings,
            'total': len(ratings)
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'获取评分列表失败: {str(e)}'
        }), 500


@app.route('/api/user/<int:user_id>/rate/<int:movie_id>', methods=['POST'])
def rate_movie(user_id, movie_id):
    """评分电影"""
    try:
        data = request.get_json()
        
        if not data or 'rating' not in data:
            return jsonify({
                'success': False,
                'message': '请提供评分'
            }), 400
        
        rating = data['rating']
        if not isinstance(rating, (int, float)) or rating < 0 or rating > 10:
            return jsonify({
                'success': False,
                'message': '评分必须在0-10之间'
            }), 400
        
        success = user_viewmodel.rate_movie(user_id, movie_id, rating)
        
        if not success:
            return jsonify({
                'success': False,
                'message': '评分失败'
            }), 400
        
        return jsonify({
            'success': True,
            'message': '评分成功'
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'评分失败: {str(e)}'
        }), 500


@app.errorhandler(404)
def not_found(error):
    """404 错误处理"""
    return jsonify({
        'success': False,
        'message': '请求的资源不存在'
    }), 404


@app.errorhandler(500)
def internal_error(error):
    """500 错误处理"""
    return jsonify({
        'success': False,
        'message': '服务器内部错误'
    }), 500


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('DEBUG', 'True') == 'True'
    
    print(f"🚀 Movie API Server is starting on http://localhost:{port}")
    print(f"📚 API Documentation: http://localhost:{port}/api/health")
    print(f"🎬 Hot Movies: http://localhost:{port}/api/movies/hot")
    print(f"🆕 New Movies: http://localhost:{port}/api/movies/new")
    print(f"⭐ Featured: http://localhost:{port}/api/movies/featured")
    
    app.run(host='0.0.0.0', port=port, debug=debug)
