<template>
  <AdminLayout>
    <div class="admin-users">
      <!-- 页面头部 -->
      <div class="page-header">
        <h1>User Management</h1>
        <p>Manage system users and permissions</p>
      </div>

    <!-- 搜索和筛选 -->
    <el-card class="filter-card" shadow="hover">
      <div class="filter-bar">
        <div class="filter-left">
          <el-input
            v-model="searchKeyword"
            placeholder="搜索用户名或邮箱"
            style="width: 300px"
            clearable
            @change="handleSearch"
          >
            <template #prefix>
              <el-icon><Search /></el-icon>
            </template>
          </el-input>
          <el-select
            v-model="filterRole"
            placeholder="筛选角色"
            style="width: 150px"
            clearable
            @change="handleSearch"
          >
            <el-option label="全部" value="" />
            <el-option label="管理员" value="admin" />
            <el-option label="普通用户" value="user" />
          </el-select>
        </div>
        <div class="filter-right">
          <el-button type="success" @click="handleAdd">
            <el-icon><Plus /></el-icon>
            添加用户
          </el-button>
          <el-button type="primary" @click="refreshData">
            <el-icon><Refresh /></el-icon>
            刷新
          </el-button>
        </div>
      </div>
    </el-card>

    <!-- 用户列表 -->
    <el-card class="table-card" shadow="hover">
      <el-table
        v-loading="loading"
        :data="userList"
        style="width: 100%"
        row-key="user_id"
        :default-sort="{ prop: 'create_time', order: 'descending' }"
      >
        <el-table-column prop="user_id" label="ID" width="80" />
        <el-table-column prop="username" label="用户名" width="150" />
        <el-table-column prop="email" label="邮箱" min-width="200" />
        <el-table-column prop="role" label="角色" width="120">
          <template #default="{ row }">
            <el-tag :type="row.role === 'admin' ? 'danger' : 'info'">
              {{ row.role === 'admin' ? '管理员' : '普通用户' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="120">
          <template #default="{ row }">
            <el-switch
              v-model="row.status"
              :active-value="1"
              :inactive-value="0"
              active-text="启用"
              inactive-text="禁用"
              @change="handleStatusChange(row)"
            />
          </template>
        </el-table-column>
        <el-table-column prop="paper_count" label="文献数量" width="120" />
        <el-table-column prop="last_login" label="最后登录" width="180">
          <template #default="{ row }">
            {{ formatTime(row.last_login) || '从未登录' }}
          </template>
        </el-table-column>
        <el-table-column prop="create_time" label="注册时间" width="180">
          <template #default="{ row }">
            {{ formatTime(row.create_time) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button
              size="small"
              type="primary"
              @click="handleEdit(row)"
            >
              编辑
            </el-button>
            <el-button
              size="small"
              type="danger"
              @click="handleDelete(row)"
              :disabled="row.role === 'admin' && row.user_id === currentUserId"
            >
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <div class="pagination-container">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :page-sizes="[10, 20, 50, 100]"
          :total="total"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>
    </el-card>

    <!-- 用户编辑对话框 -->
    <UserEditDialog
      v-model:visible="editDialogVisible"
      :user="currentUser"
      :mode="dialogMode"
      @refresh="refreshData"
    />
    </div>
  </AdminLayout>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Search, Refresh, Plus } from '@element-plus/icons-vue'
import { getAdminUsers, updateUserStatus, deleteUser } from '@/api/admin'
import UserEditDialog from '@/components/UserEditDialog.vue'
import AdminLayout from '@/components/AdminLayout.vue'

// 响应式数据
const loading = ref(false)
const userList = ref([])
const total = ref(0)
const currentPage = ref(1)
const pageSize = ref(20)
const searchKeyword = ref('')
const filterRole = ref('')
const editDialogVisible = ref(false)
const currentUser = ref({})
const currentUserId = ref(null) // 当前登录用户ID
const dialogMode = ref('add') // 对话框模式：'add' 或 'edit'

// 加载用户列表
const loadUsers = async () => {
  try {
    loading.value = true
    const params = {
      page: currentPage.value,
      limit: pageSize.value,
      search: searchKeyword.value,
      role: filterRole.value
    }
    
    const response = await getAdminUsers(params)
    if (response.success) {
      userList.value = response.data.items || []
      total.value = response.data.pagination.total || 0
    } else {
      ElMessage.error(response.error || '获取用户列表失败')
    }
  } catch (error) {
    console.error('获取用户列表失败:', error)
    ElMessage.error('获取用户列表失败')
  } finally {
    loading.value = false
  }
}

// 搜索处理
const handleSearch = () => {
  currentPage.value = 1
  loadUsers()
}

// 刷新数据
const refreshData = () => {
  loadUsers()
}

// 分页大小改变
const handleSizeChange = (size) => {
  pageSize.value = size
  currentPage.value = 1
  loadUsers()
}

// 页码改变
const handleCurrentChange = (page) => {
  currentPage.value = page
  loadUsers()
}

// 状态切换
const handleStatusChange = async (row) => {
  try {
    const response = await updateUserStatus(row.user_id, { status: row.status })
    if (response.success) {
      ElMessage.success('用户状态更新成功')
    } else {
      // 回滚状态
      row.status = row.status === 1 ? 0 : 1
      ElMessage.error(response.error || '更新用户状态失败')
    }
  } catch (error) {
    // 回滚状态
    row.status = row.status === 1 ? 0 : 1
    console.error('更新用户状态失败:', error)
    ElMessage.error('更新用户状态失败')
  }
}

// 编辑用户
const handleEdit = (row) => {
  currentUser.value = { ...row }
  dialogMode.value = 'edit'
  editDialogVisible.value = true
}

// 添加用户
const handleAdd = () => {
  currentUser.value = {} // 清空当前用户数据，表示添加新用户
  dialogMode.value = 'add'
  editDialogVisible.value = true
}

// 删除用户
const handleDelete = async (row) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除用户 "${row.username}" 吗？此操作不可撤销。`,
      '删除确认',
      {
        confirmButtonText: '确定删除',
        cancelButtonText: '取消',
        type: 'warning',
        confirmButtonClass: 'el-button--danger'
      }
    )

    const response = await deleteUser(row.user_id)
    if (response.success) {
      ElMessage.success('用户删除成功')
      refreshData()
    } else {
      ElMessage.error(response.error || '删除用户失败')
    }
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除用户失败:', error)
      ElMessage.error('删除用户失败')
    }
  }
}

// 格式化时间
const formatTime = (time) => {
  if (!time) return ''
  return new Date(time).toLocaleString('zh-CN')
}

onMounted(() => {
  // 获取当前用户ID（从本地存储或状态管理中获取）
  const userInfo = JSON.parse(localStorage.getItem('userInfo') || '{}')
  currentUserId.value = userInfo.user_id
  
  loadUsers()
})
</script>

<style scoped>
.admin-users {
  padding: 20px;
  max-width: 1400px;
  margin: 0 auto;
}

.page-header {
  margin-bottom: 20px;
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-left h1 {
  color: #2c3e50;
  margin-bottom: 5px;
}

.header-left p {
  color: #7f8c8d;
  margin: 0;
}

.header-right {
  display: flex;
  gap: 10px;
}

.filter-card {
  margin-bottom: 20px;
}

.filter-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 15px;
  flex-wrap: wrap;
}

.filter-left {
  display: flex;
  gap: 15px;
  align-items: center;
  flex-wrap: wrap;
}

.filter-right {
  display: flex;
  gap: 10px;
}

.table-card {
  border-radius: 8px;
}

.pagination-container {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}

/* 移动端适配 */
@media (max-width: 768px) {
  .admin-users {
    padding: 10px;
  }
  
  .header-content {
    flex-direction: column;
    align-items: stretch;
  }

  .header-left,
  .header-right {
    width: 100%;
    justify-content: flex-start;
  }

  .filter-bar {
    flex-direction: column;
    align-items: stretch;
  }
  
  .filter-left,
  .filter-right {
    width: 100%;
    justify-content: flex-start;
  }
}
</style> 