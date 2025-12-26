"""
RAG 模块 - 简化版：直接调用检索+重排序+LLM
"""
from typing import List, Dict, Optional
from src.config import Config
from src.llm import QwenLLM
from src.retriever import retriever
from src.rerank import reranker
from utils.response import RAGResponse


class RAGChain:
    """简化的 RAG 处理器 - 直接调用检索+重排序+LLM"""

    def __init__(self, top_k: int = None, rerank_top_n: int = None):
        # 从配置读取默认参数，如果传入参数则覆盖配置
        self.top_k = top_k if top_k is not None else Config.TOP_K
        self.rerank_top_n = rerank_top_n if rerank_top_n is not None else Config.RERANK_TOP_N
        self.llm = QwenLLM()

    def get_retrieval_details(self, query: str) -> Dict:
        """获取检索和重排序的详细信息（兼容旧接口）"""
        # 1. 分别执行向量检索和BM25检索
        search_results = retriever.hybrid_search(query, top_k=self.top_k, separate=True)

        vector_results = search_results['vector_results']
        bm25_results = search_results['bm25_results']
        combined_results = search_results['combined_results']

        if not combined_results:
            return {
                'vector_retrieval': [],
                'bm25_retrieval': [],
                'retrieval': [],
                'rerank': [],
                'final': [],
                'recommended_movie_ids': []
            }

        # 2. 重排序（使用合并后的结果）
        doc_texts = [doc['document'] for doc in combined_results]
        rerank_results = reranker.rerank(query=query, documents=doc_texts, top_n=self.rerank_top_n)

        # 3. 使用RAGResponse的静态方法构建详细信息
        return RAGResponse.build_retrieval_details(
            vector_results, bm25_results, combined_results, rerank_results
        )

    def get_full_response(self, query: str) -> RAGResponse:
        """获取完整的RAG响应（包含所有中间结果）"""
        # 1. 分别执行向量检索和BM25检索
        search_results = retriever.hybrid_search(query, top_k=self.top_k, separate=True)
        vector_results = search_results['vector_results']
        bm25_results = search_results['bm25_results']
        combined_results = search_results['combined_results']

        # 2. 重排序
        rerank_results = []
        if combined_results:
            doc_texts = [doc['document'] for doc in combined_results]
            rerank_results = reranker.rerank(query=query, documents=doc_texts, top_n=self.rerank_top_n)

        # 3. 生成LLM内容
        context = self._get_context(combined_results, rerank_results)
        messages = self._build_messages(context, query)
        llm_content = self.llm.invoke(messages)

        # 4. 构建响应对象
        return RAGResponse.from_search_results(
            query=query,
            vector_results=vector_results,
            bm25_results=bm25_results,
            rerank_results=rerank_results,
            llm_content=llm_content
        )

    def get_full_response_stream(self, query: str) -> RAGResponse:
        """获取完整的RAG响应（流式生成LLM内容）"""
        # 1. 分别执行向量检索和BM25检索
        search_results = retriever.hybrid_search(query, top_k=self.top_k, separate=True)
        vector_results = search_results['vector_results']
        bm25_results = search_results['bm25_results']
        combined_results = search_results['combined_results']

        # 2. 重排序
        rerank_results = []
        if combined_results:
            doc_texts = [doc['document'] for doc in combined_results]
            rerank_results = reranker.rerank(query=query, documents=doc_texts, top_n=self.rerank_top_n)

        # 3. 生成LLM内容（流式）
        context = self._get_context(combined_results, rerank_results)
        messages = self._build_messages(context, query)
        llm_content = ""
        for chunk in self.llm.stream(messages):
            if chunk.choices and len(chunk.choices) > 0:
                content = chunk.choices[0].delta.content
                if content:
                    llm_content += content

        # 4. 构建响应对象
        return RAGResponse.from_search_results(
            query=query,
            vector_results=vector_results,
            bm25_results=bm25_results,
            rerank_results=rerank_results,
            llm_content=llm_content
        )

    def _get_context(self, combined_results: List[Dict], rerank_results: List[Dict]) -> str:
        """检索+重排序，返回格式化的上下文"""
        if not combined_results:
            return "暂无相关电影信息"

        # 使用重排序后的结果构建上下文
        context_parts = []
        for item in rerank_results:
            idx = item['id']
            doc = combined_results[idx]
            context_parts.append(f"- {doc['metadata'].get('title', 'Unknown')}: {doc['document']}")

        return "\n".join(context_parts) if context_parts else "暂无相关电影信息"

    def _build_messages(self, context: str, question: str) -> List[Dict[str, str]]:
        """构建 messages"""
        return [
            {
                "role": "system",
                "content": f"""根据提供的电影信息为用户推荐电影。

**规则**：
1. 必须推荐检索清单中的所有电影
2. 可补充 1-2 部类似电影

直接以自然语言的形式推荐电影，包括电影名、推荐理由等。

电影信息：
{context}"""
            },
            {"role": "user", "content": question}
        ]

    def query(self, question: str) -> str:
        """执行 RAG 查询（兼容旧接口）"""
        response = self.get_full_response(question)
        return response.llm_content

    def query_stream(self, question):
        """执行 RAG 流式查询（兼容旧接口）"""
        context = self._get_context_with_details(question)['context']
        messages = self._build_messages(context, question)
        return self.llm.stream(messages)

    def _get_context_with_details(self, query: str) -> Dict:
        """获取上下文和详细信息（内部使用）"""
        details = self.get_retrieval_details(query)
        return {
            'context': "\n".join(details['final']) if details['final'] else "暂无相关电影信息",
            'details': details
        }


# 创建全局实例
rag_chain = RAGChain()
