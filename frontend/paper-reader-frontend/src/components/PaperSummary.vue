<template>
  <div class="paper-summary">
    <!-- Header Toolbar -->
    <div class="summary-header">
      <div class="header-left">
        <h3>
          <el-icon><Document /></el-icon>
          Intelligent Paper Summary
        </h3>
        <p class="header-desc">Use AI to deeply analyze paper content and extract key information</p>
      </div>
      <div class="header-right">
        <!-- Main Action Buttons -->
        <div class="action-buttons">
          <!-- Analyze Button - Always Show -->
          <el-button
            type="primary"
            size="default"
            @click="startAnalysis"
            :loading="isAnalyzing"
            :disabled="!paperId || isAnalyzing"
            class="primary-action-btn"
          >
            <el-icon><MagicStick /></el-icon>
            {{ getButtonText() }}
          </el-button>

          <!-- Secondary Action Buttons -->
          <div class="secondary-actions">
            <!-- Delete Button -->
            <el-button
              v-if="analysisData && (analysisData.analysis_status === 'completed' || analysisData.analysis_status === 'failed')"
              type="danger"
              @click="deleteAnalysis"
              :loading="isDeleting"
              size="small"
              plain
              class="secondary-action-btn"
            >
              <el-icon><Delete /></el-icon>
              Delete
            </el-button>

            <!-- Stop Polling Button -->
            <el-button
              v-if="pollTimer && isAnalyzing"
              type="warning"
              @click="forceStop"
              size="small"
              plain
              class="secondary-action-btn"
            >
              <el-icon><Loading /></el-icon>
              Stop
            </el-button>
          </div>
        </div>
        
        <!-- 状态指示器 -->
        <div class="status-indicator">
          <el-tag 
            v-if="analysisData"
            :type="getStatusTagType()" 
            size="small"
            class="status-tag"
          >
            <el-icon class="status-icon"><Cpu /></el-icon>
            {{ getStatusText() }}
          </el-tag>
        </div>
      </div>
    </div>

    <!-- Analysis Status Display -->
    <div v-if="isAnalyzing" class="analysis-status">
      <div class="status-content">
        <el-icon class="rotating"><Loading /></el-icon>
        <div class="status-info">
          <h4>AI is deeply analyzing the paper...</h4>
          <p>{{ statusMessage }}</p>
        </div>
      </div>
      <el-progress
        :percentage="analysisProgress"
        :format="() => `${analysisProgress}%`"
        :color="progressColor"
      />
    </div>

    <!-- Analysis Results Display -->
    <div v-else-if="analysisData && analysisData.analysis_status === 'completed'" class="analysis-results">
      <!-- Summary Card -->
      <el-card class="summary-card" shadow="hover">
        <template #header>
          <div class="card-header">
            <span>
              <el-icon><Document /></el-icon>
              Paper Summary
            </span>
            <el-button
              type="text"
              @click="copySummary('summary')"
              :icon="DocumentCopy"
              size="small"
              :disabled="!analysisData.summary || analysisData.summary.trim() === ''"
            >
              Copy
            </el-button>
          </div>
        </template>
        <div class="summary-content">
          <p v-if="analysisData.summary && analysisData.summary.trim() !== ''">{{ analysisData.summary }}</p>
          <p v-else class="empty-text">No summary content available</p>
        </div>
      </el-card>

      <!-- Methodology Card -->
      <el-card class="summary-card" shadow="hover">
        <template #header>
          <div class="card-header">
            <span>
              <el-icon><Tools /></el-icon>
              Methodology Analysis
            </span>
            <el-button
              type="text"
              @click="copySummary('methodology')"
              :icon="DocumentCopy"
              size="small"
              :disabled="!analysisData.methodology || analysisData.methodology.trim() === ''"
            >
              Copy
            </el-button>
          </div>
        </template>
        <div class="summary-content">
          <p v-if="analysisData.methodology && analysisData.methodology.trim() !== ''">{{ analysisData.methodology }}</p>
          <p v-else class="empty-text">No methodology content available</p>
        </div>
      </el-card>

      <!-- Experiments Summary Card -->
      <el-card class="summary-card" shadow="hover">
        <template #header>
          <div class="card-header">
            <span>
              <el-icon><DataAnalysis /></el-icon>
              Experiments Summary
            </span>
            <el-button
              type="text"
              @click="copySummary('experiments')"
              :icon="DocumentCopy"
              size="small"
              :disabled="!analysisData.experiments || analysisData.experiments.trim() === ''"
            >
              Copy
            </el-button>
          </div>
        </template>
        <div class="summary-content">
          <p v-if="analysisData.experiments && analysisData.experiments.trim() !== ''">{{ analysisData.experiments }}</p>
          <p v-else class="empty-text">No experiments content available</p>
        </div>
      </el-card>

      <!-- Key Findings Card -->
      <el-card class="summary-card" shadow="hover">
        <template #header>
          <div class="card-header">
            <span>
              <el-icon><Star /></el-icon>
              Key Findings
            </span>
            <el-button
              type="text"
              @click="copySummary('key_findings')"
              :icon="DocumentCopy"
              size="small"
              :disabled="!analysisData.key_findings || analysisData.key_findings.trim() === ''"
            >
              Copy
            </el-button>
          </div>
        </template>
        <div class="summary-content">
          <p v-if="analysisData.key_findings && analysisData.key_findings.trim() !== ''">{{ analysisData.key_findings }}</p>
          <p v-else class="empty-text">No key findings available</p>
        </div>
      </el-card>

      <!-- Analysis Information -->
      <div class="analysis-info">
        <el-tag type="info" size="small">
          <el-icon><Clock /></el-icon>
          Analysis Time: {{ formatTime(analysisData.create_time) }}
        </el-tag>
        <el-tag type="success" size="small">
          <el-icon><Cpu /></el-icon>
          Model Used: {{ analysisData.model_used || 'DeepSeek R1' }}
        </el-tag>
      </div>
    </div>

    <!-- Empty State -->
    <div v-else class="empty-state">
      <el-icon size="64" color="#c0c4cc"><Document /></el-icon>
      <h3>No analysis results yet</h3>
      <p>Click the "Start Analysis" button to use AI to deeply analyze paper content</p>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted, onUnmounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { 
  Document, 
  MagicStick, 
  Delete, 
  Loading, 
  DocumentCopy, 
  Tools, 
  DataAnalysis, 
  Star, 
  Clock, 
  Cpu 
} from '@element-plus/icons-vue'
import { 
  getPaperAnalysis, 
  createPaperAnalysis, 
  getAnalysisStatus, 
  deletePaperAnalysis 
} from '@/api/analysis'
import dayjs from 'dayjs'

