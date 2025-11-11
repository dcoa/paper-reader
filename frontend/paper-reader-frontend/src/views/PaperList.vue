<template>
  <PageLayout
    title="Papers"
    subtitle="Manage and view your research papers"
    :show-header="true"
  >
    <template #headerActions>
      <el-button class="header-button" @click="$router.push('/home')">
        <el-icon><house /></el-icon>
        Home
      </el-button>
    </template>

    <div class="paper-list-container">
      <!-- Search and Filter Section -->
      <section class="search-section">
        <div class="search-card">
          <div class="search-header">
            <h3 class="search-title">Search & Filter</h3>
            <p class="search-subtitle">Quickly find the papers you need</p>
          </div>

          <div class="search-controls">
            <div class="search-row">
              <div class="search-item">
                <label class="search-label">Publication Type</label>
                <el-select
                  v-model="filterForm.publication_type_id"
                  placeholder="Select publication type"
                  clearable
                  class="search-input"
                  @change="handleFilterChange"
                >
                  <el-option
                    v-for="type in publicationTypes"
                    :key="type.type_id"
                    :label="type.type_name"
                    :value="type.type_id"
                  />
                </el-select>
              </div>

              <div class="search-item">
                <label class="search-label">Journal/Conference</label>
                <el-input
                  v-model="filterForm.publication_name"
                  placeholder="Enter journal or conference name"
                  clearable
                  class="search-input"
                  @input="handleFilterChange"
                />
              </div>

              <div class="search-actions">
                <button class="search-button search-button--primary" @click="searchPapers">
                  <el-icon><search /></el-icon>
                  Search
                </button>
                <button class="search-button search-button--secondary" @click="resetFilter">
                  <el-icon><refresh /></el-icon>
                  Reset
                </button>
              </div>
            </div>

            <div class="search-row">
              <div class="quick-actions">
                <button class="quick-action-button" @click="$router.push('/upload')">
                  <el-icon size="20"><upload-filled /></el-icon>
                  <span>Upload Paper</span>
                </button>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- Paper List Section -->
      <section class="list-section">
        <div class="list-card">
          <div class="list-header">
            <div class="list-title-section">
              <h3 class="list-title">Papers</h3>
              <span class="list-count">Total {{ pagination.total }} papers</span>
            </div>
          </div>

          <div class="table-container">
            <el-table
              v-loading="loading"
              :data="paperList"
              class="paper-table"
              stripe
              @row-click="handleRowClick"
            >
              <el-table-column prop="title" label="Title" min-width="300">
                <template #default="{ row }">
                  <div class="paper-title-cell">
                    <h4 class="paper-title-link" @click="viewPaper(row.paper_id)">
                      {{ row.title }}
                    </h4>
                    <div class="paper-meta">
                      <span class="meta-author">{{ row.authors }}</span>
                      <span class="meta-separator">·</span>
                      <span class="meta-year">{{ row.year }}</span>
                    </div>
                  </div>
                </template>
              </el-table-column>
              
              <el-table-column prop="publication_type" label="Type" width="100">
                <template #default="{ row }">
                  <el-tag class="type-tag" size="small">{{ row.publication_type }}</el-tag>
                </template>
              </el-table-column>

              <el-table-column prop="publication_name" label="Journal/Conference" width="200" show-overflow-tooltip />

              <el-table-column prop="upload_time" label="Upload Time" width="160">
                <template #default="{ row }">
                  <span class="upload-time">{{ formatDate(row.upload_time) }}</span>
                </template>
              </el-table-column>

              <el-table-column label="Actions" width="180" fixed="right">
                <template #default="{ row }">
                  <div class="action-buttons">
                    <button class="action-btn action-btn--primary" @click="viewPaper(row.paper_id)">
                      <el-icon><view /></el-icon>
                      View
                    </button>
                    <button class="action-btn action-btn--secondary" @click="downloadPaperFile(row.paper_id)">
                      <el-icon><download /></el-icon>
                      Download
                    </button>
                  </div>
                </template>
              </el-table-column>
            </el-table>
          </div>

          <!-- Pagination -->
          <div class="pagination-section">
            <el-pagination
              v-model:current-page="pagination.page"
              v-model:page-size="pagination.limit"
              :page-sizes="[10, 20, 50, 100]"
              :total="pagination.total"
              layout="total, sizes, prev, pager, next, jumper"
              class="pagination"
              @size-change="handleSizeChange"
              @current-change="handleCurrentChange"
            />
          </div>
        </div>
      </section>
    </div>
  </PageLayout>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { getPapersList, downloadPaper } from '@/api/papers'
