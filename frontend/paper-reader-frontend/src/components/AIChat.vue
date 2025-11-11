<template>
  <div class="ai-chat">
    <!-- Function Selection Tabs -->
    <el-tabs v-model="activeMode" class="ai-mode-tabs">
      <!-- Intelligent Summary Mode -->
      <el-tab-pane label="Intelligent Summary" name="summary">
        <div class="summary-mode">
          <div class="summary-header">
            <h4>AI Intelligent Analysis Assistant</h4>
            <p>Quickly generate paper summaries, extract keywords or translate text</p>
          </div>

          <!-- Three Function Buttons -->
          <div class="ai-functions-grid">
            <div class="function-card" @click="generateKeyInsightsAction" :class="{ 'loading': isGeneratingKeyInsights }">
              <div class="function-icon">
                <el-icon size="32"><Document /></el-icon>
              </div>
              <h5>Key Insights</h5>
              <p>AI analyzes full PDF text to extract core viewpoints and highlights</p>
              <el-button
                type="primary"
                :loading="isGeneratingKeyInsights"
                :disabled="!paperId"
                class="function-button"
              >
                {{ isGeneratingKeyInsights ? 'Analyzing...' : 'Generate Key Insights' }}
              </el-button>
            </div>

            <div class="function-card" @click="generateRelatedWorkAction" :class="{ 'loading': isGeneratingRelatedWork }">
              <div class="function-icon">
                <el-icon size="32"><PriceTag /></el-icon>
              </div>
              <h5>Related Work Description</h5>
              <p>Generate research-style Related Work description based on full PDF (Bilingual)</p>
              <el-button
                type="success"
                :loading="isGeneratingRelatedWork"
                :disabled="!paperId"
                class="function-button"
              >
                {{ isGeneratingRelatedWork ? 'Generating...' : 'Generate Description' }}
              </el-button>
            </div>

            <div class="function-card" @click="openTranslateMode" :class="{ 'active': activeMode === 'translate' }">
              <div class="function-icon">
                <el-icon size="32"><EditPen /></el-icon>
              </div>
              <h5>Text Translation</h5>
              <p>High-quality Chinese-English translation service</p>
              <el-button
                type="warning"
                class="function-button"
              >
                Start Translation
              </el-button>
            </div>
          </div>
          
          <!-- Results Display Area -->
          <div v-if="keyInsightsResult || relatedWorkResult" class="results-area">
            <!-- Key Insights Result -->
            <div v-if="keyInsightsResult" class="result-card">
              <div class="result-header">
                <h6><el-icon><Document /></el-icon> Key Insights</h6>
                <div class="result-actions">
                  <el-button size="small" @click="copyKeyInsightsResult" :icon="DocumentCopy">Copy</el-button>
                  <el-button size="small" type="danger" plain @click="clearKeyInsightsResult" :icon="Delete">Clear</el-button>
                </div>
              </div>
              <div class="result-content">{{ keyInsightsResult.insights }}</div>
              <div class="result-meta">
                <el-tag size="small">Based on full PDF analysis</el-tag>
              </div>
            </div>

            <!-- Related Work Description Result -->
            <div v-if="relatedWorkResult" class="result-card">
              <div class="result-header">
                <h6><el-icon><PriceTag /></el-icon> Related Work Description</h6>
                <div class="result-actions">
                  <el-button size="small" @click="copyRelatedWorkResult" :icon="DocumentCopy">Copy</el-button>
                  <el-button size="small" type="danger" plain @click="clearRelatedWorkResult" :icon="Delete">Clear</el-button>
                </div>
              </div>
              <div class="result-content">
                <div class="related-work-description">
                  <div class="language-section">
                    <h6>Chinese Description:</h6>
                    <p>{{ relatedWorkResult.chinese_description }}</p>
                  </div>
                  <div class="language-section">
                    <h6>English Description:</h6>
                    <p>{{ relatedWorkResult.english_description }}</p>
                  </div>
                </div>
              </div>
              <div class="result-meta">
                <el-tag size="small">Research-style bilingual description</el-tag>
              </div>
            </div>
          </div>
        </div>
      </el-tab-pane>

      <!-- Translation Assistant Mode -->
      <el-tab-pane label="Translation Assistant" name="translate">
        <div class="translate-mode">
          <div class="translate-input-area">
            <div class="input-group">
              <label>Original Text:</label>
              <el-input
                v-model="translateInput"
                type="textarea"
                :autosize="{ minRows: 3, maxRows: 6 }"
                placeholder="Enter text to translate..."
                :disabled="isTranslating"
              />
            </div>

            <div class="translate-controls">
              <el-select
                v-model="translateTargetLang"
                placeholder="Target Language"
                style="width: 120px"
              >
                <el-option label="Chinese" value="zh"></el-option>
                <el-option label="English" value="en"></el-option>
              </el-select>

              <el-button
                type="primary"
                @click="translateText"
                :loading="isTranslating"
                :disabled="!translateInput.trim() || isTranslating"
              >
                <el-icon><EditPen /></el-icon>
                {{ isTranslating ? 'Translating...' : 'Translate' }}
              </el-button>
            </div>

            <div v-if="translateResult" class="translate-result">
              <label>Translation:</label>
              <div class="result-content">{{ translateResult }}</div>
              <div class="result-info">
                <small>Model: {{ translateModel }} | Tokens: {{ translateTokens }}</small>
              </div>
            </div>
          </div>
        </div>
      </el-tab-pane>
      
      <!-- Paper Q&A Mode -->
      <el-tab-pane label="Paper Q&A" name="qa">
        <div class="qa-mode">
          <!-- Chat Messages Area -->
          <div class="chat-messages" ref="messagesRef">
            <div v-if="chatHistory.length === 0" class="empty-state">
              <el-icon size="48" color="#c0c4cc"><chat-dot-round /></el-icon>
              <p>No conversation history yet</p>
              <p class="tip">Ask AI any questions about this paper</p>
            </div>

            <div
              v-for="message in chatHistory"
              :key="message.id"
              :class="['message', message.role]"
            >
              <div class="message-avatar">
                <el-avatar
                  v-if="message.role === 'user'"
                  :size="32"
                  :src="userAvatar"
                  background-color="#409EFF"
                >
                  <el-icon><user /></el-icon>
                </el-avatar>
                <el-avatar
                  v-else
                  :size="32"
                  background-color="#67C23A"
                >
                  <el-icon><ChatDotRound /></el-icon>
                </el-avatar>
              </div>

              <div class="message-content">
                <!-- AI Reasoning Process Display -->
                <div v-if="message.reasoning_content" class="reasoning-content">
                  <div class="reasoning-header">
                    <el-icon><Cpu /></el-icon>
                    <span>AI Reasoning Process</span>
                  </div>
                  <div class="reasoning-text">{{ message.reasoning_content }}</div>
                </div>

                <div class="message-text">{{ message.content }}</div>
                <div class="message-time">{{ formatDate(message.timestamp) }}</div>
              </div>
            </div>

            <!-- AI Thinking Status -->
            <div v-if="isThinking" class="message assistant thinking">
              <div class="message-avatar">
                <el-avatar :size="32" background-color="#67C23A">
                  <el-icon><ChatDotRound /></el-icon>
                </el-avatar>
              </div>
              <div class="message-content">
                <div class="thinking-indicator">
                  <span>AI is thinking deeply...</span>
                  <div class="dots">
                    <span></span>
                    <span></span>
                    <span></span>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Q&A Input Area -->
          <div class="chat-input">
            <div class="input-controls">
              <el-select
                v-model="selectedModel"
                placeholder="Select Model"
                style="width: 200px;"
                popper-class="model-select-dropdown"
                :teleported="false"
                @change="handleModelChange"
              >
                <el-option label="V3 Fast" value="deepseek-chat"></el-option>
                <el-option label="R1 Reasoning" value="deepseek-reasoner"></el-option>
                <el-option label="Test" value="test"></el-option>
              </el-select>

              <el-tooltip content="Clear conversation history">
                <el-button
                  size="small"
                  @click="confirmClearHistory"
                  :disabled="chatHistory.length === 0"
                >
                  <el-icon><delete /></el-icon>
                </el-button>
              </el-tooltip>

              <el-tooltip content="Refresh conversation">
                <el-button
                  size="small"
                  @click="refreshHistory"
                >
                  <el-icon><refresh /></el-icon>
                </el-button>
              </el-tooltip>
            </div>

            <el-input
              v-model="currentQuestion"
              type="textarea"
              :rows="3"
              placeholder="Ask AI any questions about this paper..."
              :disabled="!paperId || isThinking"
              @keyup.ctrl.enter="handleSendMessage"
              @keyup.enter.prevent
              maxlength="500"
              show-word-limit
              resize="none"
            />

            <div class="input-actions">
              <div class="input-tips">
                <span>Ctrl + Enter to send | Current model: {{ selectedModel === 'deepseek-reasoner' ? 'R1 Reasoning' : selectedModel === 'test' ? 'Test Mode' : 'V3 Fast' }}</span>
              </div>
              <el-button
                type="primary"
                :loading="isThinking"
                :disabled="!currentQuestion.trim() || !paperId"
                @click="handleSendMessage"
              >
                <el-icon><promotion /></el-icon>
                {{ isThinking ? 'Thinking...' : 'Send' }}
              </el-button>
            </div>
          </div>
        </div>
      </el-tab-pane>
    </el-tabs>
  </div>
