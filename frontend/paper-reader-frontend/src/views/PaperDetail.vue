<template>
  <div class="paper-detail-container">
    <!-- Page Header -->
    <div class="page-header">
      <div class="header-left">
        <h1 class="page-title">Paper Details</h1>
        <p class="page-subtitle">View paper details, add annotations and AI Q&A</p>
      </div>
      <div class="header-right">
        <el-button @click="$router.push('/home')">
          <el-icon><house /></el-icon>
          Home
        </el-button>
        <el-button @click="$router.push('/papers')">
          <el-icon><document /></el-icon>
          Papers
        </el-button>
      </div>
    </div>

    <!-- Split Screen Layout Container -->
    <div class="split-screen-container">
      <!-- Left Panel: Paper Info and PDF Preview -->
      <div class="left-panel">
        <!-- Paper Info Bar -->
        <div class="paper-info-bar" v-loading="loading">
          <div class="info-content" v-if="paperInfo.paper_id">
            <div class="paper-title">{{ paperInfo.title }}</div>
            <div class="paper-meta">
              <span class="author">{{ paperInfo.authors }}</span>
              <span class="separator">·</span>
              <el-tag size="small">{{ paperInfo.publication_type }}</el-tag>
              <span class="separator">·</span>
              <span class="year">{{ paperInfo.year }}</span>
              <span class="separator">·</span>
              <span class="journal">{{ paperInfo.publication_name }}</span>
            </div>
          </div>
          <div class="info-actions">
            <el-button size="small" @click="showPaperInfo = !showPaperInfo">
              <el-icon><info-filled /></el-icon>
              Details
            </el-button>
            <el-button size="small" type="primary" @click="downloadPaper">
              <el-icon><download /></el-icon>
              Download
            </el-button>

          </div>
        </div>

        <!-- Detailed Info Expand Area -->
        <div v-if="showPaperInfo" class="paper-details">
          <div class="details-content">
            <div class="detail-item">
              <label>Authors:</label>
              <span>{{ paperInfo.authors }}</span>
            </div>
            <div class="detail-item">
              <label>Journal/Conference:</label>
              <span>{{ paperInfo.publication_name }}</span>
            </div>
            <div class="detail-item">
              <label>Publication Year:</label>
              <span>{{ paperInfo.year }}</span>
            </div>
            <div class="detail-item">
              <label>Upload Time:</label>
              <span>{{ formatDate(paperInfo.upload_time) }}</span>
            </div>
            <div v-if="paperInfo.abstract" class="abstract-section">
              <label>Abstract:</label>
              <p>{{ paperInfo.abstract }}</p>
            </div>
          </div>
        </div>

        <!-- PDF Preview Area -->
        <div class="pdf-container">
          <SimplePDFViewer
            v-if="pdfSrc"
            :src="pdfSrc"
            :paper-id="paperInfo.paper_id"
            @load="handlePDFLoad"
            @error="handlePDFError"
          />
          <div v-else class="pdf-placeholder">
            <el-icon size="64" color="#c0c4cc"><document /></el-icon>
            <p>PDF preview feature is enabled</p>
            <p>Loading PDF file...</p>
          </div>
        </div>
      </div>

      <!-- Right Panel: Function Panel -->
      <div class="right-panel">
        <!-- Function Tabs -->
        <div class="function-tabs">
          <el-tabs v-model="activeTab" class="panel-tabs">
            <el-tab-pane label="Annotations" name="annotations">
              <div class="annotation-section">
                <AnnotationPanel
                  :paper-id="paperInfo.paper_id"
                  @add="handleAnnotationAdd"
                  @delete="handleAnnotationDelete"
                  @edit="handleAnnotationEdit"
                  ref="annotationPanelRef"
                />
              </div>
            </el-tab-pane>
            <el-tab-pane label="AI Summary" name="summary">
              <div class="summary-section">
                <PaperSummary
                  :paper-id="paperInfo.paper_id"
                  @analysis-completed="handleAnalysisCompleted"
                  @analysis-failed="handleAnalysisFailed"
                />
              </div>
            </el-tab-pane>
          </el-tabs>
        </div>
      </div>
    </div>

    <!-- AI Assistant Floating Button -->
    <div class="ai-assistant-fab" @click="toggleAIChat">
      <el-icon size="24"><chat-dot-round /></el-icon>
    </div>

    <!-- AI Chat Floating Window -->
    <div
      v-if="showAIChat"
      class="ai-chat-dialog"
      :style="{
        left: aiChatPosition.x + 'px',
        top: aiChatPosition.y + 'px',
        width: aiChatSize.width + 'px',
        height: aiChatSize.height + 'px'
      }"
    >
      <!-- Dialog Header - Draggable -->
      <div
        class="ai-chat-header"
        @mousedown="startDragDialog"
        @touchstart="startDragDialog"
      >
        <div class="header-title">
          <el-icon><chat-dot-round /></el-icon>
          <span>AI Assistant</span>
        </div>
        <div class="header-actions">
          <el-button
            type="text"
            size="small"
            @click="minimizeAIChat"
            style="color: #666;"
          >
            <el-icon><minus /></el-icon>
          </el-button>
          <el-button
            type="text"
            size="small"
            @click="closeAIChat"
            style="color: #666;"
          >
            <el-icon><close /></el-icon>
          </el-button>
        </div>
      </div>

      <!-- Dialog Content -->
      <div class="ai-chat-content">
        <AIChat
          :paper-id="paperInfo.paper_id"
          :paper-context="paperInfo.abstract || ''"
          @message-sent="handleAIMessageSent"
          @message-received="handleAIMessageReceived"
        />
      </div>

      <!-- Resize Handle -->
      <div
        class="resize-handle"
        @mousedown="startResize"
        @touchstart="startResize"
      ></div>
    </div>


  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, nextTick } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { getPaperDetail, downloadPaper as downloadPaperFile } from '@/api/papers'
