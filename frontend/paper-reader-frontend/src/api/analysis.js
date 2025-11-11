import request from '@/utils/request'

/**
 * 获取文献分析结果
 * @param {number} paperId - 文献ID
 * @returns {Promise}
 */
export function getPaperAnalysis(paperId) {
  return request({
    url: `/papers/${paperId}/analysis`,
    method: 'get'
  })
}

/**
 * 创建文献分析
 * @param {number} paperId - 文献ID
 * @param {object} params - 分析参数
 * @returns {Promise}
 */
export function createPaperAnalysis(paperId, params = {}) {
  return request({
    url: `/papers/${paperId}/analysis`,
    method: 'post',
    data: params
  })
}

/**
 * 获取分析状态
 * @param {number} paperId - 文献ID
 * @returns {Promise}
 */
export function getAnalysisStatus(paperId) {
  return request({
    url: `/papers/${paperId}/analysis/status`,
    method: 'get'
  })
}

/**
 * 删除文献分析结果
 * @param {number} paperId - 文献ID
 * @returns {Promise}
 */
export function deletePaperAnalysis(paperId) {
  return request({
    url: `/papers/${paperId}/analysis`,
    method: 'delete'
  })
}

/**
 * 批量分析文献
 * @param {Array} paperIds - 文献ID列表
 * @returns {Promise}
 */
export function batchAnalyzePapers(paperIds) {
  return request({
    url: '/papers/analysis/batch',
    method: 'post',
    data: {
      paper_ids: paperIds
    }
  })
} 