</template>

<script setup>
import { ref, reactive, watch, onMounted, nextTick } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { askAI, askAIWithModel, getAIHistory, translateText as translateAPI, generateSummary, extractKeywords, generateKeyInsights, generateRelatedWork } from '@/api/ai'
import { useUserStore } from '@/store/user'
import dayjs from 'dayjs'
import { EditPen, Cpu, Document, PriceTag, DocumentCopy, Delete } from '@element-plus/icons-vue'

// Props
const props = defineProps({
  paperId: {
    type: [Number, String],
    default: null
  },
  paperContext: {
    type: String,
    default: ''
  },
  autoLoad: {
    type: Boolean,
    default: true
  },
  userAvatar: {
    type: String,
    default: ''
  }
})

// Emits
const emits = defineEmits(['message-sent', 'message-received', 'history-loaded'])

// 响应式数据
const isThinking = ref(false)
const chatHistory = ref([])
const currentQuestion = ref('')
const messagesRef = ref()

// 功能模式切换
const activeMode = ref('summary') // 默认智能总结模式

// 翻译相关
const translateInput = ref('')
const translateTargetLang = ref('zh')
const translateResult = ref('')
const translateModel = ref('')
const translateTokens = ref(0)
const isTranslating = ref(false)

// 智能分析相关
const keyInsightsResult = ref(null)
const relatedWorkResult = ref(null)
const isGeneratingKeyInsights = ref(false)
const isGeneratingRelatedWork = ref(false)

