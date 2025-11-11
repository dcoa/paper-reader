import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const useUserStore = defineStore('user', () => {
  // 状态
  const user = ref(null)
  const token = ref(localStorage.getItem('token') || null)
  
  // 计算属性
  const isLoggedIn = computed(() => !!token.value)
  const username = computed(() => user.value?.username || '')
  const userRole = computed(() => user.value?.role || 'user')
  const isAdmin = computed(() => userRole.value === 'admin')
  
  // 方法
  const setUser = (userData) => {
    user.value = userData
    if (userData) {
      localStorage.setItem('user', JSON.stringify(userData))
    } else {
      localStorage.removeItem('user')
    }
  }
  
  const setToken = (tokenValue) => {
    token.value = tokenValue
    if (tokenValue) {
      localStorage.setItem('token', tokenValue)
    } else {
      localStorage.removeItem('token')
    }
  }
  
  const login = (userData, tokenValue) => {
    setUser(userData)
    setToken(tokenValue)
  }
  
  const logout = () => {
    setUser(null)
    setToken(null)
  }
  
  // 初始化时检查token
  const checkAuth = () => {
    const storedToken = localStorage.getItem('token')
    const storedUser = localStorage.getItem('user')
    if (storedToken) {
      token.value = storedToken
      // 恢复用户信息
      if (storedUser) {
        try {
          user.value = JSON.parse(storedUser)
        } catch (e) {
          console.error('Failed to parse stored user:', e)
          user.value = null
        }
      }
      return true
    }
    return false
  }
  
  return {
    user,
    token,
    isLoggedIn,
    username,
    userRole,
    isAdmin,
    setUser,
    setToken,
    login,
    logout,
    checkAuth
  }
}) 