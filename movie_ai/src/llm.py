"""
LLM 模块 - 通用的 LLM 包装器
"""
from typing import List, Dict, Iterator
from openai import OpenAI
from src.config import Config


class QwenLLM:
    """LLM 包装器 - 支持 Qwen 模型"""
    
    def __init__(self):
        self.client = OpenAI(
            api_key=Config.QWEN_API_KEY,
            base_url=Config.QWEN_API_URL
        )
        self.model = Config.QWEN_MODEL
    
    def invoke(self, messages: List[Dict[str, str]]) -> str:
        """调用 LLM 生成回复"""
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=Config.QWEN_TEMPERATURE,
            max_tokens=Config.QWEN_MAX_TOKENS
        )
        return response.choices[0].message.content
    
    def stream(self, messages: List[Dict[str, str]]) -> Iterator:
        """流式调用 LLM 生成回复"""
        return self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=Config.QWEN_TEMPERATURE,
            max_tokens=Config.QWEN_MAX_TOKENS,
            stream=True
        )