// 模型选择
const selectedModel = ref('deepseek-chat') // 默认快速模型

// User store
const userStore = useUserStore()

// Format date
const formatDate = (dateString) => {
  return dayjs(dateString).format('HH:mm')
}

// Scroll to bottom
const scrollToBottom = () => {
  nextTick(() => {
    if (messagesRef.value) {
      messagesRef.value.scrollTop = messagesRef.value.scrollHeight
    }
  })
}

// Model change handler
const handleModelChange = (value) => {
  console.log('Model selection changed:', value)
  const modelName = value === 'deepseek-reasoner' ? 'R1 Reasoning' : value === 'test' ? 'Test Mode' : 'V3 Fast'
  ElMessage.info(`Model selected: ${modelName}`)
}

// Translation function
const translateText = async () => {
  if (!translateInput.value.trim()) return

  isTranslating.value = true
  translateResult.value = ''

  try {
    const response = await translateAPI({
      text: translateInput.value,
      target_language: translateTargetLang.value
    })

    if (response.success) {
      translateResult.value = response.data.translation
      translateModel.value = response.data.model || 'DeepSeek V3'
      translateTokens.value = response.data.tokens_used || 0
      ElMessage.success('Translation completed')
    } else {
      ElMessage.error(response.error || 'Translation failed')
    }
  } catch (error) {
    console.error('Translation failed:', error)
    ElMessage.error('Translation failed, please try again')
  } finally {
    isTranslating.value = false
  }
}

// Generate key insights
const generateKeyInsightsAction = async () => {
  if (!props.paperId) {
    ElMessage.warning('Please select a paper first')
    return
  }

  isGeneratingKeyInsights.value = true

  try {
    const response = await generateKeyInsights({
      paper_id: props.paperId
    })

    if (response.success) {
      keyInsightsResult.value = response.data
      ElMessage.success('Key insights generated successfully')
    } else {
      ElMessage.error(response.error || 'Failed to generate key insights')
    }
  } catch (error) {
    console.error('Failed to generate key insights:', error)
    ElMessage.error('Failed to generate key insights, please try again')
  } finally {
    isGeneratingKeyInsights.value = false
  }
}

