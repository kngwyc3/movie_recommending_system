"""
Flask 应用配置
"""
from flask import Flask
from flask_cors import CORS
from datetime import timedelta
import os
import sys

# ==================== movie_ai 路径配置 ====================
# 添加 movie_ai 到 Python 路径，以便导入其模块
# 因为 movie_ai/src 中的文件使用 from src.xxx import 的导入方式
# 从 movie_back/src/config/app_config.py
# 向上三级：config -> src -> movie_back -> vue，然后进入 movie_ai
current_dir = os.path.dirname(os.path.abspath(__file__))
movie_ai_path = os.path.abspath(os.path.join(current_dir, '../../../movie_ai'))
movie_ai_src_path = os.path.join(movie_ai_path, 'src')

if movie_ai_path not in sys.path:
    sys.path.insert(0, movie_ai_path)

# 定义 movie_ai 相关路径常量
MOVIE_AI_PATH = movie_ai_path
MOVIE_AI_SRC_PATH = movie_ai_src_path

# 应用实例
app = Flask(__name__)

# ==================== JWT 配置 ====================
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(minutes=10)

# ==================== 文件上传配置 ====================
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB最大文件大小
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

# 使用绝对路径，确保文件保存在 movie_back/uploads/avatars
movie_back_dir = os.path.dirname(os.path.dirname(current_dir))  # 从 config -> src -> movie_back
UPLOAD_FOLDER = os.path.join(movie_back_dir, 'uploads', 'avatars')

# 创建上传目录
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    print(f"📁 创建上传目录: {UPLOAD_FOLDER}")

# ==================== CORS 配置 ====================
CORS(app, resources={
    r"/api/*": {
        "origins": ["http://localhost:5173", "http://localhost:5174", "http://localhost:3000"],
        "methods": ["GET", "POST", "PUT", "DELETE"],
        "allow_headers": ["Content-Type"]
    }
})

# ==================== JSON 配置 ====================
app.config['JSON_AS_ASCII'] = False  # 支持中文 JSON
app.config['JSONIFY_MIMETYPE'] = "application/json;charset=utf-8"


def get_upload_folder():
    """获取上传文件夹路径"""
    return UPLOAD_FOLDER


def get_allowed_extensions():
    """获取允许的文件扩展名"""
    return ALLOWED_EXTENSIONS
