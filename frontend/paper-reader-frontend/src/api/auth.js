import request from '@/utils/request'

/**
 * 用户登录
 * 对应API: POST /api/auth/login
 */
export const login = (data) => {
  return request({
    url: '/auth/login',
    method: 'post',
    data
  })
}

/**
 * 获取用户信息
 * 对应API: GET /api/user/info
 */
export const getUserInfo = () => {
  return request({
    url: '/user/info',
    method: 'get'
  })
}

/**
 * 用户退出登录
 * 对应API: POST /api/auth/logout
 */
export const logout = () => {
  return request({
    url: '/auth/logout',
    method: 'post'
  })
}