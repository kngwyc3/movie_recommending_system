/**
 * 电影 API 服务
 * 提供所有电影相关的后端接口调用
 * 注意：使用Vite代理，不需要写完整URL，直接使用 /api 即可
 */

const API_BASE_URL = '/api';
const BACKEND_BASE_URL = 'http://localhost:5000';

/**
 * 获取可靠的图片URL（带fallback）
 * @param {string} path - 图片路径或URL
 * @param {string} width - 宽度参数
 * @param {string} height - 高度参数
 * @returns {string} 可靠的图片URL
 */
export function getReliableImageUrl(path, width = '400', height = '600') {
  if (!path) {
    return `https://placehold.co/${width}x${height}/1a1a2e/00f0ff?text=No+Image`;
  }

  // 如果是已知的不可靠图片源，直接返回占位图
  if (path.includes('images.unsplash.com/photo-1478720568477-152d9b164e63')) {
    return `https://placehold.co/${width}x${height}/1a1a2e/00f0ff?text=No+Image`;
  }

  // 如果是相对路径，构建完整URL
  if (!path.startsWith('http://') && !path.startsWith('https://')) {
    return `${BACKEND_BASE_URL}${path.startsWith('/') ? '' : '/'}${path}`;
  }

  return path;
}

/**
 * 构建完整的资源URL（头像、图片等）
 * @param {string} path - 相对路径或完整URL
 * @returns {string} 完整URL
 */
export function buildResourceUrl(path) {
  if (!path) {
    return '';
  }

  // 如果已经是完整URL，直接返回
  if (path.startsWith('http://') || path.startsWith('https://')) {
    return path;
  }

  // 如果是相对路径，构建完整URL
  return `${BACKEND_BASE_URL}${path.startsWith('/') ? '' : '/'}${path}`;
}

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

    const response = await fetch(`${API_BASE_URL}${url}`, {
      headers,
      ...options
    });

    const data = await response.json();

    if (!response.ok) {
      throw new Error(data.message || data.error || `请求失败 (${response.status})`);
    }

    // 如果后端返回 { success: true, data: {...} 格式，则返回data字段
    if (data.success && data.data !== undefined) {
      return data.data;
    }

    return data;
  } catch (error) {
    console.error('API 请求错误:', error);
    throw error;
  }
}

/**
 * 构建查询字符串
 */
function buildQueryString(params) {
  const query = new URLSearchParams();
  Object.keys(params).forEach(key => {
    if (params[key] !== undefined && params[key] !== null) {
      query.append(key, params[key]);
    }
  });
  return query.toString() ? `?${query.toString()}` : '';
}

/**
 * 认证 API 接口
 */
export const authApi = {
  /**
   * 用户注册
   * @param {string} username - 用户名
   * @param {string} email - 邮箱
   * @param {string} password - 密码
   */
  async register(username, email, password) {
    return request('/auth/register', {
      method: 'POST',
      body: JSON.stringify({ username, email, password })
    });
  },

  /**
   * 用户登录
   * @param {string} email - 邮箱
   * @param {string} password - 密码
   */
  async login(email, password) {
    return request('/auth/login', {
      method: 'POST',
      body: JSON.stringify({ email, password })
    });
  },

  /**
   * 验证 Token
   * @param {string} token - JWT token
   */
  async verifyToken(token) {
    return request('/auth/verify', {
      method: 'POST',
      body: JSON.stringify({ token }),
      skipAuth: true
    });
  },

  /**
   * 修改密码
   * @param {string} oldPassword - 旧密码
   * @param {string} newPassword - 新密码
   */
  async changePassword(oldPassword, newPassword) {
    return request('/auth/change-password', {
      method: 'POST',
      body: JSON.stringify({ old_password: oldPassword, new_password: newPassword })
    });
  },

  /**
   * 退出登录
   */
  logout() {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    localStorage.removeItem('isLoggedIn');
  }
};

/**
 * 用户 API 接口
 */
