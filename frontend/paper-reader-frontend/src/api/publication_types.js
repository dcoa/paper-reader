import request from '@/utils/request'

/**
 * 获取文献类型列表
 * 对应API: GET /api/publication-types
 */
export const getPublicationTypes = () => {
  return request({
    url: '/publication-types',
    method: 'get'
  })
} 