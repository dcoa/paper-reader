import request from '@/utils/request'

/**
 * 创建批注
 * 对应API: POST /api/annotations
 */
export const createAnnotation = (data) => {
  return request({
    url: '/annotations',
    method: 'post',
    data
  })
}

/**
 * 获取批注列表
 * 对应API: GET /api/annotations/{paper_id}
 */
export const getAnnotations = (paperId) => {
  return request({
    url: `/annotations/${paperId}`,
    method: 'get'
  })
}

/**
 * 删除批注
 * 对应API: DELETE /api/annotations/{annotation_id}
 */
export const deleteAnnotation = (annotationId) => {
  return request({
    url: `/annotations/${annotationId}`,
    method: 'delete'
  })
} 