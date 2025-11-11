/**
 * 前端认证工具函数
 * 提供token管理、登录状态检查、自动登录等功能
 */

// Token存储的localStorage key
const TOKEN_KEY = 'user_token'
const USER_INFO_KEY = 'user_info'

/**
 * Token存储函数
 * @param {string} token - 用户令牌
 */
export function setToken(token) {
  if (token) {
    localStorage.setItem(TOKEN_KEY, token)
  } else {
    localStorage.removeItem(TOKEN_KEY)
  }
}

/**
 * 获取token
 * @returns {string|null} 用户令牌
 */
export function getToken() {
  return localStorage.getItem(TOKEN_KEY)
}

/**
 * 移除token
 */
export function removeToken() {
  localStorage.removeItem(TOKEN_KEY)
  localStorage.removeItem(USER_INFO_KEY)
}

/**
 * 存储用户信息
 * @param {Object} userInfo - 用户信息对象
 */
export function setUserInfo(userInfo) {
  if (userInfo) {
    localStorage.setItem(USER_INFO_KEY, JSON.stringify(userInfo))
  } else {
    localStorage.removeItem(USER_INFO_KEY)
  }
}

/**
 * 获取用户信息
 * @returns {Object|null} 用户信息对象
 */
export function getUserInfo() {
  const userInfo = localStorage.getItem(USER_INFO_KEY)
  try {
    return userInfo ? JSON.parse(userInfo) : null
  } catch (error) {
    console.error('解析用户信息失败:', error)
    return null
  }
}

/**
 * 检查是否已登录
 * @returns {boolean} 登录状态
 */
export function isLoggedIn() {
  const token = getToken()
  const userInfo = getUserInfo()
  return !!(token && userInfo)
}

/**
 * 检查登录状态（详细）
 * @returns {Object} 登录状态详细信息
 */
export function checkLoginStatus() {
  const token = getToken()
  const userInfo = getUserInfo()
  
  return {
    isLoggedIn: !!(token && userInfo),
    hasToken: !!token,
    hasUserInfo: !!userInfo,
    token,
    userInfo
  }
}

/**
 * 自动登录检查
 * 检查本地存储的token和用户信息是否有效
 * @returns {Object} 自动登录结果
 */
export function autoLogin() {
  const loginStatus = checkLoginStatus()
  
  if (!loginStatus.isLoggedIn) {
    return {
      success: false,
      message: '未找到有效的登录信息',
      data: null
    }
  }

  // 简单验证token格式（实际项目中可能需要验证token有效期）
  const { token, userInfo } = loginStatus
  
  if (token.length < 10) {
    return {
      success: false,
      message: 'Token格式无效',
      data: null
    }
  }

  if (!userInfo.user_id || !userInfo.username) {
    return {
      success: false,
      message: '用户信息不完整',
      data: null
    }
  }

  return {
    success: true,
    message: '自动登录成功',
    data: {
      token,
      userInfo
    }
  }
}

/**
 * 清除所有认证信息
 */
export function clearAuth() {
  removeToken()
}

/**
 * 格式化用户显示名称
 * @param {Object} userInfo - 用户信息
 * @returns {string} 显示名称
 */
export function getDisplayName(userInfo) {
  if (!userInfo) return '游客'
  
  return userInfo.real_name || userInfo.username || '未知用户'
}

/**
 * 检查token是否即将过期（如果有过期时间）
 * @param {number} threshold - 提前多少分钟提醒（默认30分钟）
 * @returns {boolean} 是否即将过期
 */
export function isTokenExpiringSoon(threshold = 30) {
  const userInfo = getUserInfo()
  
  if (!userInfo || !userInfo.expires_at) {
    return false
  }

  const expiresAt = new Date(userInfo.expires_at).getTime()
  const now = Date.now()
  const thresholdMs = threshold * 60 * 1000

  return (expiresAt - now) <= thresholdMs
}

/**
 * 验证token格式
 * @param {string} token - 要验证的token
 * @returns {boolean} token格式是否有效
 */
export function validateTokenFormat(token) {
  if (!token || typeof token !== 'string') {
    return false
  }

  // 简单的token格式验证（可根据实际需求调整）
  return token.length >= 10 && token.length <= 500
}

/**
 * 获取认证请求头
 * @returns {Object} 包含认证信息的请求头
 */
export function getAuthHeaders() {
  const token = getToken()
  
  if (!token) {
    return {}
  }

  return {
    'Authorization': `Bearer ${token}`,
    'X-Requested-With': 'XMLHttpRequest'
  }
}

/**
 * 处理认证错误
 * @param {Object} error - 错误对象
 * @returns {boolean} 是否为认证相关错误
 */
export function handleAuthError(error) {
  // 检查是否为401未授权错误
  if (error.response && error.response.status === 401) {
    clearAuth()
    // 重定向到登录页面（如果在组件外部调用）
    if (typeof window !== 'undefined' && window.location) {
      window.location.href = '/login'
    }
    return true
  }
  
  return false
}

/**
 * 刷新用户信息（从API重新获取）
 * @param {Function} getUserInfoAPI - 获取用户信息的API函数
 * @returns {Promise<Object>} 用户信息
 */
export async function refreshUserInfo(getUserInfoAPI) {
  try {
    if (!isLoggedIn()) {
      throw new Error('用户未登录')
    }

    const response = await getUserInfoAPI()
    
    if (response.success) {
      setUserInfo(response.data)
      return {
        success: true,
        data: response.data
      }
    } else {
      throw new Error(response.error || '获取用户信息失败')
    }
  } catch (error) {
    console.error('刷新用户信息失败:', error)
    return {
      success: false,
      error: error.message
    }
  }
}

// 默认导出所有函数
export default {
  setToken,
  getToken,
  removeToken,
  setUserInfo,
  getUserInfo,
  isLoggedIn,
  checkLoginStatus,
  autoLogin,
  clearAuth,
  getDisplayName,
  isTokenExpiringSoon,
  validateTokenFormat,
  getAuthHeaders,
  handleAuthError,
  refreshUserInfo
} 