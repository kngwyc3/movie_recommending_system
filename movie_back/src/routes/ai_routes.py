"""
AI 路由 - 提供 AI 相关接口
"""
from flask import request
from src.viewmodels.ai_viewmodel import ai_viewmodel
from src.utils.helpers import success_response, error_response, bad_request_response


def register_routes(app):
    """注册所有 AI 路由"""

    @app.route('/api/ai/recommend', methods=['POST'])
    def recommend():
        """
        电影推荐接口（完整响应）
        基于 RAG 的智能推荐
        """
        try:
            data = request.get_json()

            # 参数校验
            if not data:
                return bad_request_response('请提供请求参数')

            query = data.get('query', '').strip()
            top_k = data.get('top_k', 5)
            rerank_top_n = data.get('rerank_top_n', 3)

            if not query:
                return bad_request_response('查询文本不能为空')

            if not isinstance(top_k, int) or top_k < 1 or top_k > 20:
                return bad_request_response('top_k 参数必须是 1-20 之间的整数')

            if not isinstance(rerank_top_n, int) or rerank_top_n < 1 or rerank_top_n > 10:
                return bad_request_response('rerank_top_n 参数必须是 1-10 之间的整数')

            # 调用 AI 服务
            response = ai_viewmodel.ai_service.recommend(
                query=query,
                top_k=top_k,
                rerank_top_n=rerank_top_n
            )

            return success_response(response, message='推荐成功')

        except Exception as e:
            return error_response(f'推荐失败: {str(e)}')

    @app.route('/api/ai/recommend/stream', methods=['POST'])
    def recommend_stream():
        """
        电影推荐接口（流式响应）
        实时返回推荐结果
        """
        from flask import Response, stream_with_context
        import json

        try:
            data = request.get_json()

            # 参数校验
            if not data:
                return bad_request_response('请提供请求参数')

            query = data.get('query', '').strip()
            top_k = data.get('top_k', 5)
            rerank_top_n = data.get('rerank_top_n', 3)

            if not query:
                return bad_request_response('查询文本不能为空')

            def generate():
                """生成流式响应"""
                try:
                    for event in ai_viewmodel.ai_service.recommend_stream(
                        query=query,
                        top_k=top_k,
                        rerank_top_n=rerank_top_n
                    ):
                        yield f"data: {json.dumps(event, ensure_ascii=False)}\n\n"
                except Exception as e:
                    error_event = {
                        'type': 'error',
                        'data': {'message': str(e)}
                    }
                    yield f"data: {json.dumps(error_event, ensure_ascii=False)}\n\n"

            return Response(
                stream_with_context(generate()),
                mimetype='text/event-stream',
                headers={
                    'Cache-Control': 'no-cache',
                    'X-Accel-Buffering': 'no'
                }
            )

        except Exception as e:
            return error_response(f'流式推荐失败: {str(e)}')

    @app.route('/api/ai/search', methods=['POST'])
    def search():
        """
        混合检索接口
        支持向量检索、BM25 检索和混合检索
        """
        try:
            data = request.get_json()

            # 参数校验
            if not data:
                return bad_request_response('请提供请求参数')

            query = data.get('query', '').strip()
            mode = data.get('mode', 'hybrid')
            rerank = data.get('rerank', False)
            top_k = data.get('top_k', 5)

            if not query:
                return bad_request_response('查询文本不能为空')

            if mode not in ['hybrid', 'vector', 'bm25']:
                return bad_request_response('不支持的检索模式，可选值: hybrid, vector, bm25')

            if not isinstance(top_k, int) or top_k < 1 or top_k > 20:
                return bad_request_response('top_k 参数必须是 1-20 之间的整数')

            # 执行检索
            results = ai_viewmodel.search(
                query=query,
                mode=mode,
                top_k=top_k,
                rerank=rerank
            )

            # 格式化返回结果
            formatted_results = []
            for result in results:
                formatted_results.append({
                    'id': result['id'],
                    'title': result['metadata'].get('title', 'Unknown'),
                    'content': result['document'],
                    'genres': result['metadata'].get('genres', []),
                    'score': result.get('score', 0.0),
                    'rerank_score': result.get('rerank_score', None),
                    'method': result.get('method', 'unknown')
                })

            return success_response(
                formatted_results,
                message=f'检索成功，共找到 {len(formatted_results)} 条结果'
            )

        except Exception as e:
            return error_response(f'检索失败: {str(e)}')

    @app.route('/api/ai/vector-search', methods=['POST'])
    def vector_search():
        """
        向量检索接口
        基于语义相似度的文档检索
        """
        try:
            data = request.get_json()

            # 参数校验
            if not data:
                return bad_request_response('请提供请求参数')

            query = data.get('query', '').strip()
            rerank = data.get('rerank', False)
            top_k = data.get('top_k', 5)

            if not query:
                return bad_request_response('查询文本不能为空')

            if not isinstance(top_k, int) or top_k < 1 or top_k > 20:
                return bad_request_response('top_k 参数必须是 1-20 之间的整数')

            # 执行向量检索
            results = ai_viewmodel.search(
                query=query,
                mode='vector',
                top_k=top_k,
                rerank=rerank
            )

            # 格式化返回结果
            formatted_results = []
            for result in results:
                formatted_results.append({
                    'id': result['id'],
                    'title': result['metadata'].get('title', 'Unknown'),
                    'content': result['document'],
                    'genres': result['metadata'].get('genres', []),
                    'score': result.get('score', 0.0),
                    'rerank_score': result.get('rerank_score', None),
                    'method': 'vector'
                })

            return success_response(
                formatted_results,
                message=f'向量检索成功，共找到 {len(formatted_results)} 条结果'
            )

        except Exception as e:
            return error_response(f'向量检索失败: {str(e)}')

    @app.route('/api/ai/bm25-search', methods=['POST'])
    def bm25_search():
        """
        BM25 检索接口
        基于关键词匹配的文档检索
        """
        try:
            data = request.get_json()

            # 参数校验
            if not data:
                return bad_request_response('请提供请求参数')

            query = data.get('query', '').strip()
            rerank = data.get('rerank', False)
            top_k = data.get('top_k', 5)

            if not query:
                return bad_request_response('查询文本不能为空')

            if not isinstance(top_k, int) or top_k < 1 or top_k > 20:
                return bad_request_response('top_k 参数必须是 1-20 之间的整数')

            # 执行 BM25 检索
            results = ai_viewmodel.search(
                query=query,
                mode='bm25',
                top_k=top_k,
                rerank=rerank
            )

            # 格式化返回结果
            formatted_results = []
            for result in results:
                formatted_results.append({
                    'id': result['id'],
                    'title': result['metadata'].get('title', 'Unknown'),
                    'content': result['document'],
                    'genres': result['metadata'].get('genres', []),
                    'score': result.get('score', 0.0),
                    'rerank_score': result.get('rerank_score', None),
                    'method': 'bm25'
                })

            return success_response(
                formatted_results,
                message=f'BM25检索成功，共找到 {len(formatted_results)} 条结果'
            )

        except Exception as e:
            return error_response(f'BM25检索失败: {str(e)}')

    @app.route('/api/ai/chat', methods=['POST'])
    def chat():
        """
        智能问答接口
        基于检索结果生成自然语言回答
        """
        try:
            data = request.get_json()

            # 参数校验
            if not data:
                return bad_request_response('请提供请求参数')

            query = data.get('query', '').strip()
            top_k = data.get('top_k', 5)

            if not query:
                return bad_request_response('问题内容不能为空')

            if not isinstance(top_k, int) or top_k < 1 or top_k > 20:
                return bad_request_response('top_k 参数必须是 1-20 之间的整数')

            # 执行智能问答
            response = ai_viewmodel.chat(query=query, top_k=top_k)

            # 格式化返回结果
            return success_response({
                'query': response['query'],
                'answer': response['answer'],
                'retrieval': {
                    'vector_count': len(response['retrieval']['vector_results']),
                    'bm25_count': len(response['retrieval']['bm25_results']),
                    'rerank_count': len(response['retrieval']['rerank_results'])
                }
            }, message='智能问答成功')

        except Exception as e:
            return error_response(f'智能问答失败: {str(e)}')

    @app.route('/api/ai/rerank', methods=['POST'])
    def rerank():
        """
        重排序接口
        对检索结果进行精细化重排序
        """
        try:
            data = request.get_json()

            # 参数校验
            if not data:
                return bad_request_response('请提供请求参数')

            query = data.get('query', '').strip()
            documents = data.get('documents', [])
            top_n = data.get('top_n', 5)

            if not query:
                return bad_request_response('查询文本不能为空')

            if not isinstance(documents, list) or len(documents) == 0:
                return bad_request_response('documents 必须是非空列表')

            if not isinstance(top_n, int) or top_n < 1 or top_n > 20:
                return bad_request_response('top_n 参数必须是 1-20 之间的整数')

            # 执行重排序
            results = ai_viewmodel.rerank(
                query=query,
                documents=documents,
                top_n=top_n
            )

            # 格式化返回结果
            formatted_results = []
            for result in results:
                formatted_results.append({
                    'id': result['id'],
                    'document': documents[result['id']],
                    'score': result['score']
                })

            return success_response(
                formatted_results,
                message=f'重排序成功，共返回 {len(formatted_results)} 条结果'
            )

        except Exception as e:
            return error_response(f'重排序失败: {str(e)}')

    @app.route('/api/ai/retrieval-details', methods=['POST'])
    def retrieval_details():
        """
        获取检索详细信息接口
        返回向量检索、BM25检索、重排序等所有中间结果
        """
        try:
            data = request.get_json()

            # 参数校验
            if not data:
                return bad_request_response('请提供请求参数')

            query = data.get('query', '').strip()

            if not query:
                return bad_request_response('查询文本不能为空')

            # 获取检索详情
            details = ai_viewmodel.get_retrieval_details(query)

            return success_response({
                'vector_retrieval': details.get('vector_retrieval', []),
                'bm25_retrieval': details.get('bm25_retrieval', []),
                'retrieval': details.get('retrieval', []),
                'rerank': details.get('rerank', []),
                'final': details.get('final', []),
                'recommended_movie_ids': details.get('recommended_movie_ids', [])
            }, message='获取检索详情成功')

        except Exception as e:
            return error_response(f'获取检索详情失败: {str(e)}')
