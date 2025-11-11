<template>
  <PageLayout
    title="Upload Paper"
    subtitle="Please fill in the paper information and upload a PDF or Word file"
    :show-header="true"
  >
    <template #headerActions>
      <el-button @click="$router.push('/home')">
        <el-icon><house /></el-icon>
        Home
      </el-button>
      <el-button @click="$router.push('/papers')">
        <el-icon><document /></el-icon>
        Papers
      </el-button>
    </template>

    <el-card class="upload-card">
      <el-form
        ref="uploadFormRef"
        :model="uploadForm"
        :rules="uploadRules"
        label-width="120px"
        class="upload-form"
      >
        <!-- File Upload Area -->
        <el-form-item label="Paper File" prop="file">
          <el-upload
            ref="uploadRef"
            class="upload-dragger"
            drag
            :auto-upload="false"
            :on-change="handleFileChange"
            :on-remove="handleFileRemove"
            :before-upload="beforeUpload"
            accept=".pdf,.doc,.docx"
            :limit="1"
          >
            <el-icon class="el-icon--upload"><upload-filled /></el-icon>
            <div class="el-upload__text">
              Drag file here, or <em>click to upload</em>
            </div>
            <template #tip>
              <div class="el-upload__tip">
                Supports PDF, DOC, DOCX formats, file size not exceeding 50MB
              </div>
            </template>
          </el-upload>
        </el-form-item>

        <!-- Paper Title -->
        <el-form-item label="Paper Title" prop="title">
          <el-input
            v-model="uploadForm.title"
            placeholder="Enter paper title"
            maxlength="200"
            show-word-limit
          />
        </el-form-item>

        <!-- Authors -->
        <el-form-item label="Authors" prop="authors">
          <el-input
            v-model="uploadForm.authors"
            placeholder="Enter author names, separated by commas for multiple authors"
            maxlength="100"
            show-word-limit
          />
        </el-form-item>

        <!-- Publication Type -->
        <el-form-item label="Publication Type" prop="publication_type_id">
          <el-select
            v-model="uploadForm.publication_type_id"
            placeholder="Select publication type"
            style="width: 100%"
          >
            <el-option
              v-for="type in publicationTypes"
              :key="type.type_id"
              :label="type.type_name"
              :value="type.type_id"
            />
          </el-select>
        </el-form-item>

        <!-- Journal/Conference Name -->
        <el-form-item label="Journal/Conference Name" prop="publication_name">
          <el-input
            v-model="uploadForm.publication_name"
            placeholder="Enter journal or conference name"
            maxlength="100"
            show-word-limit
          />
        </el-form-item>

        <!-- Publication Year -->
        <el-form-item label="Publication Year" prop="year">
          <el-date-picker
            v-model="uploadForm.year"
            type="year"
            placeholder="Select publication year"
            value-format="YYYY"
            style="width: 100%"
          />
        </el-form-item>

        <!-- Abstract -->
        <el-form-item label="Abstract" prop="abstract">
          <el-input
            v-model="uploadForm.abstract"
            type="textarea"
            :rows="6"
            placeholder="Enter paper abstract (optional)"
            maxlength="1000"
            show-word-limit
          />
        </el-form-item>

        <!-- Upload Progress -->
        <el-form-item v-if="uploading">
          <div class="upload-progress">
            <el-progress
              :percentage="uploadProgress"
              :status="uploadStatus"
              :stroke-width="8"
            />
            <p class="progress-text">{{ progressText }}</p>
          </div>
        </el-form-item>

        <!-- Action Buttons -->
        <el-form-item>
          <el-button
            type="primary"
            size="large"
            :loading="uploading"
            @click="handleUpload"
          >
            {{ uploading ? 'Uploading...' : 'Start Upload' }}
          </el-button>
          <el-button size="large" @click="resetForm">
            Reset
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </PageLayout>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { uploadPaper } from '@/api/papers'
import { getPublicationTypes } from '@/api/publication_types'
import PageLayout from '@/components/PageLayout.vue'

const router = useRouter()

// 表单引用
const uploadFormRef = ref()
const uploadRef = ref()

// 上传状态
const uploading = ref(false)
const uploadProgress = ref(0)
const uploadStatus = ref('')
const progressText = ref('')

// 文献类型列表
const publicationTypes = ref([])

// 上传表单数据
const uploadForm = reactive({
  file: null,
  title: '',
  authors: '',
  publication_type_id: null,
  publication_name: '',
  year: '',
  abstract: ''
})

// Form validation rules
const uploadRules = {
  file: [
    { required: true, message: 'Please select a paper file', trigger: 'change' }
  ],
  title: [
    { required: true, message: 'Please enter paper title', trigger: 'blur' },
    { min: 5, max: 200, message: 'Title length should be between 5 and 200 characters', trigger: 'blur' }
  ],
  authors: [
    { required: true, message: 'Please enter author names', trigger: 'blur' },
    { max: 100, message: 'Author names cannot exceed 100 characters', trigger: 'blur' }
  ],
  publication_type_id: [
    { required: true, message: 'Please select publication type', trigger: 'change' }
  ],
  publication_name: [
    { required: true, message: 'Please enter journal or conference name', trigger: 'blur' },
    { max: 100, message: 'Journal/conference name cannot exceed 100 characters', trigger: 'blur' }
  ],
  year: [
    { required: true, message: 'Please select publication year', trigger: 'change' }
  ]
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
    ElMessage.error('Failed to get publication types')
  }
}