import { getPublicationTypes } from '@/api/publication_types'
import PageLayout from '@/components/PageLayout.vue'
import dayjs from 'dayjs'

const router = useRouter()

// Loading state
const loading = ref(false)

// Paper list data
const paperList = ref([])

// Publication types list
const publicationTypes = ref([])

// Filter form
const filterForm = reactive({
  publication_type_id: null,
  publication_name: ''
})

// Pagination info
const pagination = reactive({
  page: 1,
  limit: 20,
  total: 0
})

// Format date
const formatDate = (dateString) => {
  return dayjs(dateString).format('YYYY-MM-DD HH:mm')
}

// Get publication types list
const fetchPublicationTypes = async () => {
  try {
    const response = await getPublicationTypes()
    if (response.success) {
      publicationTypes.value = response.data
    }
  } catch (error) {
    console.error('Failed to get publication types:', error)
  }
}

// Get papers list
const fetchPapersList = async () => {
  loading.value = true
  try {
    const params = {
      page: pagination.page,
      limit: pagination.limit,
      ...filterForm
    }

    // Remove empty values
    Object.keys(params).forEach(key => {
      if (params[key] === null || params[key] === '') {
        delete params[key]
      }
    })

    const response = await getPapersList(params)
    if (response.success) {
      paperList.value = response.data.papers || []
      pagination.total = response.data.total || 0
    } else {
      ElMessage.error(response.error || 'Failed to get papers list')
    }
  } catch (error) {
    console.error('Failed to get papers list:', error)
    ElMessage.error('Failed to get papers list')
  } finally {
    loading.value = false
  }
}

// Search papers
const searchPapers = () => {
  pagination.page = 1
  fetchPapersList()
}

// Reset filter conditions
const resetFilter = () => {
  filterForm.publication_type_id = null
  filterForm.publication_name = ''
  pagination.page = 1
  fetchPapersList()
}

// Handle filter change
const handleFilterChange = () => {
  // Can add debounce logic here
}

// Handle pagination size change
const handleSizeChange = (newSize) => {
  pagination.limit = newSize
  pagination.page = 1
  fetchPapersList()
}

// Handle current page change
const handleCurrentChange = (newPage) => {
  pagination.page = newPage
  fetchPapersList()
}

// Handle row click
const handleRowClick = (row) => {
  viewPaper(row.paper_id)
}

// View paper details
const viewPaper = (paperId) => {
  router.push(`/paper/${paperId}`)
}

// Download paper
const downloadPaperFile = async (paperId) => {
  try {
    console.log('Starting download:', paperId)

    const response = await downloadPaper(paperId)

    console.log('Download response:', response)

    // Check if response is blob type
    if (!(response instanceof Blob)) {
      console.error('Response is not blob type:', response)
      ElMessage.error('Download failed: Invalid response format')
      return
    }

    // Check blob size
    if (response.size === 0) {
      console.error('Downloaded file is empty')
      ElMessage.error('Download failed: File is empty')
      return
    }

    // Create download link
    const url = window.URL.createObjectURL(response)
    const link = document.createElement('a')
    link.href = url
    link.download = `paper_${paperId}.pdf`

    // Add to DOM and click
    document.body.appendChild(link)
    link.click()

    // Cleanup
    document.body.removeChild(link)
    window.URL.revokeObjectURL(url)

    ElMessage.success('Download successful')
    console.log('Download completed')

  } catch (error) {
    console.error('Download failed:', error)

    // Check for network errors
    if (error.response) {
      console.error('Server response error:', error.response.status, error.response.data)
      ElMessage.error(`Download failed: ${error.response.status} ${error.response.statusText}`)
    } else if (error.request) {
      console.error('Network request error:', error.request)
      ElMessage.error('Download failed: Network connection error')
    } else {
      console.error('Other error:', error.message)
      ElMessage.error(`Download failed: ${error.message}`)
    }
  }
}

