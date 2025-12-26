"""
电影相关路由
"""
from flask import request, jsonify
from viewmodels.movie_viewmodel import movie_viewmodel
from utils.helpers import (
    success_response, error_response, bad_request_response,
    get_pagination_params
)


def register_routes(app):
    """注册所有电影路由"""

    @app.route('/api/movies/hot', methods=['GET'])
    def get_hot_movies():
        """获取热门电影列表"""
        try:
            page, per_page = get_pagination_params()
            hot_movies = movie_viewmodel.get_hot_movies(page, per_page)

            return success_response({
                'total': 8,
                'page': page,
                'per_page': per_page,
                'movies': hot_movies
            })
        except Exception as e:
            return error_response(f'获取热门电影失败: {str(e)}')

    @app.route('/api/movies/new', methods=['GET'])
    def get_new_movies():
        """获取最新上映电影列表"""
        try:
            page, per_page = get_pagination_params()
            new_movies = movie_viewmodel.get_new_movies(page, per_page)

            return success_response({
                'total': 4,
                'page': page,
                'per_page': per_page,
                'movies': new_movies
            })
        except Exception as e:
            return error_response(f'获取最新电影失败: {str(e)}')

    @app.route('/api/movies/featured', methods=['GET'])
    def get_featured_movie():
        """获取特色推荐电影（横幅展示）"""
        try:
            featured = movie_viewmodel.get_featured_movie()
            return success_response(featured)
        except Exception as e:
            return error_response(f'获取特色电影失败: {str(e)}')

    @app.route('/api/movies/category/<category>', methods=['GET'])
    def get_movies_by_category(category):
        """根据分类筛选电影"""
        try:
            page, per_page = get_pagination_params()
            movies = movie_viewmodel.get_movies_by_category(category, page, per_page)
            total = movie_viewmodel.get_category_count(category)

            return success_response({
                'total': total,
                'category': category,
                'page': page,
                'per_page': per_page,
                'movies': movies
            })
        except Exception as e:
            return error_response(f'获取分类电影失败: {str(e)}')

    @app.route('/api/movies/categories', methods=['GET'])
    def get_categories():
        """获取所有电影分类"""
        try:
            categories = movie_viewmodel.get_all_categories()
            return success_response(categories)
        except Exception as e:
            return error_response(f'获取分类失败: {str(e)}')

    @app.route('/api/movies/search', methods=['GET'])
    def search_movies():
        """搜索电影"""
        try:
            query = request.args.get('q', '', type=str)
            page, per_page = get_pagination_params()

            if not query or len(query.strip()) == 0:
                return bad_request_response('搜索关键词不能为空')

            movies = movie_viewmodel.search_movies(query, page, per_page)
            total = movie_viewmodel.get_search_count(query)

            return success_response({
                'total': total,
                'query': query,
                'page': page,
                'per_page': per_page,
                'movies': movies
            })
        except Exception as e:
            return error_response(f'搜索电影失败: {str(e)}')

    @app.route('/api/movies/<int:movie_id>', methods=['GET'])
    def get_movie_detail(movie_id):
        """获取电影详情"""
        try:
            movie = movie_viewmodel.get_movie_by_id(movie_id)

            if movie is None:
                return bad_request_response('电影不存在', status_code=404)

            return success_response(movie)
        except Exception as e:
            return error_response(f'获取电影详情失败: {str(e)}')

    @app.route('/api/movies', methods=['GET'])
    def get_all_movies():
        """获取所有电影列表"""
        try:
            page, per_page = get_pagination_params()
            movies = movie_viewmodel.get_all_movies(page, per_page)
            total = movie_viewmodel.get_category_count('全部')

            return success_response({
                'total': total,
                'page': page,
                'per_page': per_page,
                'movies': movies
            })
        except Exception as e:
            return error_response(f'获取电影列表失败: {str(e)}')

    @app.route('/api/chat/assistant', methods=['POST'])
    def chat_with_assistant():
        """电影智能助手聊天接口"""
        try:
            data = request.get_json()

            if not data or 'question' not in data:
                return bad_request_response('请提供问题内容')

            question = data['question']
            conversation_history = data.get('conversation_history', None)

            if not question or len(question.strip()) == 0:
                return bad_request_response('问题内容不能为空')

            response = movie_viewmodel.chat_with_assistant(question, conversation_history)
            return success_response(response)
        except Exception as e:
            return error_response(f'智能助手处理失败: {str(e)}')
