<template>
  <div class="login-container">
    <div class="login-background">
      <div class="background-pattern"></div>
      <div class="background-overlay"></div>
    </div>
    
    <div class="login-content">
      <div class="login-wrapper">
        <!-- Brand Section -->
        <div class="brand-section">
          <div class="brand-logo">
            <h1 class="brand-title">PaperReader</h1>
            <p class="brand-subtitle">Research Paper Management Platform</p>
          </div>
          <p class="brand-description">
            Intelligent research paper management tool to help researchers efficiently manage, read and analyze academic papers.
          </p>
        </div>

        <!-- Login Form Section -->
        <div class="form-section">
          <div class="form-container">
            <div class="form-header">
              <h2 class="form-title">Welcome Back</h2>
              <p class="form-subtitle">Please log in to your account</p>
            </div>
            
            <el-form
              ref="loginFormRef"
              :model="loginForm"
              :rules="loginRules"
              class="login-form"
              @submit.prevent="handleLogin"
            >
              <el-form-item prop="username" class="form-item">
                <label class="form-label">Username</label>
                <el-input
                  v-model="loginForm.username"
                  placeholder="Enter username"
                  size="large"
                  class="form-input"
                  clearable
                >
                  <template #prefix>
                    <el-icon class="input-icon"><User /></el-icon>
                  </template>
                </el-input>
              </el-form-item>

              <el-form-item prop="password" class="form-item">
                <label class="form-label">Password</label>
                <el-input
                  v-model="loginForm.password"
                  type="password"
                  placeholder="Enter password"
                  size="large"
                  class="form-input"
                  show-password
                  clearable
                  @keyup.enter="handleLogin"
                >
                  <template #prefix>
                    <el-icon class="input-icon"><Lock /></el-icon>
                  </template>
                </el-input>
              </el-form-item>
              
              <el-form-item class="form-item">
                <button
                  type="button"
                  class="login-button"
                  :class="{ 'login-button--loading': loading }"
                  :disabled="loading"
                  @click="handleLogin"
                >
                  <el-icon v-if="loading" class="loading-icon"><Loading /></el-icon>
                  <span>{{ loading ? 'Logging in...' : 'Login' }}</span>
                </button>
              </el-form-item>
            </el-form>

            <div class="form-footer">
              <div class="login-tips">
                <div class="tip-item">
                  <el-icon class="tip-icon"><InfoFilled /></el-icon>
                  <span>This is a simple login system</span>
                </div>
                <div class="tip-item">
                  <el-icon class="tip-icon"><Key /></el-icon>
                  <span>Please use your username and password to log in</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useUserStore } from '@/store/user'
import { login } from '@/api/auth'

const router = useRouter()
const userStore = useUserStore()

// 表单引用
const loginFormRef = ref()

// 加载状态
const loading = ref(false)

// 登录表单数据
const loginForm = reactive({
  username: '',
  password: ''
})

// Form validation rules
const loginRules = {
  username: [
    { required: true, message: 'Please enter username', trigger: 'blur' },
    { min: 1, max: 50, message: 'Username length should be between 1 and 50 characters', trigger: 'blur' }
  ],
  password: [
    { required: true, message: 'Please enter password', trigger: 'blur' },
    { min: 1, max: 50, message: 'Password length should be between 1 and 50 characters', trigger: 'blur' }
  ]
}

// 登录处理
const handleLogin = async () => {
  if (!loginFormRef.value) return
  
  try {
    // 表单验证
    await loginFormRef.value.validate()
    
    loading.value = true
    
    // 调用登录API
    const response = await login({
      username: loginForm.username,
      password: loginForm.password
    })
    
    if (response.success) {
      // Save user information and token
      userStore.login(response.data, response.data.token)

      ElMessage.success('Login successful')

      // Redirect based on user role
      if (response.data.role === 'admin') {
        router.push('/admin/dashboard')
      } else {
        router.push('/home')
      }
    } else {
      ElMessage.error(response.error || 'Login failed')
    }
  } catch (error) {
    console.error('Login failed:', error)
    ElMessage.error('Login failed, please check your username and password')
  } finally {
    loading.value = false
  }
}

// 组件挂载时检查登录状态
onMounted(() => {
  if (userStore.isLoggedIn) {
    router.push('/home')
  }
})
</script>

<style scoped>
.login-container {
  min-height: 100vh;
  width: 100%;
  display: flex;
  position: relative;
  overflow: hidden;
}

.login-background {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(135deg, var(--color-primary) 0%, var(--color-primary-dark) 100%);
}

.background-pattern {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-image: 
    radial-gradient(circle at 25% 25%, rgba(255, 255, 255, 0.1) 0%, transparent 50%),
    radial-gradient(circle at 75% 75%, rgba(255, 255, 255, 0.1) 0%, transparent 50%);
  background-size: 400px 400px;
}

.background-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.1);
}