export const userApi = {
  /**
   * 获取用户信息
   * @param {number} userId - 用户ID
   */
  async getUserInfo(userId) {
    return request(`/user/${userId}`);
  },

  /**
   * 更新用户信息
   * @param {number} userId - 用户ID
   * @param {object} data - 更新数据
   */
  async updateUserInfo(userId, data) {
    return request(`/user/${userId}`, {
      method: 'PUT',
      body: JSON.stringify(data)
    });
  },

  /**
   * 上传用户头像
   * @param {number} userId - 用户ID
   * @param {FormData} formData - 包含avatar文件的FormData
   */
  async uploadAvatar(userId, formData) {
    return request(`/user/${userId}/avatar`, {
      method: 'POST',
      body: formData,
      headers: {} // 让fetch自动设置multipart/form-data的Content-Type
    });
  },

  /**
   * 获取收藏列表
   * @param {number} userId - 用户ID
   */
  async getFavorites(userId) {
    return request(`/user/${userId}/favorites`);
  },

  /**
   * 添加收藏
   * @param {number} userId - 用户ID
   * @param {number} movieId - 电影ID
   */
  async addFavorite(userId, movieId) {
    return request(`/user/${userId}/favorites/${movieId}`, {
      method: 'POST'
    });
  },

  /**
   * 移除收藏
   * @param {number} userId - 用户ID
   * @param {number} movieId - 电影ID
   */
  async removeFavorite(userId, movieId) {
    return request(`/user/${userId}/favorites/${movieId}`, {
      method: 'DELETE'
    });
  },

  /**
   * 获取观看历史
   * @param {number} userId - 用户ID
   */
  async getHistory(userId) {
    return request(`/user/${userId}/history`);
  },

  /**
   * 添加观看记录
   * @param {number} userId - 用户ID
   * @param {number} movieId - 电影ID
   */
  async addHistory(userId, movieId) {
    return request(`/user/${userId}/history/${movieId}`, {
      method: 'POST'
    });
  },

  /**
   * 获取评分列表
   * @param {number} userId - 用户ID
   */
  async getRatings(userId) {
    return request(`/user/${userId}/ratings`);
  },

  /**
   * 评分电影
   * @param {number} userId - 用户ID
   * @param {number} movieId - 电影ID
   * @param {number} score - 评分
   */
  async rateMovie(userId, movieId, score) {
    return request(`/user/${userId}/rate/${movieId}`, {
      method: 'POST',
      body: JSON.stringify({ score })
    });
  },

  /**
   * 更新偏好设置
   * @param {number} userId - 用户ID
   * @param {object} preferences - 偏好配置
   */
  async updatePreferences(userId, preferences) {
    return request(`/user/${userId}/preferences`, {
      method: 'PUT',
      body: JSON.stringify(preferences)
    });
  }
};

/**
 * 电影 API 接口
 */
export const movieApi = {
  /**
   * 获取热门电影列表
   * @param {number} page - 页码
   * @param {number} perPage - 每页数量
   */
  async getHotMovies(page = 1, perPage = 8) {
    const query = buildQueryString({ page, per_page: perPage });
    return request(`/movies/hot${query}`);
  },

  /**
   * 获取最新上映电影
   * @param {number} page - 页码
   * @param {number} perPage - 每页数量
   */
  async getNewMovies(page = 1, perPage = 4) {
    const query = buildQueryString({ page, per_page: perPage });
    return request(`/movies/new${query}`);
  },

  /**
   * 获取特色推荐电影（横幅展示）
   */
  async getFeaturedMovie() {
    return request('/movies/featured');
  },

  /**
   * 按分类筛选电影
   * @param {string} category - 分类名称
   * @param {number} page - 页码
   * @param {number} perPage - 每页数量
   */
  async getMoviesByCategory(category, page = 1, perPage = 12) {
    const query = buildQueryString({ page, per_page: perPage });
    return request(`/movies/category/${encodeURIComponent(category)}${query}`);
  },

  /**
   * 获取所有分类
   */
  async getCategories() {
    return request('/movies/categories');
  },

  /**
   * 搜索电影
   * @param {string} query - 搜索关键词
   * @param {number} page - 页码
   * @param {number} perPage - 每页数量
   */
  async searchMovies(query, page = 1, perPage = 12) {
    const queryString = buildQueryString({ q: query, page, per_page: perPage });
    return request(`/movies/search${queryString}`);
  },

  /**
   * 获取电影详情
   * @param {number} movieId - 电影ID
   */
  async getMovieDetail(movieId) {
    return request(`/movies/${movieId}`);
  },

  /**
   * 获取所有电影
   * @param {number} page - 页码
   * @param {number} perPage - 每页数量
   */
  async getAllMovies(page = 1, perPage = 12) {
    const query = buildQueryString({ page, per_page: perPage });
    return request(`/movies${query}`);
  },

  /**
   * 健康检查
   */
  async healthCheck() {
    return request('/health');
  }
};
