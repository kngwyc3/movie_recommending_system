/**
 * AI 服务 API
 * 提供所有 AI 相关的后端接口调用
 */

const API_BASE_URL = '/api';

/**
 * 获取当前 token
 */
function getToken() {
  return localStorage.getItem('token');
}

/**
 * 通用请求方法
 */
async function request(url, options = {}) {
  try {
    const token = getToken();

    const headers = {
      'Content-Type': 'application/json',
      ...options.headers
    };

    // 如果有 token，添加到请求头
    if (token && !options.skipAuth) {
      headers['Authorization'] = `Bearer ${token}`;
    }

    console.log('AI API 请求:', {
      url: `${API_BASE_URL}${url}`,
      method: options.method || 'GET'
    });

    const response = await fetch(`${API_BASE_URL}${url}`, {
      headers,
      ...options
    });

    console.log('AI API 响应状态:', response.status, response.ok);

    const data = await response.json();

    if (!response.ok) {
      throw new Error(data.message || data.error || `请求失败 (${response.status})`);
    }

    // 如果后端返回 { success: true, data: {...} } 格式，则返回data字段
    if (data.success && data.data !== undefined) {
      return data.data;
    }

    return data;
  } catch (error) {
    console.error('AI API 请求错误:', error);
    throw error;
  }
}

/**
 * AI 推荐 API
 */
export const aiApi = {
  /**
   * 电影推荐（完整响应）
   * @param {string} query - 查询文本
   * @param {number} topK - 检索数量
   * @param {number} rerankTopN - 重排序后返回数量
   * @returns {Promise<Object>} 推荐结果
   */
  async recommend(query, topK = 5, rerankTopN = 3) {
    return request('/ai/recommend', {
      method: 'POST',
      body: JSON.stringify({
        query,
        top_k: topK,
        rerank_top_n: rerankTopN
      })
    });
  },

  /**
   * 电影推荐（流式响应）
   * @param {string} query - 查询文本
   * @param {number} topK - 检索数量
   * @param {number} rerankTopN - 重排序后返回数量
   * @param {Function} onMessage - 消息回调函数
   * @param {Function} onError - 错误回调函数
   * @param {Function} onComplete - 完成回调函数
   */
  async recommendStream(query, topK = 5, rerankTopN = 3, { onMessage, onError, onComplete }) {
    try {
      const token = getToken();
      const headers = {
        'Content-Type': 'application/json'
      };

      if (token) {
        headers['Authorization'] = `Bearer ${token}`;
      }

      const response = await fetch(`${API_BASE_URL}/ai/recommend/stream`, {
        method: 'POST',
        headers,
        body: JSON.stringify({
          query,
          top_k: topK,
          rerank_top_n: rerankTopN
        })
      });

      if (!response.ok) {
        throw new Error(`请求失败 (${response.status})`);
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder();

      while (true) {
        const { done, value } = await reader.read();
        
        if (done) {
          onComplete?.();
          break;
        }

        const chunk = decoder.decode(value);
        const lines = chunk.split('\n');

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            try {
              const data = JSON.parse(line.slice(6));
              onMessage?.(data);

              if (data.type === 'error') {
                onError?.(new Error(data.data.message));
              }
            } catch (e) {
              console.error('解析SSE数据失败:', e);
            }
          }
        }
      }
    } catch (error) {
      console.error('流式推荐失败:', error);
      onError?.(error);
    }
  },

  /**
   * 混合检索
   * @param {string} query - 查询文本
   * @param {string} mode - 检索模式 (hybrid, vector, bm25)
   * @param {number} topK - 返回结果数量
   * @param {boolean} rerank - 是否启用重排序
   * @returns {Promise<Array>} 检索结果列表
   */
  async search(query, mode = 'hybrid', topK = 5, rerank = false) {
    return request('/ai/search', {
      method: 'POST',
      body: JSON.stringify({
        query,
        mode,
        top_k: topK,
        rerank
      })
    });
  },

  /**
   * 向量检索
   * @param {string} query - 查询文本
   * @param {number} topK - 返回结果数量
   * @param {boolean} rerank - 是否启用重排序
   * @returns {Promise<Array>} 检索结果列表
   */
  async vectorSearch(query, topK = 5, rerank = false) {
    return request('/ai/vector-search', {
      method: 'POST',
      body: JSON.stringify({
        query,
        top_k: topK,
        rerank
      })
    });
  },

  /**
   * BM25 检索
   * @param {string} query - 查询文本
   * @param {number} topK - 返回结果数量
   * @param {boolean} rerank - 是否启用重排序
   * @returns {Promise<Array>} 检索结果列表
   */
  async bm25Search(query, topK = 5, rerank = false) {
    return request('/ai/bm25-search', {
      method: 'POST',
      body: JSON.stringify({
        query,
        top_k: topK,
        rerank
      })
    });
  },

  /**
   * 智能问答
   * @param {string} query - 用户问题
   * @param {number} topK - 检索的文档数量
   * @returns {Promise<Object>} 包含检索结果和 LLM 回答的对象
   */
  async chat(query, topK = 5) {
    return request('/ai/chat', {
      method: 'POST',
      body: JSON.stringify({
        query,
        top_k: topK
      })
    });
  },

  /**
   * 重排序
   * @param {string} query - 查询文本
   * @param {Array<string>} documents - 文档列表
   * @param {number} topN - 返回前N个结果
   * @returns {Promise<Array>} 重排序后的结果列表
   */
  async rerank(query, documents, topN = 5) {
    return request('/ai/rerank', {
      method: 'POST',
      body: JSON.stringify({
        query,
        documents,
        top_n: topN
      })
    });
  },

  /**
   * 获取检索详细信息
   * @param {string} query - 查询文本
   * @returns {Promise<Object>} 包含向量检索、BM25检索、重排序等详细信息的对象
   */
  async getRetrievalDetails(query) {
    return request('/ai/retrieval-details', {
      method: 'POST',
      body: JSON.stringify({ query })
    });
  }
};

export default aiApi;
