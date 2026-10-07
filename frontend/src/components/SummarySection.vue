<template>
  <div class="summary-section">
    <h2>Summary & Recommendations</h2>
    
    <el-button 
      type="primary" 
      @click="generateSummary" 
      :loading="loading"
      :disabled="loading"
      class="generate-btn"
    >
      {{ loading ? 'Generating...' : 'Generate Summary' }}
    </el-button>
    
    <div v-if="summaryData" class="content-container">
      <div class="summary-box">
        <h3>Paper Summary</h3>
        <div class="summary-text">{{ summaryData.summary }}</div>
      </div>
      
      <div class="recommendations-box">
        <h3>Recommended Articles (APA 7)</h3>
        <div v-if="summaryData.recommendations && summaryData.recommendations.length > 0" class="recommendations-list">
          <div 
            v-for="(rec, index) in summaryData.recommendations" 
            :key="index" 
            class="recommendation-item"
          >
            <span class="rec-number">{{ index + 1 }}.</span>
            <span class="rec-text">{{ rec }}</span>
          </div>
        </div>
        <div v-else class="empty-recommendations">
          No recommendations available
        </div>
      </div>
    </div>
    
    <div v-else-if="!loading" class="empty-state">
      Click "Generate Summary" to analyze the uploaded paper and get recommendations
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { ElMessage } from 'element-plus'
import { getSummary } from '../api'

const loading = ref(false)
const summaryData = ref(null)

const generateSummary = async () => {
  loading.value = true
  summaryData.value = null
  
  try {
    const response = await getSummary()
    summaryData.value = response.data
    ElMessage.success('Summary generated successfully!')
  } catch (error) {
    ElMessage.error(error.response?.data?.error || 'Failed to generate summary')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.summary-section {
  padding: 32px;
  background: #FFFFFF;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  height: 100%;
  display: flex;
  flex-direction: column;
  transition: box-shadow 0.3s ease;
}

.summary-section:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

h2 {
  margin-top: 0;
  margin-bottom: 24px;
  color: #303133;
  font-size: 20px;
  font-weight: 600;
}

.generate-btn {
  width: 100%;
  height: 44px;
  font-size: 15px;
  font-weight: 500;
  margin-bottom: 24px;
  transition: all 0.3s ease;
}

.generate-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(64, 158, 255, 0.3);
}

.generate-btn:active {
  transform: translateY(0);
  box-shadow: 0 2px 6px rgba(64, 158, 255, 0.2);
}

.content-container {
  flex: 1;
  max-height: 70dvh;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.content-container::-webkit-scrollbar {
  width: 6px;
}

.content-container::-webkit-scrollbar-track {
  background: #E4E7ED;
  border-radius: 3px;
}

.content-container::-webkit-scrollbar-thumb {
  background: #C0C4CC;
  border-radius: 3px;
  transition: background 0.3s ease;
}

.content-container::-webkit-scrollbar-thumb:hover {
  background: #909399;
}

.summary-box, .recommendations-box {
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

h3 {
  margin-top: 0;
  margin-bottom: 16px;
  color: #409EFF;
  font-size: 16px;
  font-weight: 600;
}

.summary-text {
  color: #606266;
  line-height: 1.8;
  font-size: 14px;
  text-align: justify;
}

.recommendations-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.recommendation-item {
  display: flex;
  gap: 8px;
  padding: 12px;
  background: #FFFFFF;
  border-radius: 6px;
  transition: all 0.3s ease;
  border: 1px solid #E4E7ED;
}

.recommendation-item:hover {
  transform: translateX(4px);
  box-shadow: 0 2px 8px rgba(64, 158, 255, 0.15);
  border-color: #409EFF;
}

.rec-number {
  color: #409EFF;
  font-weight: 600;
  flex-shrink: 0;
}

.rec-text {
  color: #606266;
  line-height: 1.6;
  font-size: 13px;
}

.empty-recommendations, .empty-state {
  color: #909399;
  text-align: center;
  padding: 40px 20px;
  font-size: 14px;
  line-height: 1.6;
}
</style>