import SimplePDFViewer from '@/components/SimplePDFViewer.vue'
import AnnotationPanel from '@/components/AnnotationPanel.vue'
import AIChat from '@/components/AIChat.vue'
import PaperSummary from '@/components/PaperSummary.vue'
import { useUserStore } from '@/store/user'
import dayjs from 'dayjs'
import { ChatDotRound, Close, Minus, Setting, House, Document, InfoFilled, Download } from '@element-plus/icons-vue'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()

// Loading state
const loading = ref(false)

// Paper info
const paperInfo = ref({})

// UI state
const showPaperInfo = ref(false)
const activeTab = ref('annotations')

// Component references
const annotationPanelRef = ref()

// AI floating window variables
const showAIChat = ref(false)
const aiChatPosition = ref({ x: window.innerWidth - 420, y: 100 })
const aiChatSize = ref({ width: 400, height: 600 })
const isDraggingDialog = ref(false)
const isResizing = ref(false)
const dragStartPos = ref({ x: 0, y: 0 })
const resizeStartPos = ref({ x: 0, y: 0 })
const resizeStartSize = ref({ width: 0, height: 0 })

// Computed properties
const pdfSrc = computed(() => {
  console.log('=== PaperDetail pdfSrc calculation ===')
  console.log('paperInfo:', paperInfo.value)
  console.log('paper_id:', paperInfo.value.paper_id)

  if (paperInfo.value.paper_id) {
    const url = `/api/papers/${paperInfo.value.paper_id}/download`
    console.log('Generated PDF URL:', url)
    return url
  }
  console.log('Returning null - no paper_id')
  return null
})

// Format date
const formatDate = (dateString) => {
  return dayjs(dateString).format('YYYY-MM-DD HH:mm')
}

// Get paper details
const fetchPaperDetail = async () => {
  loading.value = true
  try {
    const paperId = route.params.id
    const response = await getPaperDetail(paperId)

    if (response.success) {
      paperInfo.value = response.data
    } else {
      ElMessage.error(response.error || 'Failed to get paper details')
      router.push('/papers')
    }
  } catch (error) {
    console.error('Failed to get paper details:', error)
    ElMessage.error('Failed to get paper details')
    router.push('/papers')
  } finally {
    loading.value = false
  }
}

// AI chat event handlers
const handleAIMessageSent = (message) => {
  console.log('AI message sent:', message)
}

const handleAIMessageReceived = (message) => {
  console.log('AI message received:', message)
}

// PDF event handlers
const handlePDFLoad = () => {
  console.log('PDF loaded successfully')
}

const handlePDFError = () => {
  console.log('PDF loading failed')
  ElMessage.error('PDF loading failed, please check if the file exists')
}

// Annotation event handlers
const handleAnnotationAdd = (annotation) => {
  console.log('Annotation added:', annotation)
  ElMessage.success('Annotation added successfully')
}

const handleAnnotationDelete = (annotationId) => {
  console.log('Annotation deleted:', annotationId)
  ElMessage.success('Annotation deleted successfully')
}

