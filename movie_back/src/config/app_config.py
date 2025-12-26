"""
Flask 应用配置
"""
from flask import Flask
from flask_cors import CORS
from datetime import timedelta
import os

# 应用实例
app = Flask(__name__)

# ==================== JWT 配置 ====================
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(minutes=10)

# ==================== 文件上传配置 ====================
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB最大文件大小
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
UPLOAD_FOLDER = 'uploads/avatars'

# 创建上传目录
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

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
