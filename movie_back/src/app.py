"""
Flask 应用入口 - 整合所有路由模块
"""
import os
import sys

# 添加 movie_back 目录到 Python 路径
# 这样可以使用 src.xxx 的绝对导入方式
current_dir = os.path.dirname(os.path.abspath(__file__))
movie_back_dir = os.path.dirname(current_dir)
if movie_back_dir not in sys.path:
    sys.path.insert(0, movie_back_dir)

from src.config.app_config import app


def register_all_routes():
    """注册所有路由模块"""
    # 在函数内部导入，避免循环导入问题
    from src.routes.movie_routes import register_routes as register_movie_routes
    from src.routes.auth_routes import register_routes as register_auth_routes
    from src.routes.user_routes import register_routes as register_user_routes
    from src.routes.file_routes import register_routes as register_file_routes
    from src.routes.common_routes import register_routes as register_common_routes
    from src.routes.ai_routes import register_routes as register_ai_routes
    from src.routes.chat_routes import register_routes as register_chat_routes

    # 注册所有路由
    register_movie_routes(app)
    register_auth_routes(app)
    register_user_routes(app)
    register_file_routes(app)
    register_common_routes(app)
    register_ai_routes(app)
    register_chat_routes(app)


if __name__ == '__main__':
    # 注册所有路由
    register_all_routes()

    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('DEBUG', 'True') == 'True'

    print(f"🚀 Movie API Server is starting on http://localhost:{port}")
    print(f"📚 API Documentation: http://localhost:{port}/api/health")
    print(f"🎬 Hot Movies: http://localhost:{port}/api/movies/hot")
    print(f"🆕 New Movies: http://localhost:{port}/api/movies/new")
    print(f"⭐ Featured: http://localhost:{port}/api/movies/featured")
    print(f"🤖 AI Search: http://localhost:{port}/api/ai/search")
    print(f"💬 AI Chat: http://localhost:{port}/api/ai/chat")

    app.run(host='0.0.0.0', port=port, debug=debug, use_reloader=True)
