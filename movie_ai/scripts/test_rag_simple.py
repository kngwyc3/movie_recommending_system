"""
RAG 测试 Demo - 展示重排序结果和LLM生成结果
"""
import sys
import os
import json

# 添加 movie_ai 目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.rag import rag_chain

# 用户输入
query = "莱士与格罗米特系列的开山之作，这部短片讲述他们意外踏上探索月球的旅程"

# 获取检索和重排序详情
details = rag_chain.get_retrieval_details(query)

# ============== 执行 RAG 流式查询并实时输出 ==============
print("\n" + "="*80)
print("🎬 大模型推荐结果：")
print("="*80 + "\n")
stream_response = rag_chain.query_stream(query)

if stream_response:
    llm_content = ""
    for chunk in stream_response:
        if chunk.choices and len(chunk.choices) > 0:
            content = chunk.choices[0].delta.content
            if content:
                print(content, end='', flush=True)
                llm_content += content
    print("\n" + "="*80)

    # ============== 完整RAG JSON响应 ==============
    print("\n" + "="*80)
    print("💾 完整JSON响应:")
    print("="*80 + "\n")

    # 使用新的API获取完整响应
    full_response = rag_chain.get_full_response(query)
    full_json = full_response.to_json()
    print(full_json)
else:
    print("❌ 流式响应失败")


