<template>
  <div class="home-container">
    <el-container>
      <!-- 头部导航 -->
      <el-header class="navbar">
        <div class="navbar__content">
          <div class="navbar__brand">
            <h1 class="brand-logo">PaperReader</h1>
            <span class="brand-tagline">Research Paper Management Platform</span>
          </div>
          <div class="navbar__user">
            <el-dropdown @command="handleUserAction" trigger="click">
              <el-button link class="user-button">
                <el-icon class="user-icon"><User /></el-icon>
                <span class="username">{{ userStore.username || 'User' }}</span>
                <el-icon class="dropdown-icon"><arrow-down /></el-icon>
              </el-button>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item command="profile">Profile</el-dropdown-item>
                  <el-dropdown-item command="logout" divided>Logout</el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </div>
        </div>
      </el-header>

      <el-container>
        <!-- 侧边栏 -->
        <el-aside width="260px" class="sidebar">
          <nav class="sidebar-nav">
            <el-menu
              :default-active="activeMenu"
              class="sidebar-menu"
              @select="handleMenuSelect"
            >
              <el-menu-item index="/home">
                <el-icon><house /></el-icon>
                <span>Home</span>
              </el-menu-item>
              <el-menu-item index="/papers">
                <el-icon><document /></el-icon>
                <span>Papers</span>
              </el-menu-item>
              <el-menu-item index="/upload">
                <el-icon><upload-filled /></el-icon>
                <span>Upload Paper</span>
              </el-menu-item>


              <!-- Admin Menu -->
              <el-sub-menu v-if="userStore.isAdmin" index="admin" class="admin-menu">
                <template #title>
                  <el-icon><user-filled /></el-icon>
                  <span>Admin Panel</span>
                </template>
                <el-menu-item index="/admin/dashboard">
                  <el-icon><monitor /></el-icon>
                  <span>Dashboard</span>
                </el-menu-item>
                <el-menu-item index="/admin/users">
                  <el-icon><user /></el-icon>
                  <span>User Management</span>
                </el-menu-item>
                <el-menu-item index="/admin/papers">
                  <el-icon><folder-opened /></el-icon>
                  <span>Paper Management</span>
                </el-menu-item>
              </el-sub-menu>
            </el-menu>
          </nav>
        </el-aside>

        <!-- 主要内容区域 -->
        <el-main class="main-content">
          <!-- Welcome Section -->
          <section class="welcome-section">
            <div class="welcome-card">
              <div class="welcome-header">
                <h2 class="welcome-title">Welcome Back!</h2>
                <p class="welcome-subtitle">Manage your research papers and improve research efficiency</p>
              </div>

              <!-- Statistics Cards -->
              <div class="stats-grid">
                <div class="stat-card stat-card--primary">
                  <div class="stat-icon">
                    <el-icon size="32"><document /></el-icon>
                  </div>
                  <div class="stat-content">
                    <h3 class="stat-number">{{ stats.totalPapers }}</h3>
                    <p class="stat-label">Total Papers</p>
                  </div>
                </div>

                <div class="stat-card stat-card--success">
                  <div class="stat-icon">
                    <el-icon size="32"><edit /></el-icon>
                  </div>
                  <div class="stat-content">
                    <h3 class="stat-number">{{ stats.totalAnnotations }}</h3>
                    <p class="stat-label">Total Annotations</p>
                  </div>
                </div>

                <div class="stat-card stat-card--warning">
                  <div class="stat-icon">
                    <el-icon size="32"><chat-dot-round /></el-icon>
                  </div>
                  <div class="stat-content">
                    <h3 class="stat-number">{{ stats.totalConversations }}</h3>
                    <p class="stat-label">AI Conversations</p>
                  </div>
                </div>
              </div>
            </div>
          </section>

          <!-- Quick Actions Section -->
          <section class="actions-section">
            <div class="actions-card">
              <h3 class="actions-title">Quick Actions</h3>
              <div class="actions-grid">
                <button
                  class="action-button action-button--primary"
                  @click="$router.push('/upload')"
                >
                  <el-icon size="24"><upload-filled /></el-icon>
                  <span class="action-text">Upload Paper</span>
                  <span class="action-description">Add new research papers</span>
                </button>

                <button
                  class="action-button action-button--secondary"
                  @click="$router.push('/papers')"
                >
                  <el-icon size="24"><document /></el-icon>
                  <span class="action-text">Browse Papers</span>
                  <span class="action-description">View existing papers</span>
                </button>

                <button
                  class="action-button action-button--outline"
                  @click="refreshStats"
                >
                  <el-icon size="24"><refresh /></el-icon>
                  <span class="action-text">Refresh Stats</span>
                  <span class="action-description">Update latest data</span>
                </button>
              </div>
            </div>
          </section>
        </el-main>
      </el-container>
    </el-container>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useUserStore } from '@/store/user'
