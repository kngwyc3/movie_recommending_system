#!/usr/bin/env python3
"""
使用LLM为电影生成描述的脚本
从MovieLens数据集中读取电影信息，并使用LLM为每部电影生成描述
"""

import os
import json
import time
import sys
from typing import List, Dict, Any

# 清除可能导致冲突的环境变量
for key in list(os.environ.keys()):
    if 'PROXY' in key.upper() or key.startswith('HTTP_'):
        os.environ.pop(key, None)

from openai import OpenAI

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from datasets.processdata.data import load_movies, load_ratings, calculate_avg_ratings
from src.config import Config

class MovieDescriptionGenerator:
    def __init__(self):
        """初始化描述生成器"""
        self.api_key = os.getenv("DASHSCOPE_API_KEY")
        self.base_url = "https://dashscope.aliyuncs.com/compatible-mode/v1"
        self.model = os.getenv("QWEN_MODEL", "qwen-max")
        
        # 初始化OpenAI客户端
        self.client = OpenAI(
            api_key=self.api_key,
            base_url=self.base_url
        )
        
        # 验证API密钥
        if not self.api_key:
            raise ValueError("未设置DASHSCOPE_API_KEY环境变量")
    
    def _call_llm_api(self, prompt: str) -> str:
        """
        调用LLM API生成文本
        
        Args:
            prompt: 提示词
            
        Returns:
            生成的文本描述
        """
        try:
            completion = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=1000
            )
            return completion.choices[0].message.content
                
        except Exception as e:
            print(f"调用LLM API出错: {e}")
            return f"无法生成描述，错误信息: {str(e)}"
    
    def _create_prompt(self, movie_title: str, movie_genres: List[str], year: str = None) -> str:
        """
        创建电影描述生成的提示词
        
        Args:
            movie_title: 电影标题
            movie_genres: 电影类型列表
            year: 电影年份（可选）
            
        Returns:
            格式化的提示词
        """
        year_info = f"于{year}年" if year else ""
        genres_str = "、".join(movie_genres) if movie_genres else "未知"
        
        prompt = f"""
请为以下电影生成一段简洁、吸引人的描述，长度在50-100字之间：

电影名称：{movie_title}
上映年份：{year_info}
电影类型：{genres_str}

要求：
1. 描述应包括电影的主题、故事梗概和风格特点
2. 描述应吸引观众，但避免剧透关键情节
3. 语言应简洁明了，适合用作电影推荐
4. 如果这部电影是知名电影，可以使用一些公众熟知的信息

请直接返回描述内容，不需要额外的解释或格式。
"""
        return prompt
    
    def generate_descriptions(self, movies: Dict[str, Any]) -> Dict[str, str]:
        """
        为所有电影生成描述
        
        Args:
            movies: 电影信息字典
            
        Returns:
            电影ID到描述的映射
        """
        descriptions = {}
        total = len(movies)
        batch = []
        
        print(f"开始为{total}部电影生成描述...")
        
        for i, (movie_id, movie_info) in enumerate(movies.items(), 1):
            # 提取年份
            year = None
            title = movie_info['title']
            if '(' in title and ')' in title:
                try:
                    year = title.split('(')[-1].split(')')[0]
                except:
                    pass
            
            # 创建提示词
            prompt = self._create_prompt(title, movie_info['genres'], year)
            
            # 生成描述
            print(f"处理进度: {i}/{total} - 正在生成《{title}》的描述...")
            description = self._call_llm_api(prompt)
            descriptions[movie_id] = description
            batch.append((title, description))
            
            # 每10部打印一次结果
            if i % 10 == 0:
                print(f"\n{'='*60}")
                print(f"已处理{i}/{total}部电影 - 前10部描述结果:")
                print(f"{'='*60}")
                for idx, (t, desc) in enumerate(batch, 1):
                    print(f"\n{idx}. 《{t}》")
                    print(f"   描述: {desc}")
                print(f"{'='*60}\n")
                batch = []
                time.sleep(2)
            else:
                time.sleep(0.5)  # 每次请求间隔0.5秒
        
        # 打印剩余的
        if batch:
            print(f"\n{'='*60}")
            print(f"最后{len(batch)}部描述结果:")
            print(f"{'='*60}")
            for idx, (t, desc) in enumerate(batch, 1):
                print(f"\n{idx}. 《{t}》")
                print(f"   描述: {desc}")
            print(f"{'='*60}\n")
        
        print("所有电影描述生成完成!")
        return descriptions
    
    def save_descriptions(self, descriptions: Dict[str, str], output_path: str):
        """
        保存电影描述到文件
        
        Args:
            descriptions: 电影描述字典
            output_path: 输出文件路径
        """
        output_dir = os.path.dirname(output_path)
        os.makedirs(output_dir, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(descriptions, f, ensure_ascii=False, indent=2)
        
        print(f"电影描述已保存到: {output_path}")
    
    def update_chroma_data(self, descriptions: Dict[str, str], chroma_data_path: str, output_path: str):
        """
        更新ChromaDB数据中的电影描述
        
        Args:
            descriptions: 电影描述字典
            chroma_data_path: ChromaDB数据文件路径
            output_path: 更新后的输出文件路径
        """
        # 读取现有ChromaDB数据
        with open(chroma_data_path, 'r', encoding='utf-8') as f:
            chroma_data = json.load(f)
        
        # 更新documents字段
        updated_count = 0
        for i, movie_id in enumerate(chroma_data['ids']):
            if movie_id in descriptions:
                chroma_data['documents'][i] = descriptions[movie_id]
                updated_count += 1
        
        # 保存更新后的数据
        output_dir = os.path.dirname(output_path)
        os.makedirs(output_dir, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(chroma_data, f, ensure_ascii=False, indent=2)
        
        print(f"已更新{updated_count}部电影描述，数据已保存到: {output_path}")


def main():
    """主函数"""
    # 配置路径
    data_path = r'D:\code\vue\movie_ai\datasets\ml-100k'
    chroma_data_path = r'D:\code\vue\movie_ai\datasets\chroma_movies.json'
    descriptions_path = r'D:\code\vue\movie_ai\datasets\movie_descriptions.json'
    updated_chroma_path = r'D:\code\vue\movie_ai\datasets\chroma_movies_with_descriptions.json'
    
    # 初始化描述生成器
    generator = MovieDescriptionGenerator()
    
    # 加载电影数据
    print("加载电影数据...")
    movies = load_movies(data_path)
    ratings = load_ratings(data_path)
    calculate_avg_ratings(movies, ratings)
    
    print(f"已加载{len(movies)}部电影信息")
    
    # 生成电影描述
    descriptions = generator.generate_descriptions(movies)
    
    # 保存描述
    generator.save_descriptions(descriptions, descriptions_path)
    
    # 更新ChromaDB数据
    generator.update_chroma_data(descriptions, chroma_data_path, updated_chroma_path)
    
    print("任务完成!")


if __name__ == "__main__":
    main()