const handleAnnotationEdit = (editData) => {
  console.log('Annotation edited:', editData)
  ElMessage.success('Annotation updated successfully')
}

// Paper analysis event handlers
const handleAnalysisCompleted = (analysisData) => {
  console.log('Paper analysis completed:', analysisData)
  ElMessage.success('Paper analysis completed!')
}

const handleAnalysisFailed = () => {
  console.log('Paper analysis failed')
  ElMessage.error('Paper analysis failed, please try again later')
}

// Download paper
const downloadPaper = async () => {
  try {
    const paperId = route.params.id
    const response = await downloadPaperFile(paperId)

    // Create download link
    const blob = new Blob([response], { type: 'application/pdf' })
    const url = window.URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `${paperInfo.value.title || 'paper'}.pdf`
    a.click()
    window.URL.revokeObjectURL(url)

    ElMessage.success('Download successful')
  } catch (error) {
    console.error('Download failed:', error)
    ElMessage.error('Download failed')
  }
}

// AI floating window functions
const initializeAIChatSettings = () => {
  console.log('=== Initialize AI chat settings ===')

  // Set default values
  const defaultPosition = { x: Math.max(50, window.innerWidth - 450), y: 100 }
  const defaultSize = { width: 400, height: 600 }

  // Read user settings from localStorage
  const savedSettings = localStorage.getItem('ai-chat-settings')
  console.log('Saved settings:', savedSettings)

  if (savedSettings) {
    try {
      const { position, size, show } = JSON.parse(savedSettings)
      if (position) {
        aiChatPosition.value = position
        console.log('Restored position:', position)
      }
      if (size) {
        aiChatSize.value = size
        console.log('Restored size:', size)
      }
      // Note: Do not auto-restore display state, let user control it manually
      console.log('Display state not auto-restored, user needs to click to show')
    } catch (error) {
      console.warn('Failed to parse AI chat settings:', error)
      aiChatPosition.value = defaultPosition
      aiChatSize.value = defaultSize
    }
  } else {
    console.log('No saved settings, using default values')
    aiChatPosition.value = defaultPosition
    aiChatSize.value = defaultSize
  }

  // Ensure position is within screen bounds
  const maxX = window.innerWidth - aiChatSize.value.width
  const maxY = window.innerHeight - aiChatSize.value.height

  aiChatPosition.value.x = Math.min(Math.max(0, aiChatPosition.value.x), maxX)
  aiChatPosition.value.y = Math.min(Math.max(0, aiChatPosition.value.y), maxY)

  console.log('Final position:', aiChatPosition.value)
  console.log('Final size:', aiChatSize.value)
  console.log('Display state:', showAIChat.value)
}

const saveAIChatSettings = () => {
  const settings = {
    position: aiChatPosition.value,
    size: aiChatSize.value,
    show: showAIChat.value
  }
  localStorage.setItem('ai-chat-settings', JSON.stringify(settings))
  console.log('Saved AI chat settings:', settings)
}

// Control floating window show/hide
const toggleAIChat = () => {
  console.log('=== Toggle AI chat window ===')
  console.log('State before toggle:', showAIChat.value)

  showAIChat.value = !showAIChat.value

  console.log('State after toggle:', showAIChat.value)
  console.log('Current position:', aiChatPosition.value)
  console.log('Current size:', aiChatSize.value)
  console.log('paperInfo.paper_id:', paperInfo.value.paper_id)

  saveAIChatSettings()
}

const closeAIChat = () => {
  showAIChat.value = false
  saveAIChatSettings()
}

const minimizeAIChat = () => {
  showAIChat.value = false
  saveAIChatSettings()
}

// Drag dialog position
const startDragDialog = (event) => {
  event.preventDefault()

  isDraggingDialog.value = true
  dragStartPos.value = {
    x: (event.type === 'mousedown' ? event.clientX : event.touches[0].clientX) - aiChatPosition.value.x,
    y: (event.type === 'mousedown' ? event.clientY : event.touches[0].clientY) - aiChatPosition.value.y
  }

  // Add global event listeners
  if (event.type === 'mousedown') {
    document.addEventListener('mousemove', handleDragDialog)
    document.addEventListener('mouseup', stopDragDialog)
  } else {
    document.addEventListener('touchmove', handleDragDialog, { passive: false })
    document.addEventListener('touchend', stopDragDialog)
  }

  // Add drag styles
  document.body.style.cursor = 'move'
  document.body.style.userSelect = 'none'
}

