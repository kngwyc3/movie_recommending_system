"""
AI对话相关路由
"""
from flask import request, jsonify
from src.viewmodels.chat_viewmodel import chat_viewmodel
from src.utils.helpers import success_response, error_response, bad_request_response


def register_routes(app):
    """注册所有AI对话路由"""

    @app.route('/api/chat/save', methods=['POST'])
    def save_chat():
        """保存对话记录"""
        try:
            data = request.get_json()
            
            if not data or 'user_id' not in data or 'question' not in data or 'answer' not in data:
                return bad_request_response('缺少必要参数: user_id, question, answer')
            
            user_id = data['user_id']
            question = data['question']
            answer = data['answer']
            related_movies = data.get('related_movies', [])
            
            print(f'💬 保存对话: user_id={user_id}, question={question[:50]}...')
            
            chat = chat_viewmodel.save_chat(user_id, question, answer, related_movies)
            
            if not chat:
                return error_response('保存对话失败')
            
            return success_response(chat, message='对话已保存')
        except Exception as e:
            print(f'❌ 保存对话异常: {str(e)}')
            return error_response(f'保存对话失败: {str(e)}')

    @app.route('/api/chat/history/<int:user_id>', methods=['GET'])
    def get_chat_history(user_id):
        """获取用户的对话历史"""
        try:
            page = request.args.get('page', 1, type=int)
            per_page = request.args.get('per_page', 20, type=int)
            
            print(f'📜 获取对话历史: user_id={user_id}, page={page}, per_page={per_page}')
            
            result = chat_viewmodel.get_chat_history(user_id, page, per_page)
            return success_response(result)
        except Exception as e:
            print(f'❌ 获取对话历史异常: {str(e)}')
            return error_response(f'获取对话历史失败: {str(e)}')

    @app.route('/api/chat/<int:chat_id>', methods=['GET'])
    def get_chat(chat_id):
        """获取单条对话"""
        try:
            print(f'💬 获取对话: chat_id={chat_id}')
            
            chat = chat_viewmodel.get_chat_by_id(chat_id)
            
            if not chat:
                return bad_request_response('对话不存在', status_code=404)
            
            return success_response(chat)
        except Exception as e:
            print(f'❌ 获取对话异常: {str(e)}')
            return error_response(f'获取对话失败: {str(e)}')

    @app.route('/api/chat/<int:chat_id>/rate', methods=['POST'])
    def rate_chat(chat_id):
        """评分对话"""
        try:
            data = request.get_json()
            
            if not data or 'rating' not in data:
                return bad_request_response('缺少rating参数')
            
            rating = data['rating']
            
            if not isinstance(rating, (int, float)) or not (0 <= rating <= 5):
                return bad_request_response('rating必须是0-5之间的数字')
            
            print(f'⭐ 评分对话: chat_id={chat_id}, rating={rating}')
            
            chat = chat_viewmodel.rate_chat(chat_id, int(rating))
            
            if not chat:
                return bad_request_response('对话不存在或评分失败', status_code=404)
            
            return success_response(chat, message='评分成功')
        except Exception as e:
            print(f'❌ 评分对话异常: {str(e)}')
            return error_response(f'评分失败: {str(e)}')

    @app.route('/api/chat/<int:chat_id>', methods=['DELETE'])
    def delete_chat(chat_id):
        """删除对话"""
        try:
            print(f'🗑️ 删除对话: chat_id={chat_id}')
            
            success = chat_viewmodel.delete_chat(chat_id)
            
            if not success:
                return error_response('删除对话失败')
            
            return success_response(None, message='对话已删除')
        except Exception as e:
            print(f'❌ 删除对话异常: {str(e)}')
            return error_response(f'删除对话失败: {str(e)}')

    @app.route('/api/chat/search', methods=['POST'])
    def search_chats():
        """搜索相似的对话"""
        try:
            data = request.get_json()
            
            if not data or 'query' not in data:
                return bad_request_response('缺少query参数')
            
            query = data['query']
            user_id = data.get('user_id')  # 可选，如果提供则只搜索该用户的对话
            limit = data.get('limit', 5)
            
            print(f'🔍 搜索对话: query={query}, user_id={user_id}, limit={limit}')
            
            chats = chat_viewmodel.search_similar_chats(query, user_id, limit)
            
            return success_response({
                'query': query,
                'results': chats,
                'count': len(chats)
            })
        except Exception as e:
            print(f'❌ 搜索对话异常: {str(e)}')
            return error_response(f'搜索对话失败: {str(e)}')
