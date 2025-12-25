"""
RAG 测试 Demo - 流式输出大模型推荐结果
"""
import sys
import os

# 添加 movie_ai 目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.rag import rag_chain

# 用户输入
query = input("请输入电影推荐问题: ")

# 执行 RAG 流式查询并实时输出
print("\n🎬 推荐结果：\n")
stream_response = rag_chain.query_stream(query)

if stream_response:
    for chunk in stream_response:
        if chunk.choices and len(chunk.choices) > 0:
            content = chunk.choices[0].delta.content
            if content:
                print(content, end='', flush=True)
    print()
else:
    print("❌ 流式响应失败")
