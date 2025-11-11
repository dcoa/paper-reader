<template>
  <el-dialog
    v-model="dialogVisible"
    title="编辑文献"
    width="700px"
    :before-close="handleClose"
  >
    <el-form
      ref="formRef"
      :model="formData"
      :rules="rules"
      label-width="120px"
      label-position="left"
    >
      <el-row :gutter="20">
        <el-col :span="24">
          <el-form-item label="文献ID">
            <el-input v-model="formData.id" disabled />
          </el-form-item>
        </el-col>
        
        <el-col :span="24">
          <el-form-item label="文献标题" prop="title">
            <el-input 
              v-model="formData.title" 
              placeholder="请输入文献标题" 
              type="textarea"
              :rows="2"
            />
          </el-form-item>
        </el-col>
        
        <el-col :span="12">
          <el-form-item label="作者" prop="authors">
            <el-input v-model="formData.authors" placeholder="请输入作者" />
          </el-form-item>
        </el-col>
        
        <el-col :span="12">
          <el-form-item label="发表年份" prop="year">
            <el-input-number 
              v-model="formData.year" 
              :min="1900" 
              :max="2030"
              style="width: 100%"
            />
          </el-form-item>
        </el-col>
        
        <el-col :span="12">
          <el-form-item label="文献类型" prop="publication_type">
            <el-select v-model="formData.publication_type" placeholder="请选择文献类型" style="width: 100%">
              <el-option label="期刊论文" value="journal" />
              <el-option label="会议论文" value="conference" />
              <el-option label="学位论文" value="thesis" />
              <el-option label="书籍" value="book" />
            </el-select>
          </el-form-item>
        </el-col>
        
        <el-col :span="12">
          <el-form-item label="期刊/会议" prop="journal">
            <el-input v-model="formData.journal" placeholder="请输入期刊或会议名称" />
          </el-form-item>
        </el-col>
        
        <el-col :span="12">
          <el-form-item label="卷号">
            <el-input v-model="formData.volume" placeholder="请输入卷号" />
          </el-form-item>
        </el-col>
        
        <el-col :span="12">
          <el-form-item label="期号">
            <el-input v-model="formData.issue" placeholder="请输入期号" />
          </el-form-item>
        </el-col>
        
        <el-col :span="12">
          <el-form-item label="页码">
            <el-input v-model="formData.pages" placeholder="例如：123-135" />
          </el-form-item>
        </el-col>
        
        <el-col :span="12">
          <el-form-item label="DOI">
            <el-input v-model="formData.doi" placeholder="请输入DOI" />
          </el-form-item>
        </el-col>
        
        <el-col :span="24">
          <el-form-item label="摘要">
            <el-input 
              v-model="formData.abstract" 
              placeholder="请输入文献摘要"
              type="textarea"
              :rows="3"
            />
          </el-form-item>
        </el-col>
        
        <el-col :span="24">
          <el-form-item label="关键词">
            <el-input 
              v-model="formData.keywords" 
              placeholder="请输入关键词，用逗号分隔"
            />
          </el-form-item>
        </el-col>
        
        <el-col :span="12">
          <el-form-item label="上传用户">
            <el-input v-model="formData.upload_user" disabled />
          </el-form-item>
        </el-col>
        
        <el-col :span="12">
          <el-form-item label="上传时间">
            <el-input v-model="displayUploadDate" disabled />
          </el-form-item>
        </el-col>
        
        <el-col :span="12">
          <el-form-item label="批注数量">
            <el-input v-model="formData.annotation_count" disabled />
          </el-form-item>
        </el-col>
        
        <el-col :span="12">
          <el-form-item label="文件名">
            <el-input v-model="formData.filename" disabled />
          </el-form-item>
        </el-col>
      </el-row>
    </el-form>
    
    <template #footer>
      <div class="dialog-footer">
        <el-button @click="handleClose">取消</el-button>
        <el-button type="primary" @click="handleSubmit" :loading="loading">
          确定
        </el-button>
      </div>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { updatePaper } from '@/api/admin'

// 定义组件 props
const props = defineProps({
  visible: {
    type: Boolean,
    default: false
  },
  paper: {
    type: Object,
    default: () => ({})
  }
})

