"""
推荐系统路由 - 提供动态推荐和用户行为追踪接口
"""
from flask import request
from src.viewmodels.recommendation_viewmodel import recommendation_viewmodel
from src.utils.helpers import success_response, error_response, bad_request_response


def register_routes(app):
    """注册所有推荐系统路由"""

    @app.route('/api/recommendation/personalized', methods=['GET'])
    def get_personalized_recommendations():
        """
        获取个性化推荐
        
        参数:
            user_id: 用户ID (必需)
            top_k: 返回推荐数量 (默认 10)
            use_dynamic: 是否使用动态推荐 (默认 true)
        
        返回:
            推荐电影列表 [(movie_id, score), ...]
        """
        try:
            # 获取参数
            user_id = request.args.get('user_id', type=int)
            top_k = request.args.get('top_k', 10, type=int)
            use_dynamic = request.args.get('use_dynamic', True, type=bool)
            
            # 参数校验
            if user_id is None:
                return bad_request_response('user_id 参数不能为空')
            
            if top_k < 1 or top_k > 50:
                return bad_request_response('top_k 必须在 1-50 之间')
            
            # 获取推荐
            recommendations = recommendation_viewmodel.get_personalized_recommendations(
                user_id=user_id,
                top_k=top_k,
                use_dynamic=use_dynamic
            )
            
            return success_response({
                'user_id': user_id,
                'top_k': top_k,
                'use_dynamic': use_dynamic,
                'recommendations': recommendations
            }, message='个性化推荐成功')
            
        except Exception as e:
            return error_response(f'获取个性化推荐失败: {str(e)}')

    @app.route('/api/recommendation/behavior', methods=['POST'])
    def record_user_behavior():
        """
        记录用户行为
        
        请求体:
            {
                "user_id": 1,           # 用户ID (必需)
                "movie_id": 10,         # 电影ID (必需)
                "behavior_type": "click", # 行为类型 (必需)
                "metadata": {           # 额外元数据 (可选)
                    "rating": 5,
                    "watch_duration": 3600
                }
            }
        
        行为类型:
            - click: 点击/浏览
            - view: 观看
            - favorite: 收藏
            - like: 喜欢
            - watch: 完整观看
            - rate: 评分 (需要在 metadata 中提供 rating 值，0-10分制)
                - 8-10分: rate_high (权重0.7)
                - 5-7分: rate_medium (权重0.5)
                - 1-4分: rate_low (权重0.3)
            - share: 分享
            - comment: 评论
        
        返回:
            记录结果
        """
        try:
            data = request.get_json()
            
            # 参数校验
            if not data:
                return bad_request_response('请提供请求参数')
            
            user_id = data.get('user_id')
            movie_id = data.get('movie_id')
            behavior_type = data.get('behavior_type')
            metadata = data.get('metadata', {})
            
            if user_id is None:
                return bad_request_response('user_id 不能为空')
            
            if movie_id is None:
                return bad_request_response('movie_id 不能为空')
            
            if not behavior_type:
                return bad_request_response('behavior_type 不能为空')
            
            # 记录行为
            success = recommendation_viewmodel.record_user_behavior(
                user_id=user_id,
                movie_id=movie_id,
                behavior_type=behavior_type,
                metadata=metadata
            )
            
            if success:
                return success_response({
                    'user_id': user_id,
                    'movie_id': movie_id,
                    'behavior_type': behavior_type
                }, message='用户行为记录成功')
            else:
                return error_response('用户行为记录失败')
            
        except Exception as e:
            return error_response(f'记录用户行为失败: {str(e)}')

    @app.route('/api/recommendation/behavior/batch', methods=['POST'])
    def record_user_behaviors():
        """
        批量记录用户行为（未实现 - movie_ai 服务暂不支持批量接口）

        TODO: 需要在 movie_ai 服务中实现批量行为记录接口
        """
        return error_response('批量记录用户行为功能暂未实现')

    @app.route('/api/recommendation/user/history', methods=['GET'])
    def get_user_behavior_history():
        """
        获取用户行为历史

        参数:
            user_id: 用户ID (必需)
            limit: 返回数量限制 (默认 50)
            behavior_type: 筛选特定行为类型 (可选)

        返回:
            行为历史列表
        """
        try:
            # 获取参数
            user_id = request.args.get('user_id', type=int)
            limit = request.args.get('limit', 50, type=int)
            behavior_type = request.args.get('behavior_type', type=str)

            # 参数校验
            if user_id is None:
                return bad_request_response('user_id 参数不能为空')

            if limit < 1 or limit > 200:
                return bad_request_response('limit 必须在 1-200 之间')

            # 获取行为历史
            history = recommendation_viewmodel.get_user_behavior_history(
                user_id=user_id,
                limit=limit,
                behavior_type=behavior_type
            )

            return success_response({
                'user_id': user_id,
                'limit': limit,
                'behavior_type': behavior_type,
                'history': history,
                'total': len(history)
            }, message='获取行为历史成功')

        except Exception as e:
            return error_response(f'获取行为历史失败: {str(e)}')

    @app.route('/api/recommendation/similar-movies/<int:movie_id>', methods=['GET'])
    def get_similar_movies(movie_id):
        """
        查找相似电影

        参数:
            movie_id: 电影ID (必需)
            top_k: 返回数量 (默认 10)

        返回:
            相似电影列表
        """
        try:
            # 获取参数
            top_k = request.args.get('top_k', 10, type=int)

            # 参数校验
            if top_k < 1 or top_k > 50:
                return bad_request_response('top_k 必须在 1-50 之间')

            # 获取相似电影
            similar_movies = recommendation_viewmodel.get_similar_movies(
                movie_id=movie_id,
                top_k=top_k
            )

            return success_response({
                'movie_id': movie_id,
                'top_k': top_k,
                'similar_movies': similar_movies
            }, message='获取相似电影成功')

        except Exception as e:
            return error_response(f'获取相似电影失败: {str(e)}')

    @app.route('/api/recommendation/statistics', methods=['GET'])
    def get_recommendation_statistics():
        """
        获取推荐系统统计信息
        
        返回:
            统计信息 (用户数、行为数、行为分布等)
        """
        try:
            stats = recommendation_viewmodel.get_statistics()
            
            return success_response(stats, message='获取统计信息成功')
            
        except Exception as e:
            return error_response(f'获取统计信息失败: {str(e)}')

    @app.route('/api/recommendation/hot', methods=['GET'])
    def get_hot_movies():
        """
        获取热门电影推荐（用于新用户冷启动）

        参数:
            top_k: 返回数量 (默认 10)

        返回:
            热门电影列表
        """
        try:
            # 获取参数
            top_k = request.args.get('top_k', 10, type=int)

            # 参数校验
            if top_k < 1 or top_k > 50:
                return bad_request_response('top_k 必须在 1-50 之间')

            # 获取热门电影
            hot_movies = recommendation_viewmodel.get_hot_movies(top_k=top_k)

            return success_response({
                'top_k': top_k,
                'hot_movies': hot_movies
            }, message='获取热门电影成功')

        except Exception as e:
            return error_response(f'获取热门电影失败: {str(e)}')
