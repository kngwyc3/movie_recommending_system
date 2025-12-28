"""
Movie AI Flask API Service
提供 RAG 电影推荐接口
"""
import sys
import os

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from flask import Flask, jsonify, request, Response, stream_with_context
from flask_cors import CORS
from src.config import Config
from src.rag import rag_chain
from src.retriever import retriever
from src.rerank import reranker
import json
from datetime import datetime

app = Flask(__name__)

# 配置 CORS
CORS(app, resources={
    r"/ai/*": {
        "origins": ["http://localhost:5173", "http://localhost:5174", "http://localhost:3000", "http://localhost:5000"],
        "methods": ["GET", "POST"],
        "allow_headers": ["Content-Type"]
    }
})

# 配置
app.config['JSON_AS_ASCII'] = False
app.config['JSONIFY_MIMETYPE'] = "application/json;charset=utf-8"


@app.route('/ai/health', methods=['GET'])
def health_check():
    """健康检查接口"""
    return jsonify({
        'success': True,
        'message': 'Movie AI Service is running!',
        'service': Config.FLASK_APP_NAME,
        'version': '1.0.0'
    }), 200


@app.route('/ai/recommend', methods=['POST'])
def recommend_movies():
    """
    电影推荐接口（完整响应）
    
    请求体:
    {
        "query": "我想看科幻电影",
        "top_k": 5,  // 可选，检索数量
        "rerank_top_n": 3  // 可选，重排序后返回数量
    }
    
    响应:
    {
        "success": true,
        "data": {
            "query": "...",
            "rerank": {...},
            "recommended_movie_ids": [...],
            "llm_content": "...",
            "timestamp": "...",
            "status": "success"
        }
    }
    """
    try:
        data = request.get_json()
        
        if not data or 'query' not in data:
            return jsonify({
                'success': False,
                'message': '请提供查询内容 (query)'
            }), 400
        
        query = data['query'].strip()
        if not query:
            return jsonify({
                'success': False,
                'message': '查询内容不能为空'
            }), 400
        
        # 获取可选参数
        top_k = data.get('top_k')
        rerank_top_n = data.get('rerank_top_n')
        
        # 创建 RAG 实例（如果提供了参数）
        if top_k or rerank_top_n:
            from src.rag import RAGChain
            chain = RAGChain(top_k=top_k, rerank_top_n=rerank_top_n)
            response = chain.get_full_response(query)
        else:
            response = rag_chain.get_full_response(query)
        
        return jsonify({
            'success': True,
            'data': json.loads(response.to_json())
        }), 200
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'message': f'推荐失败: {str(e)}'
        }), 500


