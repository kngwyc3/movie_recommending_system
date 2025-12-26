"""
响应实体类 - 统一管理RAG检索和生成结果
用于降低代码耦合度，方便后端接收处理
"""
from typing import List, Dict, Optional, Any
from dataclasses import dataclass, asdict
import json
from datetime import datetime


@dataclass
class RetrievalItem:
    """检索结果项"""
    rank: int
    title: str
    movie_id: str
    score: float
    method: str  # 'vector', 'bm25', 'rerank'
    document: str
    metadata: Dict[str, Any]


@dataclass
class RetrievalResult:
    """检索结果（区分BM25和向量检索）"""
    vector_results: List[RetrievalItem]
    bm25_results: List[RetrievalItem]
    total_count: int


@dataclass
class RerankResult:
    """重排序结果"""
    results: List[RetrievalItem]
    top_n: int


@dataclass
class RAGResponse:
    """RAG完整响应 - 包含所有中间结果和最终输出"""

    # 查询信息
    query: str

    # 检索阶段结果
    retrieval: RetrievalResult

    # 重排序结果
    rerank: RerankResult

    # 推荐的电影ID列表（从重排序结果提取）
    recommended_movie_ids: List[str]

    # LLM生成的用户可见内容
    llm_content: str

    # 元数据
    timestamp: str
    status: str = "success"

    def to_dict(self) -> Dict:
        """转换为字典格式（去除retrieval字段）"""
        data = asdict(self)
        # 移除 retrieval 字段，只保留最终结果
        data.pop('retrieval', None)
        # 将嵌套的RerankItem转换为字典
        data['rerank'] = {
            'results': [asdict(item) for item in self.rerank.results],
            'top_n': self.rerank.top_n
        }
        return data

    def to_json(self, indent: int = 2) -> str:
        """转换为JSON字符串"""
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=indent)

    def to_backend_dict(self) -> Dict:
        """转换为后端友好的简化格式"""
        return {
            'query': self.query,
            'status': self.status,
            'timestamp': self.timestamp,
            'recommended_movie_ids': self.recommended_movie_ids,
            'retrieval_details': {
                'vector_count': len(self.retrieval.vector_results),
                'bm25_count': len(self.retrieval.bm25_results),
                'total_count': self.retrieval.total_count
            },
            'rerank_details': {
                'top_n': self.rerank.top_n,
                'results': [
                    {'rank': r.rank, 'movie_id': r.movie_id, 'title': r.title, 'score': r.score}
                    for r in self.rerank.results
                ]
            },
            'llm_content': self.llm_content
        }

    def to_backend_json(self) -> str:
        """转换为后端友好的JSON格式"""
        return json.dumps(self.to_backend_dict(), ensure_ascii=False)

    @classmethod
    def from_search_results(
        cls,
        query: str,
        vector_results: List[Dict],
        bm25_results: List[Dict],
        rerank_results: List[Dict],
        llm_content: str
    ) -> 'RAGResponse':
        """从搜索结果创建响应实例"""
        # 构建检索结果项
        vector_items = cls._build_retrieval_items(vector_results, 'vector')
        bm25_items = cls._build_retrieval_items(bm25_results, 'bm25')

        # 去重合并
        all_movie_ids = set()
        for item in vector_items + bm25_items:
            all_movie_ids.add(item.movie_id)
        total_count = len(all_movie_ids)

        retrieval = RetrievalResult(
            vector_results=vector_items,
            bm25_results=bm25_items,
            total_count=total_count
        )

        # 构建重排序结果
        rerank_items, recommended_ids = cls._build_rerank_items(
            rerank_results, vector_results, bm25_results
        )

        rerank = RerankResult(
            results=rerank_items,
            top_n=len(rerank_results)
        )

        return cls(
            query=query,
            retrieval=retrieval,
            rerank=rerank,
            recommended_movie_ids=recommended_ids,
            llm_content=llm_content,
            timestamp=datetime.now().isoformat()
        )

    @staticmethod
    def _build_retrieval_items(results: List[Dict], method: str) -> List[RetrievalItem]:
        """构建检索结果项列表"""
        return [
            RetrievalItem(
                rank=i + 1,
                title=result['metadata'].get('title', 'Unknown'),
                movie_id=result['metadata'].get('movie_id', ''),
                score=result['score'],
                method=method,
                document=result['document'],
                metadata=result['metadata']
            )
            for i, result in enumerate(results)
        ]

    @staticmethod
    def _build_rerank_items(
        rerank_results: List[Dict],
        vector_results: List[Dict],
        bm25_results: List[Dict]
    ) -> tuple[List[RetrievalItem], List[str]]:
        """构建重排序结果项和推荐ID列表"""
        rerank_items = []
        recommended_ids = []

        for i, item in enumerate(rerank_results):
            idx = item['id']
            # 从向量和BM25结果中获取原始文档
            doc = vector_results[idx] if idx < len(vector_results) else bm25_results[idx - len(vector_results)]

            rerank_items.append(RetrievalItem(
                rank=i + 1,
                title=doc['metadata'].get('title', 'Unknown'),
                movie_id=doc['metadata'].get('movie_id', ''),
                score=item['score'],
                method='rerank',
                document=doc['document'],
                metadata=doc['metadata']
            ))
            recommended_ids.append(doc['metadata'].get('movie_id', ''))

        return rerank_items, recommended_ids

    @classmethod
    def build_retrieval_details(
        cls,
        vector_results: List[Dict],
        bm25_results: List[Dict],
        combined_results: List[Dict],
        rerank_results: List[Dict]
    ) -> Dict:
        """构建检索和重排序的详细信息（兼容旧接口）"""
        # 构建各种格式的检索结果
        vector_retrieval_details = cls._build_simple_retrieval_details(vector_results, 'vector')
        bm25_retrieval_details = cls._build_simple_retrieval_details(bm25_results, 'bm25')
        retrieval_details = cls._build_simple_retrieval_details(combined_results, None)

        # 构建重排序详细结果和最终结果
        rerank_details, final_results, recommended_ids = cls._build_rerank_details(
            combined_results, rerank_results
        )

        return {
            'vector_retrieval': vector_retrieval_details,
            'bm25_retrieval': bm25_retrieval_details,
            'retrieval': retrieval_details,
            'rerank': rerank_details,
            'final': final_results,
            'recommended_movie_ids': recommended_ids
        }

    @staticmethod
    def _build_simple_retrieval_details(results: List[Dict], method: str = None) -> List[Dict]:
        """构建简单的检索结果详情"""
        return [
            {
                'rank': i + 1,
                'title': result['metadata'].get('title', 'Unknown'),
                'movie_id': result['metadata'].get('movie_id', ''),
                'score': result['score'],
                'method': method if method else result.get('method', ''),
                'document': result['document']
            }
            for i, result in enumerate(results)
        ]

    @staticmethod
    def _build_rerank_details(
        combined_results: List[Dict],
        rerank_results: List[Dict]
    ) -> tuple[List[Dict], List[str], List[str]]:
        """构建重排序详情、最终结果和推荐ID"""
        rerank_details = []
        final_results = []
        recommended_ids = []

        for item in rerank_results:
            idx = item['id']
            doc = combined_results[idx]

            detail = {
                'rank': len(rerank_details) + 1,
                'title': doc['metadata'].get('title', 'Unknown'),
                'movie_id': doc['metadata'].get('movie_id', ''),
                'score': item['score'],
                'document': doc['document']
            }
            rerank_details.append(detail)
            final_results.append(f"- {doc['metadata'].get('title', 'Unknown')}: {doc['document']}")
            recommended_ids.append(doc['metadata'].get('movie_id', ''))

        return rerank_details, final_results, recommended_ids

