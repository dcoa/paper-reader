import request from '@/utils/request'

/**
 * AI问答
 * 对应API: POST /api/ai/ask
 */
export const askAI = (data) => {
  return request({
    url: '/ai/ask',
    method: 'post',
    data,
    timeout: 120000  // AI请求设置120秒超时
  })
}

/**
 * AI问答（支持模型选择）
 * 对应API: POST /api/ai/ask
 */
export const askAIWithModel = (data) => {
  return request({
    url: '/ai/ask',
    method: 'post',
    data,
    timeout: 120000  // 推理模型可能需要更长时间
  })
}

/**
 * 翻译文本
 * 对应API: POST /api/ai/translate
 */
export const translateText = (data) => {
  return request({
    url: '/ai/translate',
    method: 'post',
    data,
    timeout: 90000  // 翻译请求90秒超时
  })
}

/**
 * 生成核心看点
 * 对应API: POST /api/ai/key-insights
 */
export const generateKeyInsights = (data) => {
  return request({
    url: '/ai/key-insights',
    method: 'post',
    data,
    timeout: 150000  // 核心看点生成可能需要较长时间，设置150秒
  })
}

/**
 * 生成Related Work描述
 * 对应API: POST /api/ai/related-work
 */
export const generateRelatedWork = (data) => {
  return request({
    url: '/ai/related-work',
    method: 'post',
    data,
    timeout: 150000  // Related Work描述生成可能需要较长时间，设置150秒
  })
}

/**
 * 生成智能摘要（保留原功能）
 * 对应API: POST /api/ai/summary
 */
export const generateSummary = (data) => {
  return request({
    url: '/ai/summary',
    method: 'post',
    data,
    timeout: 120000  // 摘要生成可能需要较长时间，设置120秒
  })
}

/**
 * 提取关键词（保留原功能）
 * 对应API: POST /api/ai/keywords
 */
export const extractKeywords = (data) => {
  return request({
    url: '/ai/keywords',
    method: 'post',
    data,
    timeout: 90000  // 关键词提取90秒超时
  })
}

/**
 * 获取AI对话历史
 * 对应API: GET /api/ai/history/{paper_id}
 */
export const getAIHistory = (paperId) => {
  return request({
    url: `/ai/history/${paperId}`,
    method: 'get'
  })
} 