const handleDragDialog = (event) => {
  if (!isDraggingDialog.value) return

  event.preventDefault()

  const clientX = event.type === 'mousemove' ? event.clientX : event.touches[0].clientX
  const clientY = event.type === 'mousemove' ? event.clientY : event.touches[0].clientY

  let newX = clientX - dragStartPos.value.x
  let newY = clientY - dragStartPos.value.y

  // Limit to screen bounds
  const maxX = window.innerWidth - aiChatSize.value.width
  const maxY = window.innerHeight - aiChatSize.value.height

  newX = Math.min(Math.max(0, newX), maxX)
  newY = Math.min(Math.max(0, newY), maxY)

  aiChatPosition.value = { x: newX, y: newY }
}

const stopDragDialog = () => {
  isDraggingDialog.value = false

  // Remove global event listeners
  document.removeEventListener('mousemove', handleDragDialog)
  document.removeEventListener('mouseup', stopDragDialog)
  document.removeEventListener('touchmove', handleDragDialog)
  document.removeEventListener('touchend', stopDragDialog)

  // Restore styles
  document.body.style.cursor = ''
  document.body.style.userSelect = ''

  // Save settings
  saveAIChatSettings()
}

// Resize dialog
const startResize = (event) => {
  event.preventDefault()
  event.stopPropagation()

  isResizing.value = true
  resizeStartPos.value = {
    x: event.type === 'mousedown' ? event.clientX : event.touches[0].clientX,
    y: event.type === 'mousedown' ? event.clientY : event.touches[0].clientY
  }
  resizeStartSize.value = { ...aiChatSize.value }

  // Add global event listeners
  if (event.type === 'mousedown') {
    document.addEventListener('mousemove', handleResize)
    document.addEventListener('mouseup', stopResize)
  } else {
    document.addEventListener('touchmove', handleResize, { passive: false })
    document.addEventListener('touchend', stopResize)
  }

  // Add resize styles
  document.body.style.cursor = 'nw-resize'
  document.body.style.userSelect = 'none'
}

const handleResize = (event) => {
  if (!isResizing.value) return

  event.preventDefault()

  const clientX = event.type === 'mousemove' ? event.clientX : event.touches[0].clientX
  const clientY = event.type === 'mousemove' ? event.clientY : event.touches[0].clientY

  const deltaX = clientX - resizeStartPos.value.x
  const deltaY = clientY - resizeStartPos.value.y

  let newWidth = resizeStartSize.value.width + deltaX
  let newHeight = resizeStartSize.value.height + deltaY

  // Set minimum and maximum sizes
  const minWidth = 350
  const minHeight = 400
  const maxWidth = window.innerWidth - aiChatPosition.value.x
  const maxHeight = window.innerHeight - aiChatPosition.value.y

  newWidth = Math.min(Math.max(minWidth, newWidth), maxWidth)
  newHeight = Math.min(Math.max(minHeight, newHeight), maxHeight)

  aiChatSize.value = { width: newWidth, height: newHeight }
}

const stopResize = () => {
  isResizing.value = false

  // Remove global event listeners
  document.removeEventListener('mousemove', handleResize)
  document.removeEventListener('mouseup', stopResize)
  document.removeEventListener('touchmove', handleResize)
  document.removeEventListener('touchend', stopResize)

  // Restore styles
  document.body.style.cursor = ''
  document.body.style.userSelect = ''

  // Save settings
  saveAIChatSettings()
}

const handleWindowResize = () => {
  initializeAIChatSettings()
}

// Get data when component is mounted
onMounted(() => {
  console.log('=== PaperDetail page mounted ===')
  console.log('Route params:', route.params)
  console.log('User login status check:')
  console.log('- localStorage token:', localStorage.getItem('token'))
  console.log('- userStore token:', userStore?.token)
  console.log('- userStore isLoggedIn:', userStore?.isLoggedIn)
  console.log('- userStore user:', userStore?.user)

  fetchPaperDetail()

  // Initialize AI chat settings
  initializeAIChatSettings()

  // Listen for window resize
  window.addEventListener('resize', handleWindowResize)
})

