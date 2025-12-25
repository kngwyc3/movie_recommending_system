"""
Rerank 模块 - 使用 Qwen Rerank 模型对检索结果进行重排序
"""
from typing import List, Dict, Any, Optional
from http import HTTPStatus
import dashscope

from src.config import Config


class Reranker:
    """重排序器 - 对检索结果进行精细排序"""

    def __init__(self):
        """初始化重排序器"""
        # 设置 API Key
        dashscope.api_key = Config.QWEN_API_KEY
        self.model = "qwen3-rerank"

    def rerank(
        self,
        query: str,
        documents: List[str],
        top_n: int = 10,
        instruct: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        对文档进行重排序

        Args:
            query: 查询文本
            documents: 文档列表
            top_n: 返回前 N 个结果
            instruct: 重排序指令

        Returns:
            重排序后的结果列表，只包含 id 和 score
        """
        if not documents:
            return []

        # 默认指令
        if instruct is None:
            instruct = "Given a web search query, retrieve relevant passages that answer the query."

        try:
            resp = dashscope.TextReRank.call(
                model=self.model,
                query=query,
                documents=documents,
                top_n=min(top_n, len(documents)),
                return_documents=False,
                instruct=instruct
            )

            if resp.status_code == HTTPStatus.OK:
                results = []
                output = resp.output

                if hasattr(output, 'results') and output.results:
                    for item in output.results:
                        results.append({
                            'id': item.index,
                            'score': item.relevance_score
                        })
                return results
            else:
                print(f"❌ Rerank 失败: {resp.message}")
                return []

        except Exception as e:
            print(f"❌ Rerank 调用异常: {e}")
            return []


# 创建全局实例
reranker = Reranker()

