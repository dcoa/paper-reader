<template>
  <AdminLayout>
    <div class="admin-dashboard">
      <!-- 头部 -->
      <div class="dashboard-header">
        <h1>Admin Dashboard</h1>
        <p>Welcome to PaperReader Management System</p>
      </div>

    <!-- 统计卡片 -->
    <div class="stats-grid">
      <el-card class="stat-card" shadow="hover">
        <div class="stat-content">
          <div class="stat-icon user-icon">
            <el-icon size="32"><User /></el-icon>
          </div>
          <div class="stat-info">
            <h3>{{ statistics.total_users || 0 }}</h3>
            <p>Total Users</p>
          </div>
        </div>
      </el-card>

      <el-card class="stat-card" shadow="hover">
        <div class="stat-content">
          <div class="stat-icon paper-icon">
            <el-icon size="32"><Document /></el-icon>
          </div>
          <div class="stat-info">
            <h3>{{ statistics.total_papers || 0 }}</h3>
            <p>Total Papers</p>
          </div>
        </div>
      </el-card>

      <el-card class="stat-card" shadow="hover">
        <div class="stat-content">
          <div class="stat-icon annotation-icon">
            <el-icon size="32"><ChatLineRound /></el-icon>
          </div>
          <div class="stat-info">
            <h3>{{ statistics.total_annotations || 0 }}</h3>
            <p>Total Annotations</p>
          </div>
        </div>
      </el-card>

      <el-card class="stat-card" shadow="hover">
        <div class="stat-content">
          <div class="stat-icon active-icon">
            <el-icon size="32"><Trophy /></el-icon>
          </div>
          <div class="stat-info">
            <h3>{{ (statistics.active_users && statistics.active_users.length) || 0 }}</h3>
            <p>Active Users</p>
          </div>
        </div>
      </el-card>
    </div>

    <!-- 功能模块 -->
    <div class="feature-grid">
      <el-card class="feature-card" shadow="hover" @click="navigateTo('/admin/users')">
        <div class="feature-content">
          <el-icon size="48" class="feature-icon"><UserFilled /></el-icon>
          <h3>User Management</h3>
          <p>Manage system users, view user information, and set permissions</p>
        </div>
      </el-card>

      <el-card class="feature-card" shadow="hover" @click="navigateTo('/admin/papers')">
        <div class="feature-content">
          <el-icon size="48" class="feature-icon"><FolderOpened /></el-icon>
          <h3>Paper Management</h3>
          <p>Manage papers, edit information, delete or restore papers</p>
        </div>
      </el-card>
    </div>

    <!-- 详细信息 -->
    <div class="info-grid">
      <!-- 活跃用户列表 -->
      <el-card class="info-card" shadow="hover">
        <template #header>
          <span>Active Users</span>
        </template>
        <div v-if="loading" class="loading-container">
          <el-skeleton :rows="3" animated />
        </div>
        <div v-else>
          <div class="user-item" v-for="user in statistics.active_users" :key="user.username">
            <div class="user-info">
              <strong>{{ user.username }}</strong>
              <div class="user-stats">
                <span class="stat-badge">{{ user.paper_count }} papers</span>
                <span class="stat-badge">{{ user.annotation_count }} annotations</span>
              </div>
            </div>
          </div>
          <div v-if="!statistics.active_users || !statistics.active_users.length" class="no-data">
            No active users
          </div>
        </div>
      </el-card>

      <!-- 文献类型分布 -->
      <el-card class="info-card" shadow="hover">
        <template #header>
          <span>Paper Type Distribution</span>
        </template>
        <div v-if="loading" class="loading-container">
          <el-skeleton :rows="3" animated />
        </div>
        <div v-else>
          <div class="type-item" v-for="type in statistics.paper_types" :key="type.type_name">
            <div class="type-info">
              <span class="type-name">{{ type.type_name }}</span>
              <span class="type-count">{{ type.count }} papers</span>
            </div>
            <div class="type-bar">
              <div class="type-progress" :style="{ width: getTypePercentage(type.count) + '%' }"></div>
            </div>
          </div>
          <div v-if="!statistics.paper_types || !statistics.paper_types.length" class="no-data">
            No paper type data
          </div>
        </div>
      </el-card>
    </div>

    <!-- 最近活动 -->
    <el-card class="recent-activity" shadow="hover">
      <template #header>
        <span>Recent Activity</span>
      </template>
      <div v-if="loading" class="loading-container">
        <el-skeleton :rows="5" animated />
      </div>
      <div v-else>
        <div class="activity-item" v-for="item in recentActivity" :key="item.id">
          <el-tag :type="getActivityType(item.type)">{{ item.type }}</el-tag>
          <span class="activity-desc">{{ item.description }}</span>
          <span class="activity-time">{{ formatTime(item.time) }}</span>
        </div>
        <div v-if="!recentActivity.length" class="no-data">
          No recent activity
        </div>
      </div>
    </el-card>
    </div>
  </AdminLayout>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import {
  User,
  Document,
  ChatLineRound,
  Trophy,
  UserFilled,
  FolderOpened
} from '@element-plus/icons-vue'
import { getStatistics } from '@/api/admin'
import AdminLayout from '@/components/AdminLayout.vue'

