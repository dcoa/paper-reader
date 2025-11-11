import request from '@/utils/request'

/**
 * 管理员获取文献列表
 * 对应API: GET /api/admin/papers
 */
export const getAdminPapers = (params = {}) => {
  return request({
    url: '/admin/papers',
    method: 'get',
    params
  })
}

/**
 * 管理员更新文献信息
 * 对应API: PUT /api/admin/papers/:id
 */
export const updatePaper = (id, data) => {
  return request({
    url: `/admin/papers/${id}`,
    method: 'put',
    data
  })
}

/**
 * 管理员删除文献
 * 对应API: DELETE /api/admin/papers/:id
 */
export const deletePaper = (id) => {
  return request({
    url: `/admin/papers/${id}`,
    method: 'delete'
  })
}

/**
 * 管理员恢复文献
 * 对应API: POST /api/admin/papers/:id/restore
 */
export const restorePaper = (id) => {
  return request({
    url: `/admin/papers/${id}/restore`,
    method: 'post'
  })
}

/**
 * 管理员获取用户列表
 * 对应API: GET /api/admin/users
 */
export const getAdminUsers = (params = {}) => {
  return request({
    url: '/admin/users',
    method: 'get',
    params
  })
}

/**
 * 管理员添加用户
 * 对应API: POST /api/admin/users
 */
export const createUser = (data) => {
  return request({
    url: '/admin/users',
    method: 'post',
    data
  })
}

/**
 * 管理员更新用户信息
 * 对应API: PUT /api/admin/users/:id
 */
export const updateUser = (id, data) => {
  return request({
    url: `/admin/users/${id}`,
    method: 'put',
    data
  })
}

/**
 * 管理员更新用户状态
 * 对应API: PUT /api/admin/users/:id/status
 */
export const updateUserStatus = (id, data) => {
  return request({
    url: `/admin/users/${id}/status`,
    method: 'put',
    data
  })
}

/**
 * 管理员删除用户
 * 对应API: DELETE /api/admin/users/:id
 */
export const deleteUser = (id) => {
  return request({
    url: `/admin/users/${id}`,
    method: 'delete'
  })
}

/**
 * 获取系统统计信息
 * 对应API: GET /api/admin/statistics
 */
export const getStatistics = () => {
  return request({
    url: '/admin/statistics',
    method: 'get'
  })
}

/**
 * 下载文献文件
 * 对应API: GET /api/papers/:id/download
 */
export const downloadPaper = (id) => {
  return request({
    url: `/papers/${id}/download`,
    method: 'get',
    responseType: 'blob'
  })
} 