import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  timeout: 60000
})

export const uploadPDF = (file, onProgress) => {
  const formData = new FormData()
  formData.append('file', file)
  
  return api.post('/upload', formData, {
    headers: {
      'Content-Type': 'multipart/form-data'
    },
    onUploadProgress: (progressEvent) => {
      if (onProgress) {
        const percentCompleted = Math.round((progressEvent.loaded * 100) / progressEvent.total)
        onProgress(percentCompleted)
      }
    }
  })
}

export const askQuestion = (question) => {
  return api.post('/ask', { question })
}

export const getStats = () => {
  return api.get('/stats')
}

export const clearDatabase = () => {
  return api.post('/clear')
}

export const getSummary = () => {
  // The backend waits up to 90s for the LLM, so allow more than the default timeout
  return api.post('/summarize', null, { timeout: 120000 })
}

export default api