// Props
const props = defineProps({
  paperId: {
    type: [Number, String],
    required: true
  }
})

// Emits
const emits = defineEmits(['analysis-completed', 'analysis-failed'])

// 响应式数据
const analysisData = ref(null)
const isAnalyzing = ref(false)
const isDeleting = ref(false)
const analysisProgress = ref(0)
const statusMessage = ref('')
const pollTimer = ref(null)

// 计算属性
const progressColor = computed(() => {
  if (analysisProgress.value < 30) return '#409EFF'
  if (analysisProgress.value < 70) return '#E6A23C'
  return '#67C23A'
})

// Methods
const loadAnalysisData = async () => {
  try {
    const response = await getPaperAnalysis(props.paperId)

    if (response.success) {
      analysisData.value = response.data

      // If analyzing, start polling
      if (analysisData.value.analysis_status === 'processing') {
        startPolling()
      }
    } else {
      // 404 means no analysis results, which is normal
      if (response.status !== 404) {
        console.error('Failed to fetch analysis data:', response.error)
      }
    }
  } catch (error) {
    console.error('Exception fetching analysis data:', error)
  }
}

const startAnalysis = async () => {
  try {
    // If analysis results exist, confirm re-analysis
    if (analysisData.value && analysisData.value.analysis_status === 'completed') {
      await ElMessageBox.confirm(
        'This paper already has analysis results. Are you sure you want to re-analyze? This will overwrite existing results.',
        'Re-analysis Confirmation',
        {
          confirmButtonText: 'Re-analyze',
          cancelButtonText: 'Cancel',
          type: 'warning'
        }
      )
    }

    isAnalyzing.value = true
    analysisProgress.value = 0
    statusMessage.value = 'Starting analysis task...'

    // If existing results, use force parameter
    const forceReanalysis = analysisData.value && analysisData.value.analysis_status === 'completed'
    const response = await createPaperAnalysis(props.paperId, { force: forceReanalysis })

    if (response.success) {
      ElMessage.success(forceReanalysis ? 'Re-analysis task started' : 'Analysis task started')
      statusMessage.value = 'Analysis task started, processing...'
      analysisProgress.value = 10

      // Start polling to check status
      startPolling()
    } else {
      ElMessage.error(response.error || 'Failed to start analysis')
      isAnalyzing.value = false
    }
  } catch (error) {
    if (error !== 'cancel') {
      console.error('Failed to start analysis:', error)
      ElMessage.error('Failed to start analysis')
      isAnalyzing.value = false
    }
  }
}



