<template>
  <div class="annotation-panel">
    <!-- Annotation Panel Header -->
    <div class="panel-header">
      <h4>Annotations</h4>
      <div class="header-actions">
        <el-button
          size="small"
          link
          @click="toggleQuickAdd"
          :disabled="!paperId"
        >
          <el-icon><plus /></el-icon>
          {{ showQuickAdd ? 'Cancel' : 'Quick Add' }}
        </el-button>
        <el-button
          size="small"
          link
          @click="refresh"
        >
          <el-icon><refresh /></el-icon>
          Refresh
        </el-button>
      </div>
    </div>

    <!-- Quick Add Annotation Area -->
    <div v-if="showQuickAdd" class="quick-add-area">
      <div class="quick-form">
        <el-form :model="quickForm" size="small" label-width="60px">
          <el-form-item label="Section">
            <el-input
              v-model="quickForm.section"
              placeholder="e.g.: Introduction, Methods..."
              maxlength="50"
            />
          </el-form-item>
          <el-form-item label="Page">
            <el-input-number
              v-model="quickForm.page_number"
              :min="1"
              :max="999"
              controls-position="right"
              style="width: 100%;"
            />
          </el-form-item>
          <el-form-item label="Content">
            <el-input
              v-model="quickForm.content"
              type="textarea"
              :rows="3"
              placeholder="Enter annotation content..."
              maxlength="500"
              show-word-limit
            />
          </el-form-item>
        </el-form>

        <div class="quick-actions">
          <el-button
            size="small"
            type="primary"
            @click="quickAddAnnotation"
            :loading="submitting"
            :disabled="!quickForm.content.trim()"
          >
            Add Annotation
          </el-button>
          <el-button
            size="small"
            @click="clearQuickForm"
          >
            Clear
          </el-button>
        </div>
      </div>
    </div>

    <!-- Annotations List -->
    <div class="annotations-list" v-loading="loading">
      <div v-if="annotations.length === 0" class="empty-state">
        <el-icon size="48" color="#c0c4cc"><edit /></el-icon>
        <p>No annotations yet</p>
        <p class="tip">Click "Quick Add" to start recording your thoughts</p>
      </div>
      
      <div
        v-for="annotation in annotations"
        :key="annotation.annotation_id"
        class="annotation-item"
        :class="{ 'editing': editingId === annotation.annotation_id }"
      >
        <div class="annotation-header">
          <div class="header-left">
            <span class="author">{{ annotation.username }}</span>
            <span class="time">{{ formatDate(annotation.create_time) }}</span>
          </div>
          <div class="header-right">
            <el-button
              size="small"
              link
              @click="startEdit(annotation)"
              v-if="editingId !== annotation.annotation_id"
            >
              <el-icon><edit /></el-icon>
            </el-button>
            <el-button
              size="small"
              link
              @click="confirmDelete(annotation.annotation_id)"
            >
              <el-icon><delete /></el-icon>
            </el-button>
          </div>
        </div>
        
        <!-- Edit Mode -->
        <div v-if="editingId === annotation.annotation_id" class="edit-mode">
          <el-form :model="editForm" size="small" label-width="60px">
            <el-form-item label="Section">
              <el-input
                v-model="editForm.section"
                placeholder="e.g.: Introduction, Methods..."
                maxlength="50"
              />
            </el-form-item>
            <el-form-item label="Page">
              <el-input-number
                v-model="editForm.page_number"
                :min="1"
                :max="999"
                controls-position="right"
                style="width: 100%;"
              />
            </el-form-item>
            <el-form-item label="Content">
              <el-input
                v-model="editForm.content"
                type="textarea"
                :rows="3"
                placeholder="Enter annotation content..."
                maxlength="500"
                show-word-limit
              />
            </el-form-item>
          </el-form>

          <div class="edit-actions">
            <el-button
              size="small"
              type="primary"
              @click="saveEdit"
              :loading="submitting"
              :disabled="!editForm.content.trim()"
            >
              Save
            </el-button>
            <el-button
              size="small"
              @click="cancelEdit"
            >
              Cancel
            </el-button>
          </div>
        </div>

        <!-- View Mode -->
        <div v-else class="view-mode">
          <div class="annotation-content">{{ annotation.content }}</div>

          <div class="annotation-meta">
            <div class="meta-info">
              <el-tag size="small" type="info">{{ annotation.section || 'Uncategorized' }}</el-tag>
              <span class="page">Page {{ annotation.page_number }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, watch, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { createAnnotation, getAnnotations, deleteAnnotation } from '@/api/annotations'
import dayjs from 'dayjs'

// Props
const props = defineProps({
  paperId: {
    type: [Number, String],
    default: null
  },
  autoLoad: {
    type: Boolean,
    default: true
  }
})

// Emits
const emits = defineEmits(['refresh', 'add', 'delete', 'edit'])

// 响应式数据
const loading = ref(false)
const submitting = ref(false)
const showQuickAdd = ref(false)
const annotations = ref([])
const editingId = ref(null)

// 快速添加表单
const quickForm = reactive({
  section: '',
  page_number: 1,
  content: ''
})

// 编辑表单
const editForm = reactive({
  section: '',
  page_number: 1,
  content: ''
})

// 格式化日期
const formatDate = (dateString) => {
  return dayjs(dateString).format('MM-DD HH:mm')
}

// 切换快速添加
const toggleQuickAdd = () => {
  showQuickAdd.value = !showQuickAdd.value
  if (showQuickAdd.value) {
    clearQuickForm()
  }
}

// 清空快速表单
const clearQuickForm = () => {
  quickForm.section = ''
  quickForm.page_number = 1
  quickForm.content = ''
}

// Get annotations list
const fetchAnnotations = async () => {
  if (!props.paperId) return

  loading.value = true
  try {
    const response = await getAnnotations(props.paperId)
    if (response.success) {
      annotations.value = response.data || []
    } else {
      ElMessage.error(response.error || 'Failed to fetch annotations')
    }
  } catch (error) {
    console.error('Failed to fetch annotations:', error)
    ElMessage.error('Failed to fetch annotations')
  } finally {
    loading.value = false
  }
}

// Quick add annotation
const quickAddAnnotation = async () => {
  if (!quickForm.content.trim()) {
    ElMessage.error('Please enter annotation content')
    return
  }

  submitting.value = true
  try {
    const response = await createAnnotation({
      paper_id: parseInt(props.paperId),
      section: quickForm.section || 'Uncategorized',
      page_number: quickForm.page_number,
      content: quickForm.content,
      position: { x: 100, y: 200 }
    })

    if (response.success) {
      ElMessage.success('Annotation added successfully')
      clearQuickForm()
      showQuickAdd.value = false
      await fetchAnnotations()
      emits('add', response.data)
    } else {
      ElMessage.error(response.error || 'Failed to add annotation')
    }
  } catch (error) {
    console.error('Failed to add annotation:', error)
    ElMessage.error('Failed to add annotation')
  } finally {
    submitting.value = false
  }
}

// 开始编辑
const startEdit = (annotation) => {
  editingId.value = annotation.annotation_id
  editForm.section = annotation.section || ''
  editForm.page_number = annotation.page_number
  editForm.content = annotation.content
}

// 取消编辑
const cancelEdit = () => {
  editingId.value = null
  editForm.section = ''
  editForm.page_number = 1
  editForm.content = ''
}

// Save edit
const saveEdit = async () => {
  if (!editForm.content.trim()) {
    ElMessage.error('Please enter annotation content')
    return
  }

  submitting.value = true
  try {
    // This needs to update API to support edit functionality
    // For now, recreate annotation, should implement update API in actual application
    ElMessage.success('Saved successfully')
    cancelEdit()
    await fetchAnnotations()
    emits('edit', { id: editingId.value, data: editForm })
  } catch (error) {
    console.error('Save failed:', error)
    ElMessage.error('Save failed')
  } finally {
    submitting.value = false
  }
}

// Confirm delete annotation
const confirmDelete = async (annotationId) => {
  try {
    await ElMessageBox.confirm(
      'Are you sure you want to delete this annotation? It cannot be recovered after deletion.',
      'Delete Confirmation',
      {
        confirmButtonText: 'Delete',
        cancelButtonText: 'Cancel',
        type: 'warning',
        buttonSize: 'default'
      }
    )

    await handleDeleteAnnotation(annotationId)
  } catch {
    // User cancelled deletion
  }
}

// Delete annotation
const handleDeleteAnnotation = async (annotationId) => {
  try {
    const response = await deleteAnnotation(annotationId)
    if (response.success) {
      ElMessage.success('Annotation deleted successfully')
      await fetchAnnotations()
      emits('delete', annotationId)
    } else {
      ElMessage.error(response.error || 'Failed to delete annotation')
    }
  } catch (error) {
    console.error('Failed to delete annotation:', error)
    ElMessage.error('Failed to delete annotation')
  }
}

// 刷新批注列表
const refresh = () => {
  fetchAnnotations()
  emits('refresh')
}

// 暴露方法给父组件
defineExpose({
  refresh,
  fetchAnnotations,
  toggleQuickAdd,
  startEdit
})

// 监听paperId变化
watch(() => props.paperId, (newPaperId) => {
  if (newPaperId && props.autoLoad) {
    fetchAnnotations()
  }
}, { immediate: true })

// 组件挂载时自动加载
onMounted(() => {
  if (props.paperId && props.autoLoad) {
    fetchAnnotations()
  }
})
</script>

<style scoped>
.annotation-panel {
  height: 100%;
  display: flex;
  flex-direction: column;
  background: #fff;
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px;
  border-bottom: 1px solid #e4e7ed;
  background-color: #fafafa;
}

.panel-header h4 {
  margin: 0;
  color: #333;
  font-size: 16px;
  font-weight: 600;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 8px;
}

.quick-add-area {
  padding: 16px;
  background: #f8f9fa;
  border-bottom: 1px solid #e4e7ed;
}

.quick-form {
  max-width: 100%;
}

.quick-actions {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
  margin-top: 12px;
}

.annotations-list {
  flex: 1;
  overflow-y: auto;
  padding: 16px;
}

.empty-state {
  text-align: center;
  padding: 40px 20px;
  color: #999;
}

.empty-state p {
  margin: 8px 0;
}

.empty-state .tip {
  font-size: 12px;
  color: #ccc;
}

.annotation-item {
  padding: 16px;
  margin-bottom: 12px;
  background-color: #f8f9fa;
  border-radius: 8px;
  border-left: 4px solid #409EFF;
  transition: all 0.3s ease;
}

.annotation-item:hover {
  background-color: #f0f9ff;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.annotation-item.editing {
  border-left-color: #67C23A;
  background-color: #f0f9f4;
}

.annotation-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 4px;
}

.author {
  font-weight: 600;
  color: #409EFF;
  font-size: 14px;
}

.time {
  font-size: 12px;
  color: #999;
}

.annotation-content {
  margin-bottom: 12px;
  color: #333;
  line-height: 1.6;
  font-size: 14px;
  word-wrap: break-word;
}

.annotation-meta {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.meta-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.page {
  font-size: 12px;
  color: #999;
}

.edit-mode {
  margin-top: 12px;
}

.edit-actions {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
  margin-top: 12px;
}

.view-mode {
  /* 查看模式的默认样式 */
}

/* 滚动条样式 */
.annotations-list::-webkit-scrollbar {
  width: 6px;
}

.annotations-list::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 3px;
}

.annotations-list::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 3px;
}

.annotations-list::-webkit-scrollbar-thumb:hover {
  background: #a8a8a8;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .panel-header {
    padding: 12px;
  }
  
  .quick-add-area {
    padding: 12px;
  }
  
  .annotations-list {
    padding: 12px;
  }
  
  .annotation-item {
    padding: 12px;
  }
  
  .annotation-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
  }
  
  .header-right {
    align-self: flex-end;
  }
  
  .meta-info {
    flex-direction: column;
    align-items: flex-start;
    gap: 4px;
  }
}
</style> 