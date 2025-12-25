"""
RAG 模块 - 简化版：直接调用检索+重排序+LLM
"""
from typing import List, Dict
from src.config import Config
from src.llm import QwenLLM
from src.retriever import retriever
from src.rerank import reranker


class RAGChain:
    """简化的 RAG 处理器 - 直接调用检索+重排序+LLM"""
    
    def __init__(self, top_k: int = 10, rerank_top_n: int = 5):
        self.top_k = top_k
        self.rerank_top_n = rerank_top_n
        self.llm = QwenLLM()
    
    def _get_context(self, query: str) -> str:
        """检索+重排序，返回格式化的上下文"""
        # 1. 检索
        results = retriever.search(query, method='hybrid', top_k=self.top_k)
        if not results:
            return "暂无相关电影信息"
        
        # 2. 重排序
        doc_texts = [doc['document'] for doc in results]
        rerank_results = reranker.rerank(query=query, documents=doc_texts, top_n=self.rerank_top_n)
        
        # 3. 格式化输出
        context_parts = []
        for item in rerank_results:
            doc = results[item['id']]
            context_parts.append(f"- {doc['metadata'].get('title', 'Unknown')}: {doc['document']}")
        
        return "\n".join(context_parts)
    
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
        """执行 RAG 查询"""
        context = self._get_context(question)
        messages = self._build_messages(context, question)
        return self.llm.invoke(messages)
    
    def query_stream(self, question):
        """执行 RAG 流式查询"""
        context = self._get_context(question)
        messages = self._build_messages(context, question)
        return self.llm.stream(messages)


# 创建全局实例
rag_chain = RAGChain()
