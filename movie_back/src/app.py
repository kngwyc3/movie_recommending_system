"""
Flask 应用入口 - 整合所有路由模块
"""
import os
from config.app_config import app
from routes.movie_routes import register_routes as register_movie_routes
from routes.auth_routes import register_routes as register_auth_routes
from routes.user_routes import register_routes as register_user_routes
from routes.file_routes import register_routes as register_file_routes
from routes.common_routes import register_routes as register_common_routes


def register_all_routes():
    """注册所有路由模块"""
    register_movie_routes(app)
    register_auth_routes(app)
    register_user_routes(app)
    register_file_routes(app)
    register_common_routes(app)


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

    app.run(host='0.0.0.0', port=port, debug=debug, use_reloader=True)