import { getPapersList, getUserPaperStatistics } from '@/api/papers'
import { logout } from '@/api/auth'

const router = useRouter()
const route = useRoute()
const userStore = useUserStore()

// 统计数据
const stats = reactive({
  totalPapers: 0,
  totalAnnotations: 0,
  totalConversations: 0
})

// 当前活动的菜单项
const activeMenu = computed(() => {
  return route.path
})

// 处理菜单选择
const handleMenuSelect = (index) => {
  if (index !== route.path) {
    router.push(index)
  }
}

// Handle user actions
const handleUserAction = async (command) => {
  switch (command) {
    case 'profile':
      ElMessage.info('Profile feature is under development...')
      break
    case 'logout':
      try {
        await ElMessageBox.confirm('Are you sure you want to logout?', 'Confirm', {
          confirmButtonText: 'Yes',
          cancelButtonText: 'No',
          type: 'warning'
        })

        // Call logout API
        try {
          await logout()
        } catch (error) {
          console.error('Logout API error:', error)
          // Continue with local logout even if API fails
        }

        // Clear local user data
        userStore.logout()
        ElMessage.success('Logged out successfully')
        router.push('/login')
      } catch {
        // User cancelled operation
      }
      break
  }
}

// Refresh statistics
const refreshStats = async () => {
  try {
    // Get real user statistics
    const response = await getUserPaperStatistics()
    if (response.success) {
      stats.totalPapers = response.data.total_papers || 0
      stats.totalAnnotations = response.data.total_annotations || 0
      stats.totalConversations = response.data.total_conversations || 0
      ElMessage.success('Statistics refreshed')
    } else {
      ElMessage.error(response.error || 'Failed to refresh statistics')
    }
  } catch (error) {
    console.error('Failed to refresh statistics:', error)
    ElMessage.error('Failed to refresh statistics')
  }
}

// 组件挂载时获取统计数据
onMounted(() => {
  refreshStats()
})
</script>

<style scoped>
.home-container {
  min-height: 100vh;
  width: 100%;
  box-sizing: border-box;
  background-color: var(--color-background-default);
}

/* 导航栏样式 */
.navbar {
  background-color: var(--color-background-paper);
  border-bottom: 1px solid var(--color-grey-200);
  box-shadow: var(--shadow-sm);
  padding: 0;
}

.navbar__content {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 var(--spacing-6);
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.navbar__brand {
  display: flex;
  align-items: center;
  gap: var(--spacing-3);
}

.brand-logo {
  margin: 0;
  font-size: var(--font-size-h3);
  font-weight: var(--font-weight-bold);
  color: var(--color-primary);
}

.brand-tagline {
  font-size: var(--font-size-caption);
  color: var(--color-text-secondary);
  font-weight: var(--font-weight-medium);
}

.user-button {
  display: flex;
  align-items: center;
  gap: var(--spacing-2);
  padding: var(--spacing-2) var(--spacing-3);
  border-radius: var(--border-radius);
  transition: all var(--transition-fast);
}

.user-button:hover {
  background-color: var(--color-grey-100);
}

.user-icon {
  color: var(--color-primary);
}

.username {
  font-weight: var(--font-weight-medium);
  color: var(--color-text-primary);
}

.dropdown-icon {
  color: var(--color-text-secondary);
  font-size: 12px;
}

/* 侧边栏样式 */
.sidebar {
  background-color: var(--color-background-paper);
  border-right: 1px solid var(--color-grey-200);
}

.sidebar-nav {
  padding: var(--spacing-4);
}

.sidebar-menu {
  border-right: none;
  background-color: transparent;
}

.sidebar-menu .el-menu-item {
  margin-bottom: var(--spacing-1);
  border-radius: var(--border-radius);
  font-weight: var(--font-weight-medium);
  color: var(--color-text-secondary);
  transition: all var(--transition-fast);
}

.sidebar-menu .el-menu-item:hover {
  background-color: var(--color-primary-light);
  color: var(--color-primary-dark);
}

.sidebar-menu .el-menu-item.is-active {
  background-color: var(--color-primary);
  color: white;
}

/* 主内容区域 */
.main-content {
  background-color: var(--color-background-default);
  padding: var(--spacing-8);
}

/* 欢迎区域 */
.welcome-section {
  margin-bottom: var(--spacing-8);
}

.welcome-card {
  background-color: var(--color-background-paper);
  border-radius: var(--border-radius-xl);
  padding: var(--spacing-8);
  box-shadow: var(--shadow-md);
  border: 1px solid var(--color-grey-200);
}

.welcome-header {
  text-align: center;
  margin-bottom: var(--spacing-8);
}

.welcome-title {
  margin: 0 0 var(--spacing-2) 0;
  font-size: var(--font-size-h2);
  font-weight: var(--font-weight-bold);
  color: var(--color-text-primary);
}

.welcome-subtitle {
  margin: 0;
  font-size: var(--font-size-body1);
  color: var(--color-text-secondary);
}

/* 统计卡片网格 */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: var(--spacing-6);
}