const deleteAnalysis = async () => {
  try {
    await ElMessageBox.confirm(
      'Are you sure you want to delete this analysis result? This action cannot be undone.',
      'Delete Confirmation',
      {
        confirmButtonText: 'Delete',
        cancelButtonText: 'Cancel',
        type: 'warning'
      }
    )

    isDeleting.value = true

    const response = await deletePaperAnalysis(props.paperId)

    if (response.success) {
      ElMessage.success('Analysis result deleted')
      analysisData.value = null
    } else {
      ElMessage.error(response.error || 'Delete failed')
    }
  } catch (error) {
    if (error !== 'cancel') {
      console.error('Failed to delete analysis:', error)
      ElMessage.error('Delete failed')
    }
  } finally {
    isDeleting.value = false
  }
}

const startPolling = () => {
  if (pollTimer.value) {
    clearInterval(pollTimer.value)
  }

  pollTimer.value = setInterval(async () => {
    try {
      const response = await getAnalysisStatus(props.paperId)

      if (response.success) {
        const status = response.data.status

        if (status === 'completed') {
          // Analysis completed, fetch results
          await loadAnalysisData()
          stopPolling()
          isAnalyzing.value = false
          analysisProgress.value = 100
          statusMessage.value = 'Analysis completed!'
          ElMessage.success('Paper analysis completed')
          emits('analysis-completed', analysisData.value)
        } else if (status === 'failed') {
          // Analysis failed
          stopPolling()
          isAnalyzing.value = false
          ElMessage.error('Paper analysis failed')
          emits('analysis-failed')
        } else if (status === 'processing') {
          // Processing, update progress
          analysisProgress.value = Math.min(analysisProgress.value + 5, 90)
          statusMessage.value = 'Deeply analyzing paper content...'
        }
      }
    } catch (error) {
      console.error('Failed to check analysis status:', error)
    }
  }, 3000) // Check every 3 seconds
}

const stopPolling = () => {
  if (pollTimer.value) {
    clearInterval(pollTimer.value)
    pollTimer.value = null
  }
}

const copySummary = async (field) => {
  try {
    const content = analysisData.value[field]
    if (!content) {
      ElMessage.warning('Content is empty')
      return
    }

    await navigator.clipboard.writeText(content)
    ElMessage.success('Content copied to clipboard')
  } catch (error) {
    console.error('Copy failed:', error)
    ElMessage.error('Copy failed')
  }
}

const formatTime = (timeString) => {
  if (!timeString) return 'Unknown'
  return dayjs(timeString).format('YYYY-MM-DD HH:mm:ss')
}

const getButtonText = () => {
  if (isAnalyzing.value) {
    return 'Analyzing...'
  }

  if (!analysisData.value) {
    return 'Start Analysis'
  }

  switch (analysisData.value.analysis_status) {
    case 'completed':
      return 'Re-analyze'
    case 'processing':
      return 'Analyzing...'
    case 'failed':
      return 'Retry Analysis'
    default:
      return 'Start Analysis'
  }
}

const forceStop = () => {
  stopPolling()
  isAnalyzing.value = false
  ElMessage.warning('Polling stopped')
}

// Get status tag type
const getStatusTagType = () => {
  if (!analysisData.value) return 'info'

  switch (analysisData.value.analysis_status) {
    case 'completed':
      return 'success'
    case 'processing':
      return 'warning'
    case 'failed':
      return 'danger'
    default:
      return 'info'
  }
}

// Get status text
const getStatusText = () => {
  if (!analysisData.value) return 'Not analyzed'

  switch (analysisData.value.analysis_status) {
    case 'completed':
      return 'Completed'
    case 'processing':
      return 'Analyzing'
    case 'failed':
      return 'Failed'
    default:
      return 'Unknown status'
  }
}

// Watchers
watch(() => props.paperId, (newPaperId) => {
  if (newPaperId) {
    loadAnalysisData()
  }
}, { immediate: true })

// Lifecycle
onMounted(() => {
  if (props.paperId) {
    loadAnalysisData()
  }
})

onUnmounted(() => {
  stopPolling()
})
</script>