// Cleanup when component is unmounted
onUnmounted(() => {
  // Clean up event listeners
  window.removeEventListener('resize', handleWindowResize)
  document.removeEventListener('mousemove', handleDragDialog)
  document.removeEventListener('mouseup', stopDragDialog)
  document.removeEventListener('touchmove', handleDragDialog)
  document.removeEventListener('touchend', stopDragDialog)
  document.removeEventListener('mousemove', handleResize)
  document.removeEventListener('mouseup', stopResize)
  document.removeEventListener('touchmove', handleResize)
  document.removeEventListener('touchend', stopResize)

  // Restore styles
  document.body.style.cursor = ''
  document.body.style.userSelect = ''
})
</script>

<style scoped>
.paper-detail-container {
  min-height: 100vh;
  width: 100%;
  background-color: #f0f2f5;
  padding: 20px;
  box-sizing: border-box;
}

.page-header {
  background-color: #fff;
  border-radius: 8px;
  padding: 20px;
  margin-bottom: 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.page-title {
  margin: 0 0 5px 0;
  font-size: 24px;
  font-weight: 600;
  color: #333;
}

.page-subtitle {
  margin: 0;
  font-size: 14px;
  color: #666;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 10px;
}

.split-screen-container {
  display: flex;
  height: calc(100vh - 140px);
  gap: 20px;
  background: #fff;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.left-panel {
  flex: 1;
  display: flex;
  flex-direction: column;
  border-right: 1px solid #e4e7ed;
}

.right-panel {
  width: 400px;
  display: flex;
  flex-direction: column;
  background: #fafafa;
  overflow: hidden;
}

.function-tabs {
  flex: 1;
  height: 100%;
  overflow: hidden;
  background: #fff;
}

.panel-tabs {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.panel-tabs :deep(.el-tabs__header) {
  margin: 0;
  border-bottom: 1px solid #e4e7ed;
  background: #f8f9fa;
  padding: 0 16px;
}

.panel-tabs :deep(.el-tabs__nav-wrap) {
  background: #f8f9fa;
}

.panel-tabs :deep(.el-tabs__content) {
  flex: 1;
  overflow: hidden;
  height: calc(100% - 50px);
  padding: 0;
}

.panel-tabs :deep(.el-tab-pane) {
  height: 100%;
  overflow: hidden;
}

.annotation-section {
  flex: 1;
  height: 100%;
  overflow: hidden;
  background: #fff;
}

.summary-section {
  flex: 1;
  height: 100%;
  overflow: hidden;
  background: #fff;
}

/* AI助手悬浮按钮 */
.ai-assistant-fab {
  position: fixed;
  bottom: 30px;
  right: 30px;
  width: 56px;
  height: 56px;
  background: #409eff;
  border-radius: 28px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  box-shadow: 0 4px 12px rgba(64, 158, 255, 0.4);
  transition: all 0.3s ease;
  z-index: 1000;
  color: white;
}

.ai-assistant-fab:hover {
  background: #337ecc;
  transform: scale(1.1);
  box-shadow: 0 6px 16px rgba(64, 158, 255, 0.6);
}

/* AI对话悬浮窗 */
.ai-chat-dialog {
  position: fixed !important;
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.12);
  display: flex !important;
  flex-direction: column;
  z-index: 9999 !important;
  min-width: 350px;
  min-height: 400px;
  max-width: 90vw;
  max-height: 90vh;
  border: 2px solid #409eff;
  pointer-events: auto !important;
  visibility: visible !important;
  opacity: 1 !important;
}

.ai-chat-header {
  background: #f8f9fa;
  border-bottom: 1px solid #e4e7ed;
  padding: 12px 16px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  cursor: move;
  user-select: none;
  border-radius: 8px 8px 0 0;
}

.header-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 600;
  color: #333;
  font-size: 14px;
}

.header-actions {
  display: flex;
  gap: 4px;
}

.ai-chat-content {
  flex: 1;
  overflow: hidden;
  border-radius: 0 0 8px 8px;
  position: relative;
  z-index: 1;
}

/* 确保AI聊天悬浮窗内的下拉框能正常显示 */
.ai-chat-dialog :deep(.el-select-dropdown) {
  z-index: 999999 !important;
}

.ai-chat-dialog :deep(.el-popper) {
  z-index: 999999 !important;
}

/* 调节大小的手柄 */
.resize-handle {
  position: absolute;
  bottom: 0;
  right: 0;
  width: 16px;
  height: 16px;
  cursor: nw-resize;
  background: linear-gradient(
    -45deg,
    transparent 0%,
    transparent 30%,
    #c0c4cc 30%,
    #c0c4cc 35%,
    transparent 35%,
    transparent 50%,
    #c0c4cc 50%,
    #c0c4cc 55%,
    transparent 55%,
    transparent 70%,
    #c0c4cc 70%,
    #c0c4cc 75%,
    transparent 75%
  );
  background-size: 3px 3px;
}

