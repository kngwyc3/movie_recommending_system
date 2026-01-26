"""
Recommendation Service - 调用 Movie AI 推荐系统服务 (5001端口)
"""
import requests
from typing import List, Dict, Any, Optional
import json
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()


class RecommendationService:
    """推荐系统服务客户端 - 调用独立的 Movie AI 推荐服务"""

    def __init__(self, base_url: str = None):
        """
        初始化推荐服务客户端

        Args:
            base_url: Movie AI 服务的基础 URL，默认从环境变量读取
        """
        if base_url is None:
            base_url = os.getenv('MOVIE_AI_SERVICE_URL', 'http://localhost:5001')

        self.base_url = base_url.rstrip('/')
        self.timeout = int(os.getenv('RECOMMENDATION_SERVICE_TIMEOUT', '30'))

    def health_check(self) -> Dict[str, Any]:
        """
        健康检查

        Returns:
            服务状态信息
        """
        try:
            response = requests.get(
                f"{self.base_url}/ai/health",
                timeout=5
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            raise RuntimeError(f"推荐服务健康检查失败: {str(e)}")

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
            response = requests.get(
                f"{self.base_url}/ai/recommendation/personalized",
                params={
                    'user_id': user_id,
                    'top_k': top_k,
                    'use_dynamic': use_dynamic
                },
                timeout=self.timeout
            )
            response.raise_for_status()
            result = response.json()

            if not result.get('success'):
                raise RuntimeError(result.get('message', '获取推荐失败'))

            return result['data']

        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"调用推荐服务失败: {str(e)}")

    def record_user_behavior(
        self,
        user_id: int,
        movie_id: int,
        behavior_type: str,
        metadata: Optional[Dict[str, Any]] = None
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
            response = requests.post(
                f"{self.base_url}/ai/recommendation/behavior",
                json={
                    'user_id': user_id,
                    'movie_id': movie_id,
                    'behavior_type': behavior_type,
                    'metadata': metadata or {}
                },
                timeout=self.timeout
            )
            response.raise_for_status()
            result = response.json()

            if not result.get('success'):
                raise RuntimeError(result.get('message', '记录行为失败'))

            return result['data']

        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"调用记录行为服务失败: {str(e)}")

    def get_statistics(self) -> Dict[str, Any]:
        """
        获取推荐系统统计信息

        Returns:
            统计信息 (用户数、行为数、行为分布等)
        """
        try:
            response = requests.get(
                f"{self.base_url}/ai/recommendation/statistics",
                timeout=self.timeout
            )
            response.raise_for_status()
            result = response.json()

            if not result.get('success'):
                raise RuntimeError(result.get('message', '获取统计信息失败'))

            return result['data']

        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"调用统计信息服务失败: {str(e)}")

    def get_similar_movies(self, movie_id: int, top_k: int = 10) -> List[Dict[str, Any]]:
        """
        查找相似电影

        Args:
            movie_id: 电影ID
            top_k: 返回数量 (默认 10)

        Returns:
            相似电影列表
        """
        try:
            response = requests.get(
                f"{self.base_url}/ai/recommendation/similar-movies/{movie_id}",
                params={'top_k': top_k},
                timeout=self.timeout
            )
            response.raise_for_status()
            result = response.json()

            if not result.get('success'):
                raise RuntimeError(result.get('message', '获取相似电影失败'))

            return result['data']['similar_movies']

        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"调用相似电影服务失败: {str(e)}")

    def get_hot_movies(self, top_k: int = 10) -> List[Dict[str, Any]]:
        """
        获取热门电影推荐（用于新用户冷启动）

        Args:
            top_k: 返回数量 (默认 10)

        Returns:
            热门电影列表
        """
        try:
            response = requests.get(
                f"{self.base_url}/ai/recommendation/hot",
                params={'top_k': top_k},
                timeout=self.timeout
            )
            response.raise_for_status()
            result = response.json()

            if not result.get('success'):
                raise RuntimeError(result.get('message', '获取热门电影失败'))

            return result['data']['hot_movies']

        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"调用热门电影服务失败: {str(e)}")

    def get_user_behavior_history(
        self,
        user_id: int,
        limit: int = 50,
        behavior_type: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        获取用户行为历史

        Args:
            user_id: 用户ID
            limit: 返回数量限制 (默认 50)
            behavior_type: 筛选特定行为类型 (可选)

        Returns:
            行为历史列表
        """
        try:
            params = {'user_id': user_id, 'limit': limit}
            if behavior_type:
                params['behavior_type'] = behavior_type

            response = requests.get(
                f"{self.base_url}/ai/recommendation/user/history",
                params=params,
                timeout=self.timeout
            )
            response.raise_for_status()
            result = response.json()

            if not result.get('success'):
                raise RuntimeError(result.get('message', '获取行为历史失败'))

            return result['data']['history']

        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"调用行为历史服务失败: {str(e)}")


# 创建全局实例
recommendation_service = RecommendationService()