.login-content {
  position: relative;
  z-index: 1;
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: var(--spacing-6);
}

.login-wrapper {
  width: 100%;
  max-width: 1000px;
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: var(--spacing-12);
  align-items: center;
}

/* 品牌区域 */
.brand-section {
  color: white;
  text-align: left;
}

.brand-logo {
  margin-bottom: var(--spacing-8);
}

.brand-title {
  margin: 0 0 var(--spacing-2) 0;
  font-size: 3rem;
  font-weight: var(--font-weight-bold);
  line-height: 1.1;
}

.brand-subtitle {
  margin: 0;
  font-size: var(--font-size-h4);
  font-weight: var(--font-weight-medium);
  opacity: 0.9;
}

.brand-description {
  font-size: var(--font-size-body1);
  line-height: var(--line-height-body1);
  opacity: 0.8;
  margin: 0;
}

/* 表单区域 */
.form-section {
  display: flex;
  justify-content: center;
}

.form-container {
  width: 100%;
  max-width: 400px;
  background-color: var(--color-background-paper);
  border-radius: var(--border-radius-xl);
  padding: var(--spacing-8);
  box-shadow: var(--shadow-xl);
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.form-header {
  text-align: center;
  margin-bottom: var(--spacing-8);
}

.form-title {
  margin: 0 0 var(--spacing-2) 0;
  font-size: var(--font-size-h2);
  font-weight: var(--font-weight-bold);
  color: var(--color-text-primary);
}

.form-subtitle {
  margin: 0;
  font-size: var(--font-size-body1);
  color: var(--color-text-secondary);
}

.login-form {
  margin-bottom: var(--spacing-6);
}

.form-item {
  margin-bottom: var(--spacing-6);
}

.form-label {
  display: block;
  margin-bottom: var(--spacing-2);
  font-size: var(--font-size-body2);
  font-weight: var(--font-weight-medium);
  color: var(--color-text-primary);
}

.form-input {
  width: 100%;
}

.form-input :deep(.el-input__wrapper) {
  padding: 12px 16px;
  border-radius: var(--border-radius);
  border: 1px solid var(--color-grey-300);
  transition: all var(--transition-fast);
}

.form-input :deep(.el-input__wrapper:hover) {
  border-color: var(--color-primary);
}

.form-input :deep(.el-input__wrapper.is-focus) {
  border-color: var(--color-primary);
  box-shadow: 0 0 0 3px rgba(32, 190, 255, 0.2);
}

.input-icon {
  color: var(--color-text-secondary);
  margin-right: var(--spacing-2);
}

.login-button {
  width: 100%;
  padding: 14px 24px;
  background-color: var(--color-primary);
  color: white;
  border: none;
  border-radius: var(--border-radius);
  font-size: var(--font-size-button);
  font-weight: var(--font-weight-semibold);
  cursor: pointer;
  transition: all var(--transition-fast);
  display: flex;
  align-items: center;
  justify-content: center;
  gap: var(--spacing-2);
  font-family: var(--font-family);
}

.login-button:hover:not(:disabled) {
  background-color: var(--color-primary-dark);
  transform: translateY(-1px);
  box-shadow: var(--shadow-lg);
}

.login-button:active:not(:disabled) {
  transform: translateY(0);
}

.login-button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.login-button--loading {
  pointer-events: none;
}

.loading-icon {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}

.form-footer {
  padding-top: var(--spacing-6);
  border-top: 1px solid var(--color-grey-200);
}

.login-tips {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-3);
}

.tip-item {
  display: flex;
  align-items: center;
  gap: var(--spacing-2);
  font-size: var(--font-size-body2);
  color: var(--color-text-secondary);
}

.tip-icon {
  color: var(--color-primary);
  flex-shrink: 0;
}

/* 响应式设计 */
@media (max-width: 1024px) {
  .login-wrapper {
    grid-template-columns: 1fr;
    gap: var(--spacing-8);
    max-width: 500px;
  }
  
  .brand-section {
    text-align: center;
  }
  
  .brand-title {
    font-size: 2.5rem;
  }
}

@media (max-width: 768px) {
  .login-content {
    padding: var(--spacing-4);
  }
  
  .form-container {
    padding: var(--spacing-6);
  }
  
  .brand-title {
    font-size: 2rem;
  }
  
  .brand-subtitle {
    font-size: var(--font-size-h4);
  }
}

@media (max-width: 480px) {
  .login-content {
    padding: var(--spacing-3);
  }
  
  .form-container {
    padding: var(--spacing-4);
  }
  
  .form-item {
    margin-bottom: var(--spacing-4);
  }
}

/* Element Plus 表单项样式覆盖 */
.form-item :deep(.el-form-item__error) {
  font-size: var(--font-size-caption);
  color: var(--color-feedback-error);
  margin-top: var(--spacing-1);
}

.form-item :deep(.el-form-item__content) {
  line-height: normal;
}
</style> 