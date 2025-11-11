<template>
  <el-dialog
    v-model="dialogVisible"
    :title="mode === 'add' ? '添加用户' : '编辑用户'"
    width="500px"
    :before-close="handleClose"
  >
    <el-form
      ref="formRef"
      :model="formData"
      :rules="rules"
      label-width="100px"
      label-position="left"
    >
      <el-form-item v-if="mode === 'edit'" label="用户ID">
        <el-input v-model="formData.id" disabled />
      </el-form-item>
      
      <el-form-item label="用户名" prop="username">
        <el-input v-model="formData.username" placeholder="请输入用户名" />
      </el-form-item>
      
      <el-form-item label="邮箱" prop="email">
        <el-input v-model="formData.email" placeholder="请输入邮箱地址" />
      </el-form-item>
      
      <el-form-item v-if="mode === 'add'" label="密码" prop="password">
        <el-input 
          v-model="formData.password" 
          type="password"
          placeholder="请输入密码（不少于6位）"
          show-password
        />
      </el-form-item>
      
      <el-form-item label="角色" prop="role">
        <el-select v-model="formData.role" placeholder="请选择角色" style="width: 100%">
          <el-option label="普通用户" value="user" />
          <el-option label="管理员" value="admin" />
        </el-select>
      </el-form-item>
      
      <el-form-item label="状态" prop="status">
        <el-radio-group v-model="formData.status">
          <el-radio :label="1">启用</el-radio>
          <el-radio :label="0">禁用</el-radio>
        </el-radio-group>
      </el-form-item>
      
      <el-form-item v-if="mode === 'edit'" label="注册时间">
        <el-input v-model="displayCreatedAt" disabled />
      </el-form-item>
      
      <el-form-item v-if="mode === 'edit'" label="最后登录">
        <el-input v-model="displayLastLogin" disabled />
      </el-form-item>
    </el-form>
    
    <template #footer>
      <div class="dialog-footer">
        <el-button @click="handleClose">取消</el-button>
        <el-button type="primary" @click="handleSubmit" :loading="loading">
          {{ mode === 'add' ? '创建' : '更新' }}
        </el-button>
      </div>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { updateUser, createUser } from '@/api/admin'

// 定义组件 props
const props = defineProps({
  visible: {
    type: Boolean,
    default: false
  },
  user: {
    type: Object,
    default: () => ({})
  },
  mode: {
    type: String,
    default: 'edit', // 'add' or 'edit'
    validator: (value) => ['add', 'edit'].includes(value)
  }
})

// 定义组件 emits
const emit = defineEmits(['update:visible', 'refresh'])

// 响应式数据
const formRef = ref()
const loading = ref(false)
const formData = ref({
  id: '',
  username: '',
  email: '',
  password: '',
  role: 'user',
  status: 1,
  created_at: '',
  last_login: ''
})

// 表单验证规则
const rules = computed(() => {
  const baseRules = {
    username: [
      { required: true, message: '请输入用户名', trigger: 'blur' },
      { min: 2, max: 50, message: '用户名长度在 2 到 50 个字符', trigger: 'blur' }
    ],
    email: [
      { required: true, message: '请输入邮箱地址', trigger: 'blur' },
      { type: 'email', message: '请输入正确的邮箱地址', trigger: 'blur' }
    ],
    role: [
      { required: true, message: '请选择角色', trigger: 'change' }
    ]
  }
  
  // 添加模式需要密码验证
  if (props.mode === 'add') {
    baseRules.password = [
      { required: true, message: '请输入密码', trigger: 'blur' },
      { min: 6, max: 50, message: '密码长度在 6 到 50 个字符', trigger: 'blur' }
    ]
  }
  
  return baseRules
})

// 计算属性
const dialogVisible = computed({
  get: () => props.visible,
  set: (val) => emit('update:visible', val)
})

const displayCreatedAt = computed(() => {
  return formData.value.created_at 
    ? new Date(formData.value.created_at).toLocaleString('zh-CN')
    : '无'
})

const displayLastLogin = computed(() => {
  return formData.value.last_login 
    ? new Date(formData.value.last_login).toLocaleString('zh-CN')
    : '从未登录'
})

// 监听模式和用户数据变化
watch(
  [() => props.mode, () => props.user],
  ([newMode, newUser]) => {
    if (newMode === 'add') {
      // 添加模式，重置表单
      formData.value = {
        id: '',
        username: '',
        email: '',
        password: '',
        role: 'user',
        status: 1,
        created_at: '',
        last_login: ''
      }
    } else if (newUser && Object.keys(newUser).length > 0) {
      // 编辑模式，填充用户数据
      formData.value = {
        id: newUser.id || '',
        username: newUser.username || '',
        email: newUser.email || '',
        password: '', // 编辑模式不显示密码
        role: newUser.role || 'user',
        status: newUser.status !== undefined ? Number(newUser.status) : 1,
        created_at: newUser.created_at || '',
        last_login: newUser.last_login || ''
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
      username: formData.value.username,
      email: formData.value.email,
      role: formData.value.role,
      status: formData.value.status
    }
    
    // 添加模式需要包含密码
    if (props.mode === 'add') {
      submitData.password = formData.value.password
    }
    
    let response
    if (props.mode === 'add') {
      // 调用创建用户API
      response = await createUser(submitData)
    } else {
      // 调用更新用户API
      response = await updateUser(formData.value.id, submitData)
    }
    
    if (response.success) {
      ElMessage.success(props.mode === 'add' ? '用户创建成功' : '用户信息更新成功')
      emit('refresh')
      handleClose()
    } else {
      ElMessage.error(response.error || (props.mode === 'add' ? '创建用户失败' : '更新用户信息失败'))
    }
  } catch (error) {
    if (error !== false) { // 不是表单验证错误
      console.error('操作失败:', error)
      ElMessage.error(props.mode === 'add' ? '创建用户失败' : '更新用户信息失败')
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
</style> 