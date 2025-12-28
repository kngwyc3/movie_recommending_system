"""
工具函数 - 文件检查、响应格式化等
"""
from werkzeug.utils import secure_filename
from datetime import datetime
import os
from flask import jsonify
from src.config.app_config import ALLOWED_EXTENSIONS, get_upload_folder


def allowed_file(filename):
    """检查文件是否允许"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def generate_avatar_filename(user_id, original_filename):
    """生成头像文件名"""
    timestamp = int(datetime.now().timestamp())
    ext = original_filename.rsplit('.', 1)[1].lower()
    return secure_filename(f"user_{user_id}_{timestamp}.{ext}")


def success_response(data, message="操作成功", status_code=200):
    """统一的成功响应格式"""
    return jsonify({
        'success': True,
        'data': data,
        'message': message
    }), status_code


def error_response(message, status_code=500):
    """统一的错误响应格式"""
    return jsonify({
        'success': False,
        'message': message
    }), status_code


def not_found_response(message="请求的资源不存在", status_code=404):
    """统一的404响应格式"""
    return jsonify({
        'success': False,
        'message': message
    }), status_code


def bad_request_response(message="请求参数错误", status_code=400):
    """统一的400响应格式"""
    return jsonify({
        'success': False,
        'message': message
    }), status_code


def get_pagination_params():
    """获取分页参数"""
    from flask import request

    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 12, type=int)
    return page, per_page