// 定义组件 emits
const emit = defineEmits(['update:visible', 'refresh'])

// 响应式数据
const formRef = ref()
const loading = ref(false)
const formData = ref({
  id: '',
  title: '',
  authors: '',
  year: null,
  publication_type: '',
  journal: '',
  volume: '',
  issue: '',
  pages: '',
  doi: '',
  abstract: '',
  keywords: '',
  upload_user: '',
  upload_date: '',
  annotation_count: 0,
  filename: ''
})

// 表单验证规则
const rules = {
  title: [
    { required: true, message: '请输入文献标题', trigger: 'blur' },
    { min: 1, max: 500, message: '标题长度在 1 到 500 个字符', trigger: 'blur' }
  ],
  authors: [
    { required: true, message: '请输入作者', trigger: 'blur' },
    { max: 200, message: '作者长度不能超过 200 个字符', trigger: 'blur' }
  ],
  year: [
    { required: true, message: '请输入发表年份', trigger: 'blur' },
    { type: 'number', min: 1900, max: 2030, message: '请输入有效的年份', trigger: 'blur' }
  ],
  publication_type: [
    { required: true, message: '请选择文献类型', trigger: 'change' }
  ]
}

// 计算属性
const dialogVisible = computed({
  get: () => props.visible,
  set: (val) => emit('update:visible', val)
})

const displayUploadDate = computed(() => {
  return formData.value.upload_date 
    ? new Date(formData.value.upload_date).toLocaleString('zh-CN')
    : '无'
})

// 监听文献数据变化
watch(
  () => props.paper,
  (newPaper) => {
    if (newPaper && Object.keys(newPaper).length > 0) {
      formData.value = {
        id: newPaper.id || '',
        title: newPaper.title || '',
        authors: newPaper.authors || '',
        year: newPaper.year || null,
        publication_type: newPaper.publication_type || '',
        journal: newPaper.journal || '',
        volume: newPaper.volume || '',
        issue: newPaper.issue || '',
        pages: newPaper.pages || '',
        doi: newPaper.doi || '',
        abstract: newPaper.abstract || '',
        keywords: newPaper.keywords || '',
        upload_user: newPaper.upload_user || '',
        upload_date: newPaper.upload_date || '',
        annotation_count: newPaper.annotation_count || 0,
        filename: newPaper.filename || ''
      }
    }
  },
  { immediate: true, deep: true }
)

// 处理对话框关闭
const handleClose = () => {
  dialogVisible.value = false
  // 重置表单
  if (formRef.value) {
    formRef.value.resetFields()
  }
}

// 处理表单提交
const handleSubmit = async () => {
  if (!formRef.value) return
  
  try {
    // 验证表单
    await formRef.value.validate()
    
    loading.value = true
    
    // 准备提交数据
    const submitData = {
      title: formData.value.title,
      authors: formData.value.authors,
      year: formData.value.year,
      publication_type: formData.value.publication_type,
      journal: formData.value.journal,
      volume: formData.value.volume,
      issue: formData.value.issue,
      pages: formData.value.pages,
      doi: formData.value.doi,
      abstract: formData.value.abstract,
      keywords: formData.value.keywords
    }
    
    // 调用更新文献API
    const response = await updatePaper(formData.value.id, submitData)
    
    if (response.code === 200) {
      ElMessage.success('文献信息更新成功')
      emit('refresh')
      handleClose()
    } else {
      ElMessage.error(response.message || '更新文献信息失败')
    }
  } catch (error) {
    if (error !== false) { // 不是表单验证错误
      console.error('更新文献信息失败:', error)
      ElMessage.error('更新文献信息失败')
    }
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.dialog-footer {
  text-align: right;
}

:deep(.el-form-item__label) {
  font-weight: 500;
  color: #2c3e50;
}

:deep(.el-input.is-disabled .el-input__inner) {
  background-color: #f5f7fa;
  border-color: #e4e7ed;
  color: #909399;
}

:deep(.el-textarea.is-disabled .el-textarea__inner) {
  background-color: #f5f7fa;
  border-color: #e4e7ed;
  color: #909399;
}
</style> 