// Get data when component is mounted
onMounted(() => {
  fetchPublicationTypes()
  fetchPapersList()
})
</script>

<style scoped>
.paper-list-container {
  max-width: 1200px;
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  gap: var(--spacing-6);
}

.header-button {
  font-weight: var(--font-weight-medium);
}

/* 搜索区域样式 */
.search-section {
  margin-bottom: var(--spacing-6);
}

.search-card {
  background-color: var(--color-background-paper);
  border-radius: var(--border-radius-lg);
  padding: var(--spacing-6);
  box-shadow: var(--shadow-sm);
  border: 1px solid var(--color-grey-200);
}

.search-header {
  margin-bottom: var(--spacing-6);
}

.search-title {
  margin: 0 0 var(--spacing-1) 0;
  font-size: var(--font-size-h3);
  font-weight: var(--font-weight-semibold);
  color: var(--color-text-primary);
}

.search-subtitle {
  margin: 0;
  font-size: var(--font-size-body2);
  color: var(--color-text-secondary);
}

.search-controls {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-4);
}

.search-row {
  display: flex;
  align-items: end;
  gap: var(--spacing-4);
  flex-wrap: wrap;
}

.search-item {
  flex: 1;
  min-width: 200px;
  display: flex;
  flex-direction: column;
  gap: var(--spacing-2);
}

.search-label {
  font-size: var(--font-size-body2);
  font-weight: var(--font-weight-medium);
  color: var(--color-text-primary);
}

.search-input {
  width: 100%;
}

.search-actions {
  display: flex;
  gap: var(--spacing-2);
  align-items: center;
}

.search-button {
  display: flex;
  align-items: center;
  gap: var(--spacing-2);
  padding: 10px 16px;
  border-radius: var(--border-radius);
  font-size: var(--font-size-button);
  font-weight: var(--font-weight-medium);
  cursor: pointer;
  transition: all var(--transition-fast);
  border: none;
  white-space: nowrap;
}

.search-button--primary {
  background-color: var(--color-primary);
  color: white;
}

.search-button--primary:hover {
  background-color: var(--color-primary-dark);
  transform: translateY(-1px);
  box-shadow: var(--shadow-md);
}

.search-button--secondary {
  background-color: var(--color-grey-100);
  color: var(--color-text-secondary);
  border: 1px solid var(--color-grey-300);
}

.search-button--secondary:hover {
  background-color: var(--color-grey-200);
  color: var(--color-text-primary);
}

.quick-actions {
  display: flex;
  align-items: center;
  gap: var(--spacing-3);
}

.quick-action-button {
  display: flex;
  align-items: center;
  gap: var(--spacing-2);
  padding: var(--spacing-2) var(--spacing-4);
  background-color: var(--color-feedback-success);
  color: white;
  border: none;
  border-radius: var(--border-radius);
  font-size: var(--font-size-body2);
  font-weight: var(--font-weight-medium);
  cursor: pointer;
  transition: all var(--transition-fast);
}

.quick-action-button:hover {
  background-color: #2e7d32;
  transform: translateY(-1px);
  box-shadow: var(--shadow-md);
}

/* 列表区域样式 */
.list-card {
  background-color: var(--color-background-paper);
  border-radius: var(--border-radius-lg);
  box-shadow: var(--shadow-sm);
  border: 1px solid var(--color-grey-200);
  overflow: hidden;
}

.list-header {
  padding: var(--spacing-6);
  border-bottom: 1px solid var(--color-grey-200);
  background-color: var(--color-grey-100);
}

.list-title-section {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: var(--spacing-4);
}

.list-title {
  margin: 0;
  font-size: var(--font-size-h3);
  font-weight: var(--font-weight-semibold);
  color: var(--color-text-primary);
}

.list-count {
  font-size: var(--font-size-body2);
  color: var(--color-text-secondary);
  font-weight: var(--font-weight-medium);
  background-color: var(--color-primary-light);
  color: var(--color-primary-dark);
  padding: var(--spacing-1) var(--spacing-3);
  border-radius: var(--border-radius);
}

