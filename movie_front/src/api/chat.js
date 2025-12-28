/**
 * AI对话 API 服务
 */

const API_BASE_URL = '/api';

/**
 * 保存对话记录
 * @param {number} userId - 用户ID
 * @param {string} question - 用户问题
 * @param {string} answer - AI回答
 * @param {array} relatedMovies - 相关电影ID列表
 */
export async function saveChat(userId, question, answer, relatedMovies = []) {
  try {
    const response = await fetch(`${API_BASE_URL}/chat/save`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${localStorage.getItem('token')}`
      },
      body: JSON.stringify({
        user_id: userId,
        question,
        answer,
        related_movies: relatedMovies
      })
    });

    const data = await response.json();

    if (!response.ok) {
      throw new Error(data.message || '保存对话失败');
    }

    return data.data;
  } catch (error) {
    console.error('保存对话失败:', error);
    throw error;
  }
}

/**
 * 获取对话历史
 * @param {number} userId - 用户ID
 * @param {number} page - 页码
 * @param {number} perPage - 每页数量
 */
export async function getChatHistory(userId, page = 1, perPage = 20) {
  try {
    const response = await fetch(
      `${API_BASE_URL}/chat/history/${userId}?page=${page}&per_page=${perPage}`,
      {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      }
    );

    const data = await response.json();

    if (!response.ok) {
      throw new Error(data.message || '获取对话历史失败');
    }

    return data.data;
  } catch (error) {
    console.error('获取对话历史失败:', error);
    throw error;
  }
}

/**
 * 获取单条对话
 * @param {number} chatId - 对话ID
 */
export async function getChat(chatId) {
  try {
    const response = await fetch(`${API_BASE_URL}/chat/${chatId}`, {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('token')}`
      }
    });

    const data = await response.json();

    if (!response.ok) {
      throw new Error(data.message || '获取对话失败');
    }

    return data.data;
  } catch (error) {
    console.error('获取对话失败:', error);
    throw error;
  }
}

/**
 * 评分对话
 * @param {number} chatId - 对话ID
 * @param {number} rating - 评分 (0-5)
 */
export async function rateChat(chatId, rating) {
  try {
    if (rating < 0 || rating > 5) {
      throw new Error('评分必须在0-5之间');
    }

    const response = await fetch(`${API_BASE_URL}/chat/${chatId}/rate`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${localStorage.getItem('token')}`
      },
      body: JSON.stringify({ rating })
    });

    const data = await response.json();

    if (!response.ok) {
      throw new Error(data.message || '评分失败');
    }

    return data.data;
  } catch (error) {
    console.error('评分失败:', error);
    throw error;
  }
}

/**
 * 删除对话
 * @param {number} chatId - 对话ID
 */
export async function deleteChat(chatId) {
  try {
    const response = await fetch(`${API_BASE_URL}/chat/${chatId}`, {
      method: 'DELETE',
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('token')}`
      }
    });

    const data = await response.json();

    if (!response.ok) {
      throw new Error(data.message || '删除对话失败');
    }

    return true;
  } catch (error) {
    console.error('删除对话失败:', error);
    throw error;
  }
}

/**
 * 搜索相似的对话
 * @param {string} query - 搜索关键词
 * @param {number} userId - 用户ID (可选)
 * @param {number} limit - 返回结果数量
 */
export async function searchChats(query, userId = null, limit = 5) {
  try {
    const response = await fetch(`${API_BASE_URL}/chat/search`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${localStorage.getItem('token')}`
      },
      body: JSON.stringify({
        query,
        user_id: userId,
        limit
      })
    });

    const data = await response.json();

    if (!response.ok) {
      throw new Error(data.message || '搜索失败');
    }

    return data.data;
  } catch (error) {
    console.error('搜索失败:', error);
    throw error;
  }
}