// Generate Related Work description
const generateRelatedWorkAction = async () => {
  if (!props.paperId) {
    ElMessage.warning('Please select a paper first')
    return
  }

  isGeneratingRelatedWork.value = true

  try {
    const response = await generateRelatedWork({
      paper_id: props.paperId
    })

    if (response.success) {
      relatedWorkResult.value = response.data
      ElMessage.success('Related Work description generated successfully')
    } else {
      ElMessage.error(response.error || 'Failed to generate Related Work description')
    }
  } catch (error) {
    console.error('Failed to generate Related Work description:', error)
    ElMessage.error('Failed to generate Related Work description, please try again')
  } finally {
    isGeneratingRelatedWork.value = false
  }
}

// Open translate mode
const openTranslateMode = () => {
  activeMode.value = 'translate'
}

// Copy key insights result
const copyKeyInsightsResult = async () => {
  try {
    await navigator.clipboard.writeText(keyInsightsResult.value.insights)
    ElMessage.success('Key insights copied to clipboard')
  } catch (error) {
    ElMessage.error('Copy failed')
  }
}

// Copy Related Work result
const copyRelatedWorkResult = async () => {
  try {
    const content = `Chinese Description:\n${relatedWorkResult.value.chinese_description}\n\nEnglish Description:\n${relatedWorkResult.value.english_description}`
    await navigator.clipboard.writeText(content)
    ElMessage.success('Related Work description copied to clipboard')
  } catch (error) {
    ElMessage.error('Copy failed')
  }
}

// Clear key insights result
const clearKeyInsightsResult = () => {
  keyInsightsResult.value = null
  ElMessage.info('Key insights result cleared')
}

// Clear Related Work result
const clearRelatedWorkResult = () => {
  relatedWorkResult.value = null
  ElMessage.info('Related Work result cleared')
}

// Get AI conversation history
const fetchAIHistory = async () => {
  if (!props.paperId) return

  try {
    const response = await getAIHistory(props.paperId)

    if (response.success && response.data && Array.isArray(response.data)) {
      // Convert conversation history format
      const messages = []
      response.data.forEach((conversation, index) => {
        // Add user question
        messages.push({
          id: `user_${conversation.conversation_id}_${index}`,
          role: 'user',
          content: conversation.question,
          timestamp: conversation.create_time
        })

        // Add AI answer
        messages.push({
          id: `ai_${conversation.conversation_id}_${index}`,
          role: 'assistant',
          content: conversation.answer,
          reasoning_content: conversation.reasoning_content || null, // Reasoning content
          timestamp: conversation.create_time
        })
      })

      // Sort by timestamp
      messages.sort((a, b) => new Date(a.timestamp) - new Date(b.timestamp))

      chatHistory.value = messages
      scrollToBottom()
      emits('history-loaded', chatHistory.value)
    }
  } catch (error) {
    console.error('Failed to fetch conversation history:', error)
  }
}

