<template>
  <PageLayout 
    title="前端环境测试" 
    subtitle="验证Vue3和Element Plus组件功能"
    centered
    :show-header="true"
  >
    <template #headerActions>
      <el-button @click="$router.push('/home')">返回首页</el-button>
    </template>
    
    <el-card style="width: 100%;">
      <el-row :gutter="20">
        <el-col :span="12">
          <h3>✅ Vue3 测试</h3>
          <p>当前时间: {{ currentTime }}</p>
          <p>计数器: {{ counter }}</p>
          <el-button @click="increment" type="primary">
            <el-icon><Plus /></el-icon>
            增加
          </el-button>
        </el-col>
        <el-col :span="12">
          <h3>✅ Element Plus 测试</h3>
          <el-alert title="测试成功" type="success" show-icon />
          <br>
          <el-button type="success" @click="showMessage">显示消息</el-button>
        </el-col>
      </el-row>
    </el-card>
  </PageLayout>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import dayjs from 'dayjs'
import PageLayout from '@/components/PageLayout.vue'

// 响应式数据
const currentTime = ref('')
const counter = ref(0)

// 更新时间
const updateTime = () => {
  currentTime.value = dayjs().format('YYYY-MM-DD HH:mm:ss')
}

// 计数器增加
const increment = () => {
  counter.value++
}

// 显示消息
const showMessage = () => {
  ElMessage.success('Element Plus 组件正常工作！')
}

// 组件挂载时更新时间
onMounted(() => {
  updateTime()
  setInterval(updateTime, 1000)
})
</script>

<style scoped>
h3 {
  color: #409eff;
  margin-bottom: 15px;
}

p {
  margin: 10px 0;
}

.el-button {
  margin: 10px 0;
}
</style> 