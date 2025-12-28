"""
AI ViewModel - AI 功能视图模型/业务逻辑层
通过 HTTP 调用独立的 Movie AI 服务 (5001端口)
"""
from typing import List, Dict, Any
from src.services.ai_service import ai_service


class AIViewModel:
    """AI 视图模型类 - 处理 AI 相关业务逻辑"""

    def __init__(self):
        """初始化 AI ViewModel"""
        self.ai_service = ai_service

    def search(self, query: str, mode: str = "hybrid",
                top_k: int = 5, rerank: bool = False) -> List[Dict[str, Any]]:
        """
        执行检索逻辑（向量/BM25/混合）

        Args:
            query: 查询文本
            mode: 检索模式 (vector, bm25, hybrid)
            top_k: 返回结果数量
            rerank: 是否启用重排序

        Returns:
            检索结果列表
        """
        try:
            # 根据模式选择检索方法
            if mode == "vector":
                results = self.ai_service.vector_search(query, top_k=top_k)
            elif mode == "bm25":
                results = self.ai_service.bm25_search(query, top_k=top_k)
            elif mode == "hybrid":
                # 混合检索
                search_data = self.ai_service.hybrid_search(query, top_k=top_k, separate=False)
                results = search_data.get('results', [])
            else:
                raise ValueError(f"不支持的检索模式: {mode}")

            # 如果需要重排序
            if rerank and results:
                doc_texts = [doc['document'] for doc in results]
                rerank_results = self.ai_service.rerank(query=query, documents=doc_texts, top_n=top_k)

                # 使用重排序后的结果重新组织
                reranked = []
                for item in rerank_results:
                    idx = item['id']
                    if idx < len(results):
                        result = results[idx].copy()
                        result['rerank_score'] = item['score']
                        reranked.append(result)

                return reranked

            return results

        except Exception as e:
            print(f"⚠️  检索失败: {e}")
            raise RuntimeError(f"检索失败: {str(e)}")

    def chat(self, query: str, top_k: int = 5) -> Dict[str, Any]:
        """
        执行智能问答（包含检索和 LLM 生成）

        Args:
            query: 用户问题
            top_k: 检索的文档数量

        Returns:
            包含检索结果和 LLM 回答的字典
        """
        try:
            # 调用 AI 服务的推荐接口
            response = self.ai_service.recommend(query, top_k=top_k, rerank_top_n=3)

            return {
                "query": response.get('query', query),
                "answer": response.get('llm_content', ''),
                "retrieval": {
                    "vector_results": [],
                    "bm25_results": [],
                    "rerank_results": response.get('rerank', {}).get('results', [])
                },
                "recommended_movie_ids": response.get('recommended_movie_ids', [])
            }

        except Exception as e:
            print(f"⚠️  智能问答失败: {e}")
            raise RuntimeError(f"智能问答失败: {str(e)}")

    def rerank(self, query: str, documents: List[str], top_n: int = 5) -> List[Dict[str, Any]]:
        """
        对文档列表进行重排序

        Args:
            query: 原始查询
            documents: 文档列表
            top_n: 返回前N个结果

        Returns:
            重排序后的文档列表，包含分数
        """
        try:
            return self.ai_service.rerank(query=query, documents=documents, top_n=top_n)

        except Exception as e:
            print(f"⚠️  重排序失败: {e}")
            raise RuntimeError(f"重排序失败: {str(e)}")

    def get_retrieval_details(self, query: str) -> Dict[str, Any]:
        """
        获取检索的详细信息（包含所有中间结果）

        Args:
            query: 查询文本

        Returns:
            包含向量检索、BM25检索、重排序等详细信息的字典
        """
        try:
            # 调用推荐接口获取完整信息
            response = self.ai_service.recommend(query, top_k=5, rerank_top_n=3)
            
            return {
                'vector_retrieval': [],
                'bm25_retrieval': [],
                'retrieval': [],
                'rerank': response.get('rerank', {}).get('results', []),
                'final': [item.get('document', '') for item in response.get('rerank', {}).get('results', [])],
                'recommended_movie_ids': response.get('recommended_movie_ids', [])
            }
        except Exception as e:
            print(f"⚠️  获取检索详情失败: {e}")
            raise RuntimeError(f"获取检索详情失败: {str(e)}")


# 创建全局ViewModel实例
ai_viewmodel = AIViewModel()
