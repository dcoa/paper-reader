<template>
  <div class="admin-layout">
    <!-- 顶部导航栏 -->
    <el-header class="admin-header">
      <div class="header-content">
        <div class="header-left">
          <h1 class="brand-logo">PaperReader Admin</h1>
          <span class="brand-tagline">Management Console</span>
        </div>
        <div class="header-right">
          <el-dropdown @command="handleUserAction" trigger="click">
            <el-button link class="user-button">
              <el-icon class="user-icon"><User /></el-icon>
              <span class="username">{{ userStore.username || 'Admin' }}</span>
              <el-icon class="dropdown-icon"><ArrowDown /></el-icon>
            </el-button>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="logout" divided>
                  <el-icon><SwitchButton /></el-icon>
                  Logout
                </el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </div>
    </el-header>

    <!-- 侧边导航 -->
    <el-container class="admin-container">
      <el-aside width="200px" class="admin-sidebar">
        <el-menu
          :default-active="activeMenu"
          class="admin-menu"
          router
        >
          <el-menu-item index="/admin/dashboard">
            <el-icon><Monitor /></el-icon>
            <span>Dashboard</span>
          </el-menu-item>
          <el-menu-item index="/admin/users">
            <el-icon><User /></el-icon>
            <span>User Management</span>
          </el-menu-item>
          <el-menu-item index="/admin/papers">
            <el-icon><FolderOpened /></el-icon>
            <span>Paper Management</span>
          </el-menu-item>
          <el-menu-item index="/home">
            <el-icon><HomeFilled /></el-icon>
            <span>Back to Home</span>
          </el-menu-item>
        </el-menu>
      </el-aside>

      <!-- 主内容区 -->
      <el-main class="admin-main">
        <slot></slot>
      </el-main>
    </el-container>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useUserStore } from '@/store/user'
import { ElMessage, ElMessageBox } from 'element-plus'
import { 
  User, 
  ArrowDown, 
  SwitchButton, 
  Monitor, 
  FolderOpened,
  HomeFilled
} from '@element-plus/icons-vue'
import { logout } from '@/api/auth'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()

// 当前激活的菜单
const activeMenu = computed(() => route.path)

// 处理用户操作
const handleUserAction = async (command) => {
  if (command === 'logout') {
    try {
      await ElMessageBox.confirm('Are you sure you want to logout?', 'Confirm', {
        confirmButtonText: 'Yes',
        cancelButtonText: 'No',
        type: 'warning'
      })

      // 调用登出 API
      try {
        await logout()
      } catch (error) {
        console.error('Logout API error:', error)
        // 即使 API 失败也继续本地登出
      }

      // 清除本地用户数据
      userStore.logout()
      ElMessage.success('Logged out successfully')
      router.push('/login')
    } catch {
      // 用户取消操作
    }
  }
}
</script>

<style scoped>
.admin-layout {
  height: 100vh;
  display: flex;
  flex-direction: column;
  background-color: #f5f7fa;
}

.admin-header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 0 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  height: 60px;
  display: flex;
  align-items: center;
}

.header-content {
  width: 100%;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-left {
  display: flex;
  align-items: baseline;
  gap: 12px;
}

.brand-logo {
  font-size: 24px;
  font-weight: 700;
  margin: 0;
  color: white;
}

.brand-tagline {
  font-size: 14px;
  color: rgba(255, 255, 255, 0.9);
  font-weight: 400;
}

.header-right {
  display: flex;
  align-items: center;
}

.user-button {
  color: white;
  font-size: 14px;
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  border-radius: 8px;
  transition: background-color 0.3s;
}

.user-button:hover {
  background-color: rgba(255, 255, 255, 0.1);
}

.user-icon {
  font-size: 18px;
}

.username {
  font-weight: 500;
}

.dropdown-icon {
  font-size: 14px;
  margin-left: 4px;
}

.admin-container {
  flex: 1;
  overflow: hidden;
}

.admin-sidebar {
  background-color: white;
  box-shadow: 2px 0 8px rgba(0, 0, 0, 0.05);
  overflow-y: auto;
}

.admin-menu {
  border-right: none;
  padding: 10px 0;
}

.admin-menu .el-menu-item {
  margin: 4px 8px;
  border-radius: 8px;
  transition: all 0.3s;
}

.admin-menu .el-menu-item:hover {
  background-color: #f0f2f5;
}

.admin-menu .el-menu-item.is-active {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.admin-menu .el-menu-item.is-active .el-icon {
  color: white;
}

.admin-main {
  background-color: #f5f7fa;
  overflow-y: auto;
  padding: 20px;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .admin-sidebar {
    width: 60px !important;
  }

  .admin-menu .el-menu-item span {
    display: none;
  }

  .brand-tagline {
    display: none;
  }
}
</style>