.stat-card {
  display: flex;
  align-items: center;
  gap: var(--spacing-4);
  padding: var(--spacing-6);
  background-color: var(--color-background-paper);
  border-radius: var(--border-radius-lg);
  border: 1px solid var(--color-grey-200);
  transition: all var(--transition-normal);
  position: relative;
  overflow: hidden;
}

.stat-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  width: 4px;
  height: 100%;
  background-color: var(--color-primary);
}

.stat-card--primary::before {
  background-color: var(--color-primary);
}

.stat-card--success::before {
  background-color: var(--color-feedback-success);
}

.stat-card--warning::before {
  background-color: var(--color-feedback-warning);
}

.stat-card:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-lg);
}

.stat-icon {
  flex-shrink: 0;
  color: var(--color-primary);
}

.stat-card--success .stat-icon {
  color: var(--color-feedback-success);
}

.stat-card--warning .stat-icon {
  color: var(--color-feedback-warning);
}

.stat-content {
  flex: 1;
}

.stat-number {
  margin: 0 0 var(--spacing-1) 0;
  font-size: var(--font-size-h2);
  font-weight: var(--font-weight-bold);
  color: var(--color-text-primary);
}

.stat-label {
  margin: 0;
  font-size: var(--font-size-body2);
  color: var(--color-text-secondary);
  font-weight: var(--font-weight-medium);
}

/* 快速操作区域 */
.actions-section {
  margin-top: var(--spacing-8);
}

.actions-card {
  background-color: var(--color-background-paper);
  border-radius: var(--border-radius-xl);
  padding: var(--spacing-8);
  box-shadow: var(--shadow-md);
  border: 1px solid var(--color-grey-200);
}

.actions-title {
  margin: 0 0 var(--spacing-6) 0;
  font-size: var(--font-size-h3);
  font-weight: var(--font-weight-semibold);
  color: var(--color-text-primary);
}

.actions-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: var(--spacing-6);
}

.action-button {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  padding: var(--spacing-8) var(--spacing-6);
  background: none;
  border: 2px solid var(--color-grey-200);
  border-radius: var(--border-radius-lg);
  cursor: pointer;
  transition: all var(--transition-normal);
  text-decoration: none;
  color: inherit;
  gap: var(--spacing-3);
}

.action-button--primary {
  border-color: var(--color-primary);
  background-color: var(--color-primary-light);
}

.action-button--primary:hover {
  border-color: var(--color-primary-dark);
  background-color: var(--color-primary);
  color: white;
  transform: translateY(-2px);
  box-shadow: var(--shadow-lg);
}

.action-button--secondary {
  border-color: var(--color-feedback-success);
  background-color: rgba(56, 142, 60, 0.1);
}

.action-button--secondary:hover {
  border-color: var(--color-feedback-success);
  background-color: var(--color-feedback-success);
  color: white;
  transform: translateY(-2px);
  box-shadow: var(--shadow-lg);
}

.action-button--outline:hover {
  border-color: var(--color-primary);
  background-color: var(--color-primary-light);
  transform: translateY(-2px);
  box-shadow: var(--shadow-lg);
}

.action-text {
  font-size: var(--font-size-h4);
  font-weight: var(--font-weight-semibold);
  color: inherit;
}

.action-description {
  font-size: var(--font-size-body2);
  color: var(--color-text-secondary);
  font-weight: var(--font-weight-regular);
}

.action-button:hover .action-description {
  color: inherit;
  opacity: 0.9;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .navbar__content {
    padding: 0 var(--spacing-4);
  }
  
  .brand-tagline {
    display: none;
  }
  
  .main-content {
    padding: var(--spacing-4);
  }
  
  .welcome-card,
  .actions-card {
    padding: var(--spacing-6);
  }
  
  .stats-grid {
    grid-template-columns: 1fr;
    gap: var(--spacing-4);
  }
  
  .stat-card {
    padding: var(--spacing-4);
  }
  
  .actions-grid {
    grid-template-columns: 1fr;
    gap: var(--spacing-4);
  }
  
  .action-button {
    padding: var(--spacing-6) var(--spacing-4);
  }
}

@media (max-width: 480px) {
  .el-aside {
    display: none;
  }
}
</style> 