// File upload validation
const beforeUpload = (file) => {
  const allowedTypes = ['application/pdf', 'application/msword', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document']
  const maxSize = 50 * 1024 * 1024 // 50MB

  if (!allowedTypes.includes(file.type)) {
    ElMessage.error('Only PDF, DOC, DOCX formats are supported')
    return false
  }

  if (file.size > maxSize) {
    ElMessage.error('File size cannot exceed 50MB')
    return false
  }

  return true
}

// Handle file selection
const handleFileChange = (file) => {
  if (beforeUpload(file.raw)) {
    uploadForm.file = file.raw
    ElMessage.success('File selected successfully')
  }
}

// Handle file removal
const handleFileRemove = () => {
  uploadForm.file = null
}

// Handle upload
const handleUpload = async () => {
  if (!uploadFormRef.value) return

  try {
    // Form validation
    await uploadFormRef.value.validate()

    if (!uploadForm.file) {
      ElMessage.error('Please select a file to upload')
      return
    }

    uploading.value = true
    uploadProgress.value = 0
    uploadStatus.value = 'active'
    progressText.value = 'Preparing upload...'

    // Create FormData
    const formData = new FormData()
    formData.append('file', uploadForm.file)
    formData.append('title', uploadForm.title)
    formData.append('authors', uploadForm.authors)
    formData.append('publication_type_id', uploadForm.publication_type_id)
    formData.append('publication_name', uploadForm.publication_name)
    formData.append('year', uploadForm.year)
    formData.append('abstract', uploadForm.abstract)

    // Simulate upload progress
    const progressInterval = setInterval(() => {
      if (uploadProgress.value < 90) {
        uploadProgress.value += Math.random() * 10
        progressText.value = `Uploading... ${Math.floor(uploadProgress.value)}%`
      }
    }, 200)

    // Call upload API
    const response = await uploadPaper(formData)

    clearInterval(progressInterval)

    if (response.success) {
      uploadProgress.value = 100
      uploadStatus.value = 'success'
      progressText.value = 'Upload successful!'

      ElMessage.success('Paper uploaded successfully')

      // Delayed redirect
      setTimeout(() => {
        router.push('/papers')
      }, 2000)
    } else {
      uploadStatus.value = 'exception'
      progressText.value = 'Upload failed'
      ElMessage.error(response.error || 'Upload failed')
    }
  } catch (error) {
    uploadStatus.value = 'exception'
    progressText.value = 'Upload failed'
    console.error('Upload failed:', error)
    ElMessage.error('Upload failed, please check your network connection or file format')
  } finally {
    uploading.value = false
  }
}

// Reset form
const resetForm = () => {
  if (uploadFormRef.value) {
    uploadFormRef.value.resetFields()
  }
  if (uploadRef.value) {
    uploadRef.value.clearFiles()
  }
  uploadForm.file = null
  uploadProgress.value = 0
  uploadStatus.value = ''
  progressText.value = ''
}

// 组件挂载时获取文献类型
onMounted(() => {
  fetchPublicationTypes()
})
</script>

<style scoped>
.upload-card {
  width: 100%;
  margin: 0 auto;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
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
}

:deep(.el-upload-dragger:hover) {
  border-color: #409EFF;
  background-color: #f0f9ff;
}

:deep(.el-upload-dragger .el-icon--upload) {
  font-size: 48px;
  color: #c0c4cc;
  margin: 40px 0 16px;
}

:deep(.el-upload__text) {
  color: #606266;
  font-size: 14px;
}

:deep(.el-upload__text em) {
  color: #409EFF;
  font-style: normal;
  text-decoration: underline;
}

:deep(.el-upload__tip) {
  color: #909399;
  font-size: 12px;
  margin-top: 8px;
}

.upload-progress {
  width: 100%;
  padding: 20px;
  background-color: #f8f9fa;
  border-radius: 8px;
  border: 1px solid #e9ecef;
}

.progress-text {
  text-align: center;
  margin: 10px 0 0 0;
  color: #666;
  font-size: 14px;
}

/* 表单样式优化 */
:deep(.el-form-item__label) {
  font-weight: 600;
  color: #333;
}

:deep(.el-input__inner) {
  border-radius: 6px;
}

:deep(.el-select .el-input__inner) {
  border-radius: 6px;
}

:deep(.el-textarea__inner) {
  border-radius: 6px;
}

:deep(.el-button) {
  border-radius: 6px;
  font-weight: 600;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .upload-card {
    max-width: 100%;
  }
  
  .upload-form {
    padding: 10px;
  }
  
  :deep(.el-form-item__label) {
    font-size: 14px;
  }
  
  :deep(.el-upload-dragger) {
    height: 140px;
  }
  
  :deep(.el-upload-dragger .el-icon--upload) {
    font-size: 36px;
    margin: 20px 0 12px;
  }
}
</style> 