@app.route('/ai/recommend/stream', methods=['POST'])
def recommend_movies_stream():
    """
    电影推荐接口（流式响应）
    
    请求体:
    {
        "query": "我想看科幻电影",
        "top_k": 5,
        "rerank_top_n": 3
    }
    
    响应: Server-Sent Events (SSE) 流
    """
    try:
        data = request.get_json()
        
        if not data or 'query' not in data:
            return jsonify({
                'success': False,
                'message': '请提供查询内容 (query)'
            }), 400
        
        query = data['query'].strip()
        if not query:
            return jsonify({
                'success': False,
                'message': '查询内容不能为空'
            }), 400
        
        top_k = data.get('top_k')
        rerank_top_n = data.get('rerank_top_n')
        
        def generate():
            """生成流式响应"""
            try:
                # 1. 先执行检索和重排序
                from src.rag import RAGChain
                if top_k or rerank_top_n:
                    chain = RAGChain(top_k=top_k, rerank_top_n=rerank_top_n)
                else:
                    chain = rag_chain
                
                # 获取检索结果
                search_results = retriever.hybrid_search(query, top_k=chain.top_k, separate=True)
                vector_results = search_results['vector_results']
                bm25_results = search_results['bm25_results']
                combined_results = search_results['combined_results']
                
                # 重排序
                rerank_results = []
                if combined_results:
                    doc_texts = [doc['document'] for doc in combined_results]
                    rerank_results = reranker.rerank(query=query, documents=doc_texts, top_n=chain.rerank_top_n)
                
                # 发送检索结果
                retrieval_data = {
                    'type': 'retrieval',
                    'data': {
                        'rerank_results': rerank_results,
                        'recommended_movie_ids': [item['metadata']['movie_id'] for item in 
                                                 [combined_results[r['id']] for r in rerank_results]]
                    }
                }
                yield f"data: {json.dumps(retrieval_data, ensure_ascii=False)}\n\n"
                
                # 2. 流式生成 LLM 内容
                context = chain._get_context(combined_results, rerank_results)
                messages = chain._build_messages(context, query)
                
                llm_content = ""
                for chunk in chain.llm.stream(messages):
                    if chunk.choices and len(chunk.choices) > 0:
                        content = chunk.choices[0].delta.content
                        if content:
                            llm_content += content
                            chunk_data = {
                                'type': 'llm_chunk',
                                'data': {'content': content}
                            }
                            yield f"data: {json.dumps(chunk_data, ensure_ascii=False)}\n\n"
                
                # 3. 发送完成信号
                complete_data = {
                    'type': 'complete',
                    'data': {
                        'query': query,
                        'llm_content': llm_content,
                        'timestamp': datetime.now().isoformat()
                    }
                }
                yield f"data: {json.dumps(complete_data, ensure_ascii=False)}\n\n"
                
            except Exception as e:
                error_data = {
                    'type': 'error',
                    'data': {'message': str(e)}
                }
                yield f"data: {json.dumps(error_data, ensure_ascii=False)}\n\n"
        
        return Response(
            stream_with_context(generate()),
            mimetype='text/event-stream',
            headers={
                'Cache-Control': 'no-cache',
                'X-Accel-Buffering': 'no'
            }
        )
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'message': f'推荐失败: {str(e)}'
        }), 500


