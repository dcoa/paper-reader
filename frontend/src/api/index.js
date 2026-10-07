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
  return api.post('/summarize')
}

export default api