.resize-handle:hover {
  background: linear-gradient(
    -45deg,
    transparent 0%,
    transparent 30%,
    #409eff 30%,
    #409eff 35%,
    transparent 35%,
    transparent 50%,
    #409eff 50%,
    #409eff 55%,
    transparent 55%,
    transparent 70%,
    #409eff 70%,
    #409eff 75%,
    transparent 75%
  );
}

.paper-info-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  background: #fff;
  border-bottom: 1px solid #e4e7ed;
  min-height: 80px;
  box-sizing: border-box;
}

.info-content {
  flex: 1;
  min-width: 0;
}

.paper-title {
  font-size: 18px;
  font-weight: 600;
  color: #333;
  margin-bottom: 8px;
  line-height: 1.3;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.paper-meta {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  color: #666;
  flex-wrap: wrap;
}

.author {
  color: #409EFF;
  font-weight: 500;
}

.separator {
  color: #ddd;
}

.year,
.journal {
  color: #666;
}

.info-actions {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-left: 16px;
}

.paper-details {
  background: #f8f9fa;
  border-bottom: 1px solid #e4e7ed;
  animation: slideDown 0.3s ease-out;
}

@keyframes slideDown {
  from {
    height: 0;
    opacity: 0;
  }
  to {
    height: auto;
    opacity: 1;
  }
}

.details-content {
  padding: 20px;
}

.detail-item {
  display: flex;
  margin-bottom: 12px;
  align-items: flex-start;
}

.detail-item label {
  font-weight: 600;
  color: #333;
  min-width: 80px;
  margin-right: 12px;
}

.abstract-section {
  margin-top: 16px;
  padding-top: 16px;
  border-top: 1px solid #e4e7ed;
}

.abstract-section label {
  display: block;
  margin-bottom: 8px;
}

.abstract-section p {
  margin: 0;
  line-height: 1.6;
  color: #666;
}

.pdf-container {
  flex: 1;
  overflow: hidden;
  background: #f5f7fa;
}

.pdf-placeholder {
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  height: 100%;
  color: #999;
  background: #fafafa;
}

.pdf-placeholder p {
  margin: 8px 0;
  font-size: 14px;
}

/* 响应式设计 */
@media (max-width: 1200px) {
  .right-panel {
    width: 350px;
  }
  
  .paper-meta {
    display: -webkit-box;
    -webkit-line-clamp: 2;
    -webkit-box-orient: vertical;
    overflow: hidden;
  }
}

@media (max-width: 1024px) {
  .paper-detail-container {
    padding: 10px;
  }
  
  .split-screen-container {
    flex-direction: column;
    height: auto;
    min-height: calc(100vh - 120px);
  }
  
  .left-panel {
    border-right: none;
    border-bottom: 1px solid #e4e7ed;
    min-height: 60vh;
  }
  
  .right-panel {
    width: 100%;
    min-height: 40vh;
  }
  
  .ai-assistant-fab {
    bottom: 20px;
    right: 20px;
    width: 48px;
    height: 48px;
  }
  
  .paper-info-bar {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
    min-height: auto;
  }
  
  .info-actions {
    margin-left: 0;
    align-self: flex-end;
  }
}

@media (max-width: 768px) {
  .paper-detail-container {
    padding: 10px;
  }
  
  .page-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 10px;
  }
  
  .header-right {
    align-self: flex-end;
  }
  
  .paper-title {
    font-size: 16px;
    white-space: normal;
    display: -webkit-box;
    -webkit-line-clamp: 2;
    -webkit-box-orient: vertical;
    overflow: hidden;
  }
  
  .paper-meta {
    font-size: 12px;
  }
  
  .info-actions {
    flex-wrap: wrap;
  }
  
  .details-content {
    padding: 16px;
  }
  
  .detail-item {
    flex-direction: column;
    align-items: flex-start;
  }
  
  .detail-item label {
    min-width: auto;
    margin-right: 0;
    margin-bottom: 4px;
  }
}

@media (max-width: 480px) {
  .paper-info-bar {
    padding: 12px 16px;
  }
  
  .info-actions {
    width: 100%;
    justify-content: flex-end;
  }
  
  .info-actions .el-button {
    font-size: 12px;
    padding: 6px 12px;
  }
}
</style> 