@app.route('/ai/search/vector', methods=['POST'])
def vector_search():
    """
    向量检索接口
    
    请求体:
    {
        "query": "科幻电影",
        "top_k": 5
    }
    """
    try:
        data = request.get_json()
        
        if not data or 'query' not in data:
            return jsonify({
                'success': False,
                'message': '请提供查询内容 (query)'
            }), 400
        
        query = data['query'].strip()
        top_k = data.get('top_k', 5)
        
        results = retriever.vector_search(query, top_k)
        
        return jsonify({
            'success': True,
            'data': {
                'query': query,
                'method': 'vector',
                'results': results,
                'count': len(results)
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'向量检索失败: {str(e)}'
        }), 500


@app.route('/ai/search/bm25', methods=['POST'])
def bm25_search():
    """
    BM25 检索接口
    
    请求体:
    {
        "query": "科幻电影",
        "top_k": 5
    }
    """
    try:
        data = request.get_json()
        
        if not data or 'query' not in data:
            return jsonify({
                'success': False,
                'message': '请提供查询内容 (query)'
            }), 400
        
        query = data['query'].strip()
        top_k = data.get('top_k', 5)
        
        results = retriever.bm25_search(query, top_k)
        
        return jsonify({
            'success': True,
            'data': {
                'query': query,
                'method': 'bm25',
                'results': results,
                'count': len(results)
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'BM25检索失败: {str(e)}'
        }), 500


@app.route('/ai/search/hybrid', methods=['POST'])
def hybrid_search():
    """
    混合检索接口
    
    请求体:
    {
        "query": "科幻电影",
        "top_k": 5,
        "alpha": 0.5,  // 可选，向量检索权重
        "separate": false  // 可选，是否分别返回向量和BM25结果
    }
    """
    try:
        data = request.get_json()
        
        if not data or 'query' not in data:
            return jsonify({
                'success': False,
                'message': '请提供查询内容 (query)'
            }), 400
        
        query = data['query'].strip()
        top_k = data.get('top_k', 5)
        alpha = data.get('alpha', 0.5)
        separate = data.get('separate', False)
        
        results = retriever.hybrid_search(query, top_k, alpha, separate)
        
        if separate:
            return jsonify({
                'success': True,
                'data': {
                    'query': query,
                    'method': 'hybrid',
                    'vector_results': results['vector_results'],
                    'bm25_results': results['bm25_results'],
                    'combined_results': results['combined_results'],
                    'vector_count': len(results['vector_results']),
                    'bm25_count': len(results['bm25_results']),
                    'combined_count': len(results['combined_results'])
                }
            }), 200
        else:
            return jsonify({
                'success': True,
                'data': {
                    'query': query,
                    'method': 'hybrid',
                    'results': results,
                    'count': len(results)
                }
            }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'混合检索失败: {str(e)}'
        }), 500


@app.route('/ai/rerank', methods=['POST'])
def rerank_documents():
    """
    重排序接口
    
    请求体:
    {
        "query": "科幻电影",
        "documents": ["文档1", "文档2", ...],
        "top_n": 3
    }
    """
    try:
        data = request.get_json()
        
        if not data or 'query' not in data or 'documents' not in data:
            return jsonify({
                'success': False,
                'message': '请提供查询内容 (query) 和文档列表 (documents)'
            }), 400
        
        query = data['query'].strip()
        documents = data['documents']
        top_n = data.get('top_n', len(documents))
        
        if not isinstance(documents, list) or len(documents) == 0:
            return jsonify({
                'success': False,
                'message': '文档列表不能为空'
            }), 400
        
        # 调用重排序
        rerank_results = reranker.rerank(query, documents, top_n)
        
        # 补充文档内容
        results_with_docs = []
        for item in rerank_results:
            results_with_docs.append({
                'id': item['id'],
                'score': item['score'],
                'document': documents[item['id']]
            })
        
        return jsonify({
            'success': True,
            'data': {
                'query': query,
                'results': results_with_docs,
                'count': len(results_with_docs)
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'重排序失败: {str(e)}'
        }), 500


@app.errorhandler(404)
def not_found(error):
    """404 错误处理"""
    return jsonify({
        'success': False,
        'message': '请求的资源不存在'
    }), 404


@app.errorhandler(500)
def internal_error(error):
    """500 错误处理"""
    return jsonify({
        'success': False,
        'message': '服务器内部错误'
    }), 500


if __name__ == '__main__':
    # 验证配置
    try:
        Config.validate()
    except ValueError as e:
        print(f"❌ 配置错误: {e}")
        sys.exit(1)
    
    # 预加载 BM25 索引
    print("🔄 预加载 BM25 索引...")
    retriever.preload_bm25()
    print("✅ BM25 索引加载完成")
    
    # 启动服务
    print(f"\n{'='*60}")
    print(f"🚀 {Config.FLASK_APP_NAME} 启动中...")
    print(f"{'='*60}")
    print(f"📍 地址: http://{Config.FLASK_HOST}:{Config.FLASK_PORT}")
    print(f"🏥 健康检查: http://localhost:{Config.FLASK_PORT}/ai/health")
    print(f"🎬 电影推荐: POST http://localhost:{Config.FLASK_PORT}/ai/recommend")
    print(f"🌊 流式推荐: POST http://localhost:{Config.FLASK_PORT}/ai/recommend/stream")
    print(f"🔍 向量检索: POST http://localhost:{Config.FLASK_PORT}/ai/search/vector")
    print(f"📝 BM25检索: POST http://localhost:{Config.FLASK_PORT}/ai/search/bm25")
    print(f"🔀 混合检索: POST http://localhost:{Config.FLASK_PORT}/ai/search/hybrid")
    print(f"🎯 重排序: POST http://localhost:{Config.FLASK_PORT}/ai/rerank")
    print(f"{'='*60}\n")
    
    app.run(
        host=Config.FLASK_HOST,
        port=Config.FLASK_PORT,
        debug=Config.FLASK_DEBUG
    )
