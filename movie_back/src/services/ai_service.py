"""
AI Service - 调用 Movie AI 服务 (5001端口)
"""
import requests
from typing import List, Dict, Any, Optional
import json
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()


class AIService:
    """AI 服务客户端 - 调用独立的 Movie AI 服务"""

    def __init__(self, base_url: str = None):
        """
        初始化 AI 服务客户端

        Args:
            base_url: Movie AI 服务的基础 URL，默认从环境变量读取
        """
        if base_url is None:
            base_url = os.getenv('MOVIE_AI_SERVICE_URL', 'http://localhost:5001')
        
        self.base_url = base_url.rstrip('/')
        self.timeout = int(os.getenv('AI_SERVICE_TIMEOUT', '30'))

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
            raise RuntimeError(f"AI 服务健康检查失败: {str(e)}")

    def recommend(self, query: str, top_k: int = 5, rerank_top_n: int = 3) -> Dict[str, Any]:
        """
        电影推荐（完整响应）

        Args:
            query: 查询文本
            top_k: 检索数量
            rerank_top_n: 重排序后返回数量

        Returns:
            完整的推荐结果，包含检索、重排序和LLM生成内容
        """
        try:
            response = requests.post(
                f"{self.base_url}/ai/recommend",
                json={
                    'query': query,
                    'top_k': top_k,
                    'rerank_top_n': rerank_top_n
                },
                timeout=self.timeout
            )
            response.raise_for_status()
            result = response.json()

            if not result.get('success'):
                raise RuntimeError(result.get('message', '推荐失败'))

            return result['data']

        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"调用 AI 推荐服务失败: {str(e)}")

    def recommend_stream(self, query: str, top_k: int = 5, rerank_top_n: int = 3):
        """
        电影推荐（流式响应）

        Args:
            query: 查询文本
            top_k: 检索数量
            rerank_top_n: 重排序后返回数量

        Yields:
            流式事件数据
        """
        try:
            response = requests.post(
                f"{self.base_url}/ai/recommend/stream",
                json={
                    'query': query,
                    'top_k': top_k,
                    'rerank_top_n': rerank_top_n
                },
                stream=True,
                timeout=self.timeout
            )
            response.raise_for_status()

            for line in response.iter_lines():
                if line:
                    line_str = line.decode('utf-8')
                    if line_str.startswith('data: '):
                        event_data = json.loads(line_str[6:])
                        yield event_data

        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"调用 AI 流式推荐服务失败: {str(e)}")

    def vector_search(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        向量检索

        Args:
            query: 查询文本
            top_k: 返回结果数量

        Returns:
            检索结果列表
        """
        try:
            response = requests.post(
                f"{self.base_url}/ai/search/vector",
                json={
                    'query': query,
                    'top_k': top_k
                },
                timeout=self.timeout
            )
            response.raise_for_status()
            result = response.json()

            if not result.get('success'):
                raise RuntimeError(result.get('message', '向量检索失败'))

            return result['data']['results']

        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"调用向量检索服务失败: {str(e)}")

    def bm25_search(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        BM25 检索

        Args:
            query: 查询文本
            top_k: 返回结果数量

        Returns:
            检索结果列表
        """
        try:
            response = requests.post(
                f"{self.base_url}/ai/search/bm25",
                json={
                    'query': query,
                    'top_k': top_k
                },
                timeout=self.timeout
            )
            response.raise_for_status()
            result = response.json()

            if not result.get('success'):
                raise RuntimeError(result.get('message', 'BM25检索失败'))

            return result['data']['results']

        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"调用BM25检索服务失败: {str(e)}")

    def hybrid_search(self, query: str, top_k: int = 5,
                     alpha: float = 0.5, separate: bool = False) -> Dict[str, Any]:
        """
        混合检索

        Args:
            query: 查询文本
            top_k: 返回结果数量
            alpha: 向量检索权重
            separate: 是否分别返回向量和BM25结果

        Returns:
            检索结果（格式取决于 separate 参数）
        """
        try:
            response = requests.post(
                f"{self.base_url}/ai/search/hybrid",
                json={
                    'query': query,
                    'top_k': top_k,
                    'alpha': alpha,
                    'separate': separate
                },
                timeout=self.timeout
            )
            response.raise_for_status()
            result = response.json()

            if not result.get('success'):
                raise RuntimeError(result.get('message', '混合检索失败'))

            return result['data']

        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"调用混合检索服务失败: {str(e)}")

    def rerank(self, query: str, documents: List[str], top_n: int = 5) -> List[Dict[str, Any]]:
        """
        重排序

        Args:
            query: 查询文本
            documents: 文档列表
            top_n: 返回前N个结果

        Returns:
            重排序后的结果列表
        """
        try:
            response = requests.post(
                f"{self.base_url}/ai/rerank",
                json={
                    'query': query,
                    'documents': documents,
                    'top_n': top_n
                },
                timeout=self.timeout
            )
            response.raise_for_status()
            result = response.json()

            if not result.get('success'):
                raise RuntimeError(result.get('message', '重排序失败'))

            return result['data']['results']

        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"调用重排序服务失败: {str(e)}")


# 创建全局实例
ai_service = AIService()
