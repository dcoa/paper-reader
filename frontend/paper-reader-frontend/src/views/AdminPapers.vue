<template>
  <AdminLayout>
    <div class="admin-papers">
      <!-- 页面头部 -->
      <div class="page-header">
        <h1>Paper Management</h1>
        <p>Manage system papers and status</p>
      </div>

    <!-- 搜索和筛选 -->
    <el-card class="filter-card" shadow="hover">
      <div class="filter-bar">
        <div class="filter-left">
          <el-input
            v-model="searchKeyword"
            placeholder="搜索文献标题或作者"
            style="width: 300px"
            clearable
            @change="handleSearch"
          >
            <template #prefix>
              <el-icon><Search /></el-icon>
            </template>
          </el-input>
          <el-select
            v-model="filterType"
            placeholder="筛选文献类型"
            style="width: 150px"
            clearable
            @change="handleSearch"
          >
            <el-option label="全部" value="" />
            <el-option label="期刊" value="1" />
            <el-option label="会议" value="2" />
            <el-option label="书籍" value="3" />
            <el-option label="报告" value="4" />
            <el-option label="学位论文" value="5" />
          </el-select>
          <el-select
            v-model="filterStatus"
            placeholder="筛选状态"
            style="width: 120px"
            clearable
            @change="handleSearch"
          >
            <el-option label="全部" value="" />
            <el-option label="正常" value="1" />
            <el-option label="已删除" value="0" />
          </el-select>
        </div>
        <div class="filter-right">
          <el-button type="primary" @click="refreshData">
            <el-icon><Refresh /></el-icon>
            刷新
          </el-button>
        </div>
      </div>
    </el-card>

    <!-- 文献列表 -->
    <el-card class="table-card" shadow="hover">
      <el-table
        v-loading="loading"
        :data="paperList"
        style="width: 100%"
        row-key="paper_id"
        :default-sort="{ prop: 'upload_time', order: 'descending' }"
      >
        <el-table-column prop="paper_id" label="ID" width="80" />
        <el-table-column prop="title" label="文献标题" min-width="250" show-overflow-tooltip />
        <el-table-column prop="authors" label="作者" width="150" show-overflow-tooltip />
        <el-table-column prop="publication_type" label="文献类型" width="120">
          <template #default="{ row }">
            <el-tag :type="getTypeColor(row.publication_type)">
              {{ row.publication_type || '未分类' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="publication_name" label="期刊/会议" width="150" show-overflow-tooltip />
        <el-table-column prop="year" label="发表年份" width="100" />
        <el-table-column prop="upload_user" label="上传用户" width="120" />
        <el-table-column prop="annotation_count" label="批注数" width="100" />
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.status === 1 ? 'success' : 'danger'">
              {{ row.status === 1 ? '正常' : '已删除' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="upload_time" label="上传时间" width="180">
          <template #default="{ row }">
            {{ formatTime(row.upload_time) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="220" fixed="right">
          <template #default="{ row }">
            <el-button
              size="small"
              type="primary"
              @click="handleEdit(row)"
            >
              编辑
            </el-button>
            <el-button
              v-if="row.status === 1"
              size="small"
              type="danger"
              @click="handleDelete(row)"
            >
              删除
            </el-button>
            <el-button
              v-else
              size="small"
              type="success"
              @click="handleRestore(row)"
            >
              恢复
            </el-button>
            <el-button
              size="small"
              type="info"
              @click="handleDownload(row)"
            >
              下载
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

    <!-- 文献编辑对话框 -->
    <PaperEditDialog
      v-model:visible="editDialogVisible"
      :paper="currentPaper"
      @refresh="refreshData"
    />
    </div>
  </AdminLayout>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Search, Refresh } from '@element-plus/icons-vue'
import { getAdminPapers, deletePaper, restorePaper } from '@/api/admin'
import PaperEditDialog from '@/components/PaperEditDialog.vue'
import AdminLayout from '@/components/AdminLayout.vue'

// 响应式数据
const loading = ref(false)
const paperList = ref([])
const total = ref(0)
const currentPage = ref(1)
const pageSize = ref(20)
const searchKeyword = ref('')
const filterType = ref('')
const filterStatus = ref('')
const editDialogVisible = ref(false)
const currentPaper = ref({})

// 加载文献列表
const loadPapers = async () => {
  try {
    loading.value = true
    const params = {
      page: currentPage.value,
      limit: pageSize.value
    }
    
    // 只添加非空的参数
    if (searchKeyword.value) {
      params.search = searchKeyword.value
    }
    if (filterType.value) {
      params.publication_type_id = parseInt(filterType.value)
    }
    if (filterStatus.value) {
      params.status = parseInt(filterStatus.value)
    }
    
    const response = await getAdminPapers(params)
    if (response.success) {
      paperList.value = response.data.items || []
      total.value = response.data.pagination.total || 0
    } else {
      ElMessage.error(response.error || '获取文献列表失败')
    }
  } catch (error) {
    console.error('获取文献列表失败:', error)
    ElMessage.error('获取文献列表失败')
  } finally {
    loading.value = false
  }
}

// 搜索处理
const handleSearch = () => {
  currentPage.value = 1
  loadPapers()
}

// 刷新数据
const refreshData = () => {
  loadPapers()
}

// 分页大小改变
const handleSizeChange = (size) => {
  pageSize.value = size
  currentPage.value = 1
  loadPapers()
}

// 页码改变
const handleCurrentChange = (page) => {
  currentPage.value = page
  loadPapers()
}

// 编辑文献
const handleEdit = (row) => {
  currentPaper.value = { ...row }
  editDialogVisible.value = true
}

// 删除文献
const handleDelete = async (row) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除文献 "${row.title}" 吗？删除后可以恢复。`,
      '删除确认',
      {
        confirmButtonText: '确定删除',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )

    const response = await deletePaper(row.paper_id)
    if (response.success) {
      ElMessage.success('文献删除成功')
      refreshData()
    } else {
      ElMessage.error(response.error || '删除文献失败')
    }
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除文献失败:', error)
      ElMessage.error('删除文献失败')
    }
  }
}

// 恢复文献
const handleRestore = async (row) => {
  try {
    await ElMessageBox.confirm(
      `确定要恢复文献 "${row.title}" 吗？`,
      '恢复确认',
      {
        confirmButtonText: '确定恢复',
        cancelButtonText: '取消',
        type: 'info'
      }
    )

    const response = await restorePaper(row.paper_id)
    if (response.success) {
      ElMessage.success('文献恢复成功')
      refreshData()
    } else {
      ElMessage.error(response.error || '恢复文献失败')
    }
  } catch (error) {
    if (error !== 'cancel') {
      console.error('恢复文献失败:', error)
      ElMessage.error('恢复文献失败')
    }
  }
}

// 下载文献
const handleDownload = async (row) => {
  try {
    ElMessage.info('正在准备下载...')
    
    // 使用带认证的axios请求下载文件
    const { downloadPaper } = await import('@/api/admin')
    const response = await downloadPaper(row.paper_id)
    
    // 创建blob对象
    const blob = new Blob([response], { type: 'application/pdf' })
    
    // 创建下载链接
    const downloadUrl = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = downloadUrl
    link.download = row.file_name || `${row.title}.pdf`
    link.style.display = 'none'
    
    // 触发下载
    document.body.appendChild(link)
    link.click()
    
    // 清理
    document.body.removeChild(link)
    window.URL.revokeObjectURL(downloadUrl)
    
    ElMessage.success('下载开始')
  } catch (error) {
    console.error('下载文献失败:', error)
    ElMessage.error('下载文献失败')
  }
}

// 获取文献类型颜色
const getTypeColor = (type) => {
  const colorMap = {
    '期刊': 'primary',
    '会议': 'success', 
    '学位论文': 'warning',
    '书籍': 'danger',
    '报告': 'info'
  }
  return colorMap[type] || 'info'
}

// 获取文献类型名称
const getTypeName = (type) => {
  const nameMap = {
    1: '期刊',
    2: '会议',
    3: '书籍',
    4: '报告',
    5: '学位论文'
  }
  return nameMap[type] || type
}

// 格式化时间
const formatTime = (time) => {
  if (!time) return ''
  return new Date(time).toLocaleString('zh-CN')
}

onMounted(() => {
  loadPapers()
})
</script>

<style scoped>
.admin-papers {
  padding: 20px;
  max-width: 1600px;
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
  .admin-papers {
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