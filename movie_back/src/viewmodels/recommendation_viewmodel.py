"""
Recommendation ViewModel - 推荐系统视图模型/业务逻辑层
通过 HTTP 调用独立的 Movie AI 推荐服务 (5001端口)
"""
from typing import List, Dict, Any
from src.services.recommendation_service import recommendation_service


class RecommendationViewModel:
    """推荐系统视图模型类 - 处理推荐相关业务逻辑"""

    def __init__(self):
        """初始化推荐 ViewModel"""
        self.recommendation_service = recommendation_service

    def get_personalized_recommendations(
        self,
        user_id: int,
        top_k: int = 10,
        use_dynamic: bool = True
    ) -> Dict[str, Any]:
        """
        获取个性化推荐

        Args:
            user_id: 用户ID
            top_k: 返回推荐数量 (默认 10)
            use_dynamic: 是否使用动态推荐 (默认 true)

        Returns:
            推荐结果，包含电影ID列表和分数
        """
        try:
            return self.recommendation_service.get_personalized_recommendations(
                user_id=user_id,
                top_k=top_k,
                use_dynamic=use_dynamic
            )

        except Exception as e:
            print(f"⚠️  获取个性化推荐失败: {e}")
            raise RuntimeError(f"获取个性化推荐失败: {str(e)}")

    def record_user_behavior(
        self,
        user_id: int,
        movie_id: int,
        behavior_type: str,
        metadata: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        记录用户行为

        Args:
            user_id: 用户ID
            movie_id: 电影ID
            behavior_type: 行为类型 (click, view, favorite, like, watch, rate_high, rate_medium, rate_low, share, comment)
            metadata: 额外元数据

        Returns:
            记录结果
        """
        try:
            return self.recommendation_service.record_user_behavior(
                user_id=user_id,
                movie_id=movie_id,
                behavior_type=behavior_type,
                metadata=metadata
            )

        except Exception as e:
            print(f"⚠️  记录用户行为失败: {e}")
            raise RuntimeError(f"记录用户行为失败: {str(e)}")

    def get_statistics(self) -> Dict[str, Any]:
        """
        获取推荐系统统计信息

        Returns:
            统计信息 (用户数、行为数、行为分布等)
        """
        try:
            return self.recommendation_service.get_statistics()

        except Exception as e:
            print(f"⚠️  获取统计信息失败: {e}")
            raise RuntimeError(f"获取统计信息失败: {str(e)}")

    def get_user_behavior_history(
        self,
        user_id: int,
        limit: int = 50,
        behavior_type: str = None
    ) -> List[Dict[str, Any]]:
        """
        获取用户行为历史（TODO: 需要在 movie_ai 服务中实现相应接口）

        Args:
            user_id: 用户ID
            limit: 返回数量限制 (默认 50)
            behavior_type: 筛选特定行为类型 (可选)

        Returns:
            行为历史列表
        """
        # TODO: 需要在 movie_ai 服务中实现获取用户行为历史的接口
        print(f"⚠️  get_user_behavior_history 功能待实现: user_id={user_id}")
        return []

    def get_similar_movies(self, movie_id: int, top_k: int = 10) -> List[Dict[str, Any]]:
        """
        查找相似电影（TODO: 需要在 movie_ai 服务中实现相应接口）

        Args:
            movie_id: 电影ID
            top_k: 返回数量 (默认 10)

        Returns:
            相似电影列表
        """
        # TODO: 需要在 movie_ai 服务中实现相似电影推荐的接口
        print(f"⚠️  get_similar_movies 功能待实现: movie_id={movie_id}")
        return []

    def get_hot_movies(self, top_k: int = 10) -> List[Dict[str, Any]]:
        """
        获取热门电影推荐（用于新用户冷启动）
        （TODO: 需要在 movie_ai 服务中实现相应接口）

        Args:
            top_k: 返回数量 (默认 10)

        Returns:
            热门电影列表
        """
        # TODO: 需要在 movie_ai 服务中实现热门电影推荐的接口
        print(f"⚠️  get_hot_movies 功能待实现: top_k={top_k}")
        return []

    def rate_movie(
        self,
        user_id: int,
        movie_id: int,
        rating: int
    ) -> Dict[str, Any]:
        """
        评分电影（便捷方法）

        Args:
            user_id: 用户ID
            movie_id: 电影ID
            rating: 评分 (0-10分制)

        Returns:
            记录结果
        """
        # 根据0-10分制映射到行为类型
        if rating >= 8:
            behavior_type = 'rate_high'
        elif rating >= 5:
            behavior_type = 'rate_medium'
        else:
            behavior_type = 'rate_low'

        return self.record_user_behavior(
            user_id=user_id,
            movie_id=movie_id,
            behavior_type=behavior_type,
            metadata={'rating': rating}
        )

    def like_movie(self, user_id: int, movie_id: int) -> Dict[str, Any]:
        """
        点赞电影（便捷方法）

        Args:
            user_id: 用户ID
            movie_id: 电影ID

        Returns:
            记录结果
        """
        return self.record_user_behavior(
            user_id=user_id,
            movie_id=movie_id,
            behavior_type='like'
        )

    def favorite_movie(self, user_id: int, movie_id: int) -> Dict[str, Any]:
        """
        收藏电影（便捷方法）

        Args:
            user_id: 用户ID
            movie_id: 电影ID

        Returns:
            记录结果
        """
        return self.record_user_behavior(
            user_id=user_id,
            movie_id=movie_id,
            behavior_type='favorite'
        )

    def share_movie(self, user_id: int, movie_id: int) -> Dict[str, Any]:
        """
        分享电影（便捷方法）

        Args:
            user_id: 用户ID
            movie_id: 电影ID

        Returns:
            记录结果
        """
        return self.record_user_behavior(
            user_id=user_id,
            movie_id=movie_id,
            behavior_type='share'
        )

    def comment_movie(
        self,
        user_id: int,
        movie_id: int,
        comment: str
    ) -> Dict[str, Any]:
        """
        评论电影（便捷方法）

        Args:
            user_id: 用户ID
            movie_id: 电影ID
            comment: 评论内容

        Returns:
            记录结果
        """
        return self.record_user_behavior(
            user_id=user_id,
            movie_id=movie_id,
            behavior_type='comment',
            metadata={'comment': comment}
        )


# 创建全局ViewModel实例
recommendation_viewmodel = RecommendationViewModel()
