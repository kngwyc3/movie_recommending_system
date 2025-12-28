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
query = "推荐动作片"

# 获取检索和重排序详情
details = rag_chain.get_retrieval_details(query)

# ============== 打印检索和重排序结果 ==============
print("\n" + "="*80)
print("🔍 检索和重排序结果：")
print("="*80 + "\n")
if details:
    # 打印第一个 BM25 检索结果
    if details.get('bm25_retrieval') and len(details['bm25_retrieval']) > 0:
        print("【第一个 BM25 检索结果】")
        print(json.dumps(details['bm25_retrieval'][0], indent=2, ensure_ascii=False))
    
    # 打印第一个向量检索结果
    if details.get('vector_retrieval') and len(details['vector_retrieval']) > 0:
        print("\n【第一个向量检索结果】")
        print(json.dumps(details['vector_retrieval'][0], indent=2, ensure_ascii=False))
    
    # 打印所有重排序结果
    if details.get('reranked_results'):
        print("\n【所有重排序结果】")
        print(json.dumps(details['reranked_results'], indent=2, ensure_ascii=False))
else:
    print("❌ 无法获取检索详情")

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
    print("💾 最终结果:")
    print("="*80 + "\n")

    # 使用新的API获取完整响应
    full_response = rag_chain.get_full_response(query)
    full_json = full_response.to_json()
    print(full_json)
else:
    print("❌ 流式响应失败")


