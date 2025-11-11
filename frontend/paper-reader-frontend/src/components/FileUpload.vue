<template>
  <div class="file-upload">
    <!-- 上传区域 -->
    <el-upload
      ref="uploadRef"
      class="upload-dragger"
      drag
      :auto-upload="false"
      :on-change="handleFileChange"
      :on-remove="handleFileRemove"
      :before-upload="beforeUpload"
      :accept="acceptTypes"
      :limit="limit"
      :multiple="multiple"
      :disabled="disabled || uploading"
      :show-file-list="showFileList"
    >
      <div class="upload-content">
        <el-icon class="upload-icon" :size="iconSize">
          <upload-filled v-if="!uploading" />
          <loading v-else />
        </el-icon>
        
        <div class="upload-text">
          <div class="primary-text">
            {{ uploading ? '上传中...' : (dragText || '将文件拖到此处，或点击上传') }}
          </div>
          <div class="secondary-text" v-if="!uploading">
            {{ tipText || `支持 ${acceptTypes} 格式，文件大小不超过 ${maxSizeMB}MB` }}
          </div>
        </div>
      </div>
    </el-upload>

    <!-- 上传进度 -->
    <div v-if="uploading || uploadProgress > 0" class="upload-progress">
      <el-progress
        :percentage="uploadProgress"
        :status="uploadStatus"
        :stroke-width="8"
        :show-text="true"
      />
      <p class="progress-text">{{ progressText }}</p>
    </div>

    <!-- 文件列表 -->
    <div v-if="showFileList && fileList.length > 0" class="file-list">
      <h4>文件列表</h4>
      <div
        v-for="(file, index) in fileList"
        :key="index"
        class="file-item"
      >
        <div class="file-info">
          <el-icon><document /></el-icon>
          <div class="file-details">
            <span class="file-name">{{ file.name }}</span>
            <span class="file-size">{{ formatFileSize(file.size) }}</span>
          </div>
        </div>
        <div class="file-actions">
          <el-button
            size="small"
            type="danger"
            text
            @click="removeFile(index)"
            :disabled="uploading"
          >
            <el-icon><delete /></el-icon>
            移除
          </el-button>
        </div>
      </div>
    </div>

    <!-- 操作按钮 -->
    <div v-if="showActions" class="upload-actions">
      <el-button
        type="primary"
        :loading="uploading"
        :disabled="fileList.length === 0 || disabled"
        @click="handleUpload"
      >
        <el-icon><upload-filled /></el-icon>
        {{ uploading ? '上传中...' : '开始上传' }}
      </el-button>
      
      <el-button
        :disabled="uploading"
        @click="clearFiles"
      >
        <el-icon><delete /></el-icon>
        清空文件
      </el-button>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, watch } from 'vue'
import { ElMessage } from 'element-plus'

// Props
const props = defineProps({
  // 接受的文件类型
  acceptTypes: {
    type: String,
    default: '.pdf,.doc,.docx'
  },
  // 文件大小限制（MB）
  maxSizeMB: {
    type: Number,
    default: 50
  },
  // 文件数量限制
  limit: {
    type: Number,
    default: 1
  },
  // 是否支持多选
  multiple: {
    type: Boolean,
    default: false
  },
  // 是否禁用
  disabled: {
    type: Boolean,
    default: false
  },
  // 是否显示文件列表
  showFileList: {
    type: Boolean,
    default: true
  },
  // 是否显示操作按钮
  showActions: {
    type: Boolean,
    default: true
  },
  // 自动上传
  autoUpload: {
    type: Boolean,
    default: false
  },
  // 拖拽提示文本
  dragText: {
    type: String,
    default: ''
  },
  // 提示文本
  tipText: {
    type: String,
    default: ''
  },
  // 图标大小
  iconSize: {
    type: Number,
    default: 48
  },
  // 上传函数
  uploadFunction: {
    type: Function,
    default: null
  }
})

// Emits
const emits = defineEmits([
  'file-change',
  'file-remove', 
  'upload-start',
  'upload-progress',
  'upload-success',
  'upload-error',
  'upload-complete'
])

// 响应式数据
const uploadRef = ref()
const uploading = ref(false)
const uploadProgress = ref(0)
const uploadStatus = ref('')
const progressText = ref('')
const fileList = ref([])

// 计算属性
const maxSizeBytes = computed(() => props.maxSizeMB * 1024 * 1024)

