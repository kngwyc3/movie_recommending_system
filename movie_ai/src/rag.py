"""
RAG 模块 - 使用 LangChain 实现完整的 RAG 链式流程
从用户输入 -> 检索 -> 重排序 -> 格式化输出
"""
from multiprocessing import context
from typing import List, Dict, Any
import json
import os
from openai import OpenAI

from langchain_core.runnables import RunnablePassthrough, RunnableLambda
from langchain_core.prompts import ChatPromptTemplate
from langchain_community.adapters.openai import convert_message_to_dict

from src.config import Config
from src.retriever import retriever
from src.rerank import reranker


class QwenLLM:
    """Qwen LLM 包装器 - 兼容 LangChain"""
    
    def __init__(self):
        """初始化 Qwen LLM"""
        self.client = OpenAI(
            api_key=Config.QWEN_API_KEY,
            base_url=Config.QWEN_API_URL
        )
        self.model = Config.QWEN_MODEL
    
    def invoke(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """调用 Qwen API"""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=Config.QWEN_TEMPERATURE,
                max_tokens=Config.QWEN_MAX_TOKENS
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"❌ LLM 调用失败: {e}")
            return "抱歉，生成推荐时出现错误。"
    
    def stream(self, messages: List[Dict[str, str]], **kwargs):
        """流式调用 Qwen API"""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=Config.QWEN_TEMPERATURE,
                max_tokens=Config.QWEN_MAX_TOKENS,
                stream=True
            )
            return response
        except Exception as e:
            print(f"❌ LLM 流式调用失败: {e}")
            return None


class HybridRetriever:
    """混合检索器 - 包含检索和重排序"""
    
    def __init__(self, top_k: int = 10, rerank_top_n: int = 5, verbose: bool = True):
        self.top_k = top_k
        self.rerank_top_n = rerank_top_n
        self.verbose = verbose
    
    def invoke(self, query: str) -> Dict[str, Any]:
        """执行检索和重排序，返回 JSON 格式的上下文"""
        # 步骤1: 混合检索
        results = retriever.search(query, method='hybrid', top_k=self.top_k)

        if not results:
            return {
                "query": query,
                "movies": [],
                "count": 0
            }

        # 步骤2: 重排序
        doc_texts = [doc['document'] for doc in results]
        rerank_results = reranker.rerank(
            query=query,
            documents=doc_texts,
            top_n=self.rerank_top_n
        )

        # 步骤3: 根据重排序顺序重新组织结果
        reranked_results = []
        for item in rerank_results:
            idx = item['id']
            if idx < len(results):
                reranked_results.append(results[idx])

        # 步骤4: 格式化为 JSON
        movies = []
        for doc in reranked_results:
            metadata = doc['metadata']
            movies.append({
                "movie_id": metadata.get('movie_id', 'N/A'),
                "title": metadata.get('title', 'Unknown'),
                "description": doc['document'],
                "score": doc.get('score', 0.0)
            })

        return {
            "query": query,
            "movies": movies,
            "count": len(movies)
        }


class RAGChain:
    """RAG 链式处理器 - 使用 LangChain LCEL 实现"""
    
    def __init__(self, top_k: int = 10, rerank_top_n: int = 5):
        """初始化 RAG 链"""
        # 初始化组件（禁用 verbose 避免重复输出）
        self.hybrid_retriever = HybridRetriever(top_k=top_k, rerank_top_n=rerank_top_n, verbose=False)
        self.llm = QwenLLM()
        
        # 定义提示模板
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", """根据提供的电影信息为用户推荐电影。

**规则**：
1. 必须推荐检索清单中的所有电影
2. 可补充 1-2 部类似电影

直接以自然语言的形式推荐电影，包括电影名、推荐理由等。
使用友好的语气，每部电影用序号列出。

电影信息：
{context}"""),
            ("user", "{query}")
        ])
        
        # 构建 RAG 链（LCEL 风格）
        self.chain = self._build_chain()
    
    def _build_chain(self):
        """构建 LangChain LCEL 链"""
        # 自定义格式化函数
        def format_prompt_inputs(inputs: Dict[str, Any]) -> Dict[str, str]:
            """格式化提示输入"""
            return {
                "context": inputs["context"],
                "query": inputs["query"]
            }
        # 构建 LCEL 链
        chain = (
            {
                "context": RunnableLambda(lambda x: json.dumps(self.hybrid_retriever.invoke(x), ensure_ascii=False)),
                "query": RunnablePassthrough()
            }
            | RunnableLambda(format_prompt_inputs)
            | self.prompt
            | RunnableLambda(lambda prompt_value: [convert_message_to_dict(msg) for msg in prompt_value.messages])
            | RunnableLambda(lambda msgs: self.llm.invoke(msgs))
        )

        return chain
    
    def query(self, question: str) -> str:
        """
        执行 RAG 查询

        Args:
            question: 用户问题

        Returns:
            LLM 生成的推荐文本
        """
        try:
            result = self.chain.invoke(question)
            return result
        except Exception as e:
            print(f"❌ 查询失败: {e}")
            import traceback
            traceback.print_exc()
            return "抱歉，查询过程中出现错误。"
    
    def query_stream(self, question: str):
        """
        执行 RAG 流式查询

        Args:
            question: 用户问题

        Returns:
            LLM 生成的推荐文本流
        """
        try:
            # 检索上下文
            context_data = self.hybrid_retriever.invoke(question)
            context_str = json.dumps(context_data, ensure_ascii=False)
            
            # 格式化 prompt
            prompt_messages = self.prompt.format_messages(
                context=context_str,
                query=question
            )
            messages = [convert_message_to_dict(msg) for msg in prompt_messages]
            
            # 流式调用 LLM
            stream_response = self.llm.stream(messages)
            
            return stream_response
        except Exception as e:
            print(f"❌ 流式查询失败: {e}")
            import traceback
            traceback.print_exc()
            return None


# 创建全局实例
rag_chain = RAGChain()