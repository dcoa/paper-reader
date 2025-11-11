import request from '@/utils/request'

/**
 * 文献上传
 * 对应API: POST /api/papers/upload
 */
export const uploadPaper = (formData) => {
  return request({
    url: '/papers/upload',
    method: 'post',
    data: formData,
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  })
}

/**
 * 获取文献列表
 * 对应API: GET /api/papers/list
 */
export const getPapersList = (params) => {
  return request({
    url: '/papers/list',
    method: 'get',
    params
  })
}

/**
 * 获取文献详情
 * 对应API: GET /api/papers/{paper_id}
 */
export const getPaperDetail = (paperId) => {
  return request({
    url: `/papers/${paperId}`,
    method: 'get'
  })
}

/**
 * 下载文献文件
 * 对应API: GET /api/papers/{paper_id}/download
 */
export const downloadPaper = (paperId) => {
  return request({
    url: `/papers/${paperId}/download`,
    method: 'get',
    responseType: 'blob'
  })
}

/**
 * 获取用户文献统计
 * 对应API: GET /api/papers/user-statistics
 */
export const getUserPaperStatistics = () => {
  return request({
    url: '/papers/user-statistics',
    method: 'get'
  })
} 