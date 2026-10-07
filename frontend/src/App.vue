<template>
  <div id="app">
    <header class="app-header">
      <h1>Research Paper Analysis and Recommendation System</h1>
      <div class="header-actions">
        <el-button @click="loadStats" :icon="Refresh" circle class="refresh-btn" />
        <el-popconfirm
          title="Are you sure to clear the knowledge base?"
          @confirm="clearDB"
        >
          <template #reference>
            <el-button type="danger" :icon="Delete" class="clear-btn">Clear Database</el-button>
          </template>
        </el-popconfirm>
        <el-tag v-if="stats" type="info" class="doc-count">
          Documents: {{ stats.total_documents }}
        </el-tag>
      </div>
    </header>

    <main class="app-main">
      <div class="panel">
        <UploadSection @upload-success="loadStats" />
      </div>

      <div class="panel">
        <QASection />
      </div>

      <div class="panel">
        <SummarySection />
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Refresh, Delete } from '@element-plus/icons-vue'
import UploadSection from './components/UploadSection.vue'
import QASection from './components/QASection.vue'
import SummarySection from './components/SummarySection.vue'
import { getStats, clearDatabase } from './api'

const stats = ref(null)

const loadStats = async () => {
  try {
    const response = await getStats()
    stats.value = response.data
  } catch (error) {
    console.error('Failed to load statistics', error)
  }
}

const clearDB = async () => {
  try {
    await clearDatabase()
    ElMessage.success('Knowledge base cleared successfully')
    loadStats()
  } catch (error) {
    ElMessage.error('Failed to clear database')
  }
}

onMounted(() => {
  loadStats()
})
</script>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
  background: #F5F7FA;
  min-height: 100vh;
}

#app {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.app-header {
  background: #FFFFFF;
  padding: 20px 40px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.08);
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.app-header h1 {
  color: #303133;
  font-size: 24px;
  font-weight: 600;
  letter-spacing: -0.5px;
}

.header-actions {
  display: flex;
  gap: 12px;
  align-items: center;
}

.refresh-btn {
  transition: all 0.3s ease;
}

.refresh-btn:hover {
  transform: rotate(180deg);
  background-color: #ECF5FF;
  border-color: #409EFF;
  color: #409EFF;
}

.refresh-btn:active {
  transform: rotate(180deg) scale(0.95);
}

.clear-btn {
  transition: all 0.3s ease;
}

.clear-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(245, 108, 108, 0.3);
}

.clear-btn:active {
  transform: translateY(0);
  box-shadow: 0 2px 4px rgba(245, 108, 108, 0.2);
}

.doc-count {
  font-weight: 500;
  padding: 8px 16px;
  border-radius: 4px;
}

.app-main {
  flex: 1;
  display: grid;
  grid-template-columns: 1fr 1fr 1fr;
  gap: 20px;
  padding: 24px 40px;
  max-width: 2000px;
  width: 100%;
  margin: 0 auto;
}

.panel {
  min-height: 600px;
  display: flex;
  flex-direction: column;
}

@media (max-width: 1400px) {
  .app-main {
    grid-template-columns: 1fr 1fr;
  }
}

@media (max-width: 900px) {
  .app-main {
    grid-template-columns: 1fr;
  }
}
</style>

