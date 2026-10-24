<template>
  <div class="upload-section">
    <h2>Upload PDF Paper</h2>
    <el-upload
      class="upload-demo"
      drag
      :auto-upload="false"
      :on-change="handleFileChange"
      :limit="1"
      accept=".pdf"
    >
      <el-icon class="el-icon--upload"><upload-filled /></el-icon>
      <div class="el-upload__text">
        Drop PDF file here or <em>click to upload</em>
      </div>
      <template #tip>
        <div class="el-upload__tip">
          PDF files only, max 50MB
        </div>
      </template>
    </el-upload>

    <el-button
      type="primary"
      @click="uploadFile"
      :loading="uploading"
      :disabled="!selectedFile"
      class="process-btn"
    >
      {{ uploading ? 'Processing...' : 'Start Processing' }}
    </el-button>

    <el-progress
      v-if="uploadProgress > 0"
      :percentage="uploadProgress"
      :status="uploadProgress === 100 ? 'success' : ''"
      style="margin-top: 20px;"
    />

    <div v-if="uploadResult" class="upload-result" :class="{ duplicate: uploadResult.duplicate }">
      <h3>{{ uploadResult.duplicate ? 'Paper Already in Database' : 'Processing Result' }}</h3>
      <p v-if="uploadResult.duplicate" class="duplicate-note">
        This paper was not added again. The stored version is shown below.
      </p>
      <p><strong>Filename:</strong> {{ uploadResult.filename }}</p>
      <p><strong>Title:</strong> {{ uploadResult.metadata.title }}</p>
      <p><strong>Authors:</strong> {{ (uploadResult.metadata.authors || []).join(', ') || 'Not identified' }}</p>
      <p><strong>Keywords:</strong> {{ (uploadResult.metadata.keywords || []).join(', ') || 'Not identified' }}</p>
      <p v-if="uploadResult.metadata.year"><strong>Year:</strong> {{ uploadResult.metadata.year }}</p>
      <p><strong>Chunks:</strong> {{ uploadResult.num_chunks }}</p>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { ElMessage } from 'element-plus'
import { UploadFilled } from '@element-plus/icons-vue'
import { uploadPDF } from '../api'

const selectedFile = ref(null)
const uploading = ref(false)
const uploadProgress = ref(0)
const uploadResult = ref(null)

const handleFileChange = (file) => {
  selectedFile.value = file.raw
  uploadProgress.value = 0
  uploadResult.value = null
}

const uploadFile = async () => {
  if (!selectedFile.value) {
    ElMessage.warning('Please select a file first')
    return
  }

  uploading.value = true
  uploadProgress.value = 0

  try {
    const response = await uploadPDF(selectedFile.value, (progress) => {
      uploadProgress.value = progress
    })

    uploadResult.value = response.data
    ElMessage.success('PDF processed successfully!')
  } catch (error) {
    if (error.response?.status === 409 && error.response.data?.duplicate) {
      uploadResult.value = error.response.data
      ElMessage.warning(error.response.data.error)
      return
    }
    ElMessage.error(error.response?.data?.error || 'Upload failed')
  } finally {
    uploading.value = false
  }
}
</script>

<style scoped>
.upload-section {
  padding: 32px;
  background: #FFFFFF;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  transition: box-shadow 0.3s ease;
}

.upload-section:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

h2 {
  margin-top: 0;
  margin-bottom: 24px;
  color: #303133;
  font-size: 20px;
  font-weight: 600;
}

.upload-demo {
  transition: all 0.3s ease;
}

.upload-demo :deep(.el-upload-dragger) {
  border: 2px dashed #DCDFE6;
  border-radius: 8px;
  transition: all 0.3s ease;
}

.upload-demo :deep(.el-upload-dragger:hover) {
  border-color: #409EFF;
  background-color: #ECF5FF;
}

.upload-demo :deep(.el-upload-dragger:focus) {
  border-color: #409EFF;
  box-shadow: 0 0 0 3px rgba(64, 158, 255, 0.1);
}

.process-btn {
  margin-top: 20px;
  width: 100%;
  height: 44px;
  font-size: 15px;
  font-weight: 500;
  transition: all 0.3s ease;
}

.process-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(64, 158, 255, 0.3);
}

.process-btn:active {
  transform: translateY(0);
  box-shadow: 0 2px 6px rgba(64, 158, 255, 0.2);
}

.upload-result {
  margin-top: 24px;
  padding: 20px;
  background: #F5F7FA;
  border-radius: 8px;
  border-left: 4px solid #409EFF;
  animation: slideIn 0.3s ease;
}

@keyframes slideIn {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.upload-result.duplicate {
  background: #FDF6EC;
  border-left-color: #E6A23C;
}

.upload-result.duplicate h3 {
  color: #E6A23C;
}

.upload-result .duplicate-note {
  font-style: italic;
}

.upload-result h3 {
  margin-top: 0;
  margin-bottom: 16px;
  color: #409EFF;
  font-size: 16px;
  font-weight: 600;
}

.upload-result p {
  margin: 12px 0;
  color: #606266;
  font-size: 14px;
  line-height: 1.6;
}

.upload-result p strong {
  color: #303133;
  font-weight: 600;
}
</style>