// 格式化文件大小
const formatFileSize = (bytes) => {
  if (bytes === 0) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

// 文件上传前验证
const beforeUpload = (file) => {
  // 检查文件类型
  if (props.acceptTypes) {
    const acceptedTypes = props.acceptTypes.split(',').map(type => type.trim())
    const fileExtension = '.' + file.name.split('.').pop().toLowerCase()
    
    if (!acceptedTypes.includes(fileExtension)) {
      ElMessage.error(`只支持 ${props.acceptTypes} 格式的文件`)
      return false
    }
  }

  // 检查文件大小
  if (file.size > maxSizeBytes.value) {
    ElMessage.error(`文件大小不能超过 ${props.maxSizeMB}MB`)
    return false
  }

  return true
}

// 处理文件选择
const handleFileChange = (file, files) => {
  if (beforeUpload(file.raw)) {
    // 如果是单文件上传，替换现有文件
    if (!props.multiple) {
      fileList.value = [file.raw]
    } else {
      // 多文件上传，添加到列表
      if (fileList.value.length < props.limit) {
        fileList.value.push(file.raw)
      } else {
        ElMessage.error(`最多只能上传 ${props.limit} 个文件`)
        return
      }
    }
    
    emits('file-change', file.raw, fileList.value)
    
    // 自动上传
    if (props.autoUpload && props.uploadFunction) {
      handleUpload()
    }
  }
}

// 处理文件移除
const handleFileRemove = (file, files) => {
  const index = fileList.value.findIndex(f => f.name === file.name)
  if (index > -1) {
    fileList.value.splice(index, 1)
  }
  
  emits('file-remove', file, fileList.value)
}

// 移除指定文件
const removeFile = (index) => {
  const file = fileList.value[index]
  fileList.value.splice(index, 1)
  
  // 同步移除upload组件中的文件
  if (uploadRef.value) {
    uploadRef.value.clearFiles()
  }
  
  emits('file-remove', file, fileList.value)
}

// 清空所有文件
const clearFiles = () => {
  fileList.value = []
  uploadProgress.value = 0
  uploadStatus.value = ''
  progressText.value = ''
  
  if (uploadRef.value) {
    uploadRef.value.clearFiles()
  }
}

// 开始上传
const handleUpload = async () => {
  if (fileList.value.length === 0) {
    ElMessage.error('请先选择文件')
    return
  }

  if (!props.uploadFunction) {
    ElMessage.error('未配置上传函数')
    return
  }

  uploading.value = true
  uploadProgress.value = 0
  uploadStatus.value = 'active'
  progressText.value = '准备上传...'
  
  emits('upload-start', fileList.value)

  try {
    // 模拟上传进度
    const progressInterval = setInterval(() => {
      if (uploadProgress.value < 90) {
        uploadProgress.value += Math.random() * 10
        progressText.value = `上传中... ${Math.floor(uploadProgress.value)}%`
        emits('upload-progress', uploadProgress.value)
      }
    }, 200)

    // 调用上传函数
    const result = await props.uploadFunction(fileList.value[0], fileList.value)
    
    clearInterval(progressInterval)
    
    uploadProgress.value = 100
    uploadStatus.value = 'success'
    progressText.value = '上传成功！'
    
    emits('upload-success', result, fileList.value)
    ElMessage.success('文件上传成功')
    
  } catch (error) {
    uploadStatus.value = 'exception'
    progressText.value = '上传失败'
    
    emits('upload-error', error, fileList.value)
    console.error('上传失败:', error)
    ElMessage.error('上传失败，请重试')
    
  } finally {
    uploading.value = false
    emits('upload-complete', fileList.value)
  }
}

// 重置上传状态
const resetUpload = () => {
  uploading.value = false
  uploadProgress.value = 0
  uploadStatus.value = ''
  progressText.value = ''
}

// 暴露方法给父组件
defineExpose({
  handleUpload,
  clearFiles,
  resetUpload,
  fileList: fileList
})
</script>

<style scoped>
.file-upload {
  width: 100%;
}

.upload-dragger {
  width: 100%;
}

:deep(.el-upload-dragger) {
  width: 100%;
  height: 180px;
  border: 2px dashed #d9d9d9;
  border-radius: 8px;
  background-color: #fafafa;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
}

:deep(.el-upload-dragger:hover) {
  border-color: #409EFF;
  background-color: #f0f9ff;
}

:deep(.el-upload-dragger.is-dragover) {
  border-color: #409EFF;
  background-color: #f0f9ff;
}

.upload-content {
  text-align: center;
  color: #606266;
}

.upload-icon {
  color: #c0c4cc;
  margin-bottom: 16px;
}

.upload-icon.loading {
  animation: rotate 2s linear infinite;
}

@keyframes rotate {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}

.upload-text {
  line-height: 1.4;
}

.primary-text {
  font-size: 16px;
  color: #606266;
  margin-bottom: 8px;
}

.secondary-text {
  font-size: 12px;
  color: #909399;
}

.upload-progress {
  margin: 20px 0;
  padding: 20px;
  background-color: #f8f9fa;
  border-radius: 6px;
  border: 1px solid #e9ecef;
}

.progress-text {
  text-align: center;
  margin: 10px 0 0 0;
  color: #666;
  font-size: 14px;
}

.file-list {
  margin-top: 20px;
  border: 1px solid #e4e7ed;
  border-radius: 6px;
  overflow: hidden;
}

.file-list h4 {
  margin: 0;
  padding: 12px 16px;
  background-color: #f5f7fa;
  border-bottom: 1px solid #e4e7ed;
  font-size: 14px;
  font-weight: 600;
  color: #333;
}

.file-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 16px;
  border-bottom: 1px solid #f0f0f0;
  transition: background-color 0.3s ease;
}

.file-item:hover {
  background-color: #f8f9fa;
}

.file-item:last-child {
  border-bottom: none;
}

.file-info {
  display: flex;
  align-items: center;
  gap: 12px;
  flex: 1;
}

.file-details {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.file-name {
  font-size: 14px;
  color: #333;
  font-weight: 500;
}

.file-size {
  font-size: 12px;
  color: #999;
}

.upload-actions {
  display: flex;
  gap: 12px;
  margin-top: 20px;
  justify-content: center;
}

/* 响应式设计 */
@media (max-width: 768px) {
  :deep(.el-upload-dragger) {
    height: 140px;
  }
  
  .upload-icon {
    font-size: 36px !important;
    margin-bottom: 12px;
  }
  
  .primary-text {
    font-size: 14px;
  }
  
  .secondary-text {
    font-size: 11px;
  }
  
  .file-item {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
  }
  
  .file-actions {
    align-self: flex-end;
  }
  
  .upload-actions {
    flex-direction: column;
  }
}

/* 禁用状态样式 */
:deep(.el-upload.is-disabled .el-upload-dragger) {
  background-color: #f5f7fa;
  border-color: #e4e7ed;
  color: #c0c4cc;
  cursor: not-allowed;
}

:deep(.el-upload.is-disabled .el-upload-dragger:hover) {
  border-color: #e4e7ed;
  background-color: #f5f7fa;
}
</style> 