<style scoped>
.paper-summary {
  height: 100%;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.summary-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px;
  background: #f8f9fa;
  border-bottom: 1px solid #e4e7ed;
}

.header-left h3 {
  margin: 0 0 4px 0;
  color: #333;
  font-size: 18px;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 8px;
}

.header-desc {
  margin: 0;
  color: #666;
  font-size: 14px;
}

.header-right {
  display: flex;
  flex-direction: column;
  gap: 12px;
  align-items: flex-end;
}

.action-buttons {
  display: flex;
  align-items: center;
  gap: 12px;
}

.primary-action-btn {
  min-width: 120px;
  height: 40px;
  font-weight: 600;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(64, 158, 255, 0.3);
  transition: all 0.3s ease;
}

.primary-action-btn:hover {
  box-shadow: 0 4px 16px rgba(64, 158, 255, 0.4);
  transform: translateY(-1px);
}

.secondary-actions {
  display: flex;
  gap: 8px;
  align-items: center;
}

.secondary-action-btn {
  min-width: 60px;
  height: 32px;
  border-radius: 6px;
  font-size: 12px;
  transition: all 0.3s ease;
}

.secondary-action-btn:hover {
  transform: translateY(-1px);
}

.status-indicator {
  display: flex;
  justify-content: flex-end;
}

.status-tag {
  border-radius: 20px;
  padding: 4px 12px;
  font-size: 12px;
  font-weight: 500;
  border: none;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.status-icon {
  margin-right: 4px;
}

.analysis-status {
  padding: 30px;
  background: #f0f9ff;
  border-bottom: 1px solid #e4e7ed;
}

.status-content {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 16px;
}

.status-content .el-icon {
  font-size: 24px;
  color: #409EFF;
}

.rotating {
  animation: rotate 2s linear infinite;
}

@keyframes rotate {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.status-info h4 {
  margin: 0 0 4px 0;
  color: #333;
  font-size: 16px;
}

.status-info p {
  margin: 0;
  color: #666;
  font-size: 14px;
}

.analysis-results {
  flex: 1;
  padding: 20px;
  overflow-y: auto;
}

.summary-card {
  margin-bottom: 16px;
  border: 1px solid #e4e7ed;
  border-radius: 8px;
}

.summary-card:hover {
  border-color: #409EFF;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: 600;
  color: #333;
}

.card-header span {
  display: flex;
  align-items: center;
  gap: 8px;
}

.summary-content {
  line-height: 1.6;
  color: #555;
}

.summary-content p {
  margin: 0;
  white-space: pre-wrap;
  word-break: break-word;
}

.analysis-info {
  display: flex;
  gap: 12px;
  margin-top: 20px;
  padding-top: 16px;
  border-top: 1px solid #e4e7ed;
}

.analysis-info .el-tag {
  display: flex;
  align-items: center;
  gap: 4px;
}

.empty-state {
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  height: 100%;
  padding: 60px 20px;
  color: #666;
  text-align: center;
}

.empty-state h3 {
  margin: 16px 0 8px 0;
  color: #333;
  font-size: 18px;
}

.empty-state p {
  margin: 0;
  font-size: 14px;
  color: #999;
}

.empty-text {
  color: #999;
  font-style: italic;
  margin: 0;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .summary-header {
    flex-direction: column;
    gap: 16px;
    text-align: center;
  }
  
  .header-right {
    width: 100%;
    align-items: center;
    gap: 16px;
  }
  
  .action-buttons {
    flex-direction: column;
    gap: 12px;
    width: 100%;
    align-items: center;
  }
  
  .primary-action-btn {
    min-width: 200px;
    height: 44px;
  }
  
  .secondary-actions {
    justify-content: center;
    gap: 12px;
  }
  
  .secondary-action-btn {
    min-width: 80px;
    height: 36px;
  }
  
  .status-indicator {
    justify-content: center;
  }
  
  .analysis-results {
    padding: 16px;
  }
  
  .status-content {
    flex-direction: column;
    text-align: center;
  }
}

@media (max-width: 480px) {
  .summary-header {
    padding: 16px;
  }
  
  .header-left h3 {
    font-size: 16px;
  }
  
  .header-desc {
    font-size: 12px;
  }
  
  .primary-action-btn {
    min-width: 100%;
    height: 48px;
    font-size: 14px;
  }
  
  .secondary-actions {
    width: 100%;
    justify-content: space-around;
  }
  
  .secondary-action-btn {
    flex: 1;
    min-width: auto;
    max-width: 100px;
  }
}
</style> 