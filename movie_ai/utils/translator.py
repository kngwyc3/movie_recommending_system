"""
Qwen Max 翻译工具
"""
from typing import Optional
from src.config import Config


class QwenTranslator:
    """Qwen Max 翻译器封装"""

    def __init__(self):
        """初始化翻译器"""
        from openai import OpenAI

        self.client = OpenAI(
            api_key=Config.QWEN_API_KEY,
            base_url=Config.QWEN_API_URL
        )
        self.model = Config.QWEN_MODEL

    def translate(self, text: str, from_lang: str = 'zh', to_lang: str = 'en') -> Optional[str]:
        """
        翻译文本

        Args:
            text: 待翻译文本
            from_lang: 源语言 (zh=中文, en=英文)
            to_lang: 目标语言 (zh=中文, en=英文)

        Returns:
            翻译结果，失败返回None
        """
        if not text or not text.strip():
            return text

        lang_names = {
            'zh': '中文',
            'en': '英文'
        }

        from_name = lang_names.get(from_lang, from_lang)
        to_name = lang_names.get(to_lang, to_lang)

        prompt = f"请将以下{from_name}文本翻译成{to_name}，只返回翻译结果，不要添加任何额外说明：\n\n{text}"

        try:
            completion = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=500
            )
            return completion.choices[0].message.content.strip()

        except Exception as e:
            print(f"❌ Qwen翻译失败: {e}")
            return None

    def translate_to_english(self, text: str) -> str:
        """
        将中文翻译成英文

        Args:
            text: 中文文本

        Returns:
            英文翻译，失败返回原文本
        """
        result = self.translate(text, from_lang='zh', to_lang='en')
        return result if result else text


# 创建全局实例
def get_translator() -> QwenTranslator:
    """
    获取翻译器实例

    Returns:
        QwenTranslator实例
    """
    return QwenTranslator()


# 便捷函数
def translate_to_english(text: str) -> str:
    """
    将中文翻译成英文（便捷函数）

    Args:
        text: 中文文本

    Returns:
        英文翻译，失败返回原文本
    """
    translator = get_translator()
    return translator.translate_to_english(text)