const router = useRouter()
const loading = ref(false)
const statistics = ref({})
const recentActivity = ref([])

// 导航到指定页面
const navigateTo = (path) => {
  router.push(path)
}

// 获取活动类型样式
const getActivityType = (type) => {
  const typeMap = {
    '用户注册': 'success',
    '文献上传': 'primary',
    '文献删除': 'danger',
    '批注创建': 'info'
  }
  return typeMap[type] || 'info'
}

// 格式化时间
const formatTime = (time) => {
  return new Date(time).toLocaleString('zh-CN')
}

// 获取文献类型百分比
const getTypePercentage = (count) => {
  if (!statistics.value.paper_types || !statistics.value.paper_types.length) return 0
  const maxCount = Math.max(...statistics.value.paper_types.map(type => type.count))
  return maxCount > 0 ? (count / maxCount) * 100 : 0
}

// 加载统计数据
const loadStatistics = async () => {
  try {
    loading.value = true
    const response = await getStatistics()
    if (response.success) {
      statistics.value = response.data
      // 模拟最近活动数据（实际可以从后端获取）
      recentActivity.value = [
        {
          id: 1,
          type: '用户注册',
          description: '新用户 test_user 注册成功',
          time: new Date().toISOString()
        },
        {
          id: 2,
          type: '文献上传',
          description: '用户 admin 上传了新文献',
          time: new Date(Date.now() - 3600000).toISOString()
        }
      ]
    } else {
      ElMessage.error(response.error || '获取统计数据失败')
    }
  } catch (error) {
    console.error('获取统计数据失败:', error)
    ElMessage.error('获取统计数据失败')
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadStatistics()
})
</script>

<style scoped>
.admin-dashboard {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
}

.dashboard-header {
  text-align: center;
  margin-bottom: 30px;
}

.dashboard-header h1 {
  color: #2c3e50;
  margin-bottom: 10px;
}

.dashboard-header p {
  color: #7f8c8d;
  font-size: 16px;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 20px;
  margin-bottom: 30px;
}

.stat-card {
  border-radius: 8px;
  transition: transform 0.2s;
}

.stat-card:hover {
  transform: translateY(-5px);
}

.stat-content {
  display: flex;
  align-items: center;
  gap: 15px;
}

.stat-icon {
  width: 60px;
  height: 60px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
}

.user-icon {
  background: linear-gradient(45deg, #667eea 0%, #764ba2 100%);
}

.paper-icon {
  background: linear-gradient(45deg, #f093fb 0%, #f5576c 100%);
}

.annotation-icon {
  background: linear-gradient(45deg, #4facfe 0%, #00f2fe 100%);
}

.active-icon {
  background: linear-gradient(45deg, #43e97b 0%, #38f9d7 100%);
}

.stat-info h3 {
  font-size: 28px;
  font-weight: bold;
  margin: 0;
  color: #2c3e50;
}

.stat-info p {
  margin: 5px 0 0 0;
  color: #7f8c8d;
  font-size: 14px;
}

.feature-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 20px;
  margin-bottom: 30px;
}

.feature-card {
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s;
}

.feature-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 8px 25px rgba(0,0,0,0.15);
}

.feature-content {
  text-align: center;
  padding: 20px;
}

.feature-icon {
  color: #409eff;
  margin-bottom: 15px;
}

.feature-content h3 {
  color: #2c3e50;
  margin: 15px 0 10px 0;
}

.feature-content p {
  color: #7f8c8d;
  line-height: 1.5;
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
  gap: 20px;
  margin-bottom: 30px;
}

.info-card {
  border-radius: 8px;
}

.user-item {
  padding: 12px 0;
  border-bottom: 1px solid #f0f0f0;
}

.user-item:last-child {
  border-bottom: none;
}

.user-info {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.user-stats {
  display: flex;
  gap: 10px;
}

.stat-badge {
  background: #f0f9ff;
  color: #0369a1;
  padding: 2px 8px;
  border-radius: 12px;
  font-size: 12px;
  border: 1px solid #e0f2fe;
}

.type-item {
  margin-bottom: 15px;
}

.type-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.type-name {
  font-weight: 500;
  color: #2c3e50;
}

.type-count {
  color: #7f8c8d;
  font-size: 14px;
}

.type-bar {
  width: 100%;
  height: 6px;
  background: #f0f0f0;
  border-radius: 3px;
  overflow: hidden;
}

.type-progress {
  height: 100%;
  background: linear-gradient(45deg, #409eff 0%, #67c23a 100%);
  transition: width 0.3s ease;
}

.recent-activity {
  border-radius: 8px;
}

.loading-container {
  padding: 20px;
}

.activity-item {
  display: flex;
  align-items: center;
  gap: 15px;
  padding: 12px 0;
  border-bottom: 1px solid #f0f0f0;
}

.activity-item:last-child {
  border-bottom: none;
}

.activity-desc {
  flex: 1;
  color: #2c3e50;
}

.activity-time {
  color: #7f8c8d;
  font-size: 12px;
}

.no-data {
  text-align: center;
  color: #7f8c8d;
  padding: 40px;
}
</style> 