.table-container {
  min-height: 400px;
}

.paper-table {
  width: 100%;
}

.paper-table :deep(.el-table__header) {
  background-color: var(--color-grey-50);
}

.paper-table :deep(.el-table__header th) {
  background-color: var(--color-grey-50);
  color: var(--color-text-primary);
  font-weight: var(--font-weight-semibold);
  border-bottom: 2px solid var(--color-grey-200);
}

.paper-table :deep(.el-table__row) {
  cursor: pointer;
  transition: background-color var(--transition-fast);
}

.paper-table :deep(.el-table__row:hover) {
  background-color: var(--color-primary-light);
}

.paper-title-cell {
  padding: var(--spacing-2) 0;
}

.paper-title-link {
  margin: 0 0 var(--spacing-1) 0;
  font-size: var(--font-size-body1);
  font-weight: var(--font-weight-medium);
  color: var(--color-primary);
  cursor: pointer;
  line-height: 1.4;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  transition: color var(--transition-fast);
}

.paper-title-link:hover {
  color: var(--color-primary-dark);
  text-decoration: underline;
}

.paper-meta {
  display: flex;
  align-items: center;
  gap: var(--spacing-2);
  font-size: var(--font-size-caption);
  color: var(--color-text-secondary);
}

.meta-author {
  font-weight: var(--font-weight-medium);
  color: var(--color-text-primary);
}

.meta-separator {
  color: var(--color-grey-400);
}

.type-tag {
  background-color: var(--color-primary-light);
  color: var(--color-primary-dark);
  border: 1px solid var(--color-primary);
  font-weight: var(--font-weight-medium);
}

.upload-time {
  font-size: var(--font-size-caption);
  color: var(--color-text-secondary);
}

.action-buttons {
  display: flex;
  gap: var(--spacing-2);
}

.action-btn {
  display: flex;
  align-items: center;
  gap: var(--spacing-1);
  padding: var(--spacing-1) var(--spacing-2);
  border-radius: var(--border-radius);
  font-size: var(--font-size-caption);
  font-weight: var(--font-weight-medium);
  cursor: pointer;
  transition: all var(--transition-fast);
  border: 1px solid transparent;
}

.action-btn--primary {
  background-color: var(--color-primary);
  color: white;
}

.action-btn--primary:hover {
  background-color: var(--color-primary-dark);
  transform: translateY(-1px);
  box-shadow: var(--shadow-sm);
}

.action-btn--secondary {
  background-color: var(--color-feedback-success);
  color: white;
}

.action-btn--secondary:hover {
  background-color: #2e7d32;
  transform: translateY(-1px);
  box-shadow: var(--shadow-sm);
}

/* 分页区域 */
.pagination-section {
  padding: var(--spacing-6);
  border-top: 1px solid var(--color-grey-200);
  background-color: var(--color-grey-50);
  display: flex;
  justify-content: center;
}

.pagination :deep(.el-pagination) {
  justify-content: center;
}

.pagination :deep(.el-pager li.is-active) {
  background-color: var(--color-primary);
  color: white;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .search-row {
    flex-direction: column;
    align-items: stretch;
    gap: var(--spacing-3);
  }
  
  .search-item {
    min-width: auto;
  }
  
  .search-actions {
    justify-content: center;
  }
  
  .list-title-section {
    flex-direction: column;
    align-items: center;
    text-align: center;
    gap: var(--spacing-2);
  }
  
  .paper-table :deep(.el-table__fixed-right) {
    display: none;
  }
  
  .action-buttons {
    flex-direction: column;
  }
  
  .pagination-section {
    padding: var(--spacing-4);
  }
}

@media (max-width: 480px) {
  .search-card,
  .list-card {
    border-radius: var(--border-radius);
  }
  
  .search-card {
    padding: var(--spacing-4);
  }
  
  .list-header {
    padding: var(--spacing-4);
  }
  
  .pagination-section {
    padding: var(--spacing-3);
  }
  
  .pagination :deep(.el-pagination) {
    flex-wrap: wrap;
    gap: var(--spacing-2);
  }
}
</style> 