// Send message
const handleSendMessage = async () => {
  if (!currentQuestion.value.trim() || !props.paperId || isThinking.value) {
    return
  }

  const question = currentQuestion.value.trim()
  currentQuestion.value = ''

  // Add user message to chat history
  const userMessage = {
    id: `user_${Date.now()}`,
    role: 'user',
    content: question,
    timestamp: new Date().toISOString()
  }
  chatHistory.value.push(userMessage)
  scrollToBottom()

  emits('message-sent', userMessage)

  isThinking.value = true
  try {
    let response

    // Call different APIs based on selected model
    if (selectedModel.value === 'test') {
      // Test option, show test message
      const aiMessage = {
        id: `ai_${Date.now()}`,
        role: 'assistant',
        content: 'This is a test message to verify the dropdown functionality is working correctly! Currently selected is the test option.',
        timestamp: new Date().toISOString()
      }
      chatHistory.value.push(aiMessage)
      scrollToBottom()
      emits('message-received', aiMessage)
      isThinking.value = false
      return
    } else if (selectedModel.value === 'deepseek-reasoner') {
      response = await askAIWithModel({
        question: question,
        context: props.paperContext || '',
        paper_id: parseInt(props.paperId),
        model: 'deepseek-reasoner',
        conversation_history: chatHistory.value.slice(-10)
      })
    } else {
      response = await askAI({
        question: question,
        context: props.paperContext || '',
        paper_id: parseInt(props.paperId),
        conversation_history: chatHistory.value.slice(-10)
      })
    }

    if (response.success) {
      // Add AI answer to chat history
      const aiMessage = {
        id: `ai_${Date.now()}`,
        role: 'assistant',
        content: response.data.answer,
        reasoning_content: response.data.reasoning_content || null, // Reasoning content
        timestamp: response.data.timestamp || new Date().toISOString()
      }
      chatHistory.value.push(aiMessage)
      scrollToBottom()

      emits('message-received', aiMessage)
    } else {
      ElMessage.error(response.error || 'AI Q&A failed')

      // Add error message
      const errorMessage = {
        id: `error_${Date.now()}`,
        role: 'assistant',
        content: 'Sorry, I cannot answer your question right now. Please try again later.',
        timestamp: new Date().toISOString()
      }
      chatHistory.value.push(errorMessage)
      scrollToBottom()
    }
  } catch (error) {
    console.error('AI Q&A failed:', error)
    ElMessage.error('AI Q&A failed, please check your network connection')

    // Add error message
    const errorMessage = {
      id: `error_${Date.now()}`,
      role: 'assistant',
      content: 'Network connection error. Please check your network settings.',
      timestamp: new Date().toISOString()
    }
    chatHistory.value.push(errorMessage)
    scrollToBottom()
  } finally {
    isThinking.value = false
  }
}

// Refresh conversation history
const refreshHistory = () => {
  fetchAIHistory()
}

// Confirm clear conversation history
const confirmClearHistory = async () => {
  try {
    await ElMessageBox.confirm(
      'Are you sure you want to clear all conversation records? This action cannot be undone.',
      'Clear Confirmation',
      {
        confirmButtonText: 'Clear',
        cancelButtonText: 'Cancel',
        type: 'warning'
      }
    )

    clearHistory()
  } catch {
    // User cancelled
  }
}

// Clear conversation history
const clearHistory = () => {
  chatHistory.value = []
  ElMessage.success('Conversation history cleared')
}

// Expose methods to parent component
defineExpose({
  clearHistory,
  refreshHistory,
  fetchAIHistory,
  sendMessage: handleSendMessage
})

// Watch paperId changes
watch(() => props.paperId, (newPaperId) => {
  if (newPaperId && props.autoLoad) {
    fetchAIHistory()
  }
}, { immediate: true })

// Auto load when component mounts
onMounted(() => {
  if (props.paperId && props.autoLoad) {
    fetchAIHistory()
  }
})
</script>

<style scoped>
.ai-chat {
  height: 100%;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.ai-mode-tabs {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  height: 100%;
}

.ai-mode-tabs :deep(.el-tabs__header) {
  flex-shrink: 0;
  margin-bottom: 0;
  background: #f8f9fa;
  border-bottom: 1px solid #e4e7ed;
}

.ai-mode-tabs :deep(.el-tabs__nav-wrap) {
  padding: 0 16px;
}

.ai-mode-tabs :deep(.el-tabs__content) {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  padding: 0;
}

.ai-mode-tabs :deep(.el-tab-pane) {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  min-height: 0;
}

.summary-mode {
  padding: 20px;
  overflow-y: auto;
  max-height: 100%;
}

.summary-header {
  text-align: center;
  margin-bottom: 24px;
}

.summary-header h4 {
  margin: 0 0 8px 0;
  color: #333;
  font-size: 18px;
  font-weight: 600;
}

.summary-header p {
  margin: 0;
  color: #666;
  font-size: 14px;
}

.ai-functions-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
  margin-bottom: 24px;
}

.function-card {
  background: white;
  border: 2px solid #e4e7ed;
  border-radius: 12px;
  padding: 20px;
  text-align: center;
  cursor: pointer;
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
}

.function-card:hover {
  border-color: #409eff;
  box-shadow: 0 4px 20px rgba(64, 158, 255, 0.15);
  transform: translateY(-2px);
}

