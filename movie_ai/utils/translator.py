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
    
    def extract_movie_keywords(self, query: str) -> str:
        """
        从用户查询中提取电影相关关键词（电影类型、名称等）
        用于精确的 BM25 查询
        
        Args:
            query: 用户查询（中文）
        
        Returns:
            提取出的关键词，用空格隔开
        """
        if not query or not query.strip():
            return query
        
        prompt = """从以下用户查询中提取电影相关的关键词（如电影类型、电影名称等）。

重要提示：
1. 只返回提取出的关键词，用空格隔开，不要返回其他文字
2. 如果有中文关键词，要翻译成英文
3. **电影类型映射表（必须遵守）**：
   - 爱情片/浪漫片 -> Romance
   - 科幻片 -> Sci-Fi
   - 动作片 -> Action
   - 喜剧片 -> Comedy
   - 恐怖片 -> Horror
   - 惊悚片 -> Thriller
   - 剧情片 -> Drama
   - 动画片 -> Animation
   - 冒险片 -> Adventure
   - 犯罪片 -> Crime
   - 战争片 -> War
   - 奇幻片 -> Fantasy
   - 音乐片 -> Musical
   - 悬疑片 -> Mystery
   - 西部片 -> Western
   - 儿童片 -> Children's
   - 纪录片 -> Documentary
   - 黑色电影 -> Film-Noir
4. 如果无法提取，返回原查询的关键部分

用户查询：{}

关键词：""".format(query)
        
        try:
            completion = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,
                max_tokens=100
            )
            keywords = completion.choices[0].message.content.strip()
            return keywords if keywords else query
        
        except Exception as e:
            print(f"⚠️  关键词提取失败: {e}")
            # 失败时降级为翻译
            return self.translate_to_english(query)


# 创建全局实例
def get_translator() -> QwenTranslator:
    """
    获取翻译器实例

    Returns:
        QwenTranslator实例
    """
    return QwenTranslator()


# 便揋函数
def translate_to_english(text: str) -> str:
    """
    将中文翻译成英文（便揋函数）

    Args:
        text: 中文文本

    Returns:
        英文翻译，失败返回原文本
    """
    translator = get_translator()
    return translator.translate_to_english(text)


def extract_movie_keywords(query: str) -> str:
    """
    从查询中提取电影相关关键词（便揋函数）
    
    Args:
        query: 用户查询
    
    Returns:
        提取出的关键词
    """
    translator = get_translator()
    return translator.extract_movie_keywords(query)