.function-card.loading {
  border-color: #409eff;
  background: linear-gradient(45deg, #f0f9ff, #e1f5fe);
}

.function-card.active {
  border-color: #f39c12;
  background: linear-gradient(45deg, #fff9e6, #fef5e7);
}

.function-icon {
  margin-bottom: 12px;
  color: #666;
  transition: color 0.3s ease;
}

.function-card:hover .function-icon {
  color: #409eff;
}

.function-card.loading .function-icon {
  color: #409eff;
  animation: pulse 2s ease-in-out infinite;
}

.function-card.active .function-icon {
  color: #f39c12;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.6; }
}

.function-card h5 {
  margin: 0 0 8px 0;
  color: #333;
  font-size: 16px;
  font-weight: 600;
}

.function-card p {
  margin: 0 0 16px 0;
  color: #666;
  font-size: 13px;
  line-height: 1.4;
  min-height: 36px;
}

.function-button {
  width: 100%;
  margin-top: auto;
}

.results-area {
  margin-top: 24px;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.result-card {
  background: #f8f9fa;
  border-radius: 8px;
  padding: 16px;
  border-left: 4px solid #409eff;
}

.result-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.result-header h6 {
  margin: 0;
  color: #333;
  font-size: 14px;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 6px;
}

.result-actions {
  display: flex;
  gap: 8px;
}

.result-content {
  color: #555;
  font-size: 14px;
  line-height: 1.6;
  margin-bottom: 12px;
}

.keywords-list {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.keyword-tag {
  margin: 0;
}

.related-work-description {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.language-section h6 {
  margin: 0 0 8px 0;
  color: #409eff;
  font-size: 14px;
  font-weight: 600;
}

.language-section p {
  margin: 0;
  line-height: 1.6;
  padding: 12px;
  background: #f8f9fa;
  border-radius: 6px;
  border-left: 3px solid #409eff;
}

.result-meta {
  display: flex;
  justify-content: flex-end;
}

.translate-mode {
  padding: 16px;
  overflow-y: auto;
  max-height: 100%;
}

.qa-mode {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  min-height: 0;
}

.translate-input-area {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.input-group {
  display: flex;
  flex-direction: column;
}

.input-group label {
  font-size: 14px;
  font-weight: 500;
  color: #555;
  margin-bottom: 8px;
}

/* 确保模型选择下拉框可见 */
:deep(.model-select-dropdown) {
  z-index: 999999 !important;
  background: white !important;
  border: 1px solid #dcdfe6 !important;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1) !important;
}

:deep(.el-select-dropdown) {
  z-index: 999999 !important;
  background: white !important;
  border: 1px solid #dcdfe6 !important;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1) !important;
}

:deep(.el-popper) {
  z-index: 999999 !important;
}

/* 针对悬浮窗内的下拉框特殊处理 */
.input-controls {
  position: relative;
  z-index: 1;
  overflow: visible !important;
}

.input-controls .el-select {
  overflow: visible !important;
}

:deep(.el-select-dropdown__item) {
  padding: 0 20px !important;
  height: 34px !important;
  line-height: 34px !important;
  background: white !important;
  color: #606266 !important;
}

:deep(.el-select-dropdown__item:hover) {
  background-color: #f5f7fa !important;
}

:deep(.el-select-dropdown__item.is-selected) {
  background-color: #409eff !important;
  color: white !important;
}

.input-controls {
  position: relative;
  z-index: 1;
  overflow: visible !important;
}

.input-controls .el-select {
  overflow: visible !important;
}

.translate-controls {
  display: flex;
  gap: 16px;
  align-items: center;
  flex-wrap: wrap;
}

.translate-result {
  margin-top: 16px;
  padding: 16px;
  background-color: #f8f9fa;
  border: 1px solid #e4e7ed;
  border-radius: 8px;
  max-height: 300px;
  overflow-y: auto;
}

.translate-result label {
  font-size: 14px;
  font-weight: 500;
  color: #333;
  margin-bottom: 8px;
  display: block;
}

.result-content {
  font-size: 15px;
  color: #2c3e50;
  line-height: 1.6;
  word-wrap: break-word;
  white-space: pre-wrap;
  margin-bottom: 12px;
}

.result-info {
  font-size: 12px;
  color: #909399;
  text-align: right;
  border-top: 1px solid #ebeef5;
  padding-top: 8px;
}

.chat-messages {
  flex: 1;
  overflow-y: auto;
  padding: 16px;
  background-color: #fafbfc;
  border-top: 1px solid #ebeef5;
  border-bottom: 1px solid #ebeef5;
  min-height: 200px; /* 确保最小高度 */
}

.empty-state {
  text-align: center;
  padding: 60px 20px;
  color: #909399;
}

.empty-state p {
  margin: 8px 0;
}

.empty-state .tip {
  font-size: 14px;
  color: #c0c4cc;
}

.message {
  display: flex;
  gap: 12px;
  margin-bottom: 20px;
  max-width: 100%;
}

.message.user {
  flex-direction: row-reverse;
}

.message.user .message-content {
  background-color: #409eff;
  color: white;
  border-radius: 18px 18px 4px 18px;
}

.message.user .message-time {
  color: rgba(255, 255, 255, 0.8);
  text-align: right;
}

.message.assistant .message-content {
  background-color: #f1f2f3;
  color: #2c3e50;
  border-radius: 18px 18px 18px 4px;
}

.message-content {
  max-width: 70%;
  padding: 12px 16px;
  border: 1px solid #e4e7ed;
  word-wrap: break-word;
  white-space: pre-wrap;
}

.reasoning-content {
  margin-bottom: 12px;
  padding: 12px;
  background-color: #f0f9eb;
  border: 1px solid #e1f3d8;
  border-radius: 8px;
  font-size: 13px;
}

.reasoning-header {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-bottom: 8px;
  color: #67c23a;
  font-weight: 500;
}

.reasoning-header .el-icon {
  font-size: 16px;
}

.reasoning-text {
  color: #5e6d82;
  line-height: 1.4;
  word-wrap: break-word;
  white-space: pre-wrap;
  font-family: 'Courier New', monospace;
}

.message-text {
  line-height: 1.5;
  word-wrap: break-word;
  white-space: pre-wrap;
}

.message-time {
  font-size: 12px;
  color: #909399;
  margin-top: 4px;
}

.thinking-indicator {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #67c23a;
  font-style: italic;
}

.dots {
  display: flex;
  gap: 4px;
}

.dots span {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background-color: #67c23a;
  animation: dot-pulse 1.5s infinite;
}

.dots span:nth-child(2) {
  animation-delay: 0.2s;
}

.dots span:nth-child(3) {
  animation-delay: 0.4s;
}

@keyframes dot-pulse {
  0%, 80%, 100% {
    transform: scale(0);
  }
  40% {
    transform: scale(1);
  }
}

.chat-input {
  flex-shrink: 0; /* 防止被压缩 */
  padding: 16px;
  border-top: 1px solid #ebeef5;
  background-color: #fff;
  min-height: 140px; /* 确保输入区域有足够高度 */
}

.input-controls {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
  gap: 8px;
}

.input-controls .el-button {
  padding: 8px 12px;
}

.input-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 12px;
}

.input-tips {
  font-size: 12px;
  color: #909399;
  flex: 1;
}

.input-actions .el-button {
  margin-left: 12px;
}

/* 滚动条样式 */
.chat-messages::-webkit-scrollbar {
  width: 6px;
}

.chat-messages::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 3px;
}

.chat-messages::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 3px;
}

.chat-messages::-webkit-scrollbar-thumb:hover {
  background: #a8a8a8;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .ai-mode-tabs {
    flex-direction: column;
  }

  .summary-mode {
    padding: 16px;
  }

  .ai-functions-grid {
    grid-template-columns: 1fr;
    gap: 12px;
  }

  .function-card {
    padding: 16px;
  }

  .function-card h5 {
    font-size: 15px;
  }

  .function-card p {
    font-size: 12px;
    min-height: 30px;
  }

  .results-area {
    margin-top: 16px;
    gap: 12px;
  }

  .result-card {
    padding: 12px;
  }

  .translate-mode {
    padding: 12px;
  }

  .qa-mode {
    flex: 1;
    display: flex;
    flex-direction: column;
    overflow: hidden;
    min-height: 0;
  }

  .translate-controls {
    flex-direction: column;
    align-items: stretch;
    gap: 8px;
  }

  .translate-result {
    padding: 12px;
  }

  .chat-messages {
    padding: 12px;
    min-height: 150px;
  }

  .chat-input {
    padding: 12px;
    min-height: 120px;
  }

  .message-content {
    max-width: 85%;
  }

  .input-controls {
    flex-wrap: wrap;
    gap: 8px;
  }

  .input-actions {
    flex-direction: column;
    align-items: stretch;
    gap: 8px;
  }

  .input-tips {
    text-align: center;
